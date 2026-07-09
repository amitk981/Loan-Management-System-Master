from django.urls import path

from sfpcl_credit.communications import views as communication_views
from sfpcl_credit.configurations import views as configuration_views
from sfpcl_credit.dashboard import views as dashboard_views
from sfpcl_credit.documents import views as document_views
from sfpcl_credit.identity import admin_views, audit_views
from sfpcl_credit.identity.views import login, logout, me, refresh
from sfpcl_credit.members import views as member_views
from sfpcl_credit.ops import deep_health, live_health, ready_health
from sfpcl_credit.tracer import views as tracer_views
from sfpcl_credit.workflows import event_views


urlpatterns = [
    path("api/v1/auth/login/", login, name="auth-login"),
    path("api/v1/auth/refresh/", refresh, name="auth-refresh"),
    path("api/v1/auth/logout/", logout, name="auth-logout"),
    path("api/v1/auth/me/", me, name="auth-me"),
    path("api/v1/dashboard/", dashboard_views.dashboard_summary, name="dashboard-summary"),
    path("api/v1/admin/users/", admin_views.user_list, name="admin-user-list"),
    path(
        "api/v1/admin/users/<uuid:user_id>/",
        admin_views.user_detail,
        name="admin-user-detail",
    ),
    path(
        "api/v1/admin/users/<uuid:user_id>/roles/",
        admin_views.assign_role,
        name="admin-user-role-assign",
    ),
    path(
        "api/v1/admin/users/<uuid:user_id>/teams/",
        admin_views.add_team,
        name="admin-user-team-add",
    ),
    path(
        "api/v1/admin/users/<uuid:user_id>/teams/<str:team_code>/",
        admin_views.remove_team,
        name="admin-user-team-remove",
    ),
    path(
        "api/v1/admin/users/<uuid:user_id>/status/",
        admin_views.set_status,
        name="admin-user-status-set",
    ),
    path("api/v1/audit-logs/", audit_views.audit_log_list, name="audit-log-list"),
    path(
        "api/v1/workflow-events/",
        event_views.workflow_event_list,
        name="workflow-event-list",
    ),
    path(
        "api/v1/config/loan-policy/",
        configuration_views.loan_policy_collection,
        name="loan-policy-config-list-create",
    ),
    path(
        "api/v1/config/loan-policy/<uuid:loan_policy_config_id>/",
        configuration_views.loan_policy_detail,
        name="loan-policy-config-detail",
    ),
    path(
        "api/v1/config/loan-policy/<uuid:loan_policy_config_id>/activate/",
        configuration_views.loan_policy_activate,
        name="loan-policy-config-activate",
    ),
    path(
        "api/v1/version-histories/",
        configuration_views.version_history_list,
        name="version-history-list",
    ),
    path(
        "api/v1/content-templates/",
        communication_views.content_template_collection,
        name="content-template-list-create",
    ),
    path(
        "api/v1/content-templates/<uuid:content_template_id>/",
        communication_views.content_template_detail,
        name="content-template-detail",
    ),
    path(
        "api/v1/communications/",
        communication_views.communication_collection,
        name="communication-list",
    ),
    path(
        "api/v1/communications/send/",
        communication_views.communication_send,
        name="communication-send",
    ),
    path(
        "api/v1/notifications/",
        communication_views.notification_collection,
        name="notification-list",
    ),
    path(
        "api/v1/notifications/<uuid:notification_id>/mark-read/",
        communication_views.notification_mark_read,
        name="notification-mark-read",
    ),
    path("api/v1/members/", member_views.member_collection, name="member-list"),
    path(
        "api/v1/members/<uuid:member_id>/",
        member_views.member_detail,
        name="member-detail",
    ),
    path(
        "api/v1/members/<uuid:member_id>/nominees/",
        member_views.member_nominees,
        name="member-nominees",
    ),
    path(
        "api/v1/document-files/",
        document_views.upload_document_file,
        name="document-file-upload",
    ),
    path(
        "api/v1/document-files/<uuid:document_id>/download/",
        document_views.download_document_file,
        name="document-file-download",
    ),
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
