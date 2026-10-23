# Leadership Team — Digital Twin

Simulation tools are an interesting way for us to explore the dynamics of leadership teams and how they make decisions.  The goal is to provide a tool that can be used to explore the tradeoffs and concerns that a leadership team would have when making decisions.  This can be used to inform our own actions and decisions.  As you build greater context of the organization, the people, and the memories of past discussions, your simulations will become richer.  The intent of this project is not to predict the future, rather to prepare you to understand different futures. 

A digital twin of an organizations's leadership team, note that it is not titles but people you r are trying to simulate, I have chosen specific roles, however these can be modified. 
Pose a question to the core team and read the debate the CEO, CFO, CTO and COO — plus a Moonshot and a Contrarian (added to ensure that there are diverse perspectives) — would have about it, then get a decision memo. 
Many leadership teams are bringing in Specialists such as a head of security to enrich a specific conversations. So you can add a guest specialist with a complete back story, we use specialists to educate the leadership team on a specific topic and be a part of the discussion, but they do not vote.
As the leadership team learns: memorys of past discussions can be added to the memory so that future decisions have visibility to their past, each decision can later be compared with what the real team actually did, and the twins are calibrated.


The value is in **what the team would say and why**, not in the decision itself. 

> Output is a **simulation** built from public and supplied information. It is not what the
> real executives said, and it is not a prediction to rely on.


There is two versions of the implementation:
1. Claude Desktop: A skills l variation of the above, with a zip file per skill and a `START-HEAR.html` guide.  This big difference is that the desktop version does not support subagents, and the user need to manage the memory via files within a project.
2. Claude Code: a Claude Project with the skills and a skeleton account template. It runs in the Claude Code CLI or Desktop (Code tab). The twins are in `.claude/skills/` and `.pi/skills/`.  This leverages subagents.

In building this project I have focused on the claude code version and then had to make tradeoffs for the claude chat version.



----

## Claude Desktop Version

### Installation
Follow the instructions in the `dist/START-HERE.html` file.  This will install the skills and provide a guide to using them.

### Usage
1. Install the skills
2. Create a project in claude desktop chat for each organization you want to simulate.
3. Create an initial organization brief via a chat with the account-brief-builder skill.  This will generate a markdown file that will need to be saved into your project context.
4. Add any additional information to the project context that you want the team to have access to.
5. Ask a question via the convene skill.  This will generate a decision memo and a discussion transcript.  If you want to maintain a memory of decisions then you will need to add the memo to the project context.

### The value
The value is in **what the team would say and why**, not in the decision itself.  Use the discussion to understand the concerns that a leadership team would have and the tradeoffs they would consider.  Use this insight to inform your own actions.




----
## Claude Code version

**One workspace, many customers, one customer per session.** Each customer lives in its own
folder, `accounts/<slug>/`, holding that customer's `company/` knowledge, `questions/`,
`decisions/` and `memories/`. All of `accounts/` is git-ignored. **Account data never goes into
this template.** The generic starting skeleton is `company-template/`, copied into each new
account. A session works on **one account only**: the twins carry that customer's facts, people
and memory, so switching customer means **starting a new session** (`/clear`, or exit and
run `claude` again). If you ask for a different customer mid-session, the assistant will
decline and tell you this. A hook (`scripts/account_guard.py`, configured in `.claude/settings.json`) also blocks tool access to any other account's folder once the session is locked; it is a guardrail rather than a security boundary, and you may be asked to approve project hooks the first time. If you want accounts under version control, use a private repo and
remove `accounts/*` from `.gitignore` there.

---

### Install

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
python3 scripts/accounts.py new acme   # create accounts/acme/ (git-ignored) from the template
# optional: point it at your own private remote so nothing goes back to the template
git remote set-url origin <your-private-repo-url>
```

Skills are shared between runtimes: `.claude/skills/` contains symlinks into `.pi/skills/`.
Symlinks work on macOS/Linux; on Windows enable Developer Mode and
`git config core.symlinks true` before cloning.

**Claude Desktop / Claude Code**: nothing to install. Open the folder as the project
(Desktop: Code tab → choose the folder; CLI: run `claude` from the repo root, **not** a subfolder).
Claude loads `CLAUDE.md` and the skills automatically.

**Sending it to account managers (Claude Desktop, no Code tab):** run `python3 scripts/package.py`. It writes
one zip per skill in `desktop-skill/` (brief builder, team, guest builder) plus `START-HERE.html`, all in `dist/`.
Send them all. They upload each zip under Settings > Capabilities > Skills and make one Claude Project per customer.
The guide's source is `docs/START-HERE.html`. For Claude Code users, `python3 scripts/package.py --code` builds the
folder tool zip instead (no customer data, symlinks flattened).

**Pi (secondary)**

```bash
npm install -g @mariozechner/pi-coding-agent
pi install npm:pi-subagents
pi install npm:pi-teams
```

---

### Operate

Work from the repo root. Everything below is a plain-language request; the skill noted
runs automatically.

#### 1. Populate the account — `company-research`

> *"Bootstrap Acme Corp."* — or *"Ingest this annual report"* (drop files in `accounts/<slug>/company/<area>/sources/`).

It collects the 10-K/10-Q/proxy, technology decisions in place and under evaluation, strategy,
and a dossier per leader; rebuilds the indexes; and lists the questions only you can answer
(internal knowledge, relationships, politics). **The team refuses to convene on an empty
account**: `accounts/<slug>/company/index.md` must be populated first.

Then confirm each role's real person: `accounts/<slug>/company/profiles/{leader,cfo,cto,coo}/index.md` should
have `person:` and `title:` filled in.

#### 2. Ask a question — `convene`

Either type it (*"Convene the team on: should we pitch a data-platform consolidation to the account
this quarter?"*) or save a file in `accounts/<slug>/questions/`:

```yaml
# accounts/<slug>/questions/data-platform-consolidation.yaml
topic: Data platform consolidation pitch
description: Should we pitch consolidating their data platforms to the CIO this quarter?
background: |
  Context, constraints, prior work, what we know about the buyer.
urgency: medium          # low | medium | high  (optional)
stakeholders: CIO, VP Data Engineering   # optional
guests: [ciso]           # optional guest specialists (see step 4)
```

Then: *"Process accounts/<slug>/questions/data-platform-consolidation.yaml."* The Leader frames the question,
takes opening reactions from all specialists in parallel, runs several deliberation rounds,
calls a final vote, decides, and writes the outputs. It takes a while; progress shows as it goes.

#### 3. Read the results

| File | What it is |
|---|---|
| `accounts/<slug>/decisions/YYYY-MM-DD-{slug}.md` | Decision memo (read this first) |
| `accounts/<slug>/decisions/YYYY-MM-DD-{slug}-discussion.md` | The whole debate, turn by turn |
| `accounts/<slug>/decisions/YYYY-MM-DD-{slug}-transcript.json` | Verbatim record |
| `accounts/<slug>/questions/done/` | The processed question |

Re-render a discussion any time: `python3 scripts/render_transcript.py accounts/<slug>/decisions/<slug>-transcript.json`.

#### 4. Bring in a guest specialist — `add-specialist`

> *"Add a head of security to this conversation."*

You are interviewed (title, real person or generic, their lens, what context they need); the
skill creates their agent (`.pi/agents/<slug>.md`), dossier (`accounts/<slug>/company/profiles/<slug>/`) and, if
needed, a domain area such as `accounts/<slug>/company/security/`. Guests **advise but do not vote**, any
number can join, and they are reusable. List them under `guests:` in a question, or let the
Leader propose guests when a question needs them.

#### 5. Rerun a question with a guest

> *"Rerun the data-platform question with the CISO attached."*

The original question and decision stay untouched. The rerun is a fresh, independent
deliberation with its own memo (`…-with-ciso`), and the memo compares it with the original.

#### 6. Teach the team — `record-outcome`

When you learn what the real team decided or how it played out:

> *"Record the outcome for the data-platform decision: the account actually deferred it to Q2."*

Each twin is scored against reality and a `calibration.md` in their dossier is updated; twins
load it on every future run. Run it against reruns too to see whether a guest improved accuracy.

#### 7. Fill gaps

Twins flag facts they needed and lacked in `accounts/<slug>/company/gaps.md`. *"Work through accounts/<slug>/company/gaps.md."*
runs `company-research` against that list.

#### Maintenance

| Task | How |
|---|---|
| Rebuild indexes after editing anything in `accounts/<slug>/company/` | `python3 scripts/build_index.py <slug>` |
| Check documents have summaries/front-matter | `python3 scripts/build_index.py <slug> --check` |
| Update a document's context | Edit it (keep the front-matter), rebuild indexes |
| Retire a guest | Delete `.pi/agents/<slug>.md` (keep or remove its dossier and memory) |
| Reset what the team has learned | Clear `accounts/<slug>/memories/` and `accounts/<slug>/company/profiles/*/calibration.md` |

#### Using Pi instead

Same files and skills. Agents are in `.pi/agents/`; `leadership.yaml` defines the core team.

```
pi                                   # start in iTerm2/tmux from the repo root
/login                               # connect your model provider
create my team named 'leadership' from the 'leadership.yaml' template.
send a message to the leader specialist with the following content: accounts/<slug>/questions/<file>.yaml
close down the team                  # when done
```

Other skills (`company-research`, `add-specialist`, `record-outcome`) are used by asking Pi in
plain language. **Limitations on Pi:** the team template is fixed to the core roles, so guests
must be started ad hoc by name (they are not in `leadership.yaml`); the Leader
(`.pi/agents/leader.md`) will message them if asked. Claude is the better-tested path.

---

### How it works

```
 accounts/<slug>/company/ (what they know)  ──►  convene  ──►  accounts/<slug>/decisions/  ──►  record-outcome
   progressive, indexed          core five +      memo,            calibration.md,
   brief → area → document       CEO leader       discussion       accounts/<slug>/memories/, gaps.md
        ▲                        (+ guests)                            │
        └────────────── company-research fills gaps ◄──────────────────┘
```

#### The account background — `accounts/<slug>/company/`

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
need front-matter with at least a `summary`; see `accounts/<slug>/company/_templates/`.

#### Skills

| Skill | Purpose |
|---|---|
| `convene` *(Claude)* / `leader` agent *(Pi)* | Run the deliberation |
| `profile-context` | Progressive context loading, for leader and every specialist |
| `company-research` | Populate/extend `accounts/<slug>/company/`: bootstrap, ingest files, fill gaps, refresh |
| `add-specialist` | Introduce a guest specialist |
| `record-outcome` | Compare reality to the twins, write calibration |
| `memory-management` | Each twin's own decision memory and peer patterns |
| `decision-input`, `memo-format` | Question and memo formats |

#### Directories

| Directory | Purpose |
|---|---|
| `accounts/<slug>/company/` | Account knowledge, **git-ignored** (read-only to twins; written only by `company-research` and `record-outcome`) |
| `company-template/` | Generic skeleton copied to `accounts/<slug>/company/` on setup (tracked) |
| `accounts/<slug>/questions/`, `accounts/<slug>/questions/done/` | Pending and processed questions |
| `accounts/<slug>/decisions/` | Memos, transcripts, discussions, outcomes |
| `accounts/<slug>/memories/` | Per-role episodic memory (created as the team runs) |
| `scripts/` | `accounts.py` (list/new/lock), `account_guard.py` (session-lock hook), `build_index.py <slug>`, `render_transcript.py` |
| `.pi/agents/`, `.pi/skills/` | Role prompts and shared skills |
| `.claude/skills/` | `convene` plus symlinks to the shared skills |

---

### Troubleshooting

| Symptom | Cause / fix |
|---|---|
| `accounts/<slug>/company/` doesn't exist | Run `python3 scripts/accounts.py new <slug>`, then `company-research`. |
| Team says the account has no context | `accounts/<slug>/company/index.md` is still the template. Run `company-research`. |
| Twins sound generic | Dossiers are thin or `person:` is `TBD`. Add `persona.md` and sources; check `accounts/<slug>/company/gaps.md`. |
| A skill isn't found in Claude | You opened a subfolder, or symlinks didn't survive the clone (see Install). |
| New documents aren't being used | Indexes are stale. `python3 scripts/build_index.py <slug>`. |
| Guest not available | Needs `.pi/agents/<slug>.md` and `accounts/<slug>/company/profiles/<slug>/`. Run `add-specialist`. |


