from django.apps import AppConfig


class ApprovalsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "sfpcl_credit.approvals"
    label = "approvals"

    def ready(self):
        from sfpcl_credit.approvals import signals  # noqa: F401
