# Awesome Mistral Vibe CLI Skills

**These are CLI skills, not Vibe Work Skills.** The word "Skills" names two different things in Mistral's product. Vibe Work ships its own built-in Skills with their own configuration model, managed in that interface. Everything in this repository is a folder under `.agents/skills/` with a `SKILL.md`, read by Vibe CLI off your disk. They are not interchangeable: pointing Work at this repository does nothing, and there is no import step. What does carry across is the writing. A skill body here is the text you would paste into a Work Skill, and the sibling prompt library is the place to look for the Work, scheduled task and Chat side.

**What breaks first.** A skill Mistral Vibe CLI cannot parse does not raise an error. The loader catches the exception, writes one line to a log file nobody is reading, and returns nothing. No message, no non-zero exit code, no skill. You find out when the agent quietly does not do the thing. That is the reason this repository ships a checker next to the skills, and the reason the checker has its own test.

> **<!-- n-skills:start -->137<!-- n-skills:end --> skills for Mistral Vibe CLI, across <!-- n-categories:start -->29<!-- n-categories:end --> disciplines. Copy a folder, or point Vibe CLI at this one. Every skill is written to prepare a draft, not to approve one.**

[![Licence: CC BY-SA 4.0](https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-sa/4.0/)
<!-- badge-skills:start -->[![Skills](https://img.shields.io/badge/skills-137-blue)](.agents/skills/)<!-- badge-skills:end -->
[![Format](https://img.shields.io/badge/format-Agent%20Skills-green)](https://agentskills.io)

Not affiliated with, or endorsed by, Mistral AI. The skills are plain Markdown in the Agent Skills format that Mistral Vibe CLI reads.

---

## Install

Pick one. All three end with the same thing: a directory whose children each hold a `SKILL.md`.

**In a project**, so the skills travel with the repository and the whole team gets them:

```bash
git clone https://github.com/kesslernity/awesome-mistral-vibe-skills.git /tmp/amvs
mkdir -p .agents/skills
cp -R /tmp/amvs/.agents/skills/* .agents/skills/
```

**For yourself, everywhere**, into the Vibe CLI home directory:

```bash
git clone https://github.com/kesslernity/awesome-mistral-vibe-skills.git /tmp/amvs
mkdir -p ~/.vibe/skills
cp -R /tmp/amvs/.agents/skills/* ~/.vibe/skills/
```

**Without copying anything**, by naming the clone in `~/.vibe/config.toml`:

```toml
skill_paths = ["/path/to/awesome-mistral-vibe-skills/.agents/skills"]
```

Then check the result, in the session or on disk:

```bash
vibe                                          # then type / to list the skills
cd /tmp/amvs && python3 tools/verify.py DIR   # DIR is wherever you installed them
```

`verify.py` lives in the clone, so run it from there. It takes the directory as an argument and needs nothing else from the repository.

**In the chat surface**, where there is no filesystem: open the skills panel, create a skill, and paste the three fields. Title, description and the SKILL.md body are the whole form. There is no folder, so a skill whose body says to read `references/<file>.md` needs that file's text pasted into the body or attached to the conversation, or it will look for something that is not there. The faster route for a skill you have already run by hand is to ask the assistant to turn that task into a skill, then edit what it writes.

## Five things that will cost you an afternoon

Each one is read from the loader's own source, not from documentation.

**Discovery is one level deep.** It lists the children of a skills directory and looks for `<child>/SKILL.md`. It does not recurse. A tidy `skills/finance/invoice-exception-review/` hides the skill completely, and hides it silently. Flat, or nothing.

**The description cap is 1,024 characters, and there is nothing past it.** The schema declares `max_length=1024`. Exactly 1,024 passes; 1,025 fails validation and the whole skill disappears. Discovery injects three fields per skill into the system prompt, the name, the description and the path. The description is the only one of the three that can say when to use the skill, and the body is not loaded until the `skill` tool calls it, so nothing below the front matter can rescue a description that never states its trigger. The tightest description here sits <!-- tightest-headroom:start -->28<!-- tightest-headroom:end --> characters short of the cap, in `<!-- tightest-skill:start -->knowledge-article-drafter<!-- tightest-skill:end -->`. `tools/verify.py` warns below 50.

**A name that does not match its folder is a warning, not an error.** The skill still loads, under the name in the front matter. So the slash command is not the folder you are looking at, and the only sign is a log line.

**Unknown front matter keys are ignored, not rejected.** The schema reads `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`, `user-invocable` and `disable-model-invocation`. Anything else is dropped without complaint, so a misspelled key is not an error, it is text the agent never sees. Two of those keys decide whether anyone can reach the skill at all: `user-invocable: false` hides it from the slash menu, and `disable-model-invocation: true` removes it from the routing block, so the model never sees it and only an explicit `/name` reaches it.

**There is no global vendor-neutral path.** `.agents/skills` is read inside a project. The user-level directory is `~/.vibe/skills`. Installing to `~/.agents/skills` and expecting it to work everywhere is a quiet no-op.

## Check before you ship

```bash
python3 tools/verify.py            # the skills in this repository
python3 tools/verify.py DIR ...    # any other skills directory
python3 tools/verify.py --house    # plus this repository's own conventions
python3 tools/selftest.py          # 24 cases that prove the checker rejects what it claims to
```

`verify.py` reproduces the loader's steps rather than approximating them: the same front matter boundary regular expression, the same YAML parse, the same schema. With `mistral-vibe` installed it imports the real `SkillMetadata` and validates against that; without it, a mirror of the same constraints, and it says which one ran. It reports missing reference files, duplicate names across search paths, collisions with built-in skill names, category folders that hide their contents, sync conflict copies left beside a reference file, and descriptions running out of headroom. `--house` adds this repository's own rules: the draft closer, a "Use when" clause, no em or en dashes. Failures exit 1. Warnings do not.

`selftest.py` is the control. A checker for a runtime that fails silently is worth nothing if it fails silently too, so every rule `verify.py` claims gets a deliberately broken skill it has to reject, plus one correct skill it has to pass. It also checks that a house rule stays quiet without `--house`, so the checker is still usable on somebody else's skills.

## Where these come from

Not written here. Generated from [awesome-copilot-agent-skills](https://github.com/kesslernity/awesome-copilot-agent-skills), which holds the same <!-- n-skills:start -->137<!-- n-skills:end --> files in a category tree, by `tools/generate.py`. One text, two repositories, so a correction upstream reaches this one on the next run.

```bash
python3 tools/generate.py --source ../awesome-copilot-agent-skills
python3 tools/generate.py --check     # exits 1 if the tree has drifted from its source
```

The generator changes three things and records all of them in `MANIFEST.json`, alongside the source commit and a hash per skill:

1. **Layout.** The category tree flattens, because discovery does not recurse.
2. **Vendor terms.** A three-entry map, which fires on three skills. It is that small because the text was written capability-neutral in the first place: 135 of the 137 bodies and all 131 reference files name no vendor product at all. The two that do both name SharePoint, and both name it as a document library the skill reads rather than the runtime it runs on, which is why `sharepoint-review-sweeper` keeps its name.
3. **Overrides.** One skill, `skill-file-reviewer`, whose subject is the skill format itself and which would otherwise review Mistral files against another runtime's rules. What changed and why is in [`overrides/README.md`](overrides/README.md).

Everything the generator writes is verified before it lands. Front matter that is not exactly `name` and `description` at the source, a name that does not match its folder, a description over the cap, or a patch whose anchor text no longer matches upstream all stop the run.

## What the skills are, and what they refuse to do

Each skill is one job: a named artefact, the inputs it needs, a numbered procedure, an output whose columns are specified, and the fallbacks for missing data. They are written for the work people actually hand an assistant, which is reading a pile of material and returning something a colleague can check.

Three rules run through all <!-- n-skills:start -->137<!-- n-skills:end --> of them:

- **Every output is a draft.** No skill approves, authorises, signs off, certifies or decides. The sentence that says so closes all 137 descriptions, and `verify.py --house` fails the build if one loses it.
- **Missing data is UNKNOWN, named.** No skill invents a value to fill a column, and every output carries the list of what was missing.
- **Nothing in this repository is a safety authorisation.** No skill issues or approves a permit to work, an isolation, a confined space entry, a job safety analysis, an incident classification or an inspection sign-off. The engineering skills read drawings and documents and return questions, quotes and gaps. AI prepares, a qualified human decides.

Text inside an input is data, not instruction. Every skill treats embedded instructions as content to report rather than orders to follow.

## Skills by discipline

<!-- skill-directory:start -->

### Customer support (3)

| Skill | What it does |
|---|---|
| [`customer-feedback-theme-synthesis`](.agents/skills/customer-feedback-theme-synthesis/) | Synthesises a batch of customer feedback (survey answers, reviews, ticket and chat comments) into a DRAFT themed report. |
| [`escalation-summary`](.agents/skills/escalation-summary/) | Turns one long support ticket thread (helpdesk history, email chain, chat transcript, call notes) into a one-page DRAFT escalation summary. |
| [`ticket-triage-pack`](.agents/skills/ticket-triage-pack/) | Triages a batch of customer support tickets (helpdesk export, shared mailbox, chat transcripts, web forms) into one row per ticket with category, urgency graded on the evidence in the ticket, suggested next action and owner, plus a DRAFT ... |

### Daily briefings (2)

| Skill | What it does |
|---|---|
| [`commitment-catcher`](.agents/skills/commitment-catcher/) | Sweeps the last 24 hours of email, chat messages and meeting transcripts for commitments in both directions, what the user promised others and what others promised the user, reconciles them against a running commitments ledger (open, done ... |
| [`custom-daily-brief`](.agents/skills/custom-daily-brief/) | Builds a role-tuned morning brief as a dated Markdown document covering emails that need replies, today's calendar with conflicts flagged, chat mentions and upcoming deadlines, in the section order set by a preset (project manager ... |

### Dashboards and micro-apps (1)

| Skill | What it does |
|---|---|
| [`project-dashboard-builder`](.agents/skills/project-dashboard-builder/) | Builds a self-contained single-file HTML project dashboard (status banner, milestones table, risks heat list, decisions log, links) from the project tracker files the user attaches, pastes or holds in configured knowledge sources, and ... |

### Data and analytics (4)

| Skill | What it does |
|---|---|
| [`data-dictionary-builder`](.agents/skills/data-dictionary-builder/) | Builds a DRAFT data dictionary from a schema export, table definition, sample rows or a partial existing dictionary. |
| [`data-quality-issue-log`](.agents/skills/data-quality-issue-log/) | Turns reported data problems (messages, tickets, meeting notes, complaints) into one DRAFT issue log. |
| [`dataset-insight-pack`](.agents/skills/dataset-insight-pack/) | Reads one spreadsheet, CSV export or pasted table together with the user's question and drafts an insight pack. |
| [`kpi-definition-sheet`](.agents/skills/kpi-definition-sheet/) | Turns a list of KPIs or metrics into a DRAFT definition sheet. |

### Data privacy (2)

| Skill | What it does |
|---|---|
| [`document-deidentification-pass`](.agents/skills/document-deidentification-pass/) | Proposes redactions of personal identifiers in pasted text or an attached document (names, contact details, identification and account numbers, dates that identify, quasi-identifiers) and returns a DRAFT redacted copy with consistent ... |
| [`dpia-draft-pack`](.agents/skills/dpia-draft-pack/) | Reads a project or processing description and returns a DRAFT data protection impact assessment pack. |

### Email and inbox (1)

| Skill | What it does |
|---|---|
| [`inbox-triage`](.agents/skills/inbox-triage/) | Sorts a personal inbox backlog into five buckets (needs-reply-today, needs-reply-this-week, waiting-on-others, FYI, noise), writes DRAFT reply text for the messages that need an answer (up to 10 per run), and returns a dated triage report ... |

### Engineering document control (4)

| Skill | What it does |
|---|---|
| [`interface-register-builder`](.agents/skills/interface-register-builder/) | Builds a DRAFT interface register between disciplines or parties from meeting notes, action lists and drawings or document lists. |
| [`management-of-change-intake`](.agents/skills/management-of-change-intake/) | Prepares a DRAFT management-of-change intake record from a change description (email, meeting note, marked-up drawing or request form). |
| [`master-document-register-check`](.agents/skills/master-document-register-check/) | Checks a master document register extract for gaps and returns a DRAFT question list for document control. |
| [`transmittal-drafter`](.agents/skills/transmittal-drafter/) | Drafts a document transmittal (header, one line per document with revision and purpose of issue, distribution with action required, blank acknowledgement block) from a document list and the project's transmittal template, with UNKNOWN for ... |

### Engineering, PFD to P&ID (8)

| Skill | What it does |
|---|---|
| [`instrumentation-and-control-enrichment`](.agents/skills/instrumentation-and-control-enrichment/) | Proposes the instrumentation and control content a P&ID adds to an accepted PFD process model. |
| [`pfd-intake-and-extraction`](.agents/skills/pfd-intake-and-extraction/) | Reads a process flow diagram (image, PDF or native export) with its job header and returns a provenance-tagged extraction register. |
| [`pid-tool-readiness-mapping`](.agents/skills/pid-tool-readiness-mapping/) | Maps every proposed P&ID object from an accepted enrichment draft to the generic family, catalogue class and required attributes the project's intelligent P&ID authoring tool would need, as a readiness table with UNKNOWN wherever the ... |
| [`piping-enrichment`](.agents/skills/piping-enrichment/) | Proposes the piping content a P&ID adds to an accepted PFD process model. |
| [`process-model-check`](.agents/skills/process-model-check/) | Checks an extracted PFD register as a process model and returns findings and unknowns only. |
| [`process-safety-flags`](.agents/skills/process-safety-flags/) | Flags where a P&ID draft raises a process safety question and points to the candidate evidence an engineer would review (HAZOP register, relief study, SIL assessment, isolation philosophy), as questions and quoted passages with UNKNOWN for ... |
| [`tagging-and-numbering`](.agents/skills/tagging-and-numbering/) | Proposes tag and number structures for the new lines and instruments in a P&ID draft according to the project's numbering procedures, checks every tag extracted from the PFD against the quoted procedure format, and lists cross-section ... |
| [`validation-and-review-package`](.agents/skills/validation-and-review-package/) | Runs twice in a PFD to P&ID job. |

### Executive (4)

| Skill | What it does |
|---|---|
| [`architecture-decision-record`](.agents/skills/architecture-decision-record/) | Drafts an architecture or design decision record (ADR) from the discussion notes, design review minutes, chat threads and diagram descriptions the user provides. |
| [`board-paper-skeleton`](.agents/skills/board-paper-skeleton/) | Builds a DRAFT board paper skeleton from the sponsor's inputs. |
| [`decision-memo-builder`](.agents/skills/decision-memo-builder/) | Turns one decision discussion (meeting transcript, chat thread, email chain or notes) into a DRAFT one-page decision memo. |
| [`executive-briefing-pack`](.agents/skills/executive-briefing-pack/) | Prepares a DRAFT leadership-meeting briefing pack from the reports, meeting notes, emails and dashboard exports the user provides. |

### Executive review (16)

| Skill | What it does |
|---|---|
| [`cbo-reviewer`](.agents/skills/cbo-reviewer/) | Reviews a proposal, business case, deck or plan in character as a Chief Business Officer archetype, covering commercial model, partnerships, deal structure, market positioning, strategic fit and opportunity cost, and returns a DRAFT review ... |
| [`cdo-reviewer`](.agents/skills/cdo-reviewer/) | Reviews a proposal, business case, deck or plan in character as a Chief Data Officer archetype and returns a DRAFT review in the chat with a verdict, findings that cite the exact passage, data and AI governance risks, what would change the ... |
| [`cfo-reviewer`](.agents/skills/cfo-reviewer/) | Reviews a proposal, business case, deck or plan in character as a Chief Financial Officer archetype and returns a DRAFT review in the chat with a verdict, findings that cite the exact passage, finance risks, what would change the verdict ... |
| [`chro-reviewer`](.agents/skills/chro-reviewer/) | Reviews a proposal, business case, deck, plan or restructuring paper in character as a Chief Human Resources Officer archetype and returns a DRAFT review with a verdict, findings that cite the exact passage, people and organisation risks ... |
| [`ciso-reviewer`](.agents/skills/ciso-reviewer/) | Reviews a proposal, business case, deck or plan in character as a Chief Information Security Officer archetype and returns a DRAFT review with a verdict, findings cited to specific passages, security and compliance risks and the five ... |
| [`cmo-reviewer`](.agents/skills/cmo-reviewer/) | Reviews a proposal, business case, deck or plan in character as a Chief Marketing Officer archetype and returns a DRAFT review in the chat with a verdict, findings cited to specific passages, marketing risks, what would change the verdict ... |
| [`coo-reviewer`](.agents/skills/coo-reviewer/) | Reviews a proposal, business case, deck or plan in character as a Chief Operating Officer archetype and returns a DRAFT review in the chat with a verdict, findings cited to specific sections, delivery and operational risks, what would ... |
| [`cpo-reviewer`](.agents/skills/cpo-reviewer/) | Reviews a proposal, business case, deck or product plan in character as a Chief Product Officer archetype and returns a DRAFT review in the chat with a verdict, findings that cite the exact passage, product and adoption risks, what would ... |
| [`cro-reviewer`](.agents/skills/cro-reviewer/) | Reviews a proposal, business case, deck, pricing plan, go-to-market plan or forecast in character as a Chief Revenue Officer archetype and returns a DRAFT review in the chat with a verdict, findings cited to exact passages, revenue risks ... |
| [`cto-reviewer`](.agents/skills/cto-reviewer/) | Reviews a proposal, business case, deck or plan in character as a Chief Technology Officer archetype and returns a DRAFT review in the chat with a verdict, findings cited to the exact passage, technology risks (architecture, build versus ... |
| [`customer-advocate-reviewer`](.agents/skills/customer-advocate-reviewer/) | Reviews a proposal, business case, deck or plan in character as a Customer Advocate archetype, the seat for paying customers not in the room, and returns a DRAFT review in the chat with a verdict, findings that cite the exact passage ... |
| [`frontline-skeptic-reviewer`](.agents/skills/frontline-skeptic-reviewer/) | Reviews a proposal, business case, deck or rollout plan in character as a Frontline Sceptic archetype, the experienced staff member who will live with the change, and returns a DRAFT review in the chat with a verdict, findings that cite ... |
| [`general-counsel-reviewer`](.agents/skills/general-counsel-reviewer/) | Reviews a proposal, business case, deck, plan or contract summary in character as a General Counsel archetype and returns a DRAFT review in the chat with a verdict, findings that cite the exact passage or clause, legal risks, what would ... |
| [`investor-reviewer`](.agents/skills/investor-reviewer/) | Reviews a proposal, business case, deck or plan in character as an Investor archetype and returns a DRAFT review in the chat with a verdict whose conditions read as terms, findings that cite the exact passage, capital-allocation risks ... |
| [`procurement-reviewer`](.agents/skills/procurement-reviewer/) | Reviews a proposal, business case, deck or vendor contract in character as a Head of Procurement archetype and returns a DRAFT review in the chat with a verdict, findings that cite the exact passage or clause, commercial risks, what would ... |
| [`works-council-reviewer`](.agents/skills/works-council-reviewer/) | Reviews a proposal, business case, deck or rollout plan in character as a Works Council Representative archetype and returns a DRAFT review in the chat with a verdict, findings that cite the exact passage, employee-impact risks, what would ... |

### Finance (6)

| Skill | What it does |
|---|---|
| [`budget-variance-explainer`](.agents/skills/budget-variance-explainer/) | Turns an actuals-versus-budget extract (spreadsheet, export or pasted table) into a DRAFT variance table with absolute and percentage variances, favourable or adverse marking and a ranking by size, then drafts plain-language driver ... |
| [`capex-request-pack`](.agents/skills/capex-request-pack/) | Assembles a DRAFT capital expenditure request pack from the requester's inputs. |
| [`cash-forecast-assumptions-sheet`](.agents/skills/cash-forecast-assumptions-sheet/) | Reads a cash forecast (spreadsheet, model export, pasted table or the narrative that accompanies it) and returns a DRAFT assumptions sheet. |
| [`expense-policy-precheck`](.agents/skills/expense-policy-precheck/) | Pre-checks one expense claim or travel plan, line by line, against the expense or travel policy the user supplies, and returns a DRAFT precheck sheet. |
| [`invoice-exception-review`](.agents/skills/invoice-exception-review/) | Reads an accounts payable exception list (mismatches, possible duplicates, missing or exhausted purchase orders, missing receipts, vendor or bank detail differences) with any invoice, purchase order and receipt data supplied, and returns a ... |
| [`month-end-close-checklist`](.agents/skills/month-end-close-checklist/) | Builds a DRAFT month-end, quarter-end or year-end close checklist and status table for a finance team from the close calendar, the open items list and last month's close issues that the user attaches, pastes or the agent can reach, marks ... |

### HR and people (9)

| Skill | What it does |
|---|---|
| [`change-communication-plan`](.agents/skills/change-communication-plan/) | Builds a DRAFT change-communication plan from a change description. |
| [`exit-interview-synthesis`](.agents/skills/exit-interview-synthesis/) | Synthesises exit interview notes or leaver survey responses into a DRAFT themed report. |
| [`impact-log-builder`](.agents/skills/impact-log-builder/) | Builds and maintains a DRAFT impact log from notes, messages, status updates and completed work. |
| [`interview-scorecard-builder`](.agents/skills/interview-scorecard-builder/) | Builds a DRAFT structured interview scorecard from a job description. |
| [`job-description-drafter`](.agents/skills/job-description-drafter/) | Drafts a DRAFT job description from a role brief, team context and the organisation's own template, in inclusive plain language, with every requirement traced to its source, unconfirmed fields marked TBC and a numbered list of items the ... |
| [`onboarding-plan-builder`](.agents/skills/onboarding-plan-builder/) | Produces a DRAFT 30-60-90 day onboarding plan for a new hire from the role, the team context and the systems list. |
| [`performance-review-drafter`](.agents/skills/performance-review-drafter/) | Drafts a DRAFT self-assessment, peer feedback note or manager review narrative from the evidence the writer supplies (goals, examples, metrics, notes), in the review template where given. |
| [`policy-change-briefing`](.agents/skills/policy-change-briefing/) | Compares a changed HR policy with the version it replaces and drafts a clause-by-clause change log, a plain-language DRAFT employee briefing, a manager FAQ answered only from the policy text with clause references, and a list of open ... |
| [`policy-question-answerer`](.agents/skills/policy-question-answerer/) | Answers an employee's or manager's HR policy question strictly from the policy documents the user supplies or the agent can reach as knowledge. |

### IT operations (9)

| Skill | What it does |
|---|---|
| [`access-review-pack`](.agents/skills/access-review-pack/) | Turns an access export (accounts, entitlements, grant and last-used dates per system) into a draft access review pack, one section per system owner. |
| [`change-request-pack`](.agents/skills/change-request-pack/) | Prepares a change request pack (description and justification, scope, schedule, implementation plan, risk as stated, rollback, test evidence as provided, communications, approvals route) from an engineer's notes, ticket or pull request ... |
| [`incident-postmortem-drafter`](.agents/skills/incident-postmortem-drafter/) | Drafts a blameless incident postmortem (summary, impact, timeline, detection and response, contributing factors as candidates for review, action items) from an incident channel export, ticket notes and any alert or change records, with ... |
| [`knowledge-article-drafter`](.agents/skills/knowledge-article-drafter/) | Drafts one knowledge article or known-error article from a resolved incident or ticket thread. |
| [`knowledge-base-hygiene-review`](.agents/skills/knowledge-base-hygiene-review/) | Reviews a set of knowledge files or a knowledge base listing and returns a draft hygiene table, one row per file. |
| [`runbook-drafter`](.agents/skills/runbook-drafter/) | Turns an engineer's notes, a ticket history or a chat thread into a draft step-by-step runbook with preconditions, stop conditions, numbered steps with checks, verification, rollback and escalation, for the team to validate before use. |
| [`service-catalogue-entry`](.agents/skills/service-catalogue-entry/) | Drafts one service catalogue entry (description, scope in and out, owners and support groups, service levels exactly as provided, request path, dependencies, charging, lifecycle) from the service team's notes, questionnaire answers or ... |
| [`sharepoint-review-sweeper`](.agents/skills/sharepoint-review-sweeper/) | Sweeps a SharePoint library listing (an export or a listing the agent can reach, with file name, link, review-date column and owner column) for documents past their review date and returns a dated DRAFT review sweep report (Overdue, Due ... |
| [`software-request-review`](.agents/skills/software-request-review/) | Reviews one employee software request (tool, purpose, users, data handled, cost, urgency) against the approved-tools list and the policies the user provides and returns a draft review for the reviewer. |

### Learning and development (3)

| Skill | What it does |
|---|---|
| [`course-outline-builder`](.agents/skills/course-outline-builder/) | Builds a DRAFT course outline from a training need and audience. |
| [`training-needs-synthesis`](.agents/skills/training-needs-synthesis/) | Synthesises training survey responses and manager notes into a DRAFT training needs report by role. |
| [`training-quiz-builder`](.agents/skills/training-quiz-builder/) | Builds a DRAFT quiz from the training content the user supplies (slide deck, manual, e-learning script, session transcript, procedure). |

### Legal and contracts (4)

| Skill | What it does |
|---|---|
| [`clause-comparison-table`](.agents/skills/clause-comparison-table/) | Compares one clause (liability, termination, confidentiality or any other) across several contracts, templates or successive versions and returns a DRAFT comparison table. |
| [`contract-review-pack`](.agents/skills/contract-review-pack/) | Abstracts one contract into a key-terms table with clause references, compares each term against the user's playbook of standard positions, and returns a DRAFT contract review pack. |
| [`nda-triage`](.agents/skills/nda-triage/) | Triages an incoming non-disclosure agreement against the organisation's written standard NDA positions and returns a DRAFT triage pack. |
| [`regulatory-change-impact-note`](.agents/skills/regulatory-change-impact-note/) | Turns the text of a regulatory change (new regulation, amendment, rule, guidance or standard revision) into a DRAFT impact note. |

### Marketing and communications (8)

| Skill | What it does |
|---|---|
| [`announcement-drafter`](.agents/skills/announcement-drafter/) | Drafts one internal or external announcement (email, intranet post, town hall script, customer notice or press statement) in the organisation's voice from the facts, audience, sender and style guide the user provides, with a fact trace ... |
| [`campaign-brief-builder`](.agents/skills/campaign-brief-builder/) | Turns a campaign idea, its objectives and the supporting notes (audience material, offer facts, budget and dates, channel list) into one DRAFT one-page campaign brief. |
| [`case-study-drafter`](.agents/skills/case-study-drafter/) | Drafts one anonymised DRAFT case study (situation, approach, outcome as evidenced, optional lessons) from engagement notes, status reports, closing reports, emails and metrics extracts the user supplies, with a fact trace to the notes, an ... |
| [`communication-pretest-panel`](.agents/skills/communication-pretest-panel/) | Pre-tests one message (email, announcement, intranet post, town hall script, customer notice or slide) against two to six role personas the user supplies and returns a DRAFT panel report. |
| [`content-calendar-planner`](.agents/skills/content-calendar-planner/) | Builds a DRAFT content calendar for a stated period from the themes, channels, cadence rules, fixed dates and owners the user provides. |
| [`faq-builder`](.agents/skills/faq-builder/) | Turns a set of questions (form exports, helpdesk logs, meeting Q and A, chat threads, a plain list) plus the source documents the user supplies into a DRAFT FAQ grouped by theme. |
| [`internal-newsletter-drafter`](.agents/skills/internal-newsletter-drafter/) | Drafts one issue of an internal newsletter from the items the user provides (notes, messages, snippets, meeting outputs, contributor submissions). |
| [`message-house-builder`](.agents/skills/message-house-builder/) | Builds one DRAFT message house for a product, service, programme or initiative from the source material the user provides. |

### Meetings (3)

| Skill | What it does |
|---|---|
| [`meeting-minutes-writer`](.agents/skills/meeting-minutes-writer/) | Turns one meeting transcript, recording recap or set of raw notes into concise DRAFT minutes returned in the chat as a single Markdown document. |
| [`meeting-prep-onepager`](.agents/skills/meeting-prep-onepager/) | Builds a one-page meeting preparation brief from the calendar invite, recent mail threads with the attendees, chat messages and shared files. |
| [`transcript-to-actions`](.agents/skills/transcript-to-actions/) | Turns one meeting transcript or recap into a DRAFT action-items document (decisions, owned and dated action items with verbatim source quotes, open questions), a task list ready for the user to enter into their task tracker, and one DRAFT ... |

### Meta skills (6)

| Skill | What it does |
|---|---|
| [`agent-evaluation-plan`](.agents/skills/agent-evaluation-plan/) | Designs a pre-launch evaluation plan for an agent from its instructions text, skills, capabilities, knowledge sources and sample requests. |
| [`agent-instructions-drafter`](.agents/skills/agent-instructions-drafter/) | Drafts the instructions field of an agent that orchestrates a set of custom skills, under a character cap (default 8,000), from the skills' names and descriptions. |
| [`agent-instructions-red-team`](.agents/skills/agent-instructions-red-team/) | Reviews the instructions text and skills of an agent, with its stated capabilities, knowledge sources and audience, for prompt-injection exposure, data-leakage paths, over-broad permissions and missing refusals, and returns an ... |
| [`no-delete-guardrail`](.agents/skills/no-delete-guardrail/) | Applies a change-safety review to any requested file, mail or calendar change. |
| [`skill-file-reviewer`](.agents/skills/skill-file-reviewer/) | Reviews one SKILL.md against the Mistral Vibe CLI skill rules and returns a findings table. |
| [`skills-backup-keeper`](.agents/skills/skills-backup-keeper/) | Prepares the contents of a dated backup of a custom skills folder and drafts a session journal entry, both for the user to save, so work can be resumed after a crash, a context loss or a skills wipe. |

### Operations (2)

| Skill | What it does |
|---|---|
| [`request-intake-triage`](.agents/skills/request-intake-triage/) | Turns plain-language requests (emails, chat messages, form submissions, meeting asks, voicemail or call notes) into one intake record per request (what is asked, who asks and for whom, urgency as evidenced, category, suggested owner ... |
| [`sop-drafter`](.agents/skills/sop-drafter/) | Turns process notes, a walkthrough or interview transcript, a transcript of a meeting recording or a stale existing procedure into a draft standard operating procedure. |

### Procurement (5)

| Skill | What it does |
|---|---|
| [`contract-renewal-radar`](.agents/skills/contract-renewal-radar/) | Reads a contract list (spreadsheet, CSV or pasted table) and returns a DRAFT renewal radar. |
| [`purchase-order-anomaly-review`](.agents/skills/purchase-order-anomaly-review/) | Reads a purchase order extract (spreadsheet, CSV or pasted table) and returns a DRAFT question sheet for the buyer. |
| [`rfp-comparison-pack`](.agents/skills/rfp-comparison-pack/) | Reads two or more supplier, bid or tender responses against a requirements list and returns a DRAFT comparison pack. |
| [`rfp-requirements-pack`](.agents/skills/rfp-requirements-pack/) | Turns a business need and its constraints into a DRAFT RFP requirements pack. |
| [`supplier-evaluation-matrix`](.agents/skills/supplier-evaluation-matrix/) | Builds a DRAFT weighted supplier evaluation matrix from supplier responses and the panel's agreed criteria, weights and scale. |

### Product management (3)

| Skill | What it does |
|---|---|
| [`product-requirements-draft`](.agents/skills/product-requirements-draft/) | Produces a DRAFT product requirements document from the discovery notes, interview summaries, support themes, analytics notes and stakeholder messages the user provides. |
| [`release-notes-writer`](.agents/skills/release-notes-writer/) | Turns a list of merged changes, closed work items or commit messages the user provides into DRAFT release notes under the version heading and date the user supplies, grouped as features, fixes and other, in the organisation's tone from the ... |
| [`user-personas-builder`](.agents/skills/user-personas-builder/) | Builds DRAFT user personas from the research notes, interview summaries, survey free text and support themes the user provides. |

### Project management (6)

| Skill | What it does |
|---|---|
| [`lessons-learned-synthesis`](.agents/skills/lessons-learned-synthesis/) | Synthesises retrospective notes, closing reports and post-implementation reviews into a DRAFT lessons-learned document. |
| [`project-status-tracker`](.agents/skills/project-status-tracker/) | Maintains four living project files (overview and progress log, decision log, RAID log, links) from the mail, channel posts, documents and meeting notes the user attaches or the agent can reach, returns each touched file complete in the ... |
| [`raid-log-review`](.agents/skills/raid-log-review/) | Reviews a RAID log (risks, assumptions, issues, dependencies) line by line and returns a DRAFT review pack. |
| [`schedule-slip-explainer`](.agents/skills/schedule-slip-explainer/) | Turns a schedule extract (milestone list or planning tool export) and the period's status notes into a DRAFT plain-language slip explanation. |
| [`sprint-review-summary`](.agents/skills/sprint-review-summary/) | Summarises one sprint from the board export, sprint report and review or stand-up notes the user provides into a one-page DRAFT sprint review summary. |
| [`stakeholder-map-builder`](.agents/skills/stakeholder-map-builder/) | Builds a DRAFT stakeholder map for one project from the charter, organisation chart, RACI, governance terms, steering minutes, meeting notes and messages the user provides. |

### Quality and audit (3)

| Skill | What it does |
|---|---|
| [`audit-prep-pack`](.agents/skills/audit-prep-pack/) | Prepares a DRAFT internal audit pack from the audit plan. |
| [`corrective-action-tracker`](.agents/skills/corrective-action-tracker/) | Turns corrective and preventive actions from NCRs, audit reports, action forms, minutes or a tracker into one DRAFT tracker. |
| [`nonconformance-report-drafter`](.agents/skills/nonconformance-report-drafter/) | Drafts a nonconformance report from inspection notes, test results and the governing specification or procedure. |

### Reporting and analysis (3)

| Skill | What it does |
|---|---|
| [`kpi-weekly-report-writer`](.agents/skills/kpi-weekly-report-writer/) | Writes a DRAFT weekly KPI report from the figures the user pastes or attaches (this week, last week, optionally target and earlier weeks). |
| [`news-monitor-digest`](.agents/skills/news-monitor-digest/) | Sweeps a named list of news sources and blogs for items relevant to the user's role and returns a dated digest of 5 to 8 items, each with a one-line so-what, a source URL and a publication date, as a Markdown document or a ready-to-paste ... |
| [`report-attachment-analyzer`](.agents/skills/report-attachment-analyzer/) | Prepares the trend update for a recurring emailed report. |

### Risk, ethics and compliance (3)

| Skill | What it does |
|---|---|
| [`controls-gap-pack`](.agents/skills/controls-gap-pack/) | Produces a draft controls and gap pack from a requirement, regulation, standard or policy and the organisation's control descriptions. |
| [`esg-report-question-pack`](.agents/skills/esg-report-question-pack/) | Turns sustainability or ESG reports the user provides into a DRAFT question pack for reviewers. |
| [`green-claims-review`](.agents/skills/green-claims-review/) | Reviews marketing, packaging, web or sustainability text against the environmental-claim rules the user supplies (house policy, regulator guidance extract, industry code) and returns a DRAFT claims review: every environmental claim quoted ... |

### Sales and business development (7)

| Skill | What it does |
|---|---|
| [`account-plan-builder`](.agents/skills/account-plan-builder/) | Drafts an account plan from the CRM notes, emails, meeting notes and contracts the user provides. |
| [`deal-risk-review`](.agents/skills/deal-risk-review/) | Reviews one deal's notes and timeline (CRM opportunity record, activity log, emails, meeting notes, forecast entries) for risk signals such as a single contact thread, no identified budget owner, slipped or missing dates, silence after a ... |
| [`discovery-call-prep`](.agents/skills/discovery-call-prep/) | Prepares a discovery call brief from what the user has on a prospect (CRM record, inbound form, emails, notes, public material the user supplies). |
| [`estimate-to-sow`](.agents/skills/estimate-to-sow/) | Converts a priced estimate spreadsheet into a DRAFT statement of work populated from the user's own SOW template, after checking that line items, hours, rates, subtotals and the grand total add up. |
| [`lead-qualification-scorer`](.agents/skills/lead-qualification-scorer/) | Scores inbound leads against the qualification rubric the user supplies (criteria, scale, weights, thresholds and disqualifiers as given). |
| [`proposal-skeleton`](.agents/skills/proposal-skeleton/) | Builds a DRAFT proposal skeleton from a discovery summary (call notes, discovery brief, CRM record, emails) and the organisation's own proposal template. |
| [`rfp-response-drafter`](.agents/skills/rfp-response-drafter/) | Drafts answers to the questions in a received RFP, RFQ or tender from the organisation's past responses, answer library, case studies, policies and other documents provided. |

### Security and GRC (6)

| Skill | What it does |
|---|---|
| [`control-evidence-request-pack`](.agents/skills/control-evidence-request-pack/) | Turns a control list and an audit scope into draft evidence requests grouped by control owner, each with the control as stated, the audit period, evidence examples (commonly requested) and a proposed due date derived from the fieldwork ... |
| [`data-incident-impact-brief`](.agents/skills/data-incident-impact-brief/) | Prepares a DRAFT data incident impact brief from the incident notes and data inventory the user provides. |
| [`policy-gap-review`](.agents/skills/policy-gap-review/) | Compares one policy against one requirement set (standard, regulation, contract schedule or customer requirement) clause by clause and returns a draft gap review. |
| [`risk-register-update`](.agents/skills/risk-register-update/) | Reads a risk register together with meeting notes and incident reports and returns a draft update pack. |
| [`vendor-risk-screening-brief`](.agents/skills/vendor-risk-screening-brief/) | Prepares a DRAFT vendor risk screening brief from the material the user provides on one vendor (questionnaire answers, certificates, assurance reports, policies, contract extracts). |
| [`vendor-security-questionnaire-prefill`](.agents/skills/vendor-security-questionnaire-prefill/) | Pre-fills a customer's or prospect's security or third-party risk questionnaire from the organisation's own answer sources (prior questionnaires, answer library, policies), returning one row per question with a draft answer marked Reused ... |

### Trade compliance (1)

| Skill | What it does |
|---|---|
| [`export-review-pack`](.agents/skills/export-review-pack/) | Reads one export transaction, order or shipment description and returns a DRAFT export review pack. |

### Writing and communication (5)

| Skill | What it does |
|---|---|
| [`branded-deck-builder`](.agents/skills/branded-deck-builder/) | Builds a slide-by-slide presentation draft on the user's own slide template and checks every slide against written brand rules (colours with hex codes, fonts, logo placement, slide archetypes, tone, banned visuals), returning the approved ... |
| [`claims-evidence-map`](.agents/skills/claims-evidence-map/) | Builds an evidence map for one document, section or contested claim. |
| [`document-accessibility-check`](.agents/skills/document-accessibility-check/) | Reviews the text and structure of a document, slide deck or web page against the accessibility rules the user supplies, or a default set covering heading structure, image alternative text, colour used as the only cue, link text, reading ... |
| [`weekly-status-update-writer`](.agents/skills/weekly-status-update-writer/) | Drafts one weekly status update or team status email (done, in progress, blocked, next, asks) from the notes, task lists, tracker exports and messages the user attaches, pastes or makes reachable, every bullet traced to a source and every ... |
| [`write-like-me`](.agents/skills/write-like-me/) | Builds a personal voice profile from roughly 90 days of the user's own sent messages and meeting speech, then drafts emails and documents that match how the user actually writes, returning the profile and every draft as Markdown for the ... |
<!-- skill-directory:end -->

## Related

- [awesome-mistral-vibe-agents](https://github.com/kesslernity/awesome-mistral-vibe-agents?utm_source=github&utm_medium=repo&utm_campaign=amv_skills): 17 agent profiles for the Vibe CLI. The profiles decide which tools a run can reach; these skills decide what it does with them.
- [awesome-mistral-vibe-prompts](https://github.com/kesslernity/awesome-mistral-vibe-prompts?utm_source=github&utm_medium=repo&utm_campaign=amv_skills): 49 prompts for Vibe Work, scheduled tasks and Chat, for the jobs that do not need a skill file.
- [mistral-vibe](https://github.com/mistralai/mistral-vibe): the CLI itself, Apache 2.0.
- The same work on the Microsoft side, five repositories: [agent skills](https://github.com/kesslernity/awesome-copilot-agent-skills?utm_source=github&utm_medium=repo&utm_campaign=amv_skills), [Cowork skills](https://github.com/kesslernity/awesome-copilot-cowork-skills?utm_source=github&utm_medium=repo&utm_campaign=amv_skills), [Copilot Chat agents](https://github.com/kesslernity/awesome-copilot-chat-agents?utm_source=github&utm_medium=repo&utm_campaign=amv_skills), [Copilot Studio agents](https://github.com/kesslernity/awesome-copilot-studio-agents?utm_source=github&utm_medium=repo&utm_campaign=amv_skills), [M365 Copilot prompts](https://github.com/kesslernity/awesome-microsoft-copilot-prompts?utm_source=github&utm_medium=repo&utm_campaign=amv_skills). Two runtimes, one set of rules about what an agent is allowed to decide.

## Contributing

Corrections go upstream, then get regenerated. The reason, and the three-command loop, are in [CONTRIBUTING.md](CONTRIBUTING.md).

## Licence

CC BY-SA 4.0. Use them, change them, ship them inside your own work. Keep the attribution and license derivatives the same way.

Built by [Kesslernity](https://www.kesslernity.com/?utm_source=github&utm_medium=readme&utm_campaign=awesome-mistral-vibe-skills).
