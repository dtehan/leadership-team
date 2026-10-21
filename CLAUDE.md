# Leadership Team — Digital Twin

This workspace is a digital twin of **one account's leadership team**. The user
poses a question; the team (CEO-as-Leader plus CFO, CTO, COO, Moonshot, Contrarian)
deliberates over several rounds and produces a decision memo and a readable discussion.
All output is a **simulation** built from public and user-supplied context — never
present it as what the real people said or will do.

## What to do, by intent

| The user wants to… | Use |
|---|---|
| Ask the team a question / run a scenario | `/convene` skill (reads the question, runs the deliberation) |
| Set up or enrich the account background (10-Ks, tech stack, leader dossiers) | `company-research` skill |
| Bring in a specialist who isn't on the core team (security, analytics...) | `add-specialist` skill, then list them under `guests:` in the question |
| Tell the team what the real people actually decided | `record-outcome` skill |
| See a past discussion | open `decisions/*-discussion.md` (or run `scripts/render_transcript.py` on a transcript) |

If the user just types a question with no instruction, treat it as a request to convene.

## Layout

- `company/` — everything the twins know about the account, loaded **progressively** via `index.md` files (L0 brief → L1 area index → L2 document). Areas: `financial/`, `technical/`, `strategy/`, `profiles/{leader,cfo,cto,coo,moonshot,contrarian}/`. Open knowledge gaps: `company/gaps.md`.
- `questions/` — pending questions (YAML or free text); `questions/done/` once processed.
- `decisions/` — memos, transcripts (`-transcript.json`), discussions (`-discussion.md`), outcomes (`-outcome.md`).
- `memories/{role}.md` — each twin's own episodic memory (past decisions, peer patterns).
- `.pi/agents/` — role prompts. `.pi/skills/` — shared skills (symlinked into `.claude/skills/`).
- `scripts/build_index.py` — rebuilds every `company/**/index.md` from document front-matter. Run it after adding or changing any document under `company/`.

## Rules

- `company/` is git-ignored account data (create it with `cp -R company-template company`). Never commit it, and never put account-specific facts in `company-template/` or any tracked file.
- Never bulk-read `company/`. Go through the indexes (see the profile-context skill).
- The core team is fixed; **guest specialists** (`company/profiles/{slug}/` with `type: guest`) join per conversation, advise but **do not vote**, have no cap, and are set up with `add-specialist`. To add guests to a question already run, use the rerun path in `/convene`.
- Specialists never write to `company/`; only `company-research` and `record-outcome` do.
- Do not invent facts about the account or real people. Missing → `company/gaps.md`.
- Public professional information only about real individuals.
