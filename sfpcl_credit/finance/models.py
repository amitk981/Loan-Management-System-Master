"""Legacy model imports; canonical SAP state is owned by ``sap_workflow``."""

from sfpcl_credit.sap_workflow.models import SapCustomerCode, SapCustomerProfileRequest

__all__ = ["SapCustomerCode", "SapCustomerProfileRequest"]
