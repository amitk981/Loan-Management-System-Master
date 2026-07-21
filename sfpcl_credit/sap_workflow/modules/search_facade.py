"""SAP-code exact lookup guarded by SAP read authority."""

from sfpcl_credit.sap_workflow.models import SapCustomerCode


READ_PERMISSION = "finance.sap_code.read"


def matching_member_ids(*, permissions, query):
    if READ_PERMISSION not in permissions:
        return frozenset()
    return frozenset(
        SapCustomerCode.objects.filter(sap_customer_code__iexact=query).values_list(
            "member_id", flat=True
        )
    )


__all__ = ["matching_member_ids"]
