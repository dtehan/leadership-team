# User guide: a twin of a middle-management group

For account managers using the **Claude Code** version. About ten minutes to set up.
The output is a **simulation** from public and supplied information, not what the real
people said or will do.

## What you get
A room of managers (not the C-suite) who debate a question and give you a decision memo
and the full discussion. You choose who is in the room and link each person's profile.

## Before you start
- The account exists and has a brief (`accounts/<slug>/company/index.md` is filled in).
  If not, ask: *"Set up the account Acme"* and answer the questions.
- Open the folder in Claude (run `claude` from the repo root). A session works on **one customer**.

## Step 1: Tell Claude which customer
> *"Work on the Acme account."*

Claude locks the session to that account. To switch customer, start a new session.

## Step 2: Define the group
> *"Define a group called data-platform. Priya Nair, Director of Data Engineering, reports to
> the CTO and chairs it. Sam Ortiz, Head of Procurement. Lee Chen, Security Manager, as an
> advisor. It escalates to the CTO."*

Claude asks only what it is missing:

| Question | Your options |
|---|---|
| Purpose | One line: what the group decides |
| Escalates to | Who the group answers to (decisions beyond its budget become recommendations) |
| Chair | A member, or **neutral** (default) |
| Extra voices | Contrarian (default, recommended), Moonshot, or none |
| Voting | Everyone votes, or mark someone **advisor** (speaks, no vote) |

The group is saved in `accounts/<slug>/groups/data-platform/roster.md`. You can edit that file
by hand: one row per member.

## Step 3: Link each person's profile
Each member needs a profile so their twin sounds like them. For each person, do one of:

- **Nothing**: Claude creates an empty profile to fill.
- **Point to what you have**: *"Sam's profile is the CV in company/profiles/sam-bio.md"*, or give a web page.
- **Tell Claude what you know**: priorities, how they argue, who they listen to.

Then: *"Research the members' profiles."* Public professional information only. If little is
public, Claude says so and uses the role in general terms, which gives a more generic twin.

Check your work any time: *"Check the data-platform group."* It lists each member, who they
report to, and which profiles are still thin.

## Step 4: Ask a question
> *"Convene the data-platform group on: should we standardise on one ingestion tool this year?"*

Add background if you can (budget, deadline, what is known). To call only some members, say
who: *"Just Priya and Sam."* The discussion takes a few minutes and shows its progress.

## Step 5: Read the results
In `accounts/<slug>/groups/data-platform/decisions/`:

| File | Use it for |
|---|---|
| `YYYY-MM-DD-<topic>.md` | The **memo**: decision, each member's position, what it asks of each team, next steps. Read this first. |
| `…-discussion.md` | The full debate. This is where the insight is: what each person worries about and why. |

The memo says whether the group **decided** or is **recommending escalation**.

## Step 6: Teach it (optional, valuable)
When you learn what the real group decided:

> *"Record the outcome for the data-platform decision: they chose to wait until Q2 because procurement blocked it."*

Each twin is compared with reality and adjusted. The twins also remember past decisions.

## Common requests
| You say | What happens |
|---|---|
| "Add Jo Park, Finance Business Partner, to the group" | New member and profile stub |
| "Make Jo the chair" / "Remove Sam" | Roster updated; Sam's profile is kept |
| "Check the group" | Roster and profile status |
| "Rerun that question with Jo added" | A fresh debate; the memo compares it with the first |

## Tips
- The more you tell Claude about each person, the better the twin. Thin profile, generic twin.
- Keep groups to 4-8 people. Use "just these members" for narrow questions.
- Leadership and groups are separate rooms. A member's boss (for example the CTO) is only
  background for them; the CTO twin does not attend.
- The tool never invents facts. Missing facts land in `company/gaps.md`.
