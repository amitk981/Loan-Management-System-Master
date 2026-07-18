"""Static guardrails for migration-state ownership boundaries."""

from __future__ import annotations

import ast
from collections.abc import Mapping
from pathlib import Path


LEGAL_CHECKLIST_STATE_ALLOWLIST = {
    (
        "disbursements/migrations/"
        "0005_disbursementadviceintent_loanregisterupdate_and_more.py:"
        "AddLegalChecklistConstraint"
    ),
    (
        "disbursements/migrations/"
        "0005_disbursementadviceintent_loanregisterupdate_and_more.py:"
        "RemoveLegalChecklistConstraint"
    ),
}


def legal_checklist_state_ownership_violations(
    *,
    package_root: Path | None = None,
    sources: Mapping[Path, str] | None = None,
) -> list[str]:
    """Return non-legal custom operations that mutate checklist model state.

    The historical disbursements 0005 operations are retained because applied
    migration history must not be rewritten. New checklist state changes must
    be declared by a migration in the legal_documents app.
    """

    if (package_root is None) == (sources is None):
        raise ValueError("Provide exactly one of package_root or sources.")
    if sources is None:
        sources = {
            path.relative_to(package_root): path.read_text()
            for path in package_root.glob("*/migrations/[0-9]*.py")
        }

    violations: list[str] = []
    for path, source in sorted(sources.items(), key=lambda item: str(item[0])):
        normalized = path.as_posix()
        owner_app = normalized.split("/", 1)[0]
        if owner_app == "legal_documents":
            continue
        tree = ast.parse(source, filename=normalized)
        for node in tree.body:
            if not isinstance(node, ast.ClassDef):
                continue
            if not _is_custom_migration_operation(node):
                continue
            if not _class_targets_legal_checklist(node):
                continue
            identity = f"{normalized}:{node.name}"
            if identity not in LEGAL_CHECKLIST_STATE_ALLOWLIST:
                violations.append(identity)
    return violations


def _is_custom_migration_operation(node: ast.ClassDef) -> bool:
    return any(
        isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
        and child.name == "state_forwards"
        for child in node.body
    )


def _class_targets_legal_checklist(node: ast.ClassDef) -> bool:
    constants = {
        child.value
        for child in ast.walk(node)
        if isinstance(child, ast.Constant) and isinstance(child.value, str)
    }
    return {
        "legal_documents",
        "documentchecklist",
    }.issubset(constants)
