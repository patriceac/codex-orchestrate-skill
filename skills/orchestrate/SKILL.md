---
name: orchestrate
description: Coordinate subagents automatically for substantial tasks that split into at least two independent, non-overlapping, independently verifiable workstreams. Use for parallel codebase exploration, reviews, test analysis, documentation checks, or isolated implementation with distinct ownership when delegation would materially improve speed or quality. Do not use for trivial, sequential, tightly coupled, shared-file, or single-owner work.
---

# Orchestrate

Keep the main agent responsible for decomposition, ambiguous decisions, user communication, approvals, integration, and final verification.

## Decide and delegate

When this skill is active, do not wait for the user to request delegation.

1. Identify independent work packets before starting substantive work.
2. If at least two bounded packets can proceed independently and delegation would materially improve speed or quality, delegate them automatically.
3. If the work is small, sequential, tightly coupled, likely to cause shared-file conflicts, or the client has no subagent capability, continue as a single agent.

Prefer two or three useful workers over maximizing agent count. Run independent packets concurrently. Do not parallelize a stage whose inputs depend on another unfinished stage.

## Route bounded work to Luna Max

Delegate clear, bounded, independently verifiable packets to Luna Max with no inherited conversation history. When supported, use `agent_type: "luna_worker"` with `fork_turns: "none"`. If the interface instead accepts direct overrides, use `model: "gpt-5.6-luna"`, `reasoning_effort: "max"`, and `fork_turns: "none"`.

If those exact controls are unavailable, use the closest available fast worker and the strongest appropriate reasoning setting while keeping the packet bounded and its context isolated. Do not fail or block the task solely because the preferred worker, model, reasoning level, or fork control is unavailable.

Because `fork_turns: "none"` supplies no surrounding conversation, make every delegation message self-contained. Include:

- The concrete outcome.
- Exact read-only scope or file/module ownership.
- All necessary inputs, paths, requirements, and prior decisions.
- Constraints, prohibited changes, and approval boundaries.
- The required deliverable and verification criteria or command.
- A request to return a concise summary, changed files, verification results, and blockers.

Never place secrets, credentials, unrelated personal data, or unnecessary proprietary context into a delegation message. Redact sensitive inputs. Keep the packet with the main agent when it cannot be delegated safely with minimal context.

Tell every worker that it is not alone in the codebase, must preserve others' changes, must not revert unrelated work, and must not delegate further. Never give multiple write-capable workers overlapping ownership. Read-only workers may inspect overlapping evidence when their review questions are distinct.

Keep ambiguous architecture, cross-cutting changes, destructive actions, external writes, and user approvals with the main agent. Use stronger general agents only when a packet cannot be made clear and bounded without losing essential judgment.

## Integrate

Remain available to the user while workers run and continue only useful, non-overlapping main-agent work. Reuse an existing worker for follow-up in its assigned lane when appropriate.

Wait for every required result. Inspect the returned evidence and diffs, resolve integration issues, and run final end-to-end verification from the main agent. Report one consolidated outcome; do not treat a worker's unverified claim as completion.
