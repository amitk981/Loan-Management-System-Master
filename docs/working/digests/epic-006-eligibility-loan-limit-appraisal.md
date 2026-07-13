# Epic 006 Digest: Eligibility, Loan Limit, Appraisal, and Credit Review

## 006Z15 Member Public-Action Authority Matrix Closure

- Ten independently selectable rows now invoke the real member list/detail/update, identity
  approval, supply capture/verification, service-evidence create/update, staff eligibility
  calculation, and active-status verification interfaces. No row imports or calls the authority
  evaluator as acceptance; exact denial and success ledgers cover member, identity, scope, supply,
  service-maker, status, eligibility, history, audit, and workflow facts.
- Permission-without-scope detail/mutations return `403 OBJECT_ACCESS_DENIED`; the source-required
  list contract filters to an empty `200` page before counts. Matching assigned, global,
  created-by, active-team, inactive-team, unrelated-team, and unrelated-member behavior executes
  real list/detail/mutation seams.
- Staff calculation rejects cross-member query/body substitution after application authority and
  derives the member only from the owned application. Portal self-service and borrower-limit reads
  reject a different `member_id` from the authenticated `PortalAccount` without writes or identifier
  disclosure. `ActiveMemberStatusModule.calculate` remains actorless and internal.
- HTTP adapters now preserve object-scope denial separately from missing-permission and
  maker-checker denial using typed module exceptions; member calculations and M02-FR-004..006
  business rules are unchanged.

## Architecture Review 2026-07-13 10:09 - Public Action Proof Still Shallow

- 006Z14 correctly removes the dead `calculate_for_actor` seam and brittle filename/string caller
  whitelist. Existing focused suites retain substantive member calculations, persisted scope
  shapes, and application/portal ownership behavior.
- Its new ten-row “action matrix” never invokes the named list/detail/update/identity/supply/
  evidence/status boundaries. Every row calls only `evaluate_member_authority`, asserts a Boolean,
  and counts mostly empty ledgers; a label can therefore claim a public action without executing it.
- `006Z15` replaces those aliases with independently selectable real module/HTTP actions, exact
  no-scope denial ledgers, matching-scope success, all persisted scope kinds, and actorless staff/
  portal/borrower-limit substitution proof.
- M02-FR-004..006 business behavior remains substantive, but the source-required public authority
  proof remains partial until 006Z15.

## 006Z14 Member Authority Action and Calculation Proof Closure

- Eleven independently selectable member-authority rows now use one custom-role actor with every
  action permission and no initial scope. Every denial returns the canonical object-scope result
  with unchanged member, assignment, supply, service evidence, active status, history, audit, and
  workflow ledgers; only the matching assigned scope enables the row and unrelated members/actions
  remain denied.
- Existing scope-shape tests retain global, created-by, assigned, active team, inactive team, and
  unrelated-member proof. The focused application, portal, borrower-limit, supply, and member suites
  execute the real owning boundaries rather than inferring safety from caller filenames.
- The unused `calculate_for_actor` seam and exact source-text caller whitelist are removed.
  `ActiveMemberStatusModule.calculate` remains an actorless domain calculation reached from
  application-authorised staff or authenticated member-owned boundaries; BR-004/006/007 and
  M02-FR-004..006 calculations are unchanged.

## Architecture Review 2026-07-13 08:41 - Member Authority Proof Closure

- 006Z13 correctly adds database shape/uniqueness constraints, retains valid legacy assignments,
  and preserves the underlying M02-FR-004..006 supply/status/relaxation behavior.
- Its promised public permission-versus-scope action matrix is not present: broad existing suites
  commonly pre-grant scope, while registry negatives often omit permission too. `006Z14` must use
  one all-permissions/no-scope actor, independently deny every public action with a complete ledger,
  then enable only the row receiving a matching assignment.
- The new `calculate_for_actor` has no production caller and the caller guard asserts exact source
  filenames/strings. `006Z14` replaces that with application/portal/member-owned behavioral proof
  and removes the unused seam unless a source-backed public boundary actually consumes it.

## 006Z13 Member Scope Persistence and Calculation Boundary Closure

- Database check constraints now enforce every `MemberScopeAssignment` scope/member/team shape,
  and conditional unique constraints close nullable SQL duplicate grants. Migration 0014 retains
  the earliest valid authority fact while removing only exact legacy duplicates before enforcement.
- Real evaluator tests cover global, assigned, created-by, active team, and inactive-team behavior;
  the focused public member suites retain list/detail/update, identity, supply, service evidence,
  active verification, portal ownership, zero-write denial, and immutable maker behavior.
- Actorless active-member calculation remains a domain computation. Staff has an explicit
  `calculate_for_actor` boundary; a dependency guard fixes the only production callers to the
  application-scoped eligibility path and authenticated-PortalAccount-derived portal/credit paths.

## Architecture Review 2026-07-13 06:01 - Member Scope Closure Status

- 006Z11 now separates action permission from persisted `global`/`team`/`assigned`/`created_by`
  scope, filters list totals before pagination, and retains every service-evidence maker. It closes
  the prior permission-as-global and maker-erasure defects in production.
- `MemberScopeAssignment` still relies on `clean()` for scope shape and nullable uniqueness, so
  bulk/direct ORM paths can persist invalid or duplicate authority facts. `006Z13` adds database
  constraints and non-destructive migration proof before an assignment-management surface exists.
- Public acceptance remains distributed: list/detail/count are direct, while other action fixtures
  mostly add assignments to existing happy paths. `006Z13` adds permission-without-scope then
  assignment-enabled module/HTTP rows for every member action and maps the actorless calculation
  engine behind staff object scope or authenticated portal ownership.
- 006Z12 independently executes the remaining stale/supply/missing-fact borrower-limit denials with
  the exact redacted contract and complete member/authority/evidence/assessment/application/config/
  audit/workflow before-after ledger. M04-FR-005..007 remain server-owned and passing.

## 006Z12 Portal Limit Denial Matrix Evidence Closure

- Five independently selectable authenticated public API rows now prove stale authority snapshot,
  changed supply provenance, missing profile, missing verified landholding, and contradictory
  profile/land acreage all return the same exact redacted unavailable contract without writes.
- The denial ledger captures Member, active authority, supply, service evidence, shareholding,
  landholding/profile, loan-limit assessment, application, policy/version, audit, and workflow
  state. Authentication occurs before each row's baseline, so login audit is never hidden.
- Existing future/closed/manual/mismatched authority, changed service evidence, duplicate share,
  no-policy, and invalid-amount rows retain the public boundary. Production calculation is unchanged.

## 006Z11 Member Scope Assignment and List Nondisclosure Closure

- Member action permission and object scope are separate persisted facts. Action-specific global,
  team/member, assigned/member, and created-by grants live in `MemberScopeAssignment`; no role,
  permission, unowned-row, or caller-Boolean shortcut creates management scope.
- Directory scope is applied before search, count, and pagination, and detail/actions consume the
  same authority seam. Creator ownership remains only the Field Officer-style read/update baseline;
  high-risk verification and identity approval require explicit action-specific assignment.
- Produce-supply and service/relaxation evidence maintenance now enforce member scope. Service
  evidence retains every creator/material updater in immutable maker provenance, including a
  migration backfill from legacy verifier facts, and any prior maker remains unable to verify the
  derived active status.

## Architecture Review 2026-07-13 04:49 - Scope, Maker Provenance, and Denial Proof

- 006Z9 corrected route/decision agreement, but it made the action permission itself a global member
  scope. Auth §25.1 says member reads are scope-limited unless management; `006Z11` separates
  permission from persisted/configured global/team/assigned/created-by scope across list/detail and
  every member action.
- Service-evidence update replaces the current verifier and loses earlier maker provenance.
  `006Z11` retains creator/material-updater identities so actor A cannot create, actor B update, and
  actor A later verify the derived status.
- 006Z10's calculation, mounted submit/refetch/errors, and trusted browser lifecycle pass. Its public
  backend matrix still omits stale authority, changed supply, missing profile/land, and assessment
  state in the zero-write ledger; `006Z12` closes those proof gaps.
- BR-003..007 and M02-FR-004..006 business facts remain substantive but authority/maker acceptance is
  partial until 006Z11. M04-FR-005..007 calculations and UI lifecycle pass; denial proof is partial
  until 006Z12.

## 006Z10 Portal Limit Interaction and Boundary Proof

- Portal limit policy resolution now uses the verified authority's stored calculation date, so a
  later active policy cannot invalidate or rewrite a retained projection on reload.
- Public invalid-amount cases prove a stable validation envelope, redaction, and unchanged member,
  authority, application, audit, workflow, and policy evidence.
- Mounted MP05 drives the full create, submit, and one canonical returned-amount refetch trace. The
  trusted four-screenshot contract uses contradictory amount/flag fixtures and includes submit,
  refetch, and reload while retaining the backend date/rule provenance.

## 006Z9 Active-Member Authority and Decision Contract Closure

- Member scope is projected from explicit action permissions or persisted ownership; system-role
  provenance and an unowned row never create authority. Member read, active verification, and
  identity-change approval are explicit global action scopes; member update remains owner-scoped.
- Qualification routes and stored decisions agree exactly: pass/active, relaxation/relaxation, and
  non-qualifying/inactive. Mismatches return `INVALID_DECISION` before any effective status, member
  pointer/version, history, audit, or workflow write.
- Active-status checkers cannot have captured or verified any qualifying supply row or verified any
  qualifying service/relaxation evidence used by the result.

## Architecture Review 2026-07-13 - Active Decision and Portal Lifecycle Residual

- Member global authority is currently inferred from `Role.is_system_role` for two permissions and
  from absence of an owner for other permissions. `006Z9` replaces those proxies with an explicit
  source-backed scope result shared by Registry and active verification.
- A relaxation calculation currently accepts/stores `decision = active`, and the same actor may
  maintain qualifying service/relaxation evidence and verify the result. `006Z9` owns exact
  route/decision matching, maker-checker evidence ownership, and paired module/HTTP matrices.
- 006Z8 correctly centralizes limit math and retains stored-date authority, but its tests prove
  initial GET/rendering rather than successful submit/refetch, 400/403/409, reload, or blocked deep-
  module cases. `006Z10` owns the full public projection and real portal lifecycle proof.
- BR-004/006/007 and M02-FR-004/006 remain substantive. BR-003/005 and M02-FR-005 remain partial
  until 006Z9; M04-FR-005/006/007 calculations pass while portal acceptance remains partial until
  006Z10.

## 006Z8 Portal Limit Provenance, Module, and Interaction Closure

- Borrower-limit authority is revalidated from its stored calculation date, result id, and complete
  evidence snapshot. Mere date passage no longer expires unchanged authority; future, closed, stale,
  and evidence-mismatched records remain unavailable.
- Credit now owns authority validation, current share/verified-land selection, effective policy,
  lower-limit arithmetic, and advisory derivation behind one redacted projection. The members portal
  adapter delegates without member-domain evaluation, configuration resolution, or money decisions.
- MP05 uses its single existing formatter and controlled requested amount, binds authoritative
  `required_loan_amount` errors to the visible field, and performs a canonical projection GET only
  after successful submission. The four-state browser contract enters through the real member-login
  interaction and is declared for Ralph's two trusted external runs.

## 006Z7 Active-Member Relaxation, Authority, and Evidence-Race Closure

- BR-003/BR-005 recent-member relaxation is evaluated before ordinary inactive rejection: one
  complete qualifying supply year plus distinct verified relaxation evidence is required, and the
  complete dated evidence remains in result provenance.
- Member authority has one member-owned evaluator. Ownership/unowned scope and explicitly global
  high-authority permissions are evaluated without caller bypass flags or role-code switches;
  Registry and active verification consume the same policy.
- Supply capture/verification and service-evidence create/update lock Member before the exact
  evidence row and advance Member provenance. Service mutations write matching history/audit facts.
- The authoritative PostgreSQL suite now proves verifier versus supply create, supply verify,
  service create, and service update alongside the two-verifier race. Every race has one coherent
  winner/current pointer and no loser status/history/audit/workflow evidence; the five credit races
  remain green twice.

## 006X10 Executable Credit Object-Scope Rows

- The eight public credit object-scope cases are registered as direct callable test-method
  references. Missing or renamed methods fail module resolution; missing/duplicate action rows and
  duplicate/non-test callables fail the completeness contract.
- Create, update, revalidate, submit-review, loan-limit, and sanction selections now execute only
  their own persisted arrangement, exact disabled six-field projection, matching public write,
  `OBJECT_ACCESS_DENIED`, and full before/after evidence comparison. Review and eligibility retain
  the same isolated contract.
- Projection/write/category/evidence omission proofs execute the real eligibility arrangement and
  public write rather than synthetic exceptions. All eight rows pass alone in forward and reverse
  separate processes; production behavior and PostgreSQL contracts are unchanged.

## Architecture Review 2026-07-13 - Residual Matrix, Evidence, and Portal Authority Closure

- 006X9 removed process-global state, but four advertised IDs execute paired sibling rows and its
  explicit table validates strings rather than executable cases. `006X10` owns one independently
  selected substantive row per public action and completeness that resolves/runs the cases.
- 006Z6 snapshots service/relaxation facts and fixes date intervals, but BR-003/005 recent-member
  relaxation is rejected before evidence evaluation; Registry/active authority policies diverge;
  and the required verifier-vs-evidence PostgreSQL races were not added. `006Z7` owns these closures.
- 006Z2 keeps money arithmetic on the server, but recalculating the dated result with today's date
  expires unchanged authority, and the members portal adapter duplicates credit orchestration.
  `006Z8` moves the projection behind credit, validates stored-date provenance, and owns mounted/
  trusted-browser submit, error, canonical-refetch, redaction, and screenshot proof.
- M04-FR-001/002 remain under A-053; M04-FR-003 remains under A-054. M04-FR-004..011 retain
  substantive behavior subject to 006X10/006Z8 regression closure. M02-FR-004..006 and BR-003..007
  remain partial until 006Z7.

## 006Z2 Portal Application Limit Display Authority

- A read-only PortalAccount-scoped endpoint exposes only redacted available/unavailable limit facts.
  It accepts authority only from the current effective record whose identifier and complete snapshot
  still match the member-domain result derived as of today.
- The shared 006C calculator computes effective-policy share, verified-land, and lower limits;
  requested-amount comparison is server-owned. Contradictory or incomplete facts never become zero.
- MP05 restores the existing green three-card composition, explicit unavailable/error states,
  server exception advisory, and review-row maximum with no client limit arithmetic or fallback.

## 006Z6 Active-Member Evidence Atomicity And History Closure

- Results include complete qualifying dated service and distinct relaxation evidence; every review
  fact participates in result provenance and the persisted snapshot. Reason alone cannot relax.
- Verification locks member and evidence rows and enforces forward-only immutable history.
- Member Registry and active verification consume one member-owned authority evaluator; portal
  projections remain redacted.

## 006X9 Isolated Credit Object-Scope Matrix

- The eight public credit action codes now have one explicit table of unique, independently
  selectable test identifiers. Each selected row executes its persisted-resource arrangement,
  exact disabled six-field projection, matching public write, `OBJECT_ACCESS_DENIED` category, and
  complete before/after evidence comparison without relying on another test or worker.
- The process-global `EXECUTED_OBJECT_SCOPE_RESULTS` ledger and class-name ordering are removed.
  Normal and reversed selection both execute eight substantive rows, while deliberately omitting
  any assertion phase fails locally without direct bookkeeping mutation.
- Production credit behavior, HTTP 403 non-disclosure, authority/state/provenance/maker-checker
  coverage, and PostgreSQL race contracts are unchanged.

## Architecture Review 2026-07-12 - Evidence Atomicity and Isolated Credit Proof

- 006X8 executes substantive object-scope rows, but its aggregate ledger is a module-global list
  populated only when other tests run first in the same worker. `006X9` replaces order/process
  coupling with eight independently selectable parameter rows whose projection, public write,
  denial-category, and complete evidence assertions execute together.
- 006Z5 persists the §11.5 record and complete supply-row facts, but BR-006 service evidence remains
  outside the deterministic result/snapshot and one-year relaxation can be created from free-text
  reason without a distinct evidence fact. `006Z6` makes service/relaxation evidence reviewable and
  part of result provenance.
- Active verification locks only Member while reading unversioned supply/service evidence, and its
  effective-history update accepts a backdated date that can close a prior record before it began.
  `006Z6` adds evidence-vs-verifier PostgreSQL races, valid interval rules, later-decision history,
  and one shared Member Registry/active-status authority seam.

## 006Z5 Active-Member Evidence and Verification Governance

- Active verification now creates a real source §11.5 effective-dated record and points the Member
  compatibility projection at that record UUID; later decisions close, but never rewrite, the prior
  record. Member projection, record, history, and audit remain one atomic write.
- Supply snapshots retain entity, route, Producer Institution, evidence, verifier, date, and stable
  qualification facts for credit evidence. Portal rows strip row/member/institution IDs, evidence
  references, verifier facts, and staff actions.
- BR-006 no longer trusts `employment_or_service_years`. A verified dated service-evidence row must
  prove three continuous years, an eligible recipient, and an evidence reference; otherwise the
  result is `manual_evidence_required`. Persisted relaxation status/reason/evidence plus one complete
  qualifying supply year is required for the one-year route.
- Verification requires an explicit non-future date, rejects unknown fields, and applies a member
  object-scope check before effective-record lookup with equivalent missing/existing denials.

## 006X8 Executed Credit Object-Scope Ledger

- The static `@object_scope_cases` metadata inventory is removed. Each of the eight public credit
  action codes now enters one runtime ledger only after a shared row assertion has executed the
  exact disabled six-field projection, observed the matching public write object denial, asserted
  `OBJECT_ACCESS_DENIED`, and compared the full persisted before/after evidence snapshot.
- Deliberately incomplete rows omit projection, write, category, and evidence phases in turn; each
  fails with the missing phase and cannot emit a result. The aggregate test requires exactly eight
  unique executed results, preventing labels, constants, or empty test bodies from claiming closure.
- Existing eligibility, loan-limit, appraisal, review, and sanction HTTP object-scope regressions
  remain standard `403` non-disclosure paths. Production credit code and business behavior did not
  change.

## Architecture Review 2026-07-12 - Executed Credit Rows and Active-Member Governance

- 006X7 projects and writes all eight object-denied credit actions with substantive assertions, but
  its completeness check still trusts `@object_scope_cases` metadata. `006X8` owns an executed-row
  ledger that records coverage only after projection/write/category/evidence assertions pass.
- 006Z4 fixes continuity/as-of behavior and provides real calculation, snapshot, portal, and
  PostgreSQL winner evidence. Its verify seam has no member object scope; its row snapshot omits the
  entity/route/evidence/verifier inputs; and it persists no source §11.5 effective status record.
- 006Z4 also grants BR-006 from a numeric service-years scalar without dated recipient/evidence facts.
  `006Z5` owns object-scoped verification, full internal evidence, effective-dated persistence, and
  manual-evidence fallback until the documented three-year route is actually provable. 006Z2 now
  depends on 006Z5 and may expose only the deliberately redacted verified projection.

## 006Z4 Active-Member Rule and Snapshot Closure

- `members.modules.active_member_status` now returns a deterministic dated result identifier and a
  complete immutable row/result projection. Continuity stops at gaps; financial years not completed
  by `as_of_date` stay visible with `financial_year_not_complete_as_of_date` and never qualify.
- The public rule covers service-backed four-year individual/FPC/Producer Institution routes,
  individual three-year employment/service, Producer Institution supply routing, and recorded
  one-year relaxation without inventing an approver. Pending, malformed, wrong-route/entity, and
  evidence-free rows retain stable explanations.
- Public verification owns permission, maker-checker, reason, decision, member version, current
  result, repeated-decision, atomic member/history/audit, and PostgreSQL winner/loser behavior.
- Eligibility persists the exact complete active-member snapshot used for the application. Portal
  supply consumes the same classification and exposes dated result metadata without member IDs or
  staff actions.

## 006X7 Credit Object-Scope Action Parity Closure

- A shared public projection overlay evaluates application object access before resource
  serialization. Eligibility, loan-limit/appraisal-create, appraisal update/revalidate/submit/review,
  and sanction projections all consume it without changing HTTP non-disclosure.
- All eight real credit actions execute a disabled six-field projection against the same persisted
  out-of-scope resource used by the matching public write. The exact reason is `You do not have
  access to this loan application.`, the write category is `OBJECT_ACCESS_DENIED`, and the complete
  resource/evidence snapshot is unchanged.
- Static `EXECUTED_CASES` inventories are removed. Object-scope completeness derives from decorated
  executable test methods; removing the eligibility case produces a focused completeness failure.

## Architecture Review 2026-07-12 - Credit Object-Scope Matrix Residual

- 006X6 materially expands the public action/write matrix and closes role/reason defects, but its
  object-scope rows capture an enabled action before ownership changes and assert only the later
  write exception. Static `EXECUTED_CASES` labels can therefore claim object-scope coverage without
  a disabled six-field evaluation or reason/category comparison.
- `006X7` owns executable-case-derived completeness plus same-resource object-scope evaluation/write
  parity for every credit action while preserving HTTP resource non-disclosure. M04-FR-004..011
  behavior remains substantive, but the advertised exhaustive matrix stays partial until it lands.
- 006Z4 and dependent 006Z2 remain concretely sharpened and unchanged; they follow the new corrective
  slices in filename order without depending on unrelated credit/member UI regression work.

## 006X6 Credit Authority and State Matrix Closure

- The executable public matrix now covers the eight real §44 action codes without synthetic
  review-decision suffixes. Twenty tests invoke the same public projection/write seams across
  enabled, permission, role, object-scope, maker-checker, state, stale-state, frozen-provenance,
  immutable-review, and malformed-rejection variants as applicable.
- Matrix execution exposed two projection defects: appraisal review/sanction role blockers used a
  generic role message instead of the exact public-write reason, and appraisal creation inherited
  loan-limit's ineligible reason. Both projections now use the matching write reason.
- Denied rows retain resource state and audit/workflow/review/rejection/case cardinalities. All
  three review decisions still use `credit.appraisal.review`; rejection alone creates one draft
  rejection note.
- The unchanged authoritative PostgreSQL five-race suite ran twice with five tests and zero skips.
  Its sanction race begins from an enabled projection, preserves one case/event winner, and writes
  no loser evidence. No additional projection/write race was exposed by the completed matrix.

## Architecture Review 2026-07-12 - Matrix and Active-Member Residual Closures

- 006X5 invokes every named public credit write, but its denials remain mostly permission-only. The
  required role/object/maker-checker/provenance/history/rejection/stale matrix is not executable, and
  the inventory uses synthetic decision-suffixed codes rather than projected actions. 006X6 owns the
  real parameterised action/write authority/state matrix.
- 006Z3 moved calculation into the member domain and rejects legacy flag-only service evidence, but
  its continuity helper can count across gaps: six years split across three clusters can report five
  when the longest run is three. `as_of_date` does not exclude future rows.
- The active-member module exposes no verify seam, does not preserve the complete dated evidence
  result in the application snapshot, ignores BR-006's three-year employment/service route, and lacks
  institution/relaxation/as-of tests. Portal rows hide their computed qualifying reason. 006Z4 owns
  these source-backed rule, snapshot, verification, and explanation closures before 006Z2.

## 006X5 Executable Public Action / Write Matrix

- The public regression now executes eligibility run, loan-limit calculate, appraisal create/
  update/revalidate/submit, reviewed/returned/rejected review, and sanction submission through the
  deep module interfaces. Each action is a six-field projection and each authority denial asserts
  stable reason parity plus zero state/audit/workflow/history/rejection-note/case evidence.
- The matrix exposed and corrected the loan-limit projection's generic appraisal-create denial;
  it now matches the public write's action-specific permission reason.
- The authoritative PostgreSQL suite now includes a stale-enabled sanction projection race. The
  competing transition is the sole winner; the stale write creates no loser evidence. The fixed
  five-test suite covers all six race scenarios and passed twice without skips.
- The next corrective slices 006Y5 and 006Y6 were rechecked against the already-open architecture
  findings: their concrete member-registry duplicate/maker-checker/form contract and witness
  contact/action-parity requirements remain execution-ready without new business-rule invention.

## 006X4 Public Action / Write Matrix Closure

- The public action/write trace now enumerates eligibility, loan limit, appraisal create/update/
  revalidate/submit, all three review decisions, and approval-owned sanction submission against
  their authoritative tests and lock boundaries.
- Failing-first coverage exposed appraisal permission denials whose projected generic reason did
  not match the public writes. Resource projections now return each write's stable action-specific
  denial while preserving the existing role, state, provenance, history, and maker-checker rules.
- The five PostgreSQL races pass: two loan-limit races, duplicate terminal review, rejected-review
  versus stale patch, and duplicate sanction submission. The race harness excludes resource-only
  `available_actions` from persisted audit projection comparison.

## Architecture Review 2026-07-12 - 006X2/006X3 Closure Audit

- 006X3 is substantively closed: Playwright collects the visual and real-server tests, the two-role
  Django path reaches exactly one pending sanction case, two trusted runs pass, and all twenty
  declared screenshots exist.
- 006X2's mounted frontend matrix is substantive, but its named backend action/write matrix is not:
  one new eligibility denial test does not pair every eligibility/limit/appraisal/review/sanction
  action across role, permission, object, maker-checker, provenance, history, rejection, and race
  cases. 006X4 owns the enumerated public-interface matrix and PostgreSQL concurrency proof.
- M04-FR-004 through M04-FR-011 retain substantive behavior/browser confidence pending that
  regression closure. M04-FR-001/002 remain under A-053; M04-FR-003 remains under A-054.

## 006X3 Credit Visual and Real-Browser Closure

- One focused Playwright file collects exactly two tests: the eighteen-state Appraisal Workbench
  matrix and a real-Django, real-login Deputy Manager Finance/Credit Manager tracer to one pending
  sanction case. The former zero-test wrapper and fully mocked tracer are retired.
- Reload scenarios reopen the routed workbench explicitly. The real path asserts exact six-field
  actions, writable PATCH keys, four canonical reads per successful mutation, no conflict refresh,
  shared assessment/decision/case/event IDs, and one repeat-submit `409`.
- Guarded deterministic seed data is synthetic and idempotent. A real HTTP backend regression proves
  the full two-role path, one-case cardinality, and metadata-only audit evidence.
- Submit-for-review remarks are now reachable through the existing textarea composition. Chromium
  baselines are stored losslessly as one-line base64 files to keep Ralph's binary line count bounded.

## 006X2 Credit Action Predicate and Container Closure

- Eligibility, loan-limit, and appraisal projections now consume reusable transition evaluations;
  sanction immutable history is re-evaluated only after the canonical review-decision lock.
- Stored eligibility exposes loan-limit calculation through loan-limit's public six-field action
  projector, closing the first-calculation reachability gap without client-side inference.
- The default `AppraisalWorkbench` is mounted through the authenticated request boundary for all
  named mutations, exact bodies, the canonical four-read refresh, PATCH response-field exclusion,
  stable disabled reasons, absent actions, and one-call 400/403/409 error behavior.
- Initial selection now supplies the fetched queue to assessment loading so a first appraisal
  create projects the selected application's requested amount instead of a stale empty form value.

## Architecture Review 2026-07-11 23:02 - False Closure of Action and Browser Proof

- 006H7 implements shared transition evaluation only for loan-limit. Eligibility/appraisal actions
  still duplicate narrower heuristics, and the promised mounted default-container HTTP matrix is
  absent; static child/source assertions cannot prove requests, refresh, or errors. Corrective
  006X2 owns all public action/write predicates plus the full mounted interaction matrix.
- 006H3's focused Playwright file fails collection with a temporal-dead-zone `ReferenceError`, finds
  zero tests, omits loading, and has no screenshots/baselines. 006X's browser tracer mocks every API,
  begins at a draft appraisal, and produced no screenshots, so it is not the specified real-backend
  UI chain. Corrective 006X3 declares the exact twenty-output trusted-browser contract.
- M04-FR-001/002 remain deferred to 012EA under A-053 and M04-FR-003 retains A-054's receipt proxy.
  M04-FR-004 through M04-FR-011 have substantive backend behavior, but UI/action reachability
  remains High risk until 006X2 -> 006X3. ADR-0005's dependency direction remains intact.

## 006X End-to-End Closure

- A public HTTP integration tracer now keeps one application, eligibility assessment, loan-limit
  assessment, appraisal, review-decision, workflow event, and pending approval-case chain linked by
  exact UUIDs across Deputy Manager Finance and Credit Manager sessions.
- The in-limit path finishes at `submitted_to_sanction_committee` with one pending case and no
  committee decision. Preparer review, review-only sanction, and sanction-before-reviewed attempts
  are denied; repeat sanction submission returns `409` without increasing case/audit/event counts.
- Focused 006H Playwright collection declares reviewed and pending-sanction evidence. Local browser
  startup remains sandbox-denied; independent browser validation decides screenshot acceptance.

## Architecture Review 2026-07-11 21:34 - Action Parity and Container Closure

- 006G5 is verified closed: absolute/relative/aliased/wildcard/package imports receive the same
  canonical dependency classification and ADR-0005's approvals-to-public-credit edge remains
  positively observed.
- 006H6 removes action projection from the applications HTTP adapter, retains six-field action
  objects/reasons, and performs the canonical four-read post-mutation refresh. Its action helpers,
  however, do not consume the exact public write predicates: loan-limit omits eligibility and
  named application gates, while appraisal review/sanction omit maker-checker, provenance, frozen-
  fact, and immutable-history consistency. React also rechecks status/provenance/role rules.
- The required default-container Testing Library matrix was attempted but failed for an unpinned
  package, then was omitted; committed tests only server-render a child and inspect source text.
  Corrective 006H7 owns shared transition predicates, full backend parity, the pinned standard test
  harness, and exact mounted HTTP/refresh/denial/validation/stale interactions.
- M04-FR-004 through M04-FR-011 remain backend-present but UI/action confidence remains High risk
  until 006H7, visual restoration 006H3, and tracer 006X complete. M04-FR-001/002 remain deferred to
  012EA under A-053; M04-FR-003 retains A-054's receipt-time proxy.

## 006H6 Workbench Action Projection

- Eligibility, loan-limit, and appraisal public modules now attach the six-field resource action
  projection; the applications HTTP adapter no longer infers actions from response keys.
- Eligibility and loan-limit reruns are rejected and projected disabled after appraisal begins.
  Appraisal actions retain state, permission, role, legacy-remediation, and risk-authority facts;
  response-only actions are excluded from frozen prerequisite and audit snapshots.
- React retains full action objects, displays disabled reasons, and awaits the canonical four-read
  assessment/case reload after every successful mutation instead of synthesizing statuses.

## 006G5 Relative-Import Dependency Guard

- The test-side AST resolver now canonicalizes `ast.ImportFrom.level` against each scanned source
  file's concrete package, including package `__init__`, parent/deeper-relative, alias, wildcard,
  and package-exposure forms.
- Relative and absolute imports share the same classifier: every credit-to-approvals edge and every
  approvals-to-private-credit edge is forbidden; only ADR-0005's public appraisal-workflow handoff
  remains allowed. The repository scan still must observe that exact public edge non-vacuously.
- This correction changes no production import, transaction, sanction identity, or workflow
  outcome. The focused sanction/module suite and full backend suite preserve the expected
  PostgreSQL-only skips under SQLite.

## Architecture Review 2026-07-11 19:23 - Relative Dependency Guard

- 006G4 now catches absolute direct/aliased/package-exposed imports and positively requires the
  ADR-0005 public approvals-to-credit edge. Its resolver ignores `ast.ImportFrom.level`, so
  relative cross-app imports can bypass classification. 006G5 resolves imports against each
  scanned file's package and adds failing-first relative/package/alias fixtures.
- 006H5 correctly removes App's mock application seed and local status updater. The routed sanction
  screen now receives an explicit empty input and shows honest not-connected copy until 007I; the
  component's file-level mock fallback remains owned by 007I.
- Epic 006 remains incomplete. No M04 functional ID is newly closed; 006H6 now depends on 006G5,
  then 006H3 and 006X retain the action/fidelity/end-to-end closure sequence.

## 006H5 App Shell Application State Authority

- `App.tsx` no longer imports `mockData`, seeds a `LoanApplication[]`, or exposes a client-side
  status mutation callback. Its sanction route supplies an explicit empty input until 007I owns
  the real sanction API wiring.
- The only affected consumer is `SanctionWorkbench`; application list/detail, completeness, and
  appraisal screens already own API-backed state independently. The sanction consumer reuses its
  existing empty card with explicit not-connected wording rather than claiming a mock-derived
  queue is real or clear.
- SanctionWorkbench's own standalone mock fallback remains final-removal scope for 007I, as listed
  in the binding mock-surface ownership table. No new mock or inline business fixture was added.

## 006G4 Sanction Dependency Boundary Regression

- Test-only package-aware AST resolution now covers direct imports, aliases, `from package import
  child`, and package `__init__` exposure forms.
- Every production credit-to-approvals edge is forbidden. Approvals may consume only
  `sfpcl_credit.credit.modules.appraisal_workflow`; credit package/model/common/private-module
  imports are rejected.
- The repository scan must positively observe the documented public handoff edge as well as report
  zero forbidden edges, so the architecture guard cannot pass vacuously.

## Architecture Review 2026-07-11 - Action Projection and UI Proof

- 006H4 removed the global-action union, but its response-key helper lives in the HTTP view and can
  enable eligibility/limit actions after their real module preconditions stop applying. Its test
  still static-renders only the view and never clicks the default container through mocked HTTP.
- Corrective 006H6 moves the six-field §44 projection behind public credit seams, requires parity
  with the actual transition predicates, preserves disabled reasons in React, and adds every
  container mutation/refresh/denial/stale assertion originally promised by 006H4.
- 006G3's production direction/event ownership is correct; corrective 006G4 strengthens only the
  package/alias/private-module regression promised by that slice.
- The interim portal loan-limit cleanup correctly removed client money math but changed approved
  colors/layout and states an unsourced reduction/return outcome. 006Z2 now restores the existing
  three-card/red-alert composition with server projections and configured-exception wording.

## 006G3 Sanction Handoff Dependency and Evidence Ownership

- Production credit code has no approvals import. The approvals-owned public handoff opens the
  atomic transaction, calls credit's public reviewed-appraisal preparation interface in the
  application -> appraisal -> review-history lock order, and owns case/status/audit/event writes.
- `ApprovalCase.workflow_event` durably links the unique pending case to the exact created sanction
  event. Submit and reload serialize that stored UUID; the read path has no latest-event query.
- Shared domain errors live below both business apps. Approvals imports credit's public appraisal
  interface and application object-access service, not credit's private common/error module.
- All five PostgreSQL races passed twice with zero skips after exact review-decision and sanction
  case/event/state/reason assertions replaced substring-only evidence checks.

## Architecture Review 2026-07-11 - 006G2/006H2 Corrective Follow-ups

- 006G2 hides the concrete case model, but `credit -> approvals.modules -> credit.modules.common`
  is still a circular business-app dependency forbidden by codebase-design §36.2. Credit also
  creates the sanction workflow event although 006G2 assigns created-event ownership to the
  approvals handoff; reload finds a latest event rather than reading a durable case-linked result.
  Corrective 006G3 removes the cycle, moves event creation into the atomic approvals seam, and
  reruns the five PostgreSQL races with exact canonical evidence assertions.
- 006H2's writable projection and canonical sanction reload client are useful, but the real page
  unions `/auth/me.available_actions` (global permissions) with resource actions. Appraisal
  responses do not supply a resource action projection, so an empty resource set cannot deny a
  permissioned user and the dedicated legacy revalidation action is unreachable.
- 006H2 tests static-render the exported view and call API wrappers directly; they never mount the
  default container, click controls, or observe HTTP/state refresh. Corrective 006H4 adds
  state/object-aware backend actions, intersection-only React authority, and failing-first real
  container tests before 006H3 restores visual fidelity.
- 006E4 remediation/history behavior and 006F4's twice-green five-race PostgreSQL execution match
  their core contracts. 006G3 will replace 006F4's weakened decision-ID substring checks with exact
  canonical workflow assertions while preserving all race outcomes.

## 006H2 Workbench Action Contract Hardening

- Returned appraisal responses now pass through one explicit writable projection before becoming
  editable state or PATCH bodies. The projection excludes IDs, frozen snapshots/provenance,
  statuses, reviewer/history/TAT/rejection facts, actor/time facts, and action summaries, including
  the corresponding response-only nested risk fields.
- The real workbench reload path reads the 006G2 sanction case alongside eligibility, loan limit,
  and appraisal facts. A `404 NOT_FOUND` means no case; success retains the server case UUID and
  canonical application/appraisal/submission facts. Sanction submission no longer invents either
  status in React.
- Ordinary action usability intersects `/auth/me.available_actions` with canonical permissions,
  role/state checks, while legacy remediation additionally requires the appraisal response's
  dedicated `revalidate_appraisal_prerequisites` action plus update and risk-management authority.
- Credit requests now reuse the shared authenticated envelope path. It preserves field errors,
  rejects malformed JSON as `MALFORMED_RESPONSE`, and performs no automatic stale-write retry.
- Frontend contract/behavior coverage verifies exact writable keys, nested risk keys, sanction-case
  URL/readback, role/action denial, legacy remediation authority, conditional rejection fields,
  standard `409` field errors, and the no-mock/no-formula boundary.

## 006F4 PostgreSQL Credit Concurrency Acceptance

- PostgreSQL 14.20 executed the two loan-limit, two appraisal/rejection, and one sanction-submission
  race twice through the public module interfaces. Both runs found and ran five tests, reported
  `OK`, and had zero skips; deterministic ordering showed the application row serializes each loser
  before payload/state mutation.
- Real PostgreSQL exposed acceptance-harness defects hidden by SQLite skips: inherited static
  fixture helpers were rebound as instance methods, appraisal assertions queried retired
  workflow-event fields instead of the canonical workflow projection, and eligibility attempted to
  lock nullable joined rows. The first two were corrected without weakening outcome assertions;
  eligibility now uses `select_for_update(of=("self",))` for its application lock.
- A run-packet verifier rejects missing markers, fewer/more than two logs, collection-only output,
  skips, non-PostgreSQL output, zero-test runs, connection/setup failures, and failed output.
- No formula, endpoint, state, permission, schema, migration, dependency, or frontend behavior
  changed. The earlier normal run failed only because the independent environment probe imported
  the package from the backend directory and then queried a non-existent application database;
  repair evidence records server facts through PostgreSQL's maintenance database instead.

## 006E4 Legacy Appraisal Remediation and History Backfill

- Corrective migration 0006 considers only `legacy_unverified` appraisals with a complete latest
  review projection. It derives `to_state` from `reviewed -> reviewed`, `returned -> draft`, or
  `rejected -> rejected`, adds at most one missing `legacy_latest_only` decision, preserves earlier
  native cycles, skips an exact existing latest decision and incomplete projections, preserves
  history on reverse, and is idempotent on a second forward run.
- `POST /api/v1/appraisal-notes/{id}/revalidate-prerequisites/` remains the single explicit repair
  seam with empty-object payload, appraisal-update plus risk-management permissions, and object
  scope. Draft stays draft; review-pending stays pending; reviewed returns to draft and clears only
  mutable latest-review authority. Immutable history and all caller-authored appraisal/risk/TAT
  facts remain unchanged.
- Rejected and sanction-submitted legacy rows return `409` with governed-manual-repair wording.
  Malformed JSON/unknown fields, permission/object denial, and forced audit/workflow failures write
  no remediation state or success evidence.
- Audit/workflow evidence names the remediation and prior/new state. Audit metadata includes source
  UUIDs and whether review authority was invalidated, but omits review comments, recommendation,
  financial values, and risk/free-text facts.

Sources distilled during slice `005I-application-intake-frontend-wiring` while sharpening 006A/006B:
- `docs/source/api-contracts.md` §22.1-§22.3
- `docs/source/data-model.md` §14.1
- `docs/source/screen-spec.md` S15 and §9.2
- `docs/source/functional-spec.md` BR-004 through BR-018 and M04-FR-001 through M04-FR-011
- `docs/source/auth-permissions.md` action and endpoint maps for eligibility/loan-limit actions

## 006D2C Concurrency And Boundary Regression
- Added PostgreSQL-only `TransactionTestCase` coverage around the public
  `LoanLimitCalculator.calculate_for_application(...)` seam. Deterministic barriers hold the first
  calculation after its application row lock while a second independent connection attempts the
  same lock.
- The valid/valid case requires one stable assessment UUID, complete non-mixed first/final source
  snapshots, two committed success audit/workflow pairs, and a final audit projection equal to the
  final row. The valid/invalid case requires one valid row/evidence pair and no invalid success
  evidence.
- SQLite explicitly reports these cases as non-proofs. `config.postgres_test_settings` is the
  repository integration configuration; run the two cases with that settings module after
  installing pinned `psycopg[binary]`.
- Static import inspection now resolves `ast.Import` and `ast.ImportFrom` package/alias references,
  rejects direct concrete credit-assessment/loan-policy/private calculator access, positively
  requires the calculator/appraisal public imports, and checks only the required subset of
  `AppraisalWorkflow` methods.
- No formula, endpoint, persistence, permission, rerun, audit payload, response, model, or migration
  behavior changed.

## Architecture Review 2026-07-10 17:33 - 005I5/006D2B/006D3/006E
- 006D2B's calculation module, locked mutable inputs, canonical public/audit projection, resolver
  direction, and rollback/failed-rerun assertions are substantive. 006D3's forward/reverse
  migration proof confirms state-only ownership without SQL or lost UUID/FK/evidence references.
- 006D2B's lock regression proves calls, not competing-transaction outcomes, and its AST check can
  miss package-level aliased concrete-model imports. Corrective 006D2C adds the codebase-design
  §26.3 concurrency proof and robust positive/negative import fixtures without changing behavior.
- 006E stores only eligibility/loan-limit UUIDs while explicit assessment reruns preserve those
  UUIDs and replace current facts. The appraisal therefore cannot prove which cultivated acreage,
  policy, financial limits, eligibility result, or exception flag supported its recommendation.
  ADR-0003 and corrective 006E2 require appraisal-owned immutable public projection snapshots.
- Functional §9.8/M04-FR-009 requires `repayment_capacity_notes`; 006E has risk fields but no such
  required field. API §24.3 remarks are validated and then discarded even though API §3 requires a
  reason for sensitive actions. 006E2 adds both before 006F.
- M04-FR-001/M04-FR-002 task creation and Deputy Manager – Finance assignment are not implemented
  by 006E. A-053 records the existing owner-planned 012EA task engine as their explicit owner; its
  slice now names the appraisal generation/closure/reopen rules and backfill test.
- M04-FR-011 Credit Manager rejection is not the same as 006F's returned-for-revision path. New
  corrective 006F2 owns terminal appraisal rejection plus one unsent 005H rejection-note draft;
  006G now follows that correction.
- M04-FR-003 remains implemented using application `created_at` as the available receipt proxy;
  A-054 records the unresolved receipt-versus-completeness-confirmation source ambiguity.

## Eligibility Assessment Contract
- Source endpoint:
  `POST /api/v1/loan-applications/{loan_application_id}/eligibility-assessment/run/`.
- Source read endpoint:
  `GET /api/v1/loan-applications/{loan_application_id}/eligibility-assessment/`.
- Source override endpoint:
  `POST /api/v1/loan-applications/{loan_application_id}/eligibility-assessment/override/`;
  override is not part of 006A/006B unless that slice explicitly says so.
- Response fields from §22.1 and `eligibility_assessments` §14.1:
  `eligibility_assessment_id`, `loan_application_id`, `member_active_check`, `default_check`,
  `document_check`, `terms_acceptance_check`, `purpose_check`, `nominee_check`,
  `overall_result`, `assessment_notes`, `assessed_by_user_id`, and `assessed_at`.
- Permission for run is `credit.eligibility.run`; override requires `credit.eligibility.override`.
- Endpoint map says eligibility can run only after the application is complete.

## 006A Active Member Slice Boundary
- Implement only the active-member portion of the eligibility assessment mechanism.
- Source active-member rules:
  - BR-004: individual active member must have availed services and supplied primary produce for
    four continuous financial years unless relaxation applies.
  - BR-005: recent individual member relaxation may apply after at least one year of supply to
    SFPCL/subsidiary/step-down subsidiary or through a producer institution.
  - BR-006: producer member service-based relaxation may apply after three continuous years of
    service in employment or other capacity to SFPCL/subsidiaries/step-down subsidiaries.
  - BR-007: producer institution must be a member, avail services, and supply primary produce for
    four continuous financial years unless one-year relaxation applies.
- Current persistence does not yet include enough historical produce/service rows for all variants.
  006A should implement the assessment storage/API and source-backed checks from existing member
  facts where available, and mark unavailable history as `relaxation`/manual-evidence-required only
  if the source-backed evidence is missing. Do not invent supply-history calculations.
- Active-member run must preserve 005C2 application object access and require formal `LO...`
  reference/completeness before appraisal eligibility starts.

## 006Z Produce Supply Persistence
- `produce_supply_records` follows data-model §11.6 and stores financial year, destination/route,
  optional crop/quantity/value/evidence facts, capture actor, immutable verification actor/time,
  and optimistic version.
- Capture uses `members.active_status.calculate`; verification uses
  `members.active_status.verify` with maker-checker separation. Rejected and stale verification
  attempts preserve record, history, and audit counts.
- BR-004 pass now requires services-availed evidence plus four continuous verified financial-year
  rows. Unverified, discontinuous, or absent rows require manual evidence; recorded relaxation
  remains independently reviewable.
- Portal supply is read-only and scoped only from active PortalAccount. Staff Member Profile and
  Borrower 360 project the same records; portal projections omit staff actions and member IDs.

## 006B Default, Document, Purpose, And Terms Checks
- Extend the 006A eligibility assessment to include:
  - BR-008: borrower must not be in default for any FPC loan of SFPCL, subsidiary, or associate.
  - BR-009: nominee must not be a minor.
  - BR-013/BR-014 and S15: land documents, borrower/nominee KYC, recent bank statement, and crop
    plan are mandatory checklist evidence.
  - BR-018 and S15: loan purpose must be crop production/agriculture activity only.
  - S15: borrower must agree to terms.
- Use existing 005D/005E checklist facts for document evidence where possible. Do not duplicate
  document-file storage or recalculate completeness from raw files.
- Normal ineligible results must not move the application into appraisal/sanction states. Rejection
  note generation remains the source-backed rejection-note mechanism from 005H or later appraisal
  rejection slices.
- Implemented in 006B:
  - `default_check`: `no_default` only for `Member.default_status = no_default`; existing or
    default-like statuses return `default_found` and make the assessment `ineligible`.
  - `document_check`: uses 005D/005E required checklist metadata; any blocking required item
    returns `incomplete` and makes the assessment `ineligible`.
  - `terms_acceptance_check`: `accepted` only for `LoanApplication.terms_acceptance_flag = true`;
    otherwise `pending` and `overall_result = ineligible`.
  - `purpose_check`: `agriculture_aligned` only for `crop_production` or `agriculture_activity`;
    other categories return `non_agriculture` and make the assessment `ineligible`.
  - `nominee_check`: uses `Nominee.loan_application_id` only when present. Adult nominees return
    `valid`; minor nominees return `minor` and make the assessment `ineligible`; missing
    application-specific nominee evidence remains `pending` with `overall_result =
    pending_manual_evidence`.
  - `overall_result = eligible` only when member-active, default, document, terms, purpose, and
    nominee checks all pass. Successful reruns update the existing one-to-one assessment.

## 006C Loan Limit Configuration And Calculator
- Source endpoint:
  `POST /api/v1/loan-applications/{loan_application_id}/loan-limit-assessment/calculate/`.
- Request fields from `api-contracts.md` §23.1:
  `shareholding_id`, `land_holding_ids`, `crop_plan_id`, `requested_amount`, and
  `calculation_date`.
- Response/persistence fields from §23.1 and `loan_limit_assessments` §14.2:
  `loan_limit_assessment_id`, `member_id`, `shareholding_id`, `number_of_shares`,
  `valuation_per_share`, `share_limit_percentage`, `per_share_cap_amount`,
  `shareholding_based_limit_amount`, `land_area_acres`,
  `scale_of_finance_per_acre_amount`, `land_based_limit_amount`,
  `final_eligible_loan_amount`, `requested_amount`, `amount_within_limit_flag`,
  `exception_required_flag`, `calculation_rule_version`, `calculated_by_user_id`, and
  `calculated_at`.
- Formula contract from `api-contracts.md` §23.2:
  `shareholding_based_limit = number_of_shares × configured percentage or per-share cap`;
  `land_based_limit = scale_of_finance_per_acre × land_area_acres`;
  `final_eligible_loan_amount = min(shareholding_based_limit, land_based_limit)`.
- Functional-spec BR-020 requires agricultural land-based limit from scale of finance and land area
  under cultivation. BR-021 requires final eligible amount to be lower of shareholding and
  land-based limits.
- If requested amount exceeds final eligible amount, set exception required and return a
  `REQUESTED_AMOUNT_EXCEEDS_LIMIT` warning.
- Source docs still list an open question for the operative shareholding rule: 30%, 10%, or
  Rs 200/share. 006C must use source-backed loan-policy configuration if present; otherwise block
  calculation or record the ambiguity instead of inventing the rule.
- Permission for calculation is `credit.loan_limit.calculate`; override requires
  `credit.loan_limit.override` and is out of scope for 006C.
- Implemented in 006C:
  - Calculation requires a stored 006B assessment with `overall_result = eligible`; absent,
    `pending_manual_evidence`, and `ineligible` paths return invalid state with no calculation
    evidence.
  - The request amount must match the persisted application request. Shareholding, every selected
    land holding, and crop plan must belong to that application member; application-mismatched or
    non-agriculture-aligned crop plans are rejected.
  - Exactly one active/effective Board-referenced `LoanPolicyConfig` is required. Missing,
    overlapping, non-positive, or percentage/cap-empty policies block calculation rather than
    selecting 30%, 10%, or Rs 200 in code.
  - Percentage produces a per-share amount from the stored valuation; configured per-share cap is
    a ceiling. Selected land acreage is summed and multiplied by configured scale of finance. The
    lower of share and land results is stored as the final amount.
  - Requested amount above the final limit returns `REQUESTED_AMOUNT_EXCEEDS_LIMIT` and sets both
    boundary flags. Equal/below amounts require no exception.
  - Successful calculation atomically snapshots all `data-model.md` §14.2 inputs/results, rule
    version, user, and time with `loan_limit.calculated` audit and `loan_limit_assessment` workflow
    evidence. Rerun updates the one-to-one row while denied/invalid/validation paths write none.

## 006D Immutable Loan-Limit Snapshot Readback
- Implemented `GET /api/v1/loan-applications/{loan_application_id}/loan-limit-assessment/` with
  `applications.loan_application.read` and the existing application object-access boundary.
  Missing applications/assessments return `404`; GET performs no calculation and writes no audit
  or workflow evidence.
- The persisted assessment includes policy config UUID, policy name, and Board approval reference
  snapshots. Calculate response, GET response, and audit old/new metadata serialize the policy
  source from those stored fields rather than the mutable `LoanPolicyConfig` row.
- All §14.2 numeric inputs/results, member/shareholding identifiers, requested amount, boundary
  flags/warnings, rule version, actor/time, and policy source remain unchanged on read when current
  application, shareholding, land/crop, or policy facts change.
- A successful rerun preserves the one-to-one assessment UUID, atomically replaces the stored
  snapshot, and records complete old/new snapshot audit metadata. Invalid-state, missing-source,
  permission-denied, and object-scope-denied reruns preserve the prior snapshot and create no
  success evidence.

## 006C2 Cultivated Acreage Source Hardening
- Source ambiguity A-049 remains open: functional-spec BR-020 requires land area under cultivation,
  while the model exposes selected `LandHolding.area_acres`, application `CropPlan.planned_area_acres`,
  and nullable `IndividualMemberProfile.land_area_under_cultivation_acres` without a precedence rule.
- Implemented safe interim behavior: calculation proceeds only when the normalized Decimal acreage
  values agree across total selected verified land holdings, the selected verified crop plan linked
  to the current application, and profile cultivated acreage when that profile value exists. `5`,
  `5.0`, and `5.00` compare equal.
- The calculate endpoint now rejects pending/rejected selected land holdings, pending/rejected crop
  plans, crop plans with null `loan_application_id`, crop plans linked to another application, and
  mismatched acreage evidence before any `LoanLimitAssessment.save()`, `loan_limit.calculated`
  audit, or `loan_limit_assessment` workflow event.
- Mismatch contract for 006D2/module extraction: `400 VALIDATION_ERROR` with
  `error.field_errors.cultivated_acreage = "CULTIVATED_ACREAGE_UNRESOLVED"`. A failed rerun leaves
  the existing one-to-one assessment UUID, serialized GET response, policy snapshot, acreage
  snapshot, audit count, and workflow-event count unchanged.
- Successful calculation stores the agreed cultivated acreage in `loan_limit_assessments.land_area_acres`
  and keeps the existing source-backed scale-of-finance multiplication and lower-of-two formula.

## 006D2A Credit Eligibility And Configuration Seams
- Eligibility read/run behavior now lives behind
  `credit.modules.eligibility_assessment.EligibilityAssessmentModule`; application views only
  authenticate/parse, call `get` or `run`, and translate the module result/errors.
- The module owns permission/object access, application and assessment locking, state validation,
  active/default/document/terms/purpose/nominee evaluation, one-to-one rerun persistence,
  metadata-only audit, workflow evidence, and the public eligibility snapshot.
- Eligible, ineligible, and pending-manual-evidence paths retain the 006A/006B contracts. A forced
  audit failure rolls back the assessment and workflow evidence in the same transaction.
- Effective Board-approved loan-policy selection/validation now lives only in
  `configurations.modules.configuration_resolver.resolve_effective_loan_policy`. The still-legacy
  loan-limit implementation calls it with row locking and translates its shared validation error;
  006D2B will remove that compatibility translation when it extracts the calculator.
- Application services no longer expose eligibility lookup/run/serialization/rule/audit helpers or
  a private policy resolver. Models remain in `applications.models` and existing tables/UUIDs are
  unchanged under ADR-0002; there is no migration.
- HTTP endpoints, response/error envelopes, permissions, object scope, explicit rerun semantics,
  loan-limit formula/snapshot behavior, frontend behavior, and API contracts are unchanged.

## Architecture Review 2026-07-10 15:46 - 006D2B Boundary Hardening
- 006D2A's direct module tests substantively cover eligible/ineligible/pending paths and transaction
  rollback, but the import-boundary regression uses runtime identity/`hasattr` checks and cannot
  reject aliased private imports. 006D2B must replace it with static AST/import-graph coverage for
  application views/services and the future appraisal seam.
- `configurations.modules.configuration_resolver` currently imports a credit-specific validation
  error. 006D2B must remove the reverse `configurations -> credit` dependency, keep the resolver's
  result/error configuration-owned or neutral, and translate at the credit calculator boundary.
- During calculator extraction, lock the application, current assessment, shareholding, selected
  land rows, crop plan, applicable cultivated-area profile, and effective policy in one transaction.
  Tests must patch the public resolver, assert `for_update=True`, and reject direct policy queries.
- 006C2's mismatch, verification, Decimal normalization, nullable-profile, and failed-rerun
  preservation tests are substantive and must move behind the module interface unchanged.

## 006D2B Loan-Limit Calculator And Appraisal Seam
- `LoanLimitCalculator.get_assessment/calculate_for_application` now own access, locking,
  validation, formula, rerun persistence, canonical redacted projection, audit, and workflow.
- Application views are thin adapters; `applications.services` exposes no loan-limit helpers.
- The configuration resolver owns its error type; calculator translation preserves HTTP errors and
  always resolves the effective policy with `for_update=True`.
- Calculation locks application, eligibility/current assessment, shareholding, selected land,
  crop plan, applicable profile, and policy in one transaction. Failed reruns preserve evidence.
- `AppraisalWorkflow` is the projection-only 006E entry seam; no appraisal rule was added here.

## 006D3 Credit Assessment Model Ownership
- `EligibilityAssessment` and `LoanLimitAssessment` Django model state now belongs to
  `credit.models`; the legacy physical tables remain exactly `eligibility_assessments` and
  `loan_limit_assessments`.
- The single reversible migration performs state transfer only. It emits no SQL and does not
  rename, recreate, copy, backfill, truncate, or drop either table.
- Forward and reverse migration-executor proofs preserve both primary-key UUIDs, application/member/
  shareholding/user relationships, and audit/workflow entity UUID references.
- The public behavior seam remains `EligibilityAssessmentModule`, `LoanLimitCalculator`,
  `LoanLimitAssessmentResult`, `LoanLimitSnapshot`, and `AppraisalWorkflow`; future appraisal code
  must not import the concrete assessment models.

## 006E Appraisal Note Draft And Submit
- `AppraisalWorkflow` now owns create/read/draft-update/submit-for-review. Application views are
  thin envelope adapters and import no concrete credit assessment models.
- Create requires scoped `credit.appraisal.create` plus `credit.risk_assessment.manage`, consumes
  only `EligibilityAssessmentModule.get(...).snapshot` and
  `LoanLimitCalculator.get_assessment(...).snapshot`, and stores their IDs with one linked risk
  assessment. Missing/non-eligible prerequisites are invalid state and write no success evidence.
- Strict payload rules cover non-blank summaries, positive amount/optional tenure, floating
  interest type, recommendation/risk enums, nested risk shape, unknown fields, and the rule that a
  recommendation may exceed the stored final limit only when the stored snapshot already carries
  `exception_required_flag = true`.
- PATCH is draft-only and supplied-fields-only. Risk permission is additionally required only when
  nested risk fields change. Submit requires non-blank remarks and transitions exactly once to
  `review_pending`; post-submit edits and repeated submit are blocked.
- `tat_due_at = application.created_at + 2 days` is immutable. Exact due time is within TAT;
  preparation/submission after it is breached. Create/update/submit evidence is metadata-only and
  excludes summaries, mitigation notes, and submit remarks.

## 006E2 Appraisal Source Contract And Snapshot Hardening
- Create now stores exact canonical redacted eligibility and loan-limit public projections on the
  appraisal with their same-UUID provenance IDs and `prerequisite_provenance = verified`.
- GET, draft PATCH amount/exception checks, submit, and future review/sanction consumers use only
  those frozen JSON projections. Replacing current assessment facts under the same UUID does not
  alter the appraisal response or its recommendation boundary.
- `repayment_capacity_notes` is a required non-blank appraisal fact. Submit persists trimmed
  §24.3 remarks on the appraisal; audit JSON records only reason existence and owner ID.
- The additive migration copies current projections only where assessment timestamps and success
  audit chronology prove no later rerun. Ambiguous rows remain `legacy_unverified` and cannot
  submit/review until the draft-only revalidation action pins current public projections.
- `POST /api/v1/appraisal-notes/{id}/revalidate-prerequisites/` accepts `{}`, requires appraisal
  update plus risk-management scope and object access, and preserves all caller-authored
  recommendation, repayment, summary, risk, preparer, and TAT facts. All mutation/evidence paths
  are atomic and metadata-only.

## 006E-006F Appraisal And Credit Review Source Extract
- `api-contracts.md` §24 defines appraisal create/read, submit-for-review, Credit Manager review,
  and submit-to-sanction as separate actions. 006E owns create/read/edit/submit-for-review; 006F
  owns review only; 006G owns sanction submission.
- §24.4 review request fields are `decision` and `review_comments`. The example decision is
  `reviewed`; test-plan MOD-APPRAISAL-005 additionally requires a returned review with reason.
- `data-model.md` §14.4 stores one appraisal per application with prepared/reviewed users and times,
  immutable TAT due/status, summaries, recommendation terms, linked risk assessment,
  recommendation, and appraisal status.
- `auth-permissions.md` assigns `credit.appraisal.review` to Credit Manager and separately assigns
  `credit.appraisal.submit_sanction`; review must not imply sanction authority. Test-plan
  MOD-APPRAISAL-007 requires maker-checker, so the preparer cannot review their own appraisal.
- A review return uses the source `draft` state to permit maker revision/resubmission while storing
  the returned decision/reason and evidence; `reviewed` is the terminal 006F state consumed by 006G.

## 006F Credit Manager Review
- `POST /api/v1/appraisal-notes/{id}/review/` accepts only `decision` and non-blank
  `review_comments`; 006F supports `reviewed` and `returned` while terminal rejection remains 006F2.
- `AppraisalWorkflow.review(...)` owns permission, Credit Manager object scope, row locking,
  maker-checker, state/provenance validation, review persistence, and atomic metadata-only evidence.
- `reviewed` moves `review_pending -> reviewed`; `returned` stores the reviewer/time/comments and
  decision while moving `review_pending -> draft` for maker revision and explicit resubmission.
- Review requires `credit.appraisal.review`, a different user from `prepared_by_user`, and verified
  frozen prerequisite provenance. Preparation/submit permissions do not imply review authority.
- Review never queries current eligibility/loan-limit rows or invokes prerequisite revalidation.
  Same-UUID current-assessment changes cannot alter the frozen appraisal projections,
  recommendation, repayment/submission facts, risk assessment, or TAT.
- Successful decisions write `appraisal.reviewed`/`appraisal.returned` audit and workflow evidence;
  free-text review comments and financial/risk projections remain only on the appraisal row.

## 006F2 Credit Manager Appraisal Rejection
- `AppraisalWorkflow.review(...)` accepts terminal `rejected` only from `review_pending` under the
  same review permission, Credit Manager object scope, maker-checker, verified-provenance, and row
  lock as 006F. Existing `reviewed` and `returned` behavior is unchanged.
- The rejected request adds the source 005H note fields `rejection_reason_category`,
  `detailed_reason`, `reapply_allowed_flag`, and `communication_mode`; the workflow-owned stage is
  fixed to `credit_assessment`. Missing/invalid/unknown facts write nothing.
- Rejection atomically stores reviewer/time/comments/decision, sets terminal appraisal state
  `rejected`, and calls the public applications rejection-note seam to create exactly one existing
  draft with derived `communication_status = not_sent`. It neither sends communication nor creates
  a sanction case.
- Appraisal evidence records only IDs/category/state/actor/time/request ID. Review comments and the
  detailed rejection reason are excluded; rejection-note validation/serialization/audit/workflow
  remain owned and reused from 005H. Any note or evidence failure rolls back the whole decision.
- Rejection consumes no current eligibility/loan-limit model. The frozen projections,
  recommendation/terms, repayment/submission facts, linked risk assessment, and TAT remain unchanged.

## Architecture Review 2026-07-10 19:15 - Appraisal Historical And Concurrency Corrections

- Migration 0003's legacy “safe copy” is not conservative enough: it requires no later success
  audit but does not require positive pre-appraisal success audits for both exact prerequisite IDs.
  006E3 must downgrade every unproven row to `legacy_unverified`; absence of evidence is not proof.
- Source auth §25.3 requires both `credit.appraisal.review` and actual Credit Manager role authority.
  Generic owner/receiver object access must not let another role exercise review merely because it
  was granted the permission.
- Latest `LoanAppraisalNote.review_comments` cannot serve as review history. A return reason is lost
  when a later review overwrites it, while metadata-only audit intentionally excludes the text.
  ADR-0004 and 006E3 require one immutable appraisal-owned decision record per review action.
- 006D2C merged without its mandatory PostgreSQL execution: committed evidence contains only a
  missing-driver failure and SQLite skips. 006F3 must execute those existing tests on PostgreSQL,
  normalize application → appraisal → rejection/history lock order, and add competing appraisal
  review/rejection outcomes before 006G.
- The top-level API-contract appraisal status and the older requirement-status paragraph in this
  digest are stale beside the later implemented 006F/006F2 sections. 006E3 owns reconciliation.

## 006E3 Appraisal History And Review Authority Hardening

- `AppraisalWorkflow.review(...)` now requires both `credit.appraisal.review` and active
  `credit_manager` primary-role membership before object scope. Another-role permission holders,
  including in-scope application owners/receivers, receive `PERMISSION_DENIED` with no writes. A
  real Credit Manager retains all-applications access inside the credit-assessment domain and the
  distinct `OBJECT_ACCESS_DENIED` result outside it.
- Every successful reviewed/returned/rejected action appends one appraisal-owned immutable review
  decision in the same transaction as latest appraisal projections, optional rejection note,
  audit, and workflow evidence. API `review_history` is chronological and retains decision,
  comments, reviewer/time, from/to states, and `native|legacy_latest_only` provenance. Generic
  evidence references the history UUID but excludes comments, detailed rejection reason, and
  frozen financial/risk free text.
- Migration 0005 keeps a legacy appraisal `verified` only when both exact same-application
  prerequisite UUIDs have their matching success audits at/before preparation, neither has a later
  success audit, and both source timestamps are at/before preparation. Every other formerly
  verified row is relabelled `legacy_unverified` without rewriting copied JSON or decision facts.
  Existing unverified rows stay unverified; explicit draft revalidation remains the repair path.
- The migration backfills at most one complete latest known legacy review decision and labels it
  `legacy_latest_only`; it never fabricates prior cycles. Reverse schema migration drops this
  derived table but deliberately does not relabel unproven prerequisites as verified.

## 006F3 Lock-Order Candidate And Unmet Acceptance (2026-07-10_195330)

- The implementation candidate centralizes appraisal mutation locking inside `AppraisalWorkflow`:
  application first, appraisal second, then existing immutable history and optional rejection-note
  work. PostgreSQL `FOR UPDATE OF self` limits locks to the intended rows when nullable related
  users are joined for authorization/serialization.
- PostgreSQL-only public-interface tests now describe rejected-review versus stale draft PATCH and
  duplicate terminal review races. They require deterministic serialization, one native terminal
  history row, one optional rejection note, matching audit/workflow history UUIDs, preserved
  pre-race history, and no loser success evidence.
- This run is not acceptance evidence: the live PostgreSQL 14 server socket was visible but the AFK
  sandbox denied connection with `Operation not permitted`; an in-sandbox cluster also could not
  allocate PostgreSQL's required SysV bootstrap segment. The combined loan-limit/appraisal command
  found four tests but executed none. 006F3 must remain incomplete and rerun in an environment that
  permits the PostgreSQL connection; SQLite skips and the otherwise-green standard gates do not
  satisfy the slice.

## Architecture Review 2026-07-10 04:18 - 006A Spot Check
- 006A implemented only the active-member portion of the eligibility assessment contract and left
  default, document, terms, purpose, and nominee checks pending for 006B as planned.
- The review verified 006A preserves the formal `LO...` reference, complete-documentation, and
  credit-assessment state guard; `credit.eligibility.run`; existing application object access; and
  no-success-evidence behavior on denied/invalid paths.
- Full review-run gates passed with 277 backend tests, 95% backend coverage, 95 frontend tests,
  frontend lint/typecheck/build, backend check, migration sync, and `git diff --check`.

## Architecture Review 2026-07-10 09:32 - 006B-006D Contract And Module Review
- 006B's default/document/terms/purpose paths and 006C/006D's permission, object-scope,
  lower-of-two, below/equal/above boundary, policy ambiguity, snapshot read, and failed-rerun tests
  contain substantive assertions and preserve no-success-evidence guarantees.
- Application nominee authority is not reachable through public APIs: source §19.2's `nominee_id`
  is absent from `LoanApplication`, while 006B reverse-queries nullable legacy rows and chooses the
  first. `005I3` must establish one stored selection, use it for 006B, and keep missing/ambiguous
  evidence pending rather than eligible.
- BR-020 names acreage under cultivation, but 006C uses the total of selected owned
  `LandHolding.area_acres` and only validates crop-plan ownership/alignment. `006C2` must block when
  selected-land, crop-plan, and applicable profile cultivation acreage disagree; A-049 records the
  source ambiguity so the corrective slice does not invent a selector formula.
- Eligibility, loan-limit calculation, configuration resolution, persistence, serialization, and
  audit projection now sit in `applications.services` (2,789 lines), contrary to the source-named
  `credit.modules.eligibility_assessment`, `credit.modules.loan_limit_calculator`, and
  `configurations.modules.configuration_resolver` seams. `006D2` must establish those deep module
  boundaries before 006E adds appraisal behavior.
- Explicit successful reruns currently replace the one-to-one loan-limit snapshot while preserving
  its UUID and complete old/new audit metadata. The source one-to-one data model and reviewed slice
  require that behavior; passive policy/source changes do not alter GET. Treat versioned recalculation
  as a watch item and prohibit future appraisal code from bypassing stored snapshots.
- Epic 006 remains incomplete. M04-FR-004 through M04-FR-011 are implemented through 006E3 except
  sanction submission itself, which remains 006G; M04-FR-001/M04-FR-002 remain explicitly owned by
  012EA under A-053, and M04-FR-003 keeps the A-054 receipt-time proxy pending source confirmation.

## 006G Submit To Sanction

- `POST /api/v1/loan-applications/{id}/submit-to-sanction-committee/` accepts exactly non-blank
  `remarks` and requires active Credit Manager authority, the independent
  `credit.appraisal.submit_sanction` permission, and credit-domain object scope.
- The application-first transaction locks application, appraisal, ordered immutable review rows,
  then the approval-case namespace. Submission requires reviewed state, verified complete frozen
  prerequisite projections, complete risk/appraisal facts, and a latest immutable review row that
  exactly matches every latest appraisal review projection.
- Success creates one unique pending approval-case shell, copies the frozen exception-required
  flag for later Epic 007 routing, and transitions application/appraisal status to
  `submitted_to_sanction_committee`. It preserves all recommendation, risk, TAT, prerequisite,
  reviewer/comment, history, and rejection-note facts.
- Approval-matrix selection, approver assignment/actions, exception decisions, meetings,
  documents, communication, and sanction decisions remain Epic 007. A-059 requires 007B to enrich
  the existing unique case instead of creating a duplicate.
- Metadata-only audit/workflow evidence contains application/appraisal/case/latest-review IDs,
  states, actor/time, request ID, and exception flag; it excludes request remarks, comments,
  summaries, detailed rejection text, and risk notes.
- The SQLite functional suite covers strict validation, permissions/scope, invalid/rejected/
  missing/repeated/inconsistent states, rollback, and preservation. A PostgreSQL-only competing
  submission test exists; AFK sandbox socket denial is environment evidence, not concurrency proof.

## 006G2 Sanction Handoff Module And Read Contract

- `approvals.modules.sanction_handoff.SanctionHandoffModule` is the sole pending-case create/get/
  serialization seam. Credit retains appraisal validation and the application -> appraisal ->
  immutable-history locks, then calls the approvals interface; it no longer imports the concrete
  approvals model.
- POST and authenticated object-scoped `GET /api/v1/loan-applications/{id}/sanction-case/` return
  the same case/application/appraisal/latest-review/workflow UUIDs, canonical statuses,
  exception flag, actor/time, and empty pre-007 action list. Remarks and frozen free text are absent.
- Malformed/non-object JSON is a standard `400 VALIDATION_ERROR`; missing cases are `404 NOT_FOUND`;
  denied scope retains `403 OBJECT_ACCESS_DENIED`. Case, audit, or workflow failure rolls back the
  full handoff transaction, and repeated submission remains `409 INVALID_STATE_TRANSITION`.
- The exact 006F4 five-race PostgreSQL command passed twice with five executed tests, zero skips,
  and the existing application-first serialization order after the module extraction.

## 006H Frontend Integration
- The workbench and Application Detail credit tab now read stored eligibility, limit, appraisal,
  immutable history, rejection summary, and pending sanction response through §22-§24 APIs.
- Canonical `/auth/me` permissions plus exact server states gate actions; standard errors surface.
- Decimal inputs remain strings, sanction sends exactly `{ remarks }`, and frontend formulas and
  appraisal `mockData` ownership are removed. Browser screenshots remain 006X host evidence.

## Architecture Review 2026-07-10 21:39 - 006E3 Through 006H Corrections

- Migration 0005 conservatively downgrades unproven prerequisite provenance in every appraisal
  state, but the repair action is draft-only. `review_pending` and `reviewed` rows can therefore be
  blocked forever. It also misses a known returned decision when a later submit has moved the row
  back to `review_pending`. 006E4 owns state-aware remediation and latest-known history backfill;
  A-061 records the conservative re-review rule.
- The authoritative loan-limit/appraisal PostgreSQL command found four tests and executed none,
  while 006G's sanction race found one and executed none. 006F4 must run all five tests twice with
  zero skips; connection or sandbox failure remains failed acceptance.
- 006G creates its concrete approval row from the credit module, reversing the documented
  `approvals -> credit` dependency. ADR-0005 and 006G2 put create/read/serialization behind the
  approval-case module interface, retain the same unique row for 007B, return canonical statuses,
  and make the pending case UUID recoverable after reload.
- 006H assigns the full appraisal response to the edit form, so PATCH sends response-only IDs,
  snapshots, review history, status, and TAT into a strict writable contract. Returned/existing
  drafts cannot save. Revalidation is gated by submit permission rather than update+risk authority,
  and local code synthesizes post-sanction statuses. 006H2 owns writable projection, server
  actions/state, reload, and real container interaction tests.
- 006H replaced the approved staged workbench/checklist/calculator composition with a new condensed
  layout without screenshots. 006H3 restores the pre-006H visual composition using real data and
  requires host visual regression; missing browser evidence is not deferrable there.
- Functional-ID spot check: M04-FR-004 through M04-FR-009 have substantive backend assertions;
  M04-FR-010/M04-FR-011 behavior exists but remains High-risk until 006E4/006F4/006G2 close repair,
  concurrency, and sanction-handoff defects. M04-FR-001/M04-FR-002 remain explicitly deferred to
  012EA by A-053. M04-FR-003 remains the explicit A-054 receipt-time proxy. Epic 006 is not complete.

## Architecture Review 2026-07-12 12:52 - Credit Matrix and Supply Evidence Corrections

- 006X4's new test projects five appraisal actions but executes only one missing-permission update
  denial. 006X5 must run the promised public enabled/write-success and disabled/write-denial matrix
  for eligibility, limit, appraisal create/update/revalidate/submit, all review decisions, and
  sanction, plus the PostgreSQL stale-projection race.
- BR-004/BR-007 require actual service evidence and qualifying continuous supply. A legacy active
  flag/timestamp cannot substitute for `services_availed_flag=false`, and only S16-eligible entity/
  route rows may count.
- Active-member calculation belongs behind `members.modules.active_member_status`; credit must not
  import `ProduceSupplyRecord` or own/test private continuity helpers.
- 006Z3 owns canonical financial-year, entity/route, reference, decimal, member-version, optimistic
  capture, and shared portal/eligibility continuity validation. 006Z2 must wait for 006Z3 so portal
  limits cannot project from invalid eligibility evidence.

## 006Z3 Active-Member Supply Evidence Boundary

- `members.modules.active_member_status.ActiveMemberStatusModule.calculate` is the public immutable
  BR-004/BR-007 projection. Credit and portal consumers share it; credit no longer imports supply
  persistence or owns/tests a private continuity helper.
- Normal pass requires persisted profile service usage plus four continuous verified rows with
  canonical `YYYY-YY`, SFPCL/subsidiary/step-down entity, consistent direct/eligible active Producer
  Institution route, and evidence reference. A legacy active flag/timestamp is never service proof;
  recorded relaxation remains manual evidence.
- Capture is object/known-field strict and locks the current member version. Entity/member UUID
  relationships, non-negative bounded-precision decimals, and evidence reference are validated;
  stale/competing capture yields one record/history/audit winner. Verification retains its separate
  record-version maker-checker lock.
- Portal totals/status/continuity derive only from qualifying rows while every row remains visible.
  006Z2 must consume this public result and treat non-qualifying continuity as unavailable, not zero.
