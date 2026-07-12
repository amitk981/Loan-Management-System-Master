import uuid
from dataclasses import asdict, dataclass
from decimal import Decimal, InvalidOperation

from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_date

from sfpcl_credit.applications.models import LoanApplication
from sfpcl_credit.configurations.modules.configuration_resolver import (
    ConfigurationResolutionError,
    resolve_effective_loan_policy,
)
from sfpcl_credit.credit.modules.common import (
    APPLICATION_READ_PERMISSION,
    LOAN_LIMIT_CALCULATE_PERMISSION,
    CreditModuleInvalidStateError,
    CreditModuleNotFound,
    CreditModuleValidationError,
    get_application_or_raise,
    normalize_request_meta,
    require_application_access,
    require_permission,
)
from sfpcl_credit.credit.models import EligibilityAssessment, LoanAppraisalNote, LoanLimitAssessment
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.members.models import (
    CropPlan,
    IndividualMemberProfile,
    LandHolding,
    Shareholding,
)
from sfpcl_credit.workflows.events import record_workflow_event


LOAN_LIMIT_CALCULATED_AUDIT_ACTION = "loan_limit.calculated"


@dataclass(frozen=True)
class LoanLimitSnapshot:
    loan_limit_assessment_id: str
    loan_application_id: str
    member_id: str
    shareholding_id: str | None
    number_of_shares: int
    valuation_per_share: str
    share_limit_percentage: str | None
    per_share_cap_amount: str | None
    shareholding_based_limit_amount: str
    land_area_acres: str
    scale_of_finance_per_acre_amount: str
    land_based_limit_amount: str
    final_eligible_loan_amount: str
    requested_amount: str
    amount_within_limit_flag: bool
    exception_required_flag: bool
    calculation_rule_version: str
    policy_config_id: str | None
    policy_name: str | None
    board_approval_reference: str | None
    calculated_by_user_id: str | None
    calculated_at: str | None

    def as_dict(self):
        values = asdict(self)
        values["configuration_source"] = {
            "type": "loan_policy_config",
            "loan_policy_config_id": values.pop("policy_config_id"),
            "policy_name": values.pop("policy_name"),
            "board_approval_reference": values.pop("board_approval_reference"),
        }
        return values


@dataclass(frozen=True)
class LoanLimitAssessmentResult:
    projection: LoanLimitSnapshot
    available_actions: tuple = ()

    @property
    def snapshot(self):
        snapshot = self.projection.as_dict()
        snapshot["warnings"] = _warnings(self.projection.exception_required_flag)
        snapshot["available_actions"] = list(self.available_actions)
        return snapshot


@dataclass(frozen=True)
class LoanLimitTransitionEvaluation:
    allowed: bool
    reason: str | None


def evaluate_loan_limit_calculation(application):
    """Single predicate consumed by both the write and its resource action."""
    if LoanAppraisalNote.objects.filter(loan_application=application).exists():
        return LoanLimitTransitionEvaluation(False, "Loan-limit calculation cannot be rerun after appraisal has started.")
    eligibility = EligibilityAssessment.objects.filter(loan_application=application).first()
    if eligibility is None:
        return LoanLimitTransitionEvaluation(False, "An eligible eligibility assessment is required before loan-limit calculation.")
    if eligibility.overall_result != EligibilityAssessment.OVERALL_ELIGIBLE:
        return LoanLimitTransitionEvaluation(False, "Loan-limit calculation requires eligibility overall_result eligible.")
    return LoanLimitTransitionEvaluation(True, None)


class LoanLimitCalculator:
    def get_assessment(self, *, actor, application_id, actor_permissions=None):
        permissions = require_permission(
            actor,
            APPLICATION_READ_PERMISSION,
            "You do not have permission to read loan applications.",
            actor_permissions,
        )
        application = get_application_or_raise(application_id)
        require_application_access(
            application,
            actor,
            APPLICATION_READ_PERMISSION,
            permissions,
        )
        assessment = (
            LoanLimitAssessment.objects.select_related(
                "loan_application",
                "member",
                "shareholding",
                "calculated_by_user",
            )
            .filter(loan_application=application)
            .first()
        )
        if assessment is None:
            raise CreditModuleNotFound("Loan-limit assessment was not found.")
        return _result(assessment, actor, permissions)

    @transaction.atomic
    def calculate_for_application(
        self,
        *,
        actor,
        application_id,
        payload,
        request_meta=None,
        actor_permissions=None,
    ):
        permissions = require_permission(
            actor,
            LOAN_LIMIT_CALCULATE_PERMISSION,
            "You do not have permission to calculate loan limits.",
            actor_permissions,
        )
        request_meta = normalize_request_meta(request_meta)
        application = (
            LoanApplication.objects.select_for_update(of=("self",))
            .select_related("member", "created_by_user", "received_by_user")
            .filter(loan_application_id=application_id)
            .first()
        )
        if application is None:
            raise CreditModuleNotFound("Loan application was not found.")
        require_application_access(
            application,
            actor,
            LOAN_LIMIT_CALCULATE_PERMISSION,
            permissions,
        )
        transition = evaluate_loan_limit_calculation(application)
        if not transition.allowed:
            raise CreditModuleInvalidStateError(transition.reason)
        if callable(payload):
            payload = payload()
        eligibility = (
            EligibilityAssessment.objects.select_for_update()
            .filter(loan_application=application)
            .first()
        )
        # The shared transition predicate guarantees this locked row exists and is eligible.
        if eligibility is None or eligibility.overall_result != EligibilityAssessment.OVERALL_ELIGIBLE:
            raise CreditModuleInvalidStateError(transition.reason or "Eligibility changed during loan-limit calculation.")

        current_assessment = (
            LoanLimitAssessment.objects.select_for_update()
            .filter(loan_application=application)
            .first()
        )
        cleaned = _clean_payload_with_locked_sources(application, payload)
        try:
            policy = resolve_effective_loan_policy(
                calculation_date=cleaned["calculation_date"],
                for_update=True,
            )
        except ConfigurationResolutionError as exc:
            raise CreditModuleValidationError(exc.field_errors) from exc

        shareholding = cleaned["shareholding"]
        valuation_per_share = shareholding.valuation_per_share
        percentage = policy.share_limit_percentage
        cap_amount = policy.per_share_cap_amount
        per_share_limits = []
        if percentage is not None:
            per_share_limits.append(valuation_per_share * percentage / Decimal("100"))
        if cap_amount is not None:
            per_share_limits.append(cap_amount)
        shareholding_limit = (
            Decimal(shareholding.number_of_shares) * min(per_share_limits)
        ).quantize(Decimal("0.01"))
        land_area = cleaned["cultivated_acreage"]
        land_limit = (
            land_area * policy.default_scale_of_finance_per_acre_amount
        ).quantize(Decimal("0.01"))
        final_eligible_amount = min(shareholding_limit, land_limit)
        requested_amount = cleaned["requested_amount"].quantize(Decimal("0.01"))
        amount_within_limit = requested_amount <= final_eligible_amount

        old_value_json = (
            _projection(current_assessment).as_dict()
            if current_assessment is not None
            else None
        )
        assessment = current_assessment or LoanLimitAssessment(
            loan_application=application
        )
        assessment.member = application.member
        assessment.shareholding = shareholding
        assessment.number_of_shares = shareholding.number_of_shares
        assessment.valuation_per_share = valuation_per_share
        assessment.share_limit_percentage = percentage
        assessment.per_share_cap_amount = cap_amount
        assessment.shareholding_based_limit_amount = shareholding_limit
        assessment.land_area_acres = land_area
        assessment.scale_of_finance_per_acre_amount = (
            policy.default_scale_of_finance_per_acre_amount
        )
        assessment.land_based_limit_amount = land_limit
        assessment.final_eligible_loan_amount = final_eligible_amount
        assessment.requested_amount = requested_amount
        assessment.amount_within_limit_flag = amount_within_limit
        assessment.exception_required_flag = not amount_within_limit
        assessment.calculation_rule_version = policy.policy_version
        assessment.policy_config_id_snapshot = policy.loan_policy_config_id
        assessment.policy_name_snapshot = policy.policy_name
        assessment.board_approval_reference_snapshot = (
            policy.board_approval_reference or ""
        )
        assessment.calculated_by_user = actor
        assessment.calculated_at = timezone.now()
        assessment.save()

        projection = _projection(assessment)
        _audit_assessment(
            assessment,
            actor,
            old_value_json,
            projection,
            request_meta,
        )
        record_workflow_event(
            actor=actor,
            workflow_name="loan_limit_assessment",
            entity_type="loan_application",
            entity_id=application.loan_application_id,
            from_state=application.current_stage,
            to_state="loan_limit_calculated",
            trigger_reason="Source-backed loan limit calculated.",
            action_code=LOAN_LIMIT_CALCULATED_AUDIT_ACTION,
        )
        return LoanLimitAssessmentResult(projection=projection, available_actions=tuple(_loan_limit_actions(application, actor, permissions)))


def _result(assessment, actor, permissions):
    return LoanLimitAssessmentResult(projection=_projection(assessment), available_actions=tuple(_loan_limit_actions(assessment.loan_application, actor, permissions)))


def _loan_limit_actions(application, actor, permissions):
    permissions = set(permissions)
    transition = evaluate_loan_limit_calculation(application)
    calculate_enabled = transition.allowed and LOAN_LIMIT_CALCULATE_PERMISSION in permissions
    create_enabled = transition.allowed and "credit.appraisal.create" in permissions and "credit.risk_assessment.manage" in permissions
    def item(code, label, permission, enabled, reason):
        return {"action_code": code, "label": label, "enabled": enabled, "disabled_reason": None if enabled else reason, "required_permission": permission, "required_role": None}
    reason = transition.reason or "Required permission is missing."
    if transition.allowed and "credit.appraisal.create" not in permissions:
        create_reason = "You do not have permission to create appraisal notes."
    elif transition.allowed and "credit.risk_assessment.manage" not in permissions:
        create_reason = "You do not have permission to manage risk assessments."
    elif (
        (eligibility := EligibilityAssessment.objects.filter(loan_application=application).first())
        is not None
        and eligibility.overall_result != EligibilityAssessment.OVERALL_ELIGIBLE
    ):
        create_reason = "Appraisal creation requires eligibility overall_result eligible."
    else:
        create_reason = reason
    return [
        loan_limit_calculate_action(application, permissions),
        item("credit.appraisal.create", "Create Appraisal Draft", "credit.appraisal.create", create_enabled, create_reason),
    ]


def loan_limit_calculate_action(application, permissions):
    """Public six-field projection shared by every container that can start calculation."""
    permissions = set(permissions)
    transition = evaluate_loan_limit_calculation(application)
    enabled = transition.allowed and LOAN_LIMIT_CALCULATE_PERMISSION in permissions
    return {
        "action_code": LOAN_LIMIT_CALCULATE_PERMISSION,
        "label": "Calculate Loan Limit",
        "enabled": enabled,
        "disabled_reason": None if enabled else transition.reason or "You do not have permission to calculate loan limits.",
        "required_permission": LOAN_LIMIT_CALCULATE_PERMISSION,
        "required_role": None,
    }


def _projection(assessment):
    return LoanLimitSnapshot(
        loan_limit_assessment_id=str(assessment.loan_limit_assessment_id),
        loan_application_id=str(assessment.loan_application_id),
        member_id=str(assessment.member_id),
        shareholding_id=(
            str(assessment.shareholding_id) if assessment.shareholding_id else None
        ),
        number_of_shares=assessment.number_of_shares,
        valuation_per_share=_money(assessment.valuation_per_share),
        share_limit_percentage=(
            f"{assessment.share_limit_percentage:.4f}"
            if assessment.share_limit_percentage is not None
            else None
        ),
        per_share_cap_amount=_money(assessment.per_share_cap_amount),
        shareholding_based_limit_amount=_money(
            assessment.shareholding_based_limit_amount
        ),
        land_area_acres=f"{assessment.land_area_acres:.2f}",
        scale_of_finance_per_acre_amount=_money(
            assessment.scale_of_finance_per_acre_amount
        ),
        land_based_limit_amount=_money(assessment.land_based_limit_amount),
        final_eligible_loan_amount=_money(assessment.final_eligible_loan_amount),
        requested_amount=_money(assessment.requested_amount),
        amount_within_limit_flag=assessment.amount_within_limit_flag,
        exception_required_flag=assessment.exception_required_flag,
        calculation_rule_version=assessment.calculation_rule_version,
        policy_config_id=(
            str(assessment.policy_config_id_snapshot)
            if assessment.policy_config_id_snapshot
            else None
        ),
        policy_name=assessment.policy_name_snapshot or None,
        board_approval_reference=(
            assessment.board_approval_reference_snapshot or None
        ),
        calculated_by_user_id=(
            str(assessment.calculated_by_user_id)
            if assessment.calculated_by_user_id
            else None
        ),
        calculated_at=_timestamp(assessment.calculated_at),
    )


def _warnings(exception_required):
    if not exception_required:
        return []
    return [
        {
            "code": "REQUESTED_AMOUNT_EXCEEDS_LIMIT",
            "message": "Requested amount exceeds final eligible loan amount.",
        }
    ]


def _audit_assessment(assessment, actor, old_value_json, projection, request_meta):
    new_value_json = projection.as_dict()
    new_value_json["request_id"] = request_meta.request_id
    AuditLog.objects.create(
        actor_user=actor,
        action=LOAN_LIMIT_CALCULATED_AUDIT_ACTION,
        entity_type="loan_limit_assessment",
        entity_id=assessment.loan_limit_assessment_id,
        old_value_json=old_value_json,
        new_value_json=new_value_json,
        ip_address=request_meta.ip_address,
        user_agent=request_meta.user_agent,
    )


def _clean_payload_with_locked_sources(application, payload):
    allowed_fields = {
        "shareholding_id",
        "land_holding_ids",
        "crop_plan_id",
        "requested_amount",
        "calculation_date",
    }
    errors = {
        field: "Unknown field." for field in sorted(set(payload) - allowed_fields)
    }
    for field in sorted(allowed_fields):
        if field not in payload or payload.get(field) in (None, "", []):
            errors[field] = "This field is required."

    shareholding_id = _parse_uuid(
        "shareholding_id", payload.get("shareholding_id"), errors
    )
    crop_plan_id = _parse_uuid("crop_plan_id", payload.get("crop_plan_id"), errors)
    requested_amount = _positive_decimal(
        payload.get("requested_amount"), "requested_amount", errors
    )
    calculation_date = parse_date(str(payload.get("calculation_date", "")))
    if calculation_date is None:
        errors["calculation_date"] = "Must be a valid ISO date."

    land_ids = _parse_land_ids(payload.get("land_holding_ids"), errors)
    if errors:
        raise CreditModuleValidationError(errors)

    shareholding = (
        Shareholding.objects.select_for_update()
        .filter(shareholding_id=shareholding_id, member=application.member)
        .first()
    )
    if shareholding is None:
        errors["shareholding_id"] = "Referenced record was not found for this member."
    elif shareholding.status != "active":
        errors["shareholding_id"] = "Shareholding must be active."
    elif shareholding.number_of_shares <= 0:
        errors["shareholding_id"] = "Shareholding must contain at least one share."
    elif shareholding.valuation_per_share is None or shareholding.valuation_per_share <= 0:
        errors["shareholding_id"] = (
            "Shareholding requires a positive approved valuation per share."
        )

    land_holdings = list(
        LandHolding.objects.select_for_update()
        .filter(land_holding_id__in=land_ids, member=application.member)
        .order_by("land_holding_id")
    )
    if len(land_holdings) != len(land_ids):
        errors["land_holding_ids"] = (
            "Every land holding must exist for the loan application member."
        )
    elif any(holding.verification_status != "verified" for holding in land_holdings):
        errors["land_holding_ids"] = "Every selected land holding must be verified."

    crop_plan = (
        CropPlan.objects.select_for_update()
        .filter(crop_plan_id=crop_plan_id, member=application.member)
        .first()
    )
    if crop_plan is None:
        errors["crop_plan_id"] = "Referenced record was not found for this member."
    elif crop_plan.loan_application_id != application.loan_application_id:
        errors["crop_plan_id"] = "Crop plan must be linked to this loan application."
    elif crop_plan.verification_status != "verified":
        errors["crop_plan_id"] = "Crop plan must be verified."
    elif crop_plan.loan_purpose_alignment != "agriculture_aligned":
        errors["crop_plan_id"] = "Crop plan must be agriculture aligned."

    if application.required_loan_amount is None:
        errors["requested_amount"] = (
            "Loan application must store a requested amount before calculation."
        )
    elif requested_amount != application.required_loan_amount:
        errors["requested_amount"] = (
            "Requested amount must match the loan application requested amount."
        )
    if errors:
        raise CreditModuleValidationError(errors)

    selected_land_area = _normalized_acres(
        sum((holding.area_acres for holding in land_holdings), Decimal("0.00"))
    )
    crop_plan_area = _normalized_acres(crop_plan.planned_area_acres)
    acreage_values = {selected_land_area, crop_plan_area}
    profile = (
        IndividualMemberProfile.objects.select_for_update()
        .filter(member=application.member)
        .first()
    )
    if profile and profile.land_area_under_cultivation_acres is not None:
        acreage_values.add(_normalized_acres(profile.land_area_under_cultivation_acres))
    if len(acreage_values) != 1:
        raise CreditModuleValidationError(
            {"cultivated_acreage": "CULTIVATED_ACREAGE_UNRESOLVED"}
        )
    return {
        "shareholding": shareholding,
        "land_holdings": land_holdings,
        "crop_plan": crop_plan,
        "cultivated_acreage": selected_land_area,
        "requested_amount": requested_amount,
        "calculation_date": calculation_date,
    }


def _parse_land_ids(raw_land_ids, errors):
    land_ids = []
    if isinstance(raw_land_ids, list) and raw_land_ids:
        for raw_id in raw_land_ids:
            try:
                land_ids.append(uuid.UUID(str(raw_id)))
            except (TypeError, ValueError):
                errors["land_holding_ids"] = "Every value must be a valid UUID."
                break
        if len(set(land_ids)) != len(land_ids):
            errors["land_holding_ids"] = "Duplicate land holdings are not allowed."
    elif raw_land_ids not in (None, "", []):
        errors["land_holding_ids"] = "Must be a non-empty list of UUIDs."
    return land_ids


def _parse_uuid(field, value, errors):
    if value in (None, ""):
        errors[field] = "This field is required."
        return None
    try:
        return uuid.UUID(str(value))
    except (TypeError, ValueError):
        errors[field] = "Must be a valid UUID."
        return None


def _positive_decimal(value, field, errors):
    if value in (None, ""):
        errors[field] = "This field is required."
        return None
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        errors[field] = "Must be a positive decimal amount."
        return None
    if parsed <= 0:
        errors[field] = "Must be a positive decimal amount."
    return parsed


def _normalized_acres(value):
    return Decimal(value).quantize(Decimal("0.01"))


def _money(value):
    return f"{value:.2f}" if value is not None else None


def _timestamp(value):
    return value.isoformat().replace("+00:00", "Z") if value else None
