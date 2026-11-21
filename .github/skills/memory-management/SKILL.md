---
name: memory-management
description: Instructions for reading and writing agent memory files. Use at the start and end of every evaluation, brainstorming or scoping session.
---

# Memory Management

## Reading Memory

At the START of every evaluation, brainstorm or scope, read your designated memory file:
- For a person it is `{account}/company/profiles/{your-profile-id}/memory.md`. 
- The leader uses their own profile ID too.
- Reuse this same file as leader, voter or advisor on any team in this account.
- Synthetic archetypes have no person profile memory: use
  `{team}/memories/{archetype-id}.md` for the selected team only.
- Use only your designated file inside the selected account, never peers' memory
  files or another account. Person memory may contain entries from other teams;
  retain their team context rather than treating a local lesson as universal.
- Scan for entries relevant to the current decision topic
- Pay attention to lessons learned and past positions on similar topics
- If the file doesn't exist or is empty, proceed without prior context

## Writing Memory

At the END of every completed evaluation, brainstorm or scope, append to your memory file:
- Use the exact format below
- Be concise — capture the essence, not the full analysis
- Choose relevance tags that will help future retrieval

Format to append:

```
### {YYYY-MM-DD} - {Brief Topic Description}
**Team**: {team-slug}
**Run**: {account-relative transcript or outcome path}
**Position**: {SUPPORT / OPPOSE / CONDITIONAL / ADVICE (non-voting advisor)}
**Key insight**: {One sentence capturing your most important observation}
**Lesson learned**: {What should you remember for future similar decisions?}
**Relevance tags**: {tag1, tag2, tag3}

---
```

Use `## Past Decisions` and `## Peer Patterns` headings when creating a file.
For brainstorm, wait until the facilitator confirms the transcript completion
check passed. Use `**Position**: BRAINSTORM` and add `**Priority**: {preferred idea
IDs and reason, or ADVICE for an advisor/archetype}`. Record hypotheses and
preferences as simulation insights, not approvals, real commitments or calibration.
For scope, wait for the same completion confirmation, use `**Position**: SCOPE`
and add `**Readiness**: {recorded readiness and main unresolved blocker/condition}`.
Retain source, team/run provenance and mitigation uncertainty. A blocked plan's
memory records the blocker, not permission to proceed.
Append notable peer observations under Peer Patterns only when this run supplied
new evidence. Do not edit peers' memories, researched dossier documents or earlier entries.
The designated `memory.md` is an episodic simulation log, not researched company
knowledge. It is excluded from knowledge indexes and profile evidence checks;
memory-only appends do not require rebuilding indexes.

## Existing Team Memories

Legacy person files under `{team}/memories/` are not read during deliberation.
After selecting the account, offer an explicit import for each profile/team:

```text
python3 scripts/profiles.py migrate-memory {slug} {profile-id} --team {team-slug}
```

The helper appends original content with team provenance to the profile's memory,
preserves the source file and skips an identical repeat import. If the source
changed after import, it stops for manual reconciliation rather than duplicating
history. Do not import archetypes, peers' histories or another account's data.

## Memory Hygiene

- Never delete or modify existing entries, only append. If the file exceeds 100
  entries, flag that it needs a separate, approved summarization rather than
  deleting history during a deliberation.
- Never fabricate memories from decisions you didn't participate in
