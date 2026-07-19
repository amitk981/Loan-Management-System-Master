#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$repo_root"

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

unexpected_error() {
  local rc=$?
  echo "FAIL: unexpected command exited $rc at line ${BASH_LINENO[0]}: $BASH_COMMAND" >&2
  exit "$rc"
}
trap unexpected_error ERR

[[ -f scripts/lib/ralph-exit-protocol.sh ]] || fail "missing Ralph exit protocol"
# shellcheck source=../lib/ralph-exit-protocol.sh
source scripts/lib/ralph-exit-protocol.sh
[[ -f scripts/lib/ralph-slice-selection.sh ]] || fail "missing slice-selection helpers"
# shellcheck source=../lib/ralph-slice-selection.sh
source scripts/lib/ralph-slice-selection.sh
[[ -f scripts/lib/ralph-worktree-ownership.sh ]] || fail "missing stable worktree-ownership helpers"
# shellcheck source=../lib/ralph-worktree-ownership.sh
source scripts/lib/ralph-worktree-ownership.sh

fixture_dir="$(mktemp -d)"
trap 'rm -rf "$fixture_dir"' EXIT

make_slice() {
  local directory="$1" filename="$2" status="$3" dependency="$4"
  cat > "$directory/$filename" <<EOF
## Status
$status

## Depends On
- $dependency
EOF
}

# An explicit selector is an exact slice id or filename, never a prefix. It is
# eligible only while Not Started and while all dependencies are drained.
selection_dir="$fixture_dir/selection"
mkdir -p "$selection_dir"
make_slice "$selection_dir" 001A-complete.md Complete None
make_slice "$selection_dir" 001B-ready.md "Not Started" 001A
make_slice "$selection_dir" 001B2-neighbour.md "Not Started" 001A
make_slice "$selection_dir" 001C-finished.md Complete 001A
make_slice "$selection_dir" 001D-unmet.md "Not Started" 099Z
make_slice "$selection_dir" 001E-one.md "Not Started" 001A
make_slice "$selection_dir" 001E-two.md "Not Started" 001A
make_slice "$selection_dir" 001X-one.md Complete 001A
make_slice "$selection_dir" 001X-two.md "Not Started" 001A
make_slice "$selection_dir" 001F-duplicate-dependency.md "Not Started" 001X

resolved="$(ralph_resolve_explicit_slice 001B "$selection_dir" normal_run)" \
  || fail "exact explicit slice id did not resolve"
[[ "$resolved" == "001B-ready.md" ]] \
  || fail "exact selector 001B resolved to the wrong slice: $resolved"
resolved="$(ralph_resolve_explicit_slice 001B-ready.md "$selection_dir" normal_run)" \
  || fail "exact explicit filename did not resolve"
[[ "$resolved" == "001B-ready.md" ]] \
  || fail "exact filename resolved to the wrong slice: $resolved"
if ralph_resolve_explicit_slice 001 "$selection_dir" normal_run >/dev/null 2>&1; then
  fail "prefix selector 001 was accepted"
fi
if ralph_resolve_explicit_slice 001E "$selection_dir" normal_run >/dev/null 2>&1; then
  fail "ambiguous exact slice id was accepted"
fi
if ralph_resolve_explicit_slice 001C "$selection_dir" normal_run >/dev/null 2>&1; then
  fail "completed explicit slice was accepted"
fi
if ralph_resolve_explicit_slice 001D "$selection_dir" normal_run >/dev/null 2>&1; then
  fail "dependency-blocked explicit slice was accepted"
fi
if ralph_resolve_explicit_slice 001F "$selection_dir" normal_run >/dev/null 2>&1; then
  fail "explicit slice accepted an ambiguous dependency id"
fi

# The only exception is a resumable repair context for the same unfinished
# slice. It may resume a parked/unmet candidate, but never Complete/Superseded.
make_slice "$selection_dir" 001R-repair.md Blocked 099Z
ralph_repair_context_is_resumable() { return 0; }
ralph_repair_context_value() {
  [[ "$2" == "slice_id" ]] || return 1
  printf '%s\n' "001R-repair"
}
resolved="$(ralph_resolve_explicit_slice \
  001R "$selection_dir" repair "$fixture_dir/repair-context.json")" \
  || fail "trusted same-slice repair exception was rejected"
[[ "$resolved" == "001R-repair.md" ]] \
  || fail "repair exception resolved to the wrong slice: $resolved"
if ralph_resolve_explicit_slice \
    001C "$selection_dir" repair "$fixture_dir/repair-context.json" >/dev/null 2>&1; then
  fail "repair exception accepted a completed slice"
fi

# A mandatory review gets two bounded attempts, then stops. Product work must
# never run while architecture_review_due remains true.
review_repo="$fixture_dir/review-repo"
mkdir -p "$review_repo/scripts/lib" "$review_repo/.ralph" \
  "$review_repo/docs/slices"
cp scripts/ralph-loop.sh "$review_repo/scripts/ralph-loop.sh"
for loop_lib in ralph-exit-protocol.sh ralph-retry-policy.sh ralph-repair-context.sh \
    ralph-oversized-slice.sh ralph-slice-selection.sh ralph-architecture-review.sh; do
  cp "scripts/lib/$loop_lib" "$review_repo/scripts/lib/$loop_lib"
done
cat > "$review_repo/scripts/ralph-recover.sh" <<'EOF'
#!/usr/bin/env bash
exit 0
EOF
cat > "$review_repo/scripts/afk-dev.sh" <<'EOF'
#!/usr/bin/env bash
printf '%s\n' "$*" >> .ralph/invocations.log
if [[ " $* " == *" --mode architecture-review "* ]]; then
  if [[ -f .ralph/review-exit ]]; then
    exit "$(cat .ralph/review-exit)"
  fi
  [[ -f .ralph/review-succeeds ]] && exit 0
  exit 1
fi
exit 0
EOF
chmod +x "$review_repo/scripts/ralph-loop.sh" \
  "$review_repo/scripts/ralph-recover.sh" "$review_repo/scripts/afk-dev.sh"
cat > "$review_repo/.ralph/config.yaml" <<'EOF'
agent:
  default_tool: codex
  limit_fallback: false
run:
  max_retries: 1
  max_progressive_repairs: 1
EOF
printf '%s\n' '{"architecture_review_due": true}' > "$review_repo/.ralph/state.json"
make_slice "$review_repo/docs/slices" 001A-pending.md "Not Started" None
git init -q "$review_repo"
git -C "$review_repo" add .
git -C "$review_repo" -c user.name='Ralph Regression' \
  -c user.email='ralph-regression@example.invalid' commit -qm fixture
set +e
(
  cd "$review_repo"
  ./scripts/ralph-loop.sh 1 > loop.stdout 2>&1
)
review_rc=$?
set -e
[[ "$review_rc" == "2" ]] \
  || fail "failed mandatory review returned $review_rc instead of stopping with 2"
[[ "$(grep -c -- '--mode architecture-review' "$review_repo/.ralph/invocations.log")" == "2" ]] \
  || fail "mandatory review did not receive exactly two bounded attempts"
if grep -q -- '--mode normal' "$review_repo/.ralph/invocations.log"; then
  fail "product work ran while a mandatory architecture review remained due"
fi
grep -qF 'Mandatory architecture review failed twice. Stopping before product work.' \
  "$review_repo/loop.stdout" \
  || fail "bounded mandatory-review stop did not report its exact outcome"

: > "$review_repo/.ralph/invocations.log"
printf '%s\n' "$RALPH_EXIT_MERGE_FAILED" > "$review_repo/.ralph/review-exit"
set +e
(
  cd "$review_repo"
  ./scripts/ralph-loop.sh 1 > merge-failed-review.stdout 2>&1
)
merge_failed_review_rc=$?
set -e
[[ "$merge_failed_review_rc" == "$RALPH_EXIT_MERGE_FAILED" ]] \
  || fail "quarantined review merge returned $merge_failed_review_rc instead of $RALPH_EXIT_MERGE_FAILED"
[[ "$(grep -c -- '--mode architecture-review' "$review_repo/.ralph/invocations.log")" == "1" ]] \
  || fail "quarantined review merge was retried"
if grep -q -- '--mode normal' "$review_repo/.ralph/invocations.log"; then
  fail "product work ran after a mandatory review merge failure"
fi
grep -qF 'validated review branch is preserved' \
  "$review_repo/merge-failed-review.stdout" \
  || fail "review merge failure did not report preserved quarantine"

: > "$review_repo/.ralph/invocations.log"
rm "$review_repo/.ralph/review-exit"
touch "$review_repo/.ralph/review-succeeds"
set +e
(
  cd "$review_repo"
  ./scripts/ralph-loop.sh 1 > stale-review.stdout 2>&1
)
stale_review_rc=$?
set -e
[[ "$stale_review_rc" == "2" ]] \
  || fail "successful review that left its due flag set returned $stale_review_rc instead of 2"
if grep -q -- '--mode normal' "$review_repo/.ralph/invocations.log"; then
  fail "product work ran after a review that failed to clear its mandatory due flag"
fi
grep -qF 'validated review did not clear architecture_review_due' \
  "$review_repo/stale-review.stdout" \
  || fail "stale mandatory-review state did not report its exact stop reason"

# Worktree ownership remains stable across a repair run id. Recovery skips a
# live repair, then salvages every run that used the dead worktree and clears
# only the repair context belonging to that recovered worktree.
recovery_repo="$fixture_dir/recovery-repo"
git init -q -b staging "$recovery_repo"
git -C "$recovery_repo" config user.name "Ralph Regression"
git -C "$recovery_repo" config user.email "ralph-regression@example.invalid"
mkdir -p "$recovery_repo/scripts/lib" "$recovery_repo/.ralph/worktrees" \
  "$recovery_repo/.ralph/locks"
cp scripts/ralph-recover.sh "$recovery_repo/scripts/ralph-recover.sh"
cp scripts/lib/ralph-worktree-ownership.sh \
  "$recovery_repo/scripts/lib/ralph-worktree-ownership.sh"
cp scripts/lib/ralph-repair-context.sh \
  "$recovery_repo/scripts/lib/ralph-repair-context.sh"
cat > "$recovery_repo/.ralph/config.yaml" <<'EOF'
worktree:
  integration_branch: staging
EOF
printf '%s\n' seed > "$recovery_repo/seed.txt"
git -C "$recovery_repo" add .
git -C "$recovery_repo" commit -qm seed
recovery_worktree="$recovery_repo/.ralph/worktrees/original-run"
git -C "$recovery_repo" worktree add -q -b ralph/original-run_fixture \
  "$recovery_worktree" HEAD
mkdir -p "$recovery_worktree/.ralph/runs/original-run" \
  "$recovery_worktree/.ralph/runs/repair-run"
printf '%s\n' original > "$recovery_worktree/.ralph/runs/original-run/original.txt"
printf '%s\n' repair > "$recovery_worktree/.ralph/runs/repair-run/repair.txt"
cat > "$recovery_worktree/.ralph/runs/original-run/failure-summary.md" <<'EOF'
# Validation Failure Summary

FAIL: fixture failure
EOF
ralph_record_worktree_owner "$recovery_repo" "$recovery_worktree" \
  ralph/original-run_fixture original-run original-run fixture-slice >/dev/null
ralph_record_worktree_owner "$recovery_repo" "$recovery_worktree" \
  ralph/original-run_fixture original-run repair-run fixture-slice >/dev/null
printf 'repair-run\n%s\n%s\n' "$$" "$recovery_worktree" \
  > "$recovery_repo/.ralph/locks/repair-run.lock"
# Restore the real context helpers after the narrow selector stubs above.
# shellcheck source=../lib/ralph-repair-context.sh
source scripts/lib/ralph-repair-context.sh
ralph_write_repair_context \
  "$recovery_repo/.ralph/repair-context.json" original-run "$recovery_worktree" \
  fixture-slice ralph/original-run_fixture \
  "$recovery_worktree/.ralph/runs/original-run/failure-summary.md"

owner_dir="$(ralph_worktree_owner_directory "$recovery_repo")"
mv "$owner_dir/original-run.json" "$owner_dir/owner-a.json"
cp "$owner_dir/owner-a.json" "$owner_dir/owner-b.json"
set +e
(
  cd "$recovery_repo"
  ./scripts/ralph-recover.sh > duplicate-owner.stdout 2>&1
)
duplicate_owner_rc=$?
set -e
[[ "$duplicate_owner_rc" == "1" ]] \
  || fail "duplicate owner metadata returned $duplicate_owner_rc instead of failing closed"
[[ -d "$recovery_worktree" ]] \
  || fail "duplicate owner metadata allowed recovery to remove the worktree"
mv "$owner_dir/owner-a.json" "$owner_dir/original-run.json"
rm "$owner_dir/owner-b.json"

(
  cd "$recovery_repo"
  ./scripts/ralph-recover.sh > live-recovery.stdout
)
[[ -d "$recovery_worktree" ]] \
  || fail "recovery removed a worktree owned by a live repair lock"
[[ -f "$recovery_repo/.ralph/repair-context.json" ]] \
  || fail "recovery cleared the active repair context"

printf 'repair-run\n99999999\n%s\n' "$recovery_worktree" \
  > "$recovery_repo/.ralph/locks/repair-run.lock"
(
  cd "$recovery_repo"
  ./scripts/ralph-recover.sh > dead-recovery.stdout
)
[[ ! -e "$recovery_worktree" ]] \
  || fail "dead repair worktree was not recovered"
[[ -f "$recovery_repo/.ralph/runs/original-run/original.txt" ]] \
  || fail "original run artifacts were not salvaged"
[[ -f "$recovery_repo/.ralph/runs/repair-run/repair.txt" ]] \
  || fail "repair run artifacts were not salvaged"
[[ ! -f "$recovery_repo/.ralph/repair-context.json" ]] \
  || fail "matching dead repair context was not cleared"

printf '%s\n' '{"version":1,"run_id":"malformed"}' \
  > "$recovery_repo/.ralph/repair-context.json"
set +e
(
  cd "$recovery_repo"
  ./scripts/ralph-recover.sh > malformed-context.stdout 2>&1
)
malformed_context_rc=$?
set -e
[[ "$malformed_context_rc" == "1" ]] \
  || fail "malformed repair context returned $malformed_context_rc instead of failing closed"
[[ -f "$recovery_repo/.ralph/repair-context.json" ]] \
  || fail "recovery cleared a malformed repair context"
rm "$recovery_repo/.ralph/repair-context.json"

# A crash can occur after `git worktree add` but before the stable owner record
# is written. The pre-existing trusted root lock, exact registered branch, and
# queued slice identity narrowly authenticate that bootstrap state so recovery
# can clean it instead of stopping every future loop.
mkdir -p "$recovery_repo/docs/slices"
cat > "$recovery_repo/docs/slices/bootstrap-slice.md" <<'EOF'
## Status
Not Started

## Depends On
- None
EOF
git -C "$recovery_repo" add docs/slices/bootstrap-slice.md
git -C "$recovery_repo" commit -qm 'add bootstrap slice'
bootstrap_worktree="$recovery_repo/.ralph/worktrees/bootstrap-run"
git -C "$recovery_repo" worktree add -q -b ralph/bootstrap-run_bootstrap-slice \
  "$bootstrap_worktree" HEAD
mkdir -p "$bootstrap_worktree/.ralph/runs/bootstrap-run"
printf '%s\n' bootstrap > "$bootstrap_worktree/.ralph/runs/bootstrap-run/evidence.txt"
printf 'bootstrap-run\n99999999\n%s\n' "$bootstrap_worktree" \
  > "$recovery_repo/.ralph/locks/bootstrap-run.lock"
declare -F ralph_release_run_lock >/dev/null \
  || fail "worktree ownership helper has no catchable-termination lock policy"
trap - ERR
set +e
run_bootstrap_termination_fixture() {
  bash -c '
    set -euo pipefail
    source "$1"
    fixture_repo="$2"
    fixture_lock="$3"
    fixture_worktree="$4"
    termination_cleanup() {
      ralph_release_run_lock \
        "$fixture_repo" "$fixture_lock" "$fixture_worktree" 0 0 >/dev/null
    }
    trap termination_cleanup EXIT
    kill -TERM "$$"
  ' _ "$repo_root/scripts/lib/ralph-worktree-ownership.sh" \
    "$recovery_repo" "$recovery_repo/.ralph/locks/bootstrap-run.lock" \
    "$bootstrap_worktree"
}
run_bootstrap_termination_fixture >/dev/null 2>&1
bootstrap_term_rc=$?
set -e
trap unexpected_error ERR
[[ "$bootstrap_term_rc" == "143" ]] \
  || fail "bootstrap termination fixture returned $bootstrap_term_rc instead of 143"
[[ -f "$recovery_repo/.ralph/locks/bootstrap-run.lock" ]] \
  || fail "catchable termination deleted the only bootstrap ownership proof"
rg -qF 'ralph_release_run_lock "$repo_root"' scripts/ralph-run.sh \
  || fail "ralph-run EXIT trap does not use the bootstrap-safe lock policy"
(
  cd "$recovery_repo"
  ./scripts/ralph-recover.sh > bootstrap-recovery.stdout
)
[[ ! -e "$bootstrap_worktree" ]] \
  || fail "trusted bootstrap worktree was not recovered"
[[ -f "$recovery_repo/.ralph/runs/bootstrap-run/evidence.txt" ]] \
  || fail "trusted bootstrap artifacts were not salvaged"
[[ ! -f "$recovery_repo/.ralph/locks/bootstrap-run.lock" ]] \
  || fail "trusted bootstrap lock was not cleared"
grep -qF 'Authenticated interrupted bootstrap worktree from its trusted root lock.' \
  "$recovery_repo/bootstrap-recovery.stdout" \
  || fail "bootstrap recovery did not report its narrow authentication path"

legacy_worktree="$recovery_repo/.ralph/worktrees/legacy-run"
git -C "$recovery_repo" worktree add -q -b ralph/legacy-run_fixture \
  "$legacy_worktree" HEAD
mkdir -p "$legacy_worktree/.ralph/runs/legacy-run" \
  "$legacy_worktree/.ralph/runs/legacy-repair"
printf '%s\n' legacy > "$legacy_worktree/.ralph/runs/legacy-run/evidence.txt"
printf '%s\n' repair > "$legacy_worktree/.ralph/runs/legacy-repair/evidence.txt"
set +e
(
  cd "$recovery_repo"
  ./scripts/ralph-recover.sh > legacy-owner.stdout 2>&1
)
legacy_owner_rc=$?
set -e
[[ "$legacy_owner_rc" == "1" ]] \
  || fail "legacy multi-run worktree returned $legacy_owner_rc instead of failing closed"
[[ -f "$legacy_worktree/.ralph/runs/legacy-run/evidence.txt" \
    && -f "$legacy_worktree/.ralph/runs/legacy-repair/evidence.txt" ]] \
  || fail "legacy recovery removed unsalvageable multi-run evidence"

grep -qF "set the review-packet.md Result section to exactly 'Ready for independent validation'" \
  scripts/ralph-run.sh \
  || fail "agent prompt does not declare the exact successful review-packet result"

echo "Ralph control-flow regression checks passed."
