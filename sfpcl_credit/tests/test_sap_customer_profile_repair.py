"""009B2 failing-first probes for SAP delivery and exact completion replay."""

import ast
from datetime import timedelta
import hashlib
import json
from pathlib import Path
from uuid import uuid4

from django.test import RequestFactory
from django.utils import timezone

from sfpcl_credit.communications.models import Communication, Notification
from sfpcl_credit.sap_workflow.models import SapCustomerCode, SapCustomerProfileRequest
from sfpcl_credit.sap_workflow.modules.annexure_storage import EncryptedAnnexureStorage
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

    def test_manual_and_fake_adapters_share_the_public_contract(self):
        from sfpcl_credit.sap_workflow.adapters import FakeSapAdapter, FutureSapAdapter

        payload = SapCustomerProfilePayload(
            request_id=uuid4(),
            assignee_user_id=uuid4(),
            document_id=uuid4(),
            file_name="annexure.xlsx",
            mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            workbook_bytes=b"PK-valid-test-workbook",
            checksum_sha256=hashlib.sha256(b"PK-valid-test-workbook").hexdigest(),
        )
        manual = ManualSapAdapter()
        first = manual.create_customer_profile_request(payload, "same-key")
        replay = manual.create_customer_profile_request(payload, "same-key")
        self.assertEqual(first, replay)
        self.assertEqual(
            manual.get_customer_status(first.external_reference).delivery_status,
            "delivered",
        )

        fake = FakeSapAdapter()
        fake_first = fake.create_customer_profile_request(payload, "same-key")
        self.assertEqual(fake_first, fake.create_customer_profile_request(payload, "same-key"))
        self.assertEqual(
            fake.get_customer_status(fake_first.external_reference).delivery_status,
            "delivered",
        )
        future = FutureSapAdapter(transport=fake)
        self.assertEqual(
            future.create_customer_profile_request(payload, "same-key"), fake_first
        )

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
