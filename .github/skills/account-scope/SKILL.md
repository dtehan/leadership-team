---
name: account-scope
description: Explicitly select the one customer account this session works on, without runtime locks. Use before customer work, including evaluate, brainstorm, scope, company-research, person-profile or record-outcome, and when the user asks to change customer.
---

# Account Scope

The user (typically an account manager) may have several customers in this workspace, each
a self-contained folder `accounts/{slug}/` (`company/` and named `teams/`).
**A session works on exactly one account.** The twins carry that account's
facts, people and memories; mixing two customers in one session would contaminate the
simulation and could leak one customer's information into another's.

In every skill and agent prompt, `{account}` means `accounts/{slug}` for the active account.

For repository maintenance only (generic prompts, scripts, docs, runtime setup), skip account
selection and stay in shared files. Do not read or write any customer workspace.
Subagents given an already selected `{account}` use that scope; do not ask the user to
select it again. Only the facilitator selects the account. No hook, session ID or
lock command is required. Isolation is workflow guidance, not automatic enforcement
or a security boundary.

## 1. Select the account (first thing, before reading any account data)

1. Reuse an account explicitly selected earlier in this session. Otherwise run
   `python3 scripts/accounts.py list`.
2. If the user's message names a customer, match it to a slug (ask if ambiguous).
   Otherwise ask which account to use, listing the slugs. Even when only one account
   exists, confirm it rather than assuming.
3. If there are no accounts, or the customer is new, offer
   `python3 scripts/accounts.py new <slug>`, then the **company-research** skill.
4. Confirm the selected slug exists in the list or was just created. Set
   `{account}` = `accounts/{slug}` and keep all customer work inside it. If a
   supplied question includes `account:`, check that it and the account/team path
   match the selection before opening dossiers or running a team. Conflicts
   require clarification, not a silent account change.
5. Announce the selection in plain words, e.g.:

   > Working on **{Account name}** (`accounts/{slug}`). Customer work will stay
   > within this account. Use a fresh session for a different customer.

## 2. Stay within the selected scope

- Read and write only under `{account}/`. Never open any other `accounts/*` folder, even to
  compare, borrow a pattern or "check how we handled it elsewhere".
  Scope customer searches to that account; shared repository maintenance needs
  no account selection and must not traverse customer workspaces.
- If the user names a different customer, or asks to switch, **do not switch and do not
  read that account.** Tell them: "Changing customer needs a new session so the team
  doesn't mix the two accounts. Start a fresh session and
  tell me which account." Offer to finish or save any work for the current account first.
- Facts the user types about another customer are not account data: don't write them
  into this account's `company/`, memories or decisions.
- A rerun, outcome or follow-up question about the **same** account is fine.

## 3. Pass the scope on

- Every subagent prompt (participants, advisors, archetypes) must state the active account explicitly:
  "Your account workspace is `accounts/{slug}`. Read and write only inside it. Your
  team workspace is `accounts/{slug}/teams/{team-slug}`. Your memory is
  `accounts/{slug}/company/profiles/{profile-id}/memory.md` and your dossier is
  `accounts/{slug}/company/profiles/{profile-id}/`. Reuse your own memory across
  teams within this account." For synthetic archetypes only, supply
  `accounts/{slug}/teams/{team-slug}/memories/{archetype-id}.md` instead.
- Transcripts record `session.account` = slug plus the selected team and snapshotted
  room. Memos name the account and team in their header. Several teams may be
  used within this same account selection; use a fresh session for a different customer.
- Scripts take the slug: `python3 scripts/build_index.py {slug}`.

## Shared vs per-account

Shared and tracked (no account facts ever): `.github/` instructions and skills, `company-template/`,
`scripts/`. Per account and git-ignored: everything under `accounts/{slug}/`.
A person's dossier and discussion memory live together in their account-local
profile and are reusable across teams. Synthetic archetype memory stays inside
its selected team. Named teams use generic prompt resources and do not need
shared per-person role prompts.
