# Reuse and incremental refresh contract

Company-research and person-profile use this contract in every mode. Success
means reusing reviewed evidence, gathering only missing or due evidence, and
changing knowledge only for a supported difference. A refresh is not a rewrite.
These are agent workflow rules, not an automatic network cache or truth checker.

## 1. Inventory before research

Within the selected account, read the company brief and relevant area/profile
indexes, then only documents and saved sources needed for the requested scope.
Identify existing claims, effective periods, citations and unresolved gaps before
searching. Reuse stable topic paths and profile IDs; do not make date-stamped
copies of the same living topic or person. Separate filing periods remain
separate historical documents.

Maintain `{account}/company/sources/research-ledger.md`, creating it lazily during
authorized research. `sources/` is excluded from progressive indexes. It is
gitignored account evidence, never a shared template or tracked research file.
Use one entry per topic/source pair, shared across company and person research:

| Field | Required content |
|---|---|
| Topic | Stable topic key, e.g. `financial/annual-filing` or `profiles/cto/current-role` |
| Source key | Canonical URL, filing accession/version, or supplied-file SHA-256 |
| Evidence | Publication/effective date or period; saved original path if available |
| Used by | Account-relative document paths and the claims/sections supported |
| Last attempt | ISO date, result: `changed`, `unchanged`, `not-found`, `blocked` or `error`, and reason |
| Last successful check | ISO date of actual successful comparison; absent if never checked |
| Next check | ISO date and reason, or event trigger for immutable historical material |
| Comparison | Material difference or no-change basis; ETag/Last-Modified/hash if available |

For unsuccessful searches, use the public discovery page/query as the source key
and record its scope. Do not copy confidential search terms into public queries.
Keep the last successful check/comparison when recording a later failed attempt.

If no ledger exists, seed entries from scoped existing citations and saved
evidence. Unknown check dates stay unknown; do not claim sources were checked
today or fetch every old source just to populate the ledger.

## 2. Decide what needs checking

- **Reuse** sufficient existing evidence when its next check is not due and no
  change signal exists. Repeated build/ingest requests do not force a refresh.
- **Check** missing evidence, due topics, a user-requested recheck, or a signal
  such as a new filing, role change, revised source or new supplied material.
  A refresh request checks the selected scope even before its next-check date;
  it does not bypass person-profile approval or identity/history decisions.
- Defaults after a successful check: 30 days for current roles, recent events,
  active evaluations and open discovery gaps; 90 days for other living topics.
  Use an earlier known filing/event date or the user's requested cadence.
- Verified historical filings and dated talks need no scheduled refetch.
  Reuse them unless a correction/version signal appears. Separately check the
  living "latest filing/current role" discovery topic for newer evidence.
- Failed/blocked checks do not advance successful-check dates or certify
  freshness. State the failure and a concrete retry date or unblock condition.
  A not-found result records the searched scope and retries in 30 days unless
  a new signal or explicit request warrants an earlier check.

Assign one owner to fetch a shared source during a run. Reuse its saved original
and comparison across affected topics/people instead of fetching it per profile.
If there is no saved original or sufficient excerpt, retrieve it when needed;
do not pretend a citation alone proves a new claim.

## 3. Deduplicate and compare evidence

Normalize source identity conservatively: remove fragments and known tracking
parameters from URLs, but preserve semantic query parameters, document IDs,
versions and periods. A matching URL does not imply matching content.
For supplied files compare content hashes, not filenames. Reuse an existing
original/summary when the same evidence arrives via a different filename or URL.

When supported, use conditional requests with stored ETag/Last-Modified.
An HTTP 304 or identical content hash permits source reuse; neither proves
that a newer filing or a separate source does not exist. Otherwise compare
the relevant claims, periods and provenance against saved evidence. Navigation,
formatting, advertisements or wording alone are not material research updates.
Do not treat tool/network failure, inaccessible content or an empty extraction
as an unchanged source. Do not bypass authentication or access restrictions.

## 4. Apply the smallest supported delta

- Write only new facts, corrections, changed status/period, relevant new evidence,
  or changes to confidence/interpretation justified by evidence. An independent
  corroborating source may update citations/confidence without rewriting prose.
- Patch affected claims/sections in their existing documents. Preserve unchanged
  prose, original citations, historical facts and stable IDs. Capture a replaced
  fact's effective period and superseding evidence rather than silently erasing
  history. Record conflicting evidence explicitly; absence is not a retraction.
- Preserve `as_of` unless the evidence's effective date/period changes. Do not
  bump it to the retrieval date, rewrite persona text, change evidence status,
  or rewrite the brief just to show activity.
- An unchanged check updates only the ledger's check/result fields; the profile
  and knowledge documents remain byte-for-byte unchanged. If all checks are
  skipped as not due, report reuse rather than claiming fresh verification.
- Update matching gaps in place. Rebuild indexes only after knowledge/metadata
  changes; ledger-only updates need no rebuild. Run applicable read-only
  structural checks, but disclose that these do not verify research truth.

## 5. Return an auditable result

Report topics added, updated, reused (not rechecked), checked-unchanged or
blocked; source fetches versus reuse; changed document paths with material
before/after differences and citations; unresolved gaps; and next checks.
Link the account-local ledger. If nothing material changed, say so without
claiming unsearched or failed coverage was verified. Company callers pass this
result onward rather than researching the same topics again.
