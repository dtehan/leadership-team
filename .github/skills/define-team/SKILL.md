---
name: define-team
description: Define or change a named team from available account profiles, with one leader and voting participants or advisors. Use for core or extended leadership teams, specialist teams such as DBAs, and membership changes.
---

# Define a Team

Success means a validated, named team with exactly one profile-backed leader and at
least one participant, ready to evaluate or brainstorm by name. Profiles are reusable across teams.
All outputs are simulations, not statements or predictions by real people.

## Scope and inputs

Run **account-scope** first. `{account}` is the selected account, `{slug}` its account
slug, and `{team}` is `{account}/teams/{team-slug}`. Stay inside that account.
Never put identities or account facts in shared prompts or the company template.

Ask only for missing choices: team name and purpose, leader, participants, which
participants advise without voting, optional Contrarian/Moonshot perspectives, and
decision authority or escalation. Use the user-question tool for clarification.
No person, synthetic perspective or reporting manager is silently added.

## Define or change

1. Run `python3 scripts/teams.py profiles {slug}` and
   `python3 scripts/teams.py list {slug}`. These read profile indexes, not dossier
   documents. Show available profiles and thin-profile warnings. For a selected
   profile, load its index before going deeper.
2. Select existing profiles by their stable folder identifiers. `leader`, `cfo`,
   `cto` and `coo` are usable profile IDs, not privileged seats. Only the team
   defines leadership, membership and voting assignments. Reuse an existing
   profile rather than copying its dossier.
3. If a desired person is missing, use **person-profile** to create their
   `company/profiles/{profile-id}/index.md`, `persona.md` and sourced documents.
   Capture name, title and relevant areas. Unknown identity means an explicitly
   generic role profile, never an invented biography. Rebuild and check indexes.
4. Create the team, using repeatable flags for people:
   ```text
   python3 scripts/teams.py new {slug} {team-slug} --name "{display name}" --purpose "{purpose and decision authority}" --leader {leader-profile} --participant {profile} --advisor {advisor-profile} --facilitation contrarian --escalates-to "{authority}"
   ```
   Omit optional advisors, facilitation and escalation if not requested. There are
   no automatic members or archetypes. The leader makes the simulated decision
   and is not included in the participant vote tally.
5. To change an existing team, read and edit only `{team}/team.json`. Its fields:
   `name`, `purpose`, `leader`, `participants` (objects with `profile` and boolean
   `vote`, default true), `facilitation` (unique `contrarian`/`moonshot` list),
   `escalates_to` (string or null).
   Keep the team slug stable. No nesting or inheritance. Membership changes do
   not delete profiles, memories or history.
   All people in a deliberation, including advisors, must be defined here.
   If a different room is wanted for one scenario, create another named team using
   the same profiles or explicitly approve a change to this team; do not bypass
   it with question fields.
6. Run `python3 scripts/teams.py check {slug} {team-slug}`. Correct structural
   errors before continuing. Thin profiles warn rather than fabricate detail;
   disclose the limits and offer research before a run. Confirm who leads,
   who votes, who advises, any archetypes, purpose and escalation.

Questions and decisions live under `{team}/questions/` and `{team}/decisions/`.
Person discussion memory and calibration are shared across teams in the account's
profiles (`memory.md` and `calibration.md`). `{team}/memories/` is for optional
synthetic archetypes only; membership changes do not move or reset person memory.

## Completion

Return the team name, leader, participants/advisors, profile limits and a prompt
such as "Have {team-slug} evaluate this proposal ..." or "Brainstorm with
{team-slug} on ...". Do not run either workflow until asked.
