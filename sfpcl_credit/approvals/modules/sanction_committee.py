from dataclasses import dataclass
from datetime import date
from uuid import UUID

from django.db.models import Q

from sfpcl_credit.approvals.models import SanctionCommittee


class SanctionCommitteeResolutionError(Exception):
    code = "SANCTION_COMMITTEE_RESOLUTION_ERROR"


class NoEffectiveSanctionCommittee(SanctionCommitteeResolutionError):
    code = "NO_EFFECTIVE_SANCTION_COMMITTEE"


class AmbiguousSanctionCommittee(SanctionCommitteeResolutionError):
    code = "AMBIGUOUS_SANCTION_COMMITTEE"


@dataclass(frozen=True)
class SanctionCommitteeProjection:
    sanction_committee_id: UUID
    version_number: str
    decision_date: date
    cfo_user_id: UUID
    director_1_user_id: UUID
    director_2_user_id: UUID


def resolve_sanction_committee(decision_date):
    if not isinstance(decision_date, date):
        raise NoEffectiveSanctionCommittee("A valid decision date is required.")
    matches = list(
        SanctionCommittee.objects.filter(
            status__in=(SanctionCommittee.STATUS_ACTIVE, SanctionCommittee.STATUS_SUPERSEDED),
            effective_from__lte=decision_date,
        ).filter(Q(effective_to__isnull=True) | Q(effective_to__gte=decision_date))
    )
    if not matches:
        raise NoEffectiveSanctionCommittee("No effective sanction committee matches the decision date.")
    if len(matches) != 1:
        raise AmbiguousSanctionCommittee("More than one sanction committee matches the decision date.")
    row = matches[0]
    return SanctionCommitteeProjection(
        sanction_committee_id=row.pk,
        version_number=row.version_number,
        decision_date=decision_date,
        cfo_user_id=row.cfo_user_id,
        director_1_user_id=row.director_1_user_id,
        director_2_user_id=row.director_2_user_id,
    )
