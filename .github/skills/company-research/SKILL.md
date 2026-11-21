---
name: company-research
description: Build, reuse or incrementally refresh account background under company/ — financials, technology, strategy and leadership dossiers — from public research and supplied files. Use for new accounts, ingestion, gaps or research updates; check existing evidence first and change documents only for supported updates.
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
   internal material they already hold. Building a "company profile" uses this
   workflow: establish company context, discover/confirm the selected leadership
   roster, then invoke **person-profile** for each selected person as described
   below. Do not stop at a list of names or directories.
2. **Ingest** — the user drops files or links (annual report PDF, call
   transcript, internal deck, LinkedIn export, bio). Summarise each into the
   right area; keep the original under `{account}/company/<area>/sources/` (git-ignored,
   never loaded by twins).
3. **Fill gaps** — read `{account}/company/gaps.md`, research each `[open]` item, write the
   answer into the right document, mark the line `[filled YYYY-MM-DD → path]`.
4. **Refresh** — check scoped topics for new evidence, not a full bootstrap.
   A request to refresh company research authorizes company-document updates;
   include existing real-person dossiers only when requested or approved.
   Old `as_of` dates identify candidates to check, not permission to rewrite.

## Incremental research — every mode

Read and follow [the reuse and refresh contract](references/incremental-research.md)
before external research or ingestion. It defines the account-local source ledger,
topic freshness, source deduplication, evidence comparison and no-change outcome.
Use it for company work and pass relevant ledger entries and existing source
references to person-profile so the same evidence is not gathered again per person.
Bootstrap of an existing account fills missing coverage; it does not restart research.

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

### `profiles/{role}/` — one reusable dossier per person or generic role
`{role}` is a stable profile ID, not a fixed team assignment. Existing IDs include
`leader` (CEO), `cfo`, `cto`, `coo`; any new professional profile (including DBAs,
security leads and managers) uses the same structure. Reuse a person's dossier
across teams. Team membership, leader and vote/advisor status belong in team
definitions, not the profile's `type:`.

Use **person-profile** as the single person-building workflow in every mode,
including ingest and refresh of person material. During company bootstrap:

1. Establish the company brief and discover/confirm the leadership roster in
   scope. Reuse existing IDs, including unused template seats, rather than
   generating duplicate dossiers.
2. Invoke person-profile for each selected leader, passing the selected account,
   known identity/title, stable ID, relevant areas, collected source references
   and authorized supplied material. It owns scaffolding, person research and
   dossier synthesis using the shared standards below. Do not ask the user to
   repeat known details or delegate writing to simulation specialists.
3. Collect each result's ID/path, disposition, evidence status, sources and gaps.
   Continue independent people if one identity is unresolved, but report every
   unresolved or unfinished roster entry rather than claiming complete leadership
   coverage. Existing real-person dossiers need approval before refresh.
4. Update the company leadership summary from these results. Team assignment
   remains a separate define-team operation, not part of company/profile creation.

Person-profile does not invoke company bootstrap back. Standalone requests for
managers, DBAs or other professional roles use person-profile directly with the
same research and output contract.

For `moonshot` and `contrarian`, write `account-angles.md` (industry bets,
untested assumptions) rather than a biography.
If the real person for a role is unknown or the seat is vacant, say so in the
role's `index.md` and describe the role generically.

## Document standard

Copy a template from `{account}/company/_templates/`. Every document needs front-matter
with at least `summary`, `tags`, `as_of`, `source`, `confidence`, `roles`.
- `as_of` is the evidence's effective date/period, not today's review date.
  Keep retrieval/check dates in the research ledger; checking unchanged evidence
  does not make an old fact current.
- Keep each document to a screen or two. Split by topic rather than grow.
- **Separate fact from interpretation.** Facts get a source and period.
  Inference is labelled *(inferred)*.
- `confidence`: high = primary source (filing, transcript); medium = reputable
  secondary; low = single secondary/unverified.
- `roles`: profile IDs that should load it by default (including custom profile IDs).

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

1. Complete the ledger results, next checks and change summary required by the
   incremental contract. If only the ledger changed, skip rebuilding indexes.
   Otherwise run `python3 scripts/build_index.py {slug}` after document changes.
2. Update the account brief in `{account}/company/index.md` (≤ ~400 words) only
   when supported changes affect who they are, business model, current position
   or roster. Preserve unchanged wording.
3. Confirm each selected person's returned index metadata (`person:`, `title:`,
   inline `areas:` and `evidence_status:`); do not promote thin or pending profiles
   merely because files exist.
4. Run `python3 scripts/build_index.py {slug} --check` and fix every warning.
5. Report added/updated/reused/unchanged/blocked topics, sources reused versus
   fetched, material before/after differences and next checks. An unchanged run
   explicitly says "No material updates found" only for successfully checked
   coverage; skipped or failed checks are not evidence of no change.
   Include what could not be found and the
   **questions only the user can answer** (internal knowledge, relationships,
   politics, budget cycle) — then record those in `{account}/company/gaps.md`,
   updating an existing matching gap instead of duplicating it.
