# Leadership Team

This repository implements a leadership agent framework that structures executive decision-making. A leader agent synthesizes perspectives from multiple specialist agents (Moonshot, Contrarian) to make informed, balanced decisions on strategic questions.

Questions are posed to the leader in a structured format. The leader follows a disciplined process: deliberate with specialists, surface disagreements, and arrive at a final decision with clear rationale and next steps. Decision memos are stored in `decisions/`.

Agent prompts are in `.pi/agents/`. Each agent can be augmented with background documents in `profiles/`, which they read and absorb as part of their deliberation. Each agent maintains a memory file in `memories/` — tracking past decisions and peer patterns — allowing the team to learn and adapt over time.

---

## Two Implementations

This repo contains the same deliberation framework implemented on two different orchestration systems. Both share the same agent prompts, profiles, questions, decisions, and memories.

| | Pi Framework | Claude Teams |
|---|---|---|
| **Orchestrator** | Pi CLI (separate install) | Claude Code (no extra install) |
| **Leader config** | `.pi/agents/leader.md` | `claude-teams/CLAUDE.md` |
| **Specialist config** | `.pi/agents/` | Reused from `.pi/agents/` |
| **Team config** | `leadership.yaml` | Not needed — agents spawned programmatically |
| **Specialist invocation** | Pi `message` routing between panes | Claude Code `Agent` tool calls |
| **Parallel broadcast** | Pi native | Two background `Agent` calls in one response |
| **Shared data** | `profiles/`, `questions/`, `decisions/`, `memories/` | Same directories |

---

## Running with Pi

Pi runs agents as persistent processes in separate terminal panes, routing messages between them via its own orchestration layer.

**Requirements:** [tmux](https://github.com/tmux/tmux) or [iTerm2](https://iterm2.com/), Node.js

**Install:**
```bash
npm install -g @mariozechner/pi-coding-agent
pi install npm:pi-subagents
pi install npm:pi-teams
```

**Run from the repo root:**
1. Start Pi: `pi` in iTerm2
2. Connect to your model provider: `/login`
3. Create the team: `create my team named 'leadership' from the 'leadership.yaml' template.`
4. Submit a question: `send a message to the leader specialist with the following content: questions/ai-factory-monetization-strategy.yaml`
5. When done: `close down the team`

---

## Running with Claude Teams

Claude Teams uses Claude Code's native `Agent` tool to spawn and communicate with specialists. Claude Code itself acts as the leader — no separate orchestration process, no extra installs.

**Requirements:** [Claude Code](https://claude.ai/code)

**Run from the `claude-teams/` subdirectory:**
```bash
cd claude-teams
claude
```

Claude Code loads `CLAUDE.md` automatically, which contains the leader prompt. Submit a question by referencing any file from `questions/`:

```
Process the question in ../questions/ai-factory-monetization-strategy.yaml
```

Claude Code will orchestrate the full deliberation — spawning Moonshot and Contrarian as sub-agents, collecting their responses, managing deliberation rounds, and producing the decision memo — all within a single session.

---

## Shared Resources

Both implementations read from and write to the same directories at the repo root:

| Directory | Purpose |
|---|---|
| `profiles/` | Agent background identity documents (read-only) |
| `questions/` | Pending decision topics (YAML format) |
| `questions/done/` | Processed questions (moved here after each run) |
| `decisions/` | Decision memos and full deliberation transcripts |
| `memories/` | Per-agent memory files (past decisions and peer patterns) |

---

## Extending the Framework

Add more specialists (e.g. CFO, CTO) by following the pattern in `.pi/agents/contrarian.md`:
- Create a new agent file in `.pi/agents/`
- Add a background document in `profiles/{name}/`
- Reference the new specialist in both `.pi/agents/leader.md` and `claude-teams/CLAUDE.md`
- For Pi: add the agent to `leadership.yaml`
