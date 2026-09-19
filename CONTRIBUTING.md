# Contributing

Short version: **do not edit `.agents/skills/`.** Everything in it is generated and the next run overwrites it.

## Where the text lives

The skills are written once and published twice. The source is [awesome-copilot-agent-skills](https://github.com/kesslernity/awesome-copilot-agent-skills), which holds the same files in a category tree; `tools/generate.py` flattens that tree into this one. A correction made upstream reaches both repositories. A correction made here reaches neither, and disappears on the next generate.

So:

| Change | Where |
|---|---|
| A skill's wording, procedure, output columns or description | Upstream, in `skills/<category>/<name>/SKILL.md` |
| A reference file | Upstream, in the same folder |
| Something that must differ **because the runtime is Mistral** | Here, in `overrides/<name>/` |
| The flattening, the term map, the checks, the README table | Here, in `tools/generate.py` |
| A rule the checker should enforce | Here, in `tools/verify.py`, with a case in `tools/selftest.py` |

`overrides/` is deliberately small. It exists for text that is wrong on Mistral rather than merely differently worded, and today it holds one skill. Read [`overrides/README.md`](overrides/README.md) before adding a second.

## The loop

```bash
python3 tools/generate.py --source ../awesome-copilot-agent-skills
python3 tools/verify.py
python3 tools/selftest.py
```

Then commit `.agents/skills/`, `MANIFEST.json` and `README.md` together with whatever you changed. The generated tree is checked in on purpose: people install this repository by copying a folder, and a tree that only exists after you run a script is not that.

CI, and anyone reviewing, runs:

```bash
python3 tools/generate.py --check    # exits 1 if the committed tree no longer matches its source
```

## If the generator stops

It is meant to. Each of these aborts the whole run rather than writing a bad skill:

- a front matter `name` that does not match its folder (Vibe itself only warns here and loads the front matter name, which is precisely why the generator will not let one through),
- front matter carrying anything other than `name` and `description`,
- a name that fails `^[a-z0-9]+(-[a-z0-9]+)*$`,
- a description over 1,024 characters,
- an override patch whose anchor text no longer matches upstream exactly once.

The last one is the common case. It means the upstream body was reworded and the patch would either miss or hit twice. Read the new upstream text, decide whether the override is still needed, and update `overrides/<name>/patch.json`. Do not widen the anchor to make it match again.

## If you add a rule to the checker

Add the case to `tools/selftest.py` in the same commit. It builds a deliberately broken skill per rule and asserts `verify.py` rejects it, plus one correct skill it must pass. A checker with no failing case is a checker nobody has proven runs, which on a runtime that fails silently is worse than no checker at all.

## House rules the text keeps

Three things are not style preferences and a pull request that breaks them will be asked to change:

- **Every output is a draft.** No skill approves, authorises, signs off or decides, and every description says so.
- **Missing data is named UNKNOWN**, never filled in with a plausible value.
- **Nothing is a safety authorisation.** No permit to work, isolation, confined space entry, job safety analysis, incident classification or inspection sign-off. AI prepares, a qualified human decides.

Also: no em dashes, and descriptions state when to use the skill and when not to, because the description is the whole routing decision.

## Licence

Contributions are accepted under CC BY-SA 4.0, the licence this repository ships under.
