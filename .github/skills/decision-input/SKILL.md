---
name: decision-input
description: Format for structured team questions. Parses and validates evaluation, brainstorming and scoping requests.
---

# Decision Input Format

When receiving an evaluation, brainstorming or scoping request, parse it into this structure:

## Required Fields
- **Account**: The account slug. Persist it as `account:` and ensure the question
  is saved under `accounts/{account}/teams/{team}/questions/`. Match it to the
  account explicitly selected through **account-scope**; conflicts stop the run
  for clarification. This metadata does not establish a lock. Existing questions
  without it remain usable after explicit account selection and path checks.
- **Team**: The named team's slug. It may come from the user's explicit request;
  persist it as `team:` in the saved question. If absent from both input and request,
  list teams and ask. If the two disagree, stop for clarification. Never default
  to the former core leadership team.
- **Topic**: A short title for the team discussion (under 80 characters)
- **Description**: What needs deciding, or the open-ended challenge to explore
  in a brainstorm, or the selected idea to scope (1-3 sentences)
- **Background**: Relevant context, constraints, and prior work (1-3 paragraphs)

## Optional Fields
- **Workflow**: `evaluate` (decision, default), `brainstorm` (ideas and priorities)
  or `scope` (boundaries and high-level plan).
  Legacy `convene` input means evaluate; normalize it to `evaluate` in fresh input,
  without rewriting archived questions or transcripts.
  Explicit brainstorming/scoping intent selects that workflow when omitted. If the request
  and field disagree, or the value is unknown, stop and clarify before running.
  Persist the selected workflow for new input.
- **Source evaluation** (`source_evaluation`): For scope, an account-relative
  completed evaluate transcript identifying the idea and move-forward basis.
  It does not select the team or prove actual organizational approval.
- **Move-forward basis** (`move_forward_basis`): For scope without a linked
  evaluation, explicit user direction that this particular idea should move forward.
  Require this or a usable source evaluation; never infer it from a brainstorm rank.
- **Planning constraints** (`planning_constraints`): Known budget/capacity,
  deadlines, dependencies and potential blockers for scope. Missing values stay
  unknown; record assumptions and mitigation investigations instead of estimates.
- **Priority criteria**: For brainstorming, criteria used to compare ideas.
  Default to impact, feasibility and evidence/confidence; state these in framing
  before generating ideas. Criteria guide ordinal rankings, not fabricated scores.
- **Urgency**: low / medium / high (default: medium)
- **Stakeholders**: Who is affected by this decision
- **Rerun of**: Account-relative path to the original transcript (set when rerunning;
  see evaluate).
- **Attendees**: Optional subset of the team's participant profile IDs. The leader
  always attends and is not included in this list. Omit to use all participants.
  Unknown or duplicate IDs block the run; no silent additions or removals.

Membership and advisor assignments come only from the selected team's definition.
If older input contains `guests:`, stop before evaluating, explain that the field is
retired and offer to add those profiles through **define-team** as non-voting
participants. Obtain approval, validate the revised team and save fresh input
without `guests:`; never silently ignore the field or add people at question time.

## Parsing

If the user provides a free-form prompt, extract these fields as best you can.
If the user provides structured input (YAML, JSON, or markdown with headers),
parse it directly.

Example structured input:

```yaml
account: example-company
team: core-leadership
topic: European Market Expansion
description: Should we open a sales office in Berlin and localize our product for the EU market?
background: |
  We have 15% of revenue from EU customers via self-serve.
  Three competitors have established EU presence in the last year.
  Our product needs GDPR compliance work estimated at 3 months.
  Available budget: $2M for first year.
urgency: high
```
