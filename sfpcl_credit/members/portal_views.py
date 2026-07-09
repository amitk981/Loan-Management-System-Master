from django.views.decorators.http import require_GET

from sfpcl_credit.api import error_response, success_response
from sfpcl_credit.identity.modules import http_auth
from sfpcl_credit.members import portal_services


def _portal_member_or_response(request):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return None, None, response
    member = portal_services.portal_member_for_user(user)
    if member is None:
        return None, None, error_response(
            request,
            403,
            "PERMISSION_DENIED",
            portal_services.PORTAL_PERMISSION_ERROR,
        )
    return member, user, None


@require_GET
def portal_dashboard(request):
    member, _user, response = _portal_member_or_response(request)
    if response is not None:
        return response
    return success_response(portal_services.dashboard_summary(member), request)


@require_GET
def portal_profile(request):
    member, user, response = _portal_member_or_response(request)
    if response is not None:
        return response
    return success_response(portal_services.profile(member, user), request)


@require_GET
def portal_produce_supply(request):
    member, _user, response = _portal_member_or_response(request)
    if response is not None:
        return response
    return success_response(portal_services.produce_supply(member), request)
