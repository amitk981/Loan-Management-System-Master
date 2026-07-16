# Diagnosis and RED Evidence

## Most recent failure diagnosis

No failure summary existed for this newly created repair run. The newest failed run summary was
`.ralph/runs/2026-07-16_044126_repair/failure-summary.md`; it described an earlier 008M2 diff-limit
failure and did not explain the selected 008M3 defect. No leftover failed worktree existed.

The retained architecture-review probe was therefore the minimal reproduction:

```text
PYTHONPATH=.ralph/runs/2026-07-16_072819_architecture_review/evidence/terminal-logs \
  /Users/amitkallapa/LMS/.ralph/venv/bin/python manage.py test \
  review_action_parity_probe.ReviewActionParityProbe.test_advertised_completion_is_not_executable \
  --verbosity 2
```

Observed defect (probe passed because it asserted the known disagreement):

```text
advertised_action='complete_item'
advertised_enabled=True
execution_status=409
execution_error='CHECKLIST_EVIDENCE_INCOMPLETE'
```

Root cause: workspace projection used shallow actor/item predicates while execution delegated to an
owner that checked terminal signature, stamp/notary, current-document, and other evidence. The two
paths did not share a decision/command contract.

## Failing-first regressions

Focused backend tests were added before implementation. Three failed as expected:

```text
complete_item was unexpectedly advertised while owner evidence was incomplete
opaque completion request returned 400 because the old boundary required loan_document_id
upload/correction actions were absent from the workspace contract
```

Focused frontend tests also failed before implementation:

```text
Document Pack rendered only available_actions[0]
upload submitted an input fakepath string instead of the selected File
```
