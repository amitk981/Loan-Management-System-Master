# Epic 007 Digest: Sanction Approval Workflow And Registers

Sources distilled while finishing 006G and sharpening 006H/006X:

- `docs/source/implementation-roadmap.md` §12.1-§12.5
- `docs/source/api-contracts.md` §25.1-§25.4
- `docs/source/data-model.md` §15.1-§15.4 and §30/§34
- `docs/source/auth-permissions.md` §12.6, §15.8-§15.9, §20.1, §34.5

## Architecture Review 2026-07-13 10:09 - Case Boundary and Evidence Closure

- 007A5 materially closes the pending loser and open-case ledger, but the sole new VersionHistory
  and `config.changed` rows are asserted only by cardinality. `007A6` proves their exact winner,
  maker/checker, reason, target, and old/new content in all four two-run PostgreSQL races.
- 007B enriches the real shell atomically and freezes complete configuration projections, but its
  replay predicate ignores changed loan-limit policy/assessment provenance, its governed
  immutability test manually fills a shell, and §25.2 success omits `current_status`.
- 007C correctly avoids live configuration and excludes obviously incomplete shells, but any user
  holding `approvals.case.read` can list/retrieve every routed case. Auth §15.9/§32.1/§37.3 requires
  unassigned Directors to be denied. Its routable predicate also accepts contradictory required-
  approver/matrix/committee JSON that can enable an injected user.
- `007C2` adds one case object-access predicate, validates the complete stored routing snapshot,
  tightens exact provenance replay, restores §25.2 status, and replaces the manual governance
  fixture with submit → enrich → read evidence. 007D now depends on that boundary.
- M05-FR-003..006 threshold/configuration behavior is substantive with winner-evidence content
  pending 007A6. M05-FR-001..003 routing/review behavior is present but not authority-complete until
  007C2; actions/conflicts remain explicitly owned by 007D/007E.

## Architecture Review 2026-07-13 08:41 - Complete Governance Ledger

- 007A4 restores the real `decide_proposal` seam and passes all four governed races twice on
  PostgreSQL after proposal migration 0005; canonical authority and proposal-detail access are
  aligned, and snapshot storage fields exist.
- The race helper proves one winner plus an unchanged pending proposal but compares only resource/
  version/audit counts. It has no open case and does not read the loser publicly. The separate case
  test performs rejection and sequential approval, not the required conflicting activation race.
- `007A5` adds full proposal/effective/history/audit/case equality, public loser readback, a
  discriminating open case inside all four PostgreSQL races, and the remaining historical/current/
  backfill committee rows.
- Production case snapshot population remains deliberately owned by 007B. The 006G case is an
  unrouted shell until 007B atomically consumes the approved rule/committee resolver projections;
  007C must exclude empty shells from approver queues and actions.

## Architecture Review 2026-07-13 06:01 - Governed Activation Regression

- 007A2 closes retained-history lifecycle, persisted committee authority, pagination, and the four
  direct-activation PostgreSQL races at its own commit. 007A3 then changes create/supersede into
  pending proposals but leaves those races calling the old interface; the retained PostgreSQL logs
  predate the proposal migration and no longer prove the shipped activation boundary.
- `007A4` must create competing proposals and race authorised checkers through approval for rule and
  committee create/supersede, twice on PostgreSQL. It also owns the unproved CFG-007 open-case
  snapshot, complete proposal/case loser ledger, and the partial A2 committee/lifecycle matrices.
- The canonical source error is `APPROVAL_AUTHORITY_REQUIRED`, not the introduced
  `APPROVER_AUTHORITY_REQUIRED`. Proposal detail must not expose Critical configuration reasons and
  actor/action facts to every authenticated user; 007A4 aligns both contracts.
- Sequential governed activation is substantive, but M05-FR-003..006 remain partial until 007A4
  restores current concurrency acceptance and 007B snapshots the resolver output into real cases.

## Architecture Review 2026-07-13 04:49 - Historical and Governance Corrections

- Auth §§31.1-31.2 makes the Approval Matrix Critical configuration: every change needs a reason and
  Admin plus CFO/Company Secretary approval. 007A activates immediately with one actor recorded as
  both author and approver; `007A3` adds pending proposal, distinct business approval/rejection, and
  coherent activation/version/audit evidence.
- Committee create currently validates only three distinct users, not active persisted CFO/two-
  Director authority. `007A2` enforces authority and exposes one effective-date committee resolver.
- Rule/committee overlap checks currently ignore superseded historical rows while the matrix resolver
  intentionally resolves them by date. `007A2` makes all resolvable history non-overlapping and adds
  lifecycle/database constraints, pagination, and historical-case immutability proof.
- 007A's two PostgreSQL concurrency tests were skipped by SQLite and omitted from both retained
  “five-race” commands. `007A2` must run the approval class directly twice; the protected validator's
  fixed discovery command remains an owner/orchestrator follow-up.
- M05-FR-004..006 seeded exact/above/exception facts pass sequentially. M05-FR-003..006 remain
  partial until historical concurrency and governed activation pass in 007A2/007A3.

## 007A Approval-Matrix Boundary

- Rules are effective-dated and describe decision type, inclusive amount bounds, optional
  condition code, required role list/director count, joint-approval flag, register requirement,
  and active/inactive status.
- Source sanction rules: up to and including INR 500,000 requires CFO + one Director; above INR
  500,000 requires CFO + two Directors; an exceeds-limit condition requires CFO + two Directors
  and exception handling. Configuration must persist these facts rather than hard-code them in
  the case engine.
- Admin/config management requires `approvals.matrix.manage`; reads require
  `approvals.matrix.read`. Effective ranges and amount ranges must not overlap for the same
  decision/condition route, and updates must preserve historical case snapshots.
- Architecture review sharpening: expose one resolver projection consumed unchanged by API and
  downstream routing, and prove overlapping effective rule creation/supersession with a PostgreSQL
  one-winner race while preserving already-referenced historical rule snapshots.

## 007B Existing 006G Case Enrichment

- 006G already creates the unique pending application/appraisal case shell at source §24.5. 007B
  must resolve the effective 007A rule and enrich that row with recommended amount, matrix-rule
  linkage, required-approver snapshot, related-entity facts, and exception condition/reason.
- ADR-0005 and corrective 006G2 make the approval-case module the only create/read/enrichment seam;
  007B must use that interface and must not import or mutate the case model from credit code.
- Do not expose a second generic create path that can duplicate the 006G case. Any source §25.2
  adapter must return/enrich the existing row idempotently or reject incompatible state.
- Approver selection, conflict exclusion, actions, sanction decisions, and register entries remain
  their later dedicated slices. Required approver facts are immutable snapshots once assigned.

## 007B Delivered Enrichment Contract

- Source §25.2 enriches, but never creates, the unique 006G shell. Credit owns a locked application
  → appraisal → review-history projection; approvals then locks the case and consumes each dated
  public configuration resolver exactly once.
- The case freezes amount, related application, reason/exception condition, complete rule and
  committee projections, concrete ordered CFO/Director users, excluded list, verified loan-limit
  policy provenance, decision date, and version 2 while preserving the 006G workflow-event id.
- Exact repeats are zero-write reads. Conflicts/decided cases are 409; stale provenance and missing
  effective approved configuration leave the version-1 shell and all evidence unchanged.

## 007C Delivered Routed Read Contract

- Source API §25.3/§25.4 exposes paginated case list/detail reads under
  `approvals.case.read`; assignment filtering additionally requires a still-pending user slot in
  the complete stored 007B snapshot, no exclusion, and no immutable action.
- A routed case requires matching stored rule/committee ids, versions, decision dates, complete
  matrix/committee projections, an ordered non-empty authority list, amount/entity facts, and
  `version >= 2`. An unrouted 006G shell remains invisible even when its amount/status resembles a
  real case.
- Detail authority, queue membership, and §44 actions never consult live configuration. Global
  readers may see the case but receive no enabled assignment action unless they are also the
  pending stored approver with the action-specific permission.
- M05-FR-002 review facts are dynamically read through from the application/appraisal owners;
  action decisions are read from the immutable §15.4 ledger without mutating required snapshot
  JSON. Approval actions, conflict population, and UI remain 007D/007E/007I.

## 007A Delivered Configuration Contract

- Exact ₹5,00,000 is included in the lower persisted rule; the upper rule begins at ₹5,00,000.01.
  The explicit `exceeds_permissible_limit` route is resolved only from a caller-supplied canonical
  condition code, never from client/display money comparison.
- All matrix and committee mutations serialize through a persistent approval-configuration lock,
  then validate inclusive amount/effective ranges inside the same atomic transaction. A loser writes
  no rule, committee, version history, or business audit evidence.
- Downstream 007B/007C must call `resolve_approval_matrix` with the case decision date and store its
  immutable projection unchanged; they must not query rule rows or repeat range/director/register logic.

## 007A2 Historical and Committee Closure

- Active and superseded rows are the only resolvable lifecycle states and remain resolvable only
  inside their stored inclusive dates; inactive rows never resolve. New writes cannot overlap any
  retained resolvable history.
- Committee membership is authorised exclusively by three distinct active users' persisted
  `approval_authority_type`: exactly CFO, Director, Director. Display role names are irrelevant.
- `resolve_sanction_committee(decision_date)` is the sole dated committee projection for 007B and
  returns the retained committee id/version plus the three authority user ids.
- Rule and committee lists accept only bounded `page`/`page_size` and return the standard paginated
  envelope; four PostgreSQL create/supersede races are the authoritative concurrency proof.

## 007A3 Maker-Checker Governance

- Rule and committee POST/PATCH writes create immutable pending proposals with mandatory reasons;
  resolvers remain on the prior effective configuration until approval.
- Only a distinct active user with persisted CFO or Company Secretary authority may decide.
- Approval revalidates retained history and committee authority under the shared lock, activates
  atomically, and writes separate author/approver history plus `config.changed` evidence. Rejection
  and stale/conflicting losers leave effective configuration and open-case snapshots unchanged.

## 007A4 Governance Concurrency and Snapshot Closure

- Proposal detail is readable only by its maker, an active persisted CFO/Company Secretary checker,
  or a holder of `approvals.matrix.read`; unrelated authenticated users receive `403 FORBIDDEN`.
- The sole ineligible-checker code is `403 APPROVAL_AUTHORITY_REQUIRED`. Approval-time authority is
  revalidated and Critical activation remains serialized behind the configuration lock.
- Open approval cases carry immutable rule/committee ids and versions, required approver JSON,
  decision date, workflow-event identity, and a positive case version. Configuration decisions and
  resolver/detail reads never mutate those stored facts.
- Governed rule/committee create and supersede races begin with two pending proposals and race
  distinct eligible checkers through `decide_proposal`; one activation wins and the loser proposal
  remains byte-for-byte pending with no effective/history/audit/case writes.

## 007A5 Complete Loser Ledger

- Each of the four governed PostgreSQL races now carries a discriminating open case with stored
  rule, committee, required-approver, decision-date, workflow-event, and positive-version facts.
  Proposal, effective configuration, retained history, business audit, and case ledgers distinguish
  the sole winner from an unchanged pending loser; the exact four methods pass twice after approvals
  migrations 0005 and 0006.
- Proposal detail now returns the immutable proposal `payload` and nullable `decided_at`, allowing
  the public boundary to prove a loser's reason, maker, target/payload, status/version, null decision
  fields, and checker action projection without querying private implementation state.
- Historical and current committee dates resolve independently. A conflicting historical backfill
  returns the stable configuration conflict while the complete ledger and retained resolver output
  remain unchanged; duplicate and swapped authority failures have independently named public rows.

## 007A6 Winner Evidence Content Closure

- All four governed PostgreSQL create/supersede races identify the sole new VersionHistory and
  `config.changed` rows and assert their exact winner target/version, maker, distinct checker,
  reason, proposal/request provenance, approval timestamp/reference, effective dates, and
  serialized configuration values.
- Winner and loser proposals carry discriminating reasons, request ids, and versions. Exact content
  assertions reject winner evidence containing the loser's reason, request id, or version even when
  ledger cardinality remains correct.
- Supersession audit evidence preserves the predecessor's pre-activation value in `old_value_json`
  and adds its exact closed projection as `new_value_json.superseded_configuration`; creation omits
  that key and retains a null old value.
- VersionHistory now stores nullable generic old/new JSON plus the approval reference/time. Governed
  activations persist the proposal id/type/payload, target id, activated resource, and closed
  predecessor projection; the history timestamp is exactly the proposal decision timestamp.
