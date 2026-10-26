---
name: define-group
description: Define a working group (e.g. a middle-management team) inside the locked account - who is in it, who chairs, who it escalates to - and link each member to their profile dossier. Use when the user wants to build a twin of a team of managers, add or remove a member, or link or research a member's profile.
---

# Define Group

> **Account scope:** run the **account-scope** skill first. This session works on one customer only; `{account}` = `accounts/{slug}`. Never touch another account; if the user asks to switch customer, tell them to start a new session.

The leadership team is fixed (CEO, CFO, CTO, COO). A **group** is a team the user defines: a
set of managers who decide things together (data platform leads, regional sales directors,
a change board). It lives inside one account, shares that account's `company/` knowledge, and
has its own roster, questions, decisions and memories.

```
{account}/groups/{group}/
  roster.md      who is in the group and how their profiles are linked (single source of truth)
  questions/     pending questions (+ done/)
  decisions/     memos, transcripts, discussions, outcomes
  memories/      one file per member (and per archetype seat)
```

Members' dossiers stay with the other profiles: `{account}/company/profiles/{member-slug}/`
(same shape as a leader's: `index.md` with `person:`/`title:`, `persona.md`, sources).

## Procedure

### 1. Create or open the group
`python3 scripts/groups.py list {slug}`. If the group exists, read its `roster.md` and go to
step 3. Otherwise `python3 scripts/groups.py new {slug} {group-slug}`.

### 2. Interview the user (only what you cannot already tell)
- **Purpose**: what the group is for and what it can decide on its own. Write it into the
  roster front-matter (`purpose:`).
- **Escalation**: who it reports its decisions to (`escalates_to:`, e.g. "CTO and COO").
  Anything outside the group's authority or budget becomes a recommendation to escalate.
- **Members**: for each, name, title, function and who they report to. Real people (twins) or
  generic seats ("Director of Procurement, unknown")? Mark generic seats so they are
  simulated from role and company facts only.
- **Chair**: a member (the twin runs the meeting in their style) or `neutral` (default; a
  facilitator with no function of their own).
- **Archetypes**: `facilitation: [contrarian]` is the default and recommended for peer groups
  (guards against deference and groupthink). Add `moonshot` if wanted, or leave empty.
- **Advisors**: members who attend but do not vote (`--advisor`).

### 3. Add members and link their profiles
For each member:

`python3 scripts/groups.py add {slug} {group-slug} {member-slug} "Name" "Title" [--reports-to cto] [--profile TARGET] [--chair] [--advisor]`

- `{member-slug}` is kebab-case (`priya-nair`); it cannot be a leadership role name.
- `--reports-to` is a leadership role (`leader`, `cfo`, `cto`, `coo`) or another member's slug.
  The member reads that person's dossier index to understand who they answer to.
- **Profile link** (`--profile`, or later `python3 scripts/groups.py link {slug} {group-slug} {member-slug} TARGET`):
  - *blank* (default): `company/profiles/{member-slug}/`, created as a stub for you to fill.
  - *a path inside the account*: an existing dossier folder, or a single file (a CV, a bio
    the user supplied under `company/`). Path is relative to `accounts/{slug}/`.
  - *an http(s) URL* (a LinkedIn page, company bio, speaker page): recorded as a link only;
    step 4 turns it into a dossier. LinkedIn and similar login-walled pages cannot be
    fetched: ask the user to paste or export the public text instead.
- The same person may sit in several groups of the same account; reuse the same member slug
  and profile (add the row to each roster; do not duplicate the dossier).

### 4. Build the dossiers
For each member whose profile is a stub or only a link, run the **company-research** skill for
that one dossier: `persona.md` from `company/_templates/persona.md`, plus one document per
substantial source. Use these roster-specific rules:
- Front-matter `roles: [{member-slug}]`, and `load: always` for `persona.md`.
- The member's `index.md` keeps `type: member` and an `areas:` list (L1 areas they should read by
  default; set it to what their function needs, e.g. `[technical, strategy]`).
- Middle managers are often less public than executives. If you find nothing, say so in the
  dossier index, describe the **role** generically (what someone with this title at a company
  like this typically owns and worries about), mark it *(generic, not a real person)*, and
  record the gap in `{account}/company/gaps.md`. Public professional information only.
- Ask the user what only they know: priorities, working style, relationships, what this person
  has pushed for or blocked. Record as *(account-manager input)* with the date.

Then run `python3 scripts/build_index.py {slug}` and `python3 scripts/build_index.py {slug} --check`.

### 5. Check and confirm
`python3 scripts/groups.py check {slug} {group-slug}` prints the resolved roster and warns about
a missing purpose or chair, unlinked profiles, stub dossiers and bad `reports_to`. Fix or
accept each warning. Then tell the user: who is in the room, who chairs, who votes, how
thin each profile is (a thin profile gives a generic twin), and that questions go in
`{account}/groups/{group-slug}/questions/` and are run with the **convene-group** skill.

## Changing the group
- **Remove a member**: delete their row in `roster.md` (keep their dossier and memory; the
  person may return or sit in another group).
- **Swap the chair**: edit `chair:` in the roster front-matter.
- **A role change in real life** (new manager in the seat): add the new member, remove the old
  row, and keep the old dossier and memory under the old slug.

## Rules
- Never write account facts into `company-template/`, `.pi/` or any tracked file.
- Do not invent facts about real people; unknowns go to `{account}/company/gaps.md`.
- Output about real individuals is a simulation, never a quote or prediction.
