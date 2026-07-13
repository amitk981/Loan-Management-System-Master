import re
import sys
from pathlib import Path


class AcceptanceEvidenceError(ValueError):
    pass


REQUIRED_PATTERNS = (
    re.compile(r"^Found 5 test\(s\)\.$", re.MULTILINE),
    re.compile(r"^database_backend=postgresql\b", re.MULTILINE),
    re.compile(r"^Ran 5 tests in ", re.MULTILINE),
    re.compile(r"^OK$", re.MULTILINE),
)
FORBIDDEN_PATTERNS = (
    re.compile(r"skipped", re.IGNORECASE),
    re.compile(r"^FAILED", re.MULTILINE),
    re.compile(r"^ERROR", re.MULTILINE),
    re.compile(r"OperationalError"),
    re.compile(r"connection .*?(?:failed|refused)", re.IGNORECASE),
    re.compile(r"setup failure", re.IGNORECASE),
    re.compile(r"^Ran 0 tests", re.MULTILINE),
)


def verify_acceptance_logs(log_paths):
    paths = [Path(path) for path in log_paths]
    if len(paths) != 2 or len(set(paths)) != 2:
        raise AcceptanceEvidenceError("Exactly two distinct PostgreSQL logs are required.")

    for path in paths:
        if not path.is_file():
            raise AcceptanceEvidenceError(f"Acceptance log is missing: {path}")
        content = path.read_text()
        missing = [pattern.pattern for pattern in REQUIRED_PATTERNS if not pattern.search(content)]
        if missing:
            raise AcceptanceEvidenceError(
                f"Acceptance log {path} is missing required markers: {missing}"
            )
        forbidden = [
            pattern.pattern for pattern in FORBIDDEN_PATTERNS if pattern.search(content)
        ]
        if forbidden:
            raise AcceptanceEvidenceError(
                f"Acceptance log {path} contains failure markers: {forbidden}"
            )


if __name__ == "__main__":
    try:
        verify_acceptance_logs(sys.argv[1:])
    except AcceptanceEvidenceError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
    print("Verified two PostgreSQL acceptance runs: 5 tests each, zero skips.")
