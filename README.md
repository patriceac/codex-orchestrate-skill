# Codex Orchestration Skills

This repository publishes two complementary Codex skills:

- **Orchestrate** coordinates a small bounded set of independent subagents for parallel work.
- **Feature Crew** runs substantial software feature delivery through PM, Dev, Test, UX, and Content roles with specification-first reviews, explicit Executive gates, persistent project state, execution tracking, validation, and concise status.

## Orchestrate

Orchestrate is an instruction-only Codex skill that automatically coordinates a small, bounded set of subagents when substantial work contains at least two independent, non-overlapping, independently verifiable packets. Small, sequential, tightly coupled, shared-file, single-owner, or open-ended hardening work stays with the main agent.

The skill uses a soft default envelope of no more than three active workers, two delegation waves, and six new worker starts for a substantive request or explicitly defined stage. Continuations, context compaction, stage changes, and worker results cause a fresh decision within the remaining envelope; they do not automatically justify a spawn or reset the budget. Reaching the envelope stops additional spawning, not the task: the main agent completes the remaining in-scope work without asking for permission to continue. Once the stated acceptance evidence passes, the stage freezes and adjacent findings are reported instead of turning into recursive review and remediation.

The user's task request authorizes ordinary, reversible, in-scope delegation, edits, tests, integration, and verification. The skill does not ask for plan approval, delegation approval, permission to continue, stage-by-stage confirmation, or approval after a progress checkpoint. Checkpoints are non-blocking. The main agent keeps responsibility for user communication, genuinely required approval decisions, architecture, security and privilege policy, cross-cutting integration, deployment decisions, and final verification. Clear, narrow packets may be routed sparingly to Luna Max with no inherited conversation turns when that worker type is available. Luna Max is a routing target, not a reason to create extra work.

This runtime autonomy cannot override Codex's sandbox, connector, destructive-action, or administrator-enforced approvals. When new authority is genuinely required, the skill completes other safe work first and asks once with the concrete action and reason. The approval below is only for installing the skill on a machine; it is not a recurring approval model for later tasks.

When applicable, each worker receives a working-tree baseline and sibling ownership map. Out-of-scope changes are preserved without generic dirty-worktree commentary, while real ownership or evidence conflicts are escalated. A reader whose conclusion depends on files being actively edited is sequenced after the writer or given an immutable snapshot. Existing lanes are reused where practical, and completed or stale workers are closed without disabling later eligible delegation.

The Orchestrate skill contains no scripts, binaries, MCP servers, API keys, or additional permissions. Subagents inherit the parent task's permissions. Parallel agents can use more tokens, delegated context must be kept free of secrets and unnecessary private data, and write-heavy work still requires distinct ownership to avoid conflicts.

## Feature Crew

Feature Crew models a disciplined software product organization rather than a generic task tracker or Scrum assistant. It treats the user as Executive Sponsor, instantiates dedicated PM, Dev, Test, UX, and Content roles, and enforces this lifecycle:

```text
Intake → PM Spec review and approval → Dev Design review and approval
       → Test Plan review and approval → Execution → Validation → Done → Completed
```

Implementation is blocked until all three specifications receive explicit Executive approval, unless the Executive records a deliberate gate override. Role agents review and challenge one another through repeated propose/challenge/resolve/re-review loops before the Executive is asked to decide anything the crew can resolve internally.

The installed skill includes living specification and status templates, a documented JSON state model, and a dependency-free Python helper that atomically persists project state and enforces lifecycle, approval, change-control, status-vocabulary, Test Passed, Done, and Completed invariants. Twenty executable tests and matching behavioral scenarios cover the required operating model.

For user-facing work, UX must classify the experience risk and provide versioned flow/state evidence. High-fidelity mockups are required only when material interaction, hierarchy, responsive, accessibility, brand, state-complexity, or coordination risks justify them; conventional design-system work can use lower-fidelity evidence with a documented rationale.

Feature Crew uses actual subagents when the client supports them and schedules roles in waves when concurrency is limited. If subagents are unavailable, it requires explicitly separated role passes and preserves the same review evidence and gates in canonical state.

## Install Orchestrate with Codex — approval first

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
   reaching it stops additional spawning while the main agent continues the remaining
   in-scope work without asking me for permission.
4. That ordinary in-scope work proceeds without plan, delegation, continuation,
   stage-boundary, integration, or checkpoint approvals; checkpoints are non-blocking.
   It asks only when new authority or a platform-enforced approval is genuinely required.
5. That Luna Max with fork turns set to none is used sparingly for clear, bounded
   packets when supported, while architecture, security and privilege policy,
   cross-cutting integration, deployment decisions, and final review stay with the
   main agent.
6. How it classifies findings, limits review/remediation recursion, freezes a stage
   after acceptance evidence passes, and reports adjacent issues without silently
   expanding scope.
7. How it preserves expected shared-worktree changes without noisy status reports,
   while sequencing readers after writers when final file state matters.
8. Which files will be installed and the destination Codex skill directory.
9. The material tradeoffs, including additional token use, delegated-context
   privacy, worker/model availability, and conflict risk in parallel write-heavy work.

Then ask whether I approve proceeding with installation. Do not install, modify files,
or make any other changes until I explicitly approve.

If I approve in a later message, use $skill-installer to install exactly from the
GitHub tree URL above. Do not overwrite an existing skill silently. Validate the
installed skill, report its destination, and tell me when it will become available.
```

This provides an inspect-and-explain step before any local change. After approval, Codex's built-in skill installer can download the public folder directly from GitHub.

## Orchestrate install target

The installable skill is this public folder:

```text
https://github.com/patriceac/codex-orchestrate-skill/tree/main/skills/orchestrate
```

The built-in installer copies it to `$CODEX_HOME/skills/orchestrate`, defaulting to `~/.codex/skills/orchestrate` when `CODEX_HOME` is not set. If the destination already exists, the installer stops rather than overwriting it.

No separate configuration is required. The included metadata permits implicit invocation; explicit `$orchestrate` invocation remains available. Codex normally detects installed or updated skills automatically, and a restart is the fallback if the change does not appear.

## Feature Crew install target

The Feature Crew skill is independently installable from:

```text
https://github.com/patriceac/codex-orchestrate-skill/tree/main/skills/feature-crew
```

Install it with Codex's built-in skill installer after reviewing the files and approving the local installation. The installer copies the folder to `$CODEX_HOME/skills/feature-crew`, defaulting to `~/.codex/skills/feature-crew` when `CODEX_HOME` is not set. It requires no third-party Python packages.

## Repository contents

```text
skills/
├── orchestrate/
│   ├── SKILL.md
│   └── agents/
│       └── openai.yaml
└── feature-crew/
    ├── SKILL.md
    ├── agents/openai.yaml
    ├── assets/templates/
    ├── references/
    │   └── roles/
    ├── scripts/project_state.py
    └── tests/
```

- `skills/orchestrate/SKILL.md` defines triggering, autonomous in-scope execution, the worker and review envelope, Luna Max routing, scope classification, convergence, shared-worktree coordination, lifecycle cleanup, and main-agent integration requirements.
- `skills/feature-crew/SKILL.md` routes specification-first product delivery through the gated role workflow.
- Feature Crew's references define lifecycle collaboration, canonical state, schema, and role contracts; its assets provide living review templates; its helper and tests enforce the deterministic invariants.
- Each `agents/openai.yaml` supplies UI metadata and permits implicit invocation.

## Try it after installation

On a later Codex turn, invoke it explicitly with a substantial task:

```text
$orchestrate Review this branch using independent lanes for correctness, missing
tests, and documentation drift. Use the default bounded envelope, keep architecture,
security, and integration on the main agent, freeze the stage when its acceptance
checks pass, report adjacent findings without expanding scope, and do not pause for
routine approvals.
```

Codex may also activate it implicitly when a task matches the skill description.

For a new feature project, invoke Feature Crew explicitly:

```text
$feature-crew Build feature X. Treat me as Executive Sponsor, have the crew
resolve specification issues internally, and stop for my explicit approval at
the PM Spec, Dev Design, and Test Plan gates before implementation.
```

Feature Crew persists its canonical state in the target project workspace, normally under `.feature-crew/<project-id>/` when that repository has no established project-document convention.

## Credits and license

Inspired by Eric Provencher's MIT-licensed [orchestrate skill](https://github.com/provencher/codex-skills/tree/main/orchestrate) and his recommendation to route very clear, bounded work to Luna Max with no forked turns. This expanded version adds selective automatic activation, autonomous in-scope execution, a finite worker and review envelope, convergence and scope controls, self-contained task packets, ownership boundaries, shared-worktree coordination, lifecycle cleanup, approval handling, and final integration checks.

Released under the [MIT License](LICENSE).
