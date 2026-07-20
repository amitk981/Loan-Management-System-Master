from datetime import date
from concurrent.futures import ThreadPoolExecutor
import tempfile
import uuid
from threading import Barrier
from types import SimpleNamespace
from unittest import skipUnless

from django.core.exceptions import ValidationError
from django.db import close_old_connections, connection, connections
from django.test import Client, TestCase, TransactionTestCase, override_settings
from django.utils import timezone

from sfpcl_credit.communications.models import (
    CommunicationDeliveryJob,
    ContentTemplate,
)
from sfpcl_credit.communications.adapters import (
    FakeEmailDeliveryAdapter,
    ManualEmailDeliveryAdapter,
    ManualSmsDeliveryAdapter,
)
from sfpcl_credit.communications.modules.communication_dispatcher import (
    CommunicationDispatcher,
)
from sfpcl_credit.configurations.models import (
    InterestRateConfig,
    InterestRateHistory,
    VersionHistory,
)
from sfpcl_credit.configurations.models import BorrowerRateNoticeObligation
from sfpcl_credit.configurations.modules.interest_rate_configuration import (
    MissingEffectiveRate,
    consume_effective_rate,
    activate,
    InterestRateConflict,
    resolve_effective_rate,
)
from sfpcl_credit.identity.models import Permission, Role, RolePermission, User
from sfpcl_credit.tests.api_contracts import (
    assert_pagination_shape,
    assert_success_envelope,
)
from sfpcl_credit.tests.servicing_builders import build_servicing_owner_fixture


INTEREST_RATE_URL = "/api/v1/config/interest-rates/"


@override_settings(
    DOCUMENT_STORAGE_ROOT=tempfile.mkdtemp(prefix="sfpcl-interest-rate-tests-")
)
class InterestRateConfigApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.manager_role = Role.objects.create(
            role_code="interest_rate_manager",
            role_name="Interest Rate Manager",
            is_system_role=True,
            status="active",
        )
        for code, name, risk in (
            ("config.interest_rate.manage", "Manage interest rate", "critical"),
            ("config.loan_policy.read", "View loan policy config", "medium"),
            (
                "communications.communication.send",
                "Create communication snapshots",
                "medium",
            ),
        ):
            permission = Permission.objects.create(
                permission_code=code,
                permission_name=name,
                module_name="config",
                risk_level=risk,
            )
            RolePermission.objects.create(role=self.manager_role, permission=permission)
        self.manager = User.objects.create(
            full_name="Rate Maker",
            email="rate.maker@sfpcl.example",
            status="active",
            primary_role=self.manager_role,
        )
        self.manager.set_password("RateMaker123!")
        self.manager.save()
        self.checker = User.objects.create(
            full_name="Rate Checker",
            email="rate.checker@sfpcl.example",
            status="active",
            primary_role=self.manager_role,
        )
        self.checker.set_password("RateChecker123!")
        self.checker.save()
        self.plain_role = Role.objects.create(
            role_code="rate_plain_staff",
            role_name="Rate Plain Staff",
            is_system_role=True,
            status="active",
        )
        self.plain_user = User.objects.create(
            full_name="Plain Staff",
            email="rate.plain@sfpcl.example",
            status="active",
            primary_role=self.plain_role,
        )
        self.plain_user.set_password("RatePlain123!")
        self.plain_user.save()

    def _headers(self, *, checker=False, idempotency_key=None):
        user = self.checker if checker else self.manager
        password = "RateChecker123!" if checker else "RateMaker123!"
        response = self.client.post(
            "/api/v1/auth/login/",
            data={"email": user.email, "password": password},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        token = response.json()["data"]["access_token"]
        headers = {
            "Authorization": f"Bearer {token}",
            "X-Request-ID": "req-rate-config",
        }
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        return headers

    def _plain_headers(self):
        response = self.client.post(
            "/api/v1/auth/login/",
            data={"email": self.plain_user.email, "password": "RatePlain123!"},
            content_type="application/json",
        )
        token = response.json()["data"]["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def _payload(self, **overrides):
        payload = {
            "version_number": "RATE-2026-01",
            "rate_type": "floating",
            "effective_rate": "9.2500",
            "effective_from": "2026-08-01",
            "effective_to": None,
            "benchmark_name": None,
            "spread_rate": None,
            "reset_frequency": None,
            "communication_required": True,
            "board_approval_reference": "BOARD-RATE-2026-01",
        }
        payload.update(overrides)
        return payload

    def test_manager_creates_and_lists_an_immutable_rate_proposal(self):
        created = self.client.post(
            INTEREST_RATE_URL,
            data=self._payload(),
            content_type="application/json",
            headers=self._headers(),
        )

        self.assertEqual(created.status_code, 200)
        created_payload = created.json()
        assert_success_envelope(self, created_payload)
        self.assertEqual(
            created_payload["data"],
            {
                "interest_rate_config_id": created_payload["data"][
                    "interest_rate_config_id"
                ],
                "version_number": "RATE-2026-01",
                "rate_type": "floating",
                "effective_rate": "9.2500",
                "effective_from": "2026-08-01",
                "effective_to": None,
                "benchmark_name": None,
                "spread_rate": None,
                "reset_frequency": None,
                "communication_required": True,
                "board_approval_reference": "BOARD-RATE-2026-01",
                "status": "proposed",
                "created_by_user_id": str(self.manager.pk),
                "approved_by_user_id": None,
                "activated_at": None,
                "notice_summary": {
                    "pending": 0,
                    "sent": 0,
                    "failed": 0,
                },
                "notice_channel_summary": {
                    "pending": 0,
                    "sent": 0,
                    "failed": 0,
                },
            },
        )

        listed = self.client.get(INTEREST_RATE_URL, headers=self._headers())

        self.assertEqual(listed.status_code, 200)
        listed_payload = listed.json()
        assert_pagination_shape(self, listed_payload)
        self.assertEqual(listed_payload["data"], [created_payload["data"]])

    def test_permission_validation_and_changed_replay_fail_without_side_effects(self):
        denied_read = self.client.get(INTEREST_RATE_URL, headers=self._plain_headers())
        denied_create = self.client.post(
            INTEREST_RATE_URL,
            data=self._payload(),
            content_type="application/json",
            headers=self._plain_headers(),
        )
        self.assertEqual(denied_read.status_code, 403)
        self.assertEqual(denied_create.status_code, 403)

        RolePermission.objects.create(
            role=self.plain_role,
            permission=Permission.objects.get(permission_code="config.loan_policy.read"),
        )
        read_only = self.client.get(INTEREST_RATE_URL, headers=self._plain_headers())
        read_only_create = self.client.post(
            INTEREST_RATE_URL,
            data=self._payload(),
            content_type="application/json",
            headers=self._plain_headers(),
        )
        self.assertEqual(read_only.status_code, 200)
        self.assertEqual(read_only_create.status_code, 403)

        invalid = self.client.post(
            INTEREST_RATE_URL,
            data=self._payload(rate_type="fixed", effective_rate="not-a-rate"),
            content_type="application/json",
            headers=self._headers(),
        )
        self.assertEqual(invalid.status_code, 400)
        self.assertEqual(InterestRateConfig.objects.count(), 0)

        first = self._create(
            version_number="RATE-PERM-1",
            effective_from="2026-08-01",
            effective_to="2026-08-31",
            communication_required=False,
        )
        communication_permission = Permission.objects.get(
            permission_code="communications.communication.send"
        )
        RolePermission.objects.filter(
            role=self.manager_role, permission=communication_permission
        ).delete()
        missing_communication_authority = self._activate(
            first["interest_rate_config_id"], "missing-communication-authority"
        )
        self.assertEqual(missing_communication_authority.status_code, 403)
        RolePermission.objects.create(
            role=self.manager_role, permission=communication_permission
        )
        self.assertEqual(
            self._activate(first["interest_rate_config_id"], "changed-replay").status_code,
            200,
        )
        second = self._create(
            version_number="RATE-PERM-2",
            effective_from="2026-09-01",
            communication_required=False,
        )
        changed = self._activate(second["interest_rate_config_id"], "changed-replay")
        self.assertEqual(changed.status_code, 409)
        self.assertEqual(
            InterestRateConfig.objects.filter(status="active").count(), 1
        )

        gap = self._create(
            version_number="RATE-PERM-GAP",
            effective_from="2026-10-01",
            communication_required=False,
        )
        gap_response = self._activate(
            gap["interest_rate_config_id"], "rate-gap-activation"
        )
        self.assertEqual(gap_response.status_code, 409)

    def _create(self, **overrides):
        response = self.client.post(
            INTEREST_RATE_URL,
            data=self._payload(**overrides),
            content_type="application/json",
            headers=self._headers(),
        )
        self.assertEqual(response.status_code, 200)
        return response.json()["data"]

    def _activate(self, config_id, key):
        return self.client.post(
            f"{INTEREST_RATE_URL}{config_id}/activate/",
            headers=self._headers(checker=True, idempotency_key=key),
        )

    def test_checker_activates_contiguous_versions_and_resolution_is_historical(self):
        first = self._create(
            version_number="RATE-2026-01",
            effective_from="2026-08-01",
            effective_rate="9.2500",
        )

        maker_attempt = self.client.post(
            f"{INTEREST_RATE_URL}{first['interest_rate_config_id']}/activate/",
            headers=self._headers(idempotency_key="rate-activate-1"),
        )
        self.assertEqual(maker_attempt.status_code, 409)

        activated = self._activate(first["interest_rate_config_id"], "rate-activate-1")
        self.assertEqual(activated.status_code, 200)
        self.assertEqual(activated.json()["data"]["status"], "active")

        replayed = self._activate(first["interest_rate_config_id"], "rate-activate-1")
        self.assertEqual(replayed.status_code, 200)
        self.assertEqual(
            replayed.json()["data"],
            {
                "idempotency_replayed": True,
                "original_response": activated.json()["data"],
            },
        )

        second = self._create(
            version_number="RATE-2026-02",
            effective_from="2026-09-01",
            effective_rate="9.7500",
        )
        second_activation = self._activate(
            second["interest_rate_config_id"], "rate-activate-2"
        )
        self.assertEqual(second_activation.status_code, 200)

        with self.assertRaises(MissingEffectiveRate):
            resolve_effective_rate(date(2026, 7, 31))
        self.assertEqual(
            resolve_effective_rate(date(2026, 8, 1)).effective_rate,
            InterestRateConfig.objects.get(pk=first["interest_rate_config_id"]).effective_rate,
        )
        self.assertEqual(
            resolve_effective_rate(date(2026, 8, 31)).version_number,
            "RATE-2026-01",
        )
        self.assertEqual(
            InterestRateConfig.objects.get(
                pk=first["interest_rate_config_id"]
            ).effective_to,
            date(2026, 8, 31),
        )
        self.assertEqual(
            resolve_effective_rate(date(2026, 9, 1)).version_number,
            "RATE-2026-02",
        )
        self.assertEqual(
            resolve_effective_rate(date(2027, 1, 1)).version_number,
            "RATE-2026-02",
        )
        self.assertEqual(
            VersionHistory.objects.filter(
                versioned_entity_type="interest_rate_config"
            ).count(),
            3,
        )

    def test_open_predecessor_cannot_be_closed_before_a_retained_consumption(self):
        from sfpcl_credit.configurations.models import InterestRateConsumptionSnapshot
        fixture = build_servicing_owner_fixture(suffix=uuid.uuid4().hex[:8])
        first = self._create(
            version_number="RATE-CONSUMED-OPEN",
            effective_from="2026-08-01",
            communication_required=False,
        )
        self.assertEqual(
            self._activate(first["interest_rate_config_id"], "consumed-open-first").status_code,
            200,
        )
        InterestRateConsumptionSnapshot.objects.create(
            consumer_kind="interest_invoice",
            consumer_reference_id=uuid.uuid4(),
            loan_account=fixture.account,
            calculation_date=date(2026, 10, 1),
            rate_config_id=first["interest_rate_config_id"],
            version_number="RATE-CONSUMED-OPEN",
            effective_rate="9.2500",
        )
        successor = self._create(
            version_number="RATE-CONSUMED-SUCCESSOR",
            effective_from="2026-09-01",
            communication_required=False,
        )

        response = self._activate(
            successor["interest_rate_config_id"], "consumed-open-successor"
        )

        self.assertEqual(response.status_code, 409, response.content)
        self.assertIsNone(
            InterestRateConfig.objects.get(
                pk=first["interest_rate_config_id"]
            ).effective_to
        )

    def test_activation_queues_honest_email_and_sms_obligations_for_active_loans(self):
        fixture = build_servicing_owner_fixture(suffix=uuid.uuid4().hex[:8])
        account = fixture.account
        account.member.email = "borrower.rate@sfpcl.example"
        account.member.mobile_number = "+919876543210"
        account.member.save(update_fields=["email", "mobile_number"])
        type(account).objects.filter(pk=account.pk).update(loan_account_status="active")
        today = timezone.localdate()
        for channel, code, template_type, subject in (
            ("email", "interest_rate_change_email", "email", "Rate revised"),
            ("sms", "interest_rate_change_sms", "sms", None),
        ):
            ContentTemplate.objects.create(
                template_code=code,
                template_name=f"Interest rate change {channel}",
                template_type=template_type,
                audience="borrower",
                subject_template=subject,
                body_template=(
                    "Floating rate {{effective_rate}} applies from {{effective_from}}."
                ),
                variables_json=["effective_rate", "effective_from"],
                approval_status="approved",
                template_version="1.0",
                effective_from=today,
            )
        proposed = self._create(effective_from="2026-08-01")

        response = self._activate(
            proposed["interest_rate_config_id"], "rate-notices-activate"
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(
            response.json()["data"]["notice_summary"],
            {"pending": 1, "sent": 0, "failed": 0},
        )
        self.assertEqual(
            response.json()["data"]["notice_channel_summary"],
            {"pending": 2, "sent": 0, "failed": 0},
        )
        obligations = BorrowerRateNoticeObligation.objects.filter(
            interest_rate_config_id=proposed["interest_rate_config_id"],
            loan_account=account,
        )
        self.assertEqual(obligations.count(), 1)
        obligation = obligations.get()
        self.assertEqual(
            CommunicationDeliveryJob.objects.filter(
                communication_id__in=[
                    obligation.email_communication_id,
                    obligation.sms_communication_id,
                ]
            ).count(),
            2,
        )
        self.assertEqual(obligation.delivery_status, "pending")
        self.assertEqual(obligation.email_delivery_status, "pending")
        self.assertEqual(obligation.sms_delivery_status, "pending")

        email_job = CommunicationDeliveryJob.objects.get(
            communication_id=obligation.email_communication_id
        )
        CommunicationDispatcher.execute_generic_job(
            email_job.pk, adapter=ManualEmailDeliveryAdapter()
        )
        obligation.refresh_from_db()
        self.assertEqual(obligation.email_delivery_status, "pending")
        email_job.refresh_from_db()
        email_job.next_attempt_at = timezone.now()
        email_job.save(update_fields=["next_attempt_at"])
        CommunicationDispatcher.execute_generic_job(
            email_job.pk, adapter=FakeEmailDeliveryAdapter()
        )

        sms_job = CommunicationDeliveryJob.objects.get(
            communication_id=obligation.sms_communication_id
        )
        sms_job.max_attempts = 1
        sms_job.save(update_fields=["max_attempts"])
        CommunicationDispatcher.execute_generic_job(
            sms_job.pk, adapter=ManualSmsDeliveryAdapter()
        )
        obligation.refresh_from_db()
        self.assertEqual(obligation.email_delivery_status, "sent")
        self.assertEqual(obligation.sms_delivery_status, "failed")
        self.assertEqual(obligation.delivery_status, "failed")
        account.refresh_from_db()
        self.assertEqual(f"{account.current_interest_rate:.4f}", "9.0000")

        replay = self._activate(
            proposed["interest_rate_config_id"], "rate-notices-activate"
        )
        self.assertEqual(
            replay.json()["data"],
            {
                "idempotency_replayed": True,
                "original_response": response.json()["data"],
            },
        )

        listed = self.client.get(INTEREST_RATE_URL, headers=self._headers())
        self.assertEqual(
            listed.json()["data"][0]["notice_summary"],
            {"pending": 0, "sent": 0, "failed": 1},
        )
        self.assertEqual(
            listed.json()["data"][0]["notice_channel_summary"],
            {"pending": 0, "sent": 1, "failed": 1},
        )

    def test_invoice_and_accrual_consumers_retain_the_historical_rate_snapshot(self):
        fixture = build_servicing_owner_fixture(suffix=uuid.uuid4().hex[:8])
        account = fixture.account
        first = self._create(
            version_number="RATE-2026-01",
            effective_from="2026-08-01",
            effective_to="2026-08-31",
            effective_rate="9.2500",
            communication_required=False,
        )
        self.assertEqual(
            self._activate(first["interest_rate_config_id"], "consume-rate-1").status_code,
            200,
        )
        consumer_id = uuid.uuid4()
        invoice_snapshot = consume_effective_rate(
            consumer_kind="interest_invoice",
            consumer_reference_id=consumer_id,
            loan_account_id=account.pk,
            calculation_date=date(2026, 8, 31),
        )

        second = self._create(
            version_number="RATE-2026-02",
            effective_from="2026-09-01",
            effective_rate="9.7500",
            communication_required=False,
        )
        self.assertEqual(
            self._activate(second["interest_rate_config_id"], "consume-rate-2").status_code,
            200,
        )

        replay = consume_effective_rate(
            consumer_kind="interest_invoice",
            consumer_reference_id=consumer_id,
            loan_account_id=account.pk,
            calculation_date=date(2026, 8, 31),
        )
        accrual_snapshot = consume_effective_rate(
            consumer_kind="interest_accrual",
            consumer_reference_id=uuid.uuid4(),
            loan_account_id=account.pk,
            calculation_date=date(2026, 9, 1),
        )
        self.assertEqual(replay.pk, invoice_snapshot.pk)
        self.assertEqual(f"{invoice_snapshot.effective_rate:.4f}", "9.2500")
        self.assertEqual(str(invoice_snapshot.rate_config_id), first["interest_rate_config_id"])
        self.assertEqual(f"{accrual_snapshot.effective_rate:.4f}", "9.7500")
        self.assertEqual(str(accrual_snapshot.rate_config_id), second["interest_rate_config_id"])
        account.refresh_from_db()
        self.assertEqual(f"{account.current_interest_rate:.4f}", "9.0000")
        from sfpcl_credit.loans.modules.loan_account_read import resolve_creation_truth

        self.assertIsNotNone(resolve_creation_truth(account=account))
        histories = list(
            InterestRateHistory.objects.filter(loan_account=account).order_by(
                "effective_from"
            )
        )
        self.assertEqual(
            [
                (
                    f"{history.old_interest_rate:.4f}",
                    f"{history.new_interest_rate:.4f}",
                )
                for history in histories
            ],
            [("9.0000", "9.2500"), ("9.2500", "9.7500")],
        )
        with self.assertRaises(ValidationError):
            InterestRateHistory.objects.filter(pk=histories[0].pk).update(
                new_interest_rate="10.0000"
            )
        type(account).objects.filter(pk=account.pk).update(current_interest_rate="8.5000")
        account.refresh_from_db()
        self.assertIsNone(resolve_creation_truth(account=account))

    def test_active_rate_versions_reject_model_and_queryset_mutation(self):
        proposed = self._create(
            version_number="RATE-IMMUTABLE",
            effective_from="2026-08-01",
            communication_required=False,
        )
        self.assertEqual(
            self._activate(proposed["interest_rate_config_id"], "immutable-rate").status_code,
            200,
        )
        row = InterestRateConfig.objects.get(pk=proposed["interest_rate_config_id"])
        row.effective_rate = "10.0000"

        with self.assertRaises(ValidationError):
            row.save(update_fields=["effective_rate"])
        with self.assertRaises(ValidationError):
            InterestRateConfig.objects.filter(pk=row.pk).update(
                effective_rate="10.0000"
            )
        with self.assertRaises(ValidationError):
            row.delete()


@override_settings(
    DOCUMENT_STORAGE_ROOT=tempfile.mkdtemp(prefix="sfpcl-interest-rate-pg-tests-")
)
@skipUnless(connection.vendor == "postgresql", "PostgreSQL concurrency acceptance")
class InterestRateActivationPostgreSQLAcceptanceTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        role = Role.objects.create(
            role_code="rate_pg_manager",
            role_name="Rate PG Manager",
            is_system_role=True,
            status="active",
        )
        permission = Permission.objects.create(
            permission_code="config.interest_rate.manage",
            permission_name="Manage interest rate",
            module_name="config",
            risk_level="critical",
        )
        RolePermission.objects.create(role=role, permission=permission)
        communication_permission = Permission.objects.create(
            permission_code="communications.communication.send",
            permission_name="Create communication snapshots",
            module_name="communications",
            risk_level="medium",
        )
        RolePermission.objects.create(
            role=role, permission=communication_permission
        )
        self.maker = User.objects.create(
            full_name="PG Maker",
            email="pg.maker@sfpcl.example",
            status="active",
            primary_role=role,
        )
        self.checker = User.objects.create(
            full_name="PG Checker",
            email="pg.checker@sfpcl.example",
            status="active",
            primary_role=role,
        )
        self.request = SimpleNamespace(
            META={"REMOTE_ADDR": "127.0.0.1"},
            headers={"User-Agent": "postgresql-acceptance"},
        )

    def _proposal(self, *, version, effective_from, rate="9.2500"):
        return InterestRateConfig.objects.create(
            version_number=version,
            rate_type="floating",
            effective_rate=rate,
            effective_from=effective_from,
            communication_required=False,
            board_approval_reference=f"BOARD-{version}",
            created_by_user=self.maker,
        )

    def test_concurrent_competing_versions_retain_one_effective_winner(self):
        first = self._proposal(version="PG-RATE-A", effective_from="2026-08-01")
        second = self._proposal(version="PG-RATE-B", effective_from="2026-08-01")
        outcomes = self._race(
            (first.pk, "pg-competing-a"),
            (second.pk, "pg-competing-b"),
        )
        self.assertEqual(sorted(outcomes), ["conflict", "success"])
        self.assertEqual(InterestRateConfig.objects.filter(status="active").count(), 1)
        self.assertEqual(
            VersionHistory.objects.filter(
                versioned_entity_type="interest_rate_config"
            ).count(),
            1,
        )

    def test_concurrent_exact_replay_retains_one_activation_history(self):
        row = self._proposal(version="PG-RATE-REPLAY", effective_from="2026-08-01")
        outcomes = self._race(
            (row.pk, "pg-exact-replay"),
            (row.pk, "pg-exact-replay"),
        )
        self.assertEqual(outcomes, ["success", "success"])
        self.assertEqual(
            VersionHistory.objects.filter(
                versioned_entity_type="interest_rate_config",
                versioned_entity_id=row.pk,
            ).count(),
            1,
        )

    def test_concurrent_activation_retains_one_notice_per_loan_and_channel(self):
        fixture = build_servicing_owner_fixture(suffix=uuid.uuid4().hex[:8])
        account = fixture.account
        account.member.email = "pg.borrower@sfpcl.example"
        account.member.mobile_number = "+919876543210"
        account.member.save(update_fields=["email", "mobile_number"])
        type(account).objects.filter(pk=account.pk).update(loan_account_status="active")
        for channel, code, subject in (
            ("email", "interest_rate_change_email", "Rate revised"),
            ("sms", "interest_rate_change_sms", None),
        ):
            ContentTemplate.objects.create(
                template_code=code,
                template_name=f"PG rate {channel}",
                template_type=channel,
                audience="borrower",
                subject_template=subject,
                body_template="Rate {{effective_rate}} from {{effective_from}}.",
                variables_json=["effective_rate", "effective_from"],
                approval_status="approved",
                template_version="1.0",
                effective_from=timezone.localdate(),
            )
        row = self._proposal(version="PG-RATE-NOTICE", effective_from="2026-08-01")
        row.communication_required = True
        row.save(update_fields=["communication_required"])
        outcomes = self._race(
            (row.pk, "pg-notice-a"),
            (row.pk, "pg-notice-b"),
        )
        self.assertEqual(sorted(outcomes), ["conflict", "success"])
        self.assertEqual(
            BorrowerRateNoticeObligation.objects.filter(
                interest_rate_config=row, loan_account=account
            ).count(),
            1,
        )

    def _race(self, *requests):
        barrier = Barrier(len(requests))
        checker_id = self.checker.pk

        def contender(item):
            close_old_connections()
            try:
                checker = User.objects.get(pk=checker_id)
                barrier.wait(timeout=15)
                try:
                    activate(
                        actor=checker,
                        request=self.request,
                        interest_rate_config_id=item[0],
                        idempotency_key=item[1],
                    )
                    return "success"
                except InterestRateConflict:
                    return "conflict"
            finally:
                connections["default"].close()

        with ThreadPoolExecutor(max_workers=len(requests)) as pool:
            return list(pool.map(contender, requests))
