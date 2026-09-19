#!/usr/bin/env python3
"""Check the checker.

tools/verify.py exists because the runtime fails silently. A verifier that also
fails silently would be worse than none, so every rule it claims to enforce gets
a deliberately broken skill here and has to reject it. The test also builds one
correct skill and requires a clean pass, so a verifier that rejected everything
would not survive either.

    python3 tools/selftest.py

Exit 1 if any case does not behave as stated.
"""
import json, pathlib, subprocess, sys, tempfile

VERIFY = pathlib.Path(__file__).resolve().parent / "verify.py"

GOOD = """---
name: good-skill
description: >-
  Produces a control case from nothing at all, so a verifier that rejects every input fails this
  test. Use when the user asks to "run the self test". Drafts for human review; never approves,
  authorises or signs off.
---
# Good skill

## Purpose
A file that must pass.
"""

# name -> (files in the skill folder, substring that must appear in a FAIL line)
BAD = {
    "no-frontmatter": ({"SKILL.md": "# Just a heading\n\nNo front matter at all.\n"},
                       "missing or invalid front matter"),
    "text-before": ({"SKILL.md": "oops\n---\nname: text-before\ndescription: x\n---\nbody\n"},
                    "missing or invalid front matter"),
    "broken-yaml": ({"SKILL.md": "---\nname: broken-yaml\ndescription: a: b: c\n\tt\n---\nbody\n"},
                    "invalid YAML front matter"),
    "not-a-mapping": ({"SKILL.md": "---\n- one\n- two\n---\nbody\n"},
                      "must be a mapping"),
    "bad-name": ({"SKILL.md": "---\nname: Bad_Name\ndescription: a description\n---\nbody\n"},
                 "schema rejects the metadata"),
    "no-description": ({"SKILL.md": "---\nname: no-description\n---\nbody\n"},
                       "schema rejects the metadata"),
    "over-cap": ({"SKILL.md": "---\nname: over-cap\ndescription: >-\n  " + ("x" * 1025) + "\n---\nbody\n"},
                 "schema rejects the metadata"),
    "sync-conflict": ({"SKILL.md": GOOD.replace("good-skill", "sync-conflict"),
                       "references/persona.md": "real\n",
                       "references/persona 2.md": "the copy iCloud made\n"},
                      "sync conflict copy"),
    "missing-reference": ({"SKILL.md": "---\nname: missing-reference\ndescription: a description\n---\n"
                                       "# T\n\nReference files in this skill: references/nope.md.\n"},
                          "not in the folder"),
}
# warnings, not failures
WARN = {
    "name-mismatch": ({"SKILL.md": "---\nname: other-name\ndescription: a description\n---\nbody\n"},
                      "does not match folder"),
    "unknown-key": ({"SKILL.md": "---\nname: unknown-key\ndescription: a description\nalowed-tools: bash\n---\nbody\n"},
                    "not read by the schema"),
    "deep-research": ({"SKILL.md": "---\nname: deep-research\ndescription: a description\n---\nbody\n"},
                      "collides with a built-in"),
}


# each fails only with --house, and must pass without it
HOUSE = {
    "no-closer": ({"SKILL.md": GOOD.replace("good-skill", "no-closer").replace(
                       " Drafts for human review; never approves,\n  authorises or signs off.", "")},
                  "must end with"),
    "no-trigger": ({"SKILL.md": GOOD.replace("good-skill", "no-trigger").replace(
                       'Use when the user asks to "run the self test". ', "")},
                   "must say when to use"),
    "em-dash": ({"SKILL.md": GOOD.replace("good-skill", "em-dash").replace(
                     "# Good skill", "# Good skill \u2014 with a dash")},
                "em dash"),
}


def run(base, *extra):
    out = subprocess.run([sys.executable, str(VERIFY), str(base), "--json", "--headroom", "0", *extra],
                         capture_output=True, text=True)
    return json.loads(out.stdout)


def case(files_by_skill):
    tmp = pathlib.Path(tempfile.mkdtemp()) / "skills"
    for skill, files in files_by_skill.items():
        for rel, text in files.items():
            p = tmp / skill / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text, encoding="utf-8")
    return tmp


def main():
    bad = []

    r = run(case({"good-skill": {"SKILL.md": GOOD}}))
    if r["failures"] or r["warnings"] or r["skills"] != 1:
        bad.append(f"control: a correct skill did not pass cleanly: {r['failures']} {r['warnings']}")

    for name, (files, expect) in BAD.items():
        r = run(case({name: files}))
        joined = " ".join(m for _, m in r["failures"])
        if expect not in joined:
            bad.append(f"{name}: expected a failure saying {expect!r}, got {r['failures'] or 'nothing'}")

    for name, (files, expect) in WARN.items():
        r = run(case({name: files}))
        joined = " ".join(m for _, m in r["warnings"])
        if expect not in joined:
            bad.append(f"{name}: expected a warning saying {expect!r}, got {r['warnings'] or 'nothing'}")
        if r["failures"]:
            bad.append(f"{name}: should warn, not fail: {r['failures']}")

    for name, (files, expect) in HOUSE.items():
        base = case({name: files})
        r = run(base, "--house")
        if expect not in " ".join(m for _, m in r["failures"]):
            bad.append(f"{name}: expected a --house failure saying {expect!r}, got {r['failures']}")
        r = run(base)
        if r["failures"]:
            bad.append(f"{name}: a house rule must not fail without --house: {r['failures']}")

    # a category tree hides its skills, and discovery does not recurse
    tmp = pathlib.Path(tempfile.mkdtemp()) / "skills"
    (tmp / "a-category" / "nested-skill").mkdir(parents=True)
    (tmp / "a-category" / "nested-skill" / "SKILL.md").write_text(
        GOOD.replace("good-skill", "nested-skill"), encoding="utf-8")
    r = run(tmp)
    if "does not recurse" not in " ".join(m for _, m in r["failures"]):
        bad.append(f"category tree: expected a failure about recursion, got {r['failures']}")
    if r["skills"]:
        bad.append(f"category tree: reported {r['skills']} loadable skills, it should be 0")

    # two folders defining the same name: the first wins and the second is dropped
    r = run(case({"good-skill": {"SKILL.md": GOOD},
                  "copy-of-good": {"SKILL.md": GOOD}}))
    if "duplicate skill name" not in " ".join(m for _, m in r["failures"]):
        bad.append(f"duplicate name: expected a failure, got {r['failures']}")

    for line in bad:
        print(f"  FAIL  {line}")
    total = 1 + len(BAD) + len(WARN) + 2 * len(HOUSE) + 2
    print(f"\n{total - len(bad)}/{total} cases behave as stated")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
