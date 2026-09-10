# Fix: BNDDIR override silently ignored on CRTPGM (.PGM targets)

## Context

[GitHub issue #565](https://github.com/IBM/ibmi-tobi/issues/565) reports that a
`private BNDDIR = ...` override on a `.PGM` target's `Rules.mk` line is accepted by
the parser but never reaches the generated `CRTPGM` command, so the binding
directory is silently dropped and imports resolved through it fail to bind — with
no diagnostic that the override was discarded.

The same parameter was fixed for `.SRVPGM` targets by issue #417 (commit
`926851b`, "Additional support for # and $"), which added
`BNDDIR($(call ESCAPE_FOR_SLASH,$(call replace_DOLLARESCAPE,$(BNDDIR))))` to
`CRTSRVPGMFLAGS`. That fix was never mirrored onto `CRTPGMFLAGS`, so `.PGM`
targets never got the same capability. `BNDDIR` already defaults to empty
(`src/mk/def_rules.mk:116-117`), and `CRTPGM`/`CRTSRVPGM` both accept empty
parens for omitted parameters (confirmed by `ACTGRP()`, `TGTRLS()`, `AUT()`
already rendering that way in the issue's joblog excerpt), so adding the clause
is additive and doesn't change behavior for targets that don't set `BNDDIR`.

## Approach

Mirror the exact `CRTSRVPGMFLAGS` `BNDDIR` clause into `CRTPGMFLAGS`.

**File:** `src/mk/def_rules.mk:481`

Current:
```make
CRTPGMFLAGS = ACTGRP($(ACTGRP)) ALWUPD($(ALWUPD)) USRPRF($(USRPRF)) TGTRLS($(TGTRLS)) AUT($(AUT)) DETAIL($(DETAIL)) OPTION($(CRTPGM_OPTION)) STGMDL($(STGMDL)) TEXT('$(subst ','',$(TEXT))') ALWRINZ($(ALWRINZ))
```

Change to (adding `BNDDIR(...)`, same call pattern as line 505's
`CRTSRVPGMFLAGS`):
```make
CRTPGMFLAGS = ACTGRP($(ACTGRP)) ALWUPD($(ALWUPD)) USRPRF($(USRPRF)) TGTRLS($(TGTRLS)) AUT($(AUT)) DETAIL($(DETAIL)) OPTION($(CRTPGM_OPTION)) STGMDL($(STGMDL)) TEXT('$(subst ','',$(TEXT))') ALWRINZ($(ALWRINZ)) BNDDIR($(call ESCAPE_FOR_SLASH,$(call replace_DOLLARESCAPE,$(BNDDIR))))
```

This reuses the existing `ESCAPE_FOR_SLASH` and `replace_DOLLARESCAPE` macros
(already defined in `def_rules.mk`) — no new macros needed. This is the same
`#`/`$` escaping chain documented in `standards.md` (in this folder): a
library/binding-directory name containing `#`/`$` must go through this same
unescaping before landing in a real IBM i command, exactly as `CRTSRVPGMFLAGS`
already does.

No Python changes are needed — `BNDDIR` is parsed generically as a per-target
override already (this is how it already works for `.SRVPGM`).

## Task Breakdown

### Task 1: Save spec documentation

Create `agent-os/specs/2026-09-10-0938-fix-bnddir-crtpgm/` with this plan,
`shape.md`, `standards.md`, and `references.md`.

### Task 2: Add BNDDIR clause to CRTPGMFLAGS

Edit `src/mk/def_rules.mk` line 481 as shown above.

### Task 3: Manual verification

There is no automated test coverage for `def_rules.mk` macro definitions —
`tests/unit/` only covers Python code, and nothing in the repo invokes real
`make` against these macros. Verification must be manual, per
`docs/contributing/testing.md`'s existing approach for `makei` changes:

1. On an IBM i system (or via a project like
   `https://github.com/edmundreinhardt/tobi-example`), create a `.PGM` target
   whose `Rules.mk` sets `private BNDDIR = <LIB>/<BNDDIR>` pointing to a real
   `*BNDDIR` object, reproducing the issue's repro case.
2. Run `makei b` (or `makei c -f <target>`) to build it.
3. Inspect `.logs/joblog.json` (or the echoed command) and confirm the
   generated `CRTPGM` command now includes `BNDDIR(<LIB>/<BNDDIR>)` instead of
   `BNDDIR(*NONE)`/omitted.
4. Confirm a plain `.PGM` target with **no** `BNDDIR` override still renders
   `BNDDIR()` (empty parens, same as `ACTGRP()`/`TGTRLS()` today) and builds
   successfully — i.e. the change is a no-op for targets that don't set it.
5. If a service-program import that previously failed to resolve (per the
   issue) is now resolved successfully, that confirms the fix end-to-end.
