# Architecture Review Evidence

## Fixed Point and Commits

- Fixed point: `e9c7217b567dffa4214cf0df12bb8cd769120cd1`
- Diff: `git diff e9c7217...HEAD`
- `a58515b` — 006X7 credit object-scope action parity closure
- `2664e8b` — 006Y10 witness correction matrix/module boundary closure
- `93870ed` — 006Y11 member form container/error matrix closure
- `fe8b464` — 006Z4 active-member rule/snapshot closure

## Reproduced Review Facts

| Slice | Concrete observation | Corrective owner |
|---|---|---|
| 006X7 | `MatrixInventoryTests` reads `object_scope_action_codes` from test-method decorator metadata; the decorator can survive deletion of the projected action/write assertions. | 006X8 |
| 006Y10 | `witness_corrections.evaluate_witness_correction` repeats the creator/receiver/Credit Manager scope algorithm from `applications.services.evaluate_application_object_access`; PATCH skips view-level permission/scope before witness lookup. | 006Y12 |
| 006Y10 | The commit adds no two-kind backend correction matrix; existing PATCH tests do not pair contact/identity across permission, object, maker-checker, stale, malformed, unknown/immutable, and success rows. | 006Y12 |
| 006Y11 | Mounted success covers three creates, while ordinary update, identity request, and approval have failure-only additions; browser exact request assertions cover create bodies. | 006Y13 |
| 006Z4 | `ActiveMemberStatusModule.verify` checks permission/version/result/maker but no member object scope; `SupplyRowProjection` omits entity/route/evidence/verifier inputs. | 006Z5 |
| 006Z4 | Verification updates Member plus generic history/audit without a data-model §11.5 effective active-status row; BR-006 passes from the numeric years scalar even when service usage is false. | 006Z5 |

## Repository and Queue Reconciliation

- `docs/working/CONTEXT.md` remains accurate: member/application/credit surfaces are API-backed and
  later modules remain mock-backed under their named owners.
- No slice has `## Status` of `Blocked`; no stale block required reopening.
- Queue lint produced no output (pass): every pending slice has a valid real dependency and the graph
  drains without cycles. 006Z2 now depends on 006Z5.
- No ADR was created because source functional/data-model/codebase-design requirements already define
  the desired module, evidence, persistence, and test direction.

## Functional Requirement Trace

- M02-FR-001: all three member categories are create/readback tested; success interaction proof for
  update/request/approve remains partial under 006Y13.
- M02-FR-012: requester/checker identity behavior exists; exact successful canonical interaction
  evidence remains partial under 006Y13.
- M02-FR-004..006 and BR-003..007: calculation improvements are real, but complete stored evidence,
  effective verification, object scope, and BR-006 evidence fidelity remain partial under 006Z5.
- M04-FR-004..011: production behavior is unchanged; exhaustive object-scope regression confidence
  remains partial under 006X8. M04-FR-001/002 and M04-FR-003 retain A-053/A-054 deferrals.

