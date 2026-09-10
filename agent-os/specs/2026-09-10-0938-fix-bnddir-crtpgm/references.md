# References for Fix BNDDIR on CRTPGM

## Similar Implementations

### CRTSRVPGMFLAGS BNDDIR clause

- **Location:** `src/mk/def_rules.mk:505`
- **Relevance:** This is the exact pattern being mirrored. Issue #417 added
  `BNDDIR($(call ESCAPE_FOR_SLASH,$(call replace_DOLLARESCAPE,$(BNDDIR))))`
  to `CRTSRVPGMFLAGS` (commit `926851b`, "Additional support for # and $"),
  fixing the same problem for `.SRVPGM` targets that #565 reports for `.PGM`
  targets.
- **Key patterns:** Reuses the existing `ESCAPE_FOR_SLASH` and
  `replace_DOLLARESCAPE` macros already defined in `def_rules.mk` — no new
  macro needed, just apply the same call to `CRTPGMFLAGS`.

## Issue History

- [#565](https://github.com/IBM/ibmi-tobi/issues/565) — this fix's source
  issue: `BNDDIR` override silently ignored on `CRTPGM`.
- [#417](https://github.com/IBM/ibmi-tobi/issues/417) (referenced in #565) —
  the original fix, for `CRTSRVPGM`/`.SRVPGM` targets, in commit `926851b`.
- [#356](https://github.com/IBM/ibmi-tobi/issues/356) (referenced in #565) —
  earlier question about getting a binding directory added to `CRTSRVPGM`;
  the `CRTSRVPGM` half of the same underlying gap.
