# Porting Leadership Teams to Claude Code or Pi

## Purpose and support status

This guide explains how the current Copilot setup could be adapted to **Claude
Code** or the **Pi coding agent**. It is a proposed migration approach, not an
installation guide for an existing integration. The repository currently supports
Copilot only; neither alternative has been implemented or live-validated here.

Using a Claude model inside Copilot is different from switching to Claude Code:
the former retains Copilot's instructions, tools and specialist execution.
Claude Desktop is also outside this guide's scope.

All team output must remain a simulation based on public and supplied context,
never statements or predictions by real people.

## Summary

Most of this project is portable: Markdown workflows, ordinary Python helpers,
and account-local documents. The main platform dependency is how the facilitator
launches independent simulated participants and collects their responses.

**Claude Code is the closer fit:** it already supports project instructions,
skills and custom subagents. **Pi needs more integration work:** it supports
instructions and skills, but does not ship native subagents. A Pi port needs a
reviewed extension/package or a custom participant runner.

| Component | Current Copilot setup | Claude Code adaptation | Pi adaptation |
|---|---|---|---|
| Project instructions | `.github/copilot-instructions.md` | `CLAUDE.md` entry point | `AGENTS.md` entry point |
| Skills | `.github/skills/` | Expose through `.claude/skills/` | Expose through `.pi/skills/` or configured resource paths |
| Specialist definition | `.github/agents/leadership-specialist.agent.md` | Custom agent under `.claude/agents/` | Extension/package or SDK-backed runner |
| Specialist dispatch | Copilot `task`, named agent and parallel wrapper | Claude's `Agent` mechanism and response collection | Implement fresh seat sessions, dispatch and collection |
| Account data and outputs | Account-local files and transcript JSON | Preserve | Preserve |
| Python helpers | Standard library, Python 3.8+ | Reuse | Reuse |
| Distribution | Copilot-specific ZIP allowlist | Add adapter assets and setup guidance | Add adapter assets, runner dependencies and setup guidance |

Paths for the alternative platforms above are proposed additions, not files
already present in this repository.

## What should stay unchanged

- Account layout, reusable person profiles, named team definitions and memories.
- Explicit account and team selection; no silent membership changes.
- One profile-backed leader, participant vote flags and separate synthetic roles.
- Progressive context loading through company and profile indexes.
- Question metadata, frozen-room snapshots and workflow-specific transcript fields.
- Verbatim discussion records, decision memos and scope/brainstorm outputs.
- Research evidence, gaps, calibration and preservation of historical runs.

Reuse the existing [account helper](../scripts/accounts.py),
[team resolver](../scripts/teams.py), [profile helper](../scripts/profiles.py),
[index builder](../scripts/build_index.py) and
[transcript renderer and validator](../scripts/render_transcript.py).
Do not migrate customer documents merely because the agent platform changes.

The workflows remain the source of truth:
[evaluate](../.github/skills/evaluate/SKILL.md),
[brainstorm](../.github/skills/brainstorm/SKILL.md) and
[scope](../.github/skills/scope/SKILL.md). A port should adapt their execution
mechanics, not replace their rules with a simpler generic meeting prompt.

## Recommended architecture: shared content, small adapters

Keep one authoritative set of workflow and role content. Add platform-specific
entry points and dispatch instructions rather than maintaining three independently
edited workflow copies.

Initially, the existing Copilot content can remain authoritative. An adapter can
reference shared resources or generate discoverable platform-specific files.
If generating copies, use a repeatable process and verify they stay synchronized.
Review relative links and script paths: copying a skill to a different location
can break references even when its prose is unchanged.

If all three platforms become supported, consider separating neutral workflow
content from platform-specific dispatch guidance. That refactor is not required
just to investigate a port.

The central adapter contract is:

1. Receive explicit account, team, speaker identity, assignment, designated memory
   path, round prompt and full labelled meeting history.
2. Start a fresh specialist context for that call with the shared role,
   [profile-context](../.github/skills/profile-context/SKILL.md) and
   [memory-management](../.github/skills/memory-management/SKILL.md) instructions.
3. Use the facilitator's selected model consistently across seats.
4. Return the complete response associated with the dispatched speaker.
5. Report failure or cancellation explicitly; never fabricate a response or
   substitute an unscoped agent.

The facilitator remains responsible for saving every response before advancing
to the next phase, synthesizing results and running completion checks.

## Porting to Claude Code

### 1. Adapt project instructions and skill discovery

Provide a `CLAUDE.md` entry point carrying the routing and invariants from the
[Copilot instructions](../.github/copilot-instructions.md). Replace references
to Copilot-only commands, discovery and execution with Claude-specific guidance.

Expose skills through `.claude/skills/`, preserving their `SKILL.md` structure,
descriptions and supporting references. Verify discovery and invocation in a
fresh session. Do not assume Claude will load `.github/skills/` automatically.

### 2. Define the scoped specialist

Adapt the [specialist](../.github/agents/leadership-specialist.agent.md) into
`.claude/agents/leadership-specialist.md`. Translate the frontmatter into fields
supported by the installed Claude Code version; do not blindly copy Copilot
metadata such as `user-invocable`.

Keep the specialist's assignment-based identity, no-delegation rule, progressive
reads, own-memory restriction and simulation disclaimer. Configure model
inheritance deliberately, for example with Claude's supported `model: inherit`
setting, and verify user or environment overrides do not change seat models.
Do not enable an alternative automatic agent-memory store in place of the
repository's designated person memory.

### 3. Translate dispatch and result handling

Replace Copilot's `task` parameters and parallel wrapper in the meeting workflows
with Claude's supported custom-agent invocation and collection mechanism.
Use fresh calls carrying the full history each round, as the current workflows
require; do not depend on a resumed subagent remembering previous turns.

Pass account and assignment context explicitly even if Claude loads project
instructions into the subagent. Those instructions do not contain the selected
room or the seat's designated memory path.

Require the specialist to return its complete discussion response, not a task
summary. Verify that the selected execution mechanism exposes that full response
to the facilitator for verbatim recording.

Native agent teams are not required for this design. The existing facilitator
and fresh specialist-call pattern is the smaller adaptation.

## Porting to Pi

### 1. Adapt instructions and skills

Provide `AGENTS.md` with the same routing and invariants. Pi supports project
skills under `.pi/skills/`, additional configured skill paths, and the Agent
Skills format used by these workflows. Review discovery, relative references,
project trust and reload behavior for the installed version.

Where supported, configuring discovery of the shared skill directory can avoid
copies. It does not make Copilot-specific dispatch instructions executable.

### 2. Supply participant execution

Pi does not ship native subagents, so choose either:

- A reviewed subagent extension/package that satisfies the adapter contract.
- A custom extension or runner using Pi's SDK, RPC or subprocess interfaces.

An extension is not equivalent merely because it advertises "subagents." Verify
that it supports fresh isolated contexts, model consistency, explicit seat
instructions, complete response extraction, failures and parallel collection.

A custom runner would need to:

- Create a fresh seat session for each round call, without unrelated customer
  history or a reused session's hidden context.
- Supply the role instructions and full round history.
- Provide the required file tools and handle designated-memory writes.
- Collect full final responses and associate them with speaker IDs.
- Wait for independent batches, propagate errors and stop further phases when
  required responses are missing.
- Keep runner session files separate from the canonical meeting transcript.

Keep the Python helpers as they are. Pi-side orchestration may introduce a
JavaScript/TypeScript runtime or package dependency, depending on the integration
chosen; that dependency belongs to the adapter, not the team data format.

## Behavior and data-handling requirements

Do not replace independent seats with one conversation asked to "play everyone."
That is a different simulation design: all roles share a context rather than
making separate specialist calls. Separate contexts still receive the intended
shared meeting history; they are not a guarantee of independent reasoning.

Neither a Markdown instruction nor a separate context is a filesystem security
boundary. The current repository uses explicit scope as workflow guidance, not
automatic account enforcement. A port must not claim stronger isolation without
implementing and testing it. Tool permissions and path restrictions should be
reviewed for the chosen platform, including shell access.

Account files are gitignored, not encrypted or automatically local-only. Changing
platform can change which provider receives context and where sessions are stored.
Review organizational authorization, retention, telemetry and sharing settings;
never package account data or publish customer-containing agent sessions.

Keep workflow-specific timing rules, especially memory writes. Brainstorm and
scope defer seat memory writes until explicit confirmation of a passing completion
check. Do not let a new runner write those memories automatically on every return.

Only record costs actually measured by the runtime; leave unavailable values
`null`. Do not turn reported usage into a claimed hard spending limit.

## Implementation sequence and acceptance checks

1. **Create adapter discovery and setup.** Test instructions, skills and specialist
   availability in a fresh session using only fictional disposable data.
2. **Test one seat.** Confirm identity, model, progressive reads, supplied history,
   full response capture and designated memory behavior.
3. **Port evaluate end to end.** Include an advisor, voting participants and
   multiple rounds; preserve the leader's separate position and participant-only
   tally.
4. **Port brainstorm and scope.** Preserve idea provenance and complete rankings,
   then blocker provenance, final reviews and readiness semantics.
5. **Exercise failure and history cases.** Test a missing response, cancellation,
   invalid team, absent team selection, attendee subsets, unavailable specialist,
   reruns, outcome recording and a fresh session for a different account.
6. **Update distribution.** Adjust the explicit allowlist and setup text in the
   [packager](../scripts/package.py) and its tests. Do not broaden packaging to
   traverse arbitrary directories or customer workspaces.

Run the existing Python tests during implementation:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

For each generated transcript, run the existing completion gate before publishing
a completed result:

```text
python3 scripts/render_transcript.py <transcript-path> --check
```

Then render the discussion and confirm its content matches the collected seat
responses. On an incomplete run, preserve the partial transcript, leave the input
pending and follow that workflow's publication and memory rules.

Python tests and structural checks do not certify model behavior, argument quality
or data isolation. Live fictional runs must verify those separately before a port
is described as supported. They consume the selected provider's usage or credits.

## Platform references

The approach was informed by the following official documentation, consulted on
2026-11-20. Recheck APIs, discovery paths and configuration against the version
selected for implementation.

- [Claude Code skills](https://code.claude.com/docs/en/skills)
- [Claude Code custom subagents](https://code.claude.com/docs/en/sub-agents)
- [Pi overview and supported integration interfaces](https://github.com/earendil-works/pi)
- [Pi skills](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/skills.md)
- [Pi configuration and context files](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/configuration.md)

This guide was prepared with AI assistance. Platform behavior and proposed adapter
choices require human review and implementation-time verification.
