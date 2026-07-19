"""Reusable synthetic fixture builder for the guarded Epic 009 browser contract."""

import gzip
import json
import shutil
from pathlib import Path

from django.conf import settings
from django.core import serializers
from django.core.management import call_command
from django.db import transaction
from django.db.models import Q

from sfpcl_credit.documents.models import DocumentTemplate
from sfpcl_credit.identity.models import Permission, Role, RolePermission, User


_FIXTURE_ROOT = Path(__file__).with_name("fixtures")
_FIXTURE_PATH = _FIXTURE_ROOT / "epic009_browser_fixture.json.gz"
_ANNEXURE_PATH = _FIXTURE_ROOT / "epic009_browser_files" / "annexure-i.xlsx"


@transaction.atomic
def build_ready_epic009_fixture(*, password, finance_email, credit_email, cfc_email,
                                borrower_email):
    """Load one exact owner-backed pre-initiation scenario without test dependencies."""
    call_command("seed_role_catalogue", verbosity=0)
    objects = _fixture_objects()
    role_codes = {
        row["pk"]: row["fields"]["role_code"]
        for row in objects
        if row["model"] == "identity.role"
    }
    template_ids = _existing_template_ids(objects)
    loadable = []
    for row in objects:
        if row["model"] in {
            "identity.role",
            "identity.permission",
            "identity.rolepermission",
            "identity.team",
            "identity.usersession",
            "approvals.approvalcasereadscopegrant",
        }:
            continue
        fields = row["fields"]
        for field_name in ("role", "primary_role"):
            retained_role = fields.get(field_name)
            if retained_role in role_codes:
                fields[field_name] = str(
                    Role.objects.get(role_code=role_codes[retained_role]).pk
                )
        if row["model"] == "documents.documenttemplate" and row["pk"] in template_ids:
            continue
        if row["model"] == "legal_documents.loandocument":
            retained = fields.get("document_template")
            if retained in template_ids:
                fields["document_template"] = template_ids[retained]
        loadable.append(row)

    for wrapper in serializers.deserialize("json", json.dumps(loadable)):
        wrapper.save()

    from sfpcl_credit.loans.models import LoanAccount
    from sfpcl_credit.members.models import BankAccount
    from sfpcl_credit.sap_workflow.models import SapCustomerProfileRequest

    account = LoanAccount.objects.select_related("member", "loan_application").get(
        loan_account_number="LN-REAL-OWNER-001"
    )
    request = SapCustomerProfileRequest.objects.get(
        loan_application_id=account.loan_application_id,
        request_status=SapCustomerProfileRequest.STATUS_COMPLETED,
    )
    _restore_annexure(request.excel_file.storage_key)

    finance = User.objects.get(full_name="Checklist Senior Finance")
    credit = User.objects.get(full_name="Checklist Credit")
    _make_browser_actor(finance, finance_email, password)
    _make_browser_actor(credit, credit_email, password)
    account.member.email = borrower_email
    account.member.save(update_fields=["email"])

    _grant(
        finance,
        "finance.loan_account.read",
        "communications.notification.read",
        "finance.disbursement.mark_success",
        "finance.disbursement.send_advice",
    )
    advice_permission = Permission.objects.get(
        permission_code="finance.disbursement.send_advice"
    )
    advice_permission.risk_level = Permission.RISK_HIGH
    advice_permission.save(update_fields=["risk_level"])
    _grant(credit, "finance.loan_account.read", "communications.notification.read")

    cfc_role = Role.objects.get(role_code="chief_financial_controller")
    cfc = User.objects.create(
        full_name="Epic 009 Browser CFC",
        email=cfc_email,
        status=User.ACTIVE_STATUS,
        primary_role=cfc_role,
        approval_authority_type="chief_financial_controller",
    )
    cfc.set_password(password)
    cfc.save(update_fields=["password_hash"])
    _grant(
        cfc,
        "finance.disbursement.authorise",
        "finance.disbursement.mark_success",
        "finance.loan_account.read",
        "communications.notification.read",
    )

    source_bank = BankAccount.objects.get(owner_party_type="sfpcl")
    borrower_bank = BankAccount.objects.get(
        owner_party_type="member", owner_party_id=account.member_id
    )
    return {
        "ready": {
            "account": account,
            "source_bank": source_bank,
            "borrower_bank_account_id": borrower_bank.pk,
            "payload": {
                "disbursement_amount": str(account.sanctioned_amount),
                "borrower_bank_account_id": str(borrower_bank.pk),
                "source_bank_account_id": str(source_bank.pk),
                "final_verification_comments": "All current owner evidence verified.",
            },
            "actor": finance,
        },
        "finance": finance,
        "credit": credit,
        "cfc": cfc,
    }


def _fixture_objects():
    with gzip.open(_FIXTURE_PATH, "rt", encoding="utf-8") as fixture:
        return json.load(fixture)


def _existing_template_ids(objects):
    retained = {}
    for row in objects:
        if row["model"] != "documents.documenttemplate":
            continue
        fields = row["fields"]
        existing = DocumentTemplate.objects.filter(
            Q(
                template_code=fields["template_code"],
                template_version=fields["template_version"],
            )
            | Q(
                document_type=fields["document_type"],
                borrower_type=fields["borrower_type"],
                template_version=fields["template_version"],
            )
        ).first()
        if existing is not None:
            retained[row["pk"]] = str(existing.pk)
    return retained


def _restore_annexure(storage_key):
    destination = Path(settings.DOCUMENT_STORAGE_ROOT) / storage_key
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(_ANNEXURE_PATH, destination)


def _make_browser_actor(user, email, password):
    user.email = email
    user.status = User.ACTIVE_STATUS
    user.set_password(password)
    user.save(update_fields=["email", "status", "password_hash"])


def _grant(user, *permission_codes):
    for code in permission_codes:
        permission, _ = Permission.objects.get_or_create(
            permission_code=code,
            defaults={"permission_name": code, "risk_level": Permission.RISK_CRITICAL},
        )
        RolePermission.objects.get_or_create(
            role=user.primary_role, permission=permission
        )


__all__ = ["build_ready_epic009_fixture"]
