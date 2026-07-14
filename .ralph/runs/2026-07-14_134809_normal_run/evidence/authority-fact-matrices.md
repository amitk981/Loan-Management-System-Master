# Authority and Fact Matrices

## Checklist read authority

All decisions below are made by `approvals.modules.document_checklist_access.resolve_read_access`
before a `document_checklists` or `checklist_items` query.

| Actor/fact | Required authority | Result |
|---|---|---|
| Compliance Team + checklist read + sanctioned application | sanctioned documentation queue scope | allowed |
| Company Secretary + checklist read + sanctioned application | sanctioned documentation queue scope | allowed |
| Credit Manager + checklist/application read | canonical application object scope | allowed |
| Attributable committee approver + checklist read | frozen case attribution | allowed |
| Auditor + checklist read + active audit grant | persisted audit-read scope | allowed |
| Permission-only or unrelated approver | no object scope | `403 OBJECT_ACCESS_DENIED` |
| Missing checklist permission | no global authority | `403 FORBIDDEN` |
| Unknown id, authorised Compliance Team | source-defined absent-parent disclosure | `404 NOT_FOUND` |
| Unknown id, permission-only actor | nondisclosure | `403 OBJECT_ACCESS_DENIED` |
| Pre-sanction application | A-104 compatibility | retained 005D route |
| Inactive actor | authentication boundary | `401` |

The matrix and the assertion that denied paths issue no checklist-table query are exercised by
`test_get_enforces_permission_and_source_authorised_object_scope`.

## Cancelled-cheque signature fact

| Retained rows | Published mismatch | Source/blocker |
|---|---:|---|
| none | unknown | `signature_mismatch_source_missing` |
| any pending/unverified row | unknown | `signature_mismatch_source_unverified` |
| all verified, all `false` | false | `persisted_signature_match` |
| all verified, all `true` | true | `persisted_signature_mismatch` |
| verified rows disagree | unknown | `signature_mismatch_conflicting` |
| malformed status | unknown | `signature_mismatch_source_malformed` |

Only a unanimous set of valid verified rows publishes a boolean. The application-owned seam queries
`CancelledCheque`; `legal_documents` imports neither the members model nor its ORM.

## Frozen subsidiary route

| Frozen flags | Published route |
|---|---:|
| both exact booleans, either true | subsidiary (`true`) |
| both exact booleans, both false | direct (`false`) |
| a flag missing, partial, or non-boolean | unknown/blocker |

## Refresh ownership

| Refresh input | Owned result |
|---|---|
| unchanged applicability | zero write; completion/verifier/time/remarks/checklist/signatures preserved |
| changed applicability, no completed conflict | applicability-only audit delta |
| changed applicability against completed evidence | explicit atomic conflict; zero write |
| new current-provenance generated document | linkage-only audit delta; completion preserved |
| legacy/mismatched renderer provenance | remains unlinked; zero linkage/applicability evidence |
| label/order drift | retained creation-time presentation; no applicability evidence |
