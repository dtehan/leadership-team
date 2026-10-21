---
name: account-scope
description: Select and lock the one customer account this session works on. Every other skill depends on it. Use at the start of every session, before convene, company-research, add-specialist or record-outcome, and whenever the user mentions or asks to switch to a different customer.
---

# Account Scope

The user (typically an account manager) may have several customers in this workspace, each
a self-contained folder `accounts/{slug}/` (`company/`, `questions/`, `decisions/`,
`memories/`). **A session works on exactly one account.** The twins carry that account's
facts, people and memories; mixing two customers in one session would contaminate the
simulation and could leak one customer's information into another's.

In every skill and agent prompt, `{account}` means `accounts/{slug}` for the active account.

## 1. Select the account (first thing, before reading any account data)

1. Run `python3 scripts/accounts.py list`.
2. If the user's message names a customer, match it to a slug (ask if ambiguous).
   Otherwise ask which account to use, listing the slugs. Even when only one account
   exists, confirm it rather than assuming.
3. If there are no accounts, or the customer is new, offer
   `python3 scripts/accounts.py new <slug>`, then the **company-research** skill.
4. Announce the lock in plain words, e.g.:

   > This session is locked to **{Account name}** (`accounts/{slug}`). To work on a
   > different customer, start a new session (`/clear`, or exit and run `claude` again).

## 2. Stay locked

- Read and write only under `{account}/`. Never open any other `accounts/*` folder, even to
  compare, borrow a pattern or "check how we handled it elsewhere".
- If the user names a different customer, or asks to switch, **do not switch and do not
  read that account.** Tell them: "Changing customer needs a new session so the team
  doesn't mix the two accounts. Start a new session (`/clear` or restart `claude`) and
  tell me which account." Offer to finish or save any work for the current account first.
- Facts the user types about another customer are not account data: don't write them
  into this account's `company/`, memories or decisions.
- A rerun, outcome or follow-up question about the **same** account is fine.

## 3. Pass the scope on

- Every subagent prompt (specialists, guests) must state the active account explicitly:
  "Your account workspace is `accounts/{slug}`. Read and write only inside it. Your
  memory is `accounts/{slug}/memories/{role}.md` and your dossier is
  `accounts/{slug}/company/profiles/{role}/`."
- Transcripts record it: `session.account` = slug. Memos name the account in their header.
- Scripts take the slug: `python3 scripts/build_index.py {slug}`.

## Shared vs per-account

Shared and tracked (no account facts ever): `.pi/` agents and skills, `company-template/`,
`scripts/`. Per account and git-ignored: everything under `accounts/{slug}/`. A guest
specialist's prompt (`.pi/agents/{slug}.md`) is shared, so it holds the role only; the
guest's dossier and memory live inside each account.
