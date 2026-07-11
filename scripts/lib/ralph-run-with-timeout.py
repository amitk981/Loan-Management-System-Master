#!/usr/bin/env python3
"""Run an unattended command with closed stdin and a process-group timeout."""

from __future__ import annotations

import argparse
import os
import signal
import subprocess
import sys


TIMEOUT_EXIT_CODE = 124


class ForwardSignal(Exception):
    def __init__(self, signum: int) -> None:
        self.signum = signum


def terminate_process_group(
    process: subprocess.Popen[bytes], grace_seconds: int
) -> None:
    if process.poll() is not None:
        return
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        process.wait(timeout=grace_seconds)
        return
    except subprocess.TimeoutExpired:
        pass
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        return
    process.wait()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout", type=int, required=True)
    parser.add_argument("--grace", type=int, default=10)
    parser.add_argument("--label", default="command")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()

    command = args.command
    if command[:1] == ["--"]:
        command = command[1:]
    if not command:
        parser.error("a command is required after --")
    if args.timeout <= 0:
        parser.error("--timeout must be a positive number of seconds")
    if args.grace <= 0:
        parser.error("--grace must be a positive number of seconds")

    def forward_signal(signum: int, _frame: object) -> None:
        raise ForwardSignal(signum)

    signal.signal(signal.SIGINT, forward_signal)
    signal.signal(signal.SIGTERM, forward_signal)

    process = subprocess.Popen(
        command,
        stdin=subprocess.DEVNULL,
        start_new_session=True,
    )
    try:
        return process.wait(timeout=args.timeout)
    except subprocess.TimeoutExpired:
        print(
            f"ERROR: {args.label} timed out after {args.timeout} seconds; "
            "terminating its process group.",
            file=sys.stderr,
            flush=True,
        )
        terminate_process_group(process, args.grace)
        return TIMEOUT_EXIT_CODE
    except ForwardSignal as forwarded:
        print(
            f"WARN: {args.label} received signal {forwarded.signum}; "
            "terminating its process group.",
            file=sys.stderr,
            flush=True,
        )
        terminate_process_group(process, args.grace)
        return 128 + forwarded.signum


if __name__ == "__main__":
    raise SystemExit(main())
