#!/usr/bin/env bash

# Measure candidate additions that are not represented by ordinary diff size:
# package dependencies and new database migration files. Results are exported
# as integers for the fast candidate gate.
ralph_measure_candidate_limits() {
  local worktree_dir="${1:?worktree directory is required}"
  local metrics

  metrics="$(python3 - "$worktree_dir" <<'PY'
import json
import re
import subprocess
import sys
from pathlib import Path

root = Path(sys.argv[1]).resolve()


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(root), *args], text=True, stderr=subprocess.DEVNULL
    )


def head_text(path: str) -> str:
    try:
        return git("show", f"HEAD:{path}")
    except subprocess.CalledProcessError:
        return ""


def current_text(path: str) -> str:
    candidate = root / path
    try:
        return candidate.read_text()
    except (OSError, UnicodeDecodeError):
        return ""


def dependency_manifest(path: str) -> bool:
    candidate = Path(path)
    return candidate.name == "package.json" or (
        candidate.suffix == ".txt"
        and (
            candidate.name.startswith("requirements")
            or candidate.parent.name == "requirements"
        )
    )


def requirement_names(text: str) -> set[str]:
    names: set[str] = set()
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or line.startswith(("-r ", "--requirement ", "-c ", "--constraint ")):
            continue
        editable_target = ""
        for prefix in ("-e ", "--editable ", "--editable="):
            if line.startswith(prefix):
                editable_target = line[len(prefix) :].strip()
                break
        if editable_target:
            names.add("direct:" + editable_target.lower())
            continue
        if line.startswith(("http:", "https:", "git+", "hg+", "svn+", "bzr+", "file:", "./", "../", "/")):
            names.add("direct:" + line.lower())
            continue
        if line.startswith("-"):
            continue
        match = re.match(r"([A-Za-z0-9_.-]+)", line)
        if match:
            names.add(re.sub(r"[-_.]+", "-", match.group(1)).lower())
    return names


def package_names(text: str) -> set[str]:
    try:
        payload = json.loads(text or "{}")
    except json.JSONDecodeError:
        return set()
    names: set[str] = set()
    for key in (
        "dependencies",
        "devDependencies",
        "optionalDependencies",
        "peerDependencies",
    ):
        values = payload.get(key, {})
        if isinstance(values, dict):
            names.update(str(name).lower() for name in values)
    return names


head_paths = set(git("ls-tree", "-r", "--name-only", "HEAD").splitlines())
# Ask Git for candidate files so ignored node_modules, run evidence, coverage
# artifacts, and historical logs are never traversed by this cheap gate.
current_paths = set(
    git("ls-files", "--cached", "--others", "--exclude-standard").splitlines()
)
manifest_paths = {
    path for path in head_paths | current_paths if dependency_manifest(path)
}

before: set[str] = set()
after: set[str] = set()
for path in manifest_paths:
    parser = package_names if Path(path).name == "package.json" else requirement_names
    before.update(parser(head_text(path)))
    after.update(parser(current_text(path)))

changed_paths = set(git("diff", "--name-only", "--no-renames", "HEAD", "--").splitlines())
changed_paths.update(git("ls-files", "--others", "--exclude-standard").splitlines())
new_migrations = 0
for path in changed_paths:
    candidate = Path(path)
    if (
        (root / candidate).is_file()
        and candidate.suffix == ".py"
        and candidate.parent.name == "migrations"
        and re.match(r"^[0-9]", candidate.name)
        and path not in head_paths
    ):
        new_migrations += 1

print(f"{len(after - before)}\t{new_migrations}")
PY
)"
  IFS=$'\t' read -r RALPH_NEW_DEPENDENCY_COUNT RALPH_NEW_MIGRATION_COUNT \
    <<< "$metrics"
  export RALPH_NEW_DEPENDENCY_COUNT RALPH_NEW_MIGRATION_COUNT
}
