"""009B2 failing-first probes for SAP delivery and exact completion replay."""

import ast
from dataclasses import replace
from datetime import timedelta
import hashlib
import json
from pathlib import Path
from uuid import uuid4

from django.test import RequestFactory
from django.utils import timezone

from sfpcl_credit.communications.models import Communication, Notification
from sfpcl_credit.sap_workflow.models import SapCustomerCode, SapCustomerProfileRequest
from sfpcl_credit.sap_workflow.errors import SapRequestConflict
from sfpcl_credit.sap_workflow.modules.annexure_storage import EncryptedAnnexureStorage
from sfpcl_credit.sap_workflow.modules.annexure_i import render_annexure_i
from sfpcl_credit.identity.models import AuditLog, Team, UserTeamMembership
from sfpcl_credit.sap_workflow.adapters import (
    ManualSapAdapter,
    SapCustomerProfilePayload,
)
from sfpcl_credit.sap_workflow.modules.sap_customer_profile import (
    get_customer_code_for_member,
    send_request,
)
from sfpcl_credit.tests.test_sap_customer_profile_request_api import (
    SapCustomerProfileRequestApiTests,
)
from sfpcl_credit.workflows.models import WorkflowEvent


class SapCustomerProfileRepairTests(SapCustomerProfileRequestApiTests):
    def setUp(self):
        super().setUp()
        credit_team = Team.objects.create(
            team_code="sap_credit_team", team_name="SAP Credit Team"
        )
        finance_team = Team.objects.create(
            team_code="sap_finance_team", team_name="SAP Finance Team"
        )
        UserTeamMembership.objects.create(user=self.credit_manager, team=credit_team)
        UserTeamMembership.objects.create(user=self.assignee, team=finance_team)

    def test_sent_assignee_reads_exact_retained_workbook_through_delivery_capability(self):
        request_id = self._create_and_send("009b2-delivery-red")
        row = SapCustomerProfileRequest.objects.select_related("excel_file").get(pk=request_id)
        expected = EncryptedAnnexureStorage().read_verified(row.excel_file)

        issued = self.client.post(
            f"/api/v1/sap-customer-profile-requests/{request_id}/annexure-i-delivery-capability/",
            {},
            content_type="application/json",
            HTTP_X_REQUEST_ID="req-009b2-delivery-issue",
            **self._auth(self.assignee),
        )
        self.assertEqual(issued.status_code, 200, issued.content)
        delivery = issued.json()["data"]
        self.assertEqual(delivery["checksum_sha256"], hashlib.sha256(expected).hexdigest())
        self.assertTrue(delivery["delivery_reference"])

        downloaded = self.client.get(
            f"/api/v1/sap-customer-profile-requests/{request_id}/annexure-i/",
            {"capability": delivery["capability"]},
            HTTP_X_REQUEST_ID="req-009b2-delivery-read",
            HTTP_USER_AGENT="009B2 delivery probe",
            REMOTE_ADDR="203.0.113.42",
            **self._auth(self.assignee),
        )
        self.assertEqual(downloaded.status_code, 200, downloaded.content)
        self.assertEqual(downloaded.content, expected)
        self.assertEqual(
            AuditLog.objects.filter(action="sap.annexure_i_downloaded").count(), 1
        )

    def test_reuse_changed_optional_payload_conflicts_without_loser_artifacts(self):
        retained = SapCustomerCode.objects.create(
            member=self.application.member,
            sap_customer_code="REVIEW-RETAINED-CODE",
            sap_vendor_code="REVIEW-RETAINED-VENDOR",
            created_for_loan_application=self.application,
            created_by_user=self.assignee,
            created_at_sap=timezone.now() - timedelta(days=2),
            confirmation_notes="Original retained evidence",
        )
        request_id = self._create_and_send("009b2-replay-red")
        first = self._complete(request_id, sap_customer_code=retained.sap_customer_code)
        self.assertEqual(first.status_code, 200, first.content)
        counts = (
            SapCustomerCode.objects.count(),
            Communication.objects.count(),
            Notification.objects.count(),
            AuditLog.objects.filter(action__startswith="sap.").count(),
            WorkflowEvent.objects.count(),
        )

        changed = self._complete(
            request_id,
            sap_customer_code=retained.sap_customer_code,
            sap_vendor_code=retained.sap_vendor_code,
            created_at_sap=retained.created_at_sap.isoformat(),
            confirmation_notes=retained.confirmation_notes,
        )

        self.assertEqual(changed.status_code, 409, changed.content)
        self.assertEqual(
            (
                SapCustomerCode.objects.count(),
                Communication.objects.count(),
                Notification.objects.count(),
                AuditLog.objects.filter(action__startswith="sap.").count(),
                WorkflowEvent.objects.count(),
            ),
            counts,
        )
        self.assertEqual(
            AuditLog.objects.filter(action="sap.customer_code_reused").count(), 1
        )

    def test_capability_is_one_use_expiring_tamper_safe_and_replaceable(self):
        request_id = self._create_and_send("009b2-capability-matrix")
        first = self._issue(request_id)
        replacement = self._issue(request_id)
        self.assertNotEqual(first["capability"], replacement["capability"])

        stale = self._download(request_id, first["capability"])
        self.assertEqual(stale.status_code, 409, stale.content)
        accepted = self._download(request_id, replacement["capability"])
        self.assertEqual(accepted.status_code, 200, accepted.content)
        reused = self._download(request_id, replacement["capability"])
        self.assertEqual(reused.status_code, 409, reused.content)

        expiring = self._issue(request_id)
        SapCustomerProfileRequest.objects.filter(pk=request_id).update(
            delivery_capability_expires_at=timezone.now() - timedelta(seconds=1)
        )
        expired = self._download(request_id, expiring["capability"])
        self.assertEqual(expired.status_code, 409, expired.content)
        tampered = self._download(request_id, expiring["capability"] + "x")
        self.assertEqual(tampered.status_code, 409, tampered.content)
        self.assertEqual(
            AuditLog.objects.filter(action="sap.annexure_i_downloaded").count(), 1
        )
        self.assertEqual(
            AuditLog.objects.filter(action="sap.annexure_i_download_denied").count(), 4
        )

    def test_capability_denies_cross_user_request_application_and_file(self):
        first_id = self._create_and_send("009b2-capability-scope")
        first = self._issue(first_id)
        outsider = self._user(
            "senior_manager_finance",
            "Other SAP Finance Assignee",
            "finance.sap_request.complete",
        )
        cross_user = self._download(first_id, first["capability"], actor=outsider)
        self.assertEqual(cross_user.status_code, 403, cross_user.content)

        other_application = self._terminal_application(suffix="DELIVERY-SCOPE")
        second_id = self._create_and_send("009b2-capability-other", other_application)
        cross_request = self._download(second_id, first["capability"])
        self.assertEqual(cross_request.status_code, 409, cross_request.content)

        SapCustomerProfileRequest.objects.filter(pk=first_id).update(
            delivery_file_id_snapshot=uuid4()
        )
        cross_file = self._download(first_id, first["capability"])
        self.assertEqual(cross_file.status_code, 409, cross_file.content)
        self.assertEqual(
            AuditLog.objects.filter(action="sap.annexure_i_download_denied").count(), 3
        )

    def test_create_send_complete_read_and_download_audits_freeze_safe_context(self):
        request_id = self._create_and_send("009b2-audit-matrix")
        completed = self._complete(request_id, sap_customer_code="AUDIT-CODE-009B2")
        self.assertEqual(completed.status_code, 200, completed.content)
        decision = get_customer_code_for_member(self.application.member_id)
        self.assertEqual(
            str(decision.customer_code_id),
            completed.json()["data"]["sap_customer_code_id"],
        )
        self.assertEqual(decision.loan_application_id, self.application.pk)
        read = self.client.get(
            f"/api/v1/members/{self.application.member_id}/sap-customer-code/",
            HTTP_X_REQUEST_ID="009b2-audit-read",
            HTTP_USER_AGENT="009B2 audit matrix",
            REMOTE_ADDR="203.0.113.88",
            **self._auth(self.assignee),
        )
        self.assertEqual(read.status_code, 200, read.content)
        capability = self._issue(request_id)
        downloaded = self._download(request_id, capability["capability"])
        self.assertEqual(downloaded.status_code, 200, downloaded.content)

        actions = (
            "finance.sap_customer_code.requested",
            "finance.sap_customer_code.sent",
            "sap.customer_code_created",
            "sap.customer_code_read",
            "sap.annexure_i_capability_issued",
            "sap.annexure_i_downloaded",
        )
        audits = list(AuditLog.objects.filter(action__in=actions).order_by("created_at"))
        self.assertEqual({row.action for row in audits}, set(actions))
        required = {
            "actor_user_id", "actor_type", "actor_role_codes", "actor_team_codes",
            "action", "entity_type", "entity_id", "old_state", "new_state",
            "request_id", "ip_address", "user_agent", "timestamp", "reason", "outcome",
        }
        for audit in audits:
            self.assertTrue(required.issubset(audit.new_value_json), audit.new_value_json)
            self.assertTrue(audit.new_value_json["actor_role_codes"])
            self.assertTrue(audit.new_value_json["actor_team_codes"])
        secret_surface = json.dumps([row.new_value_json for row in audits], sort_keys=True)
        for secret in ("ABCDE1234F", "123412341234", "Village Road", "AUDIT-CODE-009B2"):
            self.assertNotIn(secret, secret_surface)

    def test_current_decision_rejects_changed_send_audit_assignee(self):
        request_id = self._create_and_send("009b3c-send-assignee")
        completed = self._complete(
            request_id, sap_customer_code="CURRENT-EVIDENCE-009B3C"
        )
        self.assertEqual(completed.status_code, 200, completed.content)
        self.assertIsNotNone(get_customer_code_for_member(self.application.member_id))

        send_audit = AuditLog.objects.get(
            action="finance.sap_customer_code.sent",
            entity_type="sap_customer_profile_request",
            entity_id=request_id,
        )
        changed = dict(send_audit.new_value_json)
        changed["assigned_to_user_id"] = str(uuid4())
        send_audit.new_value_json = changed
        send_audit.save(update_fields=["new_value_json"])

        self.assertIsNone(get_customer_code_for_member(self.application.member_id))

    def test_current_decision_rejects_changed_send_communication_recipient(self):
        request_id = self._create_and_send("009b3c-send-communication")
        completed = self._complete(
            request_id, sap_customer_code="SEND-COMMUNICATION-009B3C"
        )
        self.assertEqual(completed.status_code, 200, completed.content)
        self.assertIsNotNone(get_customer_code_for_member(self.application.member_id))

        row = SapCustomerProfileRequest.objects.get(pk=request_id)
        Communication.objects.filter(pk=row.sent_communication_id).update(
            recipient_party_id=uuid4()
        )

        self.assertIsNone(get_customer_code_for_member(self.application.member_id))

    def test_current_decision_rejects_changed_send_audit_request_context(self):
        request_id = self._create_and_send("009b3c-send-context")
        completed = self._complete(request_id, sap_customer_code="SEND-CONTEXT-009B3C")
        self.assertEqual(completed.status_code, 200, completed.content)

        send_audit = AuditLog.objects.get(
            action="finance.sap_customer_code.sent",
            entity_type="sap_customer_profile_request",
            entity_id=request_id,
        )
        changed = dict(send_audit.new_value_json)
        changed["request_id"] = "changed-request-context"
        send_audit.new_value_json = changed
        send_audit.save(update_fields=["new_value_json"])

        self.assertIsNone(get_customer_code_for_member(self.application.member_id))

    def test_current_decision_rejects_rehashed_wrong_completion_role(self):
        request_id = self._create_and_send("009b3c-completion-role")
        completed = self._complete(
            request_id, sap_customer_code="COMPLETION-ROLE-009B3C"
        )
        self.assertEqual(completed.status_code, 200, completed.content)

        completion_audit = AuditLog.objects.get(
            action="sap.customer_code_created",
            entity_type="sap_customer_profile_request",
            entity_id=request_id,
        )
        changed = dict(completion_audit.new_value_json)
        changed["actor_role_codes"] = ["credit_manager"]
        completion_audit.new_value_json = changed
        completion_audit.old_value_json = {
            "request_status": changed["old_state"],
            "evidence_sha256": hashlib.sha256(
                json.dumps(changed, sort_keys=True, separators=(",", ":")).encode()
            ).hexdigest(),
            "request_id": changed["request_id"],
            "timestamp": changed["timestamp"],
        }
        completion_audit.save(update_fields=["new_value_json", "old_value_json"])

        self.assertIsNone(get_customer_code_for_member(self.application.member_id))

    def test_current_decision_rejects_changed_annexure_file_contract(self):
        request_id = self._create_and_send("009b3c-annexure-file")
        completed = self._complete(
            request_id, sap_customer_code="ANNEXURE-FILE-009B3C"
        )
        self.assertEqual(completed.status_code, 200, completed.content)

        row = SapCustomerProfileRequest.objects.get(pk=request_id)
        row.excel_file.mime_type = "application/pdf"
        row.excel_file.save(update_fields=["mime_type"])

        self.assertIsNone(get_customer_code_for_member(self.application.member_id))

    def test_current_decision_rejects_changed_created_code_identity(self):
        request_id = self._create_and_send("009b3c-code-identity")
        completed = self._complete(
            request_id, sap_customer_code="CODE-IDENTITY-009B3C"
        )
        self.assertEqual(completed.status_code, 200, completed.content)

        code = SapCustomerCode.objects.get(
            pk=completed.json()["data"]["sap_customer_code_id"]
        )
        code.created_by_user = self.credit_manager
        code.save(update_fields=["created_by_user"])

        self.assertIsNone(get_customer_code_for_member(self.application.member_id))

    def test_each_safe_send_and_completion_audit_field_is_current_evidence(self):
        request_id = self._create_and_send("009b3c-each-safe-field")
        completed = self._complete(
            request_id, sap_customer_code="EACH-SAFE-FIELD-009B3C"
        )
        self.assertEqual(completed.status_code, 200, completed.content)

        for action in ("finance.sap_customer_code.sent", "sap.customer_code_created"):
            audit = AuditLog.objects.get(
                action=action,
                entity_type="sap_customer_profile_request",
                entity_id=request_id,
            )
            original = dict(audit.new_value_json)
            for field, value in original.items():
                with self.subTest(action=action, field=field):
                    changed = dict(original)
                    changed[field] = self._different_safe_value(value)
                    audit.new_value_json = changed
                    audit.save(update_fields=["new_value_json"])
                    self.assertIsNone(
                        get_customer_code_for_member(self.application.member_id)
                    )
                    audit.new_value_json = original
                    audit.save(update_fields=["new_value_json"])
                    self.assertIsNotNone(
                        get_customer_code_for_member(self.application.member_id)
                    )

    def test_current_decision_requires_singular_linked_send_and_completion_ledgers(self):
        request_id = self._create_and_send("009b3c-singular-ledgers")
        completed = self._complete(
            request_id, sap_customer_code="SINGULAR-LEDGERS-009B3C"
        )
        self.assertEqual(completed.status_code, 200, completed.content)
        decision = lambda: get_customer_code_for_member(self.application.member_id)
        self.assertIsNotNone(decision())

        duplicate_workflow = WorkflowEvent.objects.create(
            workflow_name="SAPCustomerCodeCompleted",
            entity_type="sap_customer_profile_request",
            entity_id=request_id,
            from_state="sent",
            to_state="completed",
            triggered_by_user=self.assignee,
            trigger_reason="sap.customer_code_created",
        )
        self.assertIsNone(decision())
        duplicate_workflow.delete()
        self.assertIsNotNone(decision())

        duplicate_communication = Communication.objects.create(
            related_entity_type="sap_customer_profile_request",
            related_entity_id=request_id,
            recipient_party_type="user",
            channel=Communication.CHANNEL_EMAIL,
            body_snapshot="unrelated sibling",
        )
        self.assertIsNone(decision())
        duplicate_communication.delete()
        self.assertIsNotNone(decision())

        duplicate_task = Notification.objects.create(
            notification_type="sap_customer_profile_request",
            category="Finance",
            title="unrelated sibling",
            related_entity_type="sap_customer_profile_request",
            related_entity_id=request_id,
        )
        self.assertIsNone(decision())
        duplicate_task.delete()
        self.assertIsNotNone(decision())

        row = SapCustomerProfileRequest.objects.get(pk=request_id)
        Notification.objects.filter(pk=row.sent_task_id).update(related_entity_id=uuid4())
        self.assertIsNone(decision())

    def test_adapter_denial_leaves_draft_and_all_send_ledgers_unchanged(self):
        from sfpcl_credit.sap_workflow.adapters import (
            FutureSapAdapter,
            SapCustomerResult,
        )

        class RejectingTransport:
            calls = 0

            def create_customer_profile_request(self, payload, idempotency_key):
                self.calls += 1
                return SapCustomerResult(
                    external_reference="future:rejected",
                    delivery_status="rejected",
                    checksum_sha256=payload.checksum_sha256,
                )

            def get_customer_status(self, external_reference):
                raise AssertionError("status must not be read after rejected delivery")

        created = self._post_request("009b3c-adapter-denial").json()["data"]
        request_id = created["sap_customer_profile_request_id"]
        before = self._sap_ledger_counts()
        transport = RejectingTransport()
        with self.assertRaises(SapRequestConflict):
            send_request(
                actor=self.credit_manager,
                request_id=request_id,
                payload={"remarks": "must roll back"},
                request=RequestFactory().post(
                    "/sap/send/", HTTP_X_REQUEST_ID="009b3c-adapter-denial"
                ),
                adapter=FutureSapAdapter(transport=transport),
            )
        self.assertEqual(transport.calls, 1)
        self.assertEqual(self._sap_ledger_counts(), before)
        row = SapCustomerProfileRequest.objects.get(pk=request_id)
        self.assertEqual(row.request_status, SapCustomerProfileRequest.STATUS_DRAFT)
        self.assertFalse(row.delivery_reference)

    def test_invalid_current_evidence_exposes_no_code_capability_or_workbook(self):
        request_id = self._create_and_send("009b3c-no-exposure")
        issued = self._issue(request_id)
        completed = self._complete(
            request_id, sap_customer_code="NO-EXPOSURE-009B3C"
        )
        self.assertEqual(completed.status_code, 200, completed.content)

        send_audit = AuditLog.objects.get(
            action="finance.sap_customer_code.sent",
            entity_type="sap_customer_profile_request",
            entity_id=request_id,
        )
        changed = dict(send_audit.new_value_json)
        changed["assigned_to_user_id"] = str(uuid4())
        send_audit.new_value_json = changed
        send_audit.save(update_fields=["new_value_json"])

        code_read = self.client.get(
            f"/api/v1/members/{self.application.member_id}/sap-customer-code/",
            **self._auth(self.assignee),
        )
        capability = self.client.post(
            f"/api/v1/sap-customer-profile-requests/{request_id}/"
            "annexure-i-delivery-capability/",
            {},
            content_type="application/json",
            **self._auth(self.assignee),
        )
        workbook = self._download(request_id, issued["capability"])

        self.assertEqual(code_read.status_code, 409, code_read.content)
        self.assertEqual(capability.status_code, 409, capability.content)
        self.assertEqual(workbook.status_code, 409, workbook.content)
        exposed = code_read.content + capability.content + workbook.content
        for value in (
            b"009B3C",
            completed.json()["data"]["sap_customer_code_id"].encode(),
            issued["capability"].encode(),
        ):
            self.assertNotIn(value, exposed)

    def test_manual_fake_and_future_adapters_share_the_public_contract(self):
        from sfpcl_credit.sap_workflow.adapters import (
            FakeSapAdapter,
            FutureSapAdapter,
            SapCustomerResult,
        )

        workbook = render_annexure_i(["contract"] * 13)
        payload = SapCustomerProfilePayload(
            request_id=uuid4(),
            assignee_user_id=uuid4(),
            document_id=uuid4(),
            file_name="annexure.xlsx",
            mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            workbook_bytes=workbook,
            checksum_sha256=hashlib.sha256(workbook).hexdigest(),
        )
        for name, adapter in (
            ("manual", ManualSapAdapter()),
            ("fake", FakeSapAdapter()),
            ("future", FutureSapAdapter(transport=FakeSapAdapter())),
        ):
            with self.subTest(adapter=name, behavior="exact replay"):
                first = adapter.create_customer_profile_request(payload, "same-key")
                self.assertEqual(
                    first,
                    adapter.create_customer_profile_request(payload, "same-key"),
                )
                self.assertEqual(
                    adapter.get_customer_status(first.external_reference).delivery_status,
                    "delivered",
                )
            invalid_payloads = {
                "checksum": replace(payload, checksum_sha256="f" * 64),
                "bytes": replace(
                    payload,
                    workbook_bytes=b"PK-not-an-xlsx",
                    checksum_sha256=hashlib.sha256(b"PK-not-an-xlsx").hexdigest(),
                ),
                "assignee": replace(payload, assignee_user_id=uuid4()),
                "file": replace(payload, document_id=uuid4()),
                "name": replace(payload, file_name="annexure.pdf"),
                "mime": replace(payload, mime_type="application/pdf"),
            }
            for behavior, changed in invalid_payloads.items():
                with self.subTest(adapter=name, behavior=behavior):
                    with self.assertRaises(ValueError):
                        adapter.create_customer_profile_request(changed, "same-key")
            with self.subTest(adapter=name, behavior="changed key"):
                with self.assertRaises(ValueError):
                    adapter.create_customer_profile_request(payload, "changed-key")
            with self.subTest(adapter=name, behavior="bad reference"):
                with self.assertRaises(ValueError):
                    adapter.get_customer_status("malformed reference")

        class CountingTransport(FakeSapAdapter):
            def __init__(self):
                super().__init__()
                self.calls = 0

            def create_customer_profile_request(self, payload, idempotency_key):
                self.calls += 1
                return super().create_customer_profile_request(payload, idempotency_key)

        transport = CountingTransport()
        future = FutureSapAdapter(transport=transport)
        future.create_customer_profile_request(payload, "future-key")
        future.create_customer_profile_request(payload, "future-key")
        self.assertEqual(transport.calls, 1)
        with self.assertRaises(ValueError):
            future.create_customer_profile_request(
                replace(payload, workbook_bytes=b"not-an-xlsx"), "future-key"
            )
        with self.assertRaises(ValueError):
            future.create_customer_profile_request(
                replace(payload, assignee_user_id=uuid4()), "future-key"
            )
        with self.assertRaises(ValueError):
            future.create_customer_profile_request(payload, "changed-future-key")
        self.assertEqual(transport.calls, 1)

        class InvalidResultTransport:
            def __init__(self, result):
                self.result = result

            def create_customer_profile_request(self, payload, idempotency_key):
                return self.result

            def get_customer_status(self, external_reference):
                raise AssertionError("invalid create result must fail first")

        invalid_results = (
            SapCustomerResult(
                external_reference="malformed reference",
                delivery_status="delivered",
                checksum_sha256=payload.checksum_sha256,
            ),
            SapCustomerResult(
                external_reference="future:delivery",
                delivery_status="rejected",
                checksum_sha256=payload.checksum_sha256,
            ),
            SapCustomerResult(
                external_reference="future:delivery",
                delivery_status="delivered",
                checksum_sha256="f" * 64,
            ),
        )
        for result in invalid_results:
            with self.subTest(invalid_result=result):
                with self.assertRaises(ValueError):
                    FutureSapAdapter(
                        transport=InvalidResultTransport(result)
                    ).create_customer_profile_request(payload, "invalid-result-key")

        fake = FakeSapAdapter()
        created = self._post_request("009b2-fake-adapter").json()["data"]
        result = send_request(
            actor=self.credit_manager,
            request_id=created["sap_customer_profile_request_id"],
            payload={"remarks": "fake adapter contract"},
            request=RequestFactory().post(
                "/sap/send/", HTTP_X_REQUEST_ID="009b2-fake-adapter-send"
            ),
            adapter=fake,
        )
        self.assertTrue(result["delivery"]["delivery_reference"].startswith("manual:"))

    def test_sap_owner_has_no_executable_finance_dependency(self):
        root = Path(__file__).resolve().parents[1]
        apps = {"sap_workflow", "finance", "loans", "disbursements"}
        graph = {app: set() for app in apps}
        for app in apps:
            for source in (root / app).rglob("*.py"):
                if "migrations" in source.parts:
                    continue
                tree = ast.parse(source.read_text(), filename=str(source))
                for node in ast.walk(tree):
                    modules = ([alias.name for alias in node.names] if isinstance(node, ast.Import)
                               else [node.module] if isinstance(node, ast.ImportFrom) and node.module else [])
                    for module in modules:
                        parts = module.split(".")
                        if len(parts) > 1 and parts[0] == "sfpcl_credit" and parts[1] in apps:
                            dependency = parts[1]
                            if dependency != app:
                                graph[app].add(dependency)

        def reaches(start, target, visited=frozenset()):
            return start not in visited and (target in graph[start] or any(
                reaches(dependency, target, visited | {start}) for dependency in graph[start]))

        cycles = [f"{source}->{target}" for source in apps for target in graph[source]
                  if reaches(target, source)]
        self.assertEqual(cycles, [], graph)
        self.assertNotIn("finance", graph["sap_workflow"])
        self.assertIn("sap_workflow", graph["finance"])
        for legacy in ("annexure_i.py", "annexure_storage.py", "sap_customer_code.py",
                       "sap_customer_request.py"):
            self.assertFalse((root / "finance" / "modules" / legacy).exists(), legacy)

    def _issue(self, request_id):
        response = self.client.post(
            f"/api/v1/sap-customer-profile-requests/{request_id}/"
            "annexure-i-delivery-capability/",
            {},
            content_type="application/json",
            HTTP_X_REQUEST_ID=f"issue-{request_id}",
            **self._auth(self.assignee),
        )
        self.assertEqual(response.status_code, 200, response.content)
        return response.json()["data"]

    def _download(self, request_id, capability, *, actor=None):
        return self.client.get(
            f"/api/v1/sap-customer-profile-requests/{request_id}/annexure-i/",
            {"capability": capability},
            HTTP_X_REQUEST_ID=f"download-{request_id}",
            HTTP_USER_AGENT="009B2 capability matrix",
            REMOTE_ADDR="203.0.113.42",
            **self._auth(actor or self.assignee),
        )

    @staticmethod
    def _different_safe_value(value):
        if isinstance(value, bool):
            return not value
        if isinstance(value, list):
            return [*value, "changed"]
        if value is None:
            return "changed"
        return f"changed:{value}"

    @staticmethod
    def _sap_ledger_counts():
        return (
            SapCustomerProfileRequest.objects.count(),
            SapCustomerCode.objects.count(),
            Communication.objects.count(),
            Notification.objects.count(),
            AuditLog.objects.count(),
            WorkflowEvent.objects.count(),
        )
