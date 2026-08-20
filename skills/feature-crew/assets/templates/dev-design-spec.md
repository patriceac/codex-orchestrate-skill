# Dev Design Specification: <Project Name>

- **Project ID:** <project-id>
- **Version:** 0.1
- **Owner:** Dev
- **Lifecycle State:** Draft
- **Approved PM Spec:** <version and link>
- **Last Updated:** <date>
- **Executive Approval:** Not Approved

## Design Summary

- **Technical approach:** <summary>
- **Major decisions:** <decision IDs>
- **Constraints:** <grounded constraints>
- **Assumptions:** <assumptions requiring verification>

## Requirement Mapping

Every significant technical element must map to an approved requirement or operational need.

| PM requirement | Design component/mechanism | Interface/data/testability link | Notes |
| --- | --- | --- | --- |
| FR-001 | DES-001 | <IDs> | <reason/tradeoff> |

## Architecture

### Components, services, modules, and boundaries

<Architecture and ownership.>

### Data and control flows

<Flows, sequences, and trust boundaries.>

### State transitions

<States, transitions, concurrency, and invariants.>

## Interfaces

| ID | API/contract/protocol/event/schema | Producer/consumer | Compatibility/versioning | Failure behavior |
| --- | --- | --- | --- | --- |
| IF-001 | <interface> | <parties> | <rules> | <behavior> |

## Data

- **Models and storage:** <design>
- **Ownership and lifecycle:** <owner, creation, mutation, deletion>
- **Migration and existing state:** <behavior>
- **Retention and privacy:** <rules>
- **Integrity:** <invariants and recovery>

## Security and Privacy

| Threat/data concern | Trust boundary or exposure | Control/permission | Residual risk | Requirement |
| --- | --- | --- | --- | --- |
| <concern> | <boundary> | <control> | <risk> | <ID> |

## Performance and Scale

| Dimension | Expected scale/budget | Measurement | Degraded behavior |
| --- | --- | --- | --- |
| Latency | <budget> | <method> | <behavior> |
| Throughput/resources | <budget> | <method> | <behavior> |

## Reliability and Failure Handling

| Failure mode | Detection | Timeout/retry | Recovery/degraded mode | Data-integrity behavior |
| --- | --- | --- | --- | --- |
| <failure> | <signal> | <policy> | <behavior> | <invariant> |

## Telemetry and Observability

| PM telemetry ID | Event/metric/log | Fields and privacy | Report/alert | Diagnostic use |
| --- | --- | --- | --- | --- |
| TEL-01 | <signal> | <fields> | <consumer> | <decision/diagnosis> |

## Dependencies

| ID | Internal/external dependency | Required version/timing | Integration assumption | Risk/contingency |
| --- | --- | --- | --- | --- |
| DEP-01 | <dependency> | <grounded requirement> | <assumption> | <risk> |

## Compatibility and Migration

- **Backward compatibility:** <behavior>
- **Forward compatibility:** <behavior>
- **Versioning:** <strategy>
- **Existing customer state:** <handling>
- **Upgrade/migration:** <steps and recovery>

## Rollout and Rollback

- **Staging and environments:** <plan>
- **Feature flags/progressive rollout:** <plan>
- **Success/stop conditions:** <conditions>
- **Rollback triggers and mechanism:** <plan>
- **Recovery and data compatibility:** <plan>

## Testability

| Need | Hook/interface/telemetry/data/environment/fault mechanism | Test linkage |
| --- | --- | --- |
| <need> | <mechanism> | <planned test ID or area> |

## Implementation Plan

Use major work packages, not a low-level task dump.

| Work package | Outcome | Source requirements | Dependencies | Acceptance criteria | Validation linkage |
| --- | --- | --- | --- | --- | --- |
| WP-001 | <deliverable> | <IDs> | <IDs> | <objective criteria> | <tests> |

## Alternatives and Tradeoffs

| Decision | Alternatives | Selected approach | Rationale | Consequences |
| --- | --- | --- | --- | --- |
| <decision> | <options> | <selection> | <why> | <tradeoffs> |

## Open Questions and Risks

| ID | Type | Question/risk | Owner | Why it matters | Recommendation/mitigation | Executive input? | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Q-001 | Question | <question> | <role> | <impact> | <recommendation> | Yes/No | Open |

## Review Record

| Version | PM | Dev | Test | UX | Content | Material unresolved disagreement |
| --- | --- | --- | --- | --- | --- | --- |
| 0.1 | Pending | Authoring | Pending | Pending | Pending | <None or reference> |

## Executive Sign-off

- **Requested action:** Approve / Request Changes / Resolve Specific Question
- **Reviewed version:** <version>
- **Decision:** Pending
- **Approver:** Executive Sponsor
- **Date:** <date>
- **Notes / recorded override:** <notes or None>
