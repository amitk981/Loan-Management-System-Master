# Agent Log Summary

Agent: codex
Exit code: 1
Bytes: 600578
Lines: 10698
SHA-256: 5eae9a259745f27d28e8c24145e6a72278ccb2d4a813a1b72eed20ccb19bec10
Session ID: 019f70e3-d719-7941-b4df-99e7e604b562
Raw retention: operator-local, at most 20 runs or 14 days.

## Final Excerpt

@@ -361,6 +363,7 @@
                 "transfer_success_workflow_event",
                 "transfer_success_loan_status_history",
                 "loan_register_updated_flag",
+                "register_update",
             ]
         )
         row._state.fields_cache["loan_register_update"] = register_update
@@ -502,6 +505,7 @@
         or row.bank_transfer_evidence_document_id is not None
         or row.disbursement_advice_communication_id is not None
         or row.loan_register_updated_flag
+        or row.register_update_id is not None
         or BankTransfer.objects.filter(disbursement=row).exists()
         or LoanStatusHistory.objects.filter(
             loan_account=account, from_status="sanctioned", to_status="active"
@@ -645,6 +649,7 @@
         and row.transfer_success_actor_user_id
         and row.transfer_success_evidence_digest
         and row.loan_register_updated_flag
+        and row.register_update_id == register_update.pk
         and transfer.disbursement_id == row.pk
         and transfer.loan_account_id == row.loan_account_id
         and transfer.related_entity_id == row.pk
diff --git a/sfpcl_credit/disbursements/modules/post_transfer_evidence.py b/sfpcl_credit/disbursements/modules/post_transfer_evidence.py
index 8095096407bb87a36d2e634172b9cee2460a23ce..4fe756d05df595f056b2c1291318c337de7562eb
--- a/sfpcl_credit/disbursements/modules/post_transfer_evidence.py
+++ b/sfpcl_credit/disbursements/modules/post_transfer_evidence.py
@@ -59,6 +59,7 @@
             "transfer_success_audit",
             "transfer_success_workflow_event",
             "transfer_success_loan_status_history",
+            "register_update",
             "loan_register_update",
             "advice_intent",
         )
@@ -86,4 +87,3 @@
         transfer_audit_id=row.transfer_success_audit_id,
         transfer_workflow_event_id=row.transfer_success_workflow_event_id,
     )
-
diff --git a/sfpcl_credit/tests/test_disbursement_transfer_success_api.py b/sfpcl_credit/tests/test_disbursement_transfer_success_api.py
index 5afe3540ce6717b0baa564e8759910d87c367d98..3e23cb2e0092981f9b6e1f463583b4544a18b3dc
--- a/sfpcl_credit/tests/test_disbursement_transfer_success_api.py
+++ b/sfpcl_credit/tests/test_disbursement_transfer_success_api.py
@@ -5,6 +5,7 @@
 from uuid import UUID, uuid4
 
 from django.core.files.uploadedfile import SimpleUploadedFile
+from django.db.models.deletion import ProtectedError
 from django.db import (
     IntegrityError,
     close_old_connections,
@@ -500,6 +501,21 @@
                 transfer_success_action_id=None
             )
 
+    def test_successful_disbursement_protects_its_exact_register_owner_relation(self):
+        accepted = self._post(
+            bank_reference_number="RBL-REGISTER-OWNER-0001",
+            disbursed_at=timezone.now(),
+        )
+        self.assertEqual(accepted.status_code, 200, accepted.content)
+        row = Disbursement.objects.select_related("register_update").get()
+        register = LoanRegisterUpdate.objects.get(disbursement=row)
+
+        self.assertEqual(row.register_update_id, register.pk)
+        with self.assertRaises(ProtectedError), transaction.atomic():
+            register.delete()
+        with self.assertRaises(IntegrityError), transaction.atomic():
+            Disbursement.objects.filter(pk=row.pk).update(register_update=None)
+
     def test_rejected_instruction_and_forged_outcome_fields_are_zero_write(self):
         row = Disbursement.objects.get()
         Disbursement.objects.filter(pk=row.pk).update(authorisation_status="rejected")

ERROR: Selected model is at capacity. Please try a different model.
ERROR: Selected model is at capacity. Please try a different model.
tokens used
143,288
