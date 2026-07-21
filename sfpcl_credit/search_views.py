from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_POST

from sfpcl_credit.api import error_response, parse_json_body, success_response
from sfpcl_credit.identity.modules import http_auth
from sfpcl_credit.processes import global_search


RATE_LIMIT = 30
RATE_WINDOW_SECONDS = 60


@require_POST
def global_search_results(request):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    key = f"global-search-rate:{actor.user_id}"
    if cache.add(key, 1, RATE_WINDOW_SECONDS):
        count = 1
    else:
        try:
            count = cache.incr(key)
        except ValueError:
            cache.set(key, 1, RATE_WINDOW_SECONDS)
            count = 1
    if count > RATE_LIMIT:
        return error_response(
            request, 429, "RATE_LIMITED", "Global search is temporarily rate limited."
        )
    try:
        payload = parse_json_body(request)
        data = global_search.search(actor=actor, payload=payload)
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Global search request failed validation.",
            global_search.validation_errors(exc),
        )
    return success_response(data, request)
