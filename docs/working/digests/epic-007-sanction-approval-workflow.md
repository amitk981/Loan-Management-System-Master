# Epic 007 Digest: Sanction Approval Workflow And Registers

## 007H3 Frozen Case Provenance and Read-Scope Parity Closure

- Credit-owned enrichment remains the only point that validates the locked appraisal and complete
  loan-limit source. The approval case freezes all required provenance plus `review_facts`; canonical
  validity no longer compares an existing cycle with the mutable live appraisal snapshot or its
  assessment-id field.
- The explicit coherence/reader projection is database narrowing only. Every narrowed candidate now
  crosses the same approval-owned frozen-validity and actor-scope decision before case/register
  filters, counts, page normalization, or serialization. Detail, action, sanction decision, and
  Credit Sanction Register therefore agree even when a stale true projection/index survives a
  direct malformed save.
- Direct live appraisal edits leave pending reads/actions and terminal detail/decision/register
  responses unchanged. Return -> correction -> fresh review preserves cycle 1 provenance and review
  facts byte-for-byte while cycle 2 exposes only its newly frozen corrected facts. No model-save
  signal or cross-table side effect was restored.

## Architecture Review 2026-07-13 22:42 - Frozen Provenance and Read Parity

- 007F2 removed the appraisal save signal, but canonical case validity still compares frozen
  `loan_limit_provenance_json` to the mutable live appraisal snapshot. A public probe changed only
  live `policy_name` and made case detail return 404 while the stored projection remained coherent.
- On a terminal cycle after the same live edit, 007H2 still returned the sanction decision and one
  register row through its stored read projection while canonical case detail returned 404. `007H3`
  makes frozen case facts the sole validity input and aligns detail/action/decision/register scope
  before counts and pagination without restoring signals.
- M05-FR-003/006/009/012 remain functionally substantive; 007H3 closes historical-cycle and
  cross-endpoint authority consistency. 007I depends on it and must render old/new cycles only from
  their server-frozen projections.
- Auth §19.4 names no finer role/sensitivity pairs for Legal documents. A-085 therefore remains the
  explicit rule: every source-defined sensitivity is eligible only inside the exact legal audience,
  application provenance, related-party workflow, case scope, and permission boundary. Do not
  invent a narrower compliance matrix without governed configuration.

## 007H2 Sanction Decision and Register Object-Scope Closure

- Sanction-decision reads now require both `approvals.sanction.read` and the approval-owned
  coherent-case/read-index decision. Same-permission unused Directors receive nondisclosing
  `OBJECT_ACCESS_DENIED`; original, effective, conflicted, and acted historical actors retain only
  their attributable cycle. The pre-approval/post-rejection 404 contract is unchanged.
- Credit Sanction Register rows are joined to the canonical actor-scoped case selector before FY or
  decision filters, ordering, counts, page normalization, and serialization. Two unrelated
  Directors therefore receive independent one-row totals, while an active persisted legal/audit/
  management grant can expose its defined read-only case scope only alongside the specific register
  permission.
- Permission, object scope, and downstream authority remain separate: case scope alone cannot read
  the decision/register, register visibility grants no case action or document authority, and
  coherence flags/exception rows/meeting metadata never act as authority. Frozen sanction reasons
  remain distinct from Exception Register business reasons.

## 007G2 General-Meeting Current Evidence and Document Scope Closure

- An evidence-required pending case now projects the current unsuperseded application outcome in
  canonical collection, detail, action, and gate-error shapes with `evidence_scope = current_pending`.
  Reject, return, conflict-blocked abstention, and final approval freeze the then-current row;
  historical readers expose only that row with `evidence_scope = cycle_frozen`, so later
  supersession cannot rewrite a cycle.
- The General Meeting module no longer reads `DocumentFile`. One documents-owned reference
  interface requires public-upload provenance, exact application attribution, legal category,
  a matching source-defined sensitivity, global document permission, and a typed attributable
  related-party-case workflow context for each notice/minutes/resolution id. The source §19.4 legal
  audience is enforced separately from generic/audit-only case read. Every denial is per-field
  nondisclosing and zero-write, including no download audit.
- The real 007F2 above-limit submit/enrich/read/three-approver tracer now records pending, rejected,
  and approved meeting outcomes through public document and §25.11 endpoints. Supersession preserves
  the sanction reason, distinct exception business reason/register identity, and queue visibility.

## 007F2 Exception Routing Coherence and Explicit Projection Closure

- Non-forced exception routing now derives from coherent frozen facts: reviewed amount above the
  frozen final eligible amount and `exception_required_flag = true`. Below/equal-plus-true and
  above-plus-false snapshots return the stable 409 invalid-state contract with zero enrichment
  writes. Explicit forced within-limit stage-bypass/waiver routing remains supported.
- The sanction case's `reason_for_approval` and Exception Register's `business_reason` are distinct
  source facts. The latter is frozen as case `exception_reason`; coherence requires the same-case
  entry, matching application/reason, truthful type/risk shape, frozen amount-limit predicate,
  exception matrix condition, two Directors, and Exception Register requirement—not reason equality.
- A public above-limit tracer now covers submit, enrich, ordinary/assigned list, detail, CFO plus
  two Director actions, Exception Register closure, sanction decision, and terminal Credit Sanction
  Register without manually attaching register evidence. Replay/mismatch cases preserve the first
  immutable snapshot.
- Approval coherence and reader indexing have one explicit approval-owned projection interface.
  The appraisal `post_save` receiver is removed; direct case/appraisal saves cannot mutate another
  table, and later live appraisal changes cannot rewrite historical-cycle projection authority.
- M05-FR-003 and M05-FR-006 are now substantive through the public workflow. M05-FR-009 generation
  remains substantive; its read confidentiality is still owned by 007H2.

## Architecture Review 2026-07-13 20:10 - Exception and Evidence Read Corrections

- 007F persists the distinct Exception Register business reason on the case, but the inherited
  coherence predicate still requires it to equal `reason_for_approval`. A real public exception
  enrichment is therefore saved incoherent and disappears from case reads/actions; later tests
  bypass that route with manually attached register fixtures. `007F2` restores the full public
  submit/enrich/read/CFO+two-Director/terminal-register tracer and removes the remaining appraisal
  post-save projection side effect.
- The non-forced exception path trusts a frozen boolean even when the recommended amount is below
  the frozen eligible amount. `007F2` requires amount/flag agreement and reserves within-limit
  routing for explicit `force_exception_route` with a truthful type/reason.
- 007G freezes the applicable meeting on return/final approval, but pending/rejected current
  evidence is null on case detail. It also checks only a global document permission plus existence.
  `007G2` defines current-while-pending/frozen-when-closed projection semantics and delegates each
  evidence reference to document-owned application/sensitivity scope.
- 007H generates complete immutable rows, but sanction decision/register reads apply permission
  without case/application row scope. `007H2` filters direct reads and collection counts/pagination
  through the canonical original/effective/acted plus persisted legal/audit/management scope.
- M05-FR-011 is substantive. M05-FR-003/006 remain partial until 007F2; M05-FR-012 remains partial
  until 007G2; M05-FR-009 generation is substantive but confidential reads remain partial until
  007H2. The UI slice 007I now depends on those corrections.

## 007H Credit Sanction Register

- Approved and rejected terminal actions now create exactly one immutable case/cycle register row
  inside the existing locked approval transaction. Approved rows link the sanction decision;
  rejected rows retain a null sanction link/amount. Partial, returned, conflict-blocked, and
  general-meeting-denied outcomes create none. The row references the terminal sanction workflow
  event and has attributable creation audit evidence.
- The 15-field projection freezes application/member, verified loan-limit, reviewed appraisal,
  effective authority/action, same-case 007F exception, frozen 007E exclusion/abstention, and
  case-frozen 007G meeting evidence. It never selects the latest exception/meeting by application,
  and metadata ids do not grant document downloads.
- §25.8 sanction-decision GET requires `approvals.sanction.read` and returns 404 before approval or
  after rejection. §25.9 register GET requires `approvals.sanction_register.read`, standard bounded
  pagination, exact decision values, and A-086 April-March `FYyyyy-yy` filtering. There is no
  mutation route. Annexure K/template code remains absent under unresolved OC-002/A-087.

## 007G General-Meeting Evidence

- The §25.11 endpoint records immutable Director/relative/committee-member evidence with notice,
  minutes, and resolution document references. Recorder authority is the Critical record grant
  plus canonical case scope and existing document-read permission. Exact replay is zero-write;
  changed evidence creates a one-to-one superseding row with attributable audit/workflow history.
- The final sanction gate runs only after conflict, assignment, version, and distinct effective
  authority. Missing/pending/rejected current evidence has dedicated 409 contracts and inserts no
  final action, sanction, communication, or Exception Register outcome. Non-related cycles are
  unchanged and conflict denials retain their earlier canonical contract.
- Successful final approval freezes the approved meeting record on that exact case/cycle. Return
  freezes the then-applicable record without requiring approval, so later application supersession
  cannot rewrite historical cycles. Canonical collection/detail/action projections add the meeting
  object beside unchanged route/effective/action authority facts.

## 007F Exception Approval Workflow

- Exception enrichment requires a distinct business reason, optional risk assessment, and the
  Critical system-generation permission. One immutable entry is keyed to each case/cycle;
  ordinary routes create none and exact replay is zero-write.
- Vocabulary is bounded to `exceeds_loan_limit`, `stage_bypass`, and `waiver`. Entry status is
  pending/approved/rejected; approval/rejection project atomically from the locked case action.
  Returned and conflict-blocked closed cycles retain pending because §15.7 names no fourth status.
  A forced within-limit caller must state stage-bypass or waiver so it cannot be mislabeled as a
  frozen loan-limit breach; replay includes exact optional risk text.
- The read-only register delegates to the corrected original/effective/acted selector before
  count/pagination and returns cycle linkage plus canonical route/replacement/action history.
  Creation/status projection write attributable audit and workflow evidence.
- Credit Manager receives the system-generation grant needed by enrichment; CFO, Director, and
  Internal Auditor receive the source-backed generated-register read permission.

## 007E2 Conflict Authority, Projection, and Scope Closure

- Conflict replacement now fills exact frozen CFO/Director slots with distinct users; excluding
  either Director on a two-Director route cannot reuse the survivor and instead produces the exact
  conflict-blocked, no-sanction ledger.
- Immutable `required_approvers_json` remains route provenance. Canonical reads expose unchanged
  `route_approvers`, executable `required_approvers` with replacement attribution, and every
  immutable `approval_actions` row identically across collection/detail/action/history.
- One explicit approval-owned projection updater owns coherence and exact reader actors for case
  creation, workflow linkage, enrichment, actions/abstention, appraisal refresh, and migration.
  Ordinary model saves have no hidden cross-table workflow behavior.
- Reader SQL includes only original/effective/acted cycle participants. Unused committee alternates
  disclose neither counts nor rows; COI-005 is applied only after attributable base scope.
- General-meeting detection scans active borrower/Director-relative declarations independently of
  case assignment, while exclusions remain limited to frozen candidates. Whitespace-only reasons
  are rejected by database constraint.

## 007E Conflict-of-Interest Blocking

- `approvals.modules.conflict_of_interest` evaluates typed persisted borrower/Director-relative/
  material-interest declarations plus frozen application/appraisal maker facts for one immutable
  case cycle. Enrichment freezes unique reasons and the general-meeting-evidence flag without
  rewriting ordered required authority history.
- Exclusions are an eligibility overlay. A same-role alternate comes only from the frozen committee
  projection and the original matrix count remains binding; an unavailable CFO/Director slot closes
  the case as `blocked_by_conflict` without sanction creation.
- Excluded actors receive limited history/detail read, never queue/action scope. Approve/reject/
  return use exact `CONFLICTED_APPROVER_NOT_ALLOWED` details and add only a cycle-attributed COI-006
  denial audit.
- `POST .../abstain/` records mandatory reasoned `abstained` action history, exclusion, version
  increment, and either frozen-alternate reassignment or a communication-backed blocked outcome.
  Returned-cycle exclusions/actions never leak into a later recomputed cycle.

## Architecture Review 2026-07-13 17:04 - Conflict Authority and Scope Corrections

- 007E's replacement loop can reuse the same Director for an excluded slot and that Director's
  original slot. The length-only satisfiability check then accepts CFO + one distinct Director for
  a rule requiring CFO + two Directors. `007E2` requires exact distinct role/user cardinality and a
  conflict-blocked no-sanction outcome when the frozen candidate set cannot fill it.
- The canonical detail/action projection joins actions only to original
  `required_approvers_json`; a successful frozen alternate therefore disappears from history while
  the excluded original appears undecided. `007E2` preserves immutable route provenance and adds
  explicit replacement/action history shared by collection, detail, action, returned cycles, and
  downstream registers.
- The read helper index currently contains every committee candidate. An unused second Director can
  receive `total_count: 1` before the Python object check removes the row, and a declaration can
  grant that unused actor conflict-limited detail. `007E2` backfills an exact read projection and
  applies COI-005 only after attributable original/effective/acted cycle participation.
- Source auth §16.2 and API/data-model §25.11/§15.8 require general-meeting evidence for Director,
  relative, and Sanction Committee member borrowers. The flag must see a related Director/member
  even when they are outside this case's assigned approvers; material-interest or maker-checker
  conflict alone does not trigger it.
- M05-FR-007/008/010 remain substantive. M05-FR-011 is partial/unsafe until 007E2 closes distinct
  authority and public history; M05-FR-009 remains 007H and M05-FR-012's evidence gate remains 007G.

## 007D3 Returned Approval Cycles

- Approval cases are numbered immutable cycles per application. The database enforces positive
  cycle/revision values, unique application + cycle, and at most one pending application cycle;
  legacy rows migrate deterministically to cycle 1 with their matched immutable review and frozen
  review-fact projection.
- Return closes the current cycle and moves the appraisal to editable draft. Only actual appraisal
  value changes produce a non-empty correction ledger; a fresh independent Credit Manager review
  must follow that correction.
- The existing sanction-handoff boundary creates cycle N+1 only after a returned prior cycle, a
  newer corrected revision, and a post-return matching reviewed decision. Other prior outcomes,
  no-op correction, stale review, and duplicate/concurrent attempts create no new cycle evidence.
- Enrichment freezes each cycle's own appraisal/configuration facts. List/detail/action projections
  expose `cycle_number`; returned history stays readable but unassigned/non-actionable, and prior
  approver actions never satisfy the next cycle.
- Final approval remains application-unique and links only to the latest cycle. Same approvers may
  make new immutable decisions in a later cycle without changing cycle 1 ledgers.

## 007C3 Source Read-Scope Closure

- `approvals.case.read` is now seeded for Credit Manager, Company Secretary, and Internal Auditor,
  but it remains only the action permission gate. Object scope comes from the immutable approver
  snapshot, the existing Credit Manager application object-access decision/case submitter, or one
  active persisted role grant.
- `ApprovalCaseReadScopeGrant` permits only `legal_readonly`, `audit_readonly`, or
  `management_readonly`, with unique role/scope pairs and active-role/active-grant enforcement.
  Defaults seed only Company Secretary legal read-only and Internal Auditor audit read-only.
- One attributable `can_read_approval_case` decision is used by list, detail, and actions. Persisted
  readers can inspect routed packages but never enter assigned queues, enable actions, or write any
  case/action/sanction/audit/workflow/notification evidence.
- The approval-owned selector applies role/credit/immutable scope in SQL. A save-maintained
  coherence projection (refreshed when the owning appraisal changes) allows exact database count
  and pagination before page serialization; detail/actions still revalidate the complete live
  immutable snapshot. Permission-only readers and unassigned Directors remain empty-list/403.

## Architecture Review 2026-07-13 13:16 - Read Scope, Action Race, and Cycle Closure

- 006Z15 closes the real member public-action matrix; 007A6 closes exact winner evidence in all
  four twice-run PostgreSQL configuration races. No new material gap was found in either slice.
- 007C2 correctly denies arbitrary permission holders and unassigned Directors, but it also denies
  the source-required Credit Manager, Company Secretary, and Auditor sanction-package reads and
  scans all eligible cases before Python scope filtering. `007C3` adds persisted read-only scope
  separate from action permission and a bounded selector.
- 007D's sequential approve/reject/return behavior is substantive, but collection omits action
  history, its mandatory final-action PostgreSQL race was never implemented, application/appraisal
  transitions bypass shared guard acceptance, and terminal notifications bypass the 003I
  communication boundary. `007D2` closes those claims through one public action matrix and two
  twice-run PostgreSQL races.
- A returned case is a permanent dead end because approval cases are one-to-one and sanction
  handoff rejects any existing case. Data-model cardinality and codebase-design §13.1 require a new
  immutable approval cycle after correction/fresh review; `007D3` owns that lifecycle.
- M05-FR-001..006 are substantive. M05-FR-007/008 remain partial on parity/race/cycle acceptance;
  M05-FR-009 stays with 007H; M05-FR-010 is partial until 007D2 crosses the communication adapter.

## 007D Approval Action Boundary

- Approve/reject/return execute through one locked application -> appraisal -> case transaction and
  re-run 007C2 routability, object scope, pending assignment, permission, and optimistic version
  checks before the immutable action insert.
- Every action increments the case version and returns the canonical detail projection. Partial
  approvals stay pending; final joint approval creates the unique sanction decision and advances
  the application. Reject and return close the case without sanction; return restores the reviewed
  pre-committee state.
- Action audit/workflow evidence carries actor, decision/comments, request, case/application, IP and
  user-agent facts. Terminal outcomes notify the `credit_assessment` team. Register generation
  remains 007F/007H.
- The reviewed appraisal does not yet own numeric rate/repayment/charge/condition facts, so A-079
  preserves nullable/empty §25.8 fields rather than inventing financial rules.

## 007D2 Approval Action Boundary Closure

- Collection, detail, and action success now compose one history-aware approval-case projection;
  immutable route provenance remains unchanged while decision/acted-at and caller actions reflect
  the immutable action ledger immediately.
- One canonical §44 availability decision drives detail and writes for acted, excluded, closed,
  and action-permission states. Unassigned/object-scope and contradictory-snapshot nondisclosure
  remain outside that decision and preserve their existing 403/404 contracts.
- The locked application -> appraisal -> case transaction evaluates all three owner transitions
  through the shared guard before inserting an action. Reject/return comments remain mandatory;
  approve comments remain optional; every ordinary denial is exact zero-write.
- Terminal outcomes call the communication-owned internal team adapter. The action transaction
  persists one pending §24.2 Communication, one linked Credit Assessment notification, and one
  metadata-only communication audit; any adapter failure rolls the entire outcome back.
- PostgreSQL acceptance races different remaining actors on one version and duplicates the final
  actor on one version. Both races passed twice with one serial winner, a stable stale loser, one
  action per actor, no deadlock, and exactly one final sanction/communication/notification.

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

## 007C2 Read Scope and Snapshot Contract Closure

- `approvals.case.read` is necessary but never global object scope. The ordinary list is filtered
  before pagination/counts to immutable snapshotted actors, including their acted history;
  `assigned_to_me=true` is the narrower pending/unexcluded/unacted queue. Unassigned Directors,
  makers, and arbitrary permission holders see zero rows and direct detail returns
  `OBJECT_ACCESS_DENIED` without writes.
- One public approval-owned coherence predicate reconciles case/application/type/amount/decision/
  exception facts, rule and committee identity/version/date, exact unique CFO/Director authority,
  role/count/joint/register facts, and frozen assessment/application/policy provenance. Malformed
  or injected snapshots are neither listable, retrievable, nor eligible for later actions; live
  configuration and membership remain irrelevant.
- Exact enrichment replay now compares the locked reviewed date/recommendation plus assessment,
  application, exception, calculation-rule, policy-id/name, and calculation-time provenance. A
  changed fact returns 409 with unchanged case/action/audit/workflow evidence.
- §25.2 now includes `current_status`; enrichment, list, and detail compose the same canonical
  immutable routing projection. A real submit → enrich → canonical-read case remains byte-for-byte
  stable across rejected and later approved governed configuration proposals, including exact
  winner evidence and loser-evidence omission.

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
