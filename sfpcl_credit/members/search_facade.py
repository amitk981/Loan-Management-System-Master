"""Member-owned, scope-first inputs for global search."""

from django.db.models import Q

from sfpcl_credit.members.models import BankAccount, Member
from sfpcl_credit.members.modules.member_authority import member_scope_predicate
from sfpcl_credit.members.protected_identity import identity_hash


READ_PERMISSION = "members.member.read"
PAN_SEARCH_PERMISSION = "members.sensitive.reveal_pan"
AADHAAR_SEARCH_PERMISSION = "members.sensitive.reveal_aadhaar"


def matching_bank_member_ids(*, actor, permissions, query):
    if READ_PERMISSION not in permissions or len(query) != 4 or not query.isdigit():
        return frozenset()
    scoped_ids = Member.objects.filter(
        is_deleted=False
    ).filter(
        member_scope_predicate(actor_user=actor, permission=READ_PERMISSION)
    ).values("member_id")
    return frozenset(
        BankAccount.objects.filter(
            owner_party_type="member",
            owner_party_id__in=scoped_ids,
            account_number_last4=query,
        ).values_list("owner_party_id", flat=True)
    )


def matching_sensitive_member_ids(*, actor, permissions, query):
    if READ_PERMISSION not in permissions:
        return frozenset()
    upper = query.upper()
    predicate = Q(pk__in=[])
    if (
        len(upper) == 10
        and upper[:5].isalpha()
        and upper[5:9].isdigit()
        and upper[-1].isalpha()
        and PAN_SEARCH_PERMISSION in permissions
    ):
        predicate |= Q(pan_hash=identity_hash(upper))
    elif len(query) == 12 and query.isdigit() and AADHAAR_SEARCH_PERMISSION in permissions:
        predicate |= Q(aadhaar_hash=identity_hash(query))
    elif len(query) == 4 and query.isdigit():
        predicate |= Q(number_of_shares=int(query))
        if AADHAAR_SEARCH_PERMISSION in permissions:
            predicate |= Q(aadhaar_last4=query)
    elif query.isdigit() and len(query) < 10:
        predicate |= Q(number_of_shares=int(query))
    elif query.isdigit() and len(query) >= 10:
        predicate |= Q(mobile_number=query)
    elif "@" in query:
        predicate |= Q(email__iexact=query)
    return frozenset(
        Member.objects.filter(is_deleted=False)
        .filter(member_scope_predicate(actor_user=actor, permission=READ_PERMISSION))
        .filter(predicate)
        .values_list("member_id", flat=True)
    )


def matching_members(*, actor, permissions, query, related_member_ids, limit):
    if READ_PERMISSION not in permissions:
        return []
    upper = query.upper()
    if len(upper) == 10 and upper[:5].isalpha() and upper[5:9].isdigit() and upper[-1].isalpha():
        predicate = (
            Q(pan_hash=identity_hash(upper))
            if PAN_SEARCH_PERMISSION in permissions
            else Q(pk__in=[])
        )
    elif len(query) == 12 and query.isdigit():
        predicate = (
            Q(aadhaar_hash=identity_hash(query))
            if AADHAAR_SEARCH_PERMISSION in permissions
            else Q(pk__in=[])
        )
    elif len(query) == 4 and query.isdigit():
        predicate = Q(number_of_shares=int(query))
        if AADHAAR_SEARCH_PERMISSION in permissions:
            predicate |= Q(aadhaar_last4=query)
    elif query.isdigit() and len(query) < 10:
        predicate = Q(number_of_shares=int(query))
    elif query.isdigit() and len(query) >= 10:
        predicate = Q(mobile_number=query)
    elif "@" in query:
        predicate = Q(email__iexact=query)
    else:
        predicate = (
            Q(legal_name__istartswith=query)
            | Q(display_name__istartswith=query)
            | Q(member_number__iexact=query)
            | Q(folio_number__iexact=query)
        )
        if query.isdigit():
            predicate |= Q(number_of_shares=int(query))
    predicate |= Q(member_id__in=related_member_ids)
    return list(
        Member.objects.select_related("created_by_user", "updated_by_user")
        .filter(is_deleted=False)
        .filter(member_scope_predicate(actor_user=actor, permission=READ_PERMISSION))
        .filter(predicate)
        .order_by("legal_name", "member_id")[:limit]
    )


__all__ = [
    "matching_bank_member_ids",
    "matching_members",
    "matching_sensitive_member_ids",
]
