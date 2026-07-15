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
    NotarisationRecord,
    SignatureRecord,
    StampDutyRecord,
)
from sfpcl_credit.legal_documents.modules import document_checklist
from sfpcl_credit.legal_documents.modules import checklist_actions
from sfpcl_credit.processes import document_checklist_actions as checklist_action_process
from sfpcl_credit.applications.models import Witness
from sfpcl_credit.members.models import (
    BankAccount,
    CancelledCheque,
    Member,
    Nominee,
    Shareholding,
)
from sfpcl_credit.security_instruments.models import (
    BlankDatedCheque,
    PowerOfAttorney,
    SecurityPackage,
    SH4ShareTransferForm,
)
from sfpcl_credit.shared.encryption import FieldEncryption
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
        self.nominee = Nominee.objects.create(
            member=self.application.member,
            loan_application_id=self.application.pk,
            nominee_name="Checklist Nominee",
            gender="female",
            pan_encrypted="protected-nominee-pan",
            pan_hash="008k3-nominee-pan",
            aadhaar_encrypted="protected-nominee-aadhaar",
            aadhaar_hash="008k3-nominee-aadhaar",
            kyc_status="verified",
        )
        self.application.nominee = self.nominee
        self.application.save(update_fields=["nominee"])
        borrower_holding = Shareholding.objects.create(
            member=self.application.member,
            folio_number="008K3-BORROWER-FOLIO",
            number_of_shares=100,
            holding_mode="physical",
            pledged_share_count=0,
            available_share_count=100,
            status="active",
        )
        witness_member = Member.objects.create(
            member_number="008K3-WITNESS",
            member_type="individual_farmer",
            legal_name="Checklist Witness",
            display_name="Checklist Witness",
            folio_number="008K3-WITNESS-FOLIO",
            membership_status="active",
            pan_encrypted="protected-witness-pan",
            pan_hash="008k3-witness-pan",
            aadhaar_encrypted="protected-witness-aadhaar",
            aadhaar_hash="008k3-witness-aadhaar",
            kyc_status="verified",
            default_status="no_default",
        )
        witness_holding = Shareholding.objects.create(
            member=witness_member,
            folio_number="008K3-WITNESS-FOLIO",
            number_of_shares=5,
            holding_mode="physical",
            pledged_share_count=0,
            available_share_count=5,
            status="active",
        )
        self.witness = Witness.objects.create(
            loan_application=self.application,
            member=witness_member,
            witness_name=witness_member.legal_name,
            pan_encrypted="protected-witness-pan",
            pan_hash="008k3-witness-pan",
            aadhaar_encrypted="protected-witness-aadhaar",
            aadhaar_hash="008k3-witness-aadhaar",
            verification_shareholding=witness_holding,
            verification_folio_number=witness_holding.folio_number,
            shareholder_verified_flag=True,
            verification_status="verified",
            verified_by_user=self.compliance,
            verified_at=timezone.now(),
        )
        self.borrower_holding = borrower_holding

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

    def test_company_secretary_rejects_status_only_completion_without_actions(self):
        now = timezone.now()
        self.checklist.items.filter(applicable_flag=True, required_flag=True).update(
            completion_status=ChecklistItem.STATUS_COMPLETE,
            verified_by_user=self.compliance,
            verified_at=now,
            remarks="Bulk status without public completion.",
        )
        baseline = self._evidence_counts()

        response = self._post_stage(
            "approve-as-company-secretary",
            self.cs,
            {"comments": "All documents verified and attached."},
        )

        self.assertEqual(response.status_code, 409, response.json())
        self.assertEqual(response.json()["error"]["code"], "CHECKLIST_EVIDENCE_INCOMPLETE")
        self.assertEqual(self._evidence_counts(), baseline)
        self.checklist.refresh_from_db()
        self.assertEqual(self.checklist.checklist_status, DocumentChecklist.STATUS_IN_PROGRESS)
        self.assertIsNone(self.checklist.company_secretary_signature_id)

    def test_company_secretary_reconciles_changed_and_extra_terminal_evidence(self):
        self._complete_all_applicable_items()
        item = self.checklist.items.get(item_code="final_checklist")
        action = ChecklistAction.objects.get(
            checklist_item=item,
            action_type=ChecklistAction.TYPE_ITEM_COMPLETION,
        )
        history = VersionHistory.objects.get(
            versioned_entity_type="checklist_item_completion",
            versioned_entity_id=item.pk,
        )

        def assert_blocked(label):
            baseline = self._evidence_counts()
            response = self._post_stage(
                "approve-as-company-secretary",
                self.cs,
                {"comments": f"Blocked reconciliation: {label}."},
            )
            self.assertEqual(response.status_code, 409, response.json())
            self.assertEqual(
                response.json()["error"]["code"], "CHECKLIST_EVIDENCE_INCOMPLETE"
            )
            self.assertEqual(self._evidence_counts(), baseline)
            self.assertFalse(
                ChecklistAction.objects.filter(
                    document_checklist=self.checklist,
                    action_type=ChecklistAction.TYPE_COMPANY_SECRETARY_APPROVAL,
                ).exists()
            )

        extra = VersionHistory.objects.create(
            versioned_entity_type="checklist_item_completion",
            versioned_entity_id=item.pk,
            version_number="synthetic-extra",
            change_summary="Ambiguous completion history",
            author_user=self.compliance,
            old_value_json={},
            new_value_json={"checklist_action_id": str(action.pk)},
            effective_from=timezone.localdate(),
        )
        assert_blocked("extra history")
        extra.delete()

        original_remarks = item.remarks
        ChecklistItem.objects.filter(pk=item.pk).update(remarks="Changed after completion.")
        assert_blocked("changed remarks")
        ChecklistItem.objects.filter(pk=item.pk).update(remarks=original_remarks)

        original_verifier = item.verified_by_user_id
        ChecklistItem.objects.filter(pk=item.pk).update(verified_by_user=self.cs)
        assert_blocked("changed verifier")
        ChecklistItem.objects.filter(pk=item.pk).update(
            verified_by_user_id=original_verifier
        )

        retained = dict(history.new_value_json)
        history.new_value_json = {
            **retained,
            "approval_case_id": "10000000-0000-0000-0000-000000000099",
        }
        history.save(update_fields=["new_value_json"])
        assert_blocked("stale approval cycle")
        history.new_value_json = retained
        history.save(update_fields=["new_value_json"])

        poa = PowerOfAttorney.objects.get(security_package__loan_application=self.application)
        workflow = WorkflowEvent.objects.get(pk=poa.activation_workflow_event_id)
        workflow.trigger_reason = "forged.workflow"
        workflow.save(update_fields=["trigger_reason"])
        assert_blocked("forged workflow")
        workflow.trigger_reason = "security.poa.activated"
        workflow.save(update_fields=["trigger_reason"])

        stamp = poa.stamp_duty_record
        stamp.stamp_paper_amount = "499.00"
        stamp.save(update_fields=["stamp_paper_amount"])
        assert_blocked("wrong PoA stamp amount")
        stamp.stamp_paper_amount = "500.00"
        stamp.save(update_fields=["stamp_paper_amount"])

        term_sheet = LoanDocument.objects.get(
            loan_application=self.application, document_type="term_sheet"
        )
        wrong_signature = SignatureRecord.objects.create(
            loan_document=term_sheet,
            signer_party_type="borrower",
            signer_party_id=self.second_director.pk,
            signer_name_snapshot="Wrong Borrower",
            signature_method="wet_ink",
            signature_status="signed",
            signature_mismatch_flag=False,
            signed_at=timezone.now(),
            captured_by_user=self.compliance,
        )
        assert_blocked("extra wrong signer")
        wrong_signature.delete()

    def test_above_threshold_term_sheet_requires_two_frozen_directors(self):
        facts = dict(self.case.appraisal_facts_json)
        facts["loan_amounts"] = {
            **facts["loan_amounts"],
            "recommended_amount": "600000.00",
        }
        matrix = {
            **self.case.matrix_projection_json,
            "amount": "600000.00",
            "amount_max": "600000.00",
            "required_director_count": 2,
        }
        required = [
            *self.case.required_approvers_json,
            {
                "role_code": "director",
                "user_id": str(self.second_director.pk),
                "full_name": self.second_director.full_name,
            },
        ]
        self.case.appraisal_facts_json = facts
        self.case.amount = "600000.00"
        self.case.matrix_projection_json = matrix
        self.case.required_approvers_json = required
        self.case.save(
            update_fields=[
                "appraisal_facts_json", "amount", "matrix_projection_json",
                "required_approvers_json",
            ]
        )

        self._complete_all_applicable_items(
            term_directors=(self.director,), expected_term_status=409
        )
        term_sheet = LoanDocument.objects.get(
            loan_application=self.application, document_type="term_sheet"
        )
        item = self.checklist.items.get(item_code="term_sheet")
        self.assertFalse(
            ChecklistAction.objects.filter(
                checklist_item=item,
                action_type=ChecklistAction.TYPE_ITEM_COMPLETION,
            ).exists()
        )
        self._user_signature(term_sheet, self.second_director)
        response = self.client.post(
            f"/api/v1/checklist-items/{item.pk}/complete/",
            {
                "loan_document_id": str(term_sheet.pk),
                "remarks": "Public terminal completion term_sheet.",
            },
            content_type="application/json",
            HTTP_X_REQUEST_ID="above-threshold-two-directors",
            **self.fixture._auth(self.compliance),
        )
        self.assertEqual(response.status_code, 200, response.json())

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

    def test_multi_role_stage_freezes_authorising_role_and_name(self):
        self._complete_all_applicable_items()
        multi_role = self.fixture._user(
            "compliance_team_member", "Multi Role Checklist Secretary"
        )
        multi_role.approval_authority_type = "company_secretary"
        multi_role.save(update_fields=["approval_authority_type"])
        self._grant(
            multi_role,
            "documents.checklist.read",
            "documents.checklist.approve_cs",
        )
        payload = {"comments": "All documents verified and attached."}

        response = self._post_stage(
            "approve-as-company-secretary", multi_role, payload
        )

        self.assertEqual(response.status_code, 200, response.json())
        action = ChecklistAction.objects.get(
            pk=response.json()["data"]["checklist_action_id"]
        )
        self.assertEqual(action.canonical_role_code, "company_secretary")
        self.assertEqual(
            action.actor_user_name_snapshot, "Multi Role Checklist Secretary"
        )
        multi_role.full_name = "Later Renamed User"
        multi_role.approval_authority_type = ""
        multi_role.save(update_fields=["full_name", "approval_authority_type"])
        action.refresh_from_db()
        self.assertEqual(action.canonical_role_code, "company_secretary")
        self.assertEqual(
            action.actor_user_name_snapshot, "Multi Role Checklist Secretary"
        )

    def test_multi_role_completion_freezes_primary_authorising_role(self):
        multi_role = self.fixture._user(
            "company_secretary", "Multi Role Completion Secretary"
        )
        multi_role.approval_authority_type = "compliance_team_member"
        multi_role.save(update_fields=["approval_authority_type"])
        self._grant(multi_role, "documents.checklist.update")
        item = self.checklist.items.get(item_code="final_checklist")
        document = self._current_document("document_checklist")

        response = self.client.post(
            f"/api/v1/checklist-items/{item.pk}/complete/",
            {"loan_document_id": str(document.pk), "remarks": "Role-bound completion."},
            content_type="application/json",
            **self.fixture._auth(multi_role),
        )

        self.assertEqual(response.status_code, 200, response.json())
        action = ChecklistAction.objects.get(
            pk=response.json()["data"]["checklist_action_id"]
        )
        self.assertEqual(action.canonical_role_code, "company_secretary")

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

    def test_synthetic_cheque_version_cannot_complete_item(self):
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
        self.assertEqual(response.status_code, 409, response.json())
        self.assertEqual(response.json()["error"]["code"], "CHECKLIST_EVIDENCE_INCOMPLETE")
        item.refresh_from_db()
        self.assertEqual(item.completion_status, ChecklistItem.STATUS_PENDING)
        self.assertFalse(item.completion_actions.exists())
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

    def test_public_blank_cheque_completion_freezes_exact_source_owned_ids(self):
        document = self._current_document("blank_dated_cheque")
        cancelled = CancelledCheque.objects.create(
            loan_application_id=self.application.pk,
            member=self.application.member,
            document_id=document.document_id,
            account_number_encrypted="protected-cancelled-account",
            account_number_hash="008k3-bank-hash",
            account_number_last4="4321",
            ifsc="HDFC0001234",
            verification_status="verified",
            signature_mismatch_flag=False,
        )
        bank = BankAccount.objects.create(
            owner_party_type="member",
            owner_party_id=self.application.member_id,
            account_holder_name=self.application.member.legal_name,
            account_number_encrypted="protected-bank-account",
            account_number_hash="008k3-bank-hash",
            account_number_last4="4321",
            ifsc="HDFC0001234",
            bank_name="HDFC Bank",
            verification_status="verified",
            cancelled_cheque=cancelled,
            signature_verified_flag=True,
            status="active",
        )
        self.application.bank_account = bank
        self.application.cancelled_cheque = cancelled
        self.application.save(update_fields=["bank_account", "cancelled_cheque"])
        package = SecurityPackage.objects.create(
            loan_application=self.application,
            physical_share_security_required_flag=True,
            poa_required_flag=True,
            blank_cheque_required_flag=True,
            cancelled_cheque_required_flag=True,
        )
        cheque = BlankDatedCheque(
            security_package=package,
            member=self.application.member,
            bank_account=bank,
            cancelled_cheque=cancelled,
            cheque_number_encrypted=FieldEncryption.encrypt(
                "blank_cheque.cheque_number", "123456"
            ),
            cheque_number_hash=FieldEncryption.hash_for_lookup(
                "blank_cheque.cheque_number", "123456"
            ),
            document_id=document.document_id,
            cheque_status="held",
            custody_location="Company Secretary Vault",
            collected_at=timezone.localdate(),
            prepared_by_user=self.compliance,
            custodian_user=self.cs,
        )
        workflow = WorkflowEvent.objects.create(
            workflow_name="blank_dated_cheque",
            entity_type="blank_dated_cheque",
            entity_id=cheque.pk,
            from_state="collected",
            to_state="held",
            triggered_by_user=self.cs,
            trigger_reason="security.blank_cheque.held",
        )
        exact = {
            "loan_application_id": str(self.application.pk),
            "security_package_id": str(package.pk),
            "member_id": str(self.application.member_id),
            "bank_account_id": str(bank.pk),
            "cancelled_cheque_id": str(cancelled.pk),
            "document_id": str(document.document_id),
        }
        cheque.custody_evidence_json = exact
        cheque.custody_workflow_event_id = workflow.pk
        cheque.save()
        item = self.checklist.items.get(item_code="blank_dated_cheque")

        response = self.client.post(
            f"/api/v1/checklist-items/{item.pk}/complete/",
            {
                "loan_document_id": str(document.pk),
                "remarks": "Exact physical cheque custody verified.",
            },
            content_type="application/json",
            HTTP_X_REQUEST_ID="008k3-source-cheque-complete",
            **self.fixture._auth(self.compliance),
        )

        self.assertEqual(response.status_code, 200, response.json())
        action = ChecklistAction.objects.get(pk=response.json()["data"]["checklist_action_id"])
        retained = VersionHistory.objects.get(
            versioned_entity_type="checklist_item_completion",
            new_value_json__checklist_action_id=str(action.pk),
        ).new_value_json
        ledger = retained["consumed_terminal_evidence"]["security_ledger"]
        self.assertEqual(ledger["blank_dated_cheque_id"], str(cheque.pk))
        self.assertEqual(ledger["security_package_id"], str(package.pk))
        self.assertEqual(ledger["bank_account_id"], "[REDACTED]")
        self.assertEqual(ledger["cancelled_cheque_id"], str(cancelled.pk))
        self.assertEqual(ledger["cheque_number"], "******")
        self.assertNotIn("123456", str(retained))

    def _post_stage(self, suffix, actor, payload):
        return self.client.post(
            f"/api/v1/document-checklists/{self.checklist.pk}/{suffix}/",
            payload,
            content_type="application/json",
            **self.fixture._auth(actor),
        )

    def _complete_all_applicable_items(
        self, *, exclude_item_code=None, term_directors=(), expected_term_status=200
    ):
        items = list(
            self.checklist.items.filter(required_flag=True, applicable_flag=True)
            .order_by("display_order")
        )
        documents = {
            item.item_code: self._current_document(
                {
                    "poa": "power_of_attorney",
                    "cdsl_pledge": "cdsl_pledge_evidence",
                    "final_checklist": "document_checklist",
                }.get(item.item_code, item.item_code)
            )
            for item in items
        }
        for code, parties in {
            "poa": ("borrower", "nominee"),
            "tri_party_agreement": ("borrower", "nominee"),
            "sh4": ("borrower", "witness"),
            "term_sheet": ("borrower", "nominee", "cfo"),
            "loan_agreement": ("borrower", "witness"),
        }.items():
            if code in documents:
                for party in parties:
                    self._signature(documents[code], party)
        for director in term_directors:
            self._user_signature(documents["term_sheet"], director)

        package = SecurityPackage.objects.create(
            loan_application=self.application,
            physical_share_security_required_flag=True,
            poa_required_flag=True,
            blank_cheque_required_flag=True,
            cancelled_cheque_required_flag=True,
        )
        if "poa" in documents:
            poa_document = documents["poa"]
            stamp, notary = self._stamp_and_notary(poa_document, "500.00")
            activation = {
                "loan_document_id": str(poa_document.pk),
                "document_file_id": str(poa_document.document_id),
                "document_checksum_sha256": poa_document.renderer_validated_checksum_sha256,
                "stamp_duty_record_id": str(stamp.pk),
                "notarisation_record_id": str(notary.pk),
                "poa_prepared_by_user_id": str(self.compliance.pk),
                "poa_verified_by_user_id": str(self.cs.pk),
            }
            poa = PowerOfAttorney(
                security_package=package,
                borrower_member=self.application.member,
                nominee=self.nominee,
                attorney_user=self.cs,
                purpose_summary="Authorise Company Secretary to initiate share sale on default.",
                loan_document=poa_document,
                stamp_duty_record=stamp,
                notarisation_record=notary,
                execution_status="executed",
                effective_from=timezone.localdate(),
                status="active",
                prepared_by_user=self.compliance,
                verified_by_user=self.cs,
                activation_evidence_json=activation,
            )
            poa.activation_workflow_event_id = self._workflow_event(
                workflow_name="power_of_attorney",
                entity_type="power_of_attorney",
                entity_id=poa.pk,
                actor=self.cs,
                from_state="draft",
                to_state="active",
                reason="security.poa.activated",
            ).pk
            poa.save()
        if "sh4" in documents:
            sh4_document = documents["sh4"]
            custody = {
                "loan_application_id": str(self.application.pk),
                "security_package_id": str(package.pk),
                "member_id": str(self.application.member_id),
                "witness_id": str(self.witness.pk),
                "shareholding_id": str(self.borrower_holding.pk),
                "loan_document_id": str(sh4_document.pk),
                "document_file_id": str(sh4_document.document_id),
                "document_checksum_sha256": sh4_document.renderer_validated_checksum_sha256,
                "sh4_prepared_by_user_id": str(self.compliance.pk),
                "sh4_custodian_user_id": str(self.cs.pk),
            }
            form = SH4ShareTransferForm(
                security_package=package,
                member=self.application.member,
                witness=self.witness,
                shareholding=self.borrower_holding,
                share_count=10,
                loan_document=sh4_document,
                form_status="held_in_custody",
                custody_location="Company Secretary Vault",
                signed_at=timezone.localdate(),
                prepared_by_user=self.compliance,
                custodian_user=self.cs,
                custody_evidence_json=custody,
            )
            form.custody_workflow_event_id = self._workflow_event(
                workflow_name="sh4",
                entity_type="sh4_share_transfer_form",
                entity_id=form.pk,
                actor=self.cs,
                from_state="signed",
                to_state="held_in_custody",
                reason="security.sh4.custodied",
            ).pk
            form.save()
        if "loan_agreement" in documents:
            self._stamp_and_notary(documents["loan_agreement"], "500.00")
        if "blank_dated_cheque" in documents or "cancelled_cheque" in documents:
            self._held_cheque(
                package=package,
                blank_document=documents.get("blank_dated_cheque"),
                cancelled_document=documents.get("cancelled_cheque"),
            )

        for index, item in enumerate(items):
            if item.item_code == exclude_item_code:
                continue
            response = self.client.post(
                f"/api/v1/checklist-items/{item.pk}/complete/",
                {
                    "loan_document_id": str(documents[item.item_code].pk),
                    "remarks": f"Public terminal completion {item.item_code}.",
                },
                content_type="application/json",
                HTTP_X_REQUEST_ID=f"ordered-public-{index}-{item.item_code}",
                **self.fixture._auth(self.compliance),
            )
            expected_status = (
                expected_term_status if item.item_code == "term_sheet" else 200
            )
            self.assertEqual(response.status_code, expected_status, response.json())

    def _signature(self, document, party):
        identities = {
            "borrower": (self.application.member_id, self.application.member.legal_name),
            "nominee": (self.nominee.pk, self.nominee.nominee_name),
            "witness": (self.witness.pk, self.witness.witness_name),
            "cfo": (self.fixture.cfo.pk, self.fixture.cfo.full_name),
        }
        party_id, name = identities[party]
        SignatureRecord.objects.create(
            loan_document=document,
            signer_party_type="user" if party == "cfo" else party,
            signer_party_id=party_id,
            signer_name_snapshot=name,
            signature_method="wet_ink",
            signature_status="signed",
            signature_mismatch_flag=False,
            signed_at=timezone.now(),
            captured_by_user=self.compliance,
        )

    def _user_signature(self, document, user):
        SignatureRecord.objects.create(
            loan_document=document,
            signer_party_type="user",
            signer_party_id=user.pk,
            signer_name_snapshot=user.full_name,
            signature_method="wet_ink",
            signature_status="signed",
            signature_mismatch_flag=False,
            signed_at=timezone.now(),
            captured_by_user=self.compliance,
        )

    def _stamp_and_notary(self, document, amount):
        stamp = StampDutyRecord.objects.create(
            loan_document=document,
            stamp_paper_amount=amount,
            stamp_type="physical",
            stamp_number=f"STAMP-{document.document_type}",
            stamp_purchase_date=timezone.localdate(),
            executed_date=timezone.localdate(),
            prepared_by_user=self.compliance,
            verified_by_user=self.cs,
            status="adequate",
        )
        evidence = DocumentFile.objects.create(
            file_name=f"notary-{document.document_type}.pdf",
            storage_provider="local",
            storage_key=f"notary/{document.pk}.pdf",
            checksum_sha256=f"notary-{document.pk}",
            sensitivity_level="confidential",
        )
        notary = NotarisationRecord.objects.create(
            loan_document=document,
            notary_name="Checklist Notary",
            notary_registration_number=f"NOT-{document.document_type}",
            notarised_date=timezone.localdate(),
            status="completed",
            evidence_document=evidence,
            prepared_by_user=self.compliance,
            verified_by_user=self.cs,
        )
        return stamp, notary

    def _held_cheque(self, *, package, blank_document, cancelled_document):
        file_id = cancelled_document.document_id
        cancelled = CancelledCheque.objects.create(
            loan_application_id=self.application.pk,
            member=self.application.member,
            document_id=file_id,
            account_number_encrypted="protected-account",
            account_number_hash=f"bank-{self.application.pk}",
            account_number_last4="4321",
            ifsc="HDFC0001234",
            verification_status="verified",
            signature_mismatch_flag=False,
        )
        bank = BankAccount.objects.create(
            owner_party_type="member",
            owner_party_id=self.application.member_id,
            account_holder_name=self.application.member.legal_name,
            account_number_encrypted="protected-bank",
            account_number_hash=f"bank-{self.application.pk}",
            account_number_last4="4321",
            ifsc="HDFC0001234",
            bank_name="HDFC Bank",
            verification_status="verified",
            cancelled_cheque=cancelled,
            signature_verified_flag=True,
            status="active",
        )
        self.application.bank_account = bank
        self.application.cancelled_cheque = cancelled
        self.application.save(update_fields=["bank_account", "cancelled_cheque"])
        exact = {
            "loan_application_id": str(self.application.pk),
            "security_package_id": str(package.pk),
            "member_id": str(self.application.member_id),
            "bank_account_id": str(bank.pk),
            "cancelled_cheque_id": str(cancelled.pk),
            "document_id": str(blank_document.document_id),
        }
        cheque = BlankDatedCheque(
            security_package=package,
            member=self.application.member,
            bank_account=bank,
            cancelled_cheque=cancelled,
            cheque_number_encrypted=FieldEncryption.encrypt(
                "blank_cheque.cheque_number", "123456"
            ),
            cheque_number_hash=FieldEncryption.hash_for_lookup(
                "blank_cheque.cheque_number", "123456"
            ),
            document_id=blank_document.document_id,
            cheque_status="held",
            custody_location="Company Secretary Vault",
            collected_at=timezone.localdate(),
            prepared_by_user=self.compliance,
            custodian_user=self.cs,
            custody_evidence_json=exact,
        )
        cheque.custody_workflow_event_id = self._workflow_event(
            workflow_name="blank_dated_cheque",
            entity_type="blank_dated_cheque",
            entity_id=cheque.pk,
            actor=self.cs,
            from_state="collected",
            to_state="held",
            reason="security.blank_cheque.held",
        ).pk
        cheque.save()

    @staticmethod
    def _workflow_event(
        *, workflow_name, entity_type, entity_id, actor, from_state, to_state, reason
    ):
        return WorkflowEvent.objects.create(
            workflow_name=workflow_name,
            entity_type=entity_type,
            entity_id=entity_id,
            from_state=from_state,
            to_state=to_state,
            triggered_by_user=actor,
            trigger_reason=reason,
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
        self._exercise_full_race_matrix()

    def test_five_changed_requests_retain_one_winner_for_item_and_each_stage_repeat(self):
        self._exercise_full_race_matrix()

    def _exercise_full_race_matrix(self):
        helper = FinalDocumentationApprovalApiTests(
            methodName="test_ordered_approval_sequence_retains_meanings_and_exact_replay"
        )
        helper.setUp()
        helper._complete_all_applicable_items(exclude_item_code="final_checklist")
        compliance = helper.compliance
        cs = helper.cs
        credit = helper.credit
        director = helper.second_director
        checklist = helper.checklist
        item = checklist.items.get(item_code="final_checklist")
        document = LoanDocument.objects.get(
            loan_application=helper.application,
            document_type="document_checklist",
        )

        item_results = self._race(
            actor_id=compliance.pk,
            callback=lambda actor, index: checklist_action_process.complete_item(
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
        item_action = ChecklistAction.objects.get(
            checklist_item=item,
            action_type=ChecklistAction.TYPE_ITEM_COMPLETION,
        )
        self._assert_winner_evidence(
            results=item_results,
            action=item_action,
            entity_id=item.pk,
            versioned_entity_type="checklist_item_completion",
            label="item",
        )

        stages = (
            (
                "cs",
                cs,
                checklist_action_process.approve_company_secretary,
                ChecklistAction.TYPE_COMPANY_SECRETARY_APPROVAL,
            ),
            (
                "credit",
                credit,
                checklist_action_process.approve_credit_manager,
                ChecklistAction.TYPE_CREDIT_MANAGER_APPROVAL,
            ),
            (
                "sanction",
                director,
                checklist_action_process.approve_sanction_committee,
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
            self._assert_winner_evidence(
                results=results,
                action=action,
                entity_id=checklist.pk,
                versioned_entity_type="document_checklist_approval",
                label=label,
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

    def _assert_winner_evidence(
        self, *, results, action, entity_id, versioned_entity_type, label
    ):
        winner = next(row for row in results if row[0] == "won")
        winner_request_id = f"008k-{label}-race-{winner[1]}"
        self.assertEqual(str(action.pk), winner[2])
        self.assertEqual(action.request_id, winner_request_id)
        self.assertEqual(
            action.comments,
            (
                f"Concurrent item completion {winner[1]}."
                if label == "item"
                else f"Concurrent {label} approval {winner[1]}."
            ),
        )
        audit = AuditLog.objects.get(
            action=f"document_checklist.{action.action_type}",
            entity_id=entity_id,
        )
        version = VersionHistory.objects.get(
            versioned_entity_type=versioned_entity_type,
            new_value_json__checklist_action_id=str(action.pk),
        )
        self.assertEqual(audit.new_value_json["request_id"], winner_request_id)
        self.assertEqual(version.new_value_json["request_id"], winner_request_id)
        self.assertEqual(audit.actor_user_id, action.actor_user_id)
        self.assertEqual(version.author_user_id, action.actor_user_id)
        self.assertEqual(action.workflow_event.triggered_by_user_id, action.actor_user_id)
        self.assertEqual(
            WorkflowEvent.objects.filter(
                workflow_name="documentation_checklist",
                entity_id=entity_id,
                trigger_reason=action.action_type,
            ).count(),
            1,
        )
        retained = str(audit.new_value_json) + str(version.new_value_json)
        for _, index, _ in results:
            request_id = winner_request_id.rsplit("-", 1)[0] + f"-{index}"
            if request_id != winner_request_id:
                self.assertNotIn(request_id, retained)
                self.assertFalse(
                    ChecklistAction.objects.filter(request_id=request_id).exists()
                )
                self.assertFalse(
                    AuditLog.objects.filter(new_value_json__request_id=request_id).exists()
                )
                self.assertFalse(
                    VersionHistory.objects.filter(
                        new_value_json__request_id=request_id
                    ).exists()
                )
        self.assertEqual(
            WorkflowEvent.objects.filter(
                workflow_name="documentation_checklist",
                entity_id=entity_id,
                trigger_reason=action.action_type,
            ).values_list("workflow_event_id", flat=True).count(),
            1,
        )

    @staticmethod
    def _metadata(label, index):
        return checklist_actions.RequestMetadata(
            request_id=f"008k-{label}-race-{index}",
            ip_address=f"203.0.113.{index + 1}",
            user_agent="008K PostgreSQL Race",
        )
