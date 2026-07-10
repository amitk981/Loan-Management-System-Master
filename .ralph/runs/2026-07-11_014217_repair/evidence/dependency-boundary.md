# Dependency Boundary Evidence

The static regression resolves the module from the test file's backend-package root, parses
`credit/modules/appraisal_workflow.py` with Python AST across both `import` and `from ... import`
forms, and proves:

- forbidden import absent: `sfpcl_credit.approvals.models`
- required public import present: `sfpcl_credit.approvals.modules.sanction_handoff`

This repairs the prior run's repository-root-relative test path while keeping the signal
red-capable: `terminal-logs/red-static-dependency.txt` fails on the original concrete import and
`terminal-logs/green-sanction-module.txt` passes after extraction.

Runtime direction is `credit -> approvals public interface`; concrete approval persistence,
unique-case lookup, reload lookup, and serialization remain inside the approvals package.
