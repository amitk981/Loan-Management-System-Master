"""Source map for the R7 compliance control catalogue (functional-spec M14)."""

R7_CONTROL_CATALOGUE = (
    ("MEMBER_ONLY_LENDING", "ongoing", "company_secretary", "Loan and membership registers; Board minutes"),
    ("SECTION_186_LIMIT", "quarterly", "cfo", "Limit calculation tracker"),
    ("NBFC_PRINCIPAL_TEST", "quarterly", "cfo", "Asset/income ratios and Board minutes"),
    ("KYC_AML", "ongoing", "credit_head", "KYC files, CKYC records, audit reports"),
    ("INTEREST_DISCLOSURE", "ongoing", "company_secretary", "Signed term sheet and acknowledgement"),
    ("STAMP_DUTY", "ongoing", "company_secretary", "008D stamped agreements and purchase records"),
    ("MONEY_LENDING_ANNUAL", "annual", "company_secretary", "Restricted legal opinion and Board note"),
    ("ACCOUNTING_REPORTING", "monthly", "accounts_head", "SAP reports and Board pack"),
    ("RECOVERY_CONDUCT", "ongoing", "company_secretary", "011 recovery call/visit logs and grievance register"),
    ("DATA_PROTECTION", "quarterly", "it_head", "Access logs and destruction certificate"),
    ("RECORD_RETENTION", "annual", "company_secretary", "011 archive logs and audit reports"),
)

__all__ = ["R7_CONTROL_CATALOGUE"]
