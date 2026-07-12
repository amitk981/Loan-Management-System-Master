"""Application-owned public seam for governed witness corrections."""

import re

from django.db import transaction
from django.utils import timezone

from sfpcl_credit.applications.models import Witness, WitnessChangeHistory
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.members.protected_identity import identity_hash, mask_protected_identity, protected_identity_token


class WitnessCorrectionError(Exception):
    def __init__(self, code, message, field_errors=None):
        self.code = code
        self.message = message
        self.field_errors = field_errors or {}
        super().__init__(message)


@transaction.atomic
def correct_witness(*, witness, payload, actor_user, request_ip="", request_user_agent=""):
    allowed = {"version", "witness_name", "pan", "aadhaar"}
    unknown = sorted(set(payload) - allowed)
    if unknown:
        raise WitnessCorrectionError("VALIDATION_ERROR", "Witness payload failed validation.", {field: "This verification-time field is immutable." for field in unknown})
    version = payload.get("version")
    if not isinstance(version, int) or isinstance(version, bool) or version < 1:
        raise WitnessCorrectionError("VALIDATION_ERROR", "Witness payload failed validation.", {"version": "A current positive integer version is required."})
    locked = Witness.objects.select_for_update().get(witness_id=witness.witness_id)
    if locked.version != version:
        raise WitnessCorrectionError("VERSION_CONFLICT", "Witness was changed by another user. Refresh and try again.")
    changed = []
    old_values = {}
    new_values = {}
    if "witness_name" in payload:
        value = str(payload["witness_name"] or "").strip()
        if not value:
            raise WitnessCorrectionError("VALIDATION_ERROR", "Witness payload failed validation.", {"witness_name": "This field may not be blank."})
        if value != locked.witness_name:
            changed.append("witness_name")
            old_values["witness_name"] = locked.witness_name
            new_values["witness_name"] = value
            locked.witness_name = value
    identity_changed = False
    for field, length, pattern, message in (
        ("pan", 10, r"[A-Z]{5}[0-9]{4}[A-Z]", "PAN must match the source-defined format."),
        ("aadhaar", 12, r"[0-9]{12}", "Aadhaar must be a 12 digit number."),
    ):
        if field not in payload:
            continue
        value = str(payload[field] or "").replace(" ", "").strip()
        if field == "pan":
            value = value.upper()
        if not re.fullmatch(pattern, value):
            raise WitnessCorrectionError("VALIDATION_ERROR", "Witness payload failed validation.", {field: message})
        encrypted_field = f"{field}_encrypted"
        current_mask = mask_protected_identity(getattr(locked, encrypted_field), length)
        proposed_hash = identity_hash(value)
        if proposed_hash != getattr(locked, f"{field}_hash"):
            identity_changed = True
            changed.append(field)
            old_values[field] = current_mask
            new_values[field] = mask_protected_identity(protected_identity_token(value, length), length)
            setattr(locked, encrypted_field, protected_identity_token(value, length))
            setattr(locked, f"{field}_hash", proposed_hash)
    if identity_changed and locked.verified_by_user_id == actor_user.user_id:
        raise WitnessCorrectionError("MAKER_CHECKER_REQUIRED", "A different authorised user must correct verified witness identity.")
    if not changed:
        raise WitnessCorrectionError("VALIDATION_ERROR", "Witness payload failed validation.", {"non_field_errors": "Provide at least one changed field."})
    locked.version += 1
    locked.updated_at = timezone.now()
    locked.updated_by_user = actor_user
    locked.save()
    WitnessChangeHistory.objects.create(witness=locked, actor_user=actor_user, witness_version=locked.version, changed_fields=changed, old_value_json=old_values, new_value_json=new_values)
    AuditLog.objects.create(actor_user=actor_user, action="applications.witness.corrected", entity_type="witness", entity_id=locked.witness_id, old_value_json={"version": version}, new_value_json={"version": locked.version, "changed_fields": changed}, ip_address=request_ip, user_agent=request_user_agent)
    return locked
