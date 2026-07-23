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
}


def run_report(*, report_code, actor, query_params):
    return REPORTS[report_code].selector(
        actor=actor,
        query_params=query_params,
    )
