#!/usr/bin/env python3
"""Validate a machine-readable UAT review packet without mutating repository state."""

import argparse
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path


EXPECTED_UAT_IDS = {f"UAT-{number:03d}" for number in range(1, 27)}
EXPECTED_GATE_IDS = {
    "QA-ENTRY-BUILD",
    "QA-ENTRY-SMOKE",
    "QA-ENTRY-USERS",
    "QA-ENTRY-SEED",
    "QA-ENTRY-RELEASE-NOTES",
    "QA-ENTRY-KNOWN-ISSUES",
    "QA-ENTRY-API-SCHEMA",
    "QA-ENTRY-WORKERS",
    "QA-ENTRY-OBJECT-STORAGE",
    "QA-EXIT-P0",
    "QA-EXIT-SEV1",
    "QA-EXIT-SEV2",
    "QA-EXIT-CORE-REGRESSION",
    "QA-EXIT-SECURITY",
    "QA-EXIT-FINANCIAL",
    "QA-EXIT-AUDIT",
    "QA-EXIT-INTEGRATION",
    "QA-EXIT-SUMMARY",
    "PROD-QA-SIGNOFF",
    "PROD-UAT-SIGNOFF",
    "PROD-SECURITY-SIGNOFF",
    "PROD-MIGRATION-SIGNOFF",
    "PROD-BACKUP-VERIFIED",
    "PROD-ROLLBACK-PLAN",
    "PROD-MONITORING-ACTIVE",
    "PROD-SUPPORT-HYPERCARE",
    "PROD-BUSINESS-APPROVAL",
    "RELEASE-REPORT-RECONCILIATION",
    "RELEASE-PERFORMANCE-ENVIRONMENT",
    "RELEASE-TRAINING",
    "RELEASE-CI-CANDIDATE",
    "RELEASE-PROMOTION",
}
EXPECTED_SIGNOFF_IDS = {
    "QA",
    "UAT",
    "SECURITY",
    "DATA",
    "INTEGRATION",
    "OPERATIONS",
    "TRAINING",
    "SUPPORT",
    "BUSINESS",
    "ROLLBACK",
    "HYPERCARE",
}
SENSITIVE_PATTERNS = {
    "credential": re.compile(
        r"(?i)\b(?:password|secret|api[_-]?key|access[_-]?token|refresh[_-]?token)"
        r"\s*[:=]\s*[\"']?[A-Za-z0-9_./+=-]{8,}"
    ),
    "PAN": re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"),
    "bearer token": re.compile(
        r"(?i)\bAuthorization\s*:\s*Bearer\s+[A-Za-z0-9._~+/=-]{8,}"
    ),
    "JWT": re.compile(
        r"\beyJ[A-Za-z0-9_-]{5,}\.[A-Za-z0-9_-]{5,}\.[A-Za-z0-9_-]{5,}\b"
    ),
    "Aadhaar": re.compile(r"(?<!\d)[0-9]{4}[\s-]?[0-9]{4}[\s-]?[0-9]{4}(?!\d)"),
    "bank/cheque/BO": re.compile(
        r"(?i)\b(?:bank(?:\s+account)?|cheque(?:\s+number)?|BO\s+account)"
        r"\b[^\n]{0,30}\b[0-9]{6,18}\b"
    ),
    "signed URL": re.compile(
        r"(?i)https?://\S+[?&](?:X-Amz-Signature|Signature|sig|token)=[^\s&]+"
    ),
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--index", required=True, type=Path)
    parser.add_argument("--packet", required=True, type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--as-of", required=True)
    arguments = parser.parse_args()

    index = json.loads(arguments.index.read_text(encoding="utf-8"))
    failures = []
    as_of = datetime.fromisoformat(arguments.as_of)
    if arguments.manifest is None:
        failures.append("MANIFEST_REQUIRED: pass the packet hash manifest")
    else:
        manifested_paths = set()
        repo_root = arguments.repo_root.resolve()
        for line_number, line in enumerate(
            arguments.manifest.read_text(encoding="utf-8").splitlines(), start=1
        ):
            if not line.strip():
                continue
            parts = line.split(maxsplit=1)
            if len(parts) != 2 or not re.fullmatch(r"[0-9a-f]{64}", parts[0]):
                failures.append(
                    f"MANIFEST_FORMAT: invalid line {line_number}"
                )
                continue
            expected_hash, relative_path = parts
            manifested_path = (arguments.repo_root / relative_path).resolve()
            try:
                manifested_path.relative_to(repo_root)
            except ValueError:
                failures.append(
                    f"MANIFEST_PATH: line {line_number} escapes repository root"
                )
                continue
            manifested_paths.add(manifested_path)
            if not manifested_path.is_file():
                failures.append(
                    f"MANIFEST_MISSING_FILE: line {line_number} does not resolve"
                )
                continue
            actual_hash = hashlib.sha256(manifested_path.read_bytes()).hexdigest()
            if actual_hash != expected_hash:
                failures.append(
                    f"MANIFEST_HASH_MISMATCH: {relative_path} expected "
                    f"{expected_hash} but found {actual_hash}"
                )
        for required_path in (arguments.index.resolve(), arguments.packet.resolve()):
            if required_path not in manifested_paths:
                failures.append(
                    f"MANIFEST_COVERAGE: missing {required_path.name}"
                )
    packet_text = arguments.packet.read_text(encoding="utf-8")
    index_text = arguments.index.read_text(encoding="utf-8")
    for label, pattern in SENSITIVE_PATTERNS.items():
        if pattern.search(packet_text) or pattern.search(index_text):
            failures.append(f"SENSITIVE_VALUE: packet/index contains a raw {label} shape")
    if index["candidate_commit"] != arguments.expected_commit:
        failures.append(
            "WRONG_CANDIDATE_COMMIT: "
            f"index has {index['candidate_commit']}; expected {arguments.expected_commit}"
        )
    actual_uat_ids = [item["id"] for item in index["uat"]]
    if (
        len(actual_uat_ids) != len(set(actual_uat_ids))
        or set(actual_uat_ids) != EXPECTED_UAT_IDS
    ):
        missing = sorted(EXPECTED_UAT_IDS - set(actual_uat_ids))
        unknown = sorted(set(actual_uat_ids) - EXPECTED_UAT_IDS)
        failures.append(
            "UAT_RECONCILIATION: expected UAT-001..026 exactly once; "
            f"missing={missing}; unknown={unknown}; rows={len(actual_uat_ids)}"
        )
    actual_gate_ids = [item["id"] for item in index["gates"]]
    if (
        len(actual_gate_ids) != len(set(actual_gate_ids))
        or set(actual_gate_ids) != EXPECTED_GATE_IDS
    ):
        missing = sorted(EXPECTED_GATE_IDS - set(actual_gate_ids))
        unknown = sorted(set(actual_gate_ids) - EXPECTED_GATE_IDS)
        failures.append(
            "GATE_RECONCILIATION: expected every QA/production/release gate exactly "
            f"once; missing={missing}; unknown={unknown}; rows={len(actual_gate_ids)}"
        )
    actual_signoff_ids = [item["id"] for item in index["signoffs"]]
    if (
        len(actual_signoff_ids) != len(set(actual_signoff_ids))
        or set(actual_signoff_ids) != EXPECTED_SIGNOFF_IDS
    ):
        missing = sorted(EXPECTED_SIGNOFF_IDS - set(actual_signoff_ids))
        unknown = sorted(set(actual_signoff_ids) - EXPECTED_SIGNOFF_IDS)
        failures.append(
            "SIGNOFF_RECONCILIATION: expected every named signoff slot exactly once; "
            f"missing={missing}; unknown={unknown}; rows={len(actual_signoff_ids)}"
        )

    evidence_ids = [item["id"] for item in index["evidence"]]
    if len(evidence_ids) != len(set(evidence_ids)):
        failures.append("EVIDENCE_RECONCILIATION: duplicate evidence ids")
    evidence_by_id = {item["id"]: item for item in index["evidence"]}
    for collection_name in ("uat", "gates", "signoffs"):
        passing_status = "SIGNED" if collection_name == "signoffs" else "PASS"
        for item in index[collection_name]:
            references = item.get("evidence_ids", [])
            unknown_references = sorted(set(references) - set(evidence_by_id))
            if unknown_references:
                failures.append(
                    f"UNMAPPED_EVIDENCE: {item['id']} references {unknown_references}"
                )
            if item["status"] == passing_status:
                current_passes = [
                    evidence_by_id[reference]
                    for reference in references
                    if reference in evidence_by_id
                    and evidence_by_id[reference]["result"] == "PASS"
                    and evidence_by_id[reference]["source_commit"]
                    == arguments.expected_commit
                ]
                if not current_passes:
                    failures.append(
                        f"UNMAPPED_PASS: {item['id']} lacks current passing evidence"
                    )

    readiness_blockers = []
    for item in index["uat"]:
        if item["status"] != "PASS":
            readiness_blockers.append(
                f"MANDATORY_UAT: {item['id']} has status {item['status']}"
            )
    for item in index["gates"]:
        if item["mandatory"] and item["status"] != "PASS":
            allowed_not_applicable = (
                item["id"] == "PROD-MIGRATION-SIGNOFF"
                and item["status"] == "NOT_APPLICABLE"
                and item.get("owner")
                and item.get("reason")
            )
            if not allowed_not_applicable:
                readiness_blockers.append(
                    f"MANDATORY_GATE: {item['id']} has status {item['status']}"
                )
    for item in index["defects"]:
        if item["severity"] == "SEV1" and item["status"] != "CLOSED":
            readiness_blockers.append(
                f"BLOCKING_DEFECT: open Sev 1 {item['id']}"
            )
        if (
            item["severity"] == "SEV2"
            and item["status"] not in {"CLOSED", "ACCEPTED"}
        ):
            readiness_blockers.append(
                f"BLOCKING_DEFECT: unaccepted Sev 2 {item['id']}"
            )
        if item["status"] == "ACCEPTED" and (
            not item.get("accepted_by") or not item.get("workaround")
        ):
            readiness_blockers.append(
                f"BLOCKING_DEFECT: {item['id']} acceptance lacks owner/workaround"
            )
    for item in index["signoffs"]:
        if item["status"] != "SIGNED":
            allowed_not_applicable = (
                item["id"] == "DATA"
                and item["status"] == "NOT_APPLICABLE"
                and item.get("owner")
                and item.get("reason")
            )
            if not allowed_not_applicable:
                readiness_blockers.append(
                    f"ABSENT_SIGNOFF: {item['id']} has status {item['status']}"
                )

    if index["engineering_readiness"] == "READY" and readiness_blockers:
        failures.extend(readiness_blockers)
    business_signoff = next(
        (item for item in index["signoffs"] if item["id"] == "BUSINESS"), None
    )
    if index["business_approval"] == "APPROVED" and (
        business_signoff is None or business_signoff["status"] != "SIGNED"
    ):
        failures.append(
            "BUSINESS_APPROVAL_MISMATCH: APPROVED requires a signed BUSINESS slot"
        )
    for evidence in index["evidence"]:
        evidence_path = arguments.repo_root / evidence["path"]
        if not evidence_path.is_file():
            failures.append(
                f"MISSING_FILE: {evidence['id']} does not resolve: {evidence['path']}"
            )
            continue
        actual_hash = hashlib.sha256(evidence_path.read_bytes()).hexdigest()
        if actual_hash != evidence["sha256"]:
            failures.append(
                f"HASH_MISMATCH: {evidence['id']} expected {evidence['sha256']} "
                f"but found {actual_hash}"
            )
        if evidence.get("expires_at") and datetime.fromisoformat(
            evidence["expires_at"]
        ) < as_of:
            failures.append(
                f"STALE_EVIDENCE: {evidence['id']} expired at {evidence['expires_at']}"
            )
        if evidence["result"] == "PASS" and evidence["source_commit"] != (
            arguments.expected_commit
        ):
            failures.append(
                f"STALE_COMMIT_EVIDENCE: {evidence['id']} passed "
                f"{evidence['source_commit']}, not {arguments.expected_commit}"
            )

    for failure in failures:
        print(f"[FAIL] {failure}")
    if failures:
        return 1
    print(
        "[PASS] packet structure, mappings, hashes, commit identity, freshness, "
        "readiness consistency, and redaction are valid"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
