# Review authority matrix

Verified by
`AppraisalApiTests.test_review_enforces_independent_permission_object_scope_and_maker_checker` in
`evidence/terminal-logs/04-review-authority-green.txt`.

| Actor facts | Expected result | Writes |
|---|---|---|
| In-scope application receiver; has `credit.appraisal.review`; role is not `credit_manager` | `403 PERMISSION_DENIED` | None |
| Appraisal preparer; temporarily has review permission; role is not `credit_manager` | `403 PERMISSION_DENIED` | None |
| Non-Credit-Manager outsider; has review permission | `403 PERMISSION_DENIED` | None |
| Active `credit_manager`; has review permission; application outside credit-assessment domain | `403 OBJECT_ACCESS_DENIED` | None |
| Active `credit_manager`; has review permission; application inside credit-assessment domain; not maker | `200`, rejection succeeds | Exactly one history row, one rejection note, and matching evidence |

For every denied row, the test asserts zero review-decision rows, zero rejection notes, no review
audit, and no additional appraisal workflow event.
