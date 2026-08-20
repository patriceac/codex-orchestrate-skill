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

### UX flows, states, and artifacts

<Storyboards, mockups, screenshots, flows, controls, transitions, empty/error/degraded states, and links.>

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
