#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$repo_root"

source scripts/lib/ralph-fast-candidate-checks.sh
source scripts/lib/ralph-runtime-capabilities.sh
source scripts/lib/ralph-postgresql-acceptance.sh
source scripts/lib/ralph-browser-acceptance.sh

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

fixture_dir="$(mktemp -d "${TMPDIR:-/tmp}/ralph-acceptance-contract.XXXXXX")"
trap 'rm -rf "$fixture_dir"' EXIT

# Agent completion is a one-value protocol, not a denylist of failure words.
ralph_agent_declared_result_is_ready "Ready for independent validation" \
  || fail "the exact ready verdict was rejected"
ralph_agent_declared_result_is_ready "  Ready for independent validation  " \
  || fail "surrounding verdict whitespace was not trimmed"
for result in "" "In Progress" "Incomplete" "Partial" "Success" \
  "ready for independent validation" "Ready for independent validation." \
  "Ready  for independent validation" \
  "Ready for independent validation; except browser evidence"; do
  if ralph_agent_declared_result_is_ready "$result"; then
    fail "non-exact agent verdict passed: ${result:-<missing>}"
  fi
done
cat > "$fixture_dir/ready-packet.md" <<'EOF'
## Result
Ready for independent validation
EOF
cat > "$fixture_dir/duplicate-result-packet.md" <<'EOF'
## Result
Ready for independent validation

## Result
Incomplete
EOF
cat > "$fixture_dir/unmergeable-packet.md" <<'EOF'
## Result
Ready for independent validation

Do not merge because evidence is incomplete.
EOF
ralph_review_packet_declares_ready "$fixture_dir/ready-packet.md" \
  || fail "valid review packet was rejected"
for packet in duplicate-result-packet unmergeable-packet; do
  if ralph_review_packet_declares_ready "$fixture_dir/$packet.md"; then
    fail "$packet did not fail closed"
  fi
done

cat > "$fixture_dir/ordinary.md" <<'EOF'
## Runtime Capabilities
- `none`

## Goal
Update documentation without runtime services.
EOF
cat > "$fixture_dir/missing.md" <<'EOF'
## Goal
No declaration is present.
EOF
cat > "$fixture_dir/empty.md" <<'EOF'
## Runtime Capabilities

## Goal
The declaration is empty.
EOF
cat > "$fixture_dir/mixed-none.md" <<'EOF'
## Runtime Capabilities
- `none`
- `localhost-e2e-server`

## Trusted Browser Acceptance
- Spec: `e2e/flow.spec.ts`
- Screenshot: `flow.png`
EOF
cat > "$fixture_dir/browser-requirement-without-capability.md" <<'EOF'
## Runtime Capabilities
- `none`

## Acceptance Criteria
- Save the Playwright screenshot `flow.png`.
EOF
cat > "$fixture_dir/postgres-requirement-without-capability.md" <<'EOF'
## Runtime Capabilities
- `none`

## Test Cases
- Run the concurrent PostgreSQL race twice.
EOF
cat > "$fixture_dir/performance-concurrency.md" <<'EOF'
## Runtime Capabilities
- `none`

## Test Cases
- Measure 500 concurrent browser users in the external load-test lane.
- Preserve traceability through the three-month grace period.
EOF
cat > "$fixture_dir/domain-locking.md" <<'EOF'
## Runtime Capabilities
- `none`

## Requirements
- Follow the identity locking and reverification policy for KYC fields.
EOF
cat > "$fixture_dir/postgres-capability-without-contract.md" <<'EOF'
## Runtime Capabilities
- `postgresql-five-race-acceptance`

## Test Cases
- Run the concurrent PostgreSQL race twice.
EOF

ralph_validate_slice_capabilities "$fixture_dir/ordinary.md" \
  || fail "an explicit none capability was rejected"
for invalid in missing empty mixed-none; do
  if ralph_validate_slice_capabilities "$fixture_dir/$invalid.md" >/dev/null 2>&1; then
    fail "$invalid runtime declaration did not fail closed"
  fi
done
if ralph_validate_slice_runtime_requirements \
    "$fixture_dir/browser-requirement-without-capability.md" >/dev/null 2>&1; then
  fail "browser evidence requirement passed without localhost capability"
fi
if ralph_validate_slice_runtime_requirements \
    "$fixture_dir/postgres-requirement-without-capability.md" >/dev/null 2>&1; then
  fail "PostgreSQL race requirement passed without PostgreSQL capability"
fi
ralph_validate_slice_runtime_requirements "$fixture_dir/performance-concurrency.md" \
  || fail "ordinary concurrent-user performance text incorrectly required PostgreSQL"
ralph_validate_slice_runtime_requirements "$fixture_dir/domain-locking.md" \
  || fail "domain-level locking language incorrectly required PostgreSQL"
if ralph_validate_slice_runtime_requirements \
    "$fixture_dir/postgres-capability-without-contract.md" >/dev/null 2>&1; then
  fail "PostgreSQL capability passed without its trusted contract"
fi

cat > "$fixture_dir/postgres-valid.md" <<'EOF'
## Runtime Capabilities
- `postgresql-five-race-acceptance`

## Trusted PostgreSQL Acceptance
- Test: `sfpcl_credit.tests.test_payments.PaymentRaceTests.test_duplicate_reference`
- Test: `sfpcl_credit.tests.test_payments.PaymentRaceTests.test_concurrent_posting`
- Expected tests: `2`
EOF
cat > "$fixture_dir/postgres-no-count.md" <<'EOF'
## Runtime Capabilities
- `postgresql-five-race-acceptance`

## Trusted PostgreSQL Acceptance
- Test: `sfpcl_credit.tests.test_payments.PaymentRaceTests.test_concurrent_posting`
EOF
cat > "$fixture_dir/postgres-no-label.md" <<'EOF'
## Runtime Capabilities
- `postgresql-five-race-acceptance`

## Trusted PostgreSQL Acceptance
- Expected tests: `1`
EOF
cat > "$fixture_dir/postgres-duplicate.md" <<'EOF'
## Runtime Capabilities
- `postgresql-five-race-acceptance`

## Trusted PostgreSQL Acceptance
- Test: `sfpcl_credit.tests.test_payments.PaymentRaceTests.test_concurrent_posting`
- Test: `sfpcl_credit.tests.test_payments.PaymentRaceTests.test_concurrent_posting`
- Expected tests: `1`
EOF
cat > "$fixture_dir/postgres-unsafe.md" <<'EOF'
## Runtime Capabilities
- `postgresql-five-race-acceptance`

## Trusted PostgreSQL Acceptance
- Test: `../../manage.py`
- Expected tests: `1`
EOF

ralph_validate_trusted_postgresql_acceptance "$fixture_dir/postgres-valid.md" \
  || fail "valid slice-specific PostgreSQL contract was rejected"
[[ "$(ralph_codex_permission_profile_for_slice "$fixture_dir/postgres-valid.md")" == "ralph-postgres" ]] \
  || fail "valid PostgreSQL contract did not select the scoped PostgreSQL profile"
[[ "$(ralph_trusted_postgresql_test_labels "$fixture_dir/postgres-valid.md" | paste -sd, -)" \
    == "sfpcl_credit.tests.test_payments.PaymentRaceTests.test_duplicate_reference,sfpcl_credit.tests.test_payments.PaymentRaceTests.test_concurrent_posting" ]] \
  || fail "PostgreSQL test-label parser returned the wrong labels"
[[ "$(ralph_trusted_postgresql_expected_count "$fixture_dir/postgres-valid.md")" == "2" ]] \
  || fail "PostgreSQL expected-count parser returned the wrong value"
for invalid in postgres-no-count postgres-no-label postgres-duplicate postgres-unsafe; do
  if ralph_validate_trusted_postgresql_acceptance "$fixture_dir/$invalid.md" >/dev/null 2>&1; then
    fail "$invalid PostgreSQL contract did not fail closed"
  fi
done

cat > "$fixture_dir/postgres-pass.log" <<'EOF'
Found 2 test(s).
..
Ran 2 tests in 0.123s
OK
EOF
cat > "$fixture_dir/postgres-wrong-count.log" <<'EOF'
Found 1 test(s).
.
Ran 1 test in 0.123s
OK
EOF
postgresql_acceptance_log_passes "$fixture_dir/postgres-pass.log" 2 \
  || fail "matching PostgreSQL test evidence was rejected"
if postgresql_acceptance_log_passes "$fixture_dir/postgres-wrong-count.log" 2; then
  fail "PostgreSQL evidence with the wrong executed count passed"
fi

mkdir -p "$fixture_dir/browser/e2e"
touch "$fixture_dir/browser/e2e/flow.spec.ts"
cat > "$fixture_dir/browser-valid.md" <<'EOF'
## Runtime Capabilities
- `localhost-e2e-server`

## Trusted Browser Acceptance
- Spec: `e2e/flow.spec.ts`
- Screenshot: `flow.png`
EOF
cat > "$fixture_dir/browser-no-screenshot.md" <<'EOF'
## Runtime Capabilities
- `localhost-e2e-server`

## Trusted Browser Acceptance
- Spec: `e2e/flow.spec.ts`
EOF
cat > "$fixture_dir/browser-duplicate.md" <<'EOF'
## Runtime Capabilities
- `localhost-e2e-server`

## Trusted Browser Acceptance
- Spec: `e2e/flow.spec.ts`
- Spec: `e2e/flow.spec.ts`
- Screenshot: `flow.png`
- Screenshot: `flow.png`
EOF

ralph_validate_trusted_browser_acceptance \
  "$fixture_dir/browser-valid.md" "$fixture_dir/browser" \
  || fail "valid browser contract was rejected"
[[ "$(ralph_codex_permission_profile_for_slice "$fixture_dir/browser-valid.md")" == "ralph-localhost" ]] \
  || fail "valid browser contract did not select the scoped localhost profile"
if ralph_validate_trusted_browser_acceptance \
    "$fixture_dir/browser-no-screenshot.md" "$fixture_dir/browser" >/dev/null 2>&1; then
  fail "browser contract without a screenshot passed"
fi
if ralph_validate_trusted_browser_acceptance \
    "$fixture_dir/browser-duplicate.md" "$fixture_dir/browser" >/dev/null 2>&1; then
  fail "browser contract with duplicate evidence entries passed"
fi

run_one="$fixture_dir/browser-evidence/run-1"
run_two="$fixture_dir/browser-evidence/run-2"
mkdir -p "$run_one" "$run_two"

write_test_png() {
  local path="$1" variant="$2"
  python3 - "$path" "$variant" <<'PY'
import struct
import sys
import zlib
from pathlib import Path

path = Path(sys.argv[1])
variant = int(sys.argv[2])
width = height = 2
pixel = bytes(((40 * variant) % 256, 80, 160, 255))
raw = b"".join(b"\x00" + pixel * width for _ in range(height))

def chunk(kind: bytes, payload: bytes) -> bytes:
    return (
        struct.pack(">I", len(payload))
        + kind
        + payload
        + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
    )

png = (
    b"\x89PNG\r\n\x1a\n"
    + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
    + chunk(b"IDAT", zlib.compress(raw))
    + chunk(b"IEND", b"")
)
path.write_bytes(png)
PY
}

# A signature-only payload is not reviewable screenshot evidence.
printf '\211PNG\r\n\032\nnot-an-image' > "$run_one/flow.png"
if ralph_write_trusted_browser_screenshot_manifest \
    "$fixture_dir/browser-valid.md" "$run_one" "$fixture_dir/corrupt.sha256" \
    >/dev/null 2>&1; then
  fail "corrupt signature-only PNG evidence passed"
fi
write_test_png "$run_one/flow.png" 1
ralph_write_trusted_browser_screenshot_manifest \
  "$fixture_dir/browser-valid.md" "$run_one" "$fixture_dir/run-1.sha256" \
  || fail "valid first-run screenshot evidence was rejected"
if ralph_write_trusted_browser_screenshot_manifest \
    "$fixture_dir/browser-valid.md" "$run_two" "$fixture_dir/run-2.sha256" >/dev/null 2>&1; then
  fail "second run reused or accepted the first run screenshot"
fi
ln -s "$run_one/flow.png" "$run_two/flow.png"
if ralph_write_trusted_browser_screenshot_manifest \
    "$fixture_dir/browser-valid.md" "$run_two" "$fixture_dir/run-2.sha256" >/dev/null 2>&1; then
  fail "second run accepted a symlink to first-run screenshot evidence"
fi
rm "$run_two/flow.png"
write_test_png "$run_two/flow.png" 2
ralph_write_trusted_browser_screenshot_manifest \
  "$fixture_dir/browser-valid.md" "$run_two" "$fixture_dir/run-2.sha256" \
  || fail "valid second-run screenshot evidence was rejected"
grep -qF 'flow.png' "$fixture_dir/run-1.sha256" \
  || fail "first-run screenshot manifest is incomplete"
grep -qF 'flow.png' "$fixture_dir/run-2.sha256" \
  || fail "second-run screenshot manifest is incomplete"
if cmp -s "$fixture_dir/run-1.sha256" "$fixture_dir/run-2.sha256"; then
  fail "independent screenshot manifests unexpectedly match"
fi

rg -q 'ralph_validate_slice_runtime_requirements "\$slice_file"' scripts/ralph-validate.sh \
  || fail "independent validation does not enforce runtime requirement preflight"
rg -q 'ralph_trusted_postgresql_test_labels "\$slice_file"' scripts/ralph-validate.sh \
  || fail "PostgreSQL validation does not consume the slice-owned labels"
if rg -q 'LoanLimitConcurrencyTests|AppraisalConcurrencyTests|SanctionSubmissionConcurrencyTests' \
    scripts/ralph-validate.sh; then
  fail "PostgreSQL validation still contains the legacy hard-coded test labels"
fi
rg -q 'evidence/screenshots/run-\$\{ordinal\}' scripts/ralph-validate.sh \
  || fail "browser repetitions do not use ordinal-isolated screenshot directories"
rg -q 'trusted-browser-screenshots-\$\{ordinal\}\.sha256' scripts/ralph-validate.sh \
  || fail "browser repetitions do not retain ordinal-isolated manifests"

echo "PASS: Ralph acceptance contracts fail closed and retain independent evidence."
