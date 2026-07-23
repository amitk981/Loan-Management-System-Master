from django.apps import AppConfig


class ComplianceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "sfpcl_credit.compliance"

    def ready(self):
        from sfpcl_credit.compliance.search_facade import search_compliance_records
        from sfpcl_credit.processes.global_search import register_compliance_provider

        register_compliance_provider(search_compliance_records)
