---
name: company-research
description: Build or extend the account background under the account's company/ — financials (10-K, earnings), technology decisions and evaluations, strategy, and leadership dossiers — from public research and user-supplied files, then rebuild the indexes. Use when setting up a new account, ingesting new material, or working the gaps list.
---

# Company Research

> **Account scope:** run the **account-scope** skill first. This session works on one customer only; `{account}` = `accounts/{slug}`. Never touch another account; if the user asks to switch customer, tell them to start a new session.

Populates `{account}/company/` so the leadership twins have grounded context. You write
documents; the twins only read them. The result must be **progressively
loadable**: small, single-topic documents with good front-matter, never a
single giant dump.

## Step 0 — workspace

`{account}/company/` is git-ignored account data. If it does not exist, create it from the generic
skeleton: `python3 scripts/accounts.py new {slug}` (creates the whole account workspace). Never write account facts into `company-template/`
(it is committed to the shared template) and never `git add` anything under `{account}/company/`.

## Modes

1. **Bootstrap** — new account. Research all areas below. Ask the user first for
   the exact legal entity / ticker, the leadership roster if known, and any
   internal material they already hold.
2. **Ingest** — the user drops files or links (annual report PDF, call
   transcript, internal deck, LinkedIn export, bio). Summarise each into the
   right area; keep the original under `{account}/company/<area>/sources/` (git-ignored,
   never loaded by twins).
3. **Fill gaps** — read `{account}/company/gaps.md`, research each `[open]` item, write the
   answer into the right document, mark the line `[filled YYYY-MM-DD → path]`.
4. **Refresh** — find documents whose `as_of` is more than ~12 months old (or
   behind a newer filing) and update them.

## What to collect, by area

### `financial/`
- Latest **Form 10-K** (SEC EDGAR full-text search / company IR): segments, revenue
  and margin trends, cost structure, capex, capital allocation, risk factors,
  stated technology/investment commitments. One doc per filing year plus one
  per important topic (e.g. `segments.md`, `capital-allocation.md`).
- Last 4 **10-Q**s and **earnings calls**: guidance, what analysts push on, tone.
- **DEF 14A proxy**: how executives are paid — incentives reveal priorities.
- Put numbers in tables with the period; cite the filing URL in `source`.

### `technical/`
- Decisions **in place**: cloud providers, data platforms, ERP/core systems, AI
  vendors, security posture. Evidence: 10-K risk factors, press releases and
  partner case studies, engineering blog/talks, conference sessions, open-source
  contributions, **job postings** (stack signals), analyst coverage.
- Decisions **being evaluated**: announced pilots, RFPs, partnerships, M&A,
  stated AI/data strategy. Mark each item `status: in-place | evaluating |
  rumoured | retired` and its evidence quality.
- Who owns which technology decision, when public.

### `strategy/`
- Investor day decks, CEO letters, stated priorities and targets.
- Market position, named competitors, regulatory environment, major risks.
- Recent events: leadership changes, acquisitions, litigation, outages.

### `profiles/{role}/` — one dossier per leader
Roles: `leader` (CEO), `cfo`, `cto`, `coo`. Sources: company IR leadership
page, proxy bio, prior-employer bios, conference talks, podcasts, earnings-call
Q&A, interviews, articles, public social posts, published papers/patents.
Create `persona.md` from `{account}/company/_templates/persona.md`, plus one document per
substantial source (e.g. `bio.md`, `earnings-call-remarks.md`, `interview-2025-03.md`).
The persona is what makes the twin sound like the person — spend the effort here:
priorities in their own words, how they handle pushback, decisions they backed or
killed, what they refuse to say.
For `moonshot` and `contrarian`, write `account-angles.md` (industry bets,
untested assumptions) rather than a biography.
If the real person for a role is unknown or the seat is vacant, say so in the
role's `index.md` and describe the role generically.

## Document standard

Copy a template from `{account}/company/_templates/`. Every document needs front-matter
with at least `summary`, `tags`, `as_of`, `source`, `confidence`, `roles`.
- Keep each document to a screen or two. Split by topic rather than grow.
- **Separate fact from interpretation.** Facts get a source and period.
  Inference is labelled *(inferred)*.
- `confidence`: high = primary source (filing, transcript); medium = reputable
  secondary; low = single secondary/unverified.
- `roles`: who should load it by default (`cfo`, `cto`, `coo`, `leader`, `moonshot`, `contrarian`).

## Rules for people

- **Public professional information only.** No family, health, home address,
  private accounts, or anything obtained behind a login or paywall bypass.
- Describe behaviour that is evidenced. Do not psychoanalyse. Persona traits
  that are guesses go under "Likely blind spots / biases *(inferred)*".
- These are simulations for planning; never present generated text as a real quote.

## Never fabricate

If you cannot find or verify something, do not write it. Add a line to
`{account}/company/gaps.md` instead. If a search returns nothing for a named person, record
that rather than pad from memory. Prefer fetching the primary document over
recalling it; recalled numbers must not be written as filed figures.

## Finish every run

1. Run `python3 scripts/build_index.py {slug}` (rebuilds every `index.md` from front-matter).
2. Update the account brief in `{account}/company/index.md` (≤ ~400 words): who they are,
   business model, where they are now, roster.
3. Fill each role's `index.md` front-matter (`person:`, `title:`).
4. Run `python3 scripts/build_index.py {slug} --check` and fix every warning.
5. Report to the user: what was added, what could not be found, and the
   **questions only the user can answer** (internal knowledge, relationships,
   politics, budget cycle) — then record those in `{account}/company/gaps.md`.
