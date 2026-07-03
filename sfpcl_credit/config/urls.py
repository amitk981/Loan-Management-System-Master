from django.urls import path

from sfpcl_credit.identity.views import login, logout, me, refresh
from sfpcl_credit.ops import deep_health, live_health, ready_health
from sfpcl_credit.tracer import views as tracer_views


urlpatterns = [
    path("api/v1/auth/login/", login, name="auth-login"),
    path("api/v1/auth/refresh/", refresh, name="auth-refresh"),
    path("api/v1/auth/logout/", logout, name="auth-logout"),
    path("api/v1/auth/me/", me, name="auth-me"),
    path("api/v1/tracer/members/", tracer_views.create_member, name="tracer-member-create"),
    path(
        "api/v1/tracer/members/<uuid:member_id>/loan-applications/",
        tracer_views.create_application,
        name="tracer-application-create",
    ),
    path(
        "api/v1/tracer/loan-applications/<uuid:application_id>/sanction/",
        tracer_views.sanction_application,
        name="tracer-application-sanction",
    ),
    path(
        "api/v1/tracer/loan-applications/<uuid:application_id>/loan-account/",
        tracer_views.create_loan_account,
        name="tracer-loan-account-create",
    ),
    path(
        "api/v1/tracer/loan-accounts/<uuid:account_id>/disburse/",
        tracer_views.mark_disbursed,
        name="tracer-loan-account-disburse",
    ),
    path(
        "api/v1/tracer/loan-accounts/<uuid:account_id>/repayments/",
        tracer_views.post_repayment,
        name="tracer-repayment-post",
    ),
    path(
        "api/v1/tracer/loan-accounts/<uuid:account_id>/close/",
        tracer_views.close_loan,
        name="tracer-loan-account-close",
    ),
    path("api/v1/health/live/", live_health, name="health-live"),
    path("api/v1/health/ready/", ready_health, name="health-ready"),
    path("api/v1/health/deep/", deep_health, name="health-deep"),
]
