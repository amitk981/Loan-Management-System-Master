from dataclasses import dataclass
from typing import Callable

from sfpcl_credit.reports.selectors.application_pipeline import (
    select as select_application_pipeline,
)
from sfpcl_credit.reports.selectors.documentation_readiness import (
    select as select_documentation_readiness,
)
from sfpcl_credit.reports.selectors.loan_portfolio import (
    select as select_loan_portfolio,
)
from sfpcl_credit.reports.selectors.dpd import select as select_dpd
from sfpcl_credit.reports.selectors.disbursement_pending import (
    select as select_disbursement_pending,
)
from sfpcl_credit.reports.selectors.compliance_dashboard import (
    select as select_compliance_dashboard,
)
from sfpcl_credit.reports.selectors.cfo_quarterly_mis import (
    select as select_cfo_quarterly_mis,
)
from sfpcl_credit.reports.selectors.credit_sanction import (
    select as select_credit_sanction,
)
from sfpcl_credit.reports.selectors.disbursement import select as select_disbursement
from sfpcl_credit.reports.selectors.exception import select as select_exception
from sfpcl_credit.reports.selectors.interest_accrual import (
    select as select_interest_accrual,
)
from sfpcl_credit.reports.selectors.interest_invoice import (
    select as select_interest_invoice,
)
from sfpcl_credit.reports.selectors.repayment import select as select_repayment
from sfpcl_credit.reports.selectors.sap_pending import select as select_sap_pending
from sfpcl_credit.reports.selectors.security_custody import (
    select as select_security_custody,
)


@dataclass(frozen=True)
class ReportDefinition:
    code: str
    selector: Callable


REPORTS = {
    "application-pipeline": ReportDefinition(
        code="application-pipeline",
        selector=select_application_pipeline,
    ),
    "documentation-readiness": ReportDefinition(
        code="documentation-readiness",
        selector=select_documentation_readiness,
    ),
    "loan-portfolio": ReportDefinition(
        code="loan-portfolio",
        selector=select_loan_portfolio,
    ),
    "dpd": ReportDefinition(
        code="dpd",
        selector=select_dpd,
    ),
    "disbursement-pending": ReportDefinition(
        code="disbursement-pending",
        selector=select_disbursement_pending,
    ),
    "compliance-dashboard": ReportDefinition(
        code="compliance-dashboard",
        selector=select_compliance_dashboard,
    ),
    "credit-sanction": ReportDefinition(
        code="credit-sanction",
        selector=select_credit_sanction,
    ),
    "exception": ReportDefinition(
        code="exception",
        selector=select_exception,
    ),
    "security-custody": ReportDefinition(
        code="security-custody",
        selector=select_security_custody,
    ),
    "sap-pending": ReportDefinition(
        code="sap-pending",
        selector=select_sap_pending,
    ),
    "disbursement": ReportDefinition(
        code="disbursement",
        selector=select_disbursement,
    ),
    "repayment": ReportDefinition(
        code="repayment",
        selector=select_repayment,
    ),
    "interest-invoice": ReportDefinition(
        code="interest-invoice",
        selector=select_interest_invoice,
    ),
    "interest-accrual": ReportDefinition(
        code="interest-accrual",
        selector=select_interest_accrual,
    ),
    "cfo-quarterly-mis": ReportDefinition(
        code="cfo-quarterly-mis",
        selector=select_cfo_quarterly_mis,
    ),
}


def run_report(*, report_code, actor, query_params):
    return REPORTS[report_code].selector(
        actor=actor,
        query_params=query_params,
    )
