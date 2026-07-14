from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from unittest import skipUnless

from django.db import close_old_connections, connection, connections
from django.test import TestCase
from django.test import TransactionTestCase
from django.utils import timezone

from sfpcl_credit.configurations.models import VersionHistory
from sfpcl_credit.documents.models import DocumentFile, DocumentTemplate
from sfpcl_credit.identity.models import AuditLog, Permission, RolePermission
from sfpcl_credit.legal_documents.models import (
    ChecklistAction,
    ChecklistItem,
    DocumentChecklist,
    LoanDocument,
)
from sfpcl_credit.legal_documents.modules import document_checklist
from sfpcl_credit.legal_documents.modules import checklist_actions
from sfpcl_credit.tests.api_contracts import (
    assert_error_envelope,
    assert_success_envelope,
)
from sfpcl_credit.tests import test_document_checklist_api as checklist_fixture
from sfpcl_credit.workflows.models import WorkflowEvent


class FinalDocumentationApprovalApiTests(TestCase):
    def setUp(self):
        self.fixture = checklist_fixture.DocumentChecklistApiTests(
            methodName="test_approved_sanction_creates_ordered_applicability_once_with_evidence"
        )
        self.fixture.setUp()
        self.client = self.fixture.client
        self.application = self.fixture.application
        self.case = self.fixture.case
        self.compliance = self.fixture.actor
        self.director = self.fixture.director
        self.second_director = self.fixture.second_director
        self.cs = self.fixture._user("company_secretary", "Checklist CS")
        self.credit = self.fixture._user("credit_manager", "Checklist Credit")
        self.finance = self.fixture._user(
            "senior_manager_finance", "Checklist Senior Finance"
        )
        for user, permissions in (
            (
                self.compliance,
                ("documents.checklist.update",),
            ),
            (
                self.cs,
                (
                    "documents.checklist.read",
                    "documents.checklist.update",
                    "documents.checklist.approve_cs",
                ),
            ),
            (
                self.credit,
                (
                    "documents.checklist.read",
                    "documents.checklist.approve_credit",
                ),
            ),
            (
                self.director,
                (
                    "documents.checklist.read",
                    "documents.checklist.approve_sanction",
                ),
            ),
            (
                self.second_director,
                (
                    "documents.checklist.read",
                    "documents.checklist.approve_sanction",
                ),
            ),
            (
                self.finance,
                (
                    "documents.checklist.read",
                    "documents.checklist.sign_disbursement_complete",
                ),
            ),
        ):
            self._grant(user, *permissions)
        self.checklist = document_checklist.refresh_for_approved_sanction(
            actor=self.compliance,
            application_id=self.application.pk,
            source_reason="008k_public_fixture",
        )

    def test_item_completion_is_strict_attributable_and_replay_safe(self):
        item = self.checklist.items.get(item_code="final_checklist")
        document = self._current_document("document_checklist")
        payload = {
            "loan_document_id": str(document.pk),
            "remarks": "Final checklist verified and attached.",
        }

        response = self.client.post(
            f"/api/v1/checklist-items/{item.pk}/complete/",
            payload,
            content_type="application/json",
            HTTP_X_REQUEST_ID="complete-final-1",
            **self.fixture._auth(self.compliance),
        )
        self.assertEqual(response.status_code, 200, response.json())
        assert_success_envelope(self, response.json())
        action_id = response.json()["data"]["checklist_action_id"]
        self.assertEqual(response.json()["data"]["entity_type"], "checklist_item")
        self.assertEqual(response.json()["data"]["new_status"], "complete")
        item.refresh_from_db()
        self.assertEqual(item.completion_status, ChecklistItem.STATUS_COMPLETE)
        self.assertEqual(item.loan_document, document)
        self.assertEqual(item.verified_by_user, self.compliance)
        self.assertEqual(ChecklistAction.objects.filter(pk=action_id).count(), 1)
        counts = self._evidence_counts()

        replay = self.client.post(
            f"/api/v1/checklist-items/{item.pk}/complete/",
            payload,
            content_type="application/json",
            HTTP_X_REQUEST_ID="complete-final-replay",
            **self.fixture._auth(self.compliance),
        )
        self.assertEqual(replay.status_code, 200, replay.json())
        self.assertEqual(replay.json()["data"]["checklist_action_id"], action_id)
        self.assertEqual(self._evidence_counts(), counts)

        changed = self.client.post(
            f"/api/v1/checklist-items/{item.pk}/complete/",
            {**payload, "remarks": "Changed completion facts."},
            content_type="application/json",
            **self.fixture._auth(self.compliance),
        )
        self.assertEqual(changed.status_code, 409, changed.json())
        assert_error_envelope(self, changed.json())
        self.assertEqual(changed.json()["error"]["code"], "CHECKLIST_ACTION_CONFLICT")
        self.assertEqual(self._evidence_counts(), counts)

        malformed = self.client.post(
            f"/api/v1/checklist-items/{self.checklist.items.get(item_code='term_sheet').pk}/complete/",
            {"loan_document_id": str(document.pk), "remarks": None, "extra": True},
            content_type="application/json",
            **self.fixture._auth(self.compliance),
        )
        self.assertEqual(malformed.status_code, 400, malformed.json())
        self.assertIn("extra", malformed.json()["error"]["field_errors"])

    def test_ordered_approval_sequence_retains_meanings_and_exact_replay(self):
        self._complete_all_applicable_items()
        cs_payload = {"comments": "All documents verified and attached."}
        credit_payload = {"comments": "Loan limits reviewed and confirmed."}
        sanction_payload = {"comments": "Final approval per matrix."}

        cs = self._post_stage("approve-as-company-secretary", self.cs, cs_payload)
        self.assertEqual(cs.status_code, 200, cs.json())
        cs_action_id = cs.json()["data"]["checklist_action_id"]
        credit = self._post_stage("approve-as-credit-manager", self.credit, credit_payload)
        self.assertEqual(credit.status_code, 200, credit.json())
        sanction = self._post_stage(
            "approve-as-sanction-committee", self.second_director, sanction_payload
        )
        self.assertEqual(sanction.status_code, 200, sanction.json())

        self.checklist.refresh_from_db()
        self.assertEqual(
            self.checklist.checklist_status,
            DocumentChecklist.STATUS_SANCTION_APPROVED,
        )
        self.assertEqual(
            str(self.checklist.company_secretary_signature_id), cs_action_id
        )
        actions = list(
            ChecklistAction.objects.filter(document_checklist=self.checklist)
            .exclude(action_type=ChecklistAction.TYPE_ITEM_COMPLETION)
            .order_by("signed_at")
        )
        self.assertEqual(
            [row.action_type for row in actions],
            [
                ChecklistAction.TYPE_COMPANY_SECRETARY_APPROVAL,
                ChecklistAction.TYPE_CREDIT_MANAGER_APPROVAL,
                ChecklistAction.TYPE_SANCTION_COMMITTEE_APPROVAL,
            ],
        )
        self.assertEqual(
            [row.canonical_role_code for row in actions],
            ["company_secretary", "credit_manager", "director"],
        )
        self.assertEqual(
            [row.meaning for row in actions],
            [
                "all documents verified and attached",
                "loan limits reviewed and confirmed",
                "final approval per matrix",
            ],
        )
        counts = self._evidence_counts()
        replay = self._post_stage("approve-as-company-secretary", self.cs, cs_payload)
        self.assertEqual(replay.status_code, 200, replay.json())
        self.assertEqual(replay.json()["data"]["checklist_action_id"], cs_action_id)
        self.assertEqual(self._evidence_counts(), counts)

    def test_order_and_post_disbursement_blockers_are_zero_write(self):
        self._complete_all_applicable_items()
        baseline = self._evidence_counts()
        out_of_order = self._post_stage(
            "approve-as-credit-manager",
            self.credit,
            {"comments": "Loan limits reviewed and confirmed."},
        )
        self.assertEqual(out_of_order.status_code, 409, out_of_order.json())
        self.assertEqual(
            out_of_order.json()["error"]["code"], "CHECKLIST_APPROVAL_OUT_OF_ORDER"
        )
        self.assertEqual(self._evidence_counts(), baseline)

        blocked = self._post_stage(
            "sign-disbursement-complete",
            self.finance,
            {"comments": "Loan has been disbursed."},
        )
        self.assertEqual(blocked.status_code, 409, blocked.json())
        self.assertEqual(
            blocked.json()["error"]["code"],
            "DISBURSEMENT_EVIDENCE_UNAVAILABLE",
        )
        self.assertEqual(self._evidence_counts(), baseline)
        self.checklist.refresh_from_db()
        self.assertIsNone(self.checklist.loan_account_id)
        self.assertIsNone(self.checklist.senior_manager_finance_signature_id)

    def test_permissions_roles_committee_scope_and_unrelated_ids_fail_closed(self):
        self._complete_all_applicable_items()
        outsider = self.fixture._user("director", "Unrelated Director")
        self._grant(
            outsider,
            "documents.checklist.read",
            "documents.checklist.approve_sanction",
        )
        wrong_role = self.fixture._user("cfo", "Wrong Checklist Role")
        self._grant(wrong_role, "documents.checklist.approve_cs")
        baseline = self._evidence_counts()

        wrong = self._post_stage(
            "approve-as-company-secretary",
            wrong_role,
            {"comments": "Wrong role."},
        )
        self.assertEqual(wrong.status_code, 403, wrong.json())
        unknown = self.client.post(
            "/api/v1/document-checklists/10000000-0000-0000-0000-000000000099/approve-as-sanction-committee/",
            {"comments": "Unrelated."},
            content_type="application/json",
            **self.fixture._auth(outsider),
        )
        self.assertIn(unknown.status_code, {403, 404})
        self.assertNotIn(str(self.application.pk), str(unknown.json()))
        self.assertEqual(self._evidence_counts(), baseline)

    def test_completion_evidence_remains_plaintext_free(self):
        secret_bo = "7654321090123456"
        secret_cheque = "123456"
        VersionHistory.objects.create(
            versioned_entity_type="blank_dated_cheque",
            versioned_entity_id="10000000-0000-0000-0000-000000000088",
            version_number="1",
            change_summary="terminal masked fixture",
            author_user=self.compliance,
            old_value_json={},
            new_value_json={
                "loan_application_id": str(self.application.pk),
                "security_package_id": "10000000-0000-0000-0000-000000000081",
                "cheque_number": "******",
                "cheque_status": "held",
                "prepared_by_user_id": str(self.compliance.pk),
                "custodian_user_id": str(self.cs.pk),
                "custody_workflow_event_id": "10000000-0000-0000-0000-000000000082",
                "cancelled_cheque": {"verification_status": "verified"},
            },
            effective_from=timezone.localdate(),
        )
        item = self.checklist.items.get(item_code="blank_dated_cheque")
        document = self._current_document("blank_dated_cheque")
        response = self.client.post(
            f"/api/v1/checklist-items/{item.pk}/complete/",
            {"loan_document_id": str(document.pk), "remarks": None},
            content_type="application/json",
            **self.fixture._auth(self.compliance),
        )
        self.assertEqual(response.status_code, 200, response.json())
        retained = str(
            list(
                AuditLog.objects.filter(entity_id=item.pk).values(
                    "old_value_json", "new_value_json"
                )
            )
            + list(
                VersionHistory.objects.filter(
                    versioned_entity_type="checklist_item_completion"
                ).values("old_value_json", "new_value_json")
            )
        )
        self.assertNotIn(secret_bo, retained)
        self.assertNotIn(secret_cheque, retained)
        self.assertIn("******", retained)

    def _post_stage(self, suffix, actor, payload):
        return self.client.post(
            f"/api/v1/document-checklists/{self.checklist.pk}/{suffix}/",
            payload,
            content_type="application/json",
            **self.fixture._auth(actor),
        )

    def _complete_all_applicable_items(self):
        now = timezone.now()
        self.checklist.items.filter(applicable_flag=True, required_flag=True).update(
            completion_status=ChecklistItem.STATUS_COMPLETE,
            verified_by_user=self.compliance,
            verified_at=now,
        )

    def _current_document(self, document_type):
        template_file = DocumentFile.objects.create(
            file_name=f"{document_type}.docx",
            storage_provider="local",
            storage_key=f"templates/{document_type}.docx",
            checksum_sha256=f"template-{document_type}",
            sensitivity_level="internal",
        )
        output = DocumentFile.objects.create(
            file_name=f"{document_type}.pdf",
            storage_provider="local",
            storage_key=f"generated/{document_type}.pdf",
            checksum_sha256=f"output-{document_type}",
            sensitivity_level="confidential",
        )
        template = DocumentTemplate.objects.create(
            template_code=f"008k-{document_type}",
            template_name=f"008K {document_type}",
            document_type=document_type,
            borrower_type="individual_farmer",
            template_version="1.0",
            template_file=template_file,
            merge_fields_json=[],
            approval_status="approved",
            effective_from=timezone.localdate(),
        )
        return LoanDocument.objects.create(
            loan_application=self.application,
            document_type=document_type,
            document_category="legal",
            party_required="borrower",
            document_template=template,
            document=output,
            output_format="pdf",
            generation_status="generated",
            execution_status="pending",
            verification_status="verified",
            renderer_contract_version=LoanDocument.RENDERER_CONTRACT_V1,
            renderer_validated_document_id=output.pk,
            renderer_validated_checksum_sha256=output.checksum_sha256,
            verified_by_user=self.cs,
            verified_at=timezone.now(),
        )

    @staticmethod
    def _grant(user, *permission_codes):
        for code in permission_codes:
            permission, _ = Permission.objects.get_or_create(
                permission_code=code,
                defaults={"permission_name": code, "risk_level": "critical"},
            )
            RolePermission.objects.get_or_create(
                role=user.primary_role, permission=permission
            )

    def _evidence_counts(self):
        return {
            "actions": ChecklistAction.objects.count(),
            "audit": AuditLog.objects.filter(
                action__startswith="document_checklist."
            ).count(),
            "versions": VersionHistory.objects.filter(
                versioned_entity_type__in={
                    "checklist_item_completion",
                    "document_checklist_approval",
                }
            ).count(),
            "workflow": WorkflowEvent.objects.filter(
                workflow_name="documentation_checklist"
            ).count(),
        }


@skipUnless(
    connection.vendor == "postgresql",
    "Authoritative final-documentation five-race requires PostgreSQL.",
)
class FinalDocumentationApprovalConcurrencyTests(TransactionTestCase):
    reset_sequences = True

    def test_five_changed_requests_retain_one_winner_for_item_and_each_stage(self):
        fixture = checklist_fixture.DocumentChecklistApiTests(
            methodName="test_approved_sanction_creates_ordered_applicability_once_with_evidence"
        )
        fixture.setUp()
        compliance = fixture.actor
        cs = fixture._user("company_secretary", "Race Checklist CS")
        credit = fixture._user("credit_manager", "Race Checklist Credit")
        director = fixture.second_director
        for user, permissions in (
            (compliance, ("documents.checklist.update",)),
            (cs, ("documents.checklist.approve_cs",)),
            (credit, ("documents.checklist.approve_credit",)),
            (director, ("documents.checklist.approve_sanction",)),
        ):
            FinalDocumentationApprovalApiTests._grant(user, *permissions)
        checklist = document_checklist.refresh_for_approved_sanction(
            actor=compliance,
            application_id=fixture.application.pk,
            source_reason="008k_race_fixture",
        )
        helper = FinalDocumentationApprovalApiTests(
            methodName="test_item_completion_is_strict_attributable_and_replay_safe"
        )
        helper.application = fixture.application
        helper.cs = cs
        item = checklist.items.get(item_code="final_checklist")
        document = helper._current_document("document_checklist")

        item_results = self._race(
            actor_id=compliance.pk,
            callback=lambda actor, index: checklist_actions.complete_item(
                actor=actor,
                checklist_item_id=item.pk,
                payload={
                    "loan_document_id": str(document.pk),
                    "remarks": f"Concurrent item completion {index}.",
                },
                metadata=self._metadata("item", index),
            ),
        )
        self._assert_single_winner(item_results)
        self.assertEqual(
            ChecklistAction.objects.filter(
                checklist_item=item,
                action_type=ChecklistAction.TYPE_ITEM_COMPLETION,
            ).count(),
            1,
        )

        checklist.items.filter(
            applicable_flag=True,
            required_flag=True,
            completion_status=ChecklistItem.STATUS_PENDING,
        ).update(
            completion_status=ChecklistItem.STATUS_COMPLETE,
            verified_by_user=compliance,
            verified_at=timezone.now(),
        )
        stages = (
            (
                "cs",
                cs,
                checklist_actions.approve_company_secretary,
                ChecklistAction.TYPE_COMPANY_SECRETARY_APPROVAL,
            ),
            (
                "credit",
                credit,
                checklist_actions.approve_credit_manager,
                ChecklistAction.TYPE_CREDIT_MANAGER_APPROVAL,
            ),
            (
                "sanction",
                director,
                checklist_actions.approve_sanction_committee,
                ChecklistAction.TYPE_SANCTION_COMMITTEE_APPROVAL,
            ),
        )
        for label, actor, callback, action_type in stages:
            results = self._race(
                actor_id=actor.pk,
                callback=lambda current_actor, index, callback=callback, label=label: callback(
                    actor=current_actor,
                    document_checklist_id=checklist.pk,
                    payload={"comments": f"Concurrent {label} approval {index}."},
                    metadata=self._metadata(label, index),
                ),
            )
            self._assert_single_winner(results)
            action = ChecklistAction.objects.get(
                document_checklist=checklist, action_type=action_type
            )
            self.assertEqual(
                AuditLog.objects.filter(
                    action=f"document_checklist.{action_type}",
                    entity_id=checklist.pk,
                ).count(),
                1,
            )
            self.assertEqual(
                VersionHistory.objects.filter(
                    versioned_entity_type="document_checklist_approval",
                    new_value_json__checklist_action_id=str(action.pk),
                ).count(),
                1,
            )
            self.assertEqual(
                WorkflowEvent.objects.filter(pk=action.workflow_event_id).count(), 1
            )

    def _race(self, *, actor_id, callback):
        gate = Barrier(5)

        def attempt(index):
            close_old_connections()
            try:
                from sfpcl_credit.identity.models import User

                actor = User.objects.get(pk=actor_id)
                gate.wait(timeout=10)
                try:
                    result = callback(actor, index)
                    return "won", index, result["checklist_action_id"]
                except checklist_actions.Conflict as exc:
                    return exc.error_code, index, None
            finally:
                connections["default"].close()

        with ThreadPoolExecutor(max_workers=5) as pool:
            futures = [pool.submit(attempt, index) for index in range(5)]
            return [future.result(timeout=30) for future in futures]

    def _assert_single_winner(self, results):
        self.assertEqual([row[0] for row in results].count("won"), 1, results)
        self.assertEqual(
            [row[0] for row in results].count("CHECKLIST_ACTION_CONFLICT"),
            4,
            results,
        )

    @staticmethod
    def _metadata(label, index):
        return checklist_actions.RequestMetadata(
            request_id=f"008k-{label}-race-{index}",
            ip_address=f"203.0.113.{index + 1}",
            user_agent="008K PostgreSQL Race",
        )
