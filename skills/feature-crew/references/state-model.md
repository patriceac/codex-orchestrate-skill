# Canonical Project State

Use this reference whenever creating, reading, or updating Feature Crew state. The machine-readable shape is [project-state.schema.json](project-state.schema.json); `scripts/project_state.py` creates and validates it.

## Storage

Use one project directory, normally `.feature-crew/<project-id>/` when the target repository has no established documentation convention:

```text
<project-directory>/
|-- project-state.json
|-- artifacts/
|   |-- pm-spec.md
|   |-- dev-design-spec.md
|   |-- test-plan.md
|   `-- project-status.md
`-- status/
```

`project-state.json` is canonical structured state. The Markdown files are living human-review artifacts referenced by the state. Status snapshots are deltas and may be stored under `status/`; add their paths to `status_history`.

Do not let role agents write state concurrently. They return evidence to the orchestrator, which applies one serialized mutation and reruns validation. Use repository version control for history when available; the helper also increments `revision`, records `updated_at`, and appends material lifecycle events.

## Core records

### Project and crew

Track project identifier, name, objective, lifecycle phase, overall status, revision, timestamps, and the five required crew roles. A crew record may hold an ephemeral agent reference, but role identity and ownership survive agent recreation.

Overall project status is one of `On Track`, `Late`, `Blocked`, or `Completed`. It is a synchronized PM judgment, not a percentage calculation. Before publishing, record a current-revision fact confirmation from all required roles.

### Artifacts and sign-off

Each of `pm_spec`, `dev_design`, and `test_plan` tracks:

- path and current version;
- owner;
- state (`Draft`, `Internal Review`, `Executive Review`, or `Approved`);
- required role reviews and their reviewed versions;
- Executive approval status, approver, date, approved version, and any carried clarification note;
- changes and invalidations.

Approval is explicit and versioned. A material upstream change clears affected approvals and reviews. An Executive override is a decision, never an invisible boolean shortcut.

### Open questions

Use stable IDs. Capture question, owner, who must answer, why it matters, recommendation, status (`Open` or `Resolved`), resolution, Executive-input flag, and related artifact or requirement. When resolved, update the relevant specification; the log is not a substitute for the source of truth.

### Decisions

Capture decision, context, alternatives when relevant, rationale, owner, date, affected specifications/work, and whether it is an Executive gate override. Do not record trivial implementation chatter.

### Risks, issues, asks, and dependencies

- A risk is hypothetical and material to schedule, scope, quality, customer experience, architecture, dependencies, or release. Resolve or retire it when no longer active.
- An issue has happened. Track owner, impact, status, resolution, and explicit acceptance where applicable.
- An ask records requester, target person/team, need, reason, and needed-by only when grounded.
- A dependency records who, what, timing when grounded, delivery implications, and risk.

Never invent owners or deadlines merely to fill fields.

### Relevant artifact links

Track stable IDs, labels, paths or URLs, artifact kind, and owner for mockups, diagrams, research, builds, dashboards, test evidence, release artifacts, and other project material that is not one of the three primary specifications. Observe the linked system's own access and authorization rules; canonical state stores the reference, not copied secrets.

### Milestones and work packages

A milestone is an outcome with name, intended outcome, owner, comments, required flag, and one exact status: `Not Started`, `On Track`, `At Risk`, `Blocked`, or `Done`.

A work package belongs to one milestone and records name, owner, deliverable, source specification references, dependencies, acceptance criteria, comments, required flag, validation links, and one exact status: `Not Started`, `In Progress`, `Blocked`, or `Done`.

### Test state and completion

Test state is `Not Started`, `In Progress`, `Passed`, or `Failed`, with evidence links, unresolved acceptance failures, and the Test role's determination. Passing an automated suite may be evidence but does not set project phase to Done.

Stakeholder agreement is recorded separately by role/stakeholder and current revision. `Done` requires Test Passed, no unresolved acceptance failures, agreement from all relevant stakeholders, and a PM declaration. `Completed` additionally requires all required milestones Done, issues resolved or explicitly accepted, and formal PM closure.

### Specification changes and status history

Every significant change records artifact, old/new version, impact (`minor` or `material`), summary, date, affected requirements, invalidated approvals, and lifecycle return point. Material PM changes invalidate PM, design, and test approvals; material design changes invalidate design and test; material test changes invalidate test approval.

Each status history entry records date, overall status, snapshot path or inline summary, changed facts, synchronization revision, whether it was heartbeat or event-driven, and the status-event IDs it reported. Material blockers, schedule slips, major risks, scope or requirement changes, major milestone completions, material test failures, dependency failures, and Executive decisions enter `status_events` immediately. A heartbeat cannot be published while one of those events is pending; publish a synchronized event-driven delta first.

## State helper

Run `python scripts/project_state.py --help` for commands. Important operations include:

- `init`: create state and living artifacts without overwriting an existing project.
- `validate`: check structure, enums, gates, review versions, and completion invariants.
- `transition`: perform a normal lifecycle transition.
- `review` / `resolve-review`: record specialist approval or challenge and its resolution.
- `approve` / `reject`: record Executive review outcomes.
- `change`: record minor or material specification changes and invalidate downstream state.
- `decision`, `question`, `risk-add`, `issue-add`, `ask-add`, `dependency-add`, and `artifact-link`: maintain the lightweight project records without editing JSON by hand.
- `set-test`, `agree`, `declare-done`, and `complete`: preserve the Test Passed/Done/Completed boundaries.

The helper is a guardrail, not a replacement for role judgment. Do not directly edit state to force an invalid transition.
