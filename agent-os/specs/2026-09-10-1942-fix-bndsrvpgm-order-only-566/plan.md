# Fix #566 (path 1 only): order-only SRVPGM prerequisites never reach BNDSRVPGM

## Context

[GitHub issue #566](https://github.com/IBM/ibmi-tobi/issues/566) documents two
independent bugs that stop TOBi from binding an external, not-TOBi-built
service program (e.g. `QICSS/QYCDCUSG`) to a `.PGM`/`.SRVPGM` target via
`BNDSRVPGM`. We're fixing **only path 1** here — the order-only-prerequisite
path, which is dead code — and deliberately leaving path 2 (regular
prerequisites losing their library qualifier) as a separate, riskier decision
since it changes existing output for locally-built service programs too.

Confirmed directly against the current code (`src/mk/def_rules.mk`):
`PGM_VARIABLES` (line 1559) and `SRVPGM_VARIABLES` (line 1738) compute
`BNDSRVPGMPATH` from `$(externalsrvpgms)`, but `externalsrvpgms` is only
assigned *afterward*, in `MODULE_TO_PGM_RECIPE` (line 1690) and
`BND_TO_SRVPGM_RECIPE` (line 1757) — each of which calls
`$(PGM_VARIABLES)`/`$(SRVPGM_VARIABLES)` as their very first line. So an
order-only prerequisite like `| /QSYS.LIB/QICSS.LIB/QYCDCUSG.SRVPGM` is always
read too late to affect `BNDSRVPGMPATH`, and the generated command always
renders `bndsrvpgm(*NONE)` — even though the diagnostic `echo_cmd` line right
above it *does* read `$|` directly and prints the service program as if it
were included, making the build's own log misleading.

A `grep` across `def_rules.mk` confirms `externalsrvpgms`/`BNDSRVPGMPATH` have
exactly these 4 references (2 reads, 2 writes) — nothing else depends on
current behavior, so this is a fully self-contained ordering fix.

## Approach

Move the `$(eval externalsrvpgms := ...)` line to before the
`$(PGM_VARIABLES)`/`$(SRVPGM_VARIABLES)` call in each recipe, so the variable
is populated before anything reads it. This is exactly suggestion #1 from the
issue. No other lines change — `PGM_VARIABLES`/`SRVPGM_VARIABLES` and the rest
of each recipe are untouched, and path 2's `$(notdir $^)` qualifier-stripping
is left exactly as-is (out of scope here).

**File:** `src/mk/def_rules.mk` — `MODULE_TO_PGM_RECIPE` and
`BND_TO_SRVPGM_RECIPE`.

The `$(eval externalsrvpgms := ...)` expression itself is unchanged — it only
reads `$|` (an automatic variable available regardless of ordering), so moving
it earlier is safe and doesn't need any other adjustment.

## Task Breakdown

### Task 1: Save spec documentation

Create `agent-os/specs/2026-09-10-1942-fix-bndsrvpgm-order-only-566/` with
this plan, `shape.md`, and `references.md`.

### Task 2: Reorder `externalsrvpgms` assignment in both recipes

Edit `src/mk/def_rules.mk`: swap the two lines in `MODULE_TO_PGM_RECIPE` and
in `BND_TO_SRVPGM_RECIPE`.

### Task 3: Manual verification

No automated test invokes real `make` against these macros (same situation as
`#565`), so verification is manual:

1. Reproduce the issue's path 1 repro case:
   ```make
   FTPSAUD.PGM: CERTINV.MODULE DCMAPIS.MODULE FTPSAUD.MODULE | /QSYS.LIB/QICSS.LIB/QYCDCUSG.SRVPGM
   ```
2. Build it (`makei c -f FTPSAUD.PGM` or `makei b`) and confirm the generated
   `crtpgm` command now shows `bndsrvpgm(QICSS/QYCDCUSG)` — qualified — instead
   of `bndsrvpgm(*NONE)`, and that this matches what the `echo_cmd` diagnostic
   line already claimed (no more contradiction between log and command).
3. Confirm a `.PGM`/`.SRVPGM` target with **no** order-only SRVPGM
   prerequisite still renders `bndsrvpgm(*NONE)` unchanged (no regression).
4. Confirm a target using a *regular* (non-order-only) SRVPGM prerequisite is
   unaffected — still unqualified per path 2, which is intentionally untouched
   by this fix.
5. If this lets you drop the `*BNDDIR`-object workaround on FTPSAUD in favor of
   a plain order-only prerequisite, that's a nice end-to-end confirmation, but
   not required — the `BNDDIR` route from `#565` is already a valid, working
   solution for that project.
