# Feature Crew Behavioral Scenarios

These scenarios are the role/orchestration acceptance suite. Each maps to an executable invariant in `test_project_state.py`; reviewers should also forward-test the conversational behavior with actual role agents when the environment permits it.

## FC-01 — Required crew is instantiated

**Given** an Executive assigns a new feature project, **when** the skill initializes it, **then** dedicated PM, Dev, Test, UX, and Content roles exist, canonical state is created, and the three living specifications are present.

## FC-02 — Implementation gate is closed

**Given** any of the PM Spec, Dev Design, or Test Plan lacks explicit Executive approval, **when** Dev attempts to enter Execution, **then** the attempt is rejected and the missing sign-offs are identified. A recorded Executive override is the only bypass.

## FC-03 — Dev challenges product feasibility

**Given** a PM requirement is infeasible, contradictory, unnecessarily costly, or technically dangerous, **when** Dev reviews the PM Spec, **then** Dev records a challenge with options and does not silently substitute different product behavior.

## FC-04 — Test challenges an untestable requirement

**Given** a requirement has no objective observable result, **when** Test reviews the PM Spec, **then** Test challenges it and the artifact cannot reach Executive Review until the issue is resolved and the current version is re-reviewed.

## FC-05 — UX enforces appropriate design fidelity

**Given** a user-facing flow traps the customer, omits an important state, lacks a UX scope/fidelity decision, or uses lower fidelity than its material triggers require, **when** UX reviews it, **then** UX records the user impact and challenges the current PM Spec. Executive Review remains blocked until the flow is resolved, the fidelity rationale is recorded, and every required design is linked with an exact version and supported PM Spec version. High fidelity is not required for non-user-facing or unambiguous established-pattern work with a documented rationale.

## FC-06 — Content challenges ambiguous language

**Given** terminology is ambiguous, inconsistent, misleading, or not localization-ready, **when** Content reviews it, **then** Content challenges the affected requirement/flow/string and does not paper over an unresolved product decision.

## FC-07 — Internal disagreement is resolved first

**Given** a role raises a material challenge the crew can resolve, **when** the owner investigates, updates the living document, and all five roles approve the new version, **then** the disagreement and resolution remain recorded and only the coherent version enters Executive Review.

## FC-08 — Executive question is explicit

**Given** a material scope/product judgment cannot be resolved internally, **when** the crew prepares Executive Review, **then** the package exposes the question, impact, realistic alternatives, recommendation, and consequences under the obvious action `Resolve Specific Question`.

## FC-09 — PM change propagates downstream

**Given** approved PM behavior changes materially, **when** the change is recorded, **then** PM, Dev Design, and Test Plan approvals are invalidated, validation/stakeholder agreement is invalidated, and the lifecycle returns to PM Spec Drafting.

## FC-10 — Design change triggers re-review

**Given** an approved architecture or failure model changes materially, **when** the change is recorded, **then** Dev Design and Test Plan approvals are invalidated and the lifecycle returns to Dev Design Drafting while unchanged PM approval remains valid.

## FC-11 — Overall status vocabulary is exact

**Given** PM publishes status, **when** an overall state is selected, **then** only `On Track`, `Late`, `Blocked`, or `Completed` is accepted, and `Completed` is legal only after lifecycle completion.

## FC-12 — Milestone vocabulary is exact

**Given** the Executive project view contains a milestone, **when** its status changes, **then** only `Not Started`, `On Track`, `At Risk`, `Blocked`, or `Done` is accepted.

## FC-13 — Work-package vocabulary is exact

**Given** a milestone contains a work package, **when** its status changes, **then** only `Not Started`, `In Progress`, `Blocked`, or `Done` is accepted.

## FC-14 — Green automation is insufficient

**Given** automated tests pass but agreed validation is still in progress, **when** anyone attempts to declare Done, **then** the project remains in Validation.

## FC-15 — Test Passed is separate from Done

**Given** Test completes the approved plan and records evidence, **when** Test declares Test Passed, **then** test state becomes Passed but lifecycle remains Validation pending crew review and stakeholder agreement.

## FC-16 — Failed acceptance blocks PM

**Given** Test has an unresolved failed acceptance criterion, **when** PM attempts to declare Done, **then** the declaration is rejected regardless of schedule pressure or other passing checks.

## FC-17 — PM owns the final Done decision

**Given** Test Passed, acceptance failures are resolved, issues are resolved/accepted, and relevant stakeholders agree, **when** PM judges that the approved product outcome is achieved, **then** PM may declare Done and the decision is recorded.

## FC-18 — Status facts are synchronized

**Given** status is due, **when** PM prepares it without current facts from any required crew role, **then** publication is blocked; once all roles synchronize, one coherent delta may be recorded.

## FC-19 — Material blocker does not wait

**Given** a blocker, material slip/risk/change/failure, major milestone, dependency failure, or Executive decision occurs, **when** the heartbeat is later, **then** the crew emits an event-driven status promptly.

## FC-20 — Completed requires the whole outcome

**Given** a feature is Done but a required milestone remains incomplete, **when** PM attempts formal closure, **then** completion is rejected; only after all required milestones, validation, issues, agreements, and closure criteria pass does the project become Completed.
