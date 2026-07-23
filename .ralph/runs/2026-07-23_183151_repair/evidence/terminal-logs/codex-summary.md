# Agent Log Summary

Agent: codex
Exit code: 0
Bytes: 651255
Lines: 9889
SHA-256: 8c613e0c276d4aff6267534aa0aa7d24c385ec0ce24526aa4a3ead40a0b0e1d9
Session ID: 019f8f11-89cf-7281-9d29-c2a935ba691f
Raw retention: operator-local, at most 20 runs, 14 days, or 67108864 bytes (the active run is always preserved).

## Final Excerpt

+The changed generic-audit boundary is shared by governed communication callers. Focused
+communications API and dispatcher-job tests passed, and request-present behavior remains unchanged.
+Ralph must still run the independently selected validation lane before integration.
diff --git a/sfpcl_credit/communications/modules/communication_dispatcher.py b/sfpcl_credit/communications/modules/communication_dispatcher.py
index 625baebe575edccaa8efebedff460e63e7f33d7d..a141a42c525f2fa5870dbfc77b2a6bc4d77411a5
--- a/sfpcl_credit/communications/modules/communication_dispatcher.py
+++ b/sfpcl_credit/communications/modules/communication_dispatcher.py
@@ -892,8 +892,8 @@
                 "sent_by_user_id": str(row.sent_by_user_id),
                 "delivery_status": row.delivery_status,
             },
-            ip_address=request_ip(request),
-            user_agent=request_user_agent(request),
+            ip_address=request_ip(request) if request else "",
+            user_agent=request_user_agent(request) if request else "",
         )
 
     @classmethod
diff --git a/sfpcl_credit/tests/test_grievance_workflow.py b/sfpcl_credit/tests/test_grievance_workflow.py
index c501d7c9eaaea2b0cd4a5755a93123998db501bb..50bc2c40a55547de4c65d12400943b01004278c8
--- a/sfpcl_credit/tests/test_grievance_workflow.py
+++ b/sfpcl_credit/tests/test_grievance_workflow.py
@@ -154,6 +154,28 @@
         informed = self.client.get(f'/api/v1/grievances/{grievance.pk}/', **auth)
         self.assertTrue(informed.json()['data']['borrower_informed'])
 
+    def test_service_resolution_without_http_request_retains_blank_transport_audit(self):
+        from sfpcl_credit.communications.models import ContentTemplate
+        from sfpcl_credit.compliance.modules.grievance_workflow import GrievanceWorkflow
+        today = timezone.localdate()
+        ContentTemplate.objects.create(template_code='grievance_resolution_email', template_name='Grievance resolution', template_type='email', language_code='en', audience='borrower', subject_template='Grievance {{grievance_reference}} resolved', body_template='Dear {{member_name}}, grievance {{grievance_reference}} was resolved: {{resolution_summary}}', variables_json=['grievance_reference', 'member_name', 'resolution_summary'], approval_status=ContentTemplate.STATUS_APPROVED, template_versio
+        grievance = self._grievance('GRV-2026-SERVICE00001')
+
+        resolved = GrievanceWorkflow.resolve(
+            actor=self.company_secretary,
+            grievance_id=grievance.pk,
+            payload={'resolution_summary': 'The service-owned resolution was retained.'},
+            idempotency_key='grievance-service-resolution-001',
+        )
+
+        self.assertEqual(resolved['status'], 'resolved')
+        communication_audit = AuditLog.objects.get(
+            action='communications.communication.created',
+            entity_id=resolved['notice_communication_id'],
+        )
+        self.assertEqual(communication_audit.ip_address, '')
+        self.assertEqual(communication_audit.user_agent, '')
+
     def test_scheduler_escalates_overdue_and_recovery_cases_once_without_resolving(self):
         from sfpcl_credit.communications.models import Notification
         from sfpcl_credit.compliance.models import Grievance, GrievanceHistory

tokens used
183,727
Repair completed for `011N-grievance-workflow` and marked **Ready for independent validation**.

The PostgreSQL failure was caused by grievance resolution invoking communication dispatch without an HTTP request. Generic communication audit now preserves the actor and communication snapshot while recording blank IP/user-agent fields for legitimate service callers, instead of dereferencing `request.META`.

Changed:

- [communication_dispatcher.py](/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-23_164006_normal_run/sfpcl_credit/communications/modules/communication_dispatcher.py:875)
- [requestless resolution regression test](/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-23_164006_normal_run/sfpcl_credit/tests/test_grievance_workflow.py:157)

Validation completed:

- Exact PostgreSQL acceptance reproduced RED.
- Minimized requestless-service regression: RED → GREEN.
- PostgreSQL acceptance run 1: exactly 2/2 passed.
- PostgreSQL acceptance run 2, isolated database: exactly 2/2 passed.
- Focused grievance/communications pack: 43 run, 31 passed, 12 expected engine-specific skips.
- Django system check passed.
- No migration drift.
- PostgreSQL environment confirmed: PostgreSQL 14.20.
- `git diff --check` passed.
- No protected or forbidden paths changed.
- No debug instrumentation remains.

Evidence is summarized in [postgresql-acceptance-summary.md](/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-23_164006_normal_run/.ralph/runs/2026-07-23_183151_repair/evidence/postgresql-acceptance-summary.md), and the completed handoff is in [review-packet.md](/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-23_164006_normal_run/.ralph/runs/2026-07-23_183151_repair/review-packet.md:3).

No git add, commit, push, state transition, or mechanical Ralph bookkeeping was performed. The orchestrator should now run independent same-worktree validation.
