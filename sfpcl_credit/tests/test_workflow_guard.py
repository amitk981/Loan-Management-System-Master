from django.test import SimpleTestCase

from sfpcl_credit.workflows.guard import (
    InvalidStateTransition,
    MissingTransitionPermission,
    TransitionDefinition,
    UnknownTransitionAction,
    evaluate_transition,
)


class WorkflowGuardTests(SimpleTestCase):
    def test_allowed_transition_returns_next_state_and_metadata(self):
        transition = TransitionDefinition(
            entity_type="loan_application",
            action_code="sanction",
            from_states=frozenset({"draft"}),
            to_state="sanctioned",
            required_permission="tracer.lifecycle.run",
            audit_action="tracer.loan_application.sanctioned",
            workflow_name="tracer",
        )

        result = evaluate_transition(
            current_state="draft",
            requested_action="sanction",
            actor_permissions={"tracer.lifecycle.run"},
            transitions=[transition],
        )

        self.assertEqual(result.next_state, "sanctioned")
        self.assertEqual(result.previous_state, "draft")
        self.assertEqual(result.definition, transition)

    def test_unknown_action_raises_typed_error(self):
        with self.assertRaises(UnknownTransitionAction) as raised:
            evaluate_transition(
                current_state="draft",
                requested_action="missing",
                actor_permissions={"tracer.lifecycle.run"},
                transitions=[],
            )

        self.assertEqual(raised.exception.action_code, "missing")

    def test_invalid_current_state_raises_typed_error(self):
        transition = TransitionDefinition(
            entity_type="loan_application",
            action_code="sanction",
            from_states=frozenset({"draft"}),
            to_state="sanctioned",
            required_permission="tracer.lifecycle.run",
            audit_action="tracer.loan_application.sanctioned",
            workflow_name="tracer",
        )

        with self.assertRaises(InvalidStateTransition) as raised:
            evaluate_transition(
                current_state="sanctioned",
                requested_action="sanction",
                actor_permissions={"tracer.lifecycle.run"},
                transitions=[transition],
            )

        self.assertEqual(raised.exception.current_state, "sanctioned")
        self.assertEqual(raised.exception.allowed_states, frozenset({"draft"}))

    def test_missing_permission_raises_typed_error_before_state_success(self):
        transition = TransitionDefinition(
            entity_type="loan_account",
            action_code="disburse",
            from_states=frozenset({"pending_disbursement"}),
            to_state="active",
            required_permission="tracer.lifecycle.run",
            audit_action="tracer.loan_account.disbursed",
            workflow_name="tracer",
        )

        with self.assertRaises(MissingTransitionPermission) as raised:
            evaluate_transition(
                current_state="pending_disbursement",
                requested_action="disburse",
                actor_permissions=set(),
                transitions=[transition],
            )

        self.assertEqual(raised.exception.required_permission, "tracer.lifecycle.run")

    def test_error_result_does_not_produce_no_op_transition(self):
        transition = TransitionDefinition(
            entity_type="loan_account",
            action_code="close",
            from_states=frozenset({"active"}),
            to_state="closed",
            required_permission="tracer.lifecycle.run",
            audit_action="tracer.loan_account.closed",
            workflow_name="tracer",
        )

        with self.assertRaises(InvalidStateTransition):
            evaluate_transition(
                current_state="closed",
                requested_action="close",
                actor_permissions={"tracer.lifecycle.run"},
                transitions=[transition],
            )
