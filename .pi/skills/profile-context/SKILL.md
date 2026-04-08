---
name: profile-context
description: Instructions for loading agent profile documents at session start. Provides stable background identity context distinct from episodic memory.
---

# Profile Context

## Loading Profile Documents

At the START of every session, before reading your memory file:

1. Run `ls profiles/{your-agent-name}/` via bash to list available documents
2. If the directory does not exist or is empty, proceed without profile context — not an error
3. For each file listed, read it: `read profiles/{your-agent-name}/{filename}`

## Using Profile Context

Profile documents are your stable background identity — who you are, your
history, and the foundations of your perspective. This differs from memory,
which records episodic decision history.

- **Absorb, don't cite**: Integrate this content into your perspective and
  reasoning. Do not reference document names or quote from them unless the
  content is directly relevant to the decision at hand
- **Background, not foreground**: This context informs how you think, not
  what you say. It shapes your instincts, not your citations
- **Read-only**: Never modify or write to files in `profiles/`
