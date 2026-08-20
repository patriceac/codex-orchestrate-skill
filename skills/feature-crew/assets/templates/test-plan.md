# Test Plan: <Project Name>

- **Project ID:** <project-id>
- **Version:** 0.1
- **Owner:** Test
- **Lifecycle State:** Draft
- **Approved PM Spec:** <version and link>
- **Approved Dev Design:** <version and link>
- **Last Updated:** <date>
- **Executive Approval:** Not Approved

## Test Objectives

<Confidence the validation must establish and the product/technical risks it addresses.>

## Scope

### In scope

- <validated behavior/system/environment>

### Out of scope and rationale

- <intentional gap, why, residual uncertainty, and owner>

## Requirement Traceability

| Test ID | PM requirement/scenario | Design element | Acceptance criterion | Evidence |
| --- | --- | --- | --- | --- |
| T-001 | FR-001 / SC-01 | DES-001 | <objective criterion> | <planned evidence> |

## Environments

| Environment/configuration | Accounts/data | Devices/platforms/versions | Purpose | Owner/readiness |
| --- | --- | --- | --- | --- |
| <environment> | <needs> | <targets> | <coverage> | <owner/status> |

## Functional Testing

| Test ID | Scenario/requirement | Preconditions | Action | Expected result | Evidence |
| --- | --- | --- | --- | --- | --- |
| T-001 | <IDs> | <state> | <steps> | <observable outcome> | <artifact/log/screenshot> |

## Negative and Edge Cases

Cover invalid input, boundaries, failure paths, partial failure, interruption, unexpected state, and recovery.

| Test ID | Risk/condition | Expected safe behavior | Recovery/integrity check |
| --- | --- | --- | --- |
| T-NEG-001 | <condition> | <behavior> | <check> |

## Integration Testing

| Test ID | Components/partners | Contract/dependency | Expected interaction | Failure behavior |
| --- | --- | --- | --- | --- |
| T-INT-001 | <components> | <interface> | <result> | <result> |

## End-to-End Testing

| Test ID | Customer scenario | Start state | End state | Required evidence |
| --- | --- | --- | --- | --- |
| T-E2E-001 | SC-01 | <state> | <successful outcome> | <evidence> |

## Regression Testing

| Existing behavior at risk | Cause of risk | Coverage | Pass criterion |
| --- | --- | --- | --- |
| <behavior> | <change> | <tests> | <criterion> |

## UX and Content Validation

### UX design and implementation parity

Validate the actual interactive experience against the exact approved UX artifact versions. Cover applicable states, breakpoints, devices, input modes, and accessibility behavior; a static screenshot alone is insufficient evidence for an interactive flow.

| Test ID | Flow/state and requirement | Approved UX artifact/version | Devices, breakpoints, and inputs | Expected interaction and visual result | Evidence | UX result |
| --- | --- | --- | --- | --- | --- | --- |
| T-UX-001 | <UX/FR IDs> | <UXA ID/version> | <coverage> | <approved behavior> | <interactive evidence> | Not Run |

### Content in context

| Test ID | Flow/state/string | Approved source/version | Devices/locales | Expected copy and context | Evidence | Content result |
| --- | --- | --- | --- | --- | --- | --- |
| T-CONTENT-001 | <item> | <artifact/ID/version> | <coverage> | <approved copy/context> | <evidence> | Not Run |

## Accessibility

| Requirement | Method/tool | Assistive technology/input | Pass criterion | Evidence |
| --- | --- | --- | --- | --- |
| <ID> | <method> | <coverage> | <criterion> | <evidence> |

## World Readiness and Localization

| Language/locale/market/format risk | Coverage | Pass criterion | Evidence |
| --- | --- | --- | --- |
| <risk> | <locale/data> | <criterion> | <evidence> |

## Performance and Reliability

| Requirement/budget | Load/failure model | Measurement | Pass criterion | Evidence |
| --- | --- | --- | --- | --- |
| <ID/budget> | <model> | <measurement> | <criterion> | <evidence> |

## Security and Privacy

| Requirement/threat | Test method | Expected control/data behavior | Evidence |
| --- | --- | --- | --- |
| <ID> | <method> | <criterion> | <evidence> |

## Telemetry

| PM/Design signal ID | Trigger | Expected event/fields/privacy | Report/alert check | Evidence |
| --- | --- | --- | --- | --- |
| TEL-01 | <behavior> | <signal> | <consumer> | <evidence> |

## Rollout and Rollback

| Mechanism | Validation | Stop/rollback condition | Recovery/data check | Evidence |
| --- | --- | --- | --- | --- |
| <flag/deployment/recovery> | <method> | <condition> | <check> | <evidence> |

## Acceptance Criteria

| Criterion ID | Source requirement | Objective pass condition | Required evidence | Status |
| --- | --- | --- | --- | --- |
| AC-001 | FR-001 | <condition> | <evidence> | Not Run |

## Entry Criteria

- Approved PM Spec, Dev Design Spec, and Test Plan versions are recorded.
- The approved UX classification is recorded, and every required UX artifact ID/version is linked; an approved non-user-facing decision needs no visual artifact.
- <implementation/environment/data/build readiness criteria>

## Exit Criteria

- All required acceptance criteria pass with retained evidence.
- No unresolved required failure remains.
- Required regression, UX implementation-parity, Content, accessibility, world-readiness, performance/reliability, security/privacy, telemetry, and rollback validation is complete where applicable.
- Intentional gaps and residual risks are explicit.

## Known Gaps and Risks

| ID | Gap/risk | Impact | Owner | Disposition/acceptance needed |
| --- | --- | --- | --- | --- |
| RISK-001 | <gap> | <impact> | <owner> | <action> |

## Evidence Plan and Results

| Evidence ID | Test/criterion | Artifact/location | Build/environment identity | Result |
| --- | --- | --- | --- | --- |
| EV-001 | <IDs> | <path/link> | <identity> | Planned |

## Review Record

| Version | PM | Dev | Test | UX | Content | Material unresolved disagreement |
| --- | --- | --- | --- | --- | --- | --- |
| 0.1 | Pending | Pending | Authoring | Pending | Pending | <None or reference> |

## Executive Sign-off

- **Requested action:** Approve / Request Changes / Resolve Specific Question
- **Reviewed version:** <version>
- **Decision:** Pending
- **Approver:** Executive Sponsor
- **Date:** <date>
- **Notes / recorded override:** <notes or None>
