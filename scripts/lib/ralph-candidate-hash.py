#!/usr/bin/env python3
"""Hash the complete non-Ralph candidate diff, including untracked files."""

import argparse
import hashlib
import os
import subprocess
from pathlib import Path


def git(root: Path, *args: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(root), *args])


def candidate_hash(
    root: Path,
    *,
    target: str | None = None,
    excludes: tuple[str, ...] = (),
) -> str:
    digest = hashlib.sha256()
    digest.update(b"ralph-candidate-v2\0")
    for excluded in sorted(excludes):
        digest.update(b"exclude\0")
        digest.update(excluded.encode("utf-8", errors="surrogateescape"))
        digest.update(b"\0")

    def is_excluded(relative: str) -> bool:
        if relative == ".ralph" or relative.startswith(".ralph/"):
            return True
        return any(
            relative == excluded
            or relative.startswith(excluded.rstrip("/") + "/")
            for excluded in excludes
        )

    entries: list[tuple[bytes, bytes, bytes]] = []
    if target is None:
        raw_paths = git(
            root,
            "ls-files",
            "--cached",
            "--others",
            "--exclude-standard",
            "-z",
        )
        for raw_path in filter(None, raw_paths.split(b"\0")):
            relative = raw_path.decode("utf-8", errors="surrogateescape")
            if is_excluded(relative):
                continue
            path = root / relative
            if path.is_symlink():
                mode = b"120000"
                content = os.fsencode(os.readlink(path))
            elif path.is_file():
                mode = b"100755" if path.stat().st_mode & 0o111 else b"100644"
                content = path.read_bytes()
            else:
                # Deleted tracked paths are absent from the candidate snapshot.
                continue
            blob = hashlib.sha1(
                b"blob " + str(len(content)).encode() + b"\0" + content
            ).hexdigest().encode()
            entries.append((raw_path, mode, blob))
    else:
        for record in filter(None, git(root, "ls-tree", "-rz", target).split(b"\0")):
            metadata, raw_path = record.split(b"\t", 1)
            mode, _kind, object_id = metadata.split(b" ", 2)
            relative = raw_path.decode("utf-8", errors="surrogateescape")
            if not is_excluded(relative):
                entries.append((raw_path, mode, object_id))

    for raw_path, mode, object_id in sorted(entries):
        digest.update(raw_path)
        digest.update(b"\0")
        digest.update(mode)
        digest.update(b"\0")
        digest.update(object_id)
        digest.update(b"\0")
    return digest.hexdigest()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("worktree")
    parser.add_argument("--target")
    parser.add_argument("--exclude", action="append", default=[])
    args = parser.parse_args()
    print(
        candidate_hash(
            Path(args.worktree).resolve(),
            target=args.target,
            excludes=tuple(args.exclude),
        )
    )
