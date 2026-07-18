"""Executable ownership guard for legal-document migration state."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any

from django.db.migrations import Migration
from django.db.migrations.loader import MigrationLoader
from django.db.migrations.operations.base import Operation
from django.db.migrations.state import ProjectState
from django.db.migrations.writer import MigrationWriter


_CHECKLIST_KEY = ("legal_documents", "documentchecklist")


@dataclass(frozen=True)
class _RetainedOperation:
    path: str
    module: str
    class_name: str
    transitions: Mapping[int, tuple[str, str]]


_HISTORICAL_PATH = (
    "disbursements/migrations/"
    "0005_disbursementadviceintent_loanregisterupdate_and_more.py"
)
_HISTORICAL_MODULE = (
    "sfpcl_credit.disbursements.migrations."
    "0005_disbursementadviceintent_loanregisterupdate_and_more"
)
_RETAINED_OPERATIONS = (
    _RetainedOperation(
        path=_HISTORICAL_PATH,
        module=_HISTORICAL_MODULE,
        class_name="RemoveLegalChecklistConstraint",
        transitions=MappingProxyType(
            {
                0: ("remove", "checklist_account_requires_epic_009"),
                1: ("remove", "checklist_finance_requires_epic_009"),
            }
        ),
    ),
    _RetainedOperation(
        path=_HISTORICAL_PATH,
        module=_HISTORICAL_MODULE,
        class_name="AddLegalChecklistConstraint",
        transitions=MappingProxyType(
            {
                2: ("add", "checklist_finance_requires_sanction"),
                3: ("add", "checklist_ready_evidence_complete"),
            }
        ),
    ),
)
_RETAINED_CONSTRAINT_FINGERPRINTS = MappingProxyType(
    {
        "checklist_account_requires_epic_009": (
            "models.CheckConstraint(check=models.Q((\'loan_account_id__isnull\', True)), "
            "name=\'checklist_account_requires_epic_009\')"
        ),
        "checklist_finance_requires_epic_009": (
            "models.CheckConstraint(check=models.Q("
            "(\'senior_manager_finance_signature_id__isnull\', True)), "
            "name=\'checklist_finance_requires_epic_009\')"
        ),
        "checklist_finance_requires_sanction": (
            "models.CheckConstraint(check=models.Q("
            "(\'senior_manager_finance_signature_id__isnull\', True), "
            "(\'sanction_committee_signature_id__isnull\', False), "
            "_connector=\'OR\'), name=\'checklist_finance_requires_sanction\')"
        ),
        "checklist_ready_evidence_complete": (
            "models.CheckConstraint(check=models.Q(models.Q("
            "(\'checklist_status\', \'ready\'), "
            "(\'loan_account_id__isnull\', False), "
            "(\'senior_manager_finance_signature_id__isnull\', False)), "
            "models.Q(models.Q((\'checklist_status\', \'ready\'), _negated=True), "
            "(\'loan_account_id__isnull\', True), "
            "(\'senior_manager_finance_signature_id__isnull\', True)), "
            "_connector=\'OR\'), name=\'checklist_ready_evidence_complete\')"
        ),
    }
)

LEGAL_CHECKLIST_STATE_ALLOWLIST = frozenset(
    f"{item.path}:{item.class_name}" for item in _RETAINED_OPERATIONS
)


def legal_checklist_state_ownership_violations(
    *,
    package_root: Path | None = None,
    sources: Mapping[Path, str] | None = None,
    operations: Mapping[Path, Sequence[Operation]] | None = None,
) -> list[str]:
    """Return non-legal operations that change checklist project state.

    Repository checks use Django's loaded migration graph. ``sources`` and
    ``operations`` are test adapters for synthetic migration modules; both run
    the same state-transition comparison as the repository check.
    """

    supplied = sum(value is not None for value in (package_root, sources, operations))
    if supplied != 1:
        raise ValueError("Provide exactly one migration source.")

    if package_root is not None:
        candidates = _repository_operations(package_root)
    else:
        loader = MigrationLoader(None)
        baseline = loader.project_state()
        if sources is not None:
            candidates = _source_operations(sources, baseline)
        else:
            candidates = [
                (path, list(items), baseline.clone())
                for path, items in sorted(
                    operations.items(), key=lambda item: str(item[0])
                )
            ]

    violations: list[str] = []
    for path, migration_operations, state in candidates:
        normalized = path.as_posix()
        owner_app = normalized.split("/", 1)[0]
        for index, operation in enumerate(migration_operations):
            before, changed_models = _apply_operation_state(
                owner_app=owner_app, state=state, operation=operation
            )
            if _CHECKLIST_KEY not in changed_models or owner_app == "legal_documents":
                continue
            identity = f"{normalized}:{operation.__class__.__name__}"
            if not _is_retained_transition(
                path=normalized,
                operation=operation,
                index=index,
                before=before,
                after=state,
                changed_models=changed_models,
            ):
                violations.append(identity)
    return violations


def _apply_operation_state(
    *, owner_app: str, state: ProjectState, operation: Operation
) -> tuple[ProjectState, set[tuple[str, str]]]:
    before = deepcopy(state)
    operation.state_forwards(owner_app, state)
    return before, _changed_models(before, state)


def _repository_operations(
    package_root: Path,
) -> list[tuple[Path, list[Operation], ProjectState]]:
    loader = MigrationLoader(None)
    candidates = []
    for _key, migration in sorted(loader.disk_migrations.items()):
        module_path = Path(migration.__module__.replace(".", "/") + ".py")
        try:
            relative_path = module_path.relative_to("sfpcl_credit")
        except ValueError:
            continue
        if not (package_root / relative_path).is_file():
            continue
        state = loader.project_state(migration.dependencies)
        candidates.append((relative_path, list(migration.operations), state))
    return candidates


def _source_operations(
    sources: Mapping[Path, str], baseline: ProjectState
) -> list[tuple[Path, list[Operation], ProjectState]]:
    candidates = []
    for number, (path, source) in enumerate(
        sorted(sources.items(), key=lambda item: str(item[0]))
    ):
        normalized = path.as_posix()
        namespace: dict[str, Any] = {
            "__name__": f"_migration_guard_probe_{number}",
            "__file__": normalized,
        }
        exec(compile(source, normalized, "exec"), namespace)
        migration_classes = [
            value
            for value in namespace.values()
            if isinstance(value, type)
            and issubclass(value, Migration)
            and value is not Migration
            and value.__module__ == namespace["__name__"]
        ]
        if migration_classes:
            migration = migration_classes[0](
                path.stem, normalized.split("/", 1)[0]
            )
            items = list(migration.operations)
        else:
            items = [
                value()
                for value in namespace.values()
                if isinstance(value, type)
                and issubclass(value, Operation)
                and value is not Operation
                and value.__module__ == namespace["__name__"]
            ]
        candidates.append((path, items, baseline.clone()))
    return candidates


def _changed_models(before: ProjectState, after: ProjectState) -> set[tuple[str, str]]:
    keys = set(before.models) | set(after.models)
    return {
        key
        for key in keys
        if _model_state_value(before.models.get(key))
        != _model_state_value(after.models.get(key))
    }


def _model_state_value(model_state):
    if model_state is None:
        return None
    return (
        model_state.app_label,
        model_state.name,
        model_state.fields,
        model_state.options,
        model_state.bases,
        model_state.managers,
    )


def _constraint_names(state: ProjectState) -> set[str]:
    model_state = state.models[_CHECKLIST_KEY]
    return {
        constraint.name
        for constraint in model_state.options.get("constraints", ())
    }


def _checklist_fingerprint(
    state: ProjectState, *, omit_constraint: str | None = None
) -> str:
    model_state = state.models[_CHECKLIST_KEY].clone()
    if omit_constraint is not None:
        model_state.options["constraints"] = [
            constraint
            for constraint in model_state.options.get("constraints", ())
            if constraint.name != omit_constraint
        ]
    return MigrationWriter.serialize(_model_state_value(model_state))[0]


def _constraint_fingerprint(state: ProjectState, name: str) -> str | None:
    matching = [
        constraint
        for constraint in state.models[_CHECKLIST_KEY].options.get("constraints", ())
        if constraint.name == name
    ]
    if len(matching) != 1:
        return None
    return MigrationWriter.serialize(matching[0])[0]


def _is_retained_transition(
    *,
    path: str,
    operation: Operation,
    index: int,
    before: ProjectState,
    after: ProjectState,
    changed_models: set[tuple[str, str]],
) -> bool:
    if changed_models != {_CHECKLIST_KEY}:
        return False
    matching = next(
        (
            item
            for item in _RETAINED_OPERATIONS
            if item.path == path
            and item.module == operation.__class__.__module__
            and item.class_name == operation.__class__.__name__
        ),
        None,
    )
    if matching is None or index not in matching.transitions:
        return False
    action, constraint_name = matching.transitions[index]
    before_names = _constraint_names(before)
    after_names = _constraint_names(after)
    if action == "remove":
        return (
            before_names - after_names == {constraint_name}
            and not (after_names - before_names)
            and _constraint_fingerprint(before, constraint_name)
            == _RETAINED_CONSTRAINT_FINGERPRINTS[constraint_name]
            and _checklist_fingerprint(
                before, omit_constraint=constraint_name
            )
            == _checklist_fingerprint(after)
        )
    return (
        after_names - before_names == {constraint_name}
        and not (before_names - after_names)
        and _constraint_fingerprint(after, constraint_name)
        == _RETAINED_CONSTRAINT_FINGERPRINTS[constraint_name]
        and _checklist_fingerprint(before)
        == _checklist_fingerprint(after, omit_constraint=constraint_name)
    )
