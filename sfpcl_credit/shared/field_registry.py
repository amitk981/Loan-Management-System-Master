"""Canonical inventory of database columns owned by shared field encryption."""

from dataclasses import dataclass


@dataclass(frozen=True)
class EncryptedColumn:
    name: str
    context: str
    legacy_contexts: tuple[str, ...] = ()
    hash_name: str | None = None
    hash_context: str | None = None


@dataclass(frozen=True)
class EncryptedModel:
    model_label: str
    primary_key: str
    columns: tuple[EncryptedColumn, ...]


FIELD_ENCRYPTION_MODELS = (
    EncryptedModel(
        "members.Member",
        "member_id",
        (
            EncryptedColumn(
                "pan_encrypted",
                "identity.pan",
                ("members.pan",),
                "pan_hash",
                "identity.lookup",
            ),
            EncryptedColumn(
                "aadhaar_encrypted",
                "identity.aadhaar",
                ("members.aadhaar",),
                "aadhaar_hash",
                "identity.lookup",
            ),
        ),
    ),
    EncryptedModel(
        "members.MemberIdentityChangeRequest",
        "identity_change_request_id",
        (
            EncryptedColumn(
                "proposed_pan_encrypted",
                "identity.pan",
                hash_name="proposed_pan_hash",
                hash_context="identity.lookup",
            ),
            EncryptedColumn(
                "proposed_aadhaar_encrypted",
                "identity.aadhaar",
                hash_name="proposed_aadhaar_hash",
                hash_context="identity.lookup",
            ),
        ),
    ),
    EncryptedModel(
        "members.ProducerInstitutionProfile",
        "producer_institution_profile_id",
        (
            EncryptedColumn(
                "authorised_signatory_pan_encrypted",
                "identity.pan",
                hash_name="authorised_signatory_pan_hash",
                hash_context="identity.lookup",
            ),
            EncryptedColumn(
                "authorised_signatory_aadhaar_encrypted",
                "identity.aadhaar",
                hash_name="authorised_signatory_aadhaar_hash",
                hash_context="identity.lookup",
            ),
        ),
    ),
    EncryptedModel(
        "members.Nominee",
        "nominee_id",
        (
            EncryptedColumn(
                "pan_encrypted",
                "identity.pan",
                hash_name="pan_hash",
                hash_context="identity.lookup",
            ),
            EncryptedColumn(
                "aadhaar_encrypted",
                "identity.aadhaar",
                hash_name="aadhaar_hash",
                hash_context="identity.lookup",
            ),
        ),
    ),
    EncryptedModel(
        "applications.Witness",
        "witness_id",
        (
            EncryptedColumn(
                "pan_encrypted",
                "identity.pan",
                hash_name="pan_hash",
                hash_context="identity.lookup",
            ),
            EncryptedColumn(
                "aadhaar_encrypted",
                "identity.aadhaar",
                hash_name="aadhaar_hash",
                hash_context="identity.lookup",
            ),
        ),
    ),
    EncryptedModel(
        "members.KycProfile",
        "kyc_profile_id",
        (EncryptedColumn("ckyc_identifier_encrypted", "identity.ckyc"),),
    ),
    EncryptedModel(
        "members.BankAccount",
        "bank_account_id",
        (
            EncryptedColumn(
                "account_number_encrypted",
                "members.bank_account.account_number",
                hash_name="account_number_hash",
                hash_context="identity.lookup",
            ),
        ),
    ),
    EncryptedModel(
        "members.CancelledCheque",
        "cancelled_cheque_id",
        (
            EncryptedColumn(
                "account_number_encrypted",
                "members.cancelled_cheque.account_number",
                hash_name="account_number_hash",
                hash_context="identity.lookup",
            ),
        ),
    ),
    EncryptedModel(
        "security_instruments.CDSLSharePledge",
        "cdsl_share_pledge_id",
        (
            EncryptedColumn(
                "pledgor_bo_account_encrypted",
                "cdsl.pledgor_bo_account",
                hash_name="pledgor_bo_account_hash",
                hash_context="cdsl.pledgor_bo_account",
            ),
            EncryptedColumn(
                "pledgee_bo_account_encrypted",
                "cdsl.pledgee_bo_account",
                hash_name="pledgee_bo_account_hash",
                hash_context="cdsl.pledgee_bo_account",
            ),
        ),
    ),
    EncryptedModel(
        "security_instruments.BlankDatedCheque",
        "blank_dated_cheque_id",
        (
            EncryptedColumn(
                "cheque_number_encrypted",
                "blank_cheque.cheque_number",
                hash_name="cheque_number_hash",
                hash_context="blank_cheque.cheque_number",
            ),
        ),
    ),
    EncryptedModel(
        "sap_workflow.SAPCustomerProfileRequest",
        "sap_customer_profile_request_id",
        (
            EncryptedColumn(
                "pan_number_encrypted", "finance.sap_request.pan"
            ),
            EncryptedColumn(
                "aadhaar_number_encrypted", "finance.sap_request.aadhaar"
            ),
        ),
    ),
    EncryptedModel(
        "loans.BankStatementImport",
        "bank_statement_import_id",
        (
            EncryptedColumn(
                "legacy_collection_account_encrypted",
                "loans.bank_statement_import.legacy_collection_account",
            ),
        ),
    ),
)
