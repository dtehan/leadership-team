---
name: profile-context
description: Load a selected team member's account context progressively through the company brief, profile and area indexes, then relevant documents. Use when preparing a leader, participant, advisor or archetype for a deliberation.
---

# Profile Context

Run **account-scope** first; specialists use the facilitator's explicitly selected account.
`{account}` is that account only. The facilitator supplies your profile/speaker ID,
resolved dossier, team workspace and memory path. `leader` is an existing CEO
profile ID, not an instruction to replace a different selected team leader.

## Load progressively

1. **Company brief:** read `{account}/company/index.md`. If missing, report
   `Context gaps` rather than inventing facts; the facilitator must stop a new run
   when the brief is missing or still the empty template.
2. **Own dossier index:** read the supplied
   `{account}/company/profiles/{profile-id}/index.md`, then its `load: always`
   documents. Other dossier documents are selected by relevance to the question.
   The same profile serves all teams; membership, leadership and voting are
   assignments from the resolved room, not from profile `type:`.
3. **Area indexes:** use `areas:` from your dossier when present. For existing
   profiles without it, these profile-specific defaults apply:

   | Profile | Default areas |
   |---|---|
   | leader | strategy, financial, technical |
   | cfo | financial, strategy |
   | cto | technical, strategy |
   | coo | strategy, financial, technical |
   | any other person | all area indexes from the company brief |

   Also read indexes whose descriptions bear on the question. Use their summaries,
   tags, `as_of`, confidence and `roles` (profile IDs) to select documents.
4. **Document depth:** opening reactions use the brief, own always-loaded docs and
   index summaries. Advisor briefings may load all documents material to their
   domain. Deliberation and final positions open at most five relevant L2 documents
   per turn. Reuse loaded context; never bulk-read company directories or raw
   `sources/` dumps.
5. **Peers:** only attendees' dossier indexes may be read, not their full personal
   documents. An explicitly supplied reporting relationship permits reading the
   manager's index as background; it does not put that manager in the room.
6. **Memory:** follow **memory-management** with your resolved profile memory path,
   shared across teams in this account. Never load a peer's `memory.md` as evidence.
   Profile calibration is stable, account-wide context and should inform your view.

## Archetypes

Contrarian and Moonshot are synthetic perspectives, not people. Read the brief,
then relevant area indexes (Contrarian checks all for contradictions). If their
account-local archetype index exists, progressively load relevant account-angle
documents, not a fictional biography. Archetype memory alone stays team-local.

## Use and limits

Cite company facts briefly with source and period, flagging old or low-confidence
evidence. Absorb personal context without quoting it as public fact. Thin profiles
mean generic reasoning from responsibilities and company evidence, never invented
biography, private traits or claims about what a real person will do.

Keep researched company context read-only; your designated profile `memory.md`
is the sole dossier write allowed during deliberation. Only company-research,
person-profile and record-outcome change other dossier documents; the facilitator
may append collected gaps to the gaps log. End a response
with `Context gaps: {material fact}; {material fact}` when needed. If an index is
stale, report it and use only already located relevant documents. All contributions
are simulations, not quotes.
