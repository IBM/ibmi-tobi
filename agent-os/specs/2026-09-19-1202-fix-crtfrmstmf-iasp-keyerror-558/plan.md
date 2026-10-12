# Fix: crtfrmstmf fails with KeyError: 'iasp' outside a makei build

## Context

[GitHub issue #558](https://github.com/IBM/ibmi-tobi/issues/558) reports that
running `crtfrmstmf` standalone from the command line (e.g. over SSH, exactly
as [docs/cli/crtfrmstmf.md](docs/cli/crtfrmstmf.md) documents it as a
supported CLI tool) crashes with:

```
KeyError: 'iasp'
```

Confirmed directly against current code
([src/makei/crtfrmstmf.py:410-418](src/makei/crtfrmstmf.py:410)):

```python
if "iasp" in os.environ:
    env_settings["iasp"] = os.environ["iasp"]
...
handle = CrtFrmStmf(..., iasp=env_settings["iasp"], ...)
```

`env_settings["iasp"]` is only conditionally populated, but the constructor
call reads it unconditionally.

This doesn't surface through a normal `makei b`/`makei c` build because
`PRESETUP` in `def_rules.mk` (line 551-557) always exports `iasp="$(iasp)"`
as a shell env var before invoking `crtfrmstmf` or `launch` — even with no
IASP configured, `$(iasp)` is an empty string, but the env var still *exists*
(`iasp=""`), so `"iasp" in os.environ` is `True` and the bug never triggers
through that path. It only triggers when `crtfrmstmf` is invoked directly,
bypassing `PRESETUP` entirely, which is exactly what the reporter did and
exactly what the CLI's own docs describe as valid usage.

`CrtFrmStmf.__init__` already defaults `iasp: str = ""` (matching
`DEFAULT_IASP` in `const.py`), and internally does
`self.iasp = iasp if iasp else ""` — so the fix is purely in how the CLI
wiring reads the env var, not in `CrtFrmStmf` itself.

## Approach

Change the unconditional dict-index read to `.get(..., "")`, matching the
constructor's own default.

**File:** [src/makei/crtfrmstmf.py:418](src/makei/crtfrmstmf.py:418)

```diff
-                        postcmd=args.postcmd, output=args.output, iasp=env_settings["iasp"], dependencies=dependencies)
+                        postcmd=args.postcmd, output=args.output, iasp=env_settings.get("iasp", ""), dependencies=dependencies)
```

No other changes needed — `self.iasp`/`get_iasp_prefix()` only affect Python-
side IFS path construction for existence/dependency checks and temp-library
naming ([utils.py](src/makei/utils.py:388)); they don't add or remove any
parameter on the generated `CRTxxx` command itself. An empty `iasp` correctly
produces plain `/QSYS.LIB/...` paths, matching *SYSBAS convention — exactly
what's expected when there's no IASP in play.

## Task Breakdown

### Task 1: Save spec documentation

Create `agent-os/specs/2026-09-19-1202-fix-crtfrmstmf-iasp-keyerror-558/`
with this plan and `shape.md`.

### Task 2: Fix the KeyError

Edit `src/makei/crtfrmstmf.py` line 418 as shown above.

### Task 3: Manual verification

`tests/unit/remote/test_crtfrmstmf.py` covers the `CrtFrmStmf` class directly
but has no test for `cli()`'s argument wiring, and — like all `unit/remote`
tests — isn't run by CI regardless (requires the real `ibm_db_dbi`/`fcntl`
imports to even collect). Consistent with `#565`/`#566`, verification is
manual:

1. On an IBM i system, in a shell/job with no `iasp` environment variable set
   (i.e., a plain SSH session, not a `makei`-invoked build), run something
   like the issue's repro case:
   ```
   crtfrmstmf -f INITPGM.CLP -o initpgm -c CRTCLMOD
   ```
2. Confirm it no longer raises `KeyError: 'iasp'` and completes normally,
   creating the object in *SYSBAS.
3. Confirm a normal `makei b`/`makei c` build (which always exports
   `iasp="$(iasp)"`, even when empty) is unaffected — behavior there was
   already correct and `.get("iasp", "")` returns the exact same value
   `env_settings["iasp"]` would have.
4. If available, test on a system with an actual IASP configured
   (`iasp` env var set to a real ASP name) to confirm that path still works
   unchanged.

### Verification Results

Confirmed on a real IBM i system (TATORPA), running `crtfrmstmf` standalone
from an SSH session (no `iasp` env var set) against a real `*CMD` source
member from the FTPSAUD project:

```bash
crtfrmstmf -f /home/SCOTTS/builds/FTPSAUD/QCMDSRC/FTPSAUD.CMD \
  -o TESTCMD558 -l FTPSAUD -c CRTCMD \
  -p "PGM(FTPSAUD/FTPSAUD) VLDCKR(*NONE) PMTFILE(*NONE) HLPPNLGRP(FTPSAUD/FTPSAUD) HLPID(FTPSAUD) AUT(*EXCLUDE) TEXT('Test of #558 iasp fix')"
```

Completed cleanly with no `Traceback`/`KeyError: 'iasp'` — where it
previously would have crashed immediately on `cli()`'s unconditional
`env_settings["iasp"]` access. The scratch test object
(`FTPSAUD/TESTCMD558`) was deleted afterward (`DLTCMD`); the actual
`makei`-driven build path (which always exports `iasp`, even empty) was
already unaffected by this bug and remains unchanged.
