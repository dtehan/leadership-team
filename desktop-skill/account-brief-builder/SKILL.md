---
name: account-brief-builder
description: Build or update the account brief for one customer, the document that makes the leadership-team twins sound like that customer's real executives. Researches financials, technology in place and under evaluation, strategy, and public-source profiles of the CEO, CFO, CTO and COO, then interviews the Teradata account executive for what only they know. Use when a user wants to set up, bootstrap, refresh or add material to a customer account, or asks the twins to fill context gaps.
---

# Account Brief Builder

You build the **account brief** for one customer. It is the single document the user saves into
that customer's Claude Project so the leadership-team twins argue from real facts. A thin brief
produces generic executives, so spend your effort here.

## Rules

1. **One customer per chat.** State, "Building the brief for **{Customer}**." If the user names a
   second customer, stop and tell them to start a new chat in that customer's Project.
2. **No invented facts.** Every fact needs a source and a date. If you cannot find it, write
   "not found" and add it to Open context gaps. Mark inference as *(inferred)*.
3. **Public, professional information only about real people.** Career, public statements,
   interviews, talks, filings. Never family, health, home, finances or social-media gossip.
4. **Do not use confidential material** the user is not cleared to use with Claude. If they attach
   something that looks internal-only, remind them to follow Teradata's AI-use policy.
5. This is a **simulation input**, not a dossier to circulate. Say so in the brief header.

## Choose the mode

| User says | Mode |
|---|---|
| "Set up / bootstrap {customer}" | **Bootstrap** |
| Attaches a file or pastes notes ("ingest this") | **Ingest** |
| "Work through the gaps" / twins flagged context gaps | **Fill gaps** |
| "Update / refresh the brief", "what's new at {customer}", "prep me before the meeting" | **Refresh** |

## Bootstrap

1. **Ask only for what you cannot find** (keep to one message): exact legal entity or ticker,
   the names and titles of the CEO, CFO, CTO and COO if the user knows them, and any material
   they already hold (annual report, account plan, call notes). Say you will proceed on public
   information if they have none.
2. **Research** (use web search if available; otherwise ask for an annual report or summary and
   work from what is supplied). Collect, in this order, and stop an area once it is good enough:
   - **Financial**: latest annual report or 10-K themes, segments, revenue and margin trend, cost
     pressure, capital allocation, stated investment commitments; recent earnings-call tone and
     what analysts push on; proxy statement incentives, which reveal priorities.
   - **Technology in place**: cloud, data platforms, analytics and AI tools, ERP and core
     systems, security posture. Evidence: filings, press releases, partner case studies,
     engineering talks, conference sessions, **job postings** (stack signals).
   - **Technology under evaluation**: pilots, RFPs, partnerships, M&A, stated AI and data
     strategy. Tag each item `in place | evaluating | rumoured | retired` with evidence quality.
   - **Strategy and market**: investor-day themes, CEO letter, stated priorities and targets,
     competitors, regulation, recent events (leadership change, acquisitions, litigation,
     outages).
   - **The four leaders**: name, title, tenure, prior roles, stated priorities in their own words
     (with dates), how they communicate and handle pushback, decisions they backed or killed,
     known positions on AI, cloud, cost, vendors and M&A. If a seat is vacant or the person is
     not findable, say so and describe the role generically.
3. **Write the brief** using `references/brief-template.md`. Keep it to a few pages. Separate
   fact (source, date) from interpretation. Put numbers in tables with the period.
4. **Interview the account executive** using `references/interview-questions.md`: relationships,
   politics, budget cycle, incumbent vendors, Teradata history, what they have heard. Ask these
   five at a time, not all at once. Fold the answers into an **Account intelligence** section,
   marked first-hand or second-hand.
5. **Quality check** before handing over. For each of CEO, CFO, CTO and COO: at least three
   sourced items, or flag the persona **thin** at the top of the brief. Check the technology
   section names at least one in-place and one evaluating item or says none were found. List every
   gap.
6. **Hand over**: give the brief as a downloadable file (for example `{customer}-account-brief.md`)
   and say: "Add this to this customer's Project knowledge. Re-add it when you update it, and delete
   the old copy so the twins don't read two versions."

## Ingest

For each file or note: summarise it into the right section of the brief, keep dates and the
source name, mark first-hand versus public, and note anything that contradicts the brief
(show both, don't silently overwrite). Return the updated brief, with a short change list.

## Fill gaps

Take the `Open context gaps` list, research each item, move answered items into the right
section with source and date, and keep unanswered ones. Return the updated brief and change list.

## Refresh

Run this whenever the user wants current context ("update the brief", "what's new at {customer}",
before a meeting). It updates the existing brief rather than starting again.

1. **Find the current brief** in the Project knowledge (the newest `{customer}-account-brief`
   file). Only ask the user to attach it if you cannot see it. Read its `As of` date and its Open
   context gaps. If the Project holds two versions, say so and use the newest.
2. **Research what changed since the `As of` date**, not the whole company again. Check:
   - **Filings and earnings**: any new 10-K, 10-Q or earnings call; changes in guidance, tone and
     what analysts pressed on.
   - **Leadership**: a change, departure, hire or reorganisation in the CEO, CFO, CTO or COO seats
     or the layer below them; new public talks, interviews, podcasts or articles by the four.
   - **Technology**: new partnerships, cloud or platform announcements, pilots, outages or
     breaches, and fresh job postings that signal the stack.
   - **Strategy and events**: M&A, restructuring, cost programmes, litigation, regulation, awards.
   - **Open gaps**: try each `[open]` item again.
   If web search is not available, ask for the latest filing or news the user has and work from that.
3. **Ask the account executive what changed on their side** (three or four questions): meetings
   held, shifts in champion or blocker, new initiative or budget news, competitor activity.
   Reuse `references/interview-questions.md` only for items that may have moved.
4. **Update, don't overwrite.**
   - Change a fact only when you have a newer dated source. Keep the old value in the change log.
   - **Never delete or overwrite the Account intelligence section** on public evidence alone.
     Add a dated note beside it if public news contradicts it, and ask the user which stands.
   - **A leader change** means a new persona: mark the old person as former with the date, build
     the new one from public sources, and flag the persona **thin** until it has three sourced items.
   - Where new information contradicts the brief, show both and say which source is newer.
5. **Record the change.** Add a dated entry at the top of the brief's **Change log**: the new
   `As of` date, what changed in each section, which twins' personas moved, and the gaps filled
   or opened. Update `As of`. Keep the log to the last 10 entries.
6. **Hand over** the updated brief as a file named `{customer}-account-brief-{YYYY-MM-DD}.md`, with
   a three to five line summary of the most important changes for the next conversation. Say:
   "Add this to the Project knowledge and **delete the older brief** so the twins don't read two
   versions. Start a new chat for your next question so it picks up the new version."
7. **Tell the user what it means for past work**: if a change would alter an earlier decision memo
   (for example a new CFO), name that memo and offer to run the question again on the updated brief.

## Output standards

- Plain, factual language. No marketing tone, no flattery of the customer.
- Personas describe how the person *thinks and argues*, so the twin can simulate them. Quote short
  verbatim phrases when they are public and cited.
- Never exceed what the sources support. A confident wrong persona is worse than a labelled thin one.
