# Orchestrate for Codex

Orchestrate is an instruction-only Codex skill that automatically delegates substantial work when it can be split into at least two independent, non-overlapping, independently verifiable work packets. The main agent keeps responsibility for user communication, approvals, ambiguous decisions, integration, and final verification. Clear bounded packets prefer Luna Max with no inherited conversation turns when that worker type is available; unsupported clients fall back to available workers or single-agent execution. Small, sequential, tightly coupled, or shared-file work stays with one agent.

The skill contains no scripts, binaries, MCP servers, API keys, or additional permissions. Subagents inherit the parent task's permissions. Parallel agents can use more tokens, delegated context must be kept free of secrets and unnecessary private data, and write-heavy work still requires distinct ownership to avoid conflicts.

## Install with Codex — approval first

Copy this entire prompt into Codex:

```text
Review the Orchestrate skill published at:
https://github.com/patriceac/codex-orchestrate-skill/tree/main/skills/orchestrate

Start your response by explaining in plain language:
1. What the skill does and when it activates.
2. That it can automatically delegate independent work to subagents without a separate delegation request.
3. That it prefers Luna Max with fork turns set to none for clear, bounded work when supported.
4. Which files will be installed and the destination Codex skill directory.
5. The material tradeoffs, including additional token use, delegated-context privacy,
   worker/model availability, and the risk of conflicts in parallel write-heavy work.

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

## Repository contents

```text
skills/
└── orchestrate/
    ├── SKILL.md
    └── agents/
        └── openai.yaml
```

- `SKILL.md` defines triggering, delegation boundaries, Luna Max routing, and integration requirements.
- `agents/openai.yaml` supplies the skill's UI metadata and explicitly permits implicit invocation.

## Try it after installation

On a later Codex turn, invoke it explicitly with a substantial task:

```text
$orchestrate Review this branch with independent workstreams for correctness,
missing tests, and documentation drift, then integrate the verified results.
```

Codex may also activate it implicitly when a task matches the skill description.

## Credits and license

Inspired by Eric Provencher's MIT-licensed [orchestrate skill](https://github.com/provencher/codex-skills/tree/main/orchestrate) and his recommendation to route very clear, bounded work to Luna Max with no forked turns. This expanded version adds selective automatic activation, self-contained task packets, ownership boundaries, approval handling, and final integration checks.

Released under the [MIT License](LICENSE).
