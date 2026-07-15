"""Single nondisclosing active portal-account/member/application scope resolver."""

from dataclasses import dataclass

from sfpcl_credit.applications.models import LoanApplication
from sfpcl_credit.identity.models import PortalAccount


class PortalApplicationScopeNotFound(Exception):
    pass


@dataclass(frozen=True)
class PortalApplicationScope:
    account: PortalAccount
    application: LoanApplication


def resolve(*, actor, application_id):
    account = (
        PortalAccount.objects.select_related("member")
        .filter(
            user=actor,
            status=PortalAccount.STATUS_ACTIVE,
            member__is_deleted=False,
        )
        .first()
    )
    application = (
        LoanApplication.objects.select_related("member")
        .filter(pk=application_id, member_id=account.member_id if account else None)
        .first()
    )
    if account is None or application is None:
        raise PortalApplicationScopeNotFound
    return PortalApplicationScope(account=account, application=application)
