#!/usr/bin/env python3
"""
Ralph / Codex context-occupancy trip-wire (read-only, advisory).

Maps each Ralph run to its Codex session rollout and reports the run's PEAK
per-call context (max last_token_usage.input_tokens) as a share of the model
context window. Peak occupancy -- not the cache-inflated cumulative "tokens
used" -- is the real signal for auto-compaction risk.

Read-only: touches no protected files, only run logs and ~/.codex rollouts.
Exit 1 if any analysed run is at/over --threshold (so it can drive a monitor),
else 0. Runs with no Codex telemetry (e.g. claude-driven) are skipped.

Usage:
  scripts/ralph-context-tripwire.py [--threshold 0.85] [--watch 0.70]
                                    [--last N] [--runs-dir DIR]
                                    [--agent-logs-dir DIR] [--json]
"""
import argparse
import glob
import json
import os
import re
import subprocess
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_RUNS = os.path.join(REPO_ROOT, ".ralph/runs")
SESS_DIRS = [os.path.expanduser("~/.codex/sessions"),
             os.path.expanduser("~/.codex/archived_sessions")]
UUID = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"


def default_agent_logs():
    try:
        common = subprocess.check_output(
            [
                "git",
                "-C",
                REPO_ROOT,
                "rev-parse",
                "--path-format=absolute",
                "--git-common-dir",
            ],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        common = os.path.join(REPO_ROOT, ".git")
    return os.path.join(common, "ralph-agent-logs")


def index_rollouts():
    idx = {}
    for base in SESS_DIRS:
        for p in glob.glob(os.path.join(base, "**", "rollout-*.jsonl"), recursive=True):
            m = re.search(UUID, os.path.basename(p))
            if m:
                idx[m.group(0)] = p
    return idx


def session_id_of(run_dir, agent_logs_dir):
    run_id = os.path.basename(run_dir)
    candidates = (
        os.path.join(agent_logs_dir, run_id, "codex.log"),
        os.path.join(run_dir, "evidence/terminal-logs/codex-summary.md"),
        os.path.join(run_dir, "evidence/terminal-logs/codex.log"),
    )
    for log in candidates:
        if not os.path.exists(log):
            continue
        with open(log, errors="ignore") as stream:
            for line in stream:
                m = re.search(r"session id:\s*(" + UUID + ")", line, re.I)
                if m:
                    return m.group(1)
    return None


def peak_occupancy(rollout_path):
    peak, window = 0, None
    for line in open(rollout_path, errors="ignore"):
        if '"token_count"' not in line:
            continue
        try:
            info = json.loads(line)["payload"]["info"]
        except Exception:
            continue
        window = info.get("model_context_window", window)
        peak = max(peak, info.get("last_token_usage", {}).get("input_tokens", 0))
    return peak, window


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--threshold", type=float, default=0.85, help="fail band (fraction of window)")
    ap.add_argument("--watch", type=float, default=0.70, help="warn band (fraction of window)")
    ap.add_argument("--last", type=int, default=0, help="only the last N runs (0 = all)")
    ap.add_argument("--runs-dir", default=DEFAULT_RUNS)
    ap.add_argument("--agent-logs-dir", default=default_agent_logs())
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    rolls = index_rollouts()
    run_dirs = sorted(glob.glob(os.path.join(a.runs_dir, "2026-*")))
    if a.last:
        run_dirs = run_dirs[-a.last:]

    results, breaches, watches, skipped = [], [], [], []
    for d in run_dirs:
        rid = os.path.basename(d)
        sid = session_id_of(d, a.agent_logs_dir)
        if not sid or sid not in rolls:
            skipped.append(rid)
            continue
        peak, window = peak_occupancy(rolls[sid])
        if not window:
            skipped.append(rid)
            continue
        pct = peak / window
        row = dict(run_id=rid, peak=peak, window=window, pct=round(pct, 4))
        results.append(row)
        if pct >= a.threshold:
            breaches.append(row)
        elif pct >= a.watch:
            watches.append(row)

    if a.json:
        print(json.dumps(dict(threshold=a.threshold, watch=a.watch, analysed=len(results),
                              skipped=skipped, breaches=breaches, watches=watches, all=results), indent=1))
    else:
        print(f"Context trip-wire  |  fail>= {a.threshold:.0%}  watch>= {a.watch:.0%}  |  "
              f"{len(results)} codex run(s) analysed, {len(skipped)} skipped (no telemetry)")
        for r in sorted(results, key=lambda r: r["pct"], reverse=True):
            tag = "BREACH" if r["pct"] >= a.threshold else ("watch " if r["pct"] >= a.watch else "  ok  ")
            print(f"  [{tag}] {r['run_id']:42} peak {r['peak']:>7,} / {r['window']:,}  = {r['pct']:.0%}")
        if breaches:
            print(f"\nFAIL: {len(breaches)} run(s) >= {a.threshold:.0%} of window -- consider splitting the slice(s).")
        elif watches:
            print(f"\nOK (no breach). {len(watches)} run(s) in the watch band -- monitor scope.")
        else:
            print("\nOK. All analysed runs below the watch band.")

    sys.exit(1 if breaches else 0)


if __name__ == "__main__":
    main()
