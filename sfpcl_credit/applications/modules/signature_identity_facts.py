"""Application-owned canonical signer identity facts for legal evidence."""

from dataclasses import dataclass

from sfpcl_credit.applications.models import Witness
from sfpcl_credit.identity.models import User


@dataclass(frozen=True)
class SignerIdentityFact:
    party_type: str
    party_id: object
    name: str


def resolve_signer_identity(*, application, party_type, party_id):
    """Return the canonical signer only when the requested id belongs to its owner."""
    if party_id is None:
        return None
    if party_type == "borrower":
        if application.member_id != party_id:
            return None
        member = application.member
        return SignerIdentityFact("borrower", member.member_id, member.legal_name)
    if party_type == "nominee":
        nominee = application.nominee
        if nominee is None or nominee.nominee_id != party_id:
            return None
        return SignerIdentityFact("nominee", nominee.nominee_id, nominee.nominee_name)
    if party_type == "witness":
        witness = Witness.objects.filter(
            loan_application_id=application.pk,
            witness_id=party_id,
        ).first()
        if witness is None:
            return None
        return SignerIdentityFact("witness", witness.witness_id, witness.witness_name)
    if party_type == "user":
        user = User.objects.filter(user_id=party_id, status=User.ACTIVE_STATUS).first()
        if user is None:
            return None
        return SignerIdentityFact("user", user.user_id, user.full_name)
    return None
