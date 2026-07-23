import json
from datetime import timedelta

from django.test import Client, TestCase, override_settings
from django.utils import timezone

from sfpcl_credit.identity.models import PortalAccount, Role


@override_settings(
    PORTAL_GRIEVANCE_OWNER_ROLE_CODE="company_secretary",
    PORTAL_GRIEVANCE_TAT_DAYS=7,
)
class PortalCommunicationsApiTests(TestCase):
    password = "PortalCommunications123!"

    def setUp(self):
        from sfpcl_credit.tests.test_grievance_workflow import GrievanceWorkflowApiTests

        owner_fixture = GrievanceWorkflowApiTests(
            "test_authorised_create_generates_one_scoped_reference_and_initial_evidence"
        )
        owner_fixture.setUp()
        self.owner = owner_fixture
        self.client = Client()
        role, _ = Role.objects.get_or_create(
            role_code="borrower_portal_user",
            defaults={
                "role_name": "Borrower Portal User",
                "is_system_role": True,
                "status": "active",
            },
        )
        self.portal_user = owner_fixture._user(
            role, "portal-communications@example.test"
        )
        self.portal_user.set_password(self.password)
        self.portal_user.save(update_fields=["password_hash"])
        self.portal_account = PortalAccount.objects.create(
            member=owner_fixture.member,
            user=self.portal_user,
            status=PortalAccount.STATUS_ACTIVE,
            activated_at=timezone.now(),
        )

    def test_borrower_creates_lists_and_reads_only_own_grievances(self):
        auth = self._portal_auth()
        foreign = self.owner._grievance(
            "GRV-2026-FOREIGN00001",
            member=self.owner._member("GRV-PORTAL-FOREIGN"),
            description="Another member's private complaint.",
        )

        missing = self.client.post(
            "/api/v1/portal/grievances/",
            data=json.dumps({"grievance_category": "other", "subject": ""}),
            content_type="application/json",
            headers=auth,
            HTTP_IDEMPOTENCY_KEY="portal-grievance-missing",
        )
        created = self.client.post(
            "/api/v1/portal/grievances/",
            data=json.dumps(
                {
                    "grievance_category": "other",
                    "subject": "Account statement query",
                    "description": "Please explain the latest statement entry.",
                }
            ),
            content_type="application/json",
            headers=auth,
            HTTP_IDEMPOTENCY_KEY="portal-grievance-create",
        )
        listed = self.client.get("/api/v1/portal/grievances/", headers=auth)
        grievance_id = created.json().get("data", {}).get("grievance_id")
        detail = self.client.get(
            f"/api/v1/portal/grievances/{grievance_id}/", headers=auth
        )
        denied = self.client.get(
            f"/api/v1/portal/grievances/{foreign.pk}/", headers=auth
        )

        self.assertEqual(missing.status_code, 400, missing.content)
        self.assertEqual(created.status_code, 200, created.content)
        self.assertEqual(listed.status_code, 200, listed.content)
        self.assertEqual(detail.status_code, 200, detail.content)
        self.assertEqual(denied.status_code, 404, denied.content)
        self.assertEqual(listed.json()["pagination"]["total_count"], 1)
        self.assertEqual(detail.json()["data"]["subject"], "Account statement query")
        self.assertEqual(
            detail.json()["data"]["resolution_due_date"],
            (timezone.localdate() + timedelta(days=7)).isoformat(),
        )
        serialized = json.dumps(detail.json())
        self.assertNotIn("assigned_to_user_id", serialized)
        self.assertNotIn("internal_notes", serialized)
        self.assertNotIn("Another member", json.dumps(listed.json()))

    def test_borrower_lists_and_marks_only_direct_own_notifications(self):
        from sfpcl_credit.communications.models import Notification

        own = Notification.objects.create(
            notification_type="noc_issued",
            category="closure",
            severity=Notification.SEVERITY_INFO,
            title="Your NOC is ready",
            message="Download the issued NOC from Notices & Letters.",
            recipient_user=self.portal_user,
        )
        role_wide = Notification.objects.create(
            notification_type="internal_role_notice",
            category="internal",
            severity=Notification.SEVERITY_WARNING,
            title="Role-wide internal notice",
            recipient_role_code="borrower_portal_user",
        )
        foreign_user = self.owner._user(
            self.portal_user.primary_role, "foreign-portal-notification@example.test"
        )
        foreign = Notification.objects.create(
            notification_type="repayment_due",
            category="repayment",
            severity=Notification.SEVERITY_WARNING,
            title="Another member's repayment is due",
            recipient_user=foreign_user,
        )
        auth = self._portal_auth()

        listed = self.client.get("/api/v1/portal/notifications/", headers=auth)
        marked = self.client.post(
            f"/api/v1/portal/notifications/{own.pk}/mark-read/",
            data=json.dumps({"read_state_version": own.read_state_version}),
            content_type="application/json",
            headers=auth,
        )
        denied = self.client.post(
            f"/api/v1/portal/notifications/{foreign.pk}/mark-read/",
            data=json.dumps({"read_state_version": foreign.read_state_version}),
            content_type="application/json",
            headers=auth,
        )

        self.assertEqual(listed.status_code, 200, listed.content)
        self.assertEqual(marked.status_code, 200, marked.content)
        self.assertEqual(denied.status_code, 404, denied.content)
        self.assertEqual(listed.json()["pagination"]["total_count"], 1)
        self.assertEqual(listed.json()["data"][0]["notification_id"], str(own.pk))
        self.assertTrue(marked.json()["data"]["read"])
        self.assertNotIn(str(role_wide.pk), json.dumps(listed.json()))
        self.assertNotIn(str(foreign.pk), json.dumps(listed.json()))

    def _portal_auth(self):
        response = self.client.post(
            "/api/v1/portal/auth/login/",
            data={"identifier": self.portal_user.email, "password": self.password},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        return {"Authorization": f"Bearer {response.json()['data']['access_token']}"}


class PortalNoticeAndClosureApiTests(TestCase):
    def setUp(self):
        from sfpcl_credit.tests.test_noc_api import NocIssuanceApiTests

        noc_fixture = NocIssuanceApiTests(
            "test_eligible_full_repayment_closure_issues_one_noc_and_queues_delivery"
        )
        noc_fixture.setUp()
        self.noc_owner = noc_fixture
        issued = noc_fixture._issue("portal-communications-noc")
        self.assertEqual(issued.status_code, 200, issued.content)
        self.client = Client()
        self.portal_user = noc_fixture.fixture._user(
            "borrower_portal_user", "Portal NOC Borrower"
        )
        PortalAccount.objects.create(
            member=noc_fixture.account.member,
            user=self.portal_user,
            status=PortalAccount.STATUS_ACTIVE,
            activated_at=timezone.now(),
        )

    def test_noc_notice_download_and_closure_projection_are_own_only(self):
        from sfpcl_credit.identity.models import AuditLog, User
        from sfpcl_credit.members.models import Member

        auth = self.noc_owner.fixture._auth(self.portal_user)
        notices = self.client.get("/api/v1/portal/notices/", **auth)
        closures = self.client.get("/api/v1/portal/closures/", **auth)

        self.assertEqual(notices.status_code, 200, notices.content)
        self.assertEqual(closures.status_code, 200, closures.content)
        self.assertEqual(notices.json()["pagination"]["total_count"], 1)
        notice = notices.json()["data"][0]
        self.assertEqual(notice["notice_type"], "noc")
        self.assertEqual(notice["related_loan_account_id"], str(self.noc_owner.account.pk))
        self.assertEqual(
            notice["download_url"],
            f"/api/v1/portal/notices/{notice['notice_id']}/download/",
        )
        closure = closures.json()["data"][0]
        self.assertEqual(closure["loan_account_id"], str(self.noc_owner.account.pk))
        self.assertEqual(closure["full_repayment_status"], "confirmed")
        self.assertEqual(closure["closure_review_status"], "complete")
        self.assertEqual(closure["noc_status"], "issued")
        self.assertEqual(closure["noc_download_url"], notice["download_url"])
        self.assertEqual(closure["security_return_status"], "pending")
        self.assertEqual(closure["cdsl_unpledge_status"], "pending")

        downloaded = self.client.get(notice["download_url"], **auth)
        self.assertEqual(downloaded.status_code, 200, downloaded.content)
        self.assertEqual(
            AuditLog.objects.filter(
                action="documents.file.downloaded",
                actor_user=self.portal_user,
                entity_id=self.noc_owner.document.pk,
            ).count(),
            1,
        )

        foreign_member = Member.objects.create(
            member_type="individual_farmer",
            legal_name="Foreign Portal Member",
            display_name="Foreign Portal Member",
            folio_number="FOREIGN-PORTAL-NOC",
            membership_status="active",
            pan_encrypted="foreign-portal-pan",
            pan_hash="foreign-portal-pan-hash",
            kyc_status="verified",
            default_status="no_default",
        )
        foreign_user = User.objects.create(
            full_name="Foreign Portal NOC Borrower",
            email="foreign.portal.noc@example.test",
            status="active",
            primary_role=self.portal_user.primary_role,
        )
        foreign_user.set_password(self.noc_owner.fixture.password)
        foreign_user.save()
        PortalAccount.objects.create(
            member=foreign_member,
            user=foreign_user,
            status=PortalAccount.STATUS_ACTIVE,
            activated_at=timezone.now(),
        )
        foreign_auth = self.noc_owner.fixture._auth(foreign_user)
        foreign_notices = self.client.get("/api/v1/portal/notices/", **foreign_auth)
        foreign_closures = self.client.get("/api/v1/portal/closures/", **foreign_auth)
        foreign_download = self.client.get(notice["download_url"], **foreign_auth)
        self.assertEqual(foreign_notices.json()["data"], [])
        self.assertEqual(foreign_closures.json()["data"], [])
        self.assertEqual(foreign_download.status_code, 404, foreign_download.content)
