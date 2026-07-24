from sfpcl_credit.performance_readiness.matrix import PROBE_IDS
from sfpcl_credit.performance_readiness.runner import EvidenceValidationError


def validate_probe_outcome(probe_id, outcome):
    if probe_id not in PROBE_IDS or not isinstance(outcome, dict):
        raise EvidenceValidationError(f"{probe_id}: invalid probe")
    passed = {
        "PROBE-SUSTAINED-WORKFLOW": (
            outcome.get("stable_memory") is True
            and outcome.get("stable_latency") is True
        ),
        "PROBE-LARGE-DOCUMENT-VOLUME": (
            outcome.get("storage_stable") is True
        ),
        "PROBE-LARGE-AUDIT-TABLE": (
            outcome.get("queries_acceptable") is True
        ),
        "PROBE-HEAVY-EXPORT-QUEUE": (
            outcome.get("api_responsive") is True
        ),
        "PROBE-WORKER-RESTART": (
            outcome.get("idempotent_recovery") is True
            and outcome.get("duplicate_outputs") == 0
        ),
        "PROBE-REDIS-RESTART": (
            _valid_digest(outcome.get("system_of_record_before_sha256"))
            and outcome.get("system_of_record_before_sha256")
            == outcome.get("system_of_record_after_sha256")
            and outcome.get("data_loss_count") == 0
        ),
        "PROBE-DATABASE-PRESSURE": (
            outcome.get("controlled_degradation") is True
            and outcome.get("recovered") is True
        ),
    }[probe_id]
    if not passed:
        raise EvidenceValidationError(f"{probe_id}: probe outcome failed")
    return {"probe_id": probe_id, "status": "pass"}


def _valid_digest(value):
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )
