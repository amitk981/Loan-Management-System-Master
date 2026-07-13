# Standards Review

Review window: `git diff b32559c...78d912f`

## Hard violations

1. Exception enrichment stores a distinct business reason while the coherence predicate still
   requires it to equal `reason_for_approval`. The resulting case is saved incoherent, hidden from
   selectors, and unavailable to actions. Existing tests stop at enrichment or manually attach an
   Exception Register row. Corrective owner: 007F2.
2. Sanction-decision and Credit Sanction Register reads check only permission and omit canonical
   case/application object scope. Same-permission unrelated Directors can read or count rows.
   Corrective owner: 007H2.
3. General Meeting recording checks a global document permission and existence only, not related-
   application, sensitivity, category, or workflow access per file. Corrective owner: 007G2.
4. The appraisal post-save signal still mutates approval coherence/read-index rows, contrary to
   007E2's explicit projection seam. Corrective owner: 007F2.

## Test/architecture judgments

- A forced-route test directly calls a private validation helper despite the interface-only test
  rule; 007F2 replaces it with public acceptance.
- Pagination/positive-integer parsing is duplicated across approval register modules. This is a
  locality risk, but the current copies retain one contract and do not justify a standalone slice.
- Payload replay makes General Meeting recording zero-write. Source §45 does not list this endpoint
  among operations requiring an idempotency key, so the missing header is not classified as a defect.

Standards total: 4 material findings (1 Critical, 2 High, 1 Medium architecture). Worst: a valid
exception workflow becomes unreadable/unactionable immediately after enrichment.

