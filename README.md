# Leadership Agent team

This repository is using a leadership agent framework to structure executive decision-making. The leader agent synthesizes perspectives from multiple specialist agents (Moonshot, Contrarian, etc.) to make informed, balanced decisions on strategic questions.

Questions are posed to the leader in a structured format, and the leader follows a disciplined process to deliberate with the specialists, surface disagreements, and arrive at a final decision with clear rationale and next steps.

Memo's documenting key decisions are stored in the `decisions/` directory.

prime.md provides an example of how to prime the leader agent with a decision topic.

The leadership team is describes in the .pi/agents/ directory, we have also allowed for the agents to be augmented with additional background documents in the `profiles/` directory, which the agents can read and absorb as part of their deliberation process.

Each agent will have a memory file in `memories/` where you can store notes on past decisions and patterns of behavior for the specialists. This allows for the agents to learn over time and adapt their deliberation strategies based on what has worked well in the past.

## Extending the framework
- You can add more specialists with different perspectives (e.g. a CFO for financial implications, a CTO for technical feasibility) by following the pattern in `contrarian.md`.

## running the framework
- You will need [tmux](https://github.com/tmux/tmux) or [iTerm2](https://iterm2.com/) to run the agents in parallel. Each agent will have its own pane where it can read the question, deliberate with the other agents, and write its perspective. The leader agent will have a separate pane where it synthesizes the perspectives and makes the final decision.

- You will need to install pi and two extensions

```bash
npm install -g @mariozechner/pi-coding-agent
pi install npm:pi-subagents
pi install npm:pi-teams
```

- to start pi, run `pi` in iTerm2

- type `/login` to connect to your model provider.

- type `create my team named 'leadership' from the 'leadership.yaml' template.` to create the team.

- type `send a message to the leader specialist with the following content: questions/ai-factory-monetization-strategy.yaml` to send the question to the leader specialist and start the deliberation process.

- type `close down the team` to close down the team when you are done.
