from sfpcl_credit.legal_documents.modules import power_of_attorney as _engine
from sfpcl_credit.security_instruments.models import PowerOfAttorney
from sfpcl_credit.security_instruments.modules import security_package
_engine.bind_security_owner(PowerOfAttorney, security_package)
def __getattr__(name):
    return getattr(_engine, name)
