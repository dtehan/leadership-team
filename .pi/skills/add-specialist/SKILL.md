---
name: add-specialist
description: Introduce a guest specialist (e.g. head of security, head of analytics) who joins specific conversations but is not part of the permanent leadership team — creates their agent, dossier and any domain context, and attaches them to a question. Use when a question needs expertise the core team lacks, or the user asks to add, bring in, or set up a specialist.
---

# Add Specialist

> **Account scope:** run the **account-scope** skill first. This session works on one customer only; `{account}` = `accounts/{slug}`. Never touch another account; if the user asks to switch customer, tell them to start a new session.

The core team (CEO/Leader, CFO, CTO, COO, Moonshot, Contrarian) is always present.
**Guest specialists** are added per conversation for expertise the core team lacks.
A guest is set up once and can then be reused on any later question.

A guest consists of:

| Piece | Location |
|---|---|
| Agent prompt | `.pi/agents/{slug}.md` (from `.pi/skills/add-specialist/guest-template.md`) |
| Dossier | `{account}/company/profiles/{slug}/index.md` + documents (same shape as core roles) |
| Domain context (optional) | `{account}/company/{domain}/` area, e.g. `{account}/company/security/` |
| Memory | `{account}/memories/{slug}.md` (created on first use) |

`{slug}` is kebab-case: `ciso`, `head-of-analytics`. It is the agent name and the folder name.

## Procedure

### 1. Check for an existing guest
List `{account}/company/profiles/*/index.md` and read the `type:` front-matter. If a guest
with that role already exists, just attach it (step 6). Don't create duplicates.

### 2. Interview the user (ask only what you can't already tell)
- **Role/title** and **slug**.
- **Who is it?** The real person's name if known (a twin of them), or "unknown/generic" —
  then the guest reasons from the role and company facts and says so.
- **Their lens**: what do they weigh that the core team doesn't? (e.g. CISO: breach
  exposure, regulatory obligation, vendor risk, blast radius.)
- **Domain context needed**: which existing `{account}/company/` areas matter, and whether a new
  area is needed (security posture, analytics estate...).
- **Scope**: *this question only* or *reusable*. Reusable is the default; the files are
  the same either way, the difference is just whether the user wants them cleaned up later.

### 3. Create the agent
Copy `.pi/skills/add-specialist/guest-template.md` to `.pi/agents/{slug}.md` and fill the
`{{...}}` placeholders: `slug`, `title`, `lens` (3–6 bullets), `personality` (2–3 sentences),
`lane` (what they stay in), `skills_extra` (leave empty). Do not change the process
sections. Pick `model: us.anthropic.claude-sonnet-4-6` if a real person is being twinned,
otherwise `us.anthropic.claude-haiku-4-5-20251001-v1:0` is acceptable.

### 4. Create the dossier
`{account}/company/profiles/{slug}/index.md`:

```markdown
---
person: {Name or "Generic {Title}"}
title: {Title}
type: guest
areas: [technical, strategy]     # L1 areas to read by default; add the new domain area if created
focus: {one line — when to bring this specialist in}
---

# {Title} dossier
```

If the real person is known, run the **company-research** skill for that one dossier:
`persona.md` from the persona template plus sources. If generic, write a short `persona.md`
describing how someone in this role at a company like this typically thinks, marked
*(generic, not a real person)*.

### 5. Create domain context (if needed)
Create `{account}/company/{domain}/index.md` (front-matter `description:`) and research it with
**company-research** (e.g. public security disclosures, breach history, certifications,
analytics/BI vendors in use, relevant 10-K risk factors). Tag documents with
`roles: [{slug}]` plus any core role who should also see them.

Then run `python3 scripts/build_index.py {slug}` and `python3 scripts/build_index.py {slug} --check`.
Anything unknown goes to `{account}/company/gaps.md`, not into documents.

### 6. Attach to the question
Add `guests: [{slug}]` to the question YAML (see decision-input), or tell the leader which
guests to invite when convening. Guests advise and do not vote; there is no limit on how many
can join. To add a guest to a question already run, use the rerun path in the convene skill. Confirm back to the user: who joined, what they know,
what they don't (gaps), and that thin context means thinner, more generic contributions.

### 7. Report
Tell the user what was created, the questions only they can answer about this specialist,
and that after the deliberation the **record-outcome** skill can calibrate the guest too.

## Rules

- Guests are subject to the same rules as everyone: public professional information only,
  no fabricated biography, output is a simulation.
- A guest never writes to `{account}/company/`; only company-research / record-outcome do.
- Don't add a guest the core team already covers. If the CTO can handle it, say so and ask.
- Retire a guest by deleting their `.pi/agents/{slug}.md` (keep the dossier and memory if
  the user may reuse them; remove both on request).
