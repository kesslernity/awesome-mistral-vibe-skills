# Overrides

Everything in `.agents/skills/` is generated from the source repository. An override is the
exception: a file here replaces or edits the generated text for one skill, and the generator
records it in `MANIFEST.json` so the deviation is visible rather than buried in a diff.

Three forms, all optional, all keyed by skill name:

| File | Effect |
|---|---|
| `overrides/<name>/description.txt` | replaces the front matter description |
| `overrides/<name>/patch.json` | a list of `{old, new, why}` edits applied to the body |
| `overrides/<name>/references/<file>.md` | replaces that reference file |

A `patch.json` edit must match its `old` string **exactly once**. If upstream rewrites that
passage the count changes, the generator stops, and the override gets reviewed instead of
silently going stale.

## Why anything is overridden at all

Only where the source text describes another runtime's behaviour and would be wrong here.
Vendor nouns are not a reason: those go through the generator's `TERM_MAP`, which today holds
three entries and touches three skills.

### skill-file-reviewer

This is the one skill whose subject *is* the format, so a ported copy would review Mistral skill
files against another runtime's rules. Four differences make that wrong rather than merely
imprecise:

1. **Unknown front matter keys are ignored, not rejected.** The schema reads `name`,
   `description`, `license`, `compatibility`, `metadata`, `allowed-tools` and `user-invocable`.
   Anything else is dropped without complaint, so "exactly two keys" is a house rule here, and
   an extra key is dead text rather than a failed upload.
2. **A name that does not match its folder is a warning, not a rejection.** The skill loads
   under the front matter name, so the slash command is not the folder the author is looking at.
3. **Discovery is one level deep.** A category folder between the skills directory and the skill
   hides every skill inside it. That belongs in the rule set, because it is the single most
   likely reason a correct file does not appear.
4. **Failure is silent.** The loader catches the exception, logs a warning and returns nothing.
   No error on screen, no non-zero exit code, no skill. A reviewer who assumes the runtime will
   complain is reviewing for a runtime that complains.

The override therefore supplies a rewritten `references/skill-format-rules.md` with an `LD` group
for loader behaviour, revised `FM` severities, a `CN-08` rule for the terminal-versus-chat split,
an `SB-10` rule for `allowed-tools`, and a `description.txt` and `patch.json` that keep the skill
body honest about all of it. Everything else in the skill, the skeleton, the safety boundaries,
the report template, is the upstream text unchanged.
