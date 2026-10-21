---
name: record-outcome
description: Close the learning loop. After the real team decides (or the outcome becomes known), compare it to what the twins predicted, record per-role calibration, and feed corrections back into their dossiers and memory. Use when the user reports what actually happened on a past decision.
---

# Record Outcome

The twins only get better if they are compared to reality. This skill takes
what the real leadership team actually decided (or how events played out) and
turns the difference into calibration the twins load next time.

## Inputs

Ask the user, for the decision in question (list `decisions/*-transcript.json`
and let them pick if unclear):

1. **What actually happened?** The real decision, or the real outcome so far.
2. **Who said what, if known?** Which executives pushed for or against, and any
   stated reasons. ("Unknown" is fine.)
3. **Source and confidence**: first-hand (in the room), second-hand (customer
   told us), or public inference (press release).
4. **Anything that surprised you** about how the real team behaved.

**Reruns:** if the decision has reruns (`rerun_of` in the later question, `-with-{guests}` slugs), record
the outcome against each run. Comparing them shows whether the guests made the simulation closer to
reality, which is the best evidence of whether a guest is worth including.

## Procedure

1. Read the decision's `-transcript.json` and memo. Extract: the leader's call,
   each role's opening stance, final position, and key reasoning.
2. For **each role**, compare predicted vs. actual and classify:
   `matched` · `partial` · `missed` · `unknown` (no real-world evidence for that person).
   Write one sentence on *why* — what did the twin overweight or miss?
3. Write `decisions/YYYY-MM-DD-{slug}-outcome.md` using this format:

   ```markdown
   # Outcome: {topic}
   **Recorded**: {date} · **Evidence**: {first-hand | second-hand | public} · **Decision date**: {…}
   ## What actually happened
   ## Twin vs. reality
   | Role | Twin predicted | Reality | Verdict | Why the gap |
   ## Lessons
   ## Context that would have changed the answer
   ```

4. **Update calibration** — for each role with a verdict other than `unknown`,
   append an entry to `company/profiles/{role}/calibration.md` (create it with
   front-matter `summary: Where past simulations diverged from the real person`,
   `tags: [calibration]`, `load: always`, `roles: [{role}]`):

   ```
   ### {YYYY-MM-DD} · {topic} · {matched|partial|missed}
   {2–3 lines: what the real person did/said, what the twin predicted, the adjustment to make}
   ```
   Keep the file ≤ ~15 entries: when it grows, merge older entries into a
   "Standing adjustments" list at the top (e.g. "More cost-sensitive than the
   twin assumes; discounts vendor claims until references are shown").
   Calibration is **stable context** (read via profile-context). It is the only
   thing outside company research that writes into `company/`.

5. **Update the leader's memory** — append to `memories/leader.md` under
   `## Peer Patterns` any change in how reliable each twin was (e.g. "CFO twin
   missed twice on risk appetite — weight with the 2026-03 calibration").
   Do not edit the specialists' own memory files; they write those themselves.

6. **Capture gaps** — if the miss was caused by absent information, add
   `[open]` lines to `company/gaps.md` and offer to run the company-research
   skill on them. If the dossier is wrong (e.g. outdated role), correct it via
   company-research, not here.

7. Run `python3 scripts/build_index.py` so the new/changed calibration docs appear in the index.

8. Summarise to the user: hit rate across roles, the biggest miss and the fix
   applied, and what to look at next time.

## Rules

- Never rewrite history: don't change transcripts or the original memo.
- Don't over-fit to one outcome. A single `missed` becomes a note, not a new
  personality. A pattern across ≥ 2–3 decisions becomes a standing adjustment.
- A real decision can differ from the twin for reasons unrelated to the person
  (politics, timing, information the twin lacked). Say which.
