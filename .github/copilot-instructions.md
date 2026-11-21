# Leadership Team - Digital Twins

This workspace simulates customer teams from reusable profiles. Each named team
has one profile-backed leader and participants who vote or advise; it can be a
core leadership team, extended leadership team, DBA team or another working team.
All output is a simulation based on public and supplied context, never statements
or predictions by real people.

## One session, one account

- Run **account-scope** before customer work. It explicitly selects `{account}` =
  `accounts/{slug}`. For shared repository maintenance, skip customer selection
  and do not read or write customer workspaces.
- Never access another account. For a different customer, start a fresh session
  to avoid mixing context.
- Account isolation is workflow guidance, not automatic enforcement or a security
  boundary. There are no account-lock commands or runtime identity requirements.
  Only the facilitator selects the account; specialists receive its explicit scope.

## Route by intent

| User intent | Workflow |
|---|---|
| Select/create a customer | account-scope |
| Define a team, choose leader/participants or change membership | define-team |
| Evaluate a proposal, ask a named team for a decision or run a decision scenario | evaluate |
| Brainstorm, develop and prioritize ideas with a named team | brainstorm |
| Scope an idea moving forward and build a high-level plan with blockers/mitigations | scope |
| Build a company profile or research company knowledge | company-research (calls person-profile for selected leaders) |
| Build, research or refresh a person profile for any professional role | person-profile |
| Set up/reuse a specialist profile for team assignment | person-profile, then define-team |
| Compare a simulation with the real outcome | record-outcome |
| Read a past discussion | Open the explicitly selected team's discussion |

For an explicit brainstorming request or question `workflow: brainstorm`, run
account-scope, then brainstorm; conflicting workflow selections require clarification.
For scoping/high-level planning intent or `workflow: scope`, use account-scope,
then scope, with an explicit idea and move-forward basis.
Other questions with no instruction use account-scope, then evaluate. **Team
selection is explicit:** use the named team in the request or question `team:`.
If absent, list and ask, even for one team. If request and question disagree,
clarify. Never silently default to core leadership or infer membership from a topic.
Different teams within the selected account can be used in the same session.

## Shared mechanisms and account layout

- `scripts/teams.py`: `profiles`, `list`, `new`, `check`, `resolve`.
  Resolve validates profiles, room and vote/advisor assignments.
- `scripts/profiles.py`: `new`, `check`, `migrate-memory`. Person-profile owns scaffolding and
  person research; company-research reuses it when building company leadership.
- `{account}/company/`: shared knowledge, progressively loaded via indexes
  (company brief -> profile/area index -> relevant document). Never bulk-read it.
- `{account}/company/profiles/{profile-id}/`: one reusable dossier per person or
  explicit generic role. Existing IDs such as `leader` (CEO), `cfo`, `cto`, `coo`
  remain valid; other professionals use the same structure. Profile `type` does
  not determine leadership, membership or voting.
- `{account}/teams/{team-slug}/team.json`: purpose, one leader profile, participant
  profile references and boolean votes, optional archetypes and escalation.
- Each team owns `questions/` (+ `done/`) and `decisions/`. Person discussion
  memory lives at `{account}/company/profiles/{profile-id}/memory.md`, reusable
  across teams and assignments, including the leader. Calibration is account-wide
  too. Only synthetic archetype memory stays in `{team}/memories/{archetype-id}.md`.
  Memory entries retain team/run provenance; never read peers' memory files.
  Legacy team-local person history can be explicitly imported with
  `profiles.py migrate-memory`; source files are preserved, not used as fallback.
- `.github/skills/` owns workflows. Evaluate, brainstorm and scope inject generic leader/participant
  resources plus profile-context and memory-management into the native
  `.github/agents/leadership-specialist.agent.md` via `task`. Use model defaults;
  omit each specialist `model` parameter so every subagent inherits the orchestrator
  session model. Never assign seat-specific or remembered model choices.
  never substitute an unscoped general-purpose agent.
- `scripts/build_index.py {slug}` rebuilds company indexes after intentional
  company-document changes. `scripts/render_transcript.py` renders named-team
  transcripts with snapshotted identities without rewriting the JSON input.

## Invariants

- Account folders are gitignored customer data. Never commit them or copy account
  facts into shared files, role prompts or `company-template/`.
- Pass the selected account, selected team, assignment and own memory path to each
  specialist. Specialists read company context, write only their own memory and
  never select accounts or delegate further.
- Exactly one leader always attends. Question `attendees` may restrict participants.
  All membership and voting/advisor assignments come from `team.json`. Advisors
  are participants with `vote: false` and brief first. Retired `guests:` input must
  be explicitly converted through define-team before running, never silently
  ignored or used to bypass team membership. No silent room changes.
- Contrarian/Moonshot are optional synthetic perspectives, separate from real
  participant votes. The leader decides by argument quality and is not tallied.
- Snapshot the definition and effective room in each transcript. Editing membership
  never rewrites history; reruns get fresh input/output names.
- Only company-research, person-profile and record-outcome change researched
  dossier documents. Each seat may append its own designated `memory.md`, which
  indexing and evidence checks exclude. The facilitator may append collected
  gaps to the company gaps log. Unknown facts stay unknown.
- Use only public professional information about real individuals.
