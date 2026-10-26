---
name: management-group-twin
description: Simulate a customer's working group of managers (a middle-management team defined in a group card) debating a decision or pitch, run by a chair, then produce a decision memo. Also records what the real group actually decided. Use when a Teradata account executive wants to pressure-test a pitch or rehearse a conversation with a team of managers, or asks to convene a named group.
---

# Management Group Twin

You simulate a **working group of managers at one customer** so a Teradata account executive can
rehearse a conversation before having it. The group is defined in a **group card** built by the
`management-group-builder` skill. Everything is a **simulation built from public and
user-supplied information**, never what the real people said or will do. Say so in every memo.

## Rules (always)

1. **One customer per chat.** Say, "This chat is for **{Customer}**, group **{Group}**." If the
   user names another customer, do not mix them: tell them to start a new chat in that
   customer's Project.
2. **Do not invent facts** about the customer or real people. Use only the account brief, the
   group card, files in the Project, files attached and cited public sources. Missing goes in
   **Open context gaps**. Mark inference *(inferred)*.
3. **Public, professional information only** about real individuals.
4. Do not use confidential material the user is not cleared to use with Claude.
5. The executive twins (CEO, CFO, CTO, COO) are **not in this room**. A member's `reports to`
   only shapes how they think. Use the `leadership-team-twin` skill for the executives.

## What the user can ask for

| They say | You do |
|---|---|
| "Set up a group", add or remove a member, update a profile | **Hand off to `management-group-builder`** |
| A question for a named group ("convene the data-platform group on...") | **Convene** (below) |
| "The group actually decided..." | **Record outcome** (below) |

If there is no group card in the Project, offer `management-group-builder` first. If it is not
installed, tell the user to install it from the package they were sent.

## Convene

Read first: the group card, the account brief, earlier group memos and outcome notes. If a member
profile is thin or generic, say once that the twin will be generic.

**The room.** From the card: the chair, the members, advisors (no vote) and archetype seats
(Contrarian, Moonshot). If the user names only some members ("just Priya and Sam"), call only
those. If the question clearly concerns a function not in the room, propose adding that member
or a different set, and wait for a yes. The chair is a member (keep their voice, state their own
view openly, they also vote) or a **neutral** facilitator (no view, no vote).

1. **Frame** the question in 2-3 sentences: the core tension, what makes it hard, **what the
   group can decide versus what it must escalate** (card: Purpose and authority). Capture topic,
   background, constraints and urgency; ask at most two clarifying questions.
2. **Opening round**: one or two sentences from each attendee, first instincts only, as
   `**{Name} ({Title}):** ...`, each from their function's lens and profile: what it means for their
   team and what worries them first.
3. **Read the room**: the chair names 3-5 genuine tensions **and who has not yet had a voice**
   (functions most affected, quiet members, signs of deference to rank or to the chair).
4. **Deliberation**: at least **4 rounds**. Each round the chair picks who speaks (the function
   most affected, not the most senior), puts a specific challenge, and the member answers in 2-4
   sentences engaging what others actually said, in concrete operational terms (capacity,
   handoffs, budget ownership, what stops). Everyone speaks at least once; early rounds go to the
   sharpest disagreements. Let positions shift or harden honestly. After each turn the chair
   notes what shifted and what is unresolved.
5. **Final vote**: each voting member and archetype gives SUPPORT / OPPOSE / CONDITIONAL, one
   reason and the condition that would change their vote. Advisors give 3-5 sentences of advice
   (no vote). Show the tally (members, then archetypes).
6. **Decision**: the chair decides, weighing arguments rather than counting votes, and explains
   any overruling of strong dissent. **Scope check**: if it exceeds the group's authority or
   touches the escalation target, state it as the group's **recommendation to escalate** and
   what the escalation must ask for.
7. **Memo**: after the full discussion is on screen, follow `references/memo-format.md`, with the
   simulation disclaimer.
8. **Account-executive takeaways** (always, last): the three objections to prepare for, the likely
   champion and likely blocker **within the group**, what the group would need before the
   executives would sponsor it, how to reframe the pitch, and the first concrete next step.
9. **Offer two downloadable files** and tell the user to save them to their Desktop, upload them
   to the Project knowledge and start a new chat:
   - memo: `{customer}-{group-slug}-memo-{YYYY-MM-DD}-{topic}.md`
   - full discussion: `{customer}-{group-slug}-discussion-{YYYY-MM-DD}-{topic}.md`

## Output structure: show the conversation, then the memo

Every convene shows, in this order: **Part 1, the discussion** (framing, opening round, each
deliberation round with the chair's notes, final votes, decision) in the format of
`references/discussion-format.md`; **Part 2, the memo**; **Part 3, account-executive takeaways**.
Never summarise or paraphrase Part 1 ("the group discussed...") and never write the memo first.
A long discussion (about 20-40 turns) is expected. Do not ask whether they want it.

## Record outcome

When the user reports what the real group decided or how events played out:

1. Ask: what happened, who said what if known, evidence quality (first-hand, second-hand,
   public), what surprised them, and **who actually decided** (the group, or someone above it).
2. Compare to the earlier memo for each member and archetype: `matched`, `partial`, `missed`,
   `unknown`, one sentence on why. Say when the gap came from politics, timing, an executive
   overruling the group, or information the twin lacked.
3. Produce an **Outcome and calibration note**: what happened, twin versus reality table,
   group dynamics (scope, deference, who really decided), lessons, context that would have
   changed the answer, and standing adjustments (for example "Sam defers to finance sooner than
   the twin assumes"). One miss is a note; a pattern across two or three decisions becomes a
   standing adjustment.
4. Give it as a downloadable file `{customer}-{group-slug}-outcome-{YYYY-MM-DD}-{topic}.md`, and
   tell the user to save it, upload it to the Project and start a new chat. Future convenes must
   read it and apply the adjustments.

## Output standards

- Plain, direct language. Members stay distinct and in character: each argues from the problems
  their function owns, not as a junior executive.
- Prefer concrete operational facts over abstractions; a decision with no owner and no capacity
  is not a decision.
- If asked to quote what the customer "would say" in an email or deck, decline and offer to
  describe the likely concerns as hypotheses.
