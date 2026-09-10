# References for Fix BNDSRVPGM Order-Only Path (#566)

## Similar Implementations

### The qualifying transform (already correct, just unreachable)

- **Location:** `src/mk/def_rules.mk:1690` (`MODULE_TO_PGM_RECIPE`) and
  `src/mk/def_rules.mk:1757` (`BND_TO_SRVPGM_RECIPE`)
- **Relevance:** `$(subst .LIB,,$(subst /QSYS.LIB/,,$|))` already turns
  `/QSYS.LIB/QICSS.LIB/QYCDCUSG.SRVPGM` into the correctly-qualified
  `QICSS/QYCDCUSG.SRVPGM`. The transform itself needs no changes — the bug is
  purely that it's assigned to `externalsrvpgms` one step too late to be seen
  by `BNDSRVPGMPATH`'s computation in `PGM_VARIABLES`/`SRVPGM_VARIABLES`.
- **Key pattern:** move the assignment earlier in the recipe; don't touch the
  transform itself.

## Issue History

- [#566](https://github.com/IBM/ibmi-tobi/issues/566) — this fix's source
  issue, opened after the FTPSAUD project's real-world investigation.
- [#565](https://github.com/IBM/ibmi-tobi/issues/565) (already fixed) — the
  `BNDDIR`-on-`CRTPGM` bug, hit as attempt 1 in the same investigation; see
  `agent-os/specs/2026-09-10-0938-fix-bnddir-crtpgm/`.
- [#564](https://github.com/IBM/ibmi-tobi/issues/564) (referenced in #566) —
  `launch`'s `POSTCMD` exit code being ignored; the cosmetic issue behind
  FTPSAUD's now-removed `POSTCMD` workaround always reporting build failure.
- [#501](https://github.com/IBM/ibmi-tobi/issues/501) (referenced in #566) —
  prior art: qualified modules on `CRTPGM` resolved by listing
  `$(LIB)/NAME.MODULE` as a dependency; doesn't cover external `*SRVPGM`s.
- [#341](https://github.com/IBM/ibmi-tobi/issues/341) (referenced in #566) —
  proposed command-replacement mechanism for custom recipes; a cleaner
  escape hatch than `POSTCMD` for cases like this.

## FTPSAUD project history

`C:\DEV\GitHub\Harris\FTPSAUD\QRPGLESRC\Rules.mk` documents the three failed
attempts (BNDDIR, order-only prerequisite, regular prerequisite) before the
`POSTCMD` workaround, and was later updated to use the working `BNDDIR`
approach once `#565` was fixed. This `#566` fix offers an alternative,
`*BNDDIR`-object-free path for the same underlying need.
