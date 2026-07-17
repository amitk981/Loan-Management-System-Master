#!/usr/bin/env bash
set -uo pipefail

# Compare the serial backend coverage control with the same bounded parallel
# module used by the authoritative gate. The report proves identical outcomes
# and exact executed/missing/excluded line sets whenever concurrency is audited.

repo_root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$repo_root"

parallel_workers="${1:-2}"
output_dir="${2:-$repo_root/.ralph/shadow-coverage/$(date '+%Y-%m-%d_%H%M%S')}"
backend_python="${RALPH_BACKEND_PYTHON:-$repo_root/.ralph/venv/bin/python}"
backend_dir="$(awk -F': *' '/^[[:space:]]*backend_dir:/ {sub(/[[:space:]]*#.*$/, "", $2); print $2; exit}' "$repo_root/.ralph/config.yaml" | tr -d '"' | xargs || true)"
backend_dir="${backend_dir:-sfpcl_credit}"
coverage_floor="$(awk -F': *' '/^[[:space:]]*coverage_fail_under:/ {sub(/[[:space:]]*#.*$/, "", $2); print $2; exit}' "$repo_root/.ralph/config.yaml" | xargs || true)"
coverage_floor="${coverage_floor:-85}"

if ! [[ "$parallel_workers" =~ ^[1-9][0-9]*$ ]]; then
  echo "Parallel worker count must be a positive integer." >&2
  exit 2
fi
if [[ ! -x "$backend_python" ]]; then
  echo "Backend Python is unavailable: $backend_python" >&2
  exit 2
fi

mkdir -p "$output_dir"
output_dir="$(cd "$output_dir" && pwd -P)"
sequential_log="$output_dir/sequential.log"
parallel_log="$output_dir/parallel-${parallel_workers}.log"
sequential_data="$output_dir/.coverage.sequential"
sequential_json="$output_dir/sequential-coverage.json"
parallel_json="$output_dir/parallel-coverage.json"
comparison_json="$output_dir/comparison.json"
summary="$output_dir/parallel-coverage-pilot.md"

monotonic_ms() {
  python3 -c 'import time; print(time.monotonic_ns() // 1_000_000)'
}

echo "Shadow pilot output: $output_dir"
echo "Starting authoritative sequential coverage control..."
started="$(monotonic_ms)"
sequential_rc=0
COVERAGE_FILE="$sequential_data" "$backend_python" -m coverage run \
  --source="$backend_dir" "$backend_dir/manage.py" test "$backend_dir.tests" --timing \
  > "$sequential_log" 2>&1 || sequential_rc=$?
sequential_ms=$(( $(monotonic_ms) - started ))
COVERAGE_FILE="$sequential_data" "$backend_python" -m coverage json \
  -o "$sequential_json" --pretty-print >> "$sequential_log" 2>&1 \
  || sequential_rc=$?
if (( sequential_rc == 0 )); then
  COVERAGE_FILE="$sequential_data" "$backend_python" -m coverage report \
    --fail-under="$coverage_floor" >> "$sequential_log" 2>&1 \
    || sequential_rc=$?
fi

echo "Sequential control finished in $((sequential_ms / 1000))s (exit $sequential_rc)."
echo "Starting ${parallel_workers}-worker shadow coverage..."
started="$(monotonic_ms)"
parallel_rc=0
"$repo_root/scripts/ralph-parallel-backend-coverage.sh" \
  "$backend_python" "$repo_root" "$backend_dir" \
  "$parallel_workers" "$coverage_floor" "$parallel_json" \
  > "$parallel_log" 2>&1 || parallel_rc=$?
parallel_ms=$(( $(monotonic_ms) - started ))

echo "Parallel shadow finished in $((parallel_ms / 1000))s (exit $parallel_rc)."
python3 - \
  "$sequential_log" "$parallel_log" \
  "$sequential_json" "$parallel_json" \
  "$sequential_rc" "$parallel_rc" \
  "$sequential_ms" "$parallel_ms" "$parallel_workers" \
  "$comparison_json" "$summary" <<'PY'
import hashlib
import json
import re
import sys
from pathlib import Path

(
    sequential_log_path,
    parallel_log_path,
    sequential_json_path,
    parallel_json_path,
    sequential_rc,
    parallel_rc,
    sequential_ms,
    parallel_ms,
    workers,
    comparison_path,
    summary_path,
) = sys.argv[1:]


def outcome(path: str, rc: str) -> dict:
    text = Path(path).read_text(errors="replace")
    found = re.findall(r"Found (\d+) test\(s\)\.", text)
    ran = re.findall(r"Ran (\d+) tests? in", text)
    skipped = re.findall(r"(?:OK|FAILED) \([^\n]*skipped=(\d+)", text)
    failures = re.findall(r"FAILED \([^\n]*failures=(\d+)", text)
    errors = re.findall(r"FAILED \([^\n]*errors=(\d+)", text)
    return {
        "exit_code": int(rc),
        "discovered_tests": int(found[-1]) if found else None,
        "ran_tests": int(ran[-1]) if ran else None,
        "skipped_tests": int(skipped[-1]) if skipped else 0,
        "failures": int(failures[-1]) if failures else 0,
        "errors": int(errors[-1]) if errors else 0,
    }


def coverage(path: str) -> dict:
    report = json.loads(Path(path).read_text())
    exact_files = {
        filename: {
            "executed_lines": details["executed_lines"],
            "missing_lines": details["missing_lines"],
            "excluded_lines": details["excluded_lines"],
        }
        for filename, details in sorted(report["files"].items())
    }
    canonical = json.dumps(exact_files, sort_keys=True, separators=(",", ":"))
    totals = report["totals"]
    return {
        "num_statements": totals["num_statements"],
        "covered_lines": totals["covered_lines"],
        "missing_lines": totals["missing_lines"],
        "excluded_lines": totals["excluded_lines"],
        "percent_covered": totals["percent_covered"],
        "exact_line_set_sha256": hashlib.sha256(canonical.encode()).hexdigest(),
        "exact_files": exact_files,
    }


sequential_outcome = outcome(sequential_log_path, sequential_rc)
parallel_outcome = outcome(parallel_log_path, parallel_rc)
try:
    sequential_coverage = coverage(sequential_json_path)
    parallel_coverage = coverage(parallel_json_path)
except (OSError, KeyError, json.JSONDecodeError) as error:
    sequential_coverage = {"report_error": str(error)}
    parallel_coverage = {"report_error": str(error)}

outcomes_equal = sequential_outcome == parallel_outcome
coverage_equal = sequential_coverage == parallel_coverage
passed = outcomes_equal and coverage_equal and sequential_outcome["exit_code"] == 0
comparison = {
    "passed": passed,
    "parallel_workers": int(workers),
    "sequential_duration_ms": int(sequential_ms),
    "parallel_duration_ms": int(parallel_ms),
    "speedup": round(int(sequential_ms) / int(parallel_ms), 3),
    "outcomes_equal": outcomes_equal,
    "coverage_equal": coverage_equal,
    "sequential_outcome": sequential_outcome,
    "parallel_outcome": parallel_outcome,
    "sequential_coverage": {
        key: value for key, value in sequential_coverage.items() if key != "exact_files"
    },
    "parallel_coverage": {
        key: value for key, value in parallel_coverage.items() if key != "exact_files"
    },
}
Path(comparison_path).write_text(json.dumps(comparison, indent=2) + "\n")

verdict = "PASS" if passed else "FAIL"
Path(summary_path).write_text(
    "# Parallel Coverage Shadow Pilot\n\n"
    f"Verdict: {verdict}\n\n"
    f"- Workers: {workers}\n"
    f"- Sequential: {int(sequential_ms) / 1000:.1f}s\n"
    f"- Parallel: {int(parallel_ms) / 1000:.1f}s\n"
    f"- Speedup: {comparison['speedup']:.3f}x\n"
    f"- Test outcomes identical: {outcomes_equal}\n"
    f"- Exact executed/missing/excluded line sets identical: {coverage_equal}\n"
    f"- Sequential outcome: {sequential_outcome}\n"
    f"- Parallel outcome: {parallel_outcome}\n"
    f"- Sequential coverage: {comparison['sequential_coverage']}\n"
    f"- Parallel coverage: {comparison['parallel_coverage']}\n"
)
raise SystemExit(0 if passed else 1)
PY
comparison_rc=$?

cat "$summary"
exit "$comparison_rc"
