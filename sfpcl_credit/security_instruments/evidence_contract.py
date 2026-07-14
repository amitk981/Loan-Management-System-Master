"""Narrow immutable contract for cross-owner Stage-4 evidence.

Only a top-level process may issue this adapter. Security modules own policy; the adapter owns
canonical approval/legal lookups and checklist projection. Keeping the issuer token private makes
missing or caller-constructed adapters fail closed instead of treating a DTO as authority.
"""

from dataclasses import dataclass
from typing import Callable


_ISSUER = object()


class UncoordinatedEvidence(Exception):
    pass


@dataclass(frozen=True)
class SecurityEvidenceAccess:
    approved_facts: Callable
    approval_read_allowed: Callable
    canonical_stage4_scope: Callable
    poa_evidence: Callable
    execution_signatures: Callable
    sh4_evidence: Callable
    cdsl_evidence: Callable
    project_checklist_item: Callable
    mask_sensitive: Callable
    _issuer: object

    def __post_init__(self):
        if self._issuer is not _ISSUER:
            raise UncoordinatedEvidence("Cross-owner evidence must be issued by the process coordinator.")


def _issue_security_evidence_access(**callbacks):
    return SecurityEvidenceAccess(_issuer=_ISSUER, **callbacks)


def require_coordinated(access):
    if not isinstance(access, SecurityEvidenceAccess) or access._issuer is not _ISSUER:
        raise UncoordinatedEvidence("Canonical Stage-4 evidence coordination is required.")
    return access
