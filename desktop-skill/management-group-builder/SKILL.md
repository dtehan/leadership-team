---
name: management-group-builder
description: Define a working group of managers (for example a middle-management team, data platform leads, regional directors, a change board) for one customer - who is in the group, who chairs, who it escalates to - and build a profile for each member. Produces one reusable group card to save in the customer's Project. Use when the user wants a twin of a team of managers rather than the executive team, or asks to add, remove or update a member of such a group.
---

# Management Group Builder

A **group** is a team of managers at one customer who decide things together. This skill
defines who is in it and links each member to a profile, and produces the **group card**: the
one document that lets the `management-group-twin` skill run them. It sits alongside the
executive `leadership-team-twin`; neither replaces the other.

## Rules

1. **One customer per chat.** Say, "Building a group for **{Customer}**." A group card belongs to
   one customer because the members and context are theirs. For another customer, start a new
   chat in that customer's Project.
2. **No invented facts.** Use only the account brief, Project files, files the user attaches, what
   the user tells you, and (if web search is on) cited public sources. Unknown goes in Open
   context gaps. Never invent a biography.
3. **Public, professional information only** about real people (role, career, talks, published
   work). No family or private life. Mark inference *(inferred)*. Middle managers are often
   not very public; when little is found, say so and describe the **role** generically, marked
   *(generic, not a real person)*.
4. Do not use confidential material the user is not cleared to use with Claude. If they attach
   something that looks internal-only, remind them to follow Teradata's AI-use policy.
5. The card is simulation input, not a profile to circulate. Say so in its header.

## Procedure

1. **Check what exists.** Look in the Project knowledge for the account brief and any existing
   group cards. If the group exists, offer to update it (add or remove a member, change chair,
   deepen a profile) instead of creating another. If there is no account brief, say the members
   will lack company context and offer `account-brief-builder` first; continue if declined.
2. **Interview** in one message, skipping anything already said:
   1. **Group name and purpose**: what is it for, and what can it decide on its own?
   2. **Escalation**: who does it report decisions to, so decisions beyond its budget or
      authority become recommendations?
   3. **Members**: for each, name, title, function and who they report to (a named executive
      or another member). Real person (twin) or generic seat?
   4. **Chair**: a member (their twin runs the meeting), or **neutral** (default, a facilitator
      with no function and no vote).
   5. **Extra voices and voting**: include a Contrarian (default, recommended for peer groups:
      guards against deference and groupthink)? A Moonshot? Anyone who is an **advisor** (speaks,
      no vote)?
3. **Build each member's profile** (the link between a person and the roster). Take whatever the
   user gives you: a pasted bio or CV, a LinkedIn export, a web page (LinkedIn pages usually
   cannot be fetched; ask them to paste the public text), notes about how the person works. If
   web search is on, search for public information. For each member write a **member profile**
   (template below), citing each source with its date. Show the user how thin each profile is.
4. **Draft the group card** from `references/group-card-template.md`. Show it and ask for
   corrections to the roster, chair, escalation and any fact they know to be wrong.
5. **Hand over**: give the card as a downloadable file named `{customer}-group-{group-slug}.md`
   and say: "Save it to your Desktop, upload it to this customer's Project knowledge (delete the
   older version if you updated one) and start a new chat. To use it, say, *Convene the
   {group name} group on {question}.*"

## Member profile (one per member, inside the card)

Name, title, tenure, function and what they own (team size, budget if known); who they report
to; **career arc**; **stated priorities** (own words and dates where public); **how they
communicate and handle pushback**; **decision tendencies**; **known positions**; **likely blind
spots** *(inferred)*; **account-executive input** (what only the user knows, dated); and the
**sources** list. Keep to what is evidenced. State the source type of each: *public*,
*user-supplied*, *inferred*.

## Linking profiles across groups

A person in two groups at the same customer has one profile. Reuse it: put the full profile in
one card and, in the other, give the roster row and "profile: see {group card}, member {slug}".
Do not copy a profile that may drift.

## Updating a group

- **Add or remove a member**: revise the roster and add or drop the profile. Keep removed
  members' profiles in a "Former members" appendix if the user may bring them back.
- **Change the chair or escalation**: update the header.
- A real-life change of manager in a seat: add the new member, move the old one to Former members.

## Output standards

- Plain, direct language. Distinct people: two members must argue differently because their
  functions and incentives differ, so make each profile specific.
- If a profile is thin, say what would improve it (a bio, a talk, a user note).
