import uuid

from django.db import connection
from django.test import Client, TestCase
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from sfpcl_credit.applications.models import LoanApplication
from sfpcl_credit.approvals.models import ApprovalCaseReadScopeGrant
from sfpcl_credit.configurations.models import VersionHistory
from sfpcl_credit.identity.models import AuditLog, Permission, Role, RolePermission, User
from sfpcl_credit.members.models import Member
from sfpcl_credit.reports.registry import run_report
from sfpcl_credit.workflows.models import WorkflowEvent


class AuditExplorerApiTests(TestCase):
    URL = "/api/v1/audit-logs/"
    password = "AuditExplorerPass123!"

    def setUp(self):
        self.client = Client()
        self.role = Role.objects.create(
            role_code="internal_auditor",
            role_name="Internal Auditor",
            is_system_role=True,
            status="active",
        )
        for code in (
            "audit.audit_log.read",
            "audit.workflow_event.read",
            "audit.version_history.read",
        ):
            permission = Permission.objects.create(
                permission_code=code,
                permission_name=code,
                module_name="audit",
                risk_level="high",
            )
            RolePermission.objects.create(role=self.role, permission=permission)
            if code == "audit.audit_log.read":
                self.audit_permission = permission
        ApprovalCaseReadScopeGrant.objects.create(
            role=self.role,
            scope_type=ApprovalCaseReadScopeGrant.SCOPE_AUDIT_READONLY,
        )
        self.auditor = User.objects.create(
            full_name="Ivy Auditor",
            email="audit.explorer@sfpcl.example",
            status="active",
            primary_role=self.role,
        )
        self.auditor.set_password(self.password)
        self.auditor.save(update_fields=["password_hash"])

    def test_application_reference_translates_to_canonical_entity_without_denormalising(self):
        member = Member.objects.create(
            member_type="individual_farmer",
            legal_name="Audit Fixture Member",
            display_name="Audit Fixture Member",
            folio_number="AUD-012D",
            membership_status="active",
            pan_encrypted="fixture-token",
            pan_hash="fixture-hash-audit-012d",
            kyc_status="verified",
            default_status="no_default",
            created_by_user=self.auditor,
        )
        application = LoanApplication.objects.create(
            application_reference_number="APP-AUD-012D",
            member=member,
            borrower_type=member.member_type,
            received_by_user=self.auditor,
            created_by_user=self.auditor,
        )
        matching = AuditLog.objects.create(
            actor_user=self.auditor,
            action="applications.loan_application.created",
            entity_type="loan_application",
            entity_id=application.pk,
        )
        AuditLog.objects.create(
            actor_user=self.auditor,
            action="applications.loan_application.created",
            entity_type="loan_application",
            entity_id=uuid.uuid4(),
        )

        response = self.client.get(
            self.URL,
            {"application_reference": "APP-AUD-012D"},
            **self._auth(),
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(
            [item["audit_log_id"] for item in response.json()["data"]],
            [str(matching.pk)],
        )

    def test_filtered_page_projects_snapshot_fields_and_redacts_sensitive_changes(self):
        entity_id = uuid.uuid4()
        created_at = timezone.now() - timezone.timedelta(minutes=5)
        row = AuditLog.objects.create(
            actor_user=self.auditor,
            action="approvals.exception.approved",
            entity_type="loan_application",
            entity_id=entity_id,
            old_value_json={
                "pan_number": "ABCDE1234F",
                "status": "pending",
            },
            new_value_json={
                "bank_account_number": "123456789012",
                "access_token": "not-a-real-token",
                "request_body": {"unrestricted": "must not escape"},
                "status": "approved",
                "actor_role_codes": ["internal_auditor"],
                "actor_team_codes": ["audit"],
                "reason": "Evidence verified",
                "outcome": "success",
                "request_id": "req-audit-012d",
            },
            ip_address="10.0.0.8",
            user_agent="AuditBrowser/1.0",
            created_at=created_at,
        )
        AuditLog.objects.create(
            actor_user=self.auditor,
            action="members.member.updated",
            entity_type="member",
            entity_id=uuid.uuid4(),
            created_at=created_at - timezone.timedelta(days=2),
        )

        response = self.client.get(
            self.URL,
            {
                "created_from": created_at.date().isoformat(),
                "created_to": created_at.date().isoformat(),
                "actor_user_id": str(self.auditor.pk),
                "role_code": "internal_auditor",
                "entity_type": "loan_application",
                "entity_id": str(entity_id),
                "action": "approvals.exception.approved",
                "module": "approvals",
                "exception": "true",
                "approval": "true",
            },
            **self._auth(),
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["pagination"]["total_count"], 1)
        item = response.json()["data"][0]
        self.assertEqual(item["audit_log_id"], str(row.pk))
        self.assertEqual(item["actor_role_codes"], ["internal_auditor"])
        self.assertEqual(item["actor_team_codes"], ["audit"])
        self.assertEqual(item["reason"], "Evidence verified")
        self.assertEqual(item["outcome"], "success")
        self.assertEqual(item["request_id"], "req-audit-012d")
        self.assertEqual(item["module"], "approvals")
        self.assertEqual(item["linked_record"], {
            "entity_type": "loan_application",
            "entity_id": str(entity_id),
        })
        self.assertEqual(item["old_value"]["pan_number"], "[REDACTED]")
        self.assertEqual(
            item["new_value"]["bank_account_number"],
            "[REDACTED]",
        )
        self.assertEqual(item["new_value"]["access_token"], "[REDACTED]")
        self.assertEqual(item["new_value"]["request_body"], "[REDACTED]")
        self.assertNotIn("ABCDE1234F", str(item))
        self.assertNotIn("123456789012", str(item))

    def test_workflow_page_filters_timeline_and_is_strictly_read_only(self):
        entity_id = uuid.uuid4()
        created_at = timezone.now() - timezone.timedelta(minutes=2)
        matching = WorkflowEvent.objects.create(
            workflow_name="approval_exception",
            entity_type="loan_application",
            entity_id=entity_id,
            from_state="pending",
            to_state="approved",
            triggered_by_user=self.auditor,
            trigger_reason="Exception evidence approved",
            created_at=created_at,
        )
        WorkflowEvent.objects.create(
            workflow_name="member",
            entity_type="member",
            entity_id=uuid.uuid4(),
            from_state="draft",
            to_state="active",
            triggered_by_user=self.auditor,
            created_at=created_at - timezone.timedelta(days=2),
        )

        response = self.client.get(
            "/api/v1/workflow-events/",
            {
                "created_from": created_at.date().isoformat(),
                "created_to": created_at.date().isoformat(),
                "actor_user_id": str(self.auditor.pk),
                "workflow_name": "approval_exception",
                "entity_type": "loan_application",
                "entity_id": str(entity_id),
                "to_state": "approved",
                "exception": "true",
                "approval": "true",
            },
            **self._auth(),
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["pagination"]["total_count"], 1)
        item = response.json()["data"][0]
        self.assertEqual(item["workflow_event_id"], str(matching.pk))
        self.assertEqual(item["module"], "approval_exception")
        self.assertEqual(item["linked_record"]["entity_id"], str(entity_id))

        for method in ("post", "put", "patch", "delete"):
            with self.subTest(method=method):
                blocked = getattr(self.client, method)(
                    "/api/v1/workflow-events/",
                    data={},
                    content_type="application/json",
                    **self._auth(),
                )
                self.assertEqual(blocked.status_code, 405)
        self.assertEqual(WorkflowEvent.objects.count(), 2)

    def test_version_page_filters_approval_history_and_redacts_changes(self):
        entity_id = uuid.uuid4()
        created_at = timezone.now() - timezone.timedelta(minutes=1)
        matching = VersionHistory.objects.create(
            versioned_entity_type="loan_policy_config",
            versioned_entity_id=entity_id,
            version_number="2.0",
            change_summary="Approved policy update",
            author_user=self.auditor,
            approver_user=self.auditor,
            approval_reference="APR-012D",
            approved_at=created_at,
            old_value_json={"aadhaar_number": "123412341234"},
            new_value_json={"cheque_number": "998877"},
            effective_from=created_at.date(),
            created_at=created_at,
        )
        VersionHistory.objects.create(
            versioned_entity_type="content_template",
            versioned_entity_id=uuid.uuid4(),
            version_number="1.0",
            change_summary="Unrelated",
            effective_from=created_at.date(),
            created_at=created_at - timezone.timedelta(days=2),
        )

        response = self.client.get(
            "/api/v1/version-histories/",
            {
                "created_from": created_at.date().isoformat(),
                "created_to": created_at.date().isoformat(),
                "author_user_id": str(self.auditor.pk),
                "versioned_entity_type": "loan_policy_config",
                "versioned_entity_id": str(entity_id),
                "approval": "true",
            },
            **self._auth(),
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["pagination"]["total_count"], 1)
        item = response.json()["data"][0]
        self.assertEqual(item["version_history_id"], str(matching.pk))
        self.assertEqual(item["approval_reference"], "APR-012D")
        self.assertEqual(item["old_value"]["aadhaar_number"], "[REDACTED]")
        self.assertEqual(item["new_value"]["cheque_number"], "[REDACTED]")
        self.assertEqual(item["linked_record"]["entity_id"], str(entity_id))

        for method in ("post", "put", "patch", "delete"):
            with self.subTest(method=method):
                blocked = getattr(self.client, method)(
                    "/api/v1/version-histories/",
                    data={},
                    content_type="application/json",
                    **self._auth(),
                )
                self.assertEqual(blocked.status_code, 405)
        self.assertEqual(VersionHistory.objects.count(), 2)

    def test_restricted_export_handoff_requires_audit_export_and_stays_sanitised(self):
        row = AuditLog.objects.create(
            actor_user=self.auditor,
            action="documents.restricted.downloaded",
            entity_type="loan_application",
            entity_id=uuid.uuid4(),
            new_value_json={"pan_number": "ABCDE1234F", "outcome": "success"},
        )
        export_permission = Permission.objects.create(
            permission_code="reports.export",
            permission_name="Export reports",
            module_name="reports",
            risk_level="high",
        )
        RolePermission.objects.create(role=self.role, permission=export_permission)
        payload = {
            "report_code": "audit-log-export",
            "format": "csv",
            "filters": {"entity_id": str(row.entity_id)},
        }

        denied = self.client.post(
            "/api/v1/reports/exports/",
            payload,
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="audit-export-denied-012d",
            **self._auth(),
        )
        self.assertEqual(denied.status_code, 403, denied.content)

        audit_export_permission = Permission.objects.create(
            permission_code="audit.export",
            permission_name="Export audit logs",
            module_name="audit",
            risk_level="critical",
        )
        RolePermission.objects.create(role=self.role, permission=audit_export_permission)
        accepted = self.client.post(
            "/api/v1/reports/exports/",
            payload,
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="audit-export-accepted-012d",
            **self._auth(),
        )
        self.assertEqual(accepted.status_code, 202, accepted.content)

        rows, pagination = run_report(
            report_code="audit-log-export",
            actor=self.auditor,
            query_params={"entity_id": str(row.entity_id), "page": "1", "page_size": "20"},
        )
        self.assertEqual(pagination["total_count"], 1)
        self.assertEqual(rows[0]["new_value"]["pan_number"], "[REDACTED]")
        self.assertNotIn("ABCDE1234F", str(rows))

    def test_permission_holder_cannot_read_another_actors_unscoped_record(self):
        scoped_role = Role.objects.create(
            role_code="scoped_audit_reader",
            role_name="Scoped Audit Reader",
            status="active",
        )
        RolePermission.objects.create(
            role=scoped_role,
            permission=self.audit_permission,
        )
        scoped_reader = User.objects.create(
            full_name="Scoped Reader",
            email="scoped.reader@sfpcl.example",
            primary_role=scoped_role,
        )
        scoped_reader.set_password(self.password)
        scoped_reader.save(update_fields=["password_hash"])
        own = AuditLog.objects.create(
            actor_user=scoped_reader,
            action="audit.self.reviewed",
            entity_type="unscoped_record",
            entity_id=uuid.uuid4(),
        )
        AuditLog.objects.create(
            actor_user=self.auditor,
            action="audit.other.reviewed",
            entity_type="unscoped_record",
            entity_id=uuid.uuid4(),
        )

        response = self.client.get(
            self.URL,
            {"entity_type": "unscoped_record"},
            **self._auth_for(scoped_reader),
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(
            [item["audit_log_id"] for item in response.json()["data"]],
            [str(own.pk)],
        )

    def test_large_page_has_bounded_queries_and_stable_tie_break_order(self):
        created_at = timezone.now() - timezone.timedelta(minutes=3)
        rows = [
            AuditLog.objects.create(
                actor_user=self.auditor,
                action="audit.performance.read",
                entity_type="performance_fixture",
                entity_id=uuid.uuid4(),
                created_at=created_at,
            )
            for _ in range(40)
        ]
        headers = self._auth()

        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(
                self.URL,
                {"entity_type": "performance_fixture", "page_size": "20"},
                **headers,
            )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertLessEqual(len(queries), 8)
        expected = sorted((str(row.pk) for row in rows), reverse=True)[:20]
        self.assertEqual(
            [item["audit_log_id"] for item in response.json()["data"]],
            expected,
        )
        self.assertTrue(response.json()["pagination"]["has_next"])

    def test_invalid_date_boolean_and_all_mutation_methods_are_rejected(self):
        invalid_date = self.client.get(
            self.URL,
            {"created_from": "2026-99-99"},
            **self._auth(),
        )
        invalid_boolean = self.client.get(
            self.URL,
            {"approval": "sometimes"},
            **self._auth(),
        )
        self.assertEqual(invalid_date.status_code, 400)
        self.assertIn("created_from", invalid_date.json()["error"]["field_errors"])
        self.assertEqual(invalid_boolean.status_code, 400)
        self.assertIn("approval", invalid_boolean.json()["error"]["field_errors"])
        headers = self._auth()
        before = AuditLog.objects.count()
        for method in ("post", "put", "patch", "delete"):
            with self.subTest(method=method):
                response = getattr(self.client, method)(
                    self.URL,
                    data={},
                    content_type="application/json",
                    **headers,
                )
                self.assertEqual(response.status_code, 405)
        self.assertEqual(AuditLog.objects.count(), before)

    def test_internal_auditor_requires_active_scope_for_all_three_resources(self):
        ApprovalCaseReadScopeGrant.objects.filter(role=self.role).update(status="inactive")
        headers = self._auth()

        for path in (
            "/api/v1/audit-logs/",
            "/api/v1/workflow-events/",
            "/api/v1/version-histories/",
        ):
            with self.subTest(path=path):
                response = self.client.get(path, **headers)
                self.assertEqual(response.status_code, 403, response.content)

    def _auth(self):
        return self._auth_for(self.auditor)

    def _auth_for(self, user):
        response = self.client.post(
            "/api/v1/auth/login/",
            {"email": user.email, "password": self.password},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        return {
            "HTTP_AUTHORIZATION": (
                f"Bearer {response.json()['data']['access_token']}"
            )
        }
