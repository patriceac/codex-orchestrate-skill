# PM Specification: <Project Name>

- **Project ID:** <project-id>
- **Version:** 0.1
- **Owner:** PM
- **Lifecycle State:** Draft
- **Last Updated:** <date>
- **Executive Approval:** Not Approved

This is the single living PM Spec. Start with a concise one-page product case, then expand the same document as decisions are resolved. Do not create a separate summary that can drift.

## Executive Summary

### Elevator pitch

<What is being proposed and why it matters.>

### Customer problem and audience

<Who is affected, their situation, the problem, and why it matters.>

### Business justification and impact

<Grounded customer/business impact and relevant objectives or key results. Do not include implementation details.>

## Goals and Measures

| ID | Priority | Goal | Objective measure | Baseline | Target |
| --- | --- | --- | --- | --- | --- |
| G-01 | P0 | <specific outcome> | <how success is measured> | <known baseline or Unknown> | <target or decision needed> |

## Non-Goals

| ID | Non-goal | Clarification |
| --- | --- | --- |
| NG-01 | <behavior not actively being enabled> | <not necessarily actively prevented> |

## Customer Scenarios

### SC-01 — <Scenario name>

- **Situation:** <customer context>
- **Problem:** <customer problem>
- **Intent:** <what the customer needs to accomplish>
- **Successful experience:** <observable end-to-end experience, not implementation>

## Prioritized Functional Requirements

Use `P0` for critical ship requirements, `P1` for important initial-release value that may be deferred, and `P2` for nice-to-have value unlikely to be required initially.

| ID | Priority | Requirement | Scenario | Acceptance intent | Notes |
| --- | --- | --- | --- | --- | --- |
| FR-001 | P0 | <specific product behavior> | SC-01 | <observable success> | <constraints or decision links> |

## Partners and Dependencies

| ID | Who | What is needed | When grounded | Delivery implication | Material risk |
| --- | --- | --- | --- | --- | --- |
| DEP-01 | <person/team/system> | <dependency> | <date/phase or Not yet grounded> | <impact> | <risk> |

## Detailed Feature Description

### Intended experience and behavior

<Detailed functional behavior linked to requirement IDs.>

### UX scope and fidelity decision

- **Classification:** Non-user-facing / Established-pattern user experience / Novel or materially UX-risky
- **Selected fidelity:** No visual artifact / Annotated existing pattern / Flow-state map / Wireframe / High-fidelity mockup / Interactive prototype
- **Decision rationale:** <why this is the lowest fidelity that resolves the product risk>
- **Exception and residual-risk disposition:** <rationale/evidence for non-user-facing work or an exception to a high-fidelity trigger, or None>

| High-fidelity trigger | Applies? | Evidence or rationale |
| --- | --- | --- |
| New or unfamiliar workflow | Yes/No | <decision evidence> |
| Complex, failure, or temporal states | Yes/No | <decision evidence> |
| Information hierarchy or visual comprehension | Yes/No | <decision evidence> |
| Responsive, device, or input behavior | Yes/No | <decision evidence> |
| Accessibility-sensitive interaction | Yes/No | <decision evidence> |
| Brand-critical surface | Yes/No | <decision evidence> |
| Multiple implementers/teams or material ambiguity | Yes/No | <decision evidence> |

### UX flows and states

Every user-facing change needs versioned flow-and-state evidence. Cover applicable happy, loading, empty, error, permission, disabled, success, interruption, offline/degraded, and recovery states without inventing irrelevant variants.

| Flow/state ID | Scenario and requirement IDs | Entry/trigger | Interaction and outcome | Exceptional/recovery states | Breakpoints, devices, inputs, and accessibility behavior |
| --- | --- | --- | --- | --- | --- |
| UX-001 | SC-01 / FR-001 | <entry> | <behavior/outcome> | <states> | <coverage> |

### UX artifact index

Use stable IDs and add each artifact to canonical `artifact_links`. An interactive prototype is needed only when static artifacts cannot resolve temporal behavior, motion, gesture, focus, or multi-step interaction.

| Artifact ID | Type/fidelity | Exact version | Location | Covered flows/states | Supported PM Spec version | Owner |
| --- | --- | --- | --- | --- | --- | --- |
| UXA-001 | <type> | <version> | <path/link> | <UX IDs> | <version> | UX |

### Non-UI component behavior

<Feature component diagrams or externally observable behavior where applicable.>

### Privacy requirements

<Data collection, use, exposure, retention, controls, and customer expectations.>

### Security requirements

<Permissions, trust expectations, abuse/failure considerations, and required controls.>

### Accessibility requirements

<Applicable interaction, semantic, keyboard/input, screen-reader, visual, motion, cognitive, and validation requirements.>

### World-readiness requirements

<Languages, cultures, markets, formats, geopolitical considerations, localization behavior, and expansion needs.>

## Telemetry and Reporting

| ID | Business/customer question | Measure or event | Baseline | Development need | Post-release report/pivot | Decision enabled |
| --- | --- | --- | --- | --- | --- | --- |
| TEL-01 | <question> | <signal> | <baseline or Unknown> | <diagnostic need> | <dashboard/filter> | <decision> |

## Customer Engagement and Feedback

- **Feature health, accuracy, and performance:** <signals and thresholds>
- **Alerts and incident behavior:** <trigger and response>
- **Usage/adoption goals:** <grounded goals>
- **Feedback mechanism:** <channel and collection behavior>
- **Feedback triage:** <owner and decision path>

## World Readiness and Accessibility Review

| Area | Requirement IDs | Planned validation | Owner | Open issue |
| --- | --- | --- | --- | --- |
| Accessibility | <IDs> | <validation> | UX/Test | <issue or None> |
| Localization/world readiness | <IDs> | <validation> | Content/Test | <issue or None> |

## Open Questions

Reference canonical question IDs. Do not leave resolved answers only here; update the relevant specification section.

| ID | Question | Owner | Answer needed from | Why it matters | Recommendation | Executive input? | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Q-001 | <question> | <role> | <role/person> | <impact> | <recommendation> | Yes/No | Open |

## Decisions and Significant Changes

| ID | Decision/change | Rationale | Owner | Date | Affected requirements |
| --- | --- | --- | --- | --- | --- |
| D-001 | <decision> | <why> | <owner> | <date> | <IDs> |

## Review Record

| Version | PM | Dev | Test | UX | Content | Material unresolved disagreement |
| --- | --- | --- | --- | --- | --- | --- |
| 0.1 | Authoring | Pending | Pending | Pending | Pending | <None or reference> |

## Executive Sign-off

- **Requested action:** Approve / Request Changes / Resolve Specific Question
- **Reviewed version:** <version>
- **Decision:** Pending
- **Approver:** Executive Sponsor
- **Date:** <date>
- **Notes / recorded override:** <notes or None>
