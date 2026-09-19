# Fix pseudo-source "+" continuation ambiguity (#376 item 3) — Shaping Notes

## Scope

Bug fix: a literal `+` inside pseudo-source command text (e.g. `ADDMSGD ...
MSG('...shift+F6...')`) is misread as a line-continuation marker when it
happens to be the last non-whitespace-adjacent character on a physical
source line, corrupting the resulting command. Reported as item 3 of
[IBM/ibmi-tobi#376](https://github.com/IBM/ibmi-tobi/issues/376).

## Decisions

- Fix in both `extractAndLaunch` and `extractPseudoSrc` — the identical
  buggy regex is duplicated in both, and `MSGF_RECIPE` (and several other
  pseudo-source recipes) call both against the same source file.
- Require the continuation `+` to be preceded by whitespace and be the
  absolute last character on the line, rather than trying to detect
  "literal vs. intentional" some other way (e.g. an explicit escape
  convention). This retroactively fixes the reporter's existing file with no
  source changes needed on their end, since real-world literal `+`s (like
  `shift+F6`) are essentially never preceded by whitespace, while genuine
  continuation markers naturally are when a human types them.
- Also fixes a related silent-truncation bug found while reading the code:
  the old strip (`sed 's/\+\S*$//'`) removed the `+` *and* any non-whitespace
  text after it, not just the `+` itself.
- No automated test added — bash utility scripts, not exercised by pytest;
  verified the new logic directly via a standalone bash sanity check instead
  (see `plan.md`), full verification needs a real IBM i build.

## Context

- **Visuals:** None — backend shell-script fix.
- **References:** `docs/welcome/features.md`'s pseudo-source section
  documents the `!`-prefix (suppress errors) but never documents
  `+`-continuation at all — this feature is undocumented, and no test/example
  in the repo exercises it, which is why tightening its trigger condition is
  considered low-risk.
- **Product alignment:** N/A — no `agent-os/product/` folder exists in this
  repo.

## Standards Applied

`build/pseudo-source-dsl.md` documents the `+`-continuation syntax this fix
changes — worth revisiting that standard once this lands, to note the
tightened whitespace-before-`+` requirement.
