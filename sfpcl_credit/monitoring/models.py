import uuid

from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone


class DpdOperationalBucketScheme(models.Model):
    dpd_operational_bucket_scheme_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    version = models.CharField(max_length=40, unique=True)
    effective_from = models.DateField(db_index=True)
    effective_to = models.DateField(null=True, blank=True, db_index=True)
    first_upper_days = models.PositiveIntegerField(default=30)
    second_upper_days = models.PositiveIntegerField(default=60)
    third_upper_days = models.PositiveIntegerField(default=90)
    status = models.CharField(max_length=20, default="active", db_index=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "dpd_operational_bucket_schemes"
        indexes = [
            models.Index(
                fields=["status", "effective_from", "effective_to"],
                name="idx_dpd_scheme_effective",
            )
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(effective_to__isnull=True)
                | models.Q(effective_to__gte=models.F("effective_from")),
                name="dpd_scheme_period_order",
            ),
            models.CheckConstraint(
                check=models.Q(
                    first_upper_days=30,
                    second_upper_days=60,
                    third_upper_days=90,
                ),
                name="dpd_scheme_bounds_order",
            ),
            models.CheckConstraint(
                check=models.Q(status__in=("active", "retired")),
                name="dpd_scheme_status_bounded",
            ),
        ]


class AppendOnlyDpdStatusQuerySet(models.QuerySet):
    def update(self, **kwargs):
        raise ValidationError({"dpd_status": "DPD snapshots are append-only."})

    def bulk_update(self, objs, fields, batch_size=None):
        raise ValidationError({"dpd_status": "DPD snapshots are append-only."})

    def delete(self):
        raise ValidationError({"dpd_status": "DPD snapshots are append-only."})


class DpdStatus(models.Model):
    dpd_status_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    loan_account = models.ForeignKey(
        "loans.LoanAccount", on_delete=models.PROTECT, related_name="dpd_statuses"
    )
    as_of_date = models.DateField(db_index=True)
    days_past_due = models.PositiveIntegerField()
    sop_bucket = models.CharField(max_length=40, db_index=True)
    standard_bucket = models.CharField(max_length=40, null=True, blank=True, db_index=True)
    principal_overdue_amount = models.DecimalField(max_digits=18, decimal_places=2)
    interest_overdue_amount = models.DecimalField(max_digits=18, decimal_places=2)
    total_overdue_amount = models.DecimalField(max_digits=18, decimal_places=2)
    earliest_unpaid_due_date = models.DateField(null=True, blank=True)
    calculation_version = models.CharField(max_length=40, default="DPD-CALC-1")
    operational_scheme = models.ForeignKey(
        DpdOperationalBucketScheme,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="dpd_statuses",
    )
    calculation_inputs_json = models.JSONField(default=dict)
    calculated_by_user = models.ForeignKey(
        "identity.User", on_delete=models.PROTECT, related_name="calculated_dpd_statuses"
    )
    calculation_audit = models.OneToOneField(
        "identity.AuditLog", on_delete=models.PROTECT, related_name="dpd_status"
    )
    created_at = models.DateTimeField(default=timezone.now)

    objects = AppendOnlyDpdStatusQuerySet.as_manager()

    class Meta:
        db_table = "dpd_statuses"
        ordering = ["-as_of_date", "-created_at", "-dpd_status_id"]
        indexes = [
            models.Index(
                fields=["loan_account", "as_of_date"], name="idx_dpd_account_asof"
            )
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["loan_account", "as_of_date"], name="uniq_dpd_account_asof"
            ),
            models.CheckConstraint(
                check=models.Q(principal_overdue_amount__gte=0)
                & models.Q(interest_overdue_amount__gte=0)
                & models.Q(total_overdue_amount__gte=0),
                name="dpd_amounts_nonnegative",
            ),
            models.CheckConstraint(
                check=models.Q(
                    total_overdue_amount=models.F("principal_overdue_amount")
                    + models.F("interest_overdue_amount")
                ),
                name="dpd_total_matches_parts",
            ),
        ]

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValidationError({"dpd_status": "DPD snapshots are append-only."})
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError({"dpd_status": "DPD snapshots are append-only."})
