"""One backend owner for direct-repayment capture, SAP posting, and allocation."""

from django.db import transaction

from sfpcl_credit.loans.modules.direct_repayment_posting import (
    capture_direct_repayment,
    mark_sap_posted,
    retained_repayment_outcome,
)
from sfpcl_credit.loans.modules.repayment_allocator import RepaymentAllocator


@transaction.atomic
def execute_direct_repayment(
    *, actor, loan_account_id, payload, idempotency_key, request=None
):
    unknown = set(payload) - {"capture", "sap_posting"}
    missing = {key for key in ("capture", "sap_posting") if not isinstance(payload.get(key), dict)}
    if unknown or missing:
        from sfpcl_credit.loans.modules.direct_repayment_posting import RepaymentValidation

        errors = {key: "Unknown field." for key in sorted(unknown)}
        errors.update({key: "Must be an object." for key in sorted(missing)})
        raise RepaymentValidation(errors)

    captured = capture_direct_repayment(
        actor=actor,
        loan_account_id=loan_account_id,
        payload=payload["capture"],
        idempotency_key=idempotency_key,
        request=request,
    )
    capture_replayed = "idempotency_replayed" in captured
    capture = captured["original_response"] if capture_replayed else captured

    mark_sap_posted(
        actor=actor,
        repayment_id=capture["repayment_id"],
        payload=payload["sap_posting"],
        request=request,
        allow_exact_replay=True,
    )
    allocated = RepaymentAllocator.allocate(
        actor=actor,
        repayment_id=capture["repayment_id"],
        payload={
            "allocation_rule": "principal_first",
            "remarks": "Allocate confirmed receipt under the approved SOP.",
        },
        idempotency_key=f"{idempotency_key}:allocation",
        request=request,
    )
    allocation_replayed = "idempotency_replayed" in allocated
    allocation = allocated["original_response"] if allocation_replayed else allocated
    return {
        "replayed": capture_replayed or allocation_replayed,
        "capture": retained_repayment_outcome(repayment_id=capture["repayment_id"]),
        "allocation": allocation,
    }


__all__ = ["execute_direct_repayment"]
