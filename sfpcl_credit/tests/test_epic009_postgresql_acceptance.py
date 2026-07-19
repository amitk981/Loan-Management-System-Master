"""Exact PostgreSQL acceptance label declared by slice 009L3."""

from sfpcl_credit.tests import test_disbursement_transfer_success_api as transfer_tests


class Epic009BoundaryPostgreSQLAcceptanceTests(
    transfer_tests.DisbursementTransferSuccessRaceTests
):
    """Run the two retained five-way transfer/posting races as one exact contract."""

