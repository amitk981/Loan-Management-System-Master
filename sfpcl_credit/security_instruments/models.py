import uuid

from django.db import models
from django.utils import timezone


class SecurityPackage(models.Model):
    STATUS_PENDING = "pending"
    STATUS_COMPLETE = "complete"
    STATUS_RELEASED = "released"

    security_package_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    loan_application = models.OneToOneField(
        "applications.LoanApplication",
        on_delete=models.PROTECT,
        related_name="security_package",
    )
    loan_account_id = models.UUIDField(blank=True, null=True)
    security_status = models.CharField(max_length=60, default=STATUS_PENDING, db_index=True)
    physical_share_security_required_flag = models.BooleanField(default=False)
    demat_pledge_required_flag = models.BooleanField(default=False)
    poa_required_flag = models.BooleanField(default=True)
    blank_cheque_required_flag = models.BooleanField(default=False)
    cancelled_cheque_required_flag = models.BooleanField(default=False)
    security_summary = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "security_packages"
        indexes = [
            models.Index(
                fields=["loan_application", "security_status"],
                name="idx_security_pkg_app_status",
            )
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(security_status__in=["pending", "complete", "released"]),
                name="security_package_status_bounded",
            ),
            models.CheckConstraint(
                check=models.Q(loan_account_id__isnull=True),
                name="security_package_account_requires_009c",
            ),
            models.CheckConstraint(
                check=models.Q(poa_required_flag=True),
                name="security_package_poa_always_required",
            ),
        ]


class PowerOfAttorney(models.Model):
    EXECUTION_PENDING = "pending"
    EXECUTION_EXECUTED = "executed"
    STATUS_DRAFT = "draft"
    STATUS_ACTIVE = "active"

    power_of_attorney_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    security_package = models.OneToOneField(
        SecurityPackage, on_delete=models.PROTECT, related_name="power_of_attorney"
    )
    borrower_member = models.ForeignKey(
        "members.Member", on_delete=models.PROTECT, related_name="powers_of_attorney"
    )
    nominee = models.ForeignKey(
        "members.Nominee", on_delete=models.PROTECT, related_name="powers_of_attorney"
    )
    attorney_user = models.ForeignKey(
        "identity.User", on_delete=models.PROTECT, related_name="attorney_appointments"
    )
    purpose_summary = models.TextField()
    loan_document = models.ForeignKey(
        "legal_documents.LoanDocument",
        on_delete=models.PROTECT,
        related_name="powers_of_attorney",
    )
    stamp_duty_record = models.ForeignKey(
        "legal_documents.StampDutyRecord",
        on_delete=models.PROTECT,
        related_name="powers_of_attorney",
    )
    notarisation_record = models.ForeignKey(
        "legal_documents.NotarisationRecord",
        on_delete=models.PROTECT,
        related_name="powers_of_attorney",
    )
    execution_status = models.CharField(max_length=60, db_index=True)
    effective_from = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=60, db_index=True)
    released_at = models.DateTimeField(blank=True, null=True)
    prepared_by_user = models.ForeignKey(
        "identity.User", on_delete=models.PROTECT, related_name="prepared_powers_of_attorney"
    )
    verified_by_user = models.ForeignKey(
        "identity.User", blank=True, null=True, on_delete=models.PROTECT,
        related_name="verified_powers_of_attorney",
    )
    activation_evidence_json = models.JSONField(default=dict, blank=True)
    activation_workflow_event_id = models.UUIDField(blank=True, null=True)
    legacy_activation_evidence = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "power_of_attorneys"
        indexes = [
            models.Index(fields=["execution_status", "status"], name="idx_poa_exec_status"),
            models.Index(fields=["borrower_member", "nominee"], name="idx_poa_parties"),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(execution_status__in=["pending", "executed"]),
                name="poa_execution_status_bounded",
            ),
            models.CheckConstraint(
                check=models.Q(status__in=["draft", "active"]),
                name="poa_status_bounded",
            ),
            models.CheckConstraint(
                check=models.Q(released_at__isnull=True),
                name="poa_release_requires_later_slice",
            ),
            models.CheckConstraint(
                check=(
                    models.Q(status="draft")
                    | models.Q(
                        status="active",
                        execution_status="executed",
                        effective_from__isnull=False,
                        verified_by_user__isnull=False,
                    )
                    & (
                        models.Q(
                            legacy_activation_evidence=False,
                            activation_workflow_event_id__isnull=False,
                        )
                        | models.Q(
                            legacy_activation_evidence=True,
                            activation_workflow_event_id__isnull=True,
                        )
                    )
                ),
                name="active_poa_has_execution_verifier",
            ),
        ]


class SH4ShareTransferForm(models.Model):
    STATUS_PENDING = "pending"
    STATUS_SIGNED = "signed"
    STATUS_HELD_IN_CUSTODY = "held_in_custody"
    STATUSES = {STATUS_PENDING, STATUS_SIGNED, STATUS_HELD_IN_CUSTODY}

    sh4_share_transfer_form_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    security_package = models.OneToOneField(
        SecurityPackage, on_delete=models.PROTECT, related_name="sh4_share_transfer_form"
    )
    member = models.ForeignKey(
        "members.Member", on_delete=models.PROTECT, related_name="sh4_share_transfer_forms"
    )
    witness = models.ForeignKey(
        "applications.Witness", on_delete=models.PROTECT,
        related_name="sh4_share_transfer_forms",
    )
    shareholding = models.ForeignKey(
        "members.Shareholding", on_delete=models.PROTECT,
        related_name="sh4_share_transfer_forms",
    )
    share_count = models.PositiveIntegerField(blank=True, null=True)
    loan_document = models.ForeignKey(
        "legal_documents.LoanDocument", on_delete=models.PROTECT,
        related_name="sh4_share_transfer_forms",
    )
    form_status = models.CharField(max_length=60, db_index=True)
    custody_location = models.CharField(max_length=255, blank=True, null=True)
    signed_at = models.DateField(blank=True, null=True)
    returned_at = models.DateField(blank=True, null=True)
    invocation_approval_case_id = models.UUIDField(blank=True, null=True)
    prepared_by_user = models.ForeignKey(
        "identity.User", on_delete=models.PROTECT, related_name="prepared_sh4_forms"
    )
    custodian_user = models.ForeignKey(
        "identity.User", blank=True, null=True, on_delete=models.PROTECT,
        related_name="custodied_sh4_forms",
    )
    custody_evidence_json = models.JSONField(default=dict, blank=True)
    custody_workflow_event_id = models.UUIDField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "sh4_share_transfer_forms"
        indexes = [
            models.Index(fields=["form_status", "signed_at"], name="idx_sh4_status_signed"),
            models.Index(fields=["member", "witness"], name="idx_sh4_parties"),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(
                    form_status__in=["held_in_custody", "pending", "signed"]
                ),
                name="sh4_form_status_bounded",
            ),
            models.CheckConstraint(
                check=models.Q(share_count__isnull=True) | models.Q(share_count__gt=0),
                name="sh4_share_count_positive",
            ),
            models.CheckConstraint(
                check=models.Q(returned_at__isnull=True),
                name="sh4_return_requires_later_slice",
            ),
            models.CheckConstraint(
                check=models.Q(invocation_approval_case_id__isnull=True),
                name="sh4_invocation_requires_later_slice",
            ),
            models.CheckConstraint(
                check=(
                    models.Q(
                        form_status="pending", signed_at__isnull=True,
                        custody_location__isnull=True, custodian_user__isnull=True,
                        custody_workflow_event_id__isnull=True,
                    )
                    | models.Q(
                        form_status="signed", signed_at__isnull=False,
                        custody_location__isnull=True, custodian_user__isnull=True,
                        custody_workflow_event_id__isnull=True,
                    )
                    | models.Q(
                        form_status="held_in_custody", signed_at__isnull=False,
                        custody_location__isnull=False, custodian_user__isnull=False,
                        custody_workflow_event_id__isnull=False,
                    )
                ),
                name="sh4_status_evidence_consistent",
            ),
        ]


class CDSLSharePledge(models.Model):
    PRF_PREPARED = "prepared"
    PRF_SUBMITTED = "submitted"
    ACCEPTANCE_PENDING = "pending"
    ACCEPTANCE_ACCEPTED = "accepted"
    ACCEPTANCE_REJECTED = "rejected"
    STATUS_PENDING = "pending"
    STATUS_CREATED = "created"

    cdsl_share_pledge_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    security_package = models.OneToOneField(
        SecurityPackage, on_delete=models.PROTECT, related_name="cdsl_share_pledge"
    )
    pledgor_member = models.ForeignKey(
        "members.Member", on_delete=models.PROTECT, related_name="cdsl_share_pledges"
    )
    pledgee_entity_name = models.CharField(max_length=255)
    pledgor_bo_account_encrypted = models.TextField()
    pledgor_bo_account_hash = models.CharField(max_length=128, db_index=True)
    pledgee_bo_account_encrypted = models.TextField(blank=True, null=True)
    pledgee_bo_account_hash = models.CharField(max_length=128, blank=True, null=True)
    pledgor_dp_name = models.CharField(max_length=255, blank=True, null=True)
    pledgee_dp_name = models.CharField(max_length=255, blank=True, null=True)
    prf_status = models.CharField(max_length=60, db_index=True)
    pledge_sequence_number = models.CharField(
        max_length=120, blank=True, null=True, unique=True
    )
    pledge_acceptance_status = models.CharField(max_length=60, db_index=True)
    pledged_share_count = models.PositiveIntegerField(blank=True, null=True)
    agreement_number = models.CharField(max_length=120, blank=True, null=True)
    pledge_status = models.CharField(max_length=60, db_index=True)
    future_shares_pledged_flag = models.BooleanField(default=True)
    evidence_document = models.ForeignKey(
        "documents.DocumentFile", blank=True, null=True, on_delete=models.PROTECT,
        related_name="cdsl_share_pledges",
    )
    created_at_cdsl = models.DateTimeField(blank=True, null=True)
    invoked_at = models.DateTimeField(blank=True, null=True)
    unpledged_at = models.DateTimeField(blank=True, null=True)
    prepared_by_user = models.ForeignKey(
        "identity.User", on_delete=models.PROTECT, related_name="prepared_cdsl_pledges"
    )
    verified_by_user = models.ForeignKey(
        "identity.User", blank=True, null=True, on_delete=models.PROTECT,
        related_name="verified_cdsl_pledges",
    )
    acceptance_evidence_json = models.JSONField(default=dict, blank=True)
    acceptance_workflow_event_id = models.UUIDField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "cdsl_share_pledges"
        indexes = [
            models.Index(fields=["prf_status", "pledge_acceptance_status"], name="idx_cdsl_prf_accept"),
            models.Index(fields=["pledge_status", "created_at_cdsl"], name="idx_cdsl_status_created"),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(prf_status__in=["prepared", "submitted"]),
                name="cdsl_prf_status_bounded",
            ),
            models.CheckConstraint(
                check=models.Q(pledge_acceptance_status__in=["pending", "accepted", "rejected"]),
                name="cdsl_accept_status_bounded",
            ),
            models.CheckConstraint(
                check=models.Q(pledge_status__in=["pending", "created"]),
                name="cdsl_pledge_status_bounded",
            ),
            models.CheckConstraint(
                check=models.Q(pledged_share_count__isnull=True) | models.Q(pledged_share_count__gt=0),
                name="cdsl_share_count_positive",
            ),
            models.CheckConstraint(
                check=models.Q(future_shares_pledged_flag=True),
                name="cdsl_future_shares_pledged",
            ),
            models.CheckConstraint(
                check=models.Q(invoked_at__isnull=True),
                name="cdsl_invocation_requires_011i",
            ),
            models.CheckConstraint(
                check=models.Q(unpledged_at__isnull=True),
                name="cdsl_unpledge_requires_011i",
            ),
            models.CheckConstraint(
                check=(
                    models.Q(verified_by_user__isnull=True)
                    | ~models.Q(verified_by_user=models.F("prepared_by_user"))
                ),
                name="cdsl_distinct_maker_checker",
            ),
            models.CheckConstraint(
                check=(
                    models.Q(
                        pledge_acceptance_status="pending",
                        pledge_status="pending",
                        verified_by_user__isnull=True,
                        acceptance_workflow_event_id__isnull=True,
                        created_at_cdsl__isnull=True,
                    )
                    | models.Q(
                        pledge_acceptance_status="accepted",
                        pledge_status="created",
                        prf_status="submitted",
                        pledge_sequence_number__isnull=False,
                        pledgee_bo_account_encrypted__isnull=False,
                        pledgor_dp_name__isnull=False,
                        pledgee_dp_name__isnull=False,
                        pledged_share_count__isnull=False,
                        agreement_number__isnull=False,
                        evidence_document__isnull=False,
                        verified_by_user__isnull=False,
                        acceptance_workflow_event_id__isnull=False,
                        created_at_cdsl__isnull=False,
                    )
                    | models.Q(
                        pledge_acceptance_status="rejected",
                        pledge_status="pending",
                        prf_status="submitted",
                        pledge_sequence_number__isnull=False,
                        pledgee_bo_account_encrypted__isnull=False,
                        pledgor_dp_name__isnull=False,
                        pledgee_dp_name__isnull=False,
                        evidence_document__isnull=False,
                        verified_by_user__isnull=False,
                        acceptance_workflow_event_id__isnull=False,
                        created_at_cdsl__isnull=True,
                    )
                ),
                name="cdsl_terminal_evidence_consistent",
            ),
        ]


class BlankDatedCheque(models.Model):
    STATUS_COLLECTED = "collected"
    STATUS_HELD = "held"

    blank_dated_cheque_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    security_package = models.OneToOneField(
        SecurityPackage, on_delete=models.PROTECT, related_name="blank_dated_cheque"
    )
    member = models.ForeignKey(
        "members.Member", on_delete=models.PROTECT, related_name="blank_dated_cheques"
    )
    bank_account = models.ForeignKey(
        "members.BankAccount", on_delete=models.PROTECT, related_name="blank_dated_cheques"
    )
    cancelled_cheque = models.ForeignKey(
        "members.CancelledCheque", on_delete=models.PROTECT,
        related_name="blank_dated_security_cheques",
    )
    cheque_number_encrypted = models.TextField()
    cheque_number_hash = models.CharField(max_length=128, unique=True)
    document = models.ForeignKey(
        "documents.DocumentFile", blank=True, null=True, on_delete=models.PROTECT,
        related_name="blank_dated_cheques",
    )
    cheque_status = models.CharField(max_length=60, db_index=True)
    custody_location = models.CharField(max_length=255, blank=True, null=True)
    collected_at = models.DateField()
    prepared_by_user = models.ForeignKey(
        "identity.User", on_delete=models.PROTECT, related_name="prepared_blank_cheques"
    )
    custodian_user = models.ForeignKey(
        "identity.User", blank=True, null=True, on_delete=models.PROTECT,
        related_name="custodied_blank_cheques",
    )
    custody_evidence_json = models.JSONField(default=dict, blank=True)
    custody_workflow_event_id = models.UUIDField(blank=True, null=True)
    invocation_approval_case_id = models.UUIDField(blank=True, null=True)
    presented_date = models.DateField(blank=True, null=True)
    amount_presented = models.DecimalField(
        max_digits=18, decimal_places=2, blank=True, null=True
    )
    returned_at = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "blank_dated_cheques"
        indexes = [
            models.Index(fields=["cheque_status", "collected_at"], name="idx_blank_cheque_status"),
            models.Index(fields=["member", "bank_account"], name="idx_blank_cheque_bank"),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(cheque_status__in=["collected", "held"]),
                name="blank_cheque_status_bounded",
            ),
            models.CheckConstraint(
                check=models.Q(invocation_approval_case_id__isnull=True),
                name="blank_cheque_invocation_requires_later",
            ),
            models.CheckConstraint(
                check=models.Q(presented_date__isnull=True)
                & models.Q(amount_presented__isnull=True),
                name="blank_cheque_presentment_requires_later",
            ),
            models.CheckConstraint(
                check=models.Q(returned_at__isnull=True),
                name="blank_cheque_return_requires_later",
            ),
            models.CheckConstraint(
                check=(
                    models.Q(
                        cheque_status="collected", custody_location__isnull=True,
                        custodian_user__isnull=True, custody_workflow_event_id__isnull=True,
                    )
                    | models.Q(
                        cheque_status="held", custody_location__isnull=False,
                        custodian_user__isnull=False, custody_workflow_event_id__isnull=False,
                    )
                ),
                name="blank_cheque_custody_consistent",
            ),
            models.CheckConstraint(
                check=models.Q(custodian_user__isnull=True)
                | ~models.Q(custodian_user=models.F("prepared_by_user")),
                name="blank_cheque_distinct_maker_checker",
            ),
        ]
