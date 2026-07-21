"""Application-owned global-search candidate authority."""

from django.db.models import Q

from sfpcl_credit.applications.models import LoanApplication


READ_PERMISSION = "applications.loan_application.read"


def matching_applications(
    *, actor, permissions, query, related_member_ids, allow_direct_match, limit
):
    if READ_PERMISSION not in permissions:
        return []
    scope = Q(created_by_user=actor) | Q(received_by_user=actor)
    if "credit_manager" in actor.role_codes():
        scope |= Q(current_stage=LoanApplication.STAGE_CREDIT_ASSESSMENT)
    match = Q(member_id__in=related_member_ids)
    if allow_direct_match:
        match |= (
            Q(application_reference_number__iexact=query)
            | Q(member__legal_name__istartswith=query)
            | Q(member__display_name__istartswith=query)
            | Q(member__folio_number__iexact=query)
        )
    return list(
        LoanApplication.objects.select_related(
            "member", "received_by_user", "created_by_user", "updated_by_user"
        )
        .filter(scope)
        .filter(match)
        .distinct()
        .order_by("-created_at", "-loan_application_id")[:limit]
    )


__all__ = ["matching_applications"]
