#!/usr/bin/env bash

RALPH_UNSAFE_CHANGED_PATH_MARKER="__RALPH_UNSAFE_CHANGED_PATH__"

# Print every candidate path relative to the worktree, one per line. Git emits
# NUL-delimited names and rename detection is disabled so both endpoints remain
# visible. Paths containing control characters cannot be represented safely by
# the line-oriented validators, so they produce a marker that the cheap gate
# rejects instead of being silently misparsed.
ralph_changed_paths() {
  local worktree_dir="${1:?worktree directory is required}"
  python3 - "$worktree_dir" "$RALPH_UNSAFE_CHANGED_PATH_MARKER" <<'PY'
import os
import subprocess
import sys

root, unsafe_marker = sys.argv[1:]


def git_paths(*args: str) -> list[str]:
    output = subprocess.check_output(["git", "-C", root, *args])
    return [os.fsdecode(path) for path in output.split(b"\0") if path]


paths = set(git_paths("diff", "--name-only", "--no-renames", "-z", "HEAD", "--"))
paths.update(git_paths("ls-files", "--others", "--exclude-standard", "-z"))
unsafe = any(any(ord(char) < 32 or ord(char) == 127 for char in path) for path in paths)
if unsafe:
    print(unsafe_marker)
for path in sorted(
    (path for path in paths if not any(ord(char) < 32 or ord(char) == 127 for char in path)),
    key=os.fsencode,
):
    print(path)
PY
}
