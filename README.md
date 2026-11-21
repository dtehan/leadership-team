# Leadership Team - Digital Twins for Copilot CLI

Explore how a customer's teams might reason about a decision using **GitHub
Copilot CLI**. Define named teams from reusable profiles: core leadership,
extended leadership, DBAs or any other professional team. Each has one leader
and participants who vote or advise. Optional Contrarian/Moonshot perspectives
challenge the room without pretending to be real people.

**All output is a simulation based on public and supplied information, never
statements or predictions by the real people.** The value is in the arguments,
trade-offs and dissent, not a prediction.

## Start here

1. Install the requirements and launch Copilot from the repository root.
2. Select or create one account and build its company context and profiles.
3. Define a named team with a leader and participants from those profiles.
4. Ask that team to deliberate; read its memo alongside the discussion.
5. Record what actually happened to improve future simulations.

Open the [setup and operations handbook](docs/USER-GUIDE.html) in a browser for
company and people profiles, team creation, maintenance, and diagrams explaining
when to brainstorm, evaluate or scope.

For a proposed adaptation to another agent platform, see the
[Claude Code and Pi porting guide](docs/PORTING-GUIDE.md). These ports are not
implemented or supported by the current repository.

## Requirements and setup

- Git and Python 3.8+ (standard library only; no package installation).
- [GitHub Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/cli-getting-started),
  signed in, supporting repository skills and native custom agents.

```bash
git clone https://dev.azure.com/danieltehan/Leadership/_git/Leadership
cd Leadership
copilot
```

Review configuration before trusting it. Copilot
loads [.github/copilot-instructions.md](.github/copilot-instructions.md),
the skills under [.github/skills/](.github/skills/) and the
[specialist agent](.github/agents/leadership-specialist.agent.md).
Check `/instructions` and `/skills list` inside Copilot.
`copilot instruction list --json` and `copilot skill list --json` show discovery
from a terminal. The native specialist agent is invoked by evaluate, brainstorm or scope, not manually.

**After updating, exit old sessions and start a fresh Copilot session.** Reloading
skills alone does not reload instructions or hooks. Do not resume a pre-upgrade
session. This repository supports Copilot CLI only; do not reinstall old Claude
Code, Pi or Claude Desktop integrations.

## One customer per session, multiple teams

Each customer has a gitignored workspace under `accounts/<slug>/`. Explicitly select
one account before accessing its content. Several teams in that account may be
used in the same session. Use a fresh session for a different customer to
avoid mixing context.

Account selection and isolation are **workflow guidance, not automatic
enforcement or a security boundary**. There is no account-lock command, hook
requirement or runtime session/parent ID dependency. Specialists receive the
facilitator's explicit account, team and memory paths and cannot choose another
customer. Do not rely on this repository for hostile-code isolation.

Shared repository maintenance requires no account selection and must stay out of
customer workspaces. Never commit account data or put it in shared prompts or the
generic company template. Gitignored does not mean encrypted or local-only:
Copilot processes supplied context and company research may use online sources.
Follow organizational data-handling policies and use only authorized material.

## Operate

### Populate profiles and define teams

> "Work on Example Company. Create the account if needed and build its context."
>
> "Build the company profile, including researched profiles for its leadership."
>
> "Build a person profile for Alex Example, the database lead."
>
> "Show the available profiles."
>
> "Define core-leadership with the CEO as leader and CFO, CTO and COO as participants."
>
> "Define dba-team with Alex as leader, Sam and Jo as participants and the CTO as advisor."

**company-research** builds company knowledge and calls **person-profile** for
each selected leader. **person-profile** is also available on its own for managers,
specialists and any other professional role, without requiring team membership.
It creates the dossier structure, researches public professional sources, records
gaps and reuses existing people rather than creating duplicate profiles.
**define-team** reuses
profiles and confirms purpose, leader, participants, voting, optional synthetic
perspectives and escalation. Thin evidence produces generic reasoning, not
fabricated biography. A profile can lead one team and advise or vote in another.
Only the selected team defines that assignment.

The profile helper's `new` command creates an unfinished scaffold, not a verified
biography. Profiles with `evidence_status: pending`, `thin` or `generic` remain
thin when teams resolve them. `grounded` is set only after reviewing evidence;
structural checks do not certify research. Existing dossiers without this field
continue to work unchanged. Refreshing existing real-person dossiers requires
approval and never silently replaces the person behind a stable ID.

### Refresh research without starting over

> "Refresh the company research and its existing leadership profiles. Check for
> updates and leave unchanged information alone."
>
> "Recheck Alex Example's current role and priorities using the existing profile."

Both research workflows inventory existing evidence before searching and share
an account-local `company/sources/research-ledger.md`: sources, supported topics,
last successful checks, comparison results and next checks. Repeated builds reuse
coverage; explicit refreshes check the requested scope. Shared sources are fetched
once per run, not again for every person. Historical filings are reused while
discovery checks look for newer filings.

Only supported differences change knowledge documents. Unchanged checks update
the ledger, not profile prose, evidence dates or status. Failed checks are reported
as incomplete, never "no change." Results distinguish reused, checked-unchanged
and updated coverage and show material differences. Existing accounts adopt the
ledger from their citations without rebuilding all research. These are agent
workflow rules, not an automatic cache or a guarantee of source correctness.
See the [incremental research contract](.github/skills/company-research/references/incremental-research.md)
for default check intervals and evidence handling.

### Evaluate a proposal with a named team

> "Have dba-team evaluate the proposal to consolidate our database platforms."

Or save a question under that team's `questions/`:

```yaml
account: example-company
team: dba-team
workflow: evaluate
topic: Database consolidation
description: Should we consolidate this year?
background: |
  Describe the constraints, evidence and alternatives.
urgency: medium
```

For new questions, include `account:` matching the explicitly selected account
and question path. Older questions without it remain usable after explicit
account selection and path checks; a conflicting account requires clarification.
Question metadata never changes the active account automatically.

**evaluate** requires explicit team selection. If absent, it asks; conflicts
between a request and `team:` block until clarified. It never silently defaults
to the former core team. Optional `attendees:` restricts participants, while the
leader always attends. All membership and voting/advisor assignments come from
the team definition. Advisors are participants with `vote: false`, not a separate
guest category. Add specialists through **define-team**, or define another named
team for a different room. Retired `guests:` input must be explicitly converted
through an approved team update before it can run.

Advisors brief first, followed by opening reactions, at least four deliberation
rounds, final positions and a decision addressing dissent. Participant votes,
synthetic positions and advisor advice remain separate. The leader weighs
arguments, not majority count; decisions beyond authority become recommendations.

Copilot/user model defaults apply, with the orchestrator model inherited by every
seat. Specialist dispatch omits a model selection, so it never pins or varies
models between participants. One native
[specialist agent](.github/agents/leadership-specialist.agent.md) simulates each
seat with the supplied account scope. No per-person agent registration or team service is
required. The built-in general-purpose agent is not a supported substitute.
Costs are measured runtime values or `null`, never fabricated spending limits.

### Brainstorm and prioritize ideas

> "Brainstorm with dba-team: how could we improve database reliability?
> Develop the ideas, then prioritize them."

**brainstorm** is a separate workflow; **evaluate** keeps the existing decision
format. It reuses the selected team's profiles, membership and context. Advisors
brief first, everyone generates ideas independently, then the team develops and
stress-tests them over at least two refinement rounds. Ideas retain stable IDs,
assumptions and proposed next experiments, including lower-priority alternatives.

Voting participants independently rank every idea against the framed criteria
(default: impact, feasibility and evidence/confidence). Borda points summarize
their preferences; advisors, synthetic perspectives and the leader are not tallied.
The leader resolves ties and differences, explains departures and recommends a
prioritized shortlist. These are exploration priorities, not spending or
implementation approvals. At least one voting participant must attend.

Structured input uses `workflow: brainstorm` with the existing account, team,
topic, description and background fields; optional `priority_criteria` supplies
comparison criteria. Outputs use a `-brainstorm` basename in the team's existing
`decisions/` directory: idea/priorities memo, transcript and readable discussion.
The same renderer and `--check` command validate brainstorm provenance,
participation, refinement and rankings without imposing approve/deny votes.
Incomplete brainstorms leave input pending and append no brainstorm memories.
See the [brainstorm workflow](.github/skills/brainstorm/SKILL.md).

The former **convene** workflow is now **evaluate**. Restart Copilot to load the
renamed skill and routing. Existing questions and transcripts without `workflow:`
remain decision records; legacy `workflow: convene` is accepted as evaluate.
Historical outputs are not renamed or rewritten. Use `workflow: evaluate` for
new decision questions.

### Scope an idea and build a high-level plan

> "We want to move forward with the reliability pilot. Have dba-team scope it and
> build a high-level plan, including potential blockers and mitigation strategies."

**scope** accepts a linked completed evaluation or explicit user direction to
move an idea forward. A brainstorm ranking alone is not sufficient. It reuses
the selected team, including advisors, without formal votes. Advisors brief
first; everyone proposes boundaries, then at least two planning rounds develop
phases, dependencies and blockers. Everyone reviews the draft before the leader
synthesizes one combined scope-and-plan document.

The outcome includes success measures, in/out of scope, deliverables, assumptions,
constraints, high-level milestones/exit criteria, proposed owners and timing,
risks, dissent, open questions and next steps. Every blocker has a mitigation
strategy, a blocking gate, proposed owner and evidence/decision needed to clear it.
Unverified mitigations do not resolve blockers; unknown estimates stay unknown.
This is not a detailed task backlog or an implementation commitment.

Outputs use `-scope` basenames under the team's `decisions/` directory. Readiness
is `blocked` for an open start gate, `conditional` for open later-phase gates,
or `ready_for_review` when none remain open. A complete discussion can produce
a blocked plan. Incomplete discussions remain pending and append no scope memory.
The existing renderer's `--check` validates recorded planning, final reviews,
blocker fields and readiness consistency—not approval or mitigation effectiveness.
See the [scope workflow](.github/skills/scope/SKILL.md) and
[user guide](docs/USER-GUIDE.html#run) for structured input.

### Read results and close the loop

Under the account's `teams/<team>/`:

| Output | Purpose |
|---|---|
| `team.json` | Leader, participants, purpose, optional perspectives and escalation |
| `questions/`, `questions/done/` | Pending and archived input |
| `decisions/YYYY-MM-DD-<topic>.md` | Decision memo, rationale, dissent and next steps |
| `decisions/*-scope.md` | Combined scope, high-level plan, blockers and mitigations |
| `decisions/*-discussion.md` | Readable debate |
| `decisions/*-transcript.json` | Verbatim record and frozen definition/effective room |
| `memories/<archetype-id>.md` | Team-specific synthetic archetype memory, if configured |

Each person's discussion memory lives at
`company/profiles/<profile-id>/memory.md` within the account, alongside their
dossier and calibration. The same file follows them across teams as leader,
voter or advisor; entries retain their original team and run reference.
Only synthetic archetype memory stays team-local. Membership edits never rewrite
past outputs or reset a person's memory. Episodic memory is not researched evidence
and is excluded from company indexes and profile evidence checks.
Re-render with `python3 scripts/render_transcript.py <transcript-path>`;
named-team transcripts must include their team, leader and display-name snapshot.
JSON input is not rewritten.
Partial records render with an explicit incomplete-run warning.
Before treating a run as complete, use
`python3 scripts/render_transcript.py <transcript-path> --check`.
This writes nothing and checks the selected workflow. For evaluate it fails for
missing individual room identities, recorded responses, four numbered deliberation
rounds, final advice/votes or a matching participant-only tally.
Deliberation turns use `deliberation_round: 1`, `2`, etc.;
the declared round count alone is not proof of debate. Incomplete runs keep their
questions pending and must not be published as completed results.

> "Rerun that question with extended-leadership."
>
> "Record the outcome: the real team deferred until next quarter."

Reruns use fresh input and output names. Prior memos/transcripts are withheld until
the new decision is made, then compared. Eligible memory may mention the old run,
so this is not a blind test. **record-outcome** calibrates supported real positions,
including the historical leader and advisors; unknown positions remain unknown.

## Existing workspaces

After updating, define each desired team explicitly using the account's existing
profiles. There is no automatic import or alternate workspace fallback. New
questions and decisions belong only to the selected team; person memory belongs
to the reusable account-local profile.
Existing customer files are not moved, rewritten or deleted by the update.

Rendering and outcome recording require complete named-team records; files without
the required team identity/snapshot are not automatically interpreted or converted.

## Shared repository layout

| Path | Purpose |
|---|---|
| [.github/copilot-instructions.md](.github/copilot-instructions.md) | Routing and invariants |
| [.github/skills/](.github/skills/) | Team definition, evaluation, brainstorming, outcomes and context workflows |
| [.github/agents/leadership-specialist.agent.md](.github/agents/leadership-specialist.agent.md) | Scoped native seat agent |
| [.github/skills/evaluate/references/](.github/skills/evaluate/references/) | Generic team leader/participant prompts |
| [company-template/](company-template/) | Generic knowledge skeleton, no customer facts |
| [scripts/teams.py](scripts/teams.py) | Definitions, profile discovery, validation and room resolution |
| [scripts/](scripts/) | Account/team helpers, indexing, rendering and packaging |
| [tests/](tests/) | Disposable synthetic fixtures, never real customer data |

Company context loads progressively: brief, profile/area indexes, relevant docs.
After company-document edits, rebuild and check the active account's indexes with
`scripts/build_index.py`.

## Validate and distribute

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
python3 scripts/package.py
```

Packaging builds one workspace ZIP in `dist/`; `--output-dir <path>` selects a
destination outside customer workspaces. The old `--code` flag is rejected.
Packaging uses an explicit allowlist, never traverses customer data, rejects
symlinks and excludes local state and unrelated files. Review shared Markdown
before distribution; only generic content belongs there.

Tests cover definitions, overlapping profiles and cross-team memory paths/imports,
memory exclusion from knowledge indexes, explicit selection, advisors,
subsets, account setup without runtime locks, team-only account layout, frozen-room rendering,
invalid transcript rejection and packaged workspaces. They do **not** run model deliberations.
Live simulations use the configured model and consume credits.

The named-team workflow is not live-model certified by these tests. The live
advisor/rerun/outcome/session-lifecycle matrix remains uncertified.
Validate fresh-session discovery, specialist scope and
representative workflows in a disposable fictional project after CLI changes.

## Troubleshooting

| Symptom | Action |
|---|---|
| Skill missing or listed twice | Restart at the repository root; inspect `/skills list` and remove obsolete user registrations |
| Old account-lock messages after updating | Start a fresh session to unload cached instructions and hook registration; no lock command is needed |
| Specialist unavailable | Start a fresh session; do not substitute a general-purpose agent |
| Need a different customer | Start a fresh session to avoid mixing account context |
| Unexpected access denial | Stop and preserve the error; do not disable hooks or retry via another tool |
| Team missing or invalid | Use define-team, check the selected slug and resolve validation errors |
| No company context or generic twins | Use company-research to fill the brief and relevant dossiers |
| New company documents missing | Rebuild/check indexes for the active account |
| Advisor unavailable | Use person-profile to set up/reuse their profile, then define-team to add them with `vote: false` |
