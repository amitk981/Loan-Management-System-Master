from django.apps import apps
from django.utils import timezone
import inspect
from pathlib import Path

from sfpcl_credit.communications.adapters import (
    EmailDeliveryResult,
    FakeSmsDeliveryAdapter,
    FutureSmsDeliveryAdapter,
    ManualSmsDeliveryAdapter,
)
from sfpcl_credit.communications.models import Communication, CommunicationDeliveryJob
from sfpcl_credit.communications.modules.communication_dispatcher import (
    CommunicationDispatcher,
    CommunicationDispatchConflict,
)
from sfpcl_credit.processes.communication_delivery import execute_communication_job
from sfpcl_credit.tests.test_communications_api import (
    COMMUNICATION_SEND_URL,
    CommunicationApiTests,
)


class CommunicationChannelContractTests(CommunicationApiTests):
    def test_public_facade_signatures_match_source_module_contract(self):
        self.assertEqual(
            list(inspect.signature(CommunicationDispatcher.create_from_template).parameters),
            ["actor", "template_code", "recipient", "context", "related_entity"],
        )
        self.assertEqual(
            list(inspect.signature(CommunicationDispatcher.send).parameters),
            ["communication_id", "idempotency_key"],
        )
        retry_parameters = inspect.signature(
            CommunicationDispatcher.retry_failed
        ).parameters
        self.assertIn("actor", retry_parameters)

        project = Path(__file__).resolve().parents[1]
        services_source = (project / "communications" / "services.py").read_text()
        self.assertIn("CommunicationDispatcher.create_from_template(", services_source)
        self.assertIn("CommunicationDispatcher.send(", services_source)
        for relative in (
            "communications/services.py",
            "processes/communication_delivery.py",
            "processes/disbursement_advice_delivery.py",
            "processes/tasks.py",
        ):
            source = (project / relative).read_text()
            self.assertNotIn(".send_email(", source)
            self.assertNotIn(".send_sms(", source)
            self.assertNotIn("CommunicationDispatcher._send(", source)

    def test_sms_job_uses_only_sms_adapter(self):
        self.template.template_type = "sms"
        self.template.subject_template = "SMS notification"
        self.template.save(update_fields=["template_type", "subject_template"])
        response = self.client.post(
            COMMUNICATION_SEND_URL,
            data=self._send_payload(
                channel="sms", recipient_address="+919876543210"
            ),
            content_type="application/json",
            headers=self._auth_headers(idempotency_key="sms-channel-contract"),
        )
        self.assertEqual(response.status_code, 200, response.content)
        job = CommunicationDeliveryJob.objects.get()

        class RecordingChannelAdapter:
            email_calls = 0
            sms_calls = 0

            def send_email(self, payload, idempotency_key):
                self.email_calls += 1
                raise AssertionError("SMS crossed the Email adapter seam")

            def send_sms(self, payload, idempotency_key):
                self.sms_calls += 1
                return EmailDeliveryResult(
                    external_message_id="fake:sms-channel-contract",
                    delivery_status="sent",
                    accepted_at=timezone.now(),
                )

        adapter = RecordingChannelAdapter()
        result = execute_communication_job(job.pk, adapter=adapter)

        self.assertEqual(result["delivery_status"], "sent")
        self.assertEqual(adapter.sms_calls, 1)
        self.assertEqual(adapter.email_calls, 0)

    def test_channel_template_recipient_and_sms_safety_fail_before_writes(self):
        unsafe_cases = [
            ("email", "sms", "borrower@sfpcl.example", {}, "channel"),
            ("email", "email", "not-an-email", {}, "recipient_address"),
            ("sms", "sms", "9876543210", {}, "recipient_address"),
            ("phone", "phone", "+919876543210", {}, "channel"),
            ("courier", "courier", "Postal address", {}, "channel"),
            ("sms", "sms", "+919876543210", {"pan_number": "ABCDE1234F"}, "merge_data"),
            ("sms", "sms", "+919876543210", {"borrower_name": "ABCDE1234F"}, "merge_data"),
            ("sms", "sms", "+919876543210", {"borrower_name": "1234 5678 9012"}, "merge_data"),
            ("sms", "sms", "+919876543210", {"borrower_name": "HDFC0123456"}, "merge_data"),
            ("sms", "sms", "+919876543210", {"borrower_name": "123456"}, "merge_data"),
            ("sms", "sms", "+919876543210", {"borrower_name": "enc:gAAAA-secret"}, "merge_data"),
        ]
        base_body = (
            "Dear {{borrower_name}}, your loan {{application_reference_number}} "
            "is sanctioned."
        )
        for index, (channel, template_type, recipient, merge_override, field) in enumerate(unsafe_cases):
            with self.subTest(channel=channel, template_type=template_type, value=merge_override):
                self.template.template_type = template_type
                variables = ["application_reference_number", "borrower_name"]
                merge_data = {
                    "application_reference_number": "LA-2026-0001",
                    "borrower_name": "Ananya Rao",
                    **merge_override,
                }
                if "pan_number" in merge_override:
                    variables.append("pan_number")
                self.template.body_template = base_body + (
                    " {{pan_number}}" if "pan_number" in merge_override else ""
                )
                self.template.variables_json = variables
                self.template.save(
                    update_fields=["template_type", "variables_json", "body_template"]
                )
                response = self.client.post(
                    COMMUNICATION_SEND_URL,
                    data=self._send_payload(
                        channel=channel,
                        recipient_address=recipient,
                        merge_data=merge_data,
                    ),
                    content_type="application/json",
                    headers=self._auth_headers(
                        idempotency_key=f"unsafe-{index}-{channel}-{template_type}-{field}"
                    ),
                )
                self.assertEqual(response.status_code, 400, response.content)
                self.assertIn(field, response.json()["error"]["field_errors"])
                self.assertEqual(Communication.objects.count(), 0)
                self.assertEqual(CommunicationDeliveryJob.objects.count(), 0)

    def test_generic_acceptance_freezes_immutable_provider_evidence_and_replays(self):
        response = self.client.post(
            COMMUNICATION_SEND_URL,
            data=self._send_payload(),
            content_type="application/json",
            headers=self._auth_headers(idempotency_key="generic-provider-evidence"),
        )
        self.assertEqual(response.status_code, 200, response.content)
        job = CommunicationDeliveryJob.objects.get()

        class CountingEmailAdapter:
            calls = 0

            def send_email(self, payload, idempotency_key):
                self.calls += 1
                return EmailDeliveryResult(
                    external_message_id="fake:generic-provider-evidence",
                    delivery_status="sent",
                    accepted_at=timezone.now(),
                )

        adapter = CountingEmailAdapter()
        first = execute_communication_job(job.pk, adapter=adapter)
        replay = execute_communication_job(job.pk, adapter=adapter)
        job.refresh_from_db()
        ProviderEvidence = apps.get_model(
            "communications", "CommunicationProviderEvidence"
        )
        evidence = ProviderEvidence.objects.get(job=job)

        self.assertEqual(first["delivery_status"], "sent")
        self.assertEqual(replay["delivery_status"], "sent")
        self.assertEqual(adapter.calls, 1)
        self.assertEqual(evidence.communication_id, job.communication_id)
        self.assertEqual(evidence.channel, "email")
        self.assertEqual(evidence.payload_digest, job.request_payload_digest)
        self.assertEqual(evidence.idempotency_key, job.idempotency_key)
        self.assertEqual(evidence.actor_id, job.actor_id)
        self.assertEqual(evidence.provider_external_message_id, job.provider_external_message_id)
        with self.assertRaises(TypeError):
            ProviderEvidence.objects.filter(pk=evidence.pk).update(channel="sms")
        CommunicationDeliveryJob.objects.filter(pk=job.pk).update(
            provider_external_message_id="fake:tampered-provider-evidence"
        )
        with self.assertRaises(CommunicationDispatchConflict):
            execute_communication_job(job.pk, adapter=adapter)

    def test_exact_http_replay_returns_retained_source_envelope(self):
        headers = self._auth_headers(idempotency_key="generic-source-replay")
        first = self.client.post(
            COMMUNICATION_SEND_URL,
            data=self._send_payload(),
            content_type="application/json",
            headers=headers,
        )
        replay = self.client.post(
            COMMUNICATION_SEND_URL,
            data=self._send_payload(),
            content_type="application/json",
            headers=headers,
        )

        self.assertEqual(first.status_code, 200, first.content)
        self.assertEqual(replay.status_code, 200, replay.content)
        self.assertEqual(
            replay.json()["data"],
            {
                "idempotency_replayed": True,
                "original_response": first.json()["data"],
            },
        )
        self.assertEqual(Communication.objects.count(), 1)
        self.assertEqual(CommunicationDeliveryJob.objects.count(), 1)

    def test_sms_fake_future_and_no_provider_share_only_sms_contract(self):
        self.template.template_type = "sms"
        self.template.save(update_fields=["template_type"])
        response = self.client.post(
            COMMUNICATION_SEND_URL,
            data=self._send_payload(
                channel="sms", recipient_address="+919876543210"
            ),
            content_type="application/json",
            headers=self._auth_headers(idempotency_key="sms-adapter-modes"),
        )
        job = CommunicationDeliveryJob.objects.get()
        self.assertEqual(response.status_code, 200, response.content)

        retrying = execute_communication_job(
            job.pk, adapter=ManualSmsDeliveryAdapter()
        )
        self.assertEqual(retrying["delivery_status"], "retrying")
        safe_evidence = CommunicationDispatcher.job_evidence(job_id=job.pk, limit=1)[0]
        self.assertNotIn("+919876543210", str(safe_evidence))
        self.assertNotIn("Ananya Rao", str(safe_evidence))
        self.assertNotIn("LA-2026-0001", str(safe_evidence))
        CommunicationDeliveryJob.objects.filter(pk=job.pk).update(
            next_attempt_at=timezone.now()
        )
        sent = execute_communication_job(
            job.pk,
            adapter=FutureSmsDeliveryAdapter(transport=FakeSmsDeliveryAdapter()),
        )

        self.assertEqual(sent["delivery_status"], "sent")
        job.refresh_from_db()
        self.assertTrue(job.provider_external_message_id.startswith("fake:"))
