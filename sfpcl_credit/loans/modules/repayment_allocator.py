import hashlib
import json
import uuid
from decimal import Decimal

from django.db import IntegrityError, transaction
from django.utils import timezone

from sfpcl_credit.api import request_ip, request_user_agent
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.loans.models import (
    LoanAccount,
    ManualAllocationApproval,
    Repayment,
    RepaymentAllocation,
    RepaymentLedgerEntry,
    RepaymentSchedule,
    RepaymentScheduleAllocation,
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
    def allocate(
        cls,
        *,
        actor,
        repayment_id,
        payload,
        idempotency_key,
        manual=False,
        request=None,
    ):
        cleaned = cls._validate(payload, idempotency_key, manual=manual)
        payload_digest = cls._digest(
            {
                "repayment_id": str(repayment_id),
                "actor_user_id": str(actor.pk),
                "allocation_rule": cleaned["allocation_rule"],
                "remarks": cleaned["remarks"],
                "manual_approval_id": (
                    str(cleaned["approval_id"]) if cleaned["approval_id"] else None
                ),
            }
        )
        cls._require_authority(actor)
        try:
            return cls._allocate(
                actor=actor,
                repayment_id=repayment_id,
                cleaned=cleaned,
                payload_digest=payload_digest,
                request=request,
                manual=manual,
            )
        except IntegrityError as exc:
            retained = RepaymentAllocation.objects.filter(
                idempotency_key_digest=cleaned["idempotency_key_digest"]
            ).first()
            if (
                retained
                and retained.repayment_id == repayment_id
                and retained.payload_digest == payload_digest
            ):
                return cls._serialize(retained)
            raise RepaymentAllocationConflict(
                "The allocation idempotency key or repayment is already in use."
            ) from exc

    @classmethod
    @transaction.atomic
    def _allocate(
        cls, *, actor, repayment_id, cleaned, payload_digest, request, manual
    ):
        repayment = (
            Repayment.objects.select_for_update(of=("self",))
            .select_related("capture_audit", "sap_posting_obligation__posting_audit")
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
        retained_for_key = RepaymentAllocation.objects.filter(
            idempotency_key_digest=cleaned["idempotency_key_digest"]
        ).first()
        if retained_for_key is not None:
            if (
                retained_for_key.repayment_id == repayment.pk
                and retained_for_key.payload_digest == payload_digest
            ):
                return cls._serialize(retained_for_key)
            raise RepaymentAllocationConflict(
                "The idempotency key was already used for a different allocation."
            )
        retained = RepaymentAllocation.objects.filter(repayment=repayment).first()
        if retained is not None:
            raise RepaymentAllocationConflict(
                "The repayment was already allocated with a different idempotency key."
            )
        if not cls._capture_is_coherent(repayment, account):
            raise RepaymentAllocationConflict(
                "The retained receipt evidence is incomplete or changed."
            )
        if not cls._posting_is_coherent(repayment):
            raise RepaymentAllocationConflict(
                "A retained posted SAP decision is required before allocation."
            )
        if repayment.repayment_source == "subsidiary_deduction":
            try:
                subsidiary = repayment.subsidiary_deduction_evidence
            except Repayment.subsidiary_deduction_evidence.RelatedObjectDoesNotExist:
                raise RepaymentAllocationConflict(
                    "Subsidiary reconciliation evidence is required before allocation."
                )
            if (
                subsidiary.reconciliation_status != "reconciled"
                or subsidiary.treasury_verification_status != "verified"
                or repayment.bank_statement_line_id is None
            ):
                raise RepaymentAllocationConflict(
                    "Reconciled and Treasury-verified subsidiary evidence is required before allocation."
                )
        manual_approval = cls._manual_approval(
            repayment=repayment,
            approval_id=cleaned["approval_id"],
            manual=manual,
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
        cls._require_schedule_capacity(
            schedules, principal=principal, interest=interest
        )
        principal_after = account.principal_outstanding - principal
        interest_after = account.interest_outstanding - interest
        total_after = principal_after + interest_after + account.charges_outstanding
        loan_status_before = account.loan_account_status
        loan_status_after = (
            "repaid" if total_after == 0 else "partially_repaid"
        )
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
            "loan_status_before": loan_status_before,
            "loan_status_after": loan_status_after,
            "allocation_status": status,
            "exception_reason": exception_reason,
            "decision_reason_sha256": hashlib.sha256(
                cleaned["remarks"].encode()
            ).hexdigest(),
            "sap_posting_status": "posted",
            "sap_posting_audit_id": str(repayment.sap_posting_obligation.posting_audit_id),
            "manual_allocation_approval_id": (
                str(manual_approval.pk) if manual_approval else None
            ),
            "manual_allocation_approval_audit_id": (
                str(manual_approval.approval_audit_id) if manual_approval else None
            ),
            "request_id": request.headers.get("X-Request-ID", "") if request else "",
        }
        schedule_plan = cls._schedule_plan(
            schedules, principal=principal, interest=interest
        )
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
            decision_reason=cleaned["remarks"],
            idempotency_key_digest=cleaned["idempotency_key_digest"],
            payload_digest=payload_digest,
            manual_approval=manual_approval,
            loan_status_before=loan_status_before,
            loan_status_after=loan_status_after,
            allocated_by_user=actor,
            allocation_audit=audit,
            allocated_at=allocated_at,
        )
        cls._apply_to_schedules(schedule_plan, allocation=allocation)
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
        account.loan_account_status = loan_status_after
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
    def _schedule_plan(schedules, *, principal, interest):
        principal_remaining = principal
        interest_remaining = interest
        plan = []
        for schedule in schedules:
            principal_room = schedule.principal_due - schedule.paid_principal
            principal_applied = min(
                principal_remaining, max(principal_room, Decimal("0.00"))
            )
            principal_remaining -= principal_applied

            interest_room = schedule.interest_due - schedule.paid_interest
            interest_applied = min(
                interest_remaining, max(interest_room, Decimal("0.00"))
            )
            interest_remaining -= interest_applied
            if principal_applied or interest_applied:
                plan.append((schedule, principal_applied, interest_applied))
        return plan

    @staticmethod
    def _apply_to_schedules(plan, *, allocation):
        for schedule, principal_applied, interest_applied in plan:
            schedule_status_before = schedule.schedule_status
            schedule.paid_principal += principal_applied
            schedule.paid_interest += interest_applied
            paid_total = schedule.paid_principal + schedule.paid_interest + schedule.paid_charges
            schedule.schedule_status = "paid" if paid_total == schedule.total_due else "pending"
            schedule.save(
                update_fields=["paid_principal", "paid_interest", "schedule_status"]
            )
            RepaymentScheduleAllocation.objects.create(
                allocation=allocation,
                repayment_schedule=schedule,
                principal_applied=principal_applied,
                interest_applied=interest_applied,
                schedule_status_before=schedule_status_before,
                schedule_status_after=schedule.schedule_status,
            )

    @staticmethod
    def _require_schedule_capacity(schedules, *, principal, interest):
        principal_capacity = sum(
            (
                max(row.principal_due - row.paid_principal, Decimal("0.00"))
                for row in schedules
            ),
            Decimal("0.00"),
        )
        interest_capacity = sum(
            (
                max(row.interest_due - row.paid_interest, Decimal("0.00"))
                for row in schedules
            ),
            Decimal("0.00"),
        )
        if principal_capacity < principal or interest_capacity < interest:
            raise RepaymentAllocationConflict(
                "The repayment schedule cannot absorb the exact allocation."
            )

    @staticmethod
    def _validate(payload, idempotency_key, *, manual):
        allowed = {"allocation_rule", "remarks"}
        if manual:
            allowed.add("approval_id")
        errors = {key: "Unknown field." for key in sorted(set(payload) - allowed)}
        rule = str(payload.get("allocation_rule", "")).strip()
        if rule != "principal_first":
            errors["allocation_rule"] = "Must be principal_first."
        remarks = str(payload.get("remarks", "")).strip()
        if not remarks or len(remarks) > 2000:
            errors["remarks"] = "Must be nonblank and at most 2000 characters."
        key = str(idempotency_key or "").strip()
        if not key or len(key) > 200:
            errors["idempotency_key"] = "Idempotency-Key is required and must be at most 200 characters."
        approval_id = None
        if manual:
            try:
                approval_id = uuid.UUID(str(payload.get("approval_id", "")))
            except (TypeError, ValueError, AttributeError):
                errors["approval_id"] = "Must be a valid manual allocation approval UUID."
        if errors:
            raise RepaymentAllocationValidation(errors)
        return {
            "allocation_rule": rule,
            "remarks": remarks,
            "idempotency_key_digest": hashlib.sha256(key.encode()).hexdigest(),
            "approval_id": approval_id,
        }

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
    def _posting_is_coherent(repayment):
        try:
            obligation = repayment.sap_posting_obligation
        except Repayment.sap_posting_obligation.RelatedObjectDoesNotExist:
            return False
        audit = obligation.posting_audit
        if audit is None:
            return False
        evidence = audit.new_value_json or {}
        manifest = json.dumps(evidence, sort_keys=True, separators=(",", ":"))
        return (
            repayment.sap_posting_status == "posted"
            and obligation.status == "posted"
            and obligation.posted_at is not None
            and obligation.posted_by_user_id is not None
            and audit.action == "repayment.sap_posted"
            and audit.entity_type == "repayment"
            and audit.entity_id == repayment.pk
            and audit.selector_manifest_json == manifest
            and audit.selector_manifest_sha256
            == hashlib.sha256(manifest.encode()).hexdigest()
            and evidence.get("repayment_id") == str(repayment.pk)
            and evidence.get("obligation_id") == str(obligation.pk)
            and evidence.get("sap_posting_status") == "posted"
        )

    @staticmethod
    def _manual_approval(*, repayment, approval_id, manual):
        if not manual:
            if repayment.statement_match_status == "manual_match_exception":
                raise RepaymentAllocationConflict(
                    "A manually matched exception requires the manual allocation action."
                )
            return None
        approval = (
            ManualAllocationApproval.objects.select_for_update()
            .select_related("approval_audit")
            .filter(pk=approval_id)
            .first()
        )
        if approval is None:
            raise RepaymentAllocationConflict(
                "A terminal manual allocation approval is required."
            )
        evidence = approval.approval_audit.new_value_json or {}
        manifest = json.dumps(evidence, sort_keys=True, separators=(",", ":"))
        if not (
            repayment.statement_match_status == "manual_match_exception"
            and approval.repayment_id == repayment.pk
            and approval.loan_account_id == repayment.loan_account_id
            and approval.bank_statement_line_id == repayment.bank_statement_line_id
            and approval.approved_amount == repayment.amount_received
            and approval.approval_audit.action
            == "repayment.manual_allocation_approved"
            and approval.approval_audit.entity_id == approval.pk
            and approval.approval_audit.selector_manifest_json == manifest
            and approval.approval_audit.selector_manifest_sha256
            == hashlib.sha256(manifest.encode()).hexdigest()
            and evidence.get("repayment_id") == str(repayment.pk)
            and evidence.get("loan_account_id") == str(repayment.loan_account_id)
            and evidence.get("approved_amount") == f"{repayment.amount_received:.2f}"
            and evidence.get("decision") == "approved"
        ):
            raise RepaymentAllocationConflict(
                "The manual allocation approval does not cover this exact allocation."
            )
        return approval

    @staticmethod
    def _digest(value):
        canonical = json.dumps(value, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode()).hexdigest()

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
