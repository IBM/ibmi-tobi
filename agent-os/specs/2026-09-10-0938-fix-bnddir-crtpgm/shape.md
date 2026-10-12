# Fix BNDDIR on CRTPGM — Shaping Notes

## Scope

Bug fix: `private BNDDIR = ...` overrides on `.PGM` targets are accepted by the
`Rules.mk` parser but never reach the generated `CRTPGM` command, so the
binding directory is silently dropped. Reported as
[IBM/ibmi-tobi#565](https://github.com/IBM/ibmi-tobi/issues/565).

## Decisions

- Mirror the existing `CRTSRVPGMFLAGS` `BNDDIR` clause into `CRTPGMFLAGS`
  exactly, rather than inventing a new pattern — issue #417 already solved
  this for `.SRVPGM` targets, and #565 is that same gap for `.PGM` targets.
- No Python changes — `BNDDIR` is already parsed as a generic per-target
  override; only the Make-side macro was missing the clause.
- No automated test added — there is no existing test infrastructure that
  invokes real `make` against `def_rules.mk`, so verification is manual on an
  IBM i system, matching how issue #417's original fix was verified.

## Context

- **Visuals:** None — backend Makefile fix.
- **References:** `src/mk/def_rules.mk:505` (`CRTSRVPGMFLAGS`), the pattern
  being mirrored; see `references.md`.
- **Product alignment:** N/A — no `agent-os/product/` folder exists in this
  repo.

## Standards Applied

- `build/special-char-escaping.md` — the value flowing into the new
  `BNDDIR(...)` clause may contain `#`/`$` from the same escaping chain this
  standard documents.
- `build/make-special-char-unescaping.md` — the fix directly uses
  `ESCAPE_FOR_SLASH`/`replace_DOLLARESCAPE`, the Make-side half of that chain.
