import uuid

from django.test import Client, TestCase

from sfpcl_credit.communications.models import (
    Communication,
    CommunicationDeliveryJob,
    ContentTemplate,
)
from sfpcl_credit.communications.adapters import FakeEmailDeliveryAdapter
from sfpcl_credit.communications.modules.communication_dispatcher import (
    CommunicationDispatcher,
)
from sfpcl_credit.identity.models import AuditLog, Permission, Role, RolePermission, User
from sfpcl_credit.processes.communication_delivery import execute_communication_job
from sfpcl_credit.tests.api_contracts import (
    assert_error_envelope,
    assert_pagination_shape,
    assert_success_envelope,
)


COMMUNICATIONS_URL = "/api/v1/communications/"
COMMUNICATION_SEND_URL = "/api/v1/communications/send/"
COMMUNICATION_READ_PERMISSION = "communications.communication.read"
COMMUNICATION_SEND_PERMISSION = "communications.communication.send"


class CommunicationApiTests(TestCase):
    """003I: protected communication adapter shell over communications records."""

    def setUp(self):
        self.client = Client()
        self.role = Role.objects.create(
            role_code="communication_sender",
            role_name="Communication Sender",
            is_system_role=True,
            status="active",
        )
        read_permission = Permission.objects.create(
            permission_code=COMMUNICATION_READ_PERMISSION,
            permission_name="Read communications",
            module_name="communications",
            risk_level="medium",
        )
        send_permission = Permission.objects.create(
            permission_code=COMMUNICATION_SEND_PERMISSION,
            permission_name="Send communication snapshots",
            module_name="communications",
            risk_level="medium",
        )
        RolePermission.objects.create(role=self.role, permission=read_permission)
        RolePermission.objects.create(role=self.role, permission=send_permission)
        self.user = User.objects.create(
            full_name="Cora Communicator",
            email="cora.communicator@sfpcl.example",
            status="active",
            primary_role=self.role,
        )
        self.user.set_password("SenderPass123!")
        self.user.save()

        self.read_only_role = Role.objects.create(
            role_code="communication_reader",
            role_name="Communication Reader",
            is_system_role=True,
            status="active",
        )
        RolePermission.objects.create(role=self.read_only_role, permission=read_permission)
        self.read_only_user = User.objects.create(
            full_name="Ravi Reader",
            email="ravi.communications@sfpcl.example",
            status="active",
            primary_role=self.read_only_role,
        )
        self.read_only_user.set_password("ReaderPass123!")
        self.read_only_user.save()

        self.plain_role = Role.objects.create(
            role_code="communication_plain",
            role_name="Communication Plain",
            is_system_role=True,
            status="active",
        )
        self.plain_user = User.objects.create(
            full_name="Priya Plain",
            email="priya.communications@sfpcl.example",
            status="active",
            primary_role=self.plain_role,
        )
        self.plain_user.set_password("PlainPass123!")
        self.plain_user.save()

        self.related_entity_id = uuid.uuid4()
        self.recipient_party_id = uuid.uuid4()
        self.template = ContentTemplate.objects.create(
            template_code="loan_sanction_email_v1",
            template_name="Loan Sanction Email",
            template_type="email",
            language_code="en",
            audience="borrower",
            subject_template="Sanction {{application_reference_number}}",
            body_template=(
                "Dear {{borrower_name}}, your loan {{application_reference_number}} "
                "is sanctioned."
            ),
            variables_json=["application_reference_number", "borrower_name"],
            approval_status=ContentTemplate.STATUS_APPROVED,
            template_version="1.0",
            effective_from="2026-01-01",
            effective_to="2026-12-31",
        )

    def test_source_dispatcher_exposes_idempotent_send(self):
        self.assertTrue(
            hasattr(CommunicationDispatcher, "send"),
            "Source §40.1 requires CommunicationDispatcher.send(..., idempotency_key).",
        )

    def _access_token(
        self,
        email="cora.communicator@sfpcl.example",
        password="SenderPass123!",
    ):
        response = self.client.post(
            "/api/v1/auth/login/",
            data={
                "email": email,
                "password": password,
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        return response.json()["data"]["access_token"]

    def _auth_headers(self, *, idempotency_key="communication-send-001", **kwargs):
        return {
            "Authorization": f"Bearer {self._access_token(**kwargs)}",
            "Idempotency-Key": idempotency_key,
        }

    def _reader_headers(self):
        return self._auth_headers(
            email="ravi.communications@sfpcl.example", password="ReaderPass123!"
        )

    def _plain_headers(self):
        return self._auth_headers(
            email="priya.communications@sfpcl.example", password="PlainPass123!"
        )

    def _send_payload(self, **overrides):
        payload = {
            "related_entity_type": "loan_application",
            "related_entity_id": str(self.related_entity_id),
            "recipient_party_type": "borrower",
            "recipient_party_id": str(self.recipient_party_id),
            "recipient_address": "borrower@sfpcl.example",
            "channel": "email",
            "content_template_id": str(self.template.content_template_id),
            "merge_data": {
                "application_reference_number": "LA-2026-0001",
                "borrower_name": "Ananya Rao",
            },
        }
        payload.update(overrides)
        return payload

    def test_send_renders_snapshot_persists_pending_row_audits_and_lists(self):
        response = self.client.post(
            COMMUNICATION_SEND_URL,
            data=self._send_payload(),
            content_type="application/json",
            headers={**self._auth_headers(), "X-Request-ID": "req-communication-send"},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        assert_success_envelope(self, payload)
        self.assertEqual(payload["meta"]["request_id"], "req-communication-send")
        self.assertEqual(payload["data"]["related_entity_type"], "loan_application")
        self.assertEqual(payload["data"]["related_entity_id"], str(self.related_entity_id))
        self.assertEqual(payload["data"]["recipient_party_type"], "borrower")
        self.assertEqual(
            payload["data"]["recipient_party_id"], str(self.recipient_party_id)
        )
        self.assertEqual(payload["data"]["recipient_address"], "borrower@sfpcl.example")
        self.assertEqual(payload["data"]["channel"], "email")
        self.assertEqual(
            payload["data"]["content_template_id"],
            str(self.template.content_template_id),
        )
        self.assertEqual(payload["data"]["subject_snapshot"], "Sanction LA-2026-0001")
        self.assertEqual(
            payload["data"]["body_snapshot"],
            "Dear Ananya Rao, your loan LA-2026-0001 is sanctioned.",
        )
        self.assertEqual(payload["data"]["delivery_status"], "pending")
        self.assertIsNone(payload["data"]["sent_at"])
        self.assertIsNone(payload["data"]["external_message_id"])

        row = Communication.objects.get(
            communication_id=payload["data"]["communication_id"]
        )
        self.assertEqual(row.sent_by_user, self.user)
        self.assertEqual(row.subject_snapshot, "Sanction LA-2026-0001")
        self.assertEqual(
            row.body_snapshot, "Dear Ananya Rao, your loan LA-2026-0001 is sanctioned."
        )
        self.assertEqual(row.delivery_status, "pending")
        job = CommunicationDeliveryJob.objects.get(communication_id=row.pk)
        self.assertEqual(job.job_kind, CommunicationDeliveryJob.KIND_GENERIC)
        self.assertEqual(job.idempotency_key, "communication-send-001")
        self.assertEqual(job.status, CommunicationDeliveryJob.STATUS_QUEUED)

        audit = AuditLog.objects.get(action="communications.communication.created")
        self.assertEqual(audit.actor_user, self.user)
        self.assertEqual(audit.entity_type, "communication")
        self.assertEqual(audit.entity_id, row.communication_id)
        self.assertEqual(
            audit.new_value_json["related_entity_id"], str(self.related_entity_id)
        )
        self.assertEqual(audit.new_value_json["channel"], "email")
        self.assertEqual(audit.new_value_json["delivery_status"], "pending")
        self.assertNotIn("subject_snapshot", audit.new_value_json)
        self.assertNotIn("body_snapshot", audit.new_value_json)
        self.assertNotIn("merge_data", audit.new_value_json)

        list_response = self.client.get(
            COMMUNICATIONS_URL,
            data={
                "related_entity_type": "loan_application",
                "related_entity_id": str(self.related_entity_id),
            },
            headers={**self._auth_headers(), "X-Request-ID": "req-communication-list"},
        )

        self.assertEqual(list_response.status_code, 200)
        list_payload = list_response.json()
        assert_pagination_shape(self, list_payload)
        self.assertEqual(list_payload["meta"]["request_id"], "req-communication-list")
        self.assertEqual(len(list_payload["data"]), 1)
        self.assertEqual(
            list_payload["data"][0]["communication_id"], payload["data"]["communication_id"]
        )

    def test_send_requires_key_and_exact_replay_is_zero_write(self):
        missing_headers = self._auth_headers()
        missing_headers.pop("Idempotency-Key")
        missing = self.client.post(
            COMMUNICATION_SEND_URL,
            data=self._send_payload(),
            content_type="application/json",
            headers=missing_headers,
        )
        self.assertEqual(missing.status_code, 400, missing.content)
        self.assertIn("idempotency_key", missing.json()["error"]["field_errors"])
        self.assertEqual(Communication.objects.count(), 0)

        oversized = self.client.post(
            COMMUNICATION_SEND_URL,
            data=self._send_payload(),
            content_type="application/json",
            headers=self._auth_headers(idempotency_key="k" * 256),
        )
        self.assertEqual(oversized.status_code, 400, oversized.content)
        self.assertEqual(Communication.objects.count(), 0)

        first = self.client.post(
            COMMUNICATION_SEND_URL,
            data=self._send_payload(),
            content_type="application/json",
            headers=self._auth_headers(idempotency_key=" exact-key "),
        )
        replay = self.client.post(
            COMMUNICATION_SEND_URL,
            data=self._send_payload(),
            content_type="application/json",
            headers=self._auth_headers(idempotency_key="exact-key"),
        )
        changed_object = self.client.post(
            COMMUNICATION_SEND_URL,
            data=self._send_payload(related_entity_id=str(uuid.uuid4())),
            content_type="application/json",
            headers=self._auth_headers(idempotency_key="exact-key"),
        )
        other_actor = User.objects.create(
            full_name="Other Communication Sender",
            email="other.sender@sfpcl.example",
            status="active",
            primary_role=self.role,
        )
        other_actor.set_password("OtherSender123!")
        other_actor.save()
        changed_actor = self.client.post(
            COMMUNICATION_SEND_URL,
            data=self._send_payload(),
            content_type="application/json",
            headers=self._auth_headers(
                idempotency_key="exact-key",
                email=other_actor.email,
                password="OtherSender123!",
            ),
        )

        self.assertEqual(first.status_code, 200, first.content)
        self.assertEqual(replay.status_code, 200, replay.content)
        self.assertEqual(replay.json()["data"], first.json()["data"])
        self.assertEqual(changed_object.status_code, 409, changed_object.content)
        self.assertEqual(changed_actor.status_code, 409, changed_actor.content)
        self.assertEqual(Communication.objects.count(), 1)
        self.assertEqual(CommunicationDeliveryJob.objects.count(), 1)

    def test_configured_fake_delivers_generic_job_once_and_default_manual_does_not(self):
        queued = self.client.post(
            COMMUNICATION_SEND_URL,
            data=self._send_payload(),
            content_type="application/json",
            headers=self._auth_headers(idempotency_key="generic-provider-key"),
        )
        self.assertEqual(queued.status_code, 200, queued.content)
        job = CommunicationDeliveryJob.objects.get()

        sent = execute_communication_job(job.pk, adapter=FakeEmailDeliveryAdapter())
        replay = execute_communication_job(job.pk, adapter=FakeEmailDeliveryAdapter())

        self.assertEqual(sent["delivery_status"], "sent")
        self.assertEqual(replay, sent)
        row = Communication.objects.get(pk=sent["communication_id"])
        self.assertEqual(row.delivery_status, "sent")
        self.assertTrue(row.external_message_id.startswith("fake:"))

        second_payload = self._send_payload(
            related_entity_id=str(uuid.uuid4()),
            recipient_address="manual.pending@example.com",
        )
        second = self.client.post(
            COMMUNICATION_SEND_URL,
            data=second_payload,
            content_type="application/json",
            headers=self._auth_headers(idempotency_key="manual-provider-key"),
        )
        self.assertEqual(second.status_code, 200, second.content)
        manual_job = CommunicationDeliveryJob.objects.get(
            idempotency_key="manual-provider-key"
        )
        manual = execute_communication_job(manual_job.pk)
        self.assertEqual(manual["delivery_status"], "retrying")
        manual_row = Communication.objects.get(pk=manual["communication_id"])
        self.assertEqual(manual_row.delivery_status, "pending")
        self.assertIsNone(manual_row.external_message_id)

    def test_send_validation_errors_do_not_write_rows_or_audit(self):
        invalid = self._send_payload(
            related_entity_id="not-a-uuid",
            recipient_party_id="also-not-a-uuid",
            channel="whatsapp",
            merge_data={"application_reference_number": "LA-2026-0001"},
            unexpected_field="ignored",
        )
        invalid.pop("recipient_party_type")

        response = self.client.post(
            COMMUNICATION_SEND_URL,
            data=invalid,
            content_type="application/json",
            headers=self._auth_headers(),
        )

        self.assertEqual(response.status_code, 400)
        payload = response.json()
        assert_error_envelope(self, payload, "VALIDATION_ERROR")
        self.assertIn("recipient_party_type", payload["error"]["field_errors"])
        self.assertIn("related_entity_id", payload["error"]["field_errors"])
        self.assertIn("recipient_party_id", payload["error"]["field_errors"])
        self.assertIn("channel", payload["error"]["field_errors"])
        self.assertIn("unexpected_field", payload["error"]["field_errors"])
        self.assertEqual(Communication.objects.count(), 0)
        self.assertEqual(
            AuditLog.objects.filter(action="communications.communication.created").count(),
            0,
        )

    def test_send_rejects_unapproved_inactive_unknown_and_mismatched_template(self):
        self.template.approval_status = ContentTemplate.STATUS_DRAFT
        self.template.save(update_fields=["approval_status"])

        response = self.client.post(
            COMMUNICATION_SEND_URL,
            data=self._send_payload(),
            content_type="application/json",
            headers=self._auth_headers(),
        )
        self.assertEqual(response.status_code, 400)
        assert_error_envelope(self, response.json(), "VALIDATION_ERROR")

        self.template.approval_status = ContentTemplate.STATUS_APPROVED
        self.template.effective_to = "2026-01-31"
        self.template.save(update_fields=["approval_status", "effective_to"])
        response = self.client.post(
            COMMUNICATION_SEND_URL,
            data=self._send_payload(),
            content_type="application/json",
            headers=self._auth_headers(),
        )
        self.assertEqual(response.status_code, 400)
        assert_error_envelope(self, response.json(), "VALIDATION_ERROR")

        self.template.effective_to = "2026-12-31"
        self.template.save(update_fields=["effective_to"])
        response = self.client.post(
            COMMUNICATION_SEND_URL,
            data=self._send_payload(
                merge_data={
                    "application_reference_number": "LA-2026-0001",
                    "borrower_name": "Ananya Rao",
                    "extra_key": "not allowed",
                }
            ),
            content_type="application/json",
            headers=self._auth_headers(),
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("merge_data", response.json()["error"]["field_errors"])

        response = self.client.post(
            COMMUNICATION_SEND_URL,
            data=self._send_payload(content_template_id=str(uuid.uuid4())),
            content_type="application/json",
            headers=self._auth_headers(),
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("content_template_id", response.json()["error"]["field_errors"])
        self.assertEqual(Communication.objects.count(), 0)
        self.assertEqual(
            AuditLog.objects.filter(action="communications.communication.created").count(),
            0,
        )

    def test_list_requires_strict_related_entity_query(self):
        response = self.client.get(
            COMMUNICATIONS_URL,
            data={
                "related_entity_type": "loan_application",
                "related_entity_id": "not-a-uuid",
                "unknown": "value",
            },
            headers=self._auth_headers(),
        )

        self.assertEqual(response.status_code, 400)
        payload = response.json()
        assert_error_envelope(self, payload, "VALIDATION_ERROR")
        self.assertIn("related_entity_id", payload["error"]["field_errors"])
        self.assertIn("unknown", payload["error"]["field_errors"])

    def test_unauthenticated_and_forbidden_requests_do_not_write(self):
        unauthenticated = self.client.post(
            COMMUNICATION_SEND_URL,
            data=self._send_payload(),
            content_type="application/json",
        )
        self.assertEqual(unauthenticated.status_code, 401)
        assert_error_envelope(self, unauthenticated.json(), "AUTH_REQUIRED")

        forbidden_send = self.client.post(
            COMMUNICATION_SEND_URL,
            data=self._send_payload(),
            content_type="application/json",
            headers=self._reader_headers(),
        )
        self.assertEqual(forbidden_send.status_code, 403)
        assert_error_envelope(self, forbidden_send.json(), "PERMISSION_DENIED")

        forbidden_list = self.client.get(
            COMMUNICATIONS_URL,
            data={
                "related_entity_type": "loan_application",
                "related_entity_id": str(self.related_entity_id),
            },
            headers=self._plain_headers(),
        )
        self.assertEqual(forbidden_list.status_code, 403)
        assert_error_envelope(self, forbidden_list.json(), "PERMISSION_DENIED")
        self.assertEqual(Communication.objects.count(), 0)
        self.assertEqual(
            AuditLog.objects.filter(action="communications.communication.created").count(),
            0,
        )
