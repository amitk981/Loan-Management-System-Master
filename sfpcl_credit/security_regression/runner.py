import hashlib
import json
from pathlib import Path


def build_summary(
    *,
    control_results,
    scanner_results,
    approved_skip_reasons,
    hardening_results=(),
    control_evidence=(),
):
    controls = sorted(control_results, key=lambda result: result["control_id"])
    scanners = sorted(scanner_results, key=lambda result: result["scanner"])
    hardening = sorted(hardening_results, key=lambda result: result["check_id"])
    counts = {
        status: sum(result["status"] == status for result in controls)
        for status in ("pass", "fail", "skip")
    }
    skips = [
        {
            "control_id": result["control_id"],
            "reason": result.get("reason", ""),
        }
        for result in controls
        if result["status"] == "skip"
    ]
    failing_controls = [
        result["control_id"]
        for result in controls
        if result["status"] == "fail"
        or (
            result["status"] == "skip"
            and result.get("reason") not in approved_skip_reasons
        )
    ]
    failing_scanners = [
        result["scanner"]
        for result in scanners
        if result["status"] != "pass"
    ]
    failing_checks = [
        result["check_id"]
        for result in hardening
        if result["status"] != "pass"
    ]
    summary = {
        "schema_version": 1,
        "result": (
            "fail"
            if failing_controls or failing_scanners or failing_checks
            else "pass"
        ),
        "counts": counts,
        "failing_controls": failing_controls,
        "failing_scanners": failing_scanners,
        "failing_checks": failing_checks,
        "skips": skips,
        "scanner_versions": {
            result["scanner"]: result["version"] for result in scanners
        },
        "scanner_reports": scanners,
        "hardening_checks": hardening,
        "control_evidence": sorted(
            control_evidence,
            key=lambda result: result["control_id"],
        ),
    }
    canonical = json.dumps(
        summary,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    summary["summary_sha256"] = hashlib.sha256(canonical).hexdigest()
    return summary


def write_controlled_failure(output_path: Path, control_id: str) -> None:
    summary = {
        "schema_version": 1,
        "result": "fail",
        "failing_controls": [control_id],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(summary, separators=(",", ":"), sort_keys=True) + "\n",
        encoding="utf-8",
    )
