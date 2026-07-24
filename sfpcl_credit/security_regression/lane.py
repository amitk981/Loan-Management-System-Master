import base64
import json
import os
from pathlib import Path
import re
import subprocess
import sys

from sfpcl_credit.security_regression.matrix import (
    CONTROL_MATRIX,
    validate_control_matrix,
    validate_test_labels,
)
from sfpcl_credit.security_regression.runner import build_summary
from sfpcl_credit.security_regression.scanners import (
    ScannerSpec,
    execute_scanner,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPOSITORY_ROOT / "sfpcl_credit"
BACKEND_PYTHON = str(Path(sys.prefix) / "bin" / "python")
SENSITIVE_OUTPUT_PATTERNS = (
    re.compile(r"eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}"),
    re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"),
    re.compile(r"\b[0-9]{12}\b"),
    re.compile(r"(?i)(password|secret|api[_-]?key)\s*[:=]\s*[^\s,;]+"),
)


def scanner_specifications():
    return (
        ScannerSpec(
            name="detect-secrets",
            expected_version="1.5.0",
            version_command=(
                BACKEND_PYTHON,
                str(Path(sys.prefix) / "bin" / "detect-secrets"),
                "--version",
            ),
            scan_command=(
                BACKEND_PYTHON,
                str(Path(sys.prefix) / "bin" / "detect-secrets"),
                "scan",
                "--no-verify",
                "--exclude-files",
                r"(^|/)(tests|migrations|docs/source|\.ralph)(/|$)",
                "sfpcl_credit",
                "sfpcl-lms/src",
            ),
        ),
        ScannerSpec(
            name="pip-audit",
            expected_version="2.10.1",
            version_command=(BACKEND_PYTHON, "-m", "pip_audit", "--version"),
            scan_command=(
                BACKEND_PYTHON,
                "-m",
                "pip_audit",
                "--format",
                "json",
                "--requirement",
                "sfpcl_credit/requirements.txt",
            ),
        ),
        ScannerSpec(
            name="npm-audit",
            expected_version="10.8.2",
            version_command=("npm", "--version"),
            scan_command=(
                "npm",
                "audit",
                "--json",
                "--audit-level=high",
                "--prefix",
                "sfpcl-lms",
            ),
        ),
    )


def _run_control_tests(matrix, run=subprocess.run):
    labels = sorted(
        {
            label
            for control in matrix
            for label in control.get("test_labels", ())
        }
    )
    process = run(
        [
            BACKEND_PYTHON,
            str(BACKEND_ROOT / "manage.py"),
            "test",
            *labels,
            "--verbosity",
            "1",
        ],
        cwd=REPOSITORY_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    output = f"{process.stdout}\n{process.stderr}"
    failed_labels = set(
        re.findall(r"(?:FAIL|ERROR): [^(]+ \(([^)]+)\)", output)
    )
    if process.returncode and not failed_labels:
        failed_labels = set(labels)

    results = []
    for control in matrix:
        if control.get("blocking_finding"):
            results.append(
                {
                    "control_id": control["control_id"],
                    "status": "fail",
                    "reason": control["blocking_finding"],
                }
            )
            continue
        status = (
            "fail"
            if any(label in failed_labels for label in control["test_labels"])
            else "pass"
        )
        results.append({"control_id": control["control_id"], "status": status})
    return results, output


def _production_settings_check(run=subprocess.run):
    synthetic_key = base64.urlsafe_b64encode(b"P" * 32).decode("ascii")
    synthetic_lookup = base64.urlsafe_b64encode(b"H" * 32).decode("ascii")
    base_environment = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith("SFPCL_")
    }
    production_environment = {
        **base_environment,
        "SFPCL_DEPLOYMENT_ENVIRONMENT": "production",
        "SFPCL_SECRET_KEY": "synthetic-production-django-key-32",
        "SFPCL_JWT_SIGNING_KEY": "synthetic-production-jwt-key-value",
        "SFPCL_ALLOWED_HOSTS": "credit.example.test",
        "SFPCL_CORS_ORIGINS": "https://lms.example.test",
        "SFPCL_CSRF_TRUSTED_ORIGINS": "https://lms.example.test",
        "SFPCL_FIELD_ENCRYPTION_CURRENT_VERSION": "prod-v1",
        "SFPCL_FIELD_ENCRYPTION_KEY_REF": "vault:test/prod-v1",
        "SFPCL_FIELD_ENCRYPTION_KEYS": json.dumps({"prod-v1": synthetic_key}),
        "SFPCL_FIELD_LOOKUP_KEY": synthetic_lookup,
    }
    probe = (
        "from sfpcl_credit.config import production_settings as s;"
        "assert s.DEBUG is False;"
        "assert s.SECURE_SSL_REDIRECT is True;"
        "assert s.SESSION_COOKIE_SECURE is True;"
        "assert s.CSRF_COOKIE_SECURE is True;"
        "assert s.SECURE_HSTS_SECONDS > 0;"
        "assert s.CORS_ALLOW_ALL_ORIGINS is False;"
        "assert s.ENABLE_DEMO_SURFACES is False"
    )
    processes = [
        run(
            [BACKEND_PYTHON, "-c", probe],
            cwd=REPOSITORY_ROOT,
            env=production_environment,
            capture_output=True,
            text=True,
            check=False,
        )
    ]
    for required_variable in (
        "SFPCL_SECRET_KEY",
        "SFPCL_JWT_SIGNING_KEY",
        "SFPCL_ALLOWED_HOSTS",
        "SFPCL_CORS_ORIGINS",
        "SFPCL_CSRF_TRUSTED_ORIGINS",
        "SFPCL_FIELD_LOOKUP_KEY",
    ):
        negative_environment = {**production_environment}
        negative_environment.pop(required_variable)
        processes.append(
            run(
                [BACKEND_PYTHON, "-c", probe],
                cwd=REPOSITORY_ROOT,
                env=negative_environment,
                capture_output=True,
                text=True,
                check=False,
            )
        )
    passed = (
        processes[0].returncode == 0
        and all(process.returncode != 0 for process in processes[1:])
    )
    output = "\n".join(
        f"{process.stdout}\n{process.stderr}" for process in processes
    )
    return {
        "check_id": "production-settings",
        "status": "pass" if passed else "fail",
    }, output


def _output_safety_check(outputs):
    matched_pattern_count = sum(
        bool(pattern.search(output))
        for output in outputs
        for pattern in SENSITIVE_OUTPUT_PATTERNS
    )
    return {
        "check_id": "no-secret-output",
        "status": "pass" if matched_pattern_count == 0 else "fail",
        "finding_count": matched_pattern_count,
    }


def run_security_regression(*, run=subprocess.run):
    matrix = validate_control_matrix(CONTROL_MATRIX)
    unresolved = validate_test_labels(matrix)
    if unresolved:
        control_results = [
            {
                "control_id": control["control_id"],
                "status": "fail",
                "reason": "UNRESOLVED_TEST_LABEL",
            }
            for control in matrix
        ]
        test_output = ""
    else:
        control_results, test_output = _run_control_tests(matrix, run=run)

    production_result, production_output = _production_settings_check(run=run)
    scanner_results = [
        execute_scanner(specification, cwd=REPOSITORY_ROOT, run=run)
        for specification in scanner_specifications()
    ]
    output_result = _output_safety_check((test_output, production_output))
    return build_summary(
        control_results=control_results,
        scanner_results=scanner_results,
        approved_skip_reasons=set(),
        hardening_results=(production_result, output_result),
        control_evidence=(
            {
                "control_id": control["control_id"],
                **(
                    {"test_labels": list(control["test_labels"])}
                    if control.get("test_labels")
                    else {"blocking_finding": control["blocking_finding"]}
                ),
            }
            for control in matrix
        ),
    )
