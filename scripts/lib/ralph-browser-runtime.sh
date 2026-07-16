#!/usr/bin/env bash

# Ensure the central Playwright browser selection can launch a page. One failed
# probe receives exactly one bounded Playwright Chromium installation attempt;
# a second failure is an infrastructure stop, never a product repair signal.
ralph_ensure_browser_runtime() {
  local project_dir="${1:?frontend project directory is required}"
  local evidence_log="${2:?browser evidence log is required}"
  local watchdog="${3:?watchdog path is required}"
  local recovery_timeout="${4:-300}"

  mkdir -p "$(dirname "$evidence_log")"
  {
    echo "# Browser Infrastructure Probe"
    echo
    echo "Project: $project_dir"
    echo "Probe: npm run e2e:probe"
    echo

    if (cd "$project_dir" && npm run e2e:probe); then
      echo
      echo "PASS: the centrally selected browser launched successfully."
      return 0
    fi

    echo
    echo "RECOVERY: initial browser launch failed; installing Playwright Chromium once."
    if ! (
      cd "$project_dir"
      python3 "$watchdog" \
        --timeout "$recovery_timeout" \
        --label "Playwright Chromium infrastructure recovery" \
        -- npx playwright install chromium
    ); then
      echo "FAIL: Playwright Chromium infrastructure recovery did not complete."
      return 1
    fi

    if (cd "$project_dir" && npm run e2e:probe); then
      echo
      echo "PASS: browser launch succeeded after one infrastructure recovery."
      return 0
    fi

    echo
    echo "FAIL: browser launch still fails after one infrastructure recovery."
    return 1
  } > "$evidence_log" 2>&1
}
