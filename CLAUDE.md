# Leadership Team — Digital Twin

This workspace holds digital twins of **customer leadership teams**, one folder per account
under `accounts/`. The user (typically an account manager) may cover several customers, but
**every session works on exactly one account**. The user poses a question; that account's team
(CEO-as-Leader plus CFO, CTO, COO, Moonshot, Contrarian) deliberates over several rounds and
produces a decision memo and a readable discussion. All output is a **simulation** built from
public and user-supplied context — never present it as what the real people said or will do.

## One session, one account (read first)

- Before anything else, run the **account-scope** skill: it picks the account, announces the
  lock, and defines `{account}` = `accounts/{slug}` for every path below.
- If the user mentions another customer or asks to switch mid-session, **do not switch and
  do not read the other account.** Tell them a change of customer needs a new session
  (`/clear` or restart `claude`) so the twins don't mix accounts, then they name the account.
- Never open, read, compare or copy from any `accounts/*` folder other than the active one. A `PreToolUse` hook (`scripts/account_guard.py`) blocks this once you run `python3 scripts/accounts.py lock {slug}`, and blocks all `accounts/*` access until you do. If it blocks a call, explain the new-session rule; don't work around it.

## What to do, by intent

| The user wants to… | Use |
|---|---|
| Pick or create the customer for this session | `account-scope` skill (`python3 scripts/accounts.py list` / `new <slug>`) |
| Ask the team a question / run a scenario | `/convene` skill (reads the question, runs the deliberation) |
| Set up or enrich the account background (10-Ks, tech stack, leader dossiers) | `company-research` skill |
| Bring in a specialist who isn't on the core team (security, analytics...) | `add-specialist` skill, then list them under `guests:` in the question |
| Tell the team what the real people actually decided | `record-outcome` skill |
| See a past discussion | open `{account}/decisions/*-discussion.md` (or run `scripts/render_transcript.py` on a transcript) |

If the user just types a question with no instruction, run account-scope, then treat it as a request to convene.

## Layout

- `accounts/{slug}/` — one self-contained, git-ignored workspace per customer:
  - `company/` — everything the twins know about the account, loaded **progressively** via `index.md` files (L0 brief → L1 area index → L2 document). Areas: `financial/`, `technical/`, `strategy/`, `profiles/{leader,cfo,cto,coo,moonshot,contrarian}/`. Open knowledge gaps: `company/gaps.md`.
  - `questions/` — pending questions (YAML or free text); `questions/done/` once processed.
  - `decisions/` — memos, transcripts (`-transcript.json`), discussions (`-discussion.md`), outcomes (`-outcome.md`).
  - `memories/{role}.md` — each twin's own episodic memory (past decisions, peer patterns) **for this account**.
- `company-template/` — generic skeleton copied into each new account (tracked; no account facts).
- `.pi/agents/` — role prompts. `.pi/skills/` — shared skills (symlinked into `.claude/skills/`).
- `scripts/accounts.py` — `list` accounts, `new <slug>` creates a workspace from the template, `lock <slug>` locks the session to one account.
- `scripts/account_guard.py` — the hook (see `.claude/settings.json`) that enforces the one-account-per-session lock.
- `scripts/build_index.py {slug}` — rebuilds every `accounts/{slug}/company/**/index.md` from document front-matter. Run it after adding or changing any document under `{account}/company/`.

## Rules

- `accounts/` is git-ignored customer data. Never commit it, and never put account-specific facts in `company-template/`, `.pi/` or any tracked file.
- Pass `{account}` to every subagent and tell it to read and write only inside it.
- Never bulk-read `{account}/company/`. Go through the indexes (see the profile-context skill).
- The core team is fixed; **guest specialists** (`{account}/company/profiles/{slug}/` with `type: guest`) join per conversation, advise but **do not vote**, have no cap, and are set up with `add-specialist`. When a question has guests, the conversation starts with the guest briefing. To add guests to a question already run, use the rerun path in `/convene`.
- Specialists never write to `{account}/company/`; only `company-research` and `record-outcome` do.
- Do not invent facts about the account or real people. Missing → `{account}/company/gaps.md`.
- Public professional information only about real individuals.
