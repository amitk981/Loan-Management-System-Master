# Closure Contract Matrix

| Surface / role | Server-owned gate | Frontend behavior | Evidence |
|---|---|---|---|
| Closure readiness / scoped staff reader | `closure.readiness.read`; `ready_for_closure`; named `checks[]` | Loads the scoped loan list and readiness projection; renders every named pass/fail check and disables financial close while readiness is false. | `LoanClosureHub.test.tsx`: blocker and state cases; `closure-frontend-review-green-final.log` |
| Financial close / Credit Manager | `closure.loan.close`; readiness is true | Requires notes, sends an idempotent close action, then refetches readiness and downstream canonical reads. No balance or readiness decision is calculated in the browser. | Close/action/refetch test; `recoveryApi.test.ts` |
| NOC / Company Secretary or scoped Compliance staff | `closure.noc.issue` permission and canonical `available_actions` | Remains locked without the backend-created closure identity; after issue, refetches and renders the canonical NOC projection. | NOC action/refetch test |
| Security return / Company Secretary or scoped Compliance staff | `closure.security_return.record` permission and canonical `available_actions` | Uses structured package, version, item, outcome, recipient/time, and CDSL evidence fields. Renders the canonical POST projection because 011I exposes no GET route. | Security action/render test; known read-seam gap below |
| Archive / Company Secretary or scoped Compliance staff | `closure.archive.create` permission and canonical `available_actions` | Does not reconstruct NOC/security prerequisites locally. Sends the archive action only when the backend exposes it, then refetches the archive projection and renders server retention dates. | Security/archive test |
| Auditor and sessions without mutation permissions | Permission catalogue; no mutation action | Mutation controls are not rendered unless the matching permission and resource action are both present. Existing Epic 011 auditor/navigation consumers remain green. | `epic-011-reverse-consumers-final.log` |
| All S58-S61 surfaces | Canonical API projections | Loading, empty, error, unauthorized, validation, blocked, and success states use existing alert/card/field/badge patterns. | Closure page focused tests; full frontend suite |
| Mock-removal ratchet | No production fixture authority | `LoanClosureHub.tsx` has no `mockData` import, inline closure loan list, or named prototype borrower fixtures. | Mock-removal source regression in `LoanClosureHub.test.tsx`; final `rg` scan |

## Known API read-seam gaps

- The delivered 011G-011J staff API has no normal staff closure collection/detail read that maps a
  selected loan account to an existing `loan_closure_id`. A closed workflow therefore cannot be
  rehydrated after a page reload; the frontend can load downstream projections only after the
  current session receives the close action response.
- The delivered 011I API has only
  `POST /api/v1/loan-closures/{loan_closure_id}/security-return/`; it has no canonical GET. The
  screen truthfully renders the POST response but cannot refetch the security-return aggregate.
- The closure serializer currently exposes `closure.archive.create` whenever the archive
  requirement itself is pending, including while NOC/security remain pending. The archive write
  rejects this on the server, but the projected action is not a truthful UI eligibility signal and
  cannot be refreshed because the staff closure read seam is absent.
- Closing either gap requires backend contract, permission, and TDD work outside the prepared
  frontend-only 011PC boundary. Independent validation should decide the corrective slice rather
  than widening this candidate.
