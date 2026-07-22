"""Executable architecture-review checks for inherited closure-test quality."""

from __future__ import annotations

import argparse
import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
TEST_PATH = ROOT / "sfpcl_credit/tests/test_epic010_terminal_owner_finalizer.py"


def method_source(tree: ast.Module, class_name: str, method_name: str, source: str) -> str:
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) and child.name == method_name:
                    return ast.get_source_segment(source, child) or ""
    raise AssertionError(f"FAIL: permanent test {class_name}.{method_name} is missing")


def check_mis(tree: ast.Module, source: str) -> None:
    class_name = "Epic010MisOwnerRegressionTests"
    method_name = "test_real_invoice_model_projects_before_on_and_after_cutoff_lifecycle"
    body = method_source(tree, class_name, method_name, source)
    class_node = next(
        node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == class_name
    )
    bases = {ast.unparse(base) for base in class_node.bases}
    assert "SimpleTestCase" not in bases, (
        "FAIL: AC-E10-RR1 uses SimpleTestCase, so it cannot persist invoice lifecycle truth "
        "or generate/replay a public MIS report"
    )
    assert "_invoice_status_at_cutoff" not in body, (
        "FAIL: AC-E10-RR1 calls the private cutoff helper instead of the public MIS owner"
    )
    assert "quarterly-mis-reports/generate" in body or ".generate(" in body, (
        "FAIL: AC-E10-RR1 never generates a report through the public MIS owner"
    )
    assert "replay" in body.lower(), "FAIL: AC-E10-RR1 has no exact historical replay assertion"


def check_reminder(tree: ast.Module, source: str) -> None:
    body = method_source(
        tree,
        "Epic010TerminalOwnerFinalizerPostgreSQLAcceptanceTests",
        "test_recipient_source_change_cancels_before_provider",
        source,
    )
    assert "RolePermission.objects.filter" not in body and ".delete()" not in body, (
        "FAIL: AC-E10-RR2 changes recipient source and revokes scope in the same case, "
        "so source-owner cancellation is not isolated"
    )
    assert "CountingAdapter" in body and (
        "adapter.calls" in body or "self.assertEqual(adapter.calls" in body
    ), (
        "FAIL: AC-E10-RR2 source-change case does not assert zero provider effects"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("finding", choices=("mis", "reminder"))
    args = parser.parse_args()
    source = TEST_PATH.read_text()
    tree = ast.parse(source)
    if args.finding == "mis":
        check_mis(tree, source)
    else:
        check_reminder(tree, source)
    print("PASS: inherited closure contract has substantive permanent public-owner coverage")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
