# Repair Diagnosis

## Demonstrated failures

- The authoritative backend coverage run produced six errors across the credit-owner, SAP-owner,
  and witness historical migration tests.
- Frontend typecheck compiled the Node-only Playwright browser resolver through its `src` unit test
  and lacked declarations for `node:fs` and `process`.

## Root cause

`sap_workflow.0001_sap_model_owner_state` adds a new leaf whose dependency reaches the current
`loans`, Finance, approval, and application state. Two older migration tests projected historical
models from all graph leaves except their previously known downstream owners. Including the new SAP
leaf therefore produced current model state against intentionally reversed physical schemas. That
made the credit test lose its pre-transfer application-owned assessment models and made the witness
test try to insert post-0012 fields into a pre-0012 table. A failed setup then left the shared test
schema reversed, which caused the following SAP test's missing-table error.

The SAP transfer operation was not defective: its isolated forward/reverse preservation test passed
before the repair. The fix extends the two historical-test descendant exclusions to the new SAP leaf,
making their intended historical state explicit and restoring teardown/order safety.

The frontend failure was independent and pre-existing. The resolver already ran only in Node and
already tested exactly the same resolution behavior. The repair supplies a narrow `node:fs`
declaration and uses an optional typed `globalThis.process` view, without adding a dependency or
changing runtime resolution.

## Regression signal

The exact nine-test combined migration command moved from six errors to nine passes. The 101-test
SAP/account/readiness run, two PostgreSQL race runs, frontend focused test/typecheck/lint/build,
Django check, migration sync, and state-only SQL proof all pass.
