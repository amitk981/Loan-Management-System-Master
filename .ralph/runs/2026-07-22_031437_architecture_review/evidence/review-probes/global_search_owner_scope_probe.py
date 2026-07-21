"""Independent executable probes for the carried global-search authority root."""

from django.utils import timezone

from sfpcl_credit.identity.models import Permission, RolePermission
from sfpcl_credit.members.models import BankAccount, CancelledCheque
from sfpcl_credit.security_instruments.models import BlankDatedCheque, SecurityPackage
from sfpcl_credit.shared.encryption import FieldEncryption
from sfpcl_credit.tests.test_global_search_api import GlobalSearchApiTests


class GlobalSearchOwnerScopeProbe(GlobalSearchApiTests):
    def _grant(self, code):
        permission = Permission.objects.create(
            permission_code=code,
            permission_name=code,
            module_name="security",
            risk_level="critical",
        )
        RolePermission.objects.create(
            role=self.user.primary_role,
            permission=permission,
        )

    def test_security_input_rejects_record_outside_canonical_stage4_scope(self):
        self._grant("security.blank_cheque.manage")
        package = SecurityPackage.objects.create(
            loan_application=self.application,
            blank_cheque_required_flag=True,
            cancelled_cheque_required_flag=True,
        )
        cancelled = CancelledCheque.objects.create(
            loan_application_id=self.application.pk,
            member=self.member,
            document_id=self.application_document.document_file_id,
            account_number_encrypted="review-cancelled-account",
            account_number_hash="review-cancelled-account-hash",
            account_number_last4="7788",
            ifsc="TEST0000001",
            verification_status="verified",
        )
        raw_cheque = "CHEQUE-OUT-OF-SCOPE-001"
        BlankDatedCheque.objects.create(
            security_package=package,
            member=self.member,
            bank_account=BankAccount.objects.get(owner_party_id=self.member.pk),
            cancelled_cheque=cancelled,
            cheque_number_encrypted=FieldEncryption.encrypt(
                "blank_cheque.cheque_number", raw_cheque
            ),
            cheque_number_hash=FieldEncryption.hash_for_lookup(
                "blank_cheque.cheque_number", raw_cheque
            ),
            cheque_status="collected",
            collected_at=timezone.localdate(),
            prepared_by_user=self.user,
        )
        self.assertNotEqual(self.application.application_status, "approved_by_sanction")

        response = self._search(raw_cheque)

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(
            response.json()["data"]["groups"]["members"]["pagination"]["total_count"],
            0,
            "FAIL: security input disclosed an owner outside canonical Stage-4 scope.",
        )

    def test_unprefixed_sap_code_uses_the_sap_owner(self):
        from sfpcl_credit.sap_workflow.models import SapCustomerCode

        SapCustomerCode.objects.update(sap_customer_code="CUST000123")

        response = self._search("CUST000123")

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(
            response.json()["data"]["groups"]["members"]["pagination"]["total_count"],
            1,
            "FAIL: a valid unprefixed SAP code never reaches the canonical SAP search owner.",
        )
