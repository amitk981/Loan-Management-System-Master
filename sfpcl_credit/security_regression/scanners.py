from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import subprocess


EMPTY_REPORT_SHA256 = hashlib.sha256(b"").hexdigest()


@dataclass(frozen=True)
class ScannerSpec:
    name: str
    expected_version: str
    version_command: tuple[str, ...]
    scan_command: tuple[str, ...]


def _safe_version(output):
    words = output.strip().split()
    return words[-1] if words else "unknown"


def _finding_count(output):
    try:
        payload = json.loads(output)
    except (TypeError, json.JSONDecodeError):
        return 0
    if isinstance(payload, dict):
        findings = payload.get("findings")
        if isinstance(findings, list):
            return len(findings)
        results = payload.get("results")
        if isinstance(results, dict):
            return sum(
                len(file_findings)
                for file_findings in results.values()
                if isinstance(file_findings, list)
            )
        vulnerabilities = payload.get("metadata", {}).get("vulnerabilities")
        if isinstance(vulnerabilities, dict):
            return sum(
                count
                for severity, count in vulnerabilities.items()
                if severity in {"high", "critical"} and isinstance(count, int)
            )
    if isinstance(payload, list):
        return sum(
            len(package.get("vulns", ()))
            for package in payload
            if isinstance(package, dict)
            and isinstance(package.get("vulns", ()), list)
        )
    return 0


def execute_scanner(
    specification,
    *,
    cwd: Path,
    run=subprocess.run,
):
    try:
        version_process = run(
            specification.version_command,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return {
            "scanner": specification.name,
            "version": "unavailable",
            "status": "fail",
            "error_code": "SCANNER_UNAVAILABLE",
            "finding_count": 0,
            "report_sha256": EMPTY_REPORT_SHA256,
        }
    if version_process.returncode != 0:
        return {
            "scanner": specification.name,
            "version": "unavailable",
            "status": "fail",
            "error_code": "SCANNER_UNAVAILABLE",
            "finding_count": 0,
            "report_sha256": EMPTY_REPORT_SHA256,
        }

    version = _safe_version(version_process.stdout)
    if version != specification.expected_version:
        return {
            "scanner": specification.name,
            "version": version,
            "status": "fail",
            "error_code": "SCANNER_VERSION_MISMATCH",
            "finding_count": 0,
            "report_sha256": EMPTY_REPORT_SHA256,
        }
    try:
        scan_process = run(
            specification.scan_command,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return {
            "scanner": specification.name,
            "version": version,
            "status": "fail",
            "error_code": "SCANNER_UNAVAILABLE",
            "finding_count": 0,
            "report_sha256": EMPTY_REPORT_SHA256,
        }

    raw_report = scan_process.stdout or scan_process.stderr
    finding_count = _finding_count(raw_report)
    failed = scan_process.returncode != 0 or finding_count > 0
    result = {
        "scanner": specification.name,
        "version": version,
        "status": "fail" if failed else "pass",
        "error_code": (
            ""
            if not failed
            else (
                "SCANNER_FINDINGS"
                if finding_count
                else "SCANNER_EXECUTION_FAILED"
            )
        ),
        "finding_count": finding_count,
        "report_sha256": hashlib.sha256(
            raw_report.encode("utf-8")
        ).hexdigest(),
    }
    return result
