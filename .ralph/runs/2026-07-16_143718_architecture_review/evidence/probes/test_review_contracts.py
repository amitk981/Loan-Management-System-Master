"""Read-only architecture-review probes for the five post-1601a903 slices."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[5]


class ReviewContractProbes(unittest.TestCase):
    def test_009d_reconciles_checklist_completion_through_owner_evidence(self):
        source = (
            ROOT
            / "sfpcl_credit/legal_documents/modules/disbursement_readiness.py"
        ).read_text()
        if "borrower_safe_completed_item_ids" not in source:
            self.fail("009D currently trusts ChecklistItem.completion_status directly")

    def test_009d_does_not_filter_open_signature_mismatches_from_readiness(self):
        source = (
            ROOT
            / "sfpcl_credit/legal_documents/modules/disbursement_readiness.py"
        ).read_text()
        if 'if row["verified_by_user_id"] and row["verified_at"]' in source:
            self.fail("an unverified mismatch is excluded and all(empty) becomes true")

    def test_009d_consumes_terminal_security_evidence_not_status_only_rows(self):
        source = (
            ROOT
            / "sfpcl_credit/security_instruments/modules/disbursement_readiness.py"
        ).read_text()
        if "terminal_checklist_evidence" not in source:
            self.fail("009D bypasses the exact evidence/checksum/workflow reconciliation seam")

    def test_009d_uses_loan_account_scope_not_origination_assignment(self):
        source = (
            ROOT / "sfpcl_credit/loans/modules/loan_account_lifecycle.py"
        ).read_text()
        if "evaluate_application_object_access" in source:
            self.fail("readiness authorizes loan access through application origination scope")

    def test_009b2_public_sap_owner_does_not_depend_on_private_finance_owner(self):
        source = (
            ROOT / "sfpcl_credit/sap_workflow/modules/sap_customer_profile.py"
        ).read_text()
        if "sfpcl_credit.finance" in source:
            self.fail("the declared SAP owner is still a forwarding shell over Finance policy/models")

    def test_008m4_required_poa_path_has_an_explicit_governed_decision(self):
        source = (
            ROOT
            / "sfpcl_credit/security_instruments/modules/staff_workspace_actions.py"
        ).read_text()
        if "attorney = None" in source:
            self.fail("required PoA creation is always unreachable and no blocker is projected")

    def test_008m3_upload_and_correction_use_durable_owner_workflows(self):
        source = (
            ROOT / "sfpcl_credit/legal_documents/modules/staff_workspace_actions.py"
        ).read_text()
        if (
            "def _execute_upload_signed_copy" in source
            and "document_services.store_document_upload" in source
            and "def _execute_workspace_record" in source
            and "record_workflow_event" in source
        ):
            self.fail("upload/correction are workspace-local writes with no consumed owner state")


if __name__ == "__main__":
    unittest.main(verbosity=2)
