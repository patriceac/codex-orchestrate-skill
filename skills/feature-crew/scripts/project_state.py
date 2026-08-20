#!/usr/bin/env python3
"""Create and enforce canonical Feature Crew project state.

The module intentionally uses only the Python standard library so an installed
skill can run without adding dependencies. Role agents propose changes; the
orchestrating agent applies serialized mutations through this helper.
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Sequence


SCHEMA_VERSION = 1
ROLES = ("PM", "Dev", "Test", "UX", "Content")
PHASES = (
    "Intake",
    "PM Spec Drafting",
    "PM Spec Internal Review",
    "PM Spec Executive Review",
    "PM Spec Approved",
    "Dev Design Drafting",
    "Dev Design Internal Review",
    "Dev Design Executive Review",
    "Dev Design Approved",
    "Test Plan Drafting",
    "Test Plan Internal Review",
    "Test Plan Executive Review",
    "Test Plan Approved",
    "Execution",
    "Validation",
    "Done",
    "Completed",
)
PHASE_INDEX = {phase: index for index, phase in enumerate(PHASES)}
OVERALL_STATUSES = ("On Track", "Late", "Blocked", "Completed")
MILESTONE_STATUSES = ("Not Started", "On Track", "At Risk", "Blocked", "Done")
WORK_PACKAGE_STATUSES = ("Not Started", "In Progress", "Blocked", "Done")
TEST_STATES = ("Not Started", "In Progress", "Passed", "Failed")
ARTIFACT_KEYS = ("pm_spec", "dev_design", "test_plan")
UX_ARTIFACT_KINDS = (
    "ux-flow",
    "ux-wireframe",
    "ux-high-fidelity-mockup",
    "ux-prototype",
)
ARTIFACT_CONFIG = {
    "pm_spec": {
        "owner": "PM",
        "draft": "PM Spec Drafting",
        "internal": "PM Spec Internal Review",
        "executive": "PM Spec Executive Review",
        "approved": "PM Spec Approved",
    },
    "dev_design": {
        "owner": "Dev",
        "draft": "Dev Design Drafting",
        "internal": "Dev Design Internal Review",
        "executive": "Dev Design Executive Review",
        "approved": "Dev Design Approved",
    },
    "test_plan": {
        "owner": "Test",
        "draft": "Test Plan Drafting",
        "internal": "Test Plan Internal Review",
        "executive": "Test Plan Executive Review",
        "approved": "Test Plan Approved",
    },
}
NORMAL_NEXT = {PHASES[index]: PHASES[index + 1] for index in range(len(PHASES) - 1)}
EVENT_DRIVEN_STATUS_EVENTS = {
    "blocker",
    "material schedule slip",
    "major risk",
    "scope change",
    "requirement change",
    "major milestone completion",
    "material test failure",
    "dependency failure",
    "executive decision",
}


class StateError(ValueError):
    """Raised when a requested project-state mutation violates an invariant."""


def utc_now() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _approval() -> dict[str, Any]:
    return {
        "status": "Not Approved",
        "version": None,
        "approver": None,
        "date": None,
        "override": False,
        "notes": None,
    }


def _artifact(path: str, owner: str) -> dict[str, Any]:
    return {
        "path": path,
        "owner": owner,
        "version": "0.1",
        "state": "Draft",
        "reviews": [],
        "approval": _approval(),
    }


def new_state(project_id: str, name: str, objective: str) -> dict[str, Any]:
    """Return a new canonical state with the five required crew roles."""
    if not project_id.strip() or not name.strip() or not objective.strip():
        raise StateError("project id, name, and objective must be non-empty")
    now = utc_now()
    state: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "revision": 0,
        "created_at": now,
        "updated_at": now,
        "project": {"id": project_id, "name": name, "objective": objective},
        "phase": "Intake",
        "overall_status": "On Track",
        "crew": [
            {"role": role, "owner": role, "agent_ref": None, "active": True}
            for role in ROLES
        ],
        "artifacts": {
            "pm_spec": _artifact("artifacts/pm-spec.md", "PM"),
            "dev_design": _artifact("artifacts/dev-design-spec.md", "Dev"),
            "test_plan": _artifact("artifacts/test-plan.md", "Test"),
        },
        "open_questions": [],
        "decisions": [],
        "risks": [],
        "issues": [],
        "asks": [],
        "dependencies": [],
        "artifact_links": [],
        "milestones": [],
        "work_packages": [],
        "test": {
            "state": "Not Started",
            "automated_suite_passed": False,
            "evidence": [],
            "unresolved_acceptance_failures": [],
            "determination_by": None,
            "determined_at": None,
        },
        "stakeholder_agreement": [
            {
                "name": role,
                "role": role,
                "required": True,
                "agreed": False,
                "revision": 0,
                "date": now,
                "comments": "",
            }
            for role in ROLES
        ],
        "specification_changes": [],
        "status_events": [],
        "status_history": [],
        "lifecycle_history": [
            {
                "date": now,
                "from": None,
                "to": "Intake",
                "actor": "Feature Crew",
                "reason": "Project initialized",
                "override": False,
            }
        ],
    }
    return state


def clone_state(state: dict[str, Any]) -> dict[str, Any]:
    return copy.deepcopy(state)


def _touch(state: dict[str, Any]) -> None:
    state["revision"] += 1
    state["updated_at"] = utc_now()


def _reporting_has_started(state: dict[str, Any]) -> bool:
    return PHASE_INDEX[state["phase"]] >= PHASE_INDEX["Execution"] or any(
        entry.get("to") == "Execution" for entry in state.get("lifecycle_history", [])
    )


def _queue_status_event(
    state: dict[str, Any], event_type: str, summary: str, *, force: bool = False
) -> str | None:
    if not force and not _reporting_has_started(state):
        return None
    if event_type not in EVENT_DRIVEN_STATUS_EVENTS:
        raise StateError(f"unknown event-driven status type {event_type!r}")
    event_id = f"EVT-{len(state['status_events']) + 1:03d}"
    state["status_events"].append(
        {
            "id": event_id,
            "type": event_type,
            "summary": summary,
            "created_at": utc_now(),
            "status": "Pending",
            "reported_in": None,
        }
    )
    return event_id


def pending_status_events(state: dict[str, Any]) -> list[dict[str, Any]]:
    return [event for event in state["status_events"] if event["status"] == "Pending"]


def _require_artifact(artifact: str) -> None:
    if artifact not in ARTIFACT_KEYS:
        raise StateError(
            f"unknown artifact {artifact!r}; expected one of {', '.join(ARTIFACT_KEYS)}"
        )


def _require_role(role: str) -> None:
    if role not in ROLES:
        raise StateError(
            f"unknown required role {role!r}; expected one of {', '.join(ROLES)}"
        )


def _id_exists(records: Iterable[dict[str, Any]], record_id: str) -> bool:
    return any(record.get("id") == record_id for record in records)


def _require_unique_id(
    records: Iterable[dict[str, Any]], record_id: str, label: str
) -> None:
    if _id_exists(records, record_id):
        raise StateError(f"{label} id {record_id!r} already exists")


def _append_lifecycle(
    state: dict[str, Any],
    old_phase: str,
    new_phase: str,
    actor: str,
    reason: str,
    override: bool,
) -> None:
    state["lifecycle_history"].append(
        {
            "date": utc_now(),
            "from": old_phase,
            "to": new_phase,
            "actor": actor,
            "reason": reason,
            "override": override,
        }
    )


def _set_phase(
    state: dict[str, Any],
    new_phase: str,
    actor: str,
    reason: str,
    override: bool = False,
) -> None:
    old_phase = state["phase"]
    if old_phase == new_phase:
        return
    state["phase"] = new_phase
    _append_lifecycle(state, old_phase, new_phase, actor, reason, override)


def _reset_approval(artifact_state: dict[str, Any]) -> None:
    artifact_state["approval"] = _approval()
    artifact_state["state"] = "Draft"


def _current_reviews_by_role(
    artifact_state: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    version = artifact_state["version"]
    current: dict[str, dict[str, Any]] = {}
    for review in artifact_state["reviews"]:
        if review["version"] == version:
            current[review["role"]] = review
    return current


def unresolved_material_reviews(artifact_state: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        review
        for review in artifact_state["reviews"]
        if review["verdict"] == "challenge"
        and review["material"]
        and review["status"] == "Open"
    ]


def artifact_review_readiness(state: dict[str, Any], artifact: str) -> list[str]:
    _require_artifact(artifact)
    artifact_state = state["artifacts"][artifact]
    problems: list[str] = []
    current = _current_reviews_by_role(artifact_state)
    for role in ROLES:
        review = current.get(role)
        if review is None:
            problems.append(
                f"{role} has not reviewed {artifact} version {artifact_state['version']}"
            )
        elif review["verdict"] != "approve" or review["status"] != "Resolved":
            problems.append(
                f"{role} has not approved {artifact} version {artifact_state['version']}"
            )
    for review in unresolved_material_reviews(artifact_state):
        problems.append(f"material review challenge {review['id']} remains unresolved")
    return problems


def _override_covers(state: dict[str, Any], marker: str) -> bool:
    return any(
        decision.get("executive_override") and marker in decision.get("affected", [])
        for decision in state.get("decisions", [])
    )


def artifact_gate_satisfied(state: dict[str, Any], artifact: str) -> bool:
    artifact_state = state["artifacts"][artifact]
    approval = artifact_state["approval"]
    return approval["status"] == "Approved" or _override_covers(
        state, f"gate:{artifact}"
    )


def can_begin_execution(state: dict[str, Any]) -> tuple[bool, list[str]]:
    missing = [
        artifact
        for artifact in ARTIFACT_KEYS
        if not artifact_gate_satisfied(state, artifact)
    ]
    return (not missing, [f"missing Executive approval for {item}" for item in missing])


def _gate_markers_for_phase(state: dict[str, Any], target_phase: str) -> list[str]:
    markers: list[str] = []
    for artifact, config in ARTIFACT_CONFIG.items():
        if PHASE_INDEX[target_phase] >= PHASE_INDEX[
            config["approved"]
        ] and not artifact_gate_satisfied(state, artifact):
            markers.append(f"gate:{artifact}")
    return markers


def _record_override_decision(
    state: dict[str, Any], actor: str, reason: str, affected: Sequence[str]
) -> None:
    if "executive" not in actor.casefold():
        raise StateError(
            "only the Executive Sponsor may authorize a lifecycle gate override"
        )
    if not reason.strip():
        raise StateError(
            "an Executive override requires a concrete reason and accepted risk"
        )
    record_id = f"D-{len(state['decisions']) + 1:03d}"
    state["decisions"].append(
        {
            "id": record_id,
            "decision": "Executive lifecycle gate override",
            "context": f"Bypass authorized while project was in {state['phase']}",
            "alternatives": ["Complete the normal review and sign-off gate"],
            "rationale": reason,
            "owner": actor,
            "date": utc_now(),
            "affected": list(dict.fromkeys(affected)),
            "executive_override": True,
        }
    )


def set_crew_member(
    state: dict[str, Any],
    role: str,
    *,
    owner: str | None = None,
    agent_ref: str | None = None,
    clear_agent_ref: bool = False,
    active: bool | None = None,
) -> None:
    _require_role(role)
    member = next(item for item in state["crew"] if item["role"] == role)
    if owner is not None:
        if not owner.strip():
            raise StateError("crew owner cannot be blank")
        member["owner"] = owner
    if agent_ref is not None and clear_agent_ref:
        raise StateError("choose either an agent reference or --clear-agent-ref")
    if agent_ref is not None:
        member["agent_ref"] = agent_ref
    if clear_agent_ref:
        member["agent_ref"] = None
    if active is not None:
        member["active"] = bool(active)
    _touch(state)


def transition(
    state: dict[str, Any],
    to_phase: str,
    actor: str,
    reason: str,
    *,
    override: bool = False,
) -> None:
    if to_phase not in PHASES:
        raise StateError(f"unknown lifecycle phase {to_phase!r}")
    current = state["phase"]
    if current == to_phase:
        raise StateError(f"project is already in {to_phase}")
    if to_phase in ("Done", "Completed"):
        raise StateError(
            "use declare_done or complete_project for terminal product states"
        )

    expected = NORMAL_NEXT.get(current)
    if not override and expected != to_phase:
        raise StateError(
            f"normal transition from {current} is to {expected}, not {to_phase}"
        )

    artifact_for_internal = next(
        (
            key
            for key, config in ARTIFACT_CONFIG.items()
            if config["internal"] == to_phase
        ),
        None,
    )
    artifact_for_executive = next(
        (
            key
            for key, config in ARTIFACT_CONFIG.items()
            if config["executive"] == to_phase
        ),
        None,
    )
    artifact_for_approved = next(
        (
            key
            for key, config in ARTIFACT_CONFIG.items()
            if config["approved"] == to_phase
        ),
        None,
    )

    if artifact_for_executive and not override:
        problems = artifact_review_readiness(state, artifact_for_executive)
        if problems:
            raise StateError(
                "artifact is not ready for Executive review: " + "; ".join(problems)
            )
    if (
        artifact_for_approved
        and not artifact_gate_satisfied(state, artifact_for_approved)
        and not override
    ):
        raise StateError(
            "record explicit Executive approval before entering an Approved phase"
        )
    if to_phase == "Execution" and not override:
        allowed, problems = can_begin_execution(state)
        if not allowed:
            raise StateError("execution gate is closed: " + "; ".join(problems))

    if override:
        affected = [f"phase:{to_phase}", *_gate_markers_for_phase(state, to_phase)]
        _record_override_decision(state, actor, reason, affected)

    if artifact_for_internal:
        state["artifacts"][artifact_for_internal]["state"] = "Internal Review"
    if artifact_for_executive:
        state["artifacts"][artifact_for_executive]["state"] = "Executive Review"
    if artifact_for_approved:
        state["artifacts"][artifact_for_approved]["state"] = "Approved"
    artifact_for_draft = next(
        (key for key, config in ARTIFACT_CONFIG.items() if config["draft"] == to_phase),
        None,
    )
    if artifact_for_draft:
        state["artifacts"][artifact_for_draft]["state"] = "Draft"

    _set_phase(state, to_phase, actor, reason, override)
    _touch(state)


def record_review(
    state: dict[str, Any],
    artifact: str,
    role: str,
    verdict: str,
    summary: str,
    *,
    material: bool = True,
) -> str:
    _require_artifact(artifact)
    _require_role(role)
    if verdict not in ("approve", "challenge"):
        raise StateError("review verdict must be approve or challenge")
    if not summary.strip():
        raise StateError("review summary must be non-empty")
    artifact_state = state["artifacts"][artifact]
    if artifact_state["state"] not in ("Draft", "Internal Review"):
        raise StateError(
            "reviews may be recorded only during drafting or internal review"
        )
    review_id = f"REV-{len(artifact_state['reviews']) + 1:03d}"
    artifact_state["reviews"].append(
        {
            "id": review_id,
            "role": role,
            "version": artifact_state["version"],
            "verdict": verdict,
            "summary": summary,
            "material": bool(material),
            "status": "Resolved" if verdict == "approve" else "Open",
            "resolution": None,
            "created_at": utc_now(),
            "resolved_at": None,
        }
    )
    _touch(state)
    return review_id


def resolve_review(
    state: dict[str, Any], artifact: str, review_id: str, resolution: str
) -> None:
    _require_artifact(artifact)
    if not resolution.strip():
        raise StateError("review resolution must be non-empty")
    review = next(
        (
            item
            for item in state["artifacts"][artifact]["reviews"]
            if item["id"] == review_id
        ),
        None,
    )
    if review is None:
        raise StateError(f"review {review_id!r} was not found")
    if review["verdict"] != "challenge":
        raise StateError("only a challenge needs a resolution")
    review["status"] = "Resolved"
    review["resolution"] = resolution
    review["resolved_at"] = utc_now()
    _touch(state)


def add_question(
    state: dict[str, Any],
    question_id: str,
    question: str,
    owner: str,
    answer_from: str,
    why_it_matters: str,
    *,
    recommendation: str | None = None,
    executive_input: bool = False,
    related_to: str | None = None,
) -> None:
    _require_unique_id(state["open_questions"], question_id, "question")
    if not all(
        value.strip()
        for value in (question_id, question, owner, answer_from, why_it_matters)
    ):
        raise StateError(
            "question id, question, owner, answer source, and impact must be non-empty"
        )
    state["open_questions"].append(
        {
            "id": question_id,
            "question": question,
            "owner": owner,
            "answer_from": answer_from,
            "why_it_matters": why_it_matters,
            "recommendation": recommendation,
            "executive_input": bool(executive_input),
            "status": "Open",
            "resolution": None,
            "related_to": related_to,
        }
    )
    if executive_input:
        _queue_status_event(
            state,
            "executive decision",
            f"Executive input required for {question_id}: {question}",
        )
    _touch(state)


def resolve_question(state: dict[str, Any], question_id: str, resolution: str) -> None:
    if not resolution.strip():
        raise StateError("question resolution must be non-empty")
    question = next(
        (item for item in state["open_questions"] if item["id"] == question_id), None
    )
    if question is None:
        raise StateError(f"question {question_id!r} was not found")
    question["status"] = "Resolved"
    question["resolution"] = resolution
    _touch(state)


def executive_review_package(state: dict[str, Any], artifact: str) -> dict[str, Any]:
    _require_artifact(artifact)
    artifact_state = state["artifacts"][artifact]
    questions = [
        item
        for item in state["open_questions"]
        if item["status"] == "Open"
        and item["executive_input"]
        and (
            item["related_to"] in (None, artifact)
            or str(item["related_to"]).startswith(artifact)
        )
    ]
    challenges = unresolved_material_reviews(artifact_state)
    readiness = artifact_review_readiness(state, artifact)
    if challenges or readiness:
        recommendation = "Request Changes"
    elif questions:
        recommendation = "Resolve Specific Question"
    else:
        recommendation = "Approve"
    return {
        "artifact": artifact,
        "version": artifact_state["version"],
        "recommendation": recommendation,
        "executive_questions": questions,
        "material_challenges": challenges,
        "readiness_problems": readiness,
    }


def approve_artifact(
    state: dict[str, Any],
    artifact: str,
    version: str,
    approver: str,
    *,
    notes: str | None = None,
    override: bool = False,
) -> None:
    _require_artifact(artifact)
    config = ARTIFACT_CONFIG[artifact]
    artifact_state = state["artifacts"][artifact]
    if state["phase"] != config["executive"]:
        raise StateError(f"{artifact} may be approved only in {config['executive']}")
    if version != artifact_state["version"]:
        raise StateError(
            f"approval version {version!r} does not match current version {artifact_state['version']!r}"
        )
    if "executive" not in approver.casefold():
        raise StateError("the Executive Sponsor must explicitly approve the artifact")
    readiness = artifact_review_readiness(state, artifact)
    if readiness and not override:
        raise StateError("artifact is not internally ready: " + "; ".join(readiness))
    if override:
        if not notes or not notes.strip():
            raise StateError(
                "an approval override requires notes describing the reason and accepted risk"
            )
        _record_override_decision(state, approver, notes, [f"gate:{artifact}"])

    artifact_state["approval"] = {
        "status": "Approved",
        "version": version,
        "approver": approver,
        "date": utc_now(),
        "override": bool(override),
        "notes": notes,
    }
    artifact_state["state"] = "Approved"
    _set_phase(
        state,
        config["approved"],
        approver,
        f"Approved {artifact} version {version}",
        override,
    )
    _touch(state)


def reject_artifact(
    state: dict[str, Any], artifact: str, approver: str, reason: str
) -> None:
    _require_artifact(artifact)
    config = ARTIFACT_CONFIG[artifact]
    if state["phase"] != config["executive"]:
        raise StateError(f"{artifact} may be rejected only in {config['executive']}")
    if "executive" not in approver.casefold():
        raise StateError(
            "the Executive Sponsor must explicitly reject or request changes"
        )
    if not reason.strip():
        raise StateError("a rejected review requires a reason")
    _reset_approval(state["artifacts"][artifact])
    _set_phase(
        state, config["draft"], approver, f"Requested changes to {artifact}: {reason}"
    )
    _touch(state)


def record_specification_change(
    state: dict[str, Any],
    artifact: str,
    new_version: str,
    impact: str,
    summary: str,
    *,
    affected: Sequence[str] = (),
) -> str:
    _require_artifact(artifact)
    if impact not in ("minor", "material"):
        raise StateError("specification change impact must be minor or material")
    if not new_version.strip() or not summary.strip():
        raise StateError("new version and change summary must be non-empty")
    artifact_state = state["artifacts"][artifact]
    old_version = artifact_state["version"]
    if new_version == old_version:
        raise StateError(
            "new specification version must differ from the current version"
        )

    change_id = f"CHG-{len(state['specification_changes']) + 1:03d}"
    reporting_was_active = _reporting_has_started(state)
    invalidated: list[str] = []
    return_phase: str | None = None
    artifact_state["version"] = new_version

    if impact == "material":
        if artifact == "pm_spec":
            downstream = ("pm_spec", "dev_design", "test_plan")
        elif artifact == "dev_design":
            downstream = ("dev_design", "test_plan")
        else:
            downstream = ("test_plan",)
        for key in downstream:
            if state["artifacts"][key]["approval"]["status"] == "Approved":
                invalidated.append(key)
            _reset_approval(state["artifacts"][key])
        return_phase = ARTIFACT_CONFIG[artifact]["draft"]
        if PHASE_INDEX[state["phase"]] >= PHASE_INDEX[return_phase]:
            _set_phase(
                state,
                return_phase,
                "Feature Crew",
                f"Material {artifact} change {change_id} requires renewed review",
            )
        state["test"]["state"] = "Not Started"
        state["test"]["determination_by"] = None
        state["test"]["determined_at"] = None
        state["test"]["evidence"].append(f"Prior validation invalidated by {change_id}")
        for agreement in state["stakeholder_agreement"]:
            agreement["agreed"] = False
            agreement["comments"] = f"Reconfirmation required after {change_id}"
    elif artifact_state["approval"]["status"] == "Approved":
        prior_note = artifact_state["approval"].get("notes") or ""
        carry_note = (
            f"Approval carried across minor clarification {change_id} to {new_version}."
        )
        artifact_state["approval"]["notes"] = f"{prior_note} {carry_note}".strip()
    else:
        artifact_state["state"] = "Draft"
        draft_phase = ARTIFACT_CONFIG[artifact]["draft"]
        if PHASE_INDEX[state["phase"]] >= PHASE_INDEX[draft_phase]:
            _set_phase(
                state,
                draft_phase,
                "Feature Crew",
                f"Updated unapproved {artifact} to version {new_version}",
            )
            return_phase = draft_phase

    state["specification_changes"].append(
        {
            "id": change_id,
            "artifact": artifact,
            "old_version": old_version,
            "new_version": new_version,
            "impact": impact,
            "summary": summary,
            "date": utc_now(),
            "affected": list(affected),
            "invalidated": invalidated,
            "return_phase": return_phase,
        }
    )
    if impact == "material" and reporting_was_active:
        event_type = "scope change" if artifact == "pm_spec" else "requirement change"
        _queue_status_event(
            state,
            event_type,
            f"{change_id} materially changed {artifact}: {summary}",
            force=True,
        )
    _touch(state)
    return change_id


def add_decision(
    state: dict[str, Any],
    decision_id: str,
    decision: str,
    context: str,
    rationale: str,
    owner: str,
    *,
    alternatives: Sequence[str] = (),
    affected: Sequence[str] = (),
) -> None:
    _require_unique_id(state["decisions"], decision_id, "decision")
    if not all(
        value.strip() for value in (decision_id, decision, context, rationale, owner)
    ):
        raise StateError(
            "decision id, decision, context, rationale, and owner must be non-empty"
        )
    state["decisions"].append(
        {
            "id": decision_id,
            "decision": decision,
            "context": context,
            "alternatives": list(alternatives),
            "rationale": rationale,
            "owner": owner,
            "date": utc_now(),
            "affected": list(affected),
            "executive_override": False,
        }
    )
    _touch(state)


def set_overall_status(state: dict[str, Any], status: str) -> None:
    if status not in OVERALL_STATUSES:
        raise StateError(f"overall status must be one of {', '.join(OVERALL_STATUSES)}")
    if status == "Completed" and state["phase"] != "Completed":
        raise StateError(
            "overall status cannot be Completed before the lifecycle is Completed"
        )
    if state["phase"] == "Completed" and status != "Completed":
        raise StateError("a Completed project must report Completed overall status")
    state["overall_status"] = status
    _touch(state)


def add_milestone(
    state: dict[str, Any],
    milestone_id: str,
    name: str,
    outcome: str,
    owner: str,
    *,
    status: str = "Not Started",
    comments: str = "",
    required: bool = True,
) -> None:
    _require_unique_id(state["milestones"], milestone_id, "milestone")
    if status not in MILESTONE_STATUSES:
        raise StateError(
            f"milestone status must be one of {', '.join(MILESTONE_STATUSES)}"
        )
    if not all(value.strip() for value in (milestone_id, name, outcome, owner)):
        raise StateError("milestone id, name, outcome, and owner must be non-empty")
    state["milestones"].append(
        {
            "id": milestone_id,
            "name": name,
            "outcome": outcome,
            "owner": owner,
            "status": status,
            "comments": comments,
            "required": bool(required),
        }
    )
    _touch(state)


def set_milestone_status(
    state: dict[str, Any], milestone_id: str, status: str, comments: str | None = None
) -> None:
    if status not in MILESTONE_STATUSES:
        raise StateError(
            f"milestone status must be one of {', '.join(MILESTONE_STATUSES)}"
        )
    milestone = next(
        (item for item in state["milestones"] if item["id"] == milestone_id), None
    )
    if milestone is None:
        raise StateError(f"milestone {milestone_id!r} was not found")
    if status == "Done":
        incomplete = [
            item["id"]
            for item in state["work_packages"]
            if item["milestone_id"] == milestone_id
            and item["required"]
            and item["status"] != "Done"
        ]
        if incomplete:
            raise StateError(
                "milestone cannot be Done while required work packages remain: "
                + ", ".join(incomplete)
            )
    previous_status = milestone["status"]
    milestone["status"] = status
    if comments is not None:
        milestone["comments"] = comments
    if status == "Done" and previous_status != "Done":
        _queue_status_event(
            state,
            "major milestone completion",
            f"Milestone {milestone_id} is Done: {milestone['outcome']}",
        )
    _touch(state)


def add_work_package(
    state: dict[str, Any],
    work_package_id: str,
    milestone_id: str,
    name: str,
    owner: str,
    delivers: str,
    *,
    source_references: Sequence[str],
    dependencies: Sequence[str] = (),
    acceptance_criteria: Sequence[str],
    validation_links: Sequence[str] = (),
    status: str = "Not Started",
    comments: str = "",
    required: bool = True,
) -> None:
    _require_unique_id(state["work_packages"], work_package_id, "work package")
    if not _id_exists(state["milestones"], milestone_id):
        raise StateError(f"milestone {milestone_id!r} was not found")
    if status not in WORK_PACKAGE_STATUSES:
        raise StateError(
            f"work-package status must be one of {', '.join(WORK_PACKAGE_STATUSES)}"
        )
    if not all(value.strip() for value in (work_package_id, name, owner, delivers)):
        raise StateError(
            "work-package id, name, owner, and deliverable must be non-empty"
        )
    if not source_references or not acceptance_criteria:
        raise StateError(
            "a work package requires source references and acceptance criteria"
        )
    state["work_packages"].append(
        {
            "id": work_package_id,
            "milestone_id": milestone_id,
            "name": name,
            "owner": owner,
            "delivers": delivers,
            "source_references": list(source_references),
            "dependencies": list(dependencies),
            "acceptance_criteria": list(acceptance_criteria),
            "status": status,
            "comments": comments,
            "validation_links": list(validation_links),
            "required": bool(required),
        }
    )
    _touch(state)


def set_work_package_status(
    state: dict[str, Any],
    work_package_id: str,
    status: str,
    comments: str | None = None,
) -> None:
    if status not in WORK_PACKAGE_STATUSES:
        raise StateError(
            f"work-package status must be one of {', '.join(WORK_PACKAGE_STATUSES)}"
        )
    work_package = next(
        (item for item in state["work_packages"] if item["id"] == work_package_id), None
    )
    if work_package is None:
        raise StateError(f"work package {work_package_id!r} was not found")
    work_package["status"] = status
    if comments is not None:
        work_package["comments"] = comments
    _touch(state)


def add_issue(
    state: dict[str, Any],
    issue_id: str,
    description: str,
    owner: str,
    impact: str,
    *,
    material: bool = True,
    blocker: bool = False,
) -> None:
    _require_unique_id(state["issues"], issue_id, "issue")
    if not all(value.strip() for value in (issue_id, description, owner, impact)):
        raise StateError("issue id, description, owner, and impact must be non-empty")
    state["issues"].append(
        {
            "id": issue_id,
            "description": description,
            "owner": owner,
            "impact": impact,
            "material": bool(material),
            "blocker": bool(blocker),
            "status": "Open",
            "resolution": None,
            "accepted": False,
        }
    )
    if blocker:
        _queue_status_event(state, "blocker", f"{issue_id}: {description}")
    _touch(state)


def resolve_issue(
    state: dict[str, Any], issue_id: str, resolution: str, *, accepted: bool = False
) -> None:
    if not resolution.strip():
        raise StateError(
            "issue resolution or explicit acceptance rationale must be non-empty"
        )
    issue = next((item for item in state["issues"] if item["id"] == issue_id), None)
    if issue is None:
        raise StateError(f"issue {issue_id!r} was not found")
    issue["status"] = "Accepted" if accepted else "Resolved"
    issue["resolution"] = resolution
    issue["accepted"] = bool(accepted)
    _touch(state)


def add_risk(
    state: dict[str, Any],
    risk_id: str,
    description: str,
    area: str,
    owner: str,
    impact: str,
    mitigation: str,
) -> None:
    allowed_areas = (
        "Schedule",
        "Scope",
        "Quality",
        "Customer experience",
        "Architecture",
        "Dependencies",
        "Release",
    )
    _require_unique_id(state["risks"], risk_id, "risk")
    if area not in allowed_areas:
        raise StateError("risk area is not an approved Executive status area")
    state["risks"].append(
        {
            "id": risk_id,
            "description": description,
            "area": area,
            "owner": owner,
            "impact": impact,
            "mitigation": mitigation,
            "status": "Open",
        }
    )
    _queue_status_event(state, "major risk", f"{risk_id}: {description}")
    _touch(state)


def set_risk_status(state: dict[str, Any], risk_id: str, status: str) -> None:
    if status not in ("Open", "Resolved", "Realized"):
        raise StateError("risk status must be Open, Resolved, or Realized")
    risk = next((item for item in state["risks"] if item["id"] == risk_id), None)
    if risk is None:
        raise StateError(f"risk {risk_id!r} was not found")
    risk["status"] = status
    _touch(state)


def add_ask(
    state: dict[str, Any],
    ask_id: str,
    requester: str,
    target: str,
    need: str,
    why_it_matters: str,
    *,
    needed_by: str | None = None,
) -> None:
    _require_unique_id(state["asks"], ask_id, "ask")
    state["asks"].append(
        {
            "id": ask_id,
            "requester": requester,
            "target": target,
            "need": need,
            "why_it_matters": why_it_matters,
            "needed_by": needed_by,
            "status": "Open",
        }
    )
    _touch(state)


def add_dependency(
    state: dict[str, Any],
    dependency_id: str,
    who: str,
    need: str,
    delivery_implication: str,
    risk: str,
    *,
    needed_by: str | None = None,
) -> None:
    _require_unique_id(state["dependencies"], dependency_id, "dependency")
    state["dependencies"].append(
        {
            "id": dependency_id,
            "who": who,
            "need": need,
            "needed_by": needed_by,
            "delivery_implication": delivery_implication,
            "risk": risk,
            "status": "Open",
        }
    )
    _touch(state)


def add_artifact_link(
    state: dict[str, Any],
    artifact_id: str,
    label: str,
    location: str,
    kind: str,
    owner: str,
    *,
    version: str | None = None,
    source_artifact: str | None = None,
    source_version: str | None = None,
) -> None:
    _require_unique_id(state["artifact_links"], artifact_id, "artifact link")
    if not all(value.strip() for value in (artifact_id, label, location, kind, owner)):
        raise StateError(
            "artifact-link id, label, location, kind, and owner must be non-empty"
        )
    if version is not None and not version.strip():
        raise StateError("artifact-link version cannot be blank")
    if (source_artifact is None) != (source_version is None):
        raise StateError(
            "artifact-link source artifact and source version must be provided together"
        )
    if source_artifact is not None:
        _require_artifact(source_artifact)
        if not source_version or not source_version.strip():
            raise StateError("artifact-link source version cannot be blank")
    if kind in UX_ARTIFACT_KINDS:
        if not version or not version.strip():
            raise StateError("UX artifact links require an exact artifact version")
        if source_artifact != "pm_spec" or not source_version:
            raise StateError(
                "UX artifact links require pm_spec and its exact version as the source"
            )
        current_pm_version = state["artifacts"]["pm_spec"]["version"]
        if source_version != current_pm_version:
            raise StateError(
                "UX artifact source version must match the current PM Spec version "
                f"{current_pm_version}"
            )
    state["artifact_links"].append(
        {
            "id": artifact_id,
            "label": label,
            "location": location,
            "kind": kind,
            "owner": owner,
            "version": version,
            "source_artifact": source_artifact,
            "source_version": source_version,
        }
    )
    _touch(state)


def set_record_status(
    state: dict[str, Any], collection: str, record_id: str, status: str
) -> None:
    allowed = {"asks": ("Open", "Resolved"), "dependencies": ("Open", "Resolved")}
    if collection not in allowed:
        raise StateError("only asks and dependencies use this status operation")
    if status not in allowed[collection]:
        raise StateError(
            f"{collection} status must be one of {', '.join(allowed[collection])}"
        )
    record = next((item for item in state[collection] if item["id"] == record_id), None)
    if record is None:
        raise StateError(f"{collection[:-1]} {record_id!r} was not found")
    record["status"] = status
    _touch(state)


def set_test_state(
    state: dict[str, Any],
    result: str,
    actor: str,
    *,
    evidence: Sequence[str] = (),
    unresolved_failures: Sequence[str] = (),
    automated_suite_passed: bool = False,
) -> None:
    if result not in TEST_STATES:
        raise StateError(f"test state must be one of {', '.join(TEST_STATES)}")
    if result in ("Passed", "Failed") and actor != "Test":
        raise StateError("only the Test role may determine Passed or Failed")
    if result == "Passed" and unresolved_failures:
        raise StateError(
            "Test cannot report Passed with unresolved acceptance failures"
        )
    state["test"] = {
        "state": result,
        "automated_suite_passed": bool(automated_suite_passed),
        "evidence": list(evidence),
        "unresolved_acceptance_failures": list(unresolved_failures),
        "determination_by": actor if result in ("Passed", "Failed") else None,
        "determined_at": utc_now() if result in ("Passed", "Failed") else None,
    }
    if result == "Failed":
        _queue_status_event(
            state,
            "material test failure",
            "Test reported Failed"
            + (f": {', '.join(unresolved_failures)}" if unresolved_failures else ""),
        )
    _touch(state)


def set_stakeholder_agreement(
    state: dict[str, Any],
    name: str,
    role: str,
    agreed: bool,
    *,
    required: bool = True,
    comments: str = "",
) -> None:
    record = next(
        (
            item
            for item in state["stakeholder_agreement"]
            if item["name"] == name and item["role"] == role
        ),
        None,
    )
    if record is None:
        record = {"name": name, "role": role}
        state["stakeholder_agreement"].append(record)
    record.update(
        {
            "required": bool(required),
            "agreed": bool(agreed),
            "revision": state["revision"],
            "date": utc_now(),
            "comments": comments,
        }
    )
    _touch(state)


def done_readiness_problems(state: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    if state["test"]["state"] != "Passed":
        problems.append("Test has not reported Test Passed")
    if state["test"]["unresolved_acceptance_failures"]:
        problems.append("unresolved failed acceptance criteria remain")
    unresolved_issues = [
        issue["id"]
        for issue in state["issues"]
        if issue["status"] not in ("Resolved", "Accepted")
    ]
    if unresolved_issues:
        problems.append("unresolved issues remain: " + ", ".join(unresolved_issues))
    missing_agreement = [
        f"{item['name']} ({item['role']})"
        for item in state["stakeholder_agreement"]
        if item["required"] and not item["agreed"]
    ]
    if missing_agreement:
        problems.append(
            "required stakeholder agreement is missing: " + ", ".join(missing_agreement)
        )
    return problems


def declare_done(state: dict[str, Any], actor: str, reason: str) -> None:
    if state["phase"] != "Validation":
        raise StateError("PM may declare Done only from Validation")
    if actor != "PM":
        raise StateError("PM owns the final Done decision")
    if not reason.strip():
        raise StateError("the PM Done declaration requires a product-outcome rationale")
    problems = done_readiness_problems(state)
    if problems:
        raise StateError("Done criteria are not met: " + "; ".join(problems))
    _set_phase(state, "Done", actor, reason)
    _touch(state)


def completion_readiness_problems(state: dict[str, Any]) -> list[str]:
    problems = done_readiness_problems(state)
    incomplete_milestones = [
        item["id"]
        for item in state["milestones"]
        if item["required"] and item["status"] != "Done"
    ]
    if incomplete_milestones:
        problems.append(
            "required milestones are not Done: " + ", ".join(incomplete_milestones)
        )
    return problems


def complete_project(state: dict[str, Any], actor: str, reason: str) -> None:
    if state["phase"] != "Done":
        raise StateError("project completion requires the feature to be Done first")
    if actor != "PM":
        raise StateError("PM must formally close the project")
    if not reason.strip():
        raise StateError("formal project closure requires a rationale")
    problems = completion_readiness_problems(state)
    if problems:
        raise StateError("Completed criteria are not met: " + "; ".join(problems))
    _set_phase(state, "Completed", actor, reason)
    state["overall_status"] = "Completed"
    _touch(state)


def requires_event_driven_status(event: str) -> bool:
    return event.strip().casefold() in EVENT_DRIVEN_STATUS_EVENTS


def record_status(
    state: dict[str, Any],
    kind: str,
    overall_status: str,
    summary: str,
    *,
    changed_facts: Sequence[str],
    synchronized_roles: Sequence[str],
    snapshot_path: str | None = None,
) -> str:
    if not _reporting_has_started(state):
        raise StateError("regular Executive status reporting begins in Execution")
    if kind not in ("Heartbeat", "Event-driven"):
        raise StateError("status kind must be Heartbeat or Event-driven")
    if overall_status not in OVERALL_STATUSES:
        raise StateError(f"overall status must be one of {', '.join(OVERALL_STATUSES)}")
    if overall_status == "Completed" and state["phase"] != "Completed":
        raise StateError("Completed status requires a Completed lifecycle")
    unknown_roles = sorted(set(synchronized_roles) - set(ROLES))
    missing_roles = sorted(set(ROLES) - set(synchronized_roles))
    if unknown_roles:
        raise StateError("unknown synchronized roles: " + ", ".join(unknown_roles))
    if missing_roles:
        raise StateError(
            "status facts are not synchronized with: " + ", ".join(missing_roles)
        )
    if not summary.strip():
        raise StateError("status summary must be non-empty")
    pending_events = pending_status_events(state)
    if kind == "Heartbeat" and pending_events:
        raise StateError(
            "event-driven status is required before a heartbeat; pending events: "
            + ", ".join(event["id"] for event in pending_events)
        )
    status_id = f"STATUS-{len(state['status_history']) + 1:03d}"
    reported_event_ids = (
        [event["id"] for event in pending_events] if kind == "Event-driven" else []
    )
    state["status_history"].append(
        {
            "id": status_id,
            "date": utc_now(),
            "kind": kind,
            "overall_status": overall_status,
            "summary": summary,
            "snapshot_path": snapshot_path,
            "changed_facts": list(changed_facts),
            "synchronized_revision": state["revision"],
            "synchronized_roles": list(dict.fromkeys(synchronized_roles)),
            "reported_event_ids": reported_event_ids,
        }
    )
    for event in pending_events:
        event["status"] = "Reported"
        event["reported_in"] = status_id
    state["overall_status"] = overall_status
    _touch(state)
    return status_id


def validate_state(state: dict[str, Any]) -> list[str]:
    """Return invariant violations. An empty list means the state is valid."""
    errors: list[str] = []
    required_keys = {
        "schema_version",
        "revision",
        "created_at",
        "updated_at",
        "project",
        "phase",
        "overall_status",
        "crew",
        "artifacts",
        "open_questions",
        "decisions",
        "risks",
        "issues",
        "asks",
        "dependencies",
        "artifact_links",
        "milestones",
        "work_packages",
        "test",
        "stakeholder_agreement",
        "specification_changes",
        "status_events",
        "status_history",
        "lifecycle_history",
    }
    missing = sorted(required_keys - set(state))
    if missing:
        return ["missing top-level fields: " + ", ".join(missing)]
    if state["schema_version"] != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    if not isinstance(state["revision"], int) or state["revision"] < 0:
        errors.append("revision must be a non-negative integer")
    if state["phase"] not in PHASES:
        errors.append("phase is not an allowed lifecycle phase")
    if state["overall_status"] not in OVERALL_STATUSES:
        errors.append("overall_status is not allowed")
    if state["phase"] == "Completed" and state["overall_status"] != "Completed":
        errors.append("Completed lifecycle requires Completed overall status")
    if state["overall_status"] == "Completed" and state["phase"] != "Completed":
        errors.append("Completed overall status requires Completed lifecycle")

    crew_roles = [item.get("role") for item in state["crew"]]
    if len(crew_roles) != len(set(crew_roles)):
        errors.append("crew roles must be unique")
    if set(crew_roles) != set(ROLES):
        errors.append("crew must contain exactly PM, Dev, Test, UX, and Content")

    if set(state["artifacts"]) != set(ARTIFACT_KEYS):
        errors.append("artifacts must contain pm_spec, dev_design, and test_plan")
    else:
        for key, config in ARTIFACT_CONFIG.items():
            artifact_state = state["artifacts"][key]
            if artifact_state.get("owner") != config["owner"]:
                errors.append(f"{key} owner must be {config['owner']}")
            if artifact_state.get("state") not in (
                "Draft",
                "Internal Review",
                "Executive Review",
                "Approved",
            ):
                errors.append(f"{key} state is invalid")
            approval = artifact_state.get("approval", {})
            if approval.get("status") not in ("Not Approved", "Approved"):
                errors.append(f"{key} approval status is invalid")
            if (
                approval.get("status") == "Approved"
                and artifact_state.get("state") != "Approved"
            ):
                errors.append(f"{key} is approved but artifact state is not Approved")
            seen_review_ids: set[str] = set()
            for review in artifact_state.get("reviews", []):
                if review.get("id") in seen_review_ids:
                    errors.append(
                        f"{key} contains duplicate review id {review.get('id')}"
                    )
                seen_review_ids.add(review.get("id"))
                if review.get("role") not in ROLES:
                    errors.append(f"{key} contains a review from an unknown role")
                if review.get("verdict") not in ("approve", "challenge"):
                    errors.append(f"{key} contains an invalid review verdict")
                if review.get("status") not in ("Open", "Resolved"):
                    errors.append(f"{key} contains an invalid review status")

    if state["phase"] in PHASE_INDEX:
        for key, config in ARTIFACT_CONFIG.items():
            if PHASE_INDEX[state["phase"]] >= PHASE_INDEX[
                config["approved"]
            ] and not artifact_gate_satisfied(state, key):
                errors.append(
                    f"phase {state['phase']} requires approval or recorded override for {key}"
                )

    for collection in (
        "open_questions",
        "decisions",
        "risks",
        "issues",
        "asks",
        "dependencies",
        "artifact_links",
        "milestones",
        "work_packages",
        "status_events",
    ):
        ids = [item.get("id") for item in state[collection]]
        if len(ids) != len(set(ids)):
            errors.append(f"{collection} contains duplicate ids")

    for artifact_link in state["artifact_links"]:
        artifact_id = artifact_link.get("id")
        kind = artifact_link.get("kind")
        source_artifact = artifact_link.get("source_artifact")
        source_version = artifact_link.get("source_version")
        if (source_artifact is None) != (source_version is None):
            errors.append(
                f"artifact link {artifact_id} must pair source_artifact with source_version"
            )
        if source_artifact is not None and source_artifact not in ARTIFACT_KEYS:
            errors.append(
                f"artifact link {artifact_id} references an unknown source artifact"
            )
        if kind in UX_ARTIFACT_KINDS:
            if not artifact_link.get("version"):
                errors.append(
                    f"UX artifact link {artifact_id} requires an exact artifact version"
                )
            if source_artifact != "pm_spec" or not source_version:
                errors.append(
                    f"UX artifact link {artifact_id} requires a PM Spec source version"
                )

    milestone_ids = {item.get("id") for item in state["milestones"]}
    for milestone in state["milestones"]:
        if milestone.get("status") not in MILESTONE_STATUSES:
            errors.append(f"milestone {milestone.get('id')} has an invalid status")
    for work_package in state["work_packages"]:
        if work_package.get("status") not in WORK_PACKAGE_STATUSES:
            errors.append(
                f"work package {work_package.get('id')} has an invalid status"
            )
        if work_package.get("milestone_id") not in milestone_ids:
            errors.append(
                f"work package {work_package.get('id')} references an unknown milestone"
            )

    if state["test"].get("state") not in TEST_STATES:
        errors.append("test state is invalid")
    if state["test"].get("state") == "Passed":
        if state["test"].get("determination_by") != "Test":
            errors.append("Test Passed must be determined by the Test role")
        if state["test"].get("unresolved_acceptance_failures"):
            errors.append(
                "Test Passed cannot coexist with unresolved acceptance failures"
            )

    if state["phase"] in ("Done", "Completed"):
        errors.extend(
            "Done invariant: " + item for item in done_readiness_problems(state)
        )
    if state["phase"] == "Completed":
        errors.extend(
            "Completed invariant: " + item
            for item in completion_readiness_problems(state)
        )

    for entry in state["status_history"]:
        if entry.get("overall_status") not in OVERALL_STATUSES:
            errors.append(
                f"status entry {entry.get('id')} has an invalid overall status"
            )
        if set(entry.get("synchronized_roles", [])) != set(ROLES):
            errors.append(
                f"status entry {entry.get('id')} was not synchronized with the full crew"
            )
    status_ids = {entry.get("id") for entry in state["status_history"]}
    for event in state["status_events"]:
        if event.get("type") not in EVENT_DRIVEN_STATUS_EVENTS:
            errors.append(f"status event {event.get('id')} has an invalid type")
        if event.get("status") not in ("Pending", "Reported"):
            errors.append(f"status event {event.get('id')} has an invalid status")
        if (
            event.get("status") == "Reported"
            and event.get("reported_in") not in status_ids
        ):
            errors.append(
                f"status event {event.get('id')} does not reference a recorded status update"
            )
    return errors


def load_state(path: Path | str) -> dict[str, Any]:
    state_path = Path(path)
    try:
        with state_path.open("r", encoding="utf-8") as handle:
            state = json.load(handle)
    except FileNotFoundError as exc:
        raise StateError(f"state file does not exist: {state_path}") from exc
    except json.JSONDecodeError as exc:
        raise StateError(f"state file is not valid JSON: {exc}") from exc
    errors = validate_state(state)
    if errors:
        raise StateError("state validation failed:\n- " + "\n- ".join(errors))
    return state


def save_state(path: Path | str, state: dict[str, Any]) -> None:
    state_path = Path(path)
    errors = validate_state(state)
    if errors:
        raise StateError("refusing to save invalid state:\n- " + "\n- ".join(errors))
    state_path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temp_name = tempfile.mkstemp(
        prefix=f".{state_path.name}.", suffix=".tmp", dir=str(state_path.parent)
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(state, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, state_path)
    except Exception:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def initialize_project(
    project_dir: Path | str, project_id: str, name: str, objective: str
) -> Path:
    project_path = Path(project_dir).resolve()
    state_path = project_path / "project-state.json"
    artifacts_path = project_path / "artifacts"
    status_path = project_path / "status"
    template_root = Path(__file__).resolve().parent.parent / "assets" / "templates"
    templates = {
        "pm-spec.md": "pm-spec.md",
        "dev-design-spec.md": "dev-design-spec.md",
        "test-plan.md": "test-plan.md",
        "project-status.md": "project-status.md",
    }
    missing_templates = [
        str(template_root / source_name)
        for source_name in templates
        if not (template_root / source_name).is_file()
    ]
    if missing_templates:
        raise StateError(
            "required templates are missing: " + ", ".join(missing_templates)
        )
    existing_targets = [
        state_path,
        *(artifacts_path / target_name for target_name in templates.values()),
    ]
    collisions = [str(path) for path in existing_targets if path.exists()]
    if collisions:
        raise StateError(
            "refusing to overwrite existing project files: " + ", ".join(collisions)
        )

    artifacts_path.mkdir(parents=True, exist_ok=True)
    status_path.mkdir(parents=True, exist_ok=True)
    today = utc_now().split("T", 1)[0]
    for source_name, target_name in templates.items():
        source = template_root / source_name
        target = artifacts_path / target_name
        content = source.read_text(encoding="utf-8")
        content = content.replace("<Project Name>", name).replace(
            "<project-id>", project_id
        )
        content = content.replace("<date>", today)
        target.write_text(content, encoding="utf-8", newline="\n")

    state = new_state(project_id, name, objective)
    save_state(state_path, state)
    return state_path


def _load_mutate_save(state_path: str, operation: Any) -> dict[str, Any]:
    state = load_state(state_path)
    operation(state)
    save_state(state_path, state)
    return state


def _add_common_state_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--state", required=True, help="Path to project-state.json")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser(
        "init", help="Create canonical state and living artifacts"
    )
    init_parser.add_argument("--project-dir", required=True)
    init_parser.add_argument("--project-id", required=True)
    init_parser.add_argument("--name", required=True)
    init_parser.add_argument("--objective", required=True)

    validate_parser = subparsers.add_parser("validate", help="Validate canonical state")
    _add_common_state_argument(validate_parser)

    package_parser = subparsers.add_parser(
        "review-package", help="Summarize Executive review readiness and questions"
    )
    _add_common_state_argument(package_parser)
    package_parser.add_argument("--artifact", required=True, choices=ARTIFACT_KEYS)

    crew_parser = subparsers.add_parser(
        "crew-set", help="Update a required role's current owner or agent handle"
    )
    _add_common_state_argument(crew_parser)
    crew_parser.add_argument("--role", required=True, choices=ROLES)
    crew_parser.add_argument("--owner")
    crew_parser.add_argument("--agent-ref")
    crew_parser.add_argument("--clear-agent-ref", action="store_true")
    crew_parser.add_argument("--inactive", action="store_true")

    transition_parser = subparsers.add_parser(
        "transition", help="Advance or override lifecycle phase"
    )
    _add_common_state_argument(transition_parser)
    transition_parser.add_argument("--to", required=True, choices=PHASES)
    transition_parser.add_argument("--actor", required=True)
    transition_parser.add_argument("--reason", required=True)
    transition_parser.add_argument("--override", action="store_true")

    review_parser = subparsers.add_parser(
        "review", help="Record a role approval or challenge"
    )
    _add_common_state_argument(review_parser)
    review_parser.add_argument("--artifact", required=True, choices=ARTIFACT_KEYS)
    review_parser.add_argument("--role", required=True, choices=ROLES)
    review_parser.add_argument(
        "--verdict", required=True, choices=("approve", "challenge")
    )
    review_parser.add_argument("--summary", required=True)
    review_parser.add_argument("--non-material", action="store_true")

    resolve_review_parser = subparsers.add_parser(
        "resolve-review", help="Resolve a review challenge"
    )
    _add_common_state_argument(resolve_review_parser)
    resolve_review_parser.add_argument(
        "--artifact", required=True, choices=ARTIFACT_KEYS
    )
    resolve_review_parser.add_argument("--review-id", required=True)
    resolve_review_parser.add_argument("--resolution", required=True)

    question_parser = subparsers.add_parser("question", help="Record an open question")
    _add_common_state_argument(question_parser)
    question_parser.add_argument("--id", required=True)
    question_parser.add_argument("--question", required=True)
    question_parser.add_argument("--owner", required=True)
    question_parser.add_argument("--answer-from", required=True)
    question_parser.add_argument("--why", required=True)
    question_parser.add_argument("--recommendation")
    question_parser.add_argument("--executive-input", action="store_true")
    question_parser.add_argument("--related-to")

    resolve_question_parser = subparsers.add_parser(
        "resolve-question", help="Resolve an open question"
    )
    _add_common_state_argument(resolve_question_parser)
    resolve_question_parser.add_argument("--id", required=True)
    resolve_question_parser.add_argument("--resolution", required=True)

    decision_parser = subparsers.add_parser(
        "decision", help="Record an important non-trivial decision"
    )
    _add_common_state_argument(decision_parser)
    decision_parser.add_argument("--id", required=True)
    decision_parser.add_argument("--decision", required=True)
    decision_parser.add_argument("--context", required=True)
    decision_parser.add_argument("--rationale", required=True)
    decision_parser.add_argument("--owner", required=True)
    decision_parser.add_argument("--alternative", action="append", default=[])
    decision_parser.add_argument("--affected", action="append", default=[])

    change_parser = subparsers.add_parser(
        "change", help="Record a specification change"
    )
    _add_common_state_argument(change_parser)
    change_parser.add_argument("--artifact", required=True, choices=ARTIFACT_KEYS)
    change_parser.add_argument("--new-version", required=True)
    change_parser.add_argument("--impact", required=True, choices=("minor", "material"))
    change_parser.add_argument("--summary", required=True)
    change_parser.add_argument("--affected", action="append", default=[])

    approve_parser = subparsers.add_parser(
        "approve", help="Record explicit Executive approval"
    )
    _add_common_state_argument(approve_parser)
    approve_parser.add_argument("--artifact", required=True, choices=ARTIFACT_KEYS)
    approve_parser.add_argument("--version", required=True)
    approve_parser.add_argument("--approver", default="Executive Sponsor")
    approve_parser.add_argument("--notes")
    approve_parser.add_argument("--override", action="store_true")

    reject_parser = subparsers.add_parser(
        "reject", help="Record Executive request for changes"
    )
    _add_common_state_argument(reject_parser)
    reject_parser.add_argument("--artifact", required=True, choices=ARTIFACT_KEYS)
    reject_parser.add_argument("--approver", default="Executive Sponsor")
    reject_parser.add_argument("--reason", required=True)

    milestone_add = subparsers.add_parser(
        "milestone-add", help="Add an outcome milestone"
    )
    _add_common_state_argument(milestone_add)
    milestone_add.add_argument("--id", required=True)
    milestone_add.add_argument("--name", required=True)
    milestone_add.add_argument("--outcome", required=True)
    milestone_add.add_argument("--owner", required=True)
    milestone_add.add_argument("--optional", action="store_true")

    milestone_set = subparsers.add_parser(
        "milestone-set", help="Set a milestone status"
    )
    _add_common_state_argument(milestone_set)
    milestone_set.add_argument("--id", required=True)
    milestone_set.add_argument("--status", required=True, choices=MILESTONE_STATUSES)
    milestone_set.add_argument("--comments")

    work_add = subparsers.add_parser("work-add", help="Add a work package")
    _add_common_state_argument(work_add)
    work_add.add_argument("--id", required=True)
    work_add.add_argument("--milestone", required=True)
    work_add.add_argument("--name", required=True)
    work_add.add_argument("--owner", required=True)
    work_add.add_argument("--delivers", required=True)
    work_add.add_argument("--source", action="append", required=True)
    work_add.add_argument("--dependency", action="append", default=[])
    work_add.add_argument("--acceptance", action="append", required=True)
    work_add.add_argument("--validation", action="append", default=[])
    work_add.add_argument("--optional", action="store_true")

    work_set = subparsers.add_parser("work-set", help="Set a work-package status")
    _add_common_state_argument(work_set)
    work_set.add_argument("--id", required=True)
    work_set.add_argument("--status", required=True, choices=WORK_PACKAGE_STATUSES)
    work_set.add_argument("--comments")

    issue_add = subparsers.add_parser(
        "issue-add", help="Record an issue that has happened"
    )
    _add_common_state_argument(issue_add)
    issue_add.add_argument("--id", required=True)
    issue_add.add_argument("--description", required=True)
    issue_add.add_argument("--owner", required=True)
    issue_add.add_argument("--impact", required=True)
    issue_add.add_argument("--non-material", action="store_true")
    issue_add.add_argument("--blocker", action="store_true")

    issue_resolve = subparsers.add_parser(
        "issue-resolve", help="Resolve or explicitly accept an issue"
    )
    _add_common_state_argument(issue_resolve)
    issue_resolve.add_argument("--id", required=True)
    issue_resolve.add_argument("--resolution", required=True)
    issue_resolve.add_argument("--accept", action="store_true")

    risk_add = subparsers.add_parser(
        "risk-add", help="Record a material hypothetical risk"
    )
    _add_common_state_argument(risk_add)
    risk_add.add_argument("--id", required=True)
    risk_add.add_argument("--description", required=True)
    risk_add.add_argument(
        "--area",
        required=True,
        choices=(
            "Schedule",
            "Scope",
            "Quality",
            "Customer experience",
            "Architecture",
            "Dependencies",
            "Release",
        ),
    )
    risk_add.add_argument("--owner", required=True)
    risk_add.add_argument("--impact", required=True)
    risk_add.add_argument("--mitigation", required=True)

    risk_set = subparsers.add_parser(
        "risk-set", help="Resolve or realize an existing risk"
    )
    _add_common_state_argument(risk_set)
    risk_set.add_argument("--id", required=True)
    risk_set.add_argument(
        "--status", required=True, choices=("Open", "Resolved", "Realized")
    )

    ask_add = subparsers.add_parser(
        "ask-add", help="Record who is asking whom for what"
    )
    _add_common_state_argument(ask_add)
    ask_add.add_argument("--id", required=True)
    ask_add.add_argument("--requester", required=True)
    ask_add.add_argument("--target", required=True)
    ask_add.add_argument("--need", required=True)
    ask_add.add_argument("--why", required=True)
    ask_add.add_argument("--needed-by")

    ask_set = subparsers.add_parser("ask-set", help="Update an ask's status")
    _add_common_state_argument(ask_set)
    ask_set.add_argument("--id", required=True)
    ask_set.add_argument("--status", required=True, choices=("Open", "Resolved"))

    dependency_add = subparsers.add_parser(
        "dependency-add", help="Record a material dependency"
    )
    _add_common_state_argument(dependency_add)
    dependency_add.add_argument("--id", required=True)
    dependency_add.add_argument("--who", required=True)
    dependency_add.add_argument("--need", required=True)
    dependency_add.add_argument("--needed-by")
    dependency_add.add_argument("--delivery-implication", required=True)
    dependency_add.add_argument("--risk", required=True)

    dependency_set = subparsers.add_parser(
        "dependency-set", help="Update a dependency's status"
    )
    _add_common_state_argument(dependency_set)
    dependency_set.add_argument("--id", required=True)
    dependency_set.add_argument("--status", required=True, choices=("Open", "Resolved"))

    artifact_link = subparsers.add_parser(
        "artifact-link", help="Record a relevant project artifact path or URL"
    )
    _add_common_state_argument(artifact_link)
    artifact_link.add_argument("--id", required=True)
    artifact_link.add_argument("--label", required=True)
    artifact_link.add_argument("--location", required=True)
    artifact_link.add_argument("--kind", required=True)
    artifact_link.add_argument("--owner", required=True)
    artifact_link.add_argument("--version")
    artifact_link.add_argument("--source-artifact", choices=ARTIFACT_KEYS)
    artifact_link.add_argument("--source-version")

    test_parser = subparsers.add_parser(
        "set-test", help="Record Test validation state and evidence"
    )
    _add_common_state_argument(test_parser)
    test_parser.add_argument("--result", required=True, choices=TEST_STATES)
    test_parser.add_argument("--actor", default="Test")
    test_parser.add_argument("--evidence", action="append", default=[])
    test_parser.add_argument("--failure", action="append", default=[])
    test_parser.add_argument("--automated-suite-passed", action="store_true")

    agree_parser = subparsers.add_parser(
        "agree", help="Record relevant stakeholder agreement"
    )
    _add_common_state_argument(agree_parser)
    agree_parser.add_argument("--name", required=True)
    agree_parser.add_argument("--role", required=True)
    agree_parser.add_argument("--disagree", action="store_true")
    agree_parser.add_argument("--optional", action="store_true")
    agree_parser.add_argument("--comments", default="")

    done_parser = subparsers.add_parser(
        "declare-done", help="Record PM's final Done decision"
    )
    _add_common_state_argument(done_parser)
    done_parser.add_argument("--actor", default="PM")
    done_parser.add_argument("--reason", required=True)

    complete_parser = subparsers.add_parser(
        "complete", help="Formally close a Done project"
    )
    _add_common_state_argument(complete_parser)
    complete_parser.add_argument("--actor", default="PM")
    complete_parser.add_argument("--reason", required=True)

    status_parser = subparsers.add_parser(
        "status", help="Record a synchronized Executive status delta"
    )
    _add_common_state_argument(status_parser)
    status_parser.add_argument(
        "--kind", required=True, choices=("Heartbeat", "Event-driven")
    )
    status_parser.add_argument("--overall", required=True, choices=OVERALL_STATUSES)
    status_parser.add_argument("--summary", required=True)
    status_parser.add_argument("--changed", action="append", default=[])
    status_parser.add_argument("--role", action="append", required=True, choices=ROLES)
    status_parser.add_argument("--snapshot-path")

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            path = initialize_project(
                args.project_dir, args.project_id, args.name, args.objective
            )
            print(path)
            return 0
        if args.command == "validate":
            state = load_state(args.state)
            print(
                f"Valid Feature Crew state: {state['project']['id']} revision {state['revision']}"
            )
            return 0
        if args.command == "review-package":
            state = load_state(args.state)
            print(json.dumps(executive_review_package(state, args.artifact), indent=2))
            return 0

        def mutate(operation: Any) -> dict[str, Any]:
            return _load_mutate_save(args.state, operation)

        if args.command == "crew-set":
            state = mutate(
                lambda value: set_crew_member(
                    value,
                    args.role,
                    owner=args.owner,
                    agent_ref=args.agent_ref,
                    clear_agent_ref=args.clear_agent_ref,
                    active=False if args.inactive else None,
                )
            )
        elif args.command == "transition":
            state = mutate(
                lambda value: transition(
                    value, args.to, args.actor, args.reason, override=args.override
                )
            )
        elif args.command == "review":
            state = mutate(
                lambda value: record_review(
                    value,
                    args.artifact,
                    args.role,
                    args.verdict,
                    args.summary,
                    material=not args.non_material,
                )
            )
        elif args.command == "resolve-review":
            state = mutate(
                lambda value: resolve_review(
                    value, args.artifact, args.review_id, args.resolution
                )
            )
        elif args.command == "question":
            state = mutate(
                lambda value: add_question(
                    value,
                    args.id,
                    args.question,
                    args.owner,
                    args.answer_from,
                    args.why,
                    recommendation=args.recommendation,
                    executive_input=args.executive_input,
                    related_to=args.related_to,
                )
            )
        elif args.command == "resolve-question":
            state = mutate(
                lambda value: resolve_question(value, args.id, args.resolution)
            )
        elif args.command == "decision":
            state = mutate(
                lambda value: add_decision(
                    value,
                    args.id,
                    args.decision,
                    args.context,
                    args.rationale,
                    args.owner,
                    alternatives=args.alternative,
                    affected=args.affected,
                )
            )
        elif args.command == "change":
            state = mutate(
                lambda value: record_specification_change(
                    value,
                    args.artifact,
                    args.new_version,
                    args.impact,
                    args.summary,
                    affected=args.affected,
                )
            )
        elif args.command == "approve":
            state = mutate(
                lambda value: approve_artifact(
                    value,
                    args.artifact,
                    args.version,
                    args.approver,
                    notes=args.notes,
                    override=args.override,
                )
            )
        elif args.command == "reject":
            state = mutate(
                lambda value: reject_artifact(
                    value, args.artifact, args.approver, args.reason
                )
            )
        elif args.command == "milestone-add":
            state = mutate(
                lambda value: add_milestone(
                    value,
                    args.id,
                    args.name,
                    args.outcome,
                    args.owner,
                    required=not args.optional,
                )
            )
        elif args.command == "milestone-set":
            state = mutate(
                lambda value: set_milestone_status(
                    value, args.id, args.status, args.comments
                )
            )
        elif args.command == "work-add":
            state = mutate(
                lambda value: add_work_package(
                    value,
                    args.id,
                    args.milestone,
                    args.name,
                    args.owner,
                    args.delivers,
                    source_references=args.source,
                    dependencies=args.dependency,
                    acceptance_criteria=args.acceptance,
                    validation_links=args.validation,
                    required=not args.optional,
                )
            )
        elif args.command == "work-set":
            state = mutate(
                lambda value: set_work_package_status(
                    value, args.id, args.status, args.comments
                )
            )
        elif args.command == "issue-add":
            state = mutate(
                lambda value: add_issue(
                    value,
                    args.id,
                    args.description,
                    args.owner,
                    args.impact,
                    material=not args.non_material,
                    blocker=args.blocker,
                )
            )
        elif args.command == "issue-resolve":
            state = mutate(
                lambda value: resolve_issue(
                    value, args.id, args.resolution, accepted=args.accept
                )
            )
        elif args.command == "risk-add":
            state = mutate(
                lambda value: add_risk(
                    value,
                    args.id,
                    args.description,
                    args.area,
                    args.owner,
                    args.impact,
                    args.mitigation,
                )
            )
        elif args.command == "risk-set":
            state = mutate(lambda value: set_risk_status(value, args.id, args.status))
        elif args.command == "ask-add":
            state = mutate(
                lambda value: add_ask(
                    value,
                    args.id,
                    args.requester,
                    args.target,
                    args.need,
                    args.why,
                    needed_by=args.needed_by,
                )
            )
        elif args.command == "ask-set":
            state = mutate(
                lambda value: set_record_status(value, "asks", args.id, args.status)
            )
        elif args.command == "dependency-add":
            state = mutate(
                lambda value: add_dependency(
                    value,
                    args.id,
                    args.who,
                    args.need,
                    args.delivery_implication,
                    args.risk,
                    needed_by=args.needed_by,
                )
            )
        elif args.command == "dependency-set":
            state = mutate(
                lambda value: set_record_status(
                    value, "dependencies", args.id, args.status
                )
            )
        elif args.command == "artifact-link":
            state = mutate(
                lambda value: add_artifact_link(
                    value,
                    args.id,
                    args.label,
                    args.location,
                    args.kind,
                    args.owner,
                    version=args.version,
                    source_artifact=args.source_artifact,
                    source_version=args.source_version,
                )
            )
        elif args.command == "set-test":
            state = mutate(
                lambda value: set_test_state(
                    value,
                    args.result,
                    args.actor,
                    evidence=args.evidence,
                    unresolved_failures=args.failure,
                    automated_suite_passed=args.automated_suite_passed,
                )
            )
        elif args.command == "agree":
            state = mutate(
                lambda value: set_stakeholder_agreement(
                    value,
                    args.name,
                    args.role,
                    not args.disagree,
                    required=not args.optional,
                    comments=args.comments,
                )
            )
        elif args.command == "declare-done":
            state = mutate(lambda value: declare_done(value, args.actor, args.reason))
        elif args.command == "complete":
            state = mutate(
                lambda value: complete_project(value, args.actor, args.reason)
            )
        elif args.command == "status":
            state = mutate(
                lambda value: record_status(
                    value,
                    args.kind,
                    args.overall,
                    args.summary,
                    changed_facts=args.changed,
                    synchronized_roles=args.role,
                    snapshot_path=args.snapshot_path,
                )
            )
        else:
            parser.error(f"unsupported command {args.command}")
            return 2

        print(
            json.dumps(
                {
                    "project": state["project"]["id"],
                    "phase": state["phase"],
                    "overall_status": state["overall_status"],
                    "revision": state["revision"],
                },
                indent=2,
            )
        )
        return 0
    except StateError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
