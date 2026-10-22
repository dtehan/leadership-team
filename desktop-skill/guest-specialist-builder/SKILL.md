---
name: guest-specialist-builder
description: Define a guest specialist (for example head of security, head of analytics, head of data governance, procurement) who joins specific leadership-team conversations for one customer. Interviews the user, gathers the domain context for that customer, and produces a reusable guest card to save in the customer's Project. Use when a question needs expertise the core CEO/CFO/CTO/COO/Moonshot/Contrarian team lacks, or the user asks to add, bring in or set up a specialist or guest.
---

# Guest Specialist Builder

A **guest specialist** is an expert who joins particular conversations of the customer's
leadership-team twin. They **advise but do not vote**, there is no limit on how many join, and
they are reusable. This skill produces the **guest card**: the one document that lets the
`leadership-team-twin` skill run them well.

## Rules

1. **One customer per chat.** Name the customer first. A guest card belongs to one customer
   because its domain context is that customer's. For another customer, start a new chat in that
   customer's Project.
2. **Real person or generic.** If the user names a real person, use public, professional
   information only (no family or private life) and mark inference *(inferred)*. If generic, the
   guest reasons as a seasoned person in that role at this company, and you **never invent a
   biography**.
3. **No invented facts** about the customer's domain. Source and date every fact; unknown goes
   in Open context gaps.
4. Do not use confidential material the user is not cleared to use with Claude.

## Procedure

1. **Check what exists.** Look in the Project knowledge for the account brief and any existing
   guest cards. If this guest already exists, offer to update the card instead of creating a
   second. If there is no account brief, say the guest will lack customer context and offer to
   run `account-brief-builder` first (continue if the user declines).
2. **Interview** (one message, five questions, skip anything the user already said):
   1. **Title and the question it serves**: what decision are they here to inform?
   2. **Real or generic**: if real, their name and any public profile to use.
   3. **Their lens**: what do they weigh that the CFO, CTO and COO don't?
   4. **Their lane**: what do they speak to, and what do they leave to others?
   5. **Context they need**: documents, standards or facts about this customer in their domain.
3. **Gather domain context** for this customer, using the account brief, attached files and
   (if web search is on) public sources. Typical content by guest:
   - *Security*: public security posture, breaches or incidents, certifications, applicable
     regulation, cloud and data-residency commitments, vendor-risk stance.
   - *Analytics / data*: analytics platforms in place, data strategy statements, AI programmes,
     org structure for data, notable data-driven initiatives.
   - *Governance / compliance*: regulators, audit findings, data-privacy obligations, policies.
   - *Procurement / finance ops*: sourcing approach, vendor consolidation efforts, contract norms.
   Keep it to what changes the debate. Cite every fact with source and period.
4. **Draft the guest card** from `references/guest-card-template.md`. Show it to the user and ask
   for corrections to the lens, lane and any fact they know to be wrong.
5. **Hand over**: give the card as a downloadable file (for example `guest-{slug}.md`) and say:
   "Save it to your Desktop, upload it to this customer's Project knowledge and start a new chat. To use them, say, *Convene the team on {question},
   with the {title} attached.*"

## How the guest behaves in a conversation (so the card is written for it)

- Speaks **first**, at length (typically 4 to 8 paragraphs): their read of the situation, facts the
  team may lack, the options and which they favour, the risks and what must be true, what the team
  should debate.
- Has **no vote**. Gives 3 to 5 sentences of final advice at the end: what the decision must
  account for, the one safeguard they insist on, the risk if ignored.
- The CEO's decision must respond to the guest's advice, and the memo records how.

## Output standards

- Plain, direct language. A guest card is working material, not a profile to circulate.
- Lens and lane must be specific enough that two different guests would argue differently.
- Never let a generic guest drift into claims about a named real person.
