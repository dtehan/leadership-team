---
name: memory-management
description: Instructions for reading and writing agent memory files. Use at the start and end of every decision deliberation.
---

# Memory Management

## Reading Memory

At the START of every decision, read your memory file:
- Your memory file is at `{account}/memories/{your-agent-name}.md` (relative to project root)
- Scan for entries relevant to the current decision topic
- Pay attention to lessons learned and past positions on similar topics
- If the file doesn't exist or is empty, proceed without prior context

## Writing Memory

At the END of every decision, append to your memory file:
- Use the exact format below
- Be concise — capture the essence, not the full analysis
- Choose relevance tags that will help future retrieval

Format to append:

```
### {YYYY-MM-DD} - {Brief Topic Description}
**Position**: {SUPPORT / OPPOSE / CONDITIONAL}
**Key insight**: {One sentence capturing your most important observation}
**Lesson learned**: {What should you remember for future similar decisions?}
**Relevance tags**: {tag1, tag2, tag3}

---
```

## Memory Hygiene

- If the memory file exceeds 200 entries, summarize the oldest 100 into a
  "Historical Summary" section at the top and remove the individual entries
- Never delete or modify existing entries, only append
- Never fabricate memories from decisions you didn't participate in
