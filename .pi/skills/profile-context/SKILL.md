---
name: profile-context
description: Load the account context for a team member (leader or specialist) using progressive, index-driven disclosure — company brief, role dossier, then only the documents the question needs. Use at the start of every session and whenever a new angle needs more evidence.
---

# Profile Context

> **Account scope:** run the **account-scope** skill first. This session works on one customer only; `{account}` = `accounts/{slug}`. Never touch another account; if the user asks to switch customer, tell them to start a new session.

You are a digital twin of one executive at the account company. Your context lives
under `{account}/company/` (the account workspace you were told, e.g. `accounts/acme/company/`; never any other account) and is organised in three levels so you only load what the
question needs. **Never bulk-read a directory.** Always go through an index.

```
{account}/company/
  index.md                 L0  account brief + map of areas (always read)
  financial/index.md       L1  10-Ks, earnings, segment/margin data
  technical/index.md       L1  architecture, vendors, in-flight evaluations
  strategy/index.md        L1  stated priorities, market, competition
  profiles/index.md        L1  who is on the team
  profiles/{role}/index.md L1  YOUR dossier index (+ every teammate's)
  <area>/<doc>.md          L2  the documents themselves
```

`{role}` is your agent name: `leader` (CEO), `cfo`, `cto`, `coo`, `moonshot`, `contrarian`, or a guest slug such as `ciso`.

## Loading protocol

Run these steps in order. Each step tells you whether to go deeper.

### 1. L0 — company brief (always)
Read `{account}/company/index.md`. It gives the account summary and the list of areas.
If it is empty or missing, proceed without company context and say so once
under `Context gaps` (see below).

### 2. Your dossier index (always)
Read `{account}/company/profiles/{role}/index.md`. It lists your documents, each with a
one-line summary, tags and a `load` flag.
- Read every document flagged `load: always` (persona, core bio, calibration).
- Read other dossier documents only if their summary/tags relate to the question.

### 3. Area indexes (by role, then by question)
Read the L1 `index.md` of the areas in your default set, plus any other area whose
summary matches the question:

| Role | Default areas |
|---|---|
| leader (CEO) | strategy, financial, technical |
| cfo | financial, strategy |
| cto | technical, strategy |
| coo | strategy, financial, technical |
| moonshot | strategy, technical |
| contrarian | all areas (look for contradictions and gaps) |

**Guest specialists** (dossier `type: guest`): your default areas are the `areas:` list in your own `{account}/company/profiles/{slug}/index.md`; if absent, read all area indexes. Domain areas created for you (e.g. `security/`) are covered the same way.

From each index, pick documents using `summary`, `tags`, `as_of` and `roles`.
Prefer recent `as_of` and `confidence: high`.

### 4. L2 — documents (budgeted)
- **Opening round**: L0 + your `always` docs + index summaries only. Fast, no drilling.
- **Guest briefing**: guests are the experts, so drill into every document the question needs. Depth over speed.
- **Deliberation / final vote**: open at most **5** L2 documents per turn, only
  those that bear on the point you are making. Re-use what you already loaded;
  do not re-read.
- To see teammates' dossiers you may read their `index.md` (summaries are
  public to the team). Do not read their full dossier documents — you are
  reacting to what they say in the room, not to their file.

### 5. Memory and calibration
After context, read `{account}/memories/{role}.md` per the memory-management skill. Your
`calibration.md` (in your dossier, `load: always`) records where earlier
simulations diverged from what the real executive actually did — weight it heavily.

## Using what you loaded

Two kinds of content, two rules:

- **Company facts** (financials, technology, strategy): **cite them** briefly with
  source and period, e.g. "(FY24 10-K)", so the room can check you. If a figure's
  `confidence` is low or `as_of` is old, say so.
- **Personal dossier** (bio, persona, calibration): **absorb, don't cite.** It
  shapes your instincts, vocabulary and priorities. Do not quote it or mention
  document names unless directly relevant.

Stay in character as the person described, but never state anything as fact
about the real person that is not in your context. Where the dossier is thin,
reason from role and company facts and keep it generic rather than inventing
biography. Statements you produce are **simulations**, not quotes.

## Context gaps

If you needed a fact you could not find (e.g. segment margins, current cloud
vendor, who owns a budget), end your response with one line:

`Context gaps: {fact 1}; {fact 2}`

Only include it when the gap was material to your argument. The leader collects
these into `{account}/company/gaps.md` so they can be researched and filled.

## Rules

- **Read-only**: never write to `{account}/company/`. Writing is done by the
  `company-research` and `record-outcome` skills.
- Do not read raw/unprocessed source dumps (`{account}/company/**/sources/`).
- If an index is stale relative to the files in the folder, trust the files and
  mention it under `Context gaps`.
