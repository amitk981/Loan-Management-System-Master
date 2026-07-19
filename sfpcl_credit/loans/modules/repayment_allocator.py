import hashlib
import json
import uuid
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from sfpcl_credit.api import request_ip, request_user_agent
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.loans.models import (
    LoanAccount,
    Repayment,
    RepaymentAllocation,
    RepaymentLedgerEntry,
    RepaymentSchedule,
)


ALLOCATE_PERMISSION = "finance.repayment.allocate"
ALLOCATE_ROLES = {"credit_manager", "accounts_head"}
SERVICEABLE_STATUSES = {"active", "partially_repaid", "overdue", "grace_period", "extended"}


class RepaymentAllocationValidation(Exception):
    def __init__(self, field_errors):
        self.field_errors = field_errors


class RepaymentAllocationPermissionDenied(Exception):
    pass


class RepaymentAllocationNotFound(Exception):
    pass


class RepaymentAllocationConflict(Exception):
    pass


class RepaymentAllocator:
    @classmethod
    @transaction.atomic
    def allocate(cls, *, actor, repayment_id, payload, request=None):
        cls._validate(payload)
        cls._require_authority(actor)
        repayment = (
            Repayment.objects.select_for_update()
            .select_related("capture_audit")
            .filter(pk=repayment_id)
            .first()
        )
        if repayment is None:
            raise RepaymentAllocationNotFound
        account = (
            LoanAccount.objects.select_for_update()
            .filter(pk=repayment.loan_account_id)
            .first()
        )
        if account is None or not cls._in_scope(actor, account):
            raise RepaymentAllocationNotFound
        retained = RepaymentAllocation.objects.filter(repayment=repayment).first()
        if retained is not None:
            return cls._serialize(retained)
        if not cls._capture_is_coherent(repayment, account):
            raise RepaymentAllocationConflict(
                "The retained receipt evidence is incomplete or changed."
            )
        if repayment.allocation_status != "pending":
            raise RepaymentAllocationConflict("The repayment is not pending allocation.")
        if account.loan_account_status not in SERVICEABLE_STATUSES:
            raise RepaymentAllocationConflict("The loan is not eligible for repayment allocation.")
        if account.total_outstanding != (
            account.principal_outstanding
            + account.interest_outstanding
            + account.charges_outstanding
        ):
            raise RepaymentAllocationConflict("The retained loan balance is internally inconsistent.")

        schedules = list(
            RepaymentSchedule.objects.select_for_update()
            .filter(loan_account=account)
            .order_by("installment_number", "repayment_schedule_id")
        )
        amount = repayment.amount_received
        principal = min(amount, account.principal_outstanding)
        remaining = amount - principal
        interest = min(remaining, account.interest_outstanding)
        unallocated = remaining - interest
        principal_after = account.principal_outstanding - principal
        interest_after = account.interest_outstanding - interest
        total_after = principal_after + interest_after + account.charges_outstanding
        allocated_at = timezone.now()
        allocation_id = uuid.uuid4()
        status = "allocated_with_exception" if unallocated else "allocated"
        exception_reason = "charge_or_excess_policy_not_configured" if unallocated else None
        evidence = {
            "repayment_allocation_id": str(allocation_id),
            "repayment_id": str(repayment.pk),
            "loan_account_id": str(account.pk),
            "actor_user_id": str(actor.pk),
            "actor_role_codes": auth_service.effective_role_codes(actor),
            "allocation_rule": "principal_first_v1",
            "amount_received": f"{amount:.2f}",
            "allocated_to_principal": f"{principal:.2f}",
            "allocated_to_interest": f"{interest:.2f}",
            "allocated_to_charges": "0.00",
            "unallocated_amount": f"{unallocated:.2f}",
            "principal_before": f"{account.principal_outstanding:.2f}",
            "principal_after": f"{principal_after:.2f}",
            "interest_before": f"{account.interest_outstanding:.2f}",
            "interest_after": f"{interest_after:.2f}",
            "total_before": f"{account.total_outstanding:.2f}",
            "total_after": f"{total_after:.2f}",
            "allocation_status": status,
            "exception_reason": exception_reason,
            "request_id": request.headers.get("X-Request-ID", "") if request else "",
        }
        cls._apply_to_schedules(schedules, principal=principal, interest=interest)
        manifest = json.dumps(evidence, sort_keys=True, separators=(",", ":"))
        audit = AuditLog.objects.create(
            actor_user=actor,
            actor_type="user",
            action="repayment.allocated",
            entity_type="repayment_allocation",
            entity_id=allocation_id,
            old_value_json=None,
            new_value_json=evidence,
            selector_manifest_json=manifest,
            selector_manifest_sha256=hashlib.sha256(manifest.encode()).hexdigest(),
            ip_address=request_ip(request) if request else "",
            user_agent=request_user_agent(request) if request else "",
        )
        allocation = RepaymentAllocation.objects.create(
            repayment_allocation_id=allocation_id,
            repayment=repayment,
            loan_account=account,
            repayment_schedule=schedules[0] if schedules else None,
            allocated_to_principal=principal,
            allocated_to_interest=interest,
            allocated_to_charges=Decimal("0.00"),
            unallocated_amount=unallocated,
            principal_before=account.principal_outstanding,
            principal_after=principal_after,
            interest_before=account.interest_outstanding,
            interest_after=interest_after,
            charges_before=account.charges_outstanding,
            charges_after=account.charges_outstanding,
            total_before=account.total_outstanding,
            total_after=total_after,
            exception_reason=exception_reason,
            allocated_by_user=actor,
            allocation_audit=audit,
            allocated_at=allocated_at,
        )
        RepaymentLedgerEntry.objects.create(
            allocation=allocation,
            loan_account=account,
            transaction_date=repayment.received_date,
            credit_amount=principal + interest,
            principal_balance=principal_after,
            interest_balance=interest_after,
            charges_balance=account.charges_outstanding,
            total_outstanding=total_after,
            actor_user=actor,
            actor_display_name=actor.full_name,
            created_at=allocated_at,
        )
        account.principal_outstanding = principal_after
        account.interest_outstanding = interest_after
        account.total_outstanding = total_after
        if total_after == 0:
            account.loan_account_status = "repaid"
        elif principal or interest:
            account.loan_account_status = "partially_repaid"
        account.save(
            update_fields=[
                "principal_outstanding",
                "interest_outstanding",
                "total_outstanding",
                "loan_account_status",
            ]
        )
        repayment.allocation_status = status
        repayment.save(update_fields=["allocation_status"])
        return cls._serialize(allocation)

    @staticmethod
    def _apply_to_schedules(schedules, *, principal, interest):
        principal_remaining = principal
        interest_remaining = interest
        for schedule in schedules:
            principal_room = schedule.principal_due - schedule.paid_principal
            principal_applied = min(
                principal_remaining, max(principal_room, Decimal("0.00"))
            )
            schedule.paid_principal += principal_applied
            principal_remaining -= principal_applied

            interest_room = schedule.interest_due - schedule.paid_interest
            interest_applied = min(
                interest_remaining, max(interest_room, Decimal("0.00"))
            )
            schedule.paid_interest += interest_applied
            interest_remaining -= interest_applied
            paid_total = schedule.paid_principal + schedule.paid_interest + schedule.paid_charges
            schedule.schedule_status = "paid" if paid_total == schedule.total_due else "pending"
            if principal_applied or interest_applied:
                schedule.save(
                    update_fields=["paid_principal", "paid_interest", "schedule_status"]
                )

    @staticmethod
    def _validate(payload):
        allowed = {"allocation_rule", "remarks"}
        errors = {key: "Unknown field." for key in sorted(set(payload) - allowed)}
        rule = str(payload.get("allocation_rule", "")).strip()
        if rule != "principal_first":
            errors["allocation_rule"] = "Must be principal_first."
        remarks = str(payload.get("remarks", "")).strip()
        if not remarks or len(remarks) > 2000:
            errors["remarks"] = "Must be nonblank and at most 2000 characters."
        if errors:
            raise RepaymentAllocationValidation(errors)
        return {"allocation_rule": rule, "remarks": remarks}

    @staticmethod
    def _require_authority(actor):
        if (
            not actor.can_authenticate()
            or ALLOCATE_PERMISSION not in auth_service.effective_permission_codes(actor)
            or not set(auth_service.effective_role_codes(actor)).intersection(ALLOCATE_ROLES)
        ):
            raise RepaymentAllocationPermissionDenied

    @staticmethod
    def _in_scope(actor, account):
        roles = set(auth_service.effective_role_codes(actor))
        return "accounts_head" in roles or (
            "credit_manager" in roles and account.loan_account_status in SERVICEABLE_STATUSES
        )

    @staticmethod
    def _capture_is_coherent(repayment, account):
        audit = repayment.capture_audit
        evidence = audit.new_value_json or {}
        manifest = json.dumps(evidence, sort_keys=True, separators=(",", ":"))
        return (
            repayment.member_id == account.member_id
            and audit.action == "repayment.receipt_created"
            and audit.entity_type == "repayment"
            and audit.entity_id == repayment.pk
            and audit.actor_user_id == repayment.captured_by_user_id
            and audit.selector_manifest_json == manifest
            and audit.selector_manifest_sha256
            == hashlib.sha256(manifest.encode()).hexdigest()
            and evidence.get("repayment_id") == str(repayment.pk)
            and evidence.get("loan_account_id") == str(account.pk)
            and evidence.get("member_id") == str(account.member_id)
            and evidence.get("amount_received") == f"{repayment.amount_received:.2f}"
            and evidence.get("allocation_status") == "pending"
        )

    @staticmethod
    def _serialize(allocation):
        return {
            "repayment_allocation_id": str(allocation.pk),
            "repayment_id": str(allocation.repayment_id),
            "allocation_rule": allocation.allocation_rule,
            "allocation_rule_version": allocation.allocation_rule_version,
            "allocation_status": allocation.repayment.allocation_status,
            "allocated_to_principal": f"{allocation.allocated_to_principal:.2f}",
            "allocated_to_interest": f"{allocation.allocated_to_interest:.2f}",
            "allocated_to_charges": f"{allocation.allocated_to_charges:.2f}",
            "unallocated_amount": f"{allocation.unallocated_amount:.2f}",
            "exception_reason": allocation.exception_reason,
            "loan_account": {
                "principal_outstanding": f"{allocation.principal_after:.2f}",
                "interest_outstanding": f"{allocation.interest_after:.2f}",
                "charges_outstanding": f"{allocation.charges_after:.2f}",
                "total_outstanding": f"{allocation.total_after:.2f}",
            },
        }


__all__ = [
    "RepaymentAllocator",
    "RepaymentAllocationConflict",
    "RepaymentAllocationNotFound",
    "RepaymentAllocationPermissionDenied",
    "RepaymentAllocationValidation",
]
