# Installing

Three places Mistral Vibe looks, and one that it does not.

## Project: `.agents/skills/`

The skills travel with the repository, so everyone who clones it gets them and the set is reviewable in pull requests.

```bash
git clone https://github.com/kesslernity/awesome-mistral-vibe-skills.git /tmp/amvs
mkdir -p .agents/skills
cp -R /tmp/amvs/.agents/skills/* .agents/skills/
```

`.vibe/skills/` works identically. `.agents/` is the vendor-neutral spelling, which is why this repository publishes there; `.vibe/` is Vibe's own.

Discovery walks **down** from the working directory, not up. It descends the whole tree and collects every `.vibe/skills` and `.agents/skills` it meets, so a skills directory in a subproject is found too, and starting Vibe in a subdirectory finds what is at or below that subdirectory and nothing above it.

## User: `~/.vibe/skills/`

Every project, no per-repository setup.

```bash
git clone https://github.com/kesslernity/awesome-mistral-vibe-skills.git /tmp/amvs
mkdir -p ~/.vibe/skills
cp -R /tmp/amvs/.agents/skills/* ~/.vibe/skills/
```

`$VIBE_HOME` moves this, if it is set.

## Config: `skill_paths`

Point Vibe at the clone and skip copying altogether. Updating is then `git pull`.

```toml
# ~/.vibe/config.toml
skill_paths = ["/path/to/awesome-mistral-vibe-skills/.agents/skills"]
```

`skill_paths` is searched **first**, ahead of the project and user directories, which matters for the duplicate rule below.

## Chat, where there is no filesystem

Open the skills panel, create a skill, fill the three fields: title, description, and the SKILL.md body. There is no folder and no reference files, so a skill that reads `references/<file>.md` needs that content pasted into the body or dropped in as an attachment.

## Selecting a subset

You rarely want all 137 active at once. Both filters take glob patterns and match on the skill name:

```toml
enabled_skills  = ["*-review", "meeting-*", "invoice-exception-review"]
disabled_skills = ["sharepoint-*"]
```

## Confirm it worked

```bash
vibe                                    # type / and look for the skill names
python3 tools/verify.py ~/.vibe/skills  # or whichever directory you installed into
```

`verify.py` runs Mistral's own `SkillMetadata` schema when `mistral-vibe` is importable, and a mirror of it when it is not. It tells you which one it used.

## Five things that fail quietly

**A project install only loads in a trusted folder.** `.agents/skills` and `.vibe/skills` inside a repository are read only once Vibe has recorded the working directory, or one of its ancestors, as trusted in `~/.vibe/trusted_folders.toml`. The trust dialog appears at startup when the folder has something worth trusting in it, and never in your home directory. Answer no once and the answer is kept: the skills sit on disk, the folder sits in the untrusted list, and nothing on screen connects the two. `~/.vibe/skills` has no such gate, which is the reason to start there while you are testing.

**Discovery does not recurse.** Vibe lists the children of a skills directory and looks for `<child>/SKILL.md`. One level, no deeper. Keeping the category folders would hide all 137, with no message. This is the single reason the published layout is flat.

```
.agents/skills/invoice-exception-review/SKILL.md          found
.agents/skills/finance/invoice-exception-review/SKILL.md  invisible
```

**A skill that fails to parse produces nothing, not an error.** The loader catches the exception, logs a warning, and returns `None`. No screen output, no non-zero exit code. Run `verify.py` before you trust an install.

**Descriptions are capped at 1,024 characters, and the cap is hard.** At 1,025 validation fails and the skill vanishes by the rule above. Discovery loads the name and description only, so the description is also the entire routing decision: the body cannot rescue a description that never says when to use the skill.

**`~/.agents/skills` is not read.** `.agents/skills` is a project path. The user-level directory is `~/.vibe/skills`. Installing to `~/.agents/skills` looks right, does nothing, and says nothing.

## Two more worth knowing

**First definition wins.** If the same skill name exists in more than one search path, the first one found is kept and the rest are dropped with a debug log line. Order is `skill_paths`, then project, then user. So a project copy shadows your personal copy, and a `skill_paths` entry shadows both.

**The name in the front matter beats the folder name.** If they disagree, the skill loads under the front matter name and only logs a warning. Your slash command is then not what the folder says. `verify.py` warns on this.

## Removing them

```bash
rm -rf ~/.vibe/skills          # or the specific folders you copied
```

Or drop the `skill_paths` entry. Nothing is installed outside these directories and nothing runs at install time.
