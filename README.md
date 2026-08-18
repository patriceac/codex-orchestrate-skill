# Orchestrate for Codex

Orchestrate is an instruction-only Codex skill that automatically coordinates a small, bounded set of subagents when substantial work contains at least two independent, non-overlapping, independently verifiable packets. Small, sequential, tightly coupled, shared-file, single-owner, or open-ended hardening work stays with the main agent.

The skill uses a soft default envelope of no more than three active workers, two delegation waves, and six new worker starts for a substantive request or explicitly defined stage. Continuations, context compaction, stage changes, and worker results cause a fresh decision within the remaining envelope; they do not automatically justify a spawn or reset the budget. Once the stated acceptance evidence passes, the stage freezes and adjacent findings are reported instead of turning into recursive review and remediation.

The main agent keeps responsibility for user communication, approvals, architecture, security and privilege policy, cross-cutting integration, deployment decisions, and final verification. Clear, narrow packets may be routed sparingly to Luna Max with no inherited conversation turns when that worker type is available. Luna Max is a routing target, not a reason to create extra work.

When applicable, each worker receives a working-tree baseline and sibling ownership map. Out-of-scope changes are preserved without generic dirty-worktree commentary, while real ownership or evidence conflicts are escalated. A reader whose conclusion depends on files being actively edited is sequenced after the writer or given an immutable snapshot. Existing lanes are reused where practical, and completed or stale workers are closed without disabling later eligible delegation.

The skill contains no scripts, binaries, MCP servers, API keys, or additional permissions. Subagents inherit the parent task's permissions. Parallel agents can use more tokens, delegated context must be kept free of secrets and unnecessary private data, and write-heavy work still requires distinct ownership to avoid conflicts.

## Install with Codex — approval first

Copy this entire prompt into Codex:

```text
Review the Orchestrate skill published at:
https://github.com/patriceac/codex-orchestrate-skill/tree/main/skills/orchestrate

Start your response by explaining in plain language:
1. What the skill does, when it activates, and when work stays single-agent.
2. That it can automatically delegate independent work without a separate delegation
   request, but a continuation, compaction, stage change, or worker result is only a
   decision point and does not automatically cause another spawn.
3. Its soft default envelope: at most three active workers, two delegation waves,
   and six new worker starts for a substantive request or explicitly defined stage;
   exhausting it requires main-agent completion, a partial result, or my approval
   for a specific expansion.
4. That Luna Max with fork turns set to none is used sparingly for clear, bounded
   packets when supported, while architecture, security and privilege policy,
   cross-cutting integration, deployment decisions, and final review stay with the
   main agent.
5. How it classifies findings, limits review/remediation recursion, freezes a stage
   after acceptance evidence passes, and reports adjacent issues without silently
   expanding scope.
6. How it preserves expected shared-worktree changes without noisy status reports,
   while sequencing readers after writers when final file state matters.
7. Which files will be installed and the destination Codex skill directory.
8. The material tradeoffs, including additional token use, delegated-context
   privacy, worker/model availability, and conflict risk in parallel write-heavy work.

Then ask whether I approve proceeding with installation. Do not install, modify files,
or make any other changes until I explicitly approve.

If I approve in a later message, use $skill-installer to install exactly from the
GitHub tree URL above. Do not overwrite an existing skill silently. Validate the
installed skill, report its destination, and tell me when it will become available.
```

This provides an inspect-and-explain step before any local change. After approval, Codex's built-in skill installer can download the public folder directly from GitHub.

## Install target

The installable skill is this public folder:

```text
https://github.com/patriceac/codex-orchestrate-skill/tree/main/skills/orchestrate
```

The built-in installer copies it to `$CODEX_HOME/skills/orchestrate`, defaulting to `~/.codex/skills/orchestrate` when `CODEX_HOME` is not set. If the destination already exists, the installer stops rather than overwriting it.

No separate configuration is required. The included metadata permits implicit invocation; explicit `$orchestrate` invocation remains available. Codex normally detects installed or updated skills automatically, and a restart is the fallback if the change does not appear.

## Repository contents

```text
skills/
└── orchestrate/
    ├── SKILL.md
    └── agents/
        └── openai.yaml
```

- `SKILL.md` defines triggering, the worker and review envelope, Luna Max routing, scope classification, convergence, shared-worktree coordination, lifecycle cleanup, and main-agent integration requirements.
- `agents/openai.yaml` supplies the skill's UI metadata and explicitly permits implicit invocation.

## Try it after installation

On a later Codex turn, invoke it explicitly with a substantial task:

```text
$orchestrate Review this branch using independent lanes for correctness, missing
tests, and documentation drift. Use the default bounded envelope, keep architecture,
security, and integration on the main agent, freeze the stage when its acceptance
checks pass, and report adjacent findings without expanding scope.
```

Codex may also activate it implicitly when a task matches the skill description.

## Credits and license

Inspired by Eric Provencher's MIT-licensed [orchestrate skill](https://github.com/provencher/codex-skills/tree/main/orchestrate) and his recommendation to route very clear, bounded work to Luna Max with no forked turns. This expanded version adds selective automatic activation, a finite worker and review envelope, convergence and scope controls, self-contained task packets, ownership boundaries, shared-worktree coordination, lifecycle cleanup, approval handling, and final integration checks.

Released under the [MIT License](LICENSE).
