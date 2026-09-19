# Fix: literal "+" in pseudo-source text misread as line continuation

## Context

[GitHub issue #376](https://github.com/IBM/ibmi-tobi/issues/376), item 3,
reports that an `ADDMSGD` command in a CL pseudo source file fails when its
message text contains a literal `+` (e.g. `"...Press F18 (shift+F6) for more
details."`). The reporter confirmed (in a follow-up comment, after a
maintainer asked for clarification) that the `+` is literal text, not
intended as continuation syntax.

Confirmed directly against the code — the pseudo-source line-continuation
detection is duplicated in two scripts:
[src/scripts/extractAndLaunch:31](src/scripts/extractAndLaunch:31) and
[src/scripts/extractPseudoSrc:16](src/scripts/extractPseudoSrc:16):

```bash
if [[ $line =~ .*\+\S*$ ]]; then
  linetmp=$(echo "$line" | sed 's/\+\S*$//')
  ...
```

This treats **any** `+` where everything from it to end-of-line is
non-whitespace as a continuation marker — including a `+` glued into the
middle of a word like `shift+F6`, with no escape mechanism to mark it as
literal. `MSGF_RECIPE` in `def_rules.mk` (the recipe handling `.MSGF`/
`ADDMSGD` pseudo-source — exactly the reported object type) calls both
scripts against the same source file, so both needed the same fix or they'd
disagree with each other.

A second, related bug in the same code: the strip step,
`sed 's/\+\S*$//'`, removes the `+` **and everything non-whitespace after
it**, not just the `+` itself — so a coincidental trailing `+something` (no
separating space) would be silently truncated, not merely mis-treated as
continuation.

This behavior is undocumented — `docs/welcome/features.md`'s pseudo-source
section documents the `!`-prefix (suppress errors) explicitly but never
mentions `+`-continuation at all, and no test or example in the repo
exercises it.

## Approach

Require the continuation `+` to be its own separate token: preceded by
whitespace, and the literal last character on the line (nothing following
it). This matches how anyone would naturally write an intentional
continuation marker (`...some command +`, mirroring native CL's own `+`/`-`
continuation-character convention), and fixes the reporter's exact existing
file with zero changes needed on their end, since `shift+F6` has no space
before its `+`.

**Files:** `src/scripts/extractAndLaunch`, `src/scripts/extractPseudoSrc`

```diff
-  if [[ $line =~ .*\+\S*$ ]]; then
-    linetmp=$(echo "$line" | sed 's/\+\S*$//')
+  if [[ $line =~ [[:space:]]\+$ ]]; then
+    linetmp="${line%+}"
```

(`extractPseudoSrc` keeps its existing `$`-escaping pipeline after the strip,
just swapping in the same corrected detection/strip.)

This also fixes the related truncation bug as a side effect, since `$` now
sits directly after `\+` with nothing allowed to follow.

## Task Breakdown

### Task 1: Save spec documentation

Create `agent-os/specs/2026-09-19-1357-fix-pseudo-source-plus-continuation-376/`
with this plan and `shape.md`.

### Task 2: Fix both scripts

Edit `src/scripts/extractAndLaunch` and `src/scripts/extractPseudoSrc` as
shown above.

### Task 3: Manual verification

No automated test exists for either script (bash utilities, not exercised by
pytest). Sanity-tested the new regex/strip logic directly in bash against
representative cases:
- Reported bug case (`...shift+F6...`, no space before `+`) → correctly
  treated as literal, no continuation.
- Genuine continuation (`...text +`, space before trailing `+`) → still
  triggers continuation correctly.
- Edge case (`1+2`, bare plus, no space, nothing trailing) → correctly left
  as literal.

Remaining verification needs a real IBM i system:
1. Reproduce the issue: an `.MSGF` pseudo-source file with an `ADDMSGD`
   command whose `MSG(...)` text contains a `+` with no preceding space
   (e.g. `(shift+F6)`), ideally wrapped across two physical source lines the
   same way the reporter's was.
2. Build it (`makei c -f <target>.MSGF` or `makei b`) and confirm the
   `ADDMSGD` command now succeeds, with the full message text intact
   (including the literal `+`).
3. If a genuine multi-line pseudo-source command can be constructed (command
   text ending in `... +` with a space), confirm it still continues onto the
   next line correctly — a no-regression check for the (undocumented, but
   possibly relied-upon) continuation feature itself.
