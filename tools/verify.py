#!/usr/bin/env python3
"""Verify a skills directory the way Mistral Vibe loads it.

Why this exists. The loader catches every exception a skill file can raise,
writes one warning to its log, and returns nothing. A malformed skill produces
no message on screen and no non-zero exit code. It is simply not in the list,
and the first sign of trouble is an agent that quietly does not do the thing.
So the check has to happen before the skill ships, not after it fails.

The script reproduces the loader's own steps rather than approximating them:
the same front matter boundary regex, the same YAML parse, the same schema.
When mistral-vibe is installed it imports the real SkillMetadata and validates
against that. When it is not, it falls back to a mirror of the same constraints
and says so, so a pass is never mistaken for a pass against the real thing.

    python3 tools/verify.py                       # checks .agents/skills
    python3 tools/verify.py PATH [PATH ...]
    python3 tools/verify.py --headroom 100        # warn under N characters spare
    python3 tools/verify.py --json

Exit 1 on any failure. Warnings alone exit 0.
"""
import argparse, json, pathlib, re, sys

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required: pip install pyyaml")

FM_BOUNDARY = re.compile(r"^-{3,}\s*$", re.MULTILINE)   # vibe/core/skills/parser.py
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")       # vibe/core/skills/models.py
NAME_MAX, DESC_MAX, COMPAT_MAX = 64, 1024, 500
SCHEMA_KEYS = {"name", "description", "license", "compatibility",
               "metadata", "allowed-tools", "user-invocable"}
REF_LINE = re.compile(r"references/[A-Za-z0-9_-]+(?:\.[A-Za-z0-9]+)+")  # stops before sentence punctuation

# Built-in skill names that ship with the hosted work surface. A local skill of
# the same name is a collision the user has to resolve, not an override.
BUILTINS = {"deep-research", "skill-creator", "data-analysis", "document-review",
            "structured-extraction", "meeting-prep", "internal-comms",
            "stakeholder-translator", "challenge-my-thinking", "doc-coauthoring",
            "research-synthesis", "vibe-work-onboarding"}


CONFLICT = re.compile(r" \d+(\.[A-Za-z0-9]+)?$")   # "persona 2.md", the iCloud conflict copy

HOUSE_CLOSER = "Drafts for human review; never approves, authorises or signs off."
DASHES = "\u2014\u2013"   # em dash, en dash


def load_validator():
    """Return (validate, source). validate(dict) raises on invalid metadata."""
    try:
        from vibe.core.skills.models import SkillMetadata
    except Exception:
        def validate(fm):
            if not isinstance(fm.get("name"), str) or not fm["name"]:
                raise ValueError("name is required and must be a non-empty string")
            if len(fm["name"]) > NAME_MAX:
                raise ValueError(f"name is {len(fm['name'])} characters, the maximum is {NAME_MAX}")
            if not NAME_RE.match(fm["name"]):
                raise ValueError(f"name {fm['name']!r} does not match {NAME_RE.pattern}")
            d = fm.get("description")
            if not isinstance(d, str) or not d:
                raise ValueError("description is required and must be a non-empty string")
            if len(d) > DESC_MAX:
                raise ValueError(f"description is {len(d)} characters, the maximum is {DESC_MAX}")
            c = fm.get("compatibility")
            if c is not None and (not isinstance(c, str) or len(c) > COMPAT_MAX):
                raise ValueError(f"compatibility must be a string of at most {COMPAT_MAX} characters")
            if not isinstance(fm.get("user-invocable", False), bool):
                raise ValueError("user-invocable must be a boolean")
            return fm["name"], d
        return validate, "mirrored schema (mistral-vibe is not installed on this machine)"

    def validate(fm):
        m = SkillMetadata.model_validate(fm)
        return m.name, m.description
    import vibe
    return validate, f"mistral-vibe {getattr(vibe, '__version__', 'installed')} SkillMetadata"


def check_dir(base, headroom_at, validate, house=False):
    """Walk one skills directory exactly as discovery does: one level, then SKILL.md."""
    failures, warnings, rows = [], [], []
    if not base.is_dir():
        return [(str(base), "not a directory")], [], []

    stray = sorted(p.name for p in base.iterdir()
                   if p.is_dir() and not (p / "SKILL.md").is_file() and not p.name.startswith("."))
    for s in stray:
        nested = list((base / s).glob("*/SKILL.md"))
        if nested:
            failures.append((f"{base}/{s}", f"holds {len(nested)} skills one level deeper; "
                                            "discovery does not recurse, so all of them are invisible"))
        else:
            warnings.append((f"{base}/{s}", "no SKILL.md, so this folder is skipped"))

    for skill_dir in sorted(p for p in base.iterdir() if p.is_dir()):
        f = skill_dir / "SKILL.md"
        if not f.is_file():
            continue
        where = str(f)
        raw = f.read_text(encoding="utf-8")

        parts = FM_BOUNDARY.split(raw, 2)
        if len(parts) < 3 or parts[0].strip():
            failures.append((where, "missing or invalid front matter: the file must open with a "
                                    "delimiter line and close the block with a second one, with "
                                    "nothing before the first"))
            continue
        try:
            fm = yaml.safe_load(parts[1])
        except yaml.YAMLError as e:
            failures.append((where, f"invalid YAML front matter: {e}"))
            continue
        if fm is None:
            fm = {}
        if not isinstance(fm, dict):
            failures.append((where, "front matter parses to a "
                                    f"{type(fm).__name__}, it must be a mapping"))
            continue
        try:
            name, desc = validate(fm)
        except Exception as e:
            failures.append((where, f"schema rejects the metadata: {e}"))
            continue

        if name != skill_dir.name:
            warnings.append((where, f"name {name!r} does not match folder {skill_dir.name!r}; "
                                    "the skill loads under the front matter name, so the slash "
                                    "command is not the folder"))
        if name in BUILTINS:
            warnings.append((where, f"{name} collides with a built-in skill name"))
        spare = DESC_MAX - len(desc)
        if spare < headroom_at:
            warnings.append((where, f"description is {len(desc)} characters, {spare} short of the "
                                    f"{DESC_MAX} cap; one added clause drops the skill"))
        for key in sorted(set(fm) - SCHEMA_KEYS):
            warnings.append((where, f"front matter key {key!r} is not read by the schema and is "
                                    "silently ignored, so its text never reaches the agent"))
        if house:
            # Conventions of this repository, not of the runtime. Off by default so
            # verify.py stays usable on any skills directory; CI runs it with --house.
            if not desc.endswith(HOUSE_CLOSER):
                failures.append((where, "house rule: the description must end with "
                                        f"{HOUSE_CLOSER!r}, which is what states that the output "
                                        "is a draft a human still decides on"))
            if "Use when" not in desc:
                failures.append((where, "house rule: the description must say when to use the "
                                        "skill; discovery loads the description only, so nothing "
                                        "in the body can route the skill"))
            for rel, text in [("SKILL.md", raw)] + [
                    (str(r.relative_to(skill_dir)), r.read_text(encoding="utf-8"))
                    for r in sorted(skill_dir.rglob("*")) if r.is_file() and r.name != "SKILL.md"]:
                hit = next((c for c in DASHES if c in text), None)
                if hit:
                    line = next(i for i, l in enumerate(text.splitlines(), 1) if hit in l)
                    failures.append((f"{skill_dir}/{rel}:{line}",
                                     f"house rule: {'em' if hit == DASHES[0] else 'en'} dash"))

        for ref in sorted(set(REF_LINE.findall(parts[2]))):
            if not (skill_dir / ref).is_file():
                failures.append((where, f"names {ref} but that file is not in the folder"))

        refs = sorted(r for r in skill_dir.rglob("*") if r.is_file() and r.name != "SKILL.md")
        dupes = [r for r in refs if CONFLICT.search(r.stem)]
        for r in dupes:
            failures.append((str(r), "looks like a sync conflict copy of "
                                     f"{CONFLICT.sub('', r.stem)}{r.suffix}. The loader never reads "
                                     "it, so it costs nothing at runtime and everything in review: "
                                     "delete it before committing"))

        rows.append({"name": name, "path": str(f), "description_chars": len(desc),
                     "headroom": spare,
                     "reference_files": len(refs) - len(dupes)})
    return failures, warnings, rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="*", type=pathlib.Path)
    ap.add_argument("--headroom", type=int, default=50,
                    help="warn when a description has fewer than N characters spare (default 50)")
    ap.add_argument("--house", action="store_true",
                    help="also enforce this repository's own conventions: the draft closer, a "
                         "\"Use when\" clause, and no em or en dashes. Off by default so the "
                         "checker stays usable on any skills directory.")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    root = pathlib.Path(__file__).resolve().parent.parent
    bases = [p.expanduser().resolve() for p in args.paths] or [root / ".agents" / "skills"]

    validate, source = load_validator()
    failures, warnings, rows = [], [], []
    for b in bases:
        f, w, r = check_dir(b, args.headroom, validate, house=args.house)
        failures += f; warnings += w; rows += r

    seen = {}
    for r in rows:
        if r["name"] in seen:
            failures.append((r["path"], f"duplicate skill name, already defined at {seen[r['name']]}; "
                                        "the first one found wins and this copy is dropped"))
        else:
            seen[r["name"]] = r["path"]

    if args.json:
        print(json.dumps({"validator": source, "checked": [str(b) for b in bases],
                          "skills": len(rows), "failures": [list(x) for x in failures],
                          "warnings": [list(x) for x in warnings], "rows": rows}, indent=1))
        return 1 if failures else 0

    print(f"validator: {source}")
    for b in bases:
        print(f"checked:   {b}")
    for where, msg in failures:
        print(f"  FAIL  {where}\n        {msg}")
    for where, msg in warnings:
        print(f"  WARN  {where}\n        {msg}")
    if rows:
        tight = sorted(rows, key=lambda r: r["headroom"])[:3]
        print(f"\n{len(rows)} skills load, {sum(r['reference_files'] for r in rows)} reference files")
        print("tightest descriptions: " + ", ".join(f"{r['name']} ({r['headroom']} spare)" for r in tight))
    print(f"\n{len(failures)} failures, {len(warnings)} warnings")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
