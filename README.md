# Leadership Team — Digital Twin

A digital twin of an account's leadership team. Pose a question and read the debate
the CEO, CFO, CTO and COO — plus a Moonshot and a Contrarian — would have about it, then
get a decision memo. Specialists such as a head of security can be brought into specific
conversations. The team learns: each decision can later be compared with what the real team
actually did, and the twins are calibrated.

> Output is a **simulation** built from public and supplied information. It is not what the
> real executives said, and it is not a prediction to rely on.

**One workspace per account.** Clone this repo for each account (e.g. `acme-leadership-team`)
and populate `company/` for that account. **Account data never goes into this template:**
`company/` and the run artifacts (`decisions/`, `memories/`, `questions/`) are git-ignored.
The generic starting skeleton is `company-template/`, which you copy to `company/` on setup.
If you want an account workspace under version control, use a private repo and remove
`/company/` from `.gitignore` there.

---

## Install

**Requirements**

| For | You need |
|---|---|
| Everything | `git` and `python3` (3.8+, standard library only; no pip installs) |
| Claude (primary) | Claude Desktop (Code tab) or the Claude Code CLI, signed in |
| Pi (optional) | Node.js, tmux or iTerm2, and the Pi CLI (below) |

**Set up a workspace**

```bash
git clone https://github.com/dtehan/leadership-team.git acme-leadership-team
cd acme-leadership-team
cp -R company-template company     # create the (git-ignored) account knowledge folder
# optional: point it at your own private remote so nothing goes back to the template
git remote set-url origin <your-private-repo-url>
```

Skills are shared between runtimes: `.claude/skills/` contains symlinks into `.pi/skills/`.
Symlinks work on macOS/Linux; on Windows enable Developer Mode and
`git config core.symlinks true` before cloning.

**Claude Desktop / Claude Code**: nothing to install. Open the folder as the project
(Desktop: Code tab → choose the folder; CLI: run `claude` from the repo root, **not** a subfolder).
Claude loads `CLAUDE.md` and the skills automatically.

**Pi (secondary)**

```bash
npm install -g @mariozechner/pi-coding-agent
pi install npm:pi-subagents
pi install npm:pi-teams
```

---

## Operate

Work from the repo root. Everything below is a plain-language request; the skill noted
runs automatically.

### 1. Populate the account — `company-research`

> *"Bootstrap Acme Corp."* — or *"Ingest this annual report"* (drop files in `company/<area>/sources/`).

It collects the 10-K/10-Q/proxy, technology decisions in place and under evaluation, strategy,
and a dossier per leader; rebuilds the indexes; and lists the questions only you can answer
(internal knowledge, relationships, politics). **The team refuses to convene on an empty
account**: `company/index.md` must be populated first.

Then confirm each role's real person: `company/profiles/{leader,cfo,cto,coo}/index.md` should
have `person:` and `title:` filled in.

### 2. Ask a question — `convene`

Either type it (*"Convene the team on: should we pitch a data-platform consolidation to the account
this quarter?"*) or save a file in `questions/`:

```yaml
# questions/data-platform-consolidation.yaml
topic: Data platform consolidation pitch
description: Should we pitch consolidating their data platforms to the CIO this quarter?
background: |
  Context, constraints, prior work, what we know about the buyer.
urgency: medium          # low | medium | high  (optional)
stakeholders: CIO, VP Data Engineering   # optional
guests: [ciso]           # optional guest specialists (see step 4)
```

Then: *"Process questions/data-platform-consolidation.yaml."* The Leader frames the question,
takes opening reactions from all specialists in parallel, runs several deliberation rounds,
calls a final vote, decides, and writes the outputs. It takes a while; progress shows as it goes.

### 3. Read the results

| File | What it is |
|---|---|
| `decisions/YYYY-MM-DD-{slug}.md` | Decision memo (read this first) |
| `decisions/YYYY-MM-DD-{slug}-discussion.md` | The whole debate, turn by turn |
| `decisions/YYYY-MM-DD-{slug}-transcript.json` | Verbatim record |
| `questions/done/` | The processed question |

Re-render a discussion any time: `python3 scripts/render_transcript.py decisions/<slug>-transcript.json`.

### 4. Bring in a guest specialist — `add-specialist`

> *"Add a head of security to this conversation."*

You are interviewed (title, real person or generic, their lens, what context they need); the
skill creates their agent (`.pi/agents/<slug>.md`), dossier (`company/profiles/<slug>/`) and, if
needed, a domain area such as `company/security/`. Guests **advise but do not vote**, any
number can join, and they are reusable. List them under `guests:` in a question, or let the
Leader propose guests when a question needs them.

### 5. Rerun a question with a guest

> *"Rerun the data-platform question with the CISO attached."*

The original question and decision stay untouched. The rerun is a fresh, independent
deliberation with its own memo (`…-with-ciso`), and the memo compares it with the original.

### 6. Teach the team — `record-outcome`

When you learn what the real team decided or how it played out:

> *"Record the outcome for the data-platform decision: the account actually deferred it to Q2."*

Each twin is scored against reality and a `calibration.md` in their dossier is updated; twins
load it on every future run. Run it against reruns too to see whether a guest improved accuracy.

### 7. Fill gaps

Twins flag facts they needed and lacked in `company/gaps.md`. *"Work through company/gaps.md."*
runs `company-research` against that list.

### Maintenance

| Task | How |
|---|---|
| Rebuild indexes after editing anything in `company/` | `python3 scripts/build_index.py` |
| Check documents have summaries/front-matter | `python3 scripts/build_index.py --check` |
| Update a document's context | Edit it (keep the front-matter), rebuild indexes |
| Retire a guest | Delete `.pi/agents/<slug>.md` (keep or remove its dossier and memory) |
| Reset what the team has learned | Clear `memories/` and `company/profiles/*/calibration.md` |

### Using Pi instead

Same files and skills. Agents are in `.pi/agents/`; `leadership.yaml` defines the core team.

```
pi                                   # start in iTerm2/tmux from the repo root
/login                               # connect your model provider
create my team named 'leadership' from the 'leadership.yaml' template.
send a message to the leader specialist with the following content: questions/<file>.yaml
close down the team                  # when done
```

Other skills (`company-research`, `add-specialist`, `record-outcome`) are used by asking Pi in
plain language. **Limitations on Pi:** the team template is fixed to the core roles, so guests
must be started ad hoc by name (they are not in `leadership.yaml`); the Leader
(`.pi/agents/leader.md`) will message them if asked. Claude is the better-tested path.

---

## How it works

```
 company/ (what they know)  ──►  convene  ──►  decisions/  ──►  record-outcome
   progressive, indexed          core five +      memo,            calibration.md,
   brief → area → document       CEO leader       discussion       memories/, gaps.md
        ▲                        (+ guests)                            │
        └────────────── company-research fills gaps ◄──────────────────┘
```

### The account background — `company/`

| Folder | Holds |
|---|---|
| `index.md` | **L0**: account brief + map of areas. Always loaded. |
| `financial/` | 10-K/10-Q summaries, earnings themes, segments, capital allocation |
| `technical/` | Technology decisions in place, what is being evaluated, vendors, architecture |
| `strategy/` | Stated priorities, market, competitors, regulatory pressure |
| `profiles/{leader,cfo,cto,coo}/` | A dossier per real executive: `persona.md`, bio, talks, interviews, `calibration.md` |
| `profiles/{moonshot,contrarian}/` | Account-specific angles for the two archetype roles |
| `profiles/<guest>/` | Guest specialists (`type: guest` in their `index.md`) |
| `gaps.md` | Facts the twins needed and didn't have |
| `_templates/` | Document templates (persona, financial, general) |

Every folder has an `index.md` (**L1**) listing its documents with summary, tags, date,
confidence and which roles should load it. Twins read L0, their own dossier, then only the
documents the question needs (**L2**); see `.pi/skills/profile-context/SKILL.md`. Documents
need front-matter with at least a `summary`; see `company/_templates/`.

### Skills

| Skill | Purpose |
|---|---|
| `convene` *(Claude)* / `leader` agent *(Pi)* | Run the deliberation |
| `profile-context` | Progressive context loading, for leader and every specialist |
| `company-research` | Populate/extend `company/`: bootstrap, ingest files, fill gaps, refresh |
| `add-specialist` | Introduce a guest specialist |
| `record-outcome` | Compare reality to the twins, write calibration |
| `memory-management` | Each twin's own decision memory and peer patterns |
| `decision-input`, `memo-format` | Question and memo formats |

### Directories

| Directory | Purpose |
|---|---|
| `company/` | Account knowledge, **git-ignored** (read-only to twins; written only by `company-research` and `record-outcome`) |
| `company-template/` | Generic skeleton copied to `company/` on setup (tracked) |
| `questions/`, `questions/done/` | Pending and processed questions |
| `decisions/` | Memos, transcripts, discussions, outcomes |
| `memories/` | Per-role episodic memory (created as the team runs) |
| `scripts/` | `build_index.py`, `render_transcript.py` |
| `.pi/agents/`, `.pi/skills/` | Role prompts and shared skills |
| `.claude/skills/` | `convene` plus symlinks to the shared skills |

---

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| `company/` doesn't exist | Run `cp -R company-template company`, then `company-research`. |
| Team says the account has no context | `company/index.md` is still the template. Run `company-research`. |
| Twins sound generic | Dossiers are thin or `person:` is `TBD`. Add `persona.md` and sources; check `company/gaps.md`. |
| A skill isn't found in Claude | You opened a subfolder, or symlinks didn't survive the clone (see Install). |
| New documents aren't being used | Indexes are stale. `python3 scripts/build_index.py`. |
| Guest not available | Needs `.pi/agents/<slug>.md` and `company/profiles/<slug>/`. Run `add-specialist`. |
