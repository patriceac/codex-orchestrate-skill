import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "project_state.py"
SPEC = importlib.util.spec_from_file_location("feature_crew_project_state", SCRIPT_PATH)
assert SPEC and SPEC.loader
fc = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(fc)


class FeatureCrewStateTests(unittest.TestCase):
    def new_state(self):
        return fc.new_state("feature-x", "Feature X", "Solve the customer problem")

    def review_all(self, state, artifact):
        for role in fc.ROLES:
            fc.record_review(
                state,
                artifact,
                role,
                "approve",
                f"{role} approves the current version",
            )

    def approve_pm(self, state):
        fc.transition(state, "PM Spec Drafting", "PM", "Begin PM specification")
        fc.transition(
            state, "PM Spec Internal Review", "PM", "Draft is ready for crew review"
        )
        self.review_all(state, "pm_spec")
        fc.transition(
            state, "PM Spec Executive Review", "PM", "Crew recommends approval"
        )
        fc.approve_artifact(state, "pm_spec", "0.1", "Executive Sponsor")

    def approve_design(self, state):
        fc.transition(state, "Dev Design Drafting", "Dev", "Begin design")
        fc.transition(
            state, "Dev Design Internal Review", "Dev", "Design is ready for review"
        )
        self.review_all(state, "dev_design")
        fc.transition(
            state, "Dev Design Executive Review", "Dev", "Crew recommends approval"
        )
        fc.approve_artifact(state, "dev_design", "0.1", "Executive Sponsor")

    def approve_test_plan(self, state):
        fc.transition(state, "Test Plan Drafting", "Test", "Begin test planning")
        fc.transition(
            state, "Test Plan Internal Review", "Test", "Plan is ready for review"
        )
        self.review_all(state, "test_plan")
        fc.transition(
            state, "Test Plan Executive Review", "Test", "Crew recommends approval"
        )
        fc.approve_artifact(state, "test_plan", "0.1", "Executive Sponsor")

    def execution_state(self):
        state = self.new_state()
        self.approve_pm(state)
        self.approve_design(state)
        self.approve_test_plan(state)
        fc.transition(state, "Execution", "PM", "All three specifications are approved")
        return state

    def validation_state(self):
        state = self.execution_state()
        fc.transition(
            state, "Validation", "Test", "Implementation is ready for formal validation"
        )
        return state

    def agree_all(self, state):
        for role in fc.ROLES:
            fc.set_stakeholder_agreement(
                state,
                role,
                role,
                True,
                comments="Agrees the outcome satisfies the approved specifications",
            )

    # FC-01
    def test_01_new_project_creates_required_feature_crew(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir) / "feature-x"
            state_path = fc.initialize_project(
                project_dir, "feature-x", "Feature X", "Solve the customer problem"
            )
            state = fc.load_state(state_path)
            self.assertEqual({item["role"] for item in state["crew"]}, set(fc.ROLES))
            self.assertTrue((project_dir / "artifacts" / "pm-spec.md").is_file())
            self.assertTrue(
                (project_dir / "artifacts" / "dev-design-spec.md").is_file()
            )
            self.assertTrue((project_dir / "artifacts" / "test-plan.md").is_file())
            original_state = state_path.read_text(encoding="utf-8")
            with self.assertRaises(fc.StateError):
                fc.initialize_project(
                    project_dir,
                    "feature-x",
                    "Feature X",
                    "Do not overwrite the existing project",
                )
            self.assertEqual(state_path.read_text(encoding="utf-8"), original_state)

    # FC-02
    def test_02_execution_is_blocked_until_all_three_signoffs(self):
        state = self.new_state()
        allowed, missing = fc.can_begin_execution(state)
        self.assertFalse(allowed)
        self.assertEqual(len(missing), 3)
        with self.assertRaises(fc.StateError):
            fc.transition(state, "Execution", "Dev", "Start coding")
        override_state = self.new_state()
        fc.transition(
            override_state,
            "Execution",
            "Executive Sponsor",
            "Time-critical prototype; skipped-gate risks explicitly accepted",
            override=True,
        )
        self.assertTrue(override_state["decisions"][-1]["executive_override"])
        self.approve_pm(state)
        self.approve_design(state)
        self.approve_test_plan(state)
        allowed, missing = fc.can_begin_execution(state)
        self.assertTrue(allowed)
        self.assertEqual(missing, [])

    # FC-03
    def test_03_dev_can_challenge_pm_spec(self):
        state = self.new_state()
        fc.transition(state, "PM Spec Drafting", "PM", "Begin PM specification")
        fc.transition(state, "PM Spec Internal Review", "PM", "Ready for review")
        review_id = fc.record_review(
            state,
            "pm_spec",
            "Dev",
            "challenge",
            "The stated behavior is infeasible within the required trust boundary",
        )
        self.assertIn(
            review_id, " ".join(fc.artifact_review_readiness(state, "pm_spec"))
        )
        with self.assertRaises(fc.StateError):
            fc.transition(state, "PM Spec Executive Review", "PM", "Ready")

    # FC-04
    def test_04_test_can_challenge_untestable_requirement(self):
        state = self.new_state()
        fc.transition(state, "PM Spec Drafting", "PM", "Begin PM specification")
        fc.transition(state, "PM Spec Internal Review", "PM", "Ready for review")
        fc.record_review(
            state,
            "pm_spec",
            "Test",
            "challenge",
            "FR-001 has no observable or objective acceptance result",
        )
        self.assertTrue(fc.unresolved_material_reviews(state["artifacts"]["pm_spec"]))

    # FC-05
    def test_05_ux_can_challenge_poor_user_flow(self):
        state = self.new_state()
        fc.transition(state, "PM Spec Drafting", "PM", "Begin PM specification")
        fc.transition(state, "PM Spec Internal Review", "PM", "Ready for review")
        fc.record_review(
            state,
            "pm_spec",
            "UX",
            "challenge",
            "The recovery path traps the customer after a partial failure",
        )
        challenge = fc.unresolved_material_reviews(state["artifacts"]["pm_spec"])[0]
        self.assertEqual(challenge["role"], "UX")

    # FC-06
    def test_06_content_can_challenge_ambiguous_language(self):
        state = self.new_state()
        fc.transition(state, "PM Spec Drafting", "PM", "Begin PM specification")
        fc.transition(state, "PM Spec Internal Review", "PM", "Ready for review")
        fc.record_review(
            state,
            "pm_spec",
            "Content",
            "challenge",
            "The command label uses two different terms for the same customer action",
        )
        challenge = fc.unresolved_material_reviews(state["artifacts"]["pm_spec"])[0]
        self.assertEqual(challenge["role"], "Content")

    # FC-07
    def test_07_internal_disagreement_is_resolved_before_executive_review(self):
        state = self.new_state()
        fc.transition(state, "PM Spec Drafting", "PM", "Begin PM specification")
        fc.transition(state, "PM Spec Internal Review", "PM", "Ready for review")
        review_id = fc.record_review(
            state,
            "pm_spec",
            "Dev",
            "challenge",
            "Dependency behavior is contradictory",
        )
        fc.resolve_review(
            state,
            "pm_spec",
            review_id,
            "PM and Dev aligned on explicit fallback behavior",
        )
        fc.record_specification_change(
            state,
            "pm_spec",
            "0.2",
            "minor",
            "Clarified fallback behavior without changing intended scope",
        )
        fc.transition(
            state, "PM Spec Internal Review", "PM", "Updated version is ready"
        )
        self.review_all(state, "pm_spec")
        fc.transition(state, "PM Spec Executive Review", "PM", "Crew is aligned")
        self.assertEqual(state["phase"], "PM Spec Executive Review")
        self.assertEqual(
            fc.unresolved_material_reviews(state["artifacts"]["pm_spec"]), []
        )
        fc.reject_artifact(
            state,
            "pm_spec",
            "Executive Sponsor",
            "Clarify the launch success measure",
        )
        self.assertEqual(state["phase"], "PM Spec Drafting")

    # FC-08
    def test_08_material_executive_question_is_surfaced(self):
        state = self.new_state()
        fc.transition(state, "PM Spec Drafting", "PM", "Begin PM specification")
        fc.transition(state, "PM Spec Internal Review", "PM", "Ready for review")
        self.review_all(state, "pm_spec")
        fc.add_question(
            state,
            "Q-001",
            "Should the initial release include market B?",
            "PM",
            "Executive Sponsor",
            "The choice changes launch scope and localization cost",
            recommendation="Launch market A first",
            executive_input=True,
            related_to="pm_spec:FR-010",
        )
        package = fc.executive_review_package(state, "pm_spec")
        self.assertEqual(package["recommendation"], "Resolve Specific Question")
        self.assertEqual(package["executive_questions"][0]["id"], "Q-001")

    # FC-09
    def test_09_material_pm_change_invalidates_downstream_artifacts(self):
        state = self.execution_state()
        fc.record_specification_change(
            state,
            "pm_spec",
            "2.0",
            "material",
            "Changed a P0 customer behavior",
            affected=["FR-001"],
        )
        self.assertEqual(state["phase"], "PM Spec Drafting")
        self.assertEqual(
            [state["artifacts"][key]["approval"]["status"] for key in fc.ARTIFACT_KEYS],
            ["Not Approved", "Not Approved", "Not Approved"],
        )
        self.assertEqual(fc.pending_status_events(state)[0]["type"], "scope change")
        fc.record_status(
            state,
            "Event-driven",
            "Late",
            "Material PM change returned the project to specification review",
            changed_facts=["CHG-001 invalidated downstream approvals"],
            synchronized_roles=fc.ROLES,
        )
        self.assertEqual(fc.pending_status_events(state), [])

    # FC-10
    def test_10_material_design_change_triggers_design_and_test_rereview(self):
        state = self.execution_state()
        fc.record_specification_change(
            state,
            "dev_design",
            "2.0",
            "material",
            "Changed the persistence architecture and recovery model",
            affected=["DES-003", "T-REC-001"],
        )
        self.assertEqual(state["phase"], "Dev Design Drafting")
        self.assertEqual(
            state["artifacts"]["pm_spec"]["approval"]["status"], "Approved"
        )
        self.assertEqual(
            state["artifacts"]["dev_design"]["approval"]["status"], "Not Approved"
        )
        self.assertEqual(
            state["artifacts"]["test_plan"]["approval"]["status"], "Not Approved"
        )

    # FC-11
    def test_11_status_reports_accept_only_required_overall_states(self):
        for status in ("On Track", "Late", "Blocked"):
            state = self.new_state()
            fc.set_overall_status(state, status)
            self.assertEqual(state["overall_status"], status)
        with self.assertRaises(fc.StateError):
            fc.set_overall_status(self.new_state(), "At Risk")

    # FC-12
    def test_12_milestones_accept_only_approved_statuses(self):
        for index, status in enumerate(fc.MILESTONE_STATUSES):
            state = self.new_state()
            fc.add_milestone(
                state,
                f"M-{index}",
                "Outcome",
                "A meaningful outcome",
                "PM",
                status=status,
            )
            self.assertEqual(state["milestones"][0]["status"], status)
        with self.assertRaises(fc.StateError):
            fc.add_milestone(
                self.new_state(),
                "M-X",
                "Activity",
                "Dev coding",
                "Dev",
                status="In Progress",
            )

    # FC-13
    def test_13_work_packages_accept_only_approved_statuses(self):
        for index, status in enumerate(fc.WORK_PACKAGE_STATUSES):
            state = self.new_state()
            fc.add_milestone(state, "M-1", "Outcome", "A meaningful outcome", "PM")
            fc.add_work_package(
                state,
                f"WP-{index}",
                "M-1",
                "Deliverable",
                "Dev",
                "An independently verifiable deliverable",
                source_references=["FR-001"],
                acceptance_criteria=["Observable result passes"],
                status=status,
            )
            self.assertEqual(state["work_packages"][0]["status"], status)
        with self.assertRaises(fc.StateError):
            state = self.new_state()
            fc.add_milestone(state, "M-1", "Outcome", "A meaningful outcome", "PM")
            fc.add_work_package(
                state,
                "WP-X",
                "M-1",
                "Deliverable",
                "Dev",
                "Deliverable",
                source_references=["FR-001"],
                acceptance_criteria=["Pass"],
                status="On Track",
            )

    # FC-14
    def test_14_passing_automated_suite_alone_does_not_cause_done(self):
        state = self.validation_state()
        fc.set_test_state(
            state,
            "In Progress",
            "Test",
            evidence=["Automated suite passed"],
            automated_suite_passed=True,
        )
        self.agree_all(state)
        with self.assertRaises(fc.StateError):
            fc.declare_done(state, "PM", "Automated suite is green")
        self.assertEqual(state["phase"], "Validation")

    # FC-15
    def test_15_test_passed_and_done_are_separate_states(self):
        state = self.validation_state()
        fc.set_test_state(
            state, "Passed", "Test", evidence=["Approved Test Plan evidence"]
        )
        self.assertEqual(state["test"]["state"], "Passed")
        self.assertEqual(state["phase"], "Validation")

    # FC-16
    def test_16_pm_cannot_declare_done_with_failed_acceptance_criterion(self):
        state = self.validation_state()
        fc.set_test_state(
            state,
            "Failed",
            "Test",
            evidence=["AC-001 failed"],
            unresolved_failures=["AC-001"],
        )
        self.agree_all(state)
        with self.assertRaises(fc.StateError):
            fc.declare_done(state, "PM", "Ship despite failure")

    # FC-17
    def test_17_pm_declares_done_after_test_passed_and_agreement(self):
        state = self.validation_state()
        fc.set_test_state(state, "Passed", "Test", evidence=["All required evidence"])
        self.agree_all(state)
        fc.declare_done(
            state, "PM", "Crew agrees the approved product outcome is achieved"
        )
        self.assertEqual(state["phase"], "Done")
        self.assertEqual(state["lifecycle_history"][-1]["actor"], "PM")

    # FC-18
    def test_18_status_requires_synchronized_feature_crew_facts(self):
        state = self.execution_state()
        with self.assertRaises(fc.StateError):
            fc.record_status(
                state,
                "Heartbeat",
                "On Track",
                "Implementation began",
                changed_facts=["WP-001 started"],
                synchronized_roles=["PM", "Dev", "Test", "UX"],
            )
        status_id = fc.record_status(
            state,
            "Heartbeat",
            "On Track",
            "Implementation began",
            changed_facts=["WP-001 started"],
            synchronized_roles=fc.ROLES,
        )
        self.assertEqual(state["status_history"][-1]["id"], status_id)

    # FC-19
    def test_19_material_blocker_requires_prompt_event_status(self):
        self.assertTrue(fc.requires_event_driven_status("blocker"))
        self.assertTrue(fc.requires_event_driven_status("material test failure"))
        self.assertFalse(fc.requires_event_driven_status("unchanged routine activity"))
        state = self.execution_state()
        fc.add_issue(
            state,
            "ISSUE-001",
            "Required partner endpoint is unavailable",
            "Dev",
            "End-to-end integration cannot proceed",
            blocker=True,
        )
        self.assertEqual(fc.pending_status_events(state)[0]["type"], "blocker")
        with self.assertRaises(fc.StateError):
            fc.record_status(
                state,
                "Heartbeat",
                "Blocked",
                "Routine heartbeat",
                changed_facts=["Partner endpoint unavailable"],
                synchronized_roles=fc.ROLES,
            )
        status_id = fc.record_status(
            state,
            "Event-driven",
            "Blocked",
            "Partner outage blocks end-to-end integration",
            changed_facts=["ISSUE-001 opened"],
            synchronized_roles=fc.ROLES,
        )
        self.assertEqual(fc.pending_status_events(state), [])
        self.assertEqual(state["status_events"][0]["reported_in"], status_id)

    # FC-20
    def test_20_completed_requires_required_milestones_and_validation(self):
        state = self.validation_state()
        fc.add_milestone(
            state, "M-1", "Release ready", "Approved outcome is release ready", "PM"
        )
        fc.add_work_package(
            state,
            "WP-1",
            "M-1",
            "Validated deliverable",
            "Dev",
            "Feature implementation",
            source_references=["FR-001", "DES-001"],
            acceptance_criteria=["T-001 passes"],
            validation_links=["T-001"],
        )
        fc.set_work_package_status(state, "WP-1", "Done")
        fc.set_test_state(state, "Passed", "Test", evidence=["T-001 evidence"])
        self.agree_all(state)
        fc.declare_done(state, "PM", "The intended outcome is achieved")
        with self.assertRaises(fc.StateError):
            fc.complete_project(state, "PM", "Close project")
        fc.set_milestone_status(state, "M-1", "Done")
        fc.complete_project(
            state, "PM", "All required outcomes and validation are complete"
        )
        self.assertEqual(state["phase"], "Completed")
        self.assertEqual(state["overall_status"], "Completed")
        self.assertEqual(fc.validate_state(state), [])


if __name__ == "__main__":
    unittest.main()
