# Lifecycle and Collaboration

Use this reference when starting or resuming a Feature Crew project, preparing a review, changing an approved specification, entering execution, validating, or reporting status.

## Ownership and project voice

| Role | Owns | Must not do |
| --- | --- | --- |
| PM | Product problem, intent, requirements, priority, scenarios, measures, coordination, canonical project view, status, and final Done judgment with stakeholder agreement | Own technical implementation, ignore validation failures, or use the Executive for routine coordination |
| Dev | Feasibility, architecture, interfaces, data, security/privacy implementation, performance, reliability, observability, implementation, migration, rollout, rollback, and engineering risks | Silently redefine product behavior or begin implementation before gates pass |
| Test | Test strategy and plan, traceability, acceptance validation, negative/edge/integration/E2E/regression coverage, evidence, and Test Passed | Unilaterally declare the product Done or implement fixes unless reassigned |
| UX | Flows, interaction models, hierarchy, mockups, states, transitions, usability, accessibility implications, and experience consistency | Decide engineering architecture or silently waive product requirements |
| Content | Terminology, labels, commands, messages, empty/error/onboarding/help content, consistency, and localization readiness | Treat copy as an implementation afterthought or redesign the interaction model alone |

Routine Executive communication comes through PM after synchronization. The orchestrator integrates role outputs, keeps state, and verifies gates; it does not erase specialist ownership.

## Intake and staffing

At Intake:

1. Capture the Executive's objective without inventing scope, owners, or deadlines.
2. Initialize canonical state and artifacts.
3. Instantiate all five required roles. Store role and current agent reference when available; agent references may be replaced on resume.
4. Record known stakeholders, dependencies, constraints, artifact links, and material open questions.
5. Advance to PM Spec Drafting only when the objective is intelligible enough for discovery. Ask the Executive only if a missing decision materially changes the requested outcome and cannot be resolved by investigation.

## Internal review protocol

Each artifact version needs a review from all five roles. Every review returns:

- `verdict`: `approve` or `challenge`;
- concise finding and why it matters;
- affected requirement, section, flow, interface, test, or string;
- proposed resolution or investigation;
- materiality;
- any Executive decision genuinely required.

A challenge is not failure; it is specification work. PM coordinates the loop:

1. Author proposes the current artifact version.
2. Other roles challenge ambiguity, contradiction, feasibility, usability, language, testability, risk, or traceability.
3. The responsible role investigates.
4. Crew resolves what it reasonably can.
5. Artifact owner updates the living document and increments its version.
6. All required roles review the new version again.

Record disagreements and resolutions. An `approve` applies only to the reviewed version. The orchestrator may enter Executive Review only when every required role approves that version and no unresolved material review item remains.

## PM Spec gate

PM drafts the single living PM Spec with early input from UX and Content and feasibility/testability input from Dev and Test. Reviewers verify:

- PM: customer problem, intent, priorities, scenarios, measures, non-goals, and coherent product judgment.
- Dev: feasibility, cost/constraint implications, dependencies, security/privacy concerns, and no accidental implementation prescription.
- Test: objective, testable requirements and acceptance criteria, edge/failure coverage implications, and measurable outcomes.
- UX: complete and coherent flows, states, accessibility implications, and experience quality.
- Content: terminology and user-visible language are designed, consistent, and localization-ready.

Only explicit Executive approval of the reviewed version advances to PM Spec Approved and then Dev Design Drafting.

## Dev Design gate

Dev maps every significant design element to approved PM requirement IDs and records important alternatives. Reviewers verify:

- PM: the design implements, rather than reinterprets, approved product intent.
- Dev: feasibility, architecture, interfaces, data, threats/controls, performance, reliability, observability, compatibility, migration, rollout/rollback, and executable work packages.
- Test: adequate hooks, environments, data, fault injection, telemetry, and other testability mechanisms.
- UX and Content: technical choices preserve the approved flow, states, accessibility behavior, terminology, and messages.

If design exposes a PM Spec flaw, return to the PM gate. A material change to approved behavior requires renewed PM review and approval before design continues. Execution remains prohibited after Dev Design approval.

## Test Plan gate

Test maps tests to PM requirements, Dev Design elements, and acceptance criteria. Reviewers verify coverage of functional, negative, edge, failure, integration, E2E, regression, UX/content, accessibility, world-readiness, performance/reliability, security/privacy, telemetry, and rollout/rollback needs where applicable.

Entry criteria, exit criteria, known gaps, evidence, environments, configurations, accounts, data, devices, platforms, and versions must be explicit enough to establish confidence. Questions that expose upstream flaws return to the affected specification. Only explicit Executive approval of the reviewed Test Plan permits Execution.

## Executive review package

Each package contains:

1. The artifact and exact version.
2. Changes since the previous review, when relevant.
3. Significant decisions and rationale.
4. Remaining open questions and material disagreements.
5. Material risks.
6. Explicit Executive asks.
7. The synchronized crew recommendation.
8. One obvious action: **Approve / Request Changes / Resolve Specific Question**.

For an Executive question, state the question, why it matters, realistic alternatives, recommendation, and consequences. Record the response in canonical state. A rejection returns to drafting. An override records the bypassed gate and accepted risk.

## Execution and change control

Use outcome milestones and independently trackable work packages. Each work package must name its owner, deliverable, source specification references, dependencies, objective acceptance criteria, status, comments, and validation linkage when applicable.

During execution, role responsibilities continue:

- PM protects intent, prioritizes unblocked work, coordinates dependencies, and maintains the Executive view.
- Dev implements approved design and engineer-authored tests, reports technical facts promptly, and raises spec conflicts.
- Test prepares and performs agreed validation, preserving evidence.
- UX and Content review implementation states and strings, not merely the documents.

For a clarification, update the relevant living document and record why meaning did not change. For a material change, stop affected work, invalidate downstream approvals, update the earliest affected artifact, rerun internal review, and obtain renewed Executive approval where appropriate. Unaffected work may continue if it remains safe and consistent with approved direction.

## Validation, Done, and Completed

Validation begins only after implementation entry criteria are met. Test records evidence and either `Passed` or `Failed`; unresolved failed acceptance criteria block Done.

The normal flow is:

`Implementation Complete` → `Test Validation` → `Test Passed` → `Crew Review` → `Issues Resolved` → `Stakeholder Agreement` → `PM Declares Done`

PM's Done authority is accountability for product judgment, not unilateral power. Tests passing does not cure a customer-experience miss; PM approval does not cure a test failure. Completed requires all required milestones Done, validation Passed, issues resolved or explicitly accepted, stakeholder agreement, and formal PM closure.

## Status synchronization and cadence

Status starts in Execution. Before publishing, collect current facts from PM, Dev, Test, UX, Content, and other relevant contributors. Resolve conflicting facts or expose the material disagreement. Never report On Track over a known unresolved blocker.

Choose a heartbeat based on pace and dependency shape; do not default mechanically to daily or weekly. Publish immediately when a blocker, material schedule slip, major risk, scope or requirement change, major milestone, material test failure, dependency failure, or Executive judgment appears.

Status is a delta: material changes, open questions, current risks, next meaningful work, explicit asks, and milestones. Resolved risks leave the active list; realized risks become issues or status facts.
