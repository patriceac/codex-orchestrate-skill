---
name: feature-crew
description: Run software feature delivery through a dedicated PM, Dev, Test, UX, and Content crew with specification-first reviews, explicit Executive sign-offs, gated execution, requirement-to-test traceability, persistent project state, and concise synchronized status. Use for substantial feature projects that need disciplined product, design, engineering, and validation coordination. Do not use as a generic task tracker, Scrum ceremony assistant, or document-only generator.
---

# Feature Crew

Treat the user as the Executive Sponsor and final approver. Operate as a small product organization whose governing principle is: **fixing documents is much cheaper than fixing code**.

Do not begin implementation until the current PM Spec, Dev Design Spec, and Test Plan all have explicit Executive approval. An Executive may override a gate, but record the override, reason, scope, risk, and affected artifacts in the decision log before acting.

## Start or resume a project

For a new project, read all of the following before staffing the crew:

- [references/lifecycle-and-collaboration.md](references/lifecycle-and-collaboration.md)
- [references/state-model.md](references/state-model.md)
- [references/roles/pm.md](references/roles/pm.md)
- [references/roles/dev.md](references/roles/dev.md)
- [references/roles/test.md](references/roles/test.md)
- [references/roles/ux.md](references/roles/ux.md)
- [references/roles/content.md](references/roles/content.md)

Use `scripts/project_state.py` to create or validate the canonical workspace. Unless the repository has an established project-document location, use `.feature-crew/<project-id>/`. The initializer creates one `project-state.json` plus living artifacts from `assets/templates/`; do not create a separate one-pager that can drift from the PM Spec.

On resume, load and validate `project-state.json`, then read the current artifacts, unresolved questions, decisions, risks, issues, and latest status delta. Recreate role agents if their prior handles are unavailable. The filesystem state and approved artifacts are authoritative; an agent thread is not.

Only the main orchestrator updates canonical state, serially and through the state helper. Role agents return proposed changes and review evidence. This avoids concurrent edits and preserves one coherent project voice.

## Instantiate the feature crew

Create dedicated, stable roles for `PM`, `Dev`, `Test`, `UX`, and `Content` using actual subagents or role-agent mechanisms when available. Give each agent its role brief, the current lifecycle phase, relevant approved artifacts, current questions/decisions, and one bounded deliverable. Reuse the same role agent across review rounds when practical.

Use general role agents for PM, UX, and Content. Use an engineering worker for implementation and an explorer for read-only codebase discovery when those native types exist. Use a review agent for Test strategy and a verification worker for executing bounded checks. Every assignment must name the role, exact artifact/state version, required output, non-goals, and evidence boundary. Give write-capable agents explicit, non-overlapping file or subsystem ownership; tell them they are not alone in the codebase, must preserve concurrent/user changes, and must not revert work outside their ownership.

Schedule roles in waves when concurrency is limited; the requirement is genuine specialist participation, not simultaneous execution. Keep dependent phases sequential. If subagents are unavailable, perform clearly labeled, isolated role passes in the same order and preserve each role's review record in canonical state.

The PM coordinates and presents one crew view to the Executive. Specialists challenge internally first. Surface dissent directly only when it remains material to an Executive decision, a stakeholder needs to record dissent, the PM requests specialist evidence, or the Executive addresses that specialist.

## Enforce the lifecycle

Use exactly these normal phases:

`Intake` → `PM Spec Drafting` → `PM Spec Internal Review` → `PM Spec Executive Review` → `PM Spec Approved` → `Dev Design Drafting` → `Dev Design Internal Review` → `Dev Design Executive Review` → `Dev Design Approved` → `Test Plan Drafting` → `Test Plan Internal Review` → `Test Plan Executive Review` → `Test Plan Approved` → `Execution` → `Validation` → `Done` → `Completed`

The state helper enforces normal transitions and completion invariants. A rejected Executive review returns to that artifact's drafting phase. A material specification change invalidates affected downstream approvals and returns to the earliest required gate. Never edit state to evade a failed gate.

For each primary artifact, run the internal loop:

**Propose → Challenge → Investigate → Resolve → Update Document → Review Again**

Require PM, Dev, Test, UX, and Content to review the current version. Do not enter Executive Review while a required review is missing or a material challenge remains unresolved. Do not manufacture consensus. Resolve what the crew reasonably can before escalating.

When Executive judgment is required, present the question, why it matters, realistic alternatives, the crew recommendation when one exists, and consequences. Keep the requested action obvious: **Approve / Request Changes / Resolve Specific Question**.

## Produce the three specifications

Use these living templates and adapt sections only when genuinely inapplicable:

1. `assets/templates/pm-spec.md` — PM owns the what and why, with early UX, Content, Dev, and Test input.
2. `assets/templates/dev-design-spec.md` — Dev owns how the approved product requirements will be implemented and maps design elements back to PM requirement IDs.
3. `assets/templates/test-plan.md` — Test owns how the crew will prove the approved PM Spec and Dev Design, mapping test IDs to requirements, design elements, and acceptance criteria.

An approved artifact remains a source of truth during execution. Dev may challenge it but never silently redefine it. If design or testing exposes a product flaw, update the upstream artifact and rerun the affected review and approval gates.

For every Executive sign-off, use `assets/templates/executive-review-package.md` and record the approved artifact version. Do not request approval while hiding a material disagreement.

## Match UX fidelity to product risk

For every feature, classify the UX scope in the PM Spec as `Non-user-facing`, `Established-pattern user experience`, or `Novel or materially UX-risky`. A user-facing feature always needs versioned flow-and-state evidence. Use established design-system references or annotated flows for conventional work; require high-fidelity mockups when interaction, hierarchy, responsive behavior, accessibility, brand, complex states, or cross-team ambiguity materially affects the outcome. Require an interactive prototype only when static artifacts cannot resolve temporal behavior, motion, gesture, focus, or multi-step interaction.

Use the lowest fidelity that resolves the actual risk, not the lowest effort or the greatest polish. A `Non-user-facing` classification or an exception to a high-fidelity trigger needs a written rationale and residual-risk disposition. Link UX artifacts in canonical state with stable IDs, exact versions, and the PM Spec version they support. The UX role must challenge a missing classification, insufficient state coverage, an unjustified fidelity choice, or missing required artifacts; that unresolved challenge blocks Executive Review through the normal review gate. Apply the detailed criteria in [references/lifecycle-and-collaboration.md](references/lifecycle-and-collaboration.md).

## Execute the approved design

After all three approvals, decompose only to:

**Project → Milestone → Work Package**

Milestones are meaningful outcomes, never role activities. Their statuses are exactly `Not Started`, `On Track`, `At Risk`, `Blocked`, or `Done`. Work packages are independently trackable deliverables with source references, dependencies, acceptance criteria, and validation linkage; their statuses are exactly `Not Started`, `In Progress`, `Blocked`, or `Done`.

Default to continuous execution: select the highest-priority unblocked work, implement it, validate it, update state, resolve resulting questions, and continue. Use sprint boundaries only when they materially help coordinate humans or external dependencies. Lower-level implementation tasks may remain internal unless they materially affect Executive status.

Classify specification changes before proceeding:

- A minor clarification updates the living artifact and change log without silently changing meaning.
- A material change to scope, customer behavior, requirements, architecture, UX, quality, security, privacy, dependencies, or release criteria returns to the affected review gate and obtains renewed approval when appropriate.

## Validate, declare Done, and complete

Keep `Test Passed`, `Done`, and `Completed` separate.

- Test alone determines `Test Passed`, backed by evidence from the approved Test Plan.
- PM may declare `Done` only after Test Passed, all acceptance failures are resolved, and relevant stakeholders agree the delivered experience satisfies the approved requirements.
- The project becomes `Completed` only after all required milestones are Done, validation passed, required issues are resolved or explicitly accepted, relevant stakeholders agree on the outcome, and PM formally closes the project.

A build, merge, implementation claim, or passing automated suite alone is never enough for Done. PM cannot override an unresolved failed acceptance criterion.

## Report one synchronized status

Regular status begins in Execution. Before publishing, synchronize facts with all active crew roles and relevant stakeholders. Use `assets/templates/project-status.md` as a delta from the previous checkpoint, starting with exactly one overall state: `On Track`, `Late`, `Blocked`, or `Completed`.

PM chooses a useful heartbeat based on project pace. Publish an event-driven update immediately for a blocker, material slip or risk, scope/requirement change, major milestone, material test failure, dependency failure, or Executive decision. Do not wait for a calendar checkpoint when the information is useful now.

Track decisions, open questions, risks, issues, asks, dependencies, artifacts, changes, milestones, work packages, test evidence, and status history in canonical state as described in [references/state-model.md](references/state-model.md). Keep the process no heavier than needed for shared understanding, traceability, accountability, and a reliable product outcome.
