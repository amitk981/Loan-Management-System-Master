from dataclasses import dataclass

from django.utils import timezone


@dataclass(frozen=True)
class NomineeValidationResult:
    status: str
    field_error: str | None


def evaluate_nominee_selection(nominee, member, *, on_date=None):
    """Classify an application nominee and preserve the intake validation contract."""
    if nominee is None:
        return NomineeValidationResult("pending", "An adult nominee must be selected.")
    if nominee.member_id != member.member_id:
        return NomineeValidationResult(
            "pending",
            "Selected nominee must belong to the application member.",
        )

    age_from_birth = None
    if nominee.date_of_birth is not None:
        age_from_birth = _age_on_date(
            nominee.date_of_birth,
            on_date=on_date or timezone.localdate(),
        )
    if nominee.minor_flag or (
        nominee.age_at_application is not None and nominee.age_at_application < 18
    ) or (age_from_birth is not None and age_from_birth < 18):
        return NomineeValidationResult(
            "minor",
            "Selected nominee must be at least 18 years old.",
        )
    if nominee.age_at_application is None and nominee.date_of_birth is None:
        return NomineeValidationResult(
            "pending",
            "Selected nominee requires age or date-of-birth evidence.",
        )
    return NomineeValidationResult("valid", None)


def _age_on_date(date_of_birth, *, on_date):
    return on_date.year - date_of_birth.year - (
        (on_date.month, on_date.day) < (date_of_birth.month, date_of_birth.day)
    )
