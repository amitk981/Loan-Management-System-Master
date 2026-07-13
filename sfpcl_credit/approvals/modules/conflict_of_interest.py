"""Conflict assessment for one immutable approval-case cycle."""

from dataclasses import dataclass

from sfpcl_credit.approvals.models import ApprovalConflictDeclaration


@dataclass(frozen=True)
class ConflictAssessment:
    exclusions: tuple[dict, ...]
    general_meeting_evidence_required: bool = False


class ConflictOfInterestModule:
    """Evaluate conflict facts without consulting mutable application/appraisal rows."""

    _MAKER_REASONS = (
        ("application_created_by_user_id", "own_application", "User created the loan application."),
        ("application_received_by_user_id", "material_preparer", "User received and materially prepared the loan application."),
        ("application_submitted_by_user_id", "material_preparer", "User submitted the loan application."),
        ("appraisal_prepared_by_user_id", "maker_checker", "User prepared the loan appraisal."),
    )

    def evaluate_for_case(self, case) -> ConflictAssessment:
        candidate_ids = self._candidate_ids(case)
        maker_facts = (case.appraisal_facts_json or {}).get("maker_checker", {})
        exclusions = []
        excluded_ids = set()
        for fact_name, conflict_code, reason in self._MAKER_REASONS:
            user_id = str(maker_facts.get(fact_name) or "")
            if user_id in candidate_ids and user_id not in excluded_ids:
                exclusions.append(
                    {
                        "user_id": user_id,
                        "conflict_code": conflict_code,
                        "reason": reason,
                    }
                )
                excluded_ids.add(user_id)
        general_meeting_required = False
        declarations = ApprovalConflictDeclaration.objects.filter(
            loan_application_id=case.loan_application_id,
            user_id__in=candidate_ids,
            is_active=True,
        ).order_by("created_at", "approval_conflict_declaration_id")
        for declaration in declarations:
            user_id = str(declaration.user_id)
            if user_id not in excluded_ids:
                exclusions.append(
                    {
                        "user_id": user_id,
                        "conflict_code": declaration.conflict_type,
                        "reason": declaration.reason.strip(),
                    }
                )
                excluded_ids.add(user_id)
            if declaration.conflict_type in {
                ApprovalConflictDeclaration.CONFLICT_BORROWER,
                ApprovalConflictDeclaration.CONFLICT_DIRECTOR_RELATIVE,
            }:
                general_meeting_required = True
        return ConflictAssessment(
            exclusions=tuple(exclusions),
            general_meeting_evidence_required=general_meeting_required,
        )

    @staticmethod
    def conflict_reason(*, case, actor_id):
        actor_id = str(actor_id)
        for exclusion in case.excluded_approvers_json:
            if (
                isinstance(exclusion, dict)
                and str(exclusion.get("user_id")) == actor_id
            ):
                return str(exclusion.get("reason") or "").strip() or None
        return None

    @classmethod
    def effective_approvers(cls, case):
        """Overlay exclusions and frozen same-role alternates on immutable routing history."""
        excluded_ids = {
            str(item.get("user_id"))
            for item in case.excluded_approvers_json
            if isinstance(item, dict) and item.get("user_id")
        }
        effective = []
        used_ids = set()
        committee = case.committee_projection_json or {}
        director_candidates = [
            str(user_id) for user_id in committee.get("director_user_ids", [])
        ]
        for approver in case.required_approvers_json:
            user_id = str(approver.get("user_id"))
            if user_id not in excluded_ids:
                effective.append(dict(approver))
                used_ids.add(user_id)
                continue
            if approver.get("role_code") != "director":
                continue
            replacement_id = next(
                (
                    candidate_id
                    for candidate_id in director_candidates
                    if candidate_id not in excluded_ids and candidate_id not in used_ids
                ),
                None,
            )
            if replacement_id:
                effective.append(
                    {"role_code": "director", "user_id": replacement_id}
                )
                used_ids.add(replacement_id)
        return tuple(effective)

    @classmethod
    def authority_is_satisfiable(cls, case):
        return len(cls.effective_approvers(case)) == len(case.required_approvers_json)

    @classmethod
    def authority_gap_reason(cls, case):
        effective_roles = [
            item["role_code"] for item in cls.effective_approvers(case)
        ]
        required_roles = [
            item["role_code"] for item in case.required_approvers_json
        ]
        if effective_roles.count("cfo") < required_roles.count("cfo"):
            return "Required CFO approval authority is unavailable after conflict exclusion."
        return "Required Director approval authority is unavailable after conflict exclusion."

    @staticmethod
    def _candidate_ids(case):
        committee = case.committee_projection_json or {}
        return {
            str(committee.get("cfo_user_id") or ""),
            *(str(user_id) for user_id in committee.get("director_user_ids", [])),
        } - {""}
