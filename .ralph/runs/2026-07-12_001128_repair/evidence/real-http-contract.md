# Real Epic 006 HTTP Contract

The focused backend test and second Playwright test share the guarded deterministic fixture:

- Finance: `e2e.credit.finance@sfpcl.example`
- Manager: `e2e.credit.manager@sfpcl.example`
- Application: `00000000-0000-4000-8000-000000000601` / `LOE2E00601`

The path runs eligibility, limit, appraisal create/PATCH/submit, independent review, sanction
submission, reload, and one repeat `409`. The browser asserts each exact resource action, writable
PATCH allowlist, four-read success refresh, no conflict refresh, and shared server IDs. The focused
backend log `terminal-logs/backend-seed-http-green.log` additionally proves one-case audit/workflow
cardinality and that borrower, risk, review, and sanction free text never enters audit JSON.
