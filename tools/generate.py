#!/usr/bin/env python3
"""Generate .agents/skills/ from the source skill repo.

The skills in this repository are NOT hand written. They are generated from
kesslernity/awesome-copilot-agent-skills, which holds the same 137 SKILL.md
files in a category tree. Both repositories therefore carry one text, so a
correction upstream reaches Mistral Vibe on the next run of this script.

What the generator changes, and nothing else:

  1. Layout. Mistral Vibe discovers skills one level deep: SkillManager
     iterates a skills directory and looks for <dir>/SKILL.md. A category
     tree is invisible to it. So skills/<category>/<name>/ becomes the flat
     .agents/skills/<name>/.
  2. Vendor terms. TERM_MAP below, applied to descriptions, bodies and
     reference files. It is deliberately tiny: 133 of the 137 bodies and 130
     of the 131 reference files contain no vendor term at all.
  3. Overrides. A skill whose content is genuinely runtime specific gets a
     replacement under overrides/<name>/. Today that is one skill, and the
     reason is in overrides/README.md.

    python3 tools/generate.py                     # source: ../awesome-copilot-agent-skills
    python3 tools/generate.py --source PATH
    python3 tools/generate.py --check             # fail if the output would change
"""
import argparse, hashlib, json, pathlib, re, subprocess, sys, textwrap

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / ".agents" / "skills"
OVERRIDES = ROOT / "overrides"
DEFAULT_SOURCE = ROOT.parent / "awesome-copilot-agent-skills"

# Applied longest first so the article form wins before the bare form.
TERM_MAP = {
    "a declarative agent": "an agent",
    "declarative agents": "agents",
    "declarative agent": "agent",
}

FM_BOUNDARY = re.compile(r"^-{3,}\s*$", re.MULTILINE)   # the regex Mistral's parser uses
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")       # the pattern SkillMetadata enforces
DESC_MAX = 1024                                         # SkillMetadata max_length


def retarget(text):
    """Apply TERM_MAP and report which terms fired."""
    fired = []
    for old, new in sorted(TERM_MAP.items(), key=lambda kv: -len(kv[0])):
        if old in text:
            fired.append(old)
            text = text.replace(old, new)
    return text, fired


def split_skill(raw, where):
    parts = FM_BOUNDARY.split(raw, 2)
    if len(parts) < 3 or parts[0].strip():
        sys.exit(f"{where}: no parseable front matter")
    fm = yaml.safe_load(parts[1])
    if not isinstance(fm, dict):
        sys.exit(f"{where}: front matter is not a mapping")
    return fm, parts[2]


def render(name, description):
    """House front matter: folded scalar, two-space indent, wrapped at 98 columns."""
    body = "  " + "\n  ".join(
        textwrap.wrap(description, width=98, break_long_words=False, break_on_hyphens=False)
    )
    return f"---\nname: {name}\ndescription: >-\n{body}\n---"


def source_commit(src):
    try:
        out = subprocess.run(["git", "-C", str(src), "rev-parse", "HEAD"],
                             capture_output=True, text=True, timeout=10)
        return out.stdout.strip() or "UNKNOWN"
    except Exception:
        return "UNKNOWN"


def fill_markers(path, blocks):
    """Replace the text between <!-- key:start --> and <!-- key:end --> markers.

    Markers, not {{PLACEHOLDER}} tokens. A placeholder is consumed the first time
    it is filled, so the second run has nothing to substitute and writes the
    literal token into the page. Markers survive every run.
    """
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8")
    filled = []
    for key, value in blocks.items():
        pat = re.compile(rf"(<!-- {key}:start -->).*?(<!-- {key}:end -->)", re.S)
        if not pat.search(text):
            continue
        text = pat.sub(lambda m: m.group(1) + value + m.group(2), text)
        filled.append(key)
    path.write_text(text, encoding="utf-8")
    return filled


CATEGORY_TITLES = {
    "customer-support": "Customer support",
    "daily-briefings": "Daily briefings",
    "dashboards-microapps": "Dashboards and micro-apps",
    "data-analytics": "Data and analytics",
    "data-privacy": "Data privacy",
    "email-inbox": "Email and inbox",
    "engineering-document-control": "Engineering document control",
    "engineering-pfd-to-pid": "Engineering, PFD to P&ID",
    "executive": "Executive",
    "executive-review": "Executive review",
    "finance": "Finance",
    "hr-people": "HR and people",
    "it-operations": "IT operations",
    "learning-development": "Learning and development",
    "legal-contracts": "Legal and contracts",
    "marketing-communications": "Marketing and communications",
    "meetings": "Meetings",
    "meta-skills": "Meta skills",
    "operations": "Operations",
    "procurement": "Procurement",
    "product-management": "Product management",
    "project-management": "Project management",
    "quality-audit": "Quality and audit",
    "reporting-analysis": "Reporting and analysis",
    "risk-ethics-compliance": "Risk, ethics and compliance",
    "sales-bd": "Sales and business development",
    "security-grc": "Security and GRC",
    "trade-compliance": "Trade compliance",
    "writing-communication": "Writing and communication",
}


def one_liner(description, soft=200, hard=240):
    """The first clause of a description, for the directory table.

    The description itself is the routing text and stays whole in the file.
    This is only the human-facing cell, so it cuts at the first natural
    boundary rather than at a character count wherever it can.
    """
    text = description.split(" Use when")[0].strip()
    colon = text.find(": ")
    if 0 < colon <= soft:
        return text[:colon] + "."
    stop = text.find(". ")
    if 0 < stop <= hard:
        return text[:stop + 1]
    if len(text) <= hard:
        return text if text.endswith(".") else text + "."
    return text[:text.rfind(" ", 0, hard)].rstrip(",;:") + " ..."


def directory_table(records, source_descriptions):
    by_cat = {}
    for r in records:
        by_cat.setdefault(r["category"], []).append(r)
    untitled = sorted(set(by_cat) - set(CATEGORY_TITLES))
    if untitled:
        print(f"  note: no title for {', '.join(untitled)}, using the slug")
    lines = []
    for cat in sorted(by_cat, key=lambda c: CATEGORY_TITLES.get(c, c)):
        rows = sorted(by_cat[cat], key=lambda r: r["name"])
        title = CATEGORY_TITLES.get(cat, cat.replace("-", " ").capitalize())
        lines += ["", f"### {title} ({len(rows)})", "",
                  "| Skill | What it does |", "|---|---|"]
        for r in rows:
            cell = one_liner(source_descriptions[r["name"]]).replace("|", "\\|")
            lines.append(f"| [`{r['name']}`](.agents/skills/{r['name']}/) | {cell} |")
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=pathlib.Path, default=DEFAULT_SOURCE)
    ap.add_argument("--check", action="store_true",
                    help="write nothing; exit 1 if the tree or the manifest would change")
    args = ap.parse_args()

    src = args.source.expanduser().resolve()
    if not (src / "skills").is_dir():
        sys.exit(f"source repo not found: {src}/skills")

    staged = {}     # name -> {files: {relpath: text}, record: {...}}
    for skill_md in sorted((src / "skills").glob("*/*/SKILL.md")):
        folder = skill_md.parent
        category = folder.parent.name
        name = folder.name
        fm, body = split_skill(skill_md.read_text(encoding="utf-8"), skill_md)

        if fm.get("name") != name:
            sys.exit(f"{skill_md}: front matter name {fm.get('name')!r} != folder {name!r}")
        if set(fm) != {"name", "description"}:
            sys.exit(f"{skill_md}: unexpected front matter keys {sorted(set(fm) - {'name', 'description'})}")

        desc, d_fired = retarget(" ".join(str(fm["description"]).split()))
        body, b_fired = retarget(body)

        ov = OVERRIDES / name
        overridden = []
        ov_desc = ov / "description.txt"
        if ov_desc.is_file():
            desc = " ".join(ov_desc.read_text(encoding="utf-8").split())
            overridden.append("description")

        ov_patch = ov / "patch.json"
        if ov_patch.is_file():
            for i, edit in enumerate(json.loads(ov_patch.read_text(encoding="utf-8"))):
                if body.count(edit["old"]) != 1:
                    sys.exit(f"{name}: patch {i} matches {body.count(edit['old'])} times, "
                             f"it must match exactly once. Upstream text changed; update the patch.")
                body = body.replace(edit["old"], edit["new"], 1)
                overridden.append(f"body patch {i}: {edit['why']}")

        files = {"SKILL.md": render(name, desc) + body}

        for ref in sorted(folder.glob("references/*")):
            if not ref.is_file() or ref.name.startswith("."):
                continue
            ov_ref = ov / "references" / ref.name
            if ov_ref.is_file():
                text = ov_ref.read_text(encoding="utf-8")
                overridden.append(f"references/{ref.name}")
            else:
                text, r_fired = retarget(ref.read_text(encoding="utf-8"))
                b_fired += r_fired
            files[f"references/{ref.name}"] = text

        # invariants checked before anything is written
        if not NAME_RE.match(name) or len(name) > 64:
            sys.exit(f"{name}: fails the SkillMetadata name pattern")
        if not 1 <= len(desc) <= DESC_MAX:
            sys.exit(f"{name}: description is {len(desc)} characters, the cap is {DESC_MAX}")

        staged[name] = {
            "files": files,
            "record": {
                "name": name,
                "source": f"skills/{category}/{name}",
                "category": category,
                "description_chars": len(desc),
                "headroom": DESC_MAX - len(desc),
                "reference_files": sorted(k for k in files if k != "SKILL.md"),
                "terms_rewritten": sorted(set(d_fired + b_fired)),
                "overridden": overridden,
                "sha256": hashlib.sha256(files["SKILL.md"].encode("utf-8")).hexdigest()[:16],
            },
        }

    manifest = {
        "generated_from": {
            "repository": "kesslernity/awesome-copilot-agent-skills",
            "path": str(src),
            "commit": source_commit(src),
        },
        "generator": "tools/generate.py",
        "term_map": TERM_MAP,
        "skill_count": len(staged),
        "skills": [staged[n]["record"] for n in sorted(staged)],
    }
    manifest_text = json.dumps(manifest, indent=1) + "\n"

    # what is on disk now
    current = {}
    if OUT.is_dir():
        for p in sorted(OUT.rglob("*")):
            if p.is_file() and not p.name.startswith("."):
                current[str(p.relative_to(OUT))] = p.read_text(encoding="utf-8", errors="replace")
    wanted = {f"{n}/{rel}": text for n, s in staged.items() for rel, text in s["files"].items()}

    added = sorted(set(wanted) - set(current))
    removed = sorted(set(current) - set(wanted))
    changed = sorted(k for k in set(wanted) & set(current) if wanted[k] != current[k])
    mpath = ROOT / "MANIFEST.json"
    manifest_differs = (not mpath.is_file()) or mpath.read_text(encoding="utf-8") != manifest_text

    if args.check:
        drift = added or removed or changed or manifest_differs
        for label, items in (("added", added), ("removed", removed), ("changed", changed)):
            for k in items:
                print(f"  {label}: {k}")
        if manifest_differs:
            print("  changed: MANIFEST.json")
        print(f"CHECK: {'DRIFT, run tools/generate.py' if drift else 'clean'}")
        return 1 if drift else 0

    # Write in place. An earlier version wiped OUT with shutil.rmtree and rebuilt
    # all 268 files every run; on an iCloud-synced Desktop that churn made the sync
    # daemon spawn "<name> 2.md" conflict duplicates, 95 of them in one run. The
    # loader ignores them (it reads SKILL.md only) but git would not. Touch only
    # what actually differs, and delete stale paths by name.
    for rel in removed:
        (OUT / rel).unlink()
    for rel in added + changed:
        f = OUT / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(wanted[rel], encoding="utf-8")
    for d in sorted(OUT.rglob("*"), reverse=True):
        if d.is_dir() and not any(d.iterdir()):
            d.rmdir()
    mpath.write_text(manifest_text, encoding="utf-8")

    descs = {n: " ".join(split_skill(staged[n]["files"]["SKILL.md"], n)[0]["description"].split())
             for n in staged}
    tightest = sorted(manifest["skills"], key=lambda r: r["headroom"])[0]
    filled = fill_markers(ROOT / "README.md", {
        "n-skills": str(len(staged)),
        "badge-skills": (f"[![Skills](https://img.shields.io/badge/skills-{len(staged)}-blue)]"
                         "(.agents/skills/)"),
        "n-categories": str(len({r["category"] for r in manifest["skills"]})),
        "n-references": str(sum(len(r["reference_files"]) for r in manifest["skills"])),
        "tightest-headroom": str(tightest["headroom"]),
        "tightest-skill": tightest["name"],
        "source-commit": manifest["generated_from"]["commit"][:12],
        "skill-directory": "\n" + directory_table(manifest["skills"], descs),
    })

    rewritten = [r["name"] for r in manifest["skills"] if r["terms_rewritten"]]
    over = [r["name"] for r in manifest["skills"] if r["overridden"]]
    tight = sorted((r["headroom"], r["name"]) for r in manifest["skills"])[:3]
    print(f"{len(staged)} skills written to .agents/skills/ from {src}")
    print(f"  source commit      {manifest['generated_from']['commit'][:12]}")
    print(f"  reference files    {sum(len(r['reference_files']) for r in manifest['skills'])}")
    print(f"  term rewrites      {len(rewritten)}: {', '.join(rewritten) or 'none'}")
    print(f"  overridden         {len(over)}: {', '.join(over) or 'none'}")
    print(f"  tightest headroom  " + ", ".join(f"{n} ({h} chars)" for h, n in tight))
    print(f"  added {len(added)}  changed {len(changed)}  removed {len(removed)}")
    print(f"  README markers     {len(filled)} filled")
    return 0


if __name__ == "__main__":
    sys.exit(main())
