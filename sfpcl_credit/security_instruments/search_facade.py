"""Authority-enforcing global-search inputs owned by security instruments."""

import uuid

from sfpcl_credit.security_instruments.models import (
    BlankDatedCheque,
    CDSLSharePledge,
    SH4ShareTransferForm,
)
from sfpcl_credit.shared.encryption import FieldEncryption


PACKAGE_READ = "security.package.read"
BLANK_CHEQUE_MANAGE = "security.blank_cheque.manage"
SH4_MANAGE = "security.sh4.manage"
CDSL_MANAGE = "security.cdsl_pledge.manage"


def matching_member_ids(*, actor, permissions, query):
    """Return member ids only for security inputs the actor may resolve."""
    del actor  # Effective permissions are frozen by the aggregate for this request.
    member_ids = set()
    if BLANK_CHEQUE_MANAGE in permissions:
        member_ids.update(
            BlankDatedCheque.objects.filter(
                cheque_number_hash=FieldEncryption.hash_for_lookup(
                    "blank_cheque.cheque_number", query
                )
            ).values_list("member_id", flat=True)
        )
    if PACKAGE_READ in permissions or CDSL_MANAGE in permissions:
        member_ids.update(
            CDSLSharePledge.objects.filter(
                pledge_sequence_number__iexact=query
            ).values_list("pledgor_member_id", flat=True)
        )
    if PACKAGE_READ in permissions or SH4_MANAGE in permissions:
        try:
            sh4_id = uuid.UUID(query)
        except (ValueError, TypeError, AttributeError):
            sh4_id = None
        if sh4_id:
            member_ids.update(
                SH4ShareTransferForm.objects.filter(pk=sh4_id).values_list(
                    "member_id", flat=True
                )
            )
    return frozenset(member_ids)


__all__ = ["matching_member_ids"]
