# Fix BNDSRVPGM Order-Only Path (#566) — Shaping Notes

## Scope

Bug fix: an order-only `.SRVPGM` prerequisite (`| /QSYS.LIB/LIB.LIB/OBJ.SRVPGM`)
on a `.PGM`/`.SRVPGM` target is silently dropped from the generated
`bndsrvpgm(...)` clause, always rendering `bndsrvpgm(*NONE)`. Reported as
[IBM/ibmi-tobi#566](https://github.com/IBM/ibmi-tobi/issues/566).

## Decisions

- Fix only path 1 (the order-only-prerequisite ordering bug) in this pass.
  Path 2 (regular prerequisites losing their library qualifier via
  `$(notdir $^)`) is a separate, deliberately deferred decision — fixing it
  changes existing `BNDSRVPGM(...)` output for locally-built service programs
  too, which is a compatibility question the issue itself flags as needing
  its own decision.
- Minimal reorder, not a rewrite: swap two lines per recipe
  (`MODULE_TO_PGM_RECIPE`, `BND_TO_SRVPGM_RECIPE`) so `externalsrvpgms` is
  assigned before `PGM_VARIABLES`/`SRVPGM_VARIABLES` reads it. No new
  variables, no change to the qualifying transform itself (which was already
  correct, just unreachable).
- No automated test added — same situation as `#565`: no test infrastructure
  invokes real `make` against `def_rules.mk`, so verification is manual.

## Context

- **Visuals:** None — backend Makefile fix.
- **References:** the surrounding `#565` fix and FTPSAUD's `Rules.mk` history
  (three failed attempts before a `POSTCMD` workaround) — see `references.md`.
- **Product alignment:** N/A — no `agent-os/product/` folder exists in this
  repo.

## Standards Applied

None of the currently-documented `agent-os/standards/` entries apply directly
— this is a pure Make variable-evaluation-order bug, not related to the
`#`/`$` escaping chain, source-extension mapping, or the other captured
standards.
