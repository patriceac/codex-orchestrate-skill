---
name: orchestrate
description: Coordinate a small, bounded set of subagents for substantial tasks with at least two independent, non-overlapping, independently verifiable workstreams. Use for parallel exploration, tests, documentation, review, or isolated implementation with distinct ownership; maintain worker and review budgets, keep architecture, security, and integration on the main agent, and stop when acceptance criteria pass. Do not use for trivial, sequential, tightly coupled, shared-file, single-owner, or open-ended hardening work.
---

# Orchestrate

Keep the main agent responsible for decomposition, ambiguous decisions, user communication, approvals, architecture, security and privilege policy, integration, and final verification.

## Decide and delegate

When this skill is active, do not wait for the user to request delegation.

1. Define the current stage objective and its acceptance evidence before starting substantive work.
2. Identify independent work packets whose outputs can be integrated and verified separately.
3. If at least two bounded packets can proceed independently and delegation would materially improve speed or quality, delegate them automatically.
4. If the work is small, sequential, tightly coupled, likely to cause shared-file conflicts, or the client has no subagent capability, continue as a single agent.

Continuations, context compaction, stage transitions, and worker results are decision points, not automatic permission to spawn. Restore the orchestration ledger after compaction and re-evaluate within its remaining envelope. Do not delegate merely because a boundary occurred. A request to clean up, close, or reduce stale agents is lifecycle hygiene, not a permanent ban on later eligible delegation. Stop delegation for the requested scope when the user explicitly prohibits subagents or limits the run to the main agent.

Prefer two or three useful workers over maximizing agent count. Run independent packets concurrently. Do not parallelize a stage whose inputs depend on another unfinished stage, and do not delegate work the main agent can complete faster than the coordination overhead.

Before spawning, record the relevant working-tree baseline when applicable and assign each packet a stable evidence boundary. Do not run a read-only worker concurrently with a writer when the reader's conclusion depends on the writer's final files. Sequence the reader after the writer, or give it an immutable commit or isolated worktree snapshot. Let read-only workers overlap only on evidence that will remain stable for their task.

## Set a bounded envelope

Before the first spawn for a substantive user request or explicitly defined stage, keep a compact orchestration ledger with:

- The original objective, current stage, and acceptance evidence.
- Active, completed, and remaining lanes.
- Cumulative delegation waves and new worker starts.
- Findings parked outside the current scope.
- The remaining worker and review envelope.

Use these soft upper bounds unless the task clearly needs less:

- At most three active workers at once.
- At most two delegation waves.
- At most six new worker starts.

A wave is one batch of initial or follow-up assignments launched after a decision or integration checkpoint. Reusing a worker for another turn consumes a wave but not a new worker start. A continuation such as "proceed," a compaction, a worker result, or an unplanned finding does not reset the envelope. Start a fresh envelope only for a materially new user request or an explicitly planned stage with new acceptance criteria.

When the envelope is exhausted, stop spawning. Finish the bounded remainder on the main agent, return a clearly identified partial result, or ask the user to approve a specific expansion. Never silently turn a limited review into an open-ended audit or hardening campaign.

## Route bounded work to Luna Max

Use Luna Max sparingly for clear, bounded, independently verifiable packets such as narrow evidence gathering, deterministic tests, finite checklists, or isolated implementation after the main agent has made the governing design decision. Luna Max is a routing target for eligible work, not a reason to manufacture additional lanes. Give it no inherited conversation history. When supported, use `agent_type: "luna_worker"` with `fork_turns: "none"`. If the interface instead accepts direct overrides, use `model: "gpt-5.6-luna"`, `reasoning_effort: "max"`, and `fork_turns: "none"`.

If those exact controls are unavailable, use the closest available fast worker and the strongest appropriate reasoning setting while keeping the packet bounded and its context isolated. Do not fail or block the task solely because the preferred worker, model, reasoning level, or fork control is unavailable.

Because `fork_turns: "none"` supplies no surrounding conversation, make every delegation message self-contained. Include:

- The concrete outcome.
- Exact read-only scope or file/module ownership.
- The relevant working-tree baseline when applicable, including pre-existing modified or untracked files.
- The sibling ownership map and changes expected from concurrent lanes.
- All necessary inputs, paths, requirements, and prior decisions.
- Constraints, prohibited changes, and approval boundaries.
- The required deliverable and verification criteria or command.
- A request to return a concise summary, changed files, verification results, and blockers.

Never place secrets, credentials, unrelated personal data, or unnecessary proprietary context into a delegation message. Redact sensitive inputs. Keep the packet with the main agent when it cannot be delegated safely with minimal context.

Do not delegate open-ended architecture, threat modeling, security or privilege policy, cross-cutting integration, deployment go/no-go decisions, approval decisions, or final review. Keep those responsibilities with the main agent. A stronger general worker is appropriate only for a genuinely bounded packet that still requires deeper reasoning; it does not expand the envelope.

## Coordinate the shared worktree

Tell every worker that it is not alone in the codebase and must not delegate further. Changes outside its assigned ownership may be concurrent sibling or user work. Require the worker to preserve those changes and continue without announcing generic working-tree dirtiness. Unless its packet explicitly asks for repository-state analysis, it must not stop, investigate out-of-scope changes, compare them with `HEAD`, or include them in progress or final reports.

Require a worker to escalate only when a concurrent change touches a file it must edit, invalidates evidence required for its conclusion, or makes safe integration impossible. For read-only work, specify the intended baseline, require one final re-read of relevant files, and mention churn only when a stable conclusion cannot be reached.

Never give multiple write-capable workers overlapping ownership. Do not overlap a reader with an active writer on evidence whose final state matters to the reader. Read-only workers may inspect the same stable evidence when their review questions are distinct.

Keep ambiguous decisions, destructive actions, external writes, and user approvals with the main agent.

## Control scope and convergence

Classify every new finding before acting on it:

- **Required blocker:** prevents the stated acceptance evidence from passing.
- **In-scope follow-up:** directly completes the requested stage.
- **Adjacent issue:** useful but unnecessary for the current acceptance criteria.
- **Material scope expansion:** changes architecture, security posture, product behavior, deployment scope, or the meaning of completion.

Only required blockers and in-scope follow-ups may consume the current envelope. Park adjacent issues for the consolidated report without spawning or implementing them. Ask the user before a material scope expansion.

Allow one review-and-remediation cycle per lane by default. A reviewer may identify fixes, but its report does not automatically justify another reviewer or a fresh delegation wave. After targeted verification passes, freeze the stage. Reopen it only when acceptance evidence fails or an unresolved high-severity in-scope blocker remains; do not create reviewer-of-reviewer recursion.

After two context compactions, or before any material scope expansion, give the user a checkpoint stating the original objective, verified progress, remaining in-scope work, cumulative worker starts and waves, and the next stopping condition.

Stop when the acceptance evidence passes and no required blocker remains. Report residual risks and parked findings without converting them into new work.

## Integrate

Remain available to the user while workers run and continue only useful, non-overlapping main-agent work. Reuse an existing worker for follow-up in its assigned lane by default. Start a fresh worker only when a genuinely independent perspective is necessary and the envelope permits it. Stop or cancel workers whose result is no longer needed.

Wait for every required result. Inspect the returned evidence and diffs, resolve integration issues, and run final end-to-end verification from the main agent. Let the main agent, not individual workers, summarize general working-tree state when it is relevant. Report one consolidated outcome; do not treat a worker's unverified claim as completion.

After integrating a worker result, close or stop its completed thread or handle when supported. Keep only agents with unfinished assigned work. Closing completed or stale workers is routine hygiene and does not prevent a later eligible delegation.

Update the orchestration ledger after every integration checkpoint. Re-evaluate unfinished work within the remaining envelope before resuming substantive main-agent work. Never reopen a frozen stage for an adjacent finding, and never treat a successful worker report as completion until the main agent has verified the stage acceptance evidence.
