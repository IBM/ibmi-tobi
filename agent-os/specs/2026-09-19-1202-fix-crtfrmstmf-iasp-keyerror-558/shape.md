# Fix crtfrmstmf iasp KeyError (#558) — Shaping Notes

## Scope

Bug fix: `crtfrmstmf`, when invoked standalone (not via `makei b`/`makei c`),
crashes with `KeyError: 'iasp'` whenever the `iasp` environment variable
isn't set — which is the normal case for a plain SSH session. Reported as
[IBM/ibmi-tobi#558](https://github.com/IBM/ibmi-tobi/issues/558).

## Decisions

- One-line fix: `env_settings["iasp"]` → `env_settings.get("iasp", "")`,
  matching `CrtFrmStmf.__init__`'s own existing default (`iasp: str = ""`)
  and `const.py`'s `DEFAULT_IASP`. No behavior change for the `makei`-driven
  build path, since it always sets `iasp` (even to `""`) via `PRESETUP`.
- No automated test added — `tests/unit/remote/test_crtfrmstmf.py` has no
  coverage of `cli()`'s argument wiring, and `unit/remote` tests aren't run
  by CI at all (same situation documented for `#565`/`#566`), so verification
  is manual.

## Context

- **Visuals:** None — backend Python fix.
- **References:** `docs/cli/crtfrmstmf.md` confirms standalone CLI usage
  (exactly the reporter's repro case) is documented, supported behavior, not
  an edge case.
- **Product alignment:** N/A — no `agent-os/product/` folder exists in this
  repo.

## Standards Applied

None of the currently-documented `agent-os/standards/` entries apply
directly — this is a plain Python `KeyError` from an unconditional dict
access, unrelated to the escaping chain, build-macro ordering, or testing
conventions already captured.
