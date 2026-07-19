# Epic 009 Digest — SAP, Loan Account, and Disbursement

## 009L5 Architecture Review Closure

- Architecture review `2026-07-19_123045_architecture_review` proves the 009L4 database selectors
  are broader than their owner-level projectors. Creation-role, completion-digest, send-checksum,
  and initiation-evidence drift all suppress row bodies while leaving `total_count: 1`; count,
  offset, and projection therefore do not yet share one exact eligible identity set.
- The member portal checks a current SAP decision's member/status but not its application edge. A
  coherent completion for another application can mark the requested application's SAP stage
  complete, contrary to M07-FR-010 and 009L4's all-consumer contract.
- 009L5 owns these two High root findings, collapses the duplicated lifecycle validator, completes
  mixed 1/21/101 workspace and action/error matrices, and turns the five retained review probes
  green. `CR-012` remains the separate hosted browser-evidence owner and runs after 009L5.

## 009L4 Architecture Review Closure

- Architecture review `2026-07-19_104332_architecture_review` proves member and account reads still
  choose different SAP completion records. A newer incoherent cross-application request makes the
  canonical member decision unavailable while the application-specific account facade accepts the
  older completion. M07-FR-010 therefore remains conditional on one SAP-owned current-completion
  decision shared by every downstream consumer.
- 009L3 corrected count leakage by validating all rows before Python slicing, but that implementation
  deep-projects the entire eligible Loan Account portfolio. The staff workspace then walks every
  nominal account page and slices again. 009L4 must retain truthful totals while moving complex
  eligibility behind one bounded selector and proving stable work at 1, 21, and 101 mixed rows.
- S36 reachability, governed CFC admission, pending-only initial posting, masked SAP output, transfer
  winner/posting singularity, and the restored S42 tab shell remain retained contracts. 009L4 closes
  the omitted SAP-component/consumer, action/mutation, transport/error, pagination, and MP14 unit
  matrices without duplicating CR-012's hosted nine-state UI evidence.
- A-135 remains binding: no initial-payment SAP confirmation actor, permission, adapter, or success
  evidence exists, so the obligation stays pending-only.

## 009L Epic Closure

- Credit Manager S36 and assigned Senior Finance S37 now share the staff workspace through SAP-owned
  projections; exact roles, permissions, assignment, current evidence, safe assignee choices, optional
  fields, and aware browser timestamps are enforced without exposing protected SAP workbook facts.
- Successful transfer atomically creates one singular `pending` initial-payment SAP obligation tied to
  the exact transfer/register/application/account/amount evidence. A-135 leaves posting confirmation
  unavailable until governance names its actor, grant, adapter, and immutable acceptance evidence.
- Loan Account search/status/member filters are implemented; `dpd_bucket` is explicitly deferred to
  Epic 010. Database pagination precedes row composition, SAP reads cross the public owner facade, and
  real account summaries cannot render mock repayment/interest/default/closure truth.

## 009K Staff Disbursement Workspace and Frontend Wiring

- S36-S41 require a walkable staff workflow, while the retained §§29-31 APIs supply mutations and
  account/readiness fragments but no safe finance/CFC queue or source-bank selection contract.
  009K therefore adds one strict, paginated `/api/v1/disbursement-workspaces/` projection over the
  existing SAP, loan, readiness, disbursement, bank, and advice owners.
- Rows are scoped to effective Senior Finance initiation or CFC authorisation authority, mask
  protected bank/SAP/reference values, preserve Money strings, and expose only server-owned action
  descriptors. The browser never infers readiness, permission, payment state, bank identifiers, or
  next actions. Initiation/transfer/advice retries use stable §45 idempotency keys.
- A CFC lacking readiness-read permission sees the retained at-initiation readiness fact only; the
  authorisation mutation still revalidates the exact current evidence before accepting a decision.

## 009H9D communications provenance and operator-boundary closure

- Migration 0008 now validates every required frozen fact for type/content, checksum, channel, and
  exact agreement with the still-referenced queued template. Recomputed one-field drift and
  malformed variable collections are cleared to `ambiguous_legacy`/`legacy_partial`; the genuine
  coherent queued job retains its exact forward/reverse/reapply identity.
- Exception collection/detail/resolution select the current permission from the exact retained job
  kind in addition to assigned ownership. Retained adapter paths normalize once to source
  `email`/`sms` vocabulary, and strict stable page/page-size pagination applies the same authority
  and redaction to every page.
- Channel/configured-adapter selection, job execution, due iteration, and task evidence shaping now
  sit behind public `CommunicationDispatcher` interfaces. Process/Celery entries only compose or
  delegate; executable interface tests cover Email/SMS execution and exact/changed/cross-channel
  idempotency without coupling to private implementation spelling.
- Architecture review `2026-07-19_014802_architecture_review` proves migration 0008 accepts a blank
  required queued-template fact when its checksum is recomputed. Complete provenance must validate
  required fact content, not only non-null presence and checksum equality.
- Exception list/detail/resolve currently authorise the union of generic/advice send permissions;
  the exact retained job kind must choose the required current permission in addition to assigned
  ownership. Provider vocabulary is `email`/`sms`, not a dotted adapter implementation path.
- The corrective also owns real exception pagination, channel/adapter selection inside the deep
  communications owner, observable public-interface tests, and cross-channel idempotency coverage.
  It preserves H6 legacy exclusion, H8/H9B leases and exact-cap recovery, H9C immutable provider
  replay, and the existing advice finalization seam.
- MP14 uses the explicit selected id and exact owner stages, but its required two-finance-record
  opposite-order regression remains an Epic 009 closure evidence gap rather than a new leaf slice.

## 009H9C communication channel, interface, and provider-evidence closure

- Generic HTTP now rejects channel/template mismatch, malformed Email/SMS recipients, unsupported
  phone/courier delivery, and sensitive SMS variable/value forms before any row, job, notification,
  or audit write. Email and SMS have distinct configured/manual/fake/future adapter seams; SMS can
  never call `send_email`.
- Exact generic and §31.5 advice key replays return API §45.2's retained-original-response wrapper;
  changed actor/object/channel/payload reuse remains zero-write conflict. HTTP remains provider-free.
- One communications migration adds a singular immutable generic provider-evidence owner bound to
  job, Communication, channel, payload digest, key, actor, adapter identity, provider result, and
  acceptance time. Worker replay reconciles it before returning `sent` and never re-enters the
  provider. Retained pre-migration generic acceptance is backfilled as explicit legacy evidence.
- Due-job selection, iteration, and safe task evidence shaping now remain in the deep communications
  module; Celery tasks only delegate. H6 legacy exclusion, H8 leases/on-commit/recovery, H9B exact-cap
  exception behavior, and the acyclic communications/process/disbursements seam remain intact.

## Architecture Review 2026-07-18 20:56 — Queued Migration, Retry Cap, and Channel Truth

- Independent review of 009G6, 009H6, 009H7, 009H8, and CR-011 found that communications 0008
  treats every attempt-less pending outbox as ambiguous even when a complete frozen snapshot is
  bound to a genuine queued H5 job. Migration 0009 then refuses that job, so a valid 0007 database
  can fail to upgrade. `009H9A` preserves only the singular coherent queued-job/snapshot shape and
  leaves unlinked or malformed pending history honestly legacy-partial.
- H8 recovers every expired running job without comparing attempts to `max_attempts`. A crash on
  attempt 3 of 3 becomes due again and its next claim violates the database cap, while the source
  §22.3 exception ledger is represented only by a notification. `009H9B` makes exact-cap recovery
  terminal, fenced, and singular and adds the protected operator exception/resolution owner.
- Generic HTTP accepts Email, SMS, phone, and courier, but the worker creates only
  `EmailDeliveryPayload` and invokes `send_email`; no SMS-specific recipient or sensitive-content
  contract exists. The public dispatcher and replay response also remain wider/different than
  codebase-design §40.1 and API §45.2, and generic provider acceptance lacks immutable attempt
  evidence. `009H9C` closes channel, facade, replay, evidence, and thin-task contracts.
- Forty-three retained focused tests pass. Three review-only probes fail on the exact queued
  migration, final-attempt recovery, and SMS-through-Email paths. 009G6's full state fingerprint and
  CR-011's migration-test leaf restoration appear complete. Full traceability and evidence are in
  the newest `docs/working/REVIEW_FINDINGS.md` entry and run folder.

## 009H8 Communications Worker Runtime and Crash Recovery Closure

- The pinned Celery app now loads environment-driven broker/result/provider/runtime settings,
  explicitly imports `communications.execute_job` and `communications.dispatch_due_jobs`, and
  loads a 60-second periodic due/recovery schedule. New generic and advice jobs publish exactly one
  named signature only from a robust `transaction.on_commit`; rollback publishes nothing, while a
  broker-publish crash leaves the committed row discoverable by the periodic selector.
- One migration adds a fenced UUID claim, expiry, recovery count, and last-recovered timestamp.
  Existing running jobs receive expired claims rather than rewritten attempt history. The default
  five-minute lease and 100-row batch are environment-configurable under A-134. Recovery preserves
  attempts, records safe `worker_crash` evidence, and prevents an expired worker from completing or
  deferring a replacement claim.
- Generic and advice jobs run through the same configured adapter seam. Manual mode remains honest;
  explicit Fake/eager integration proves both job kinds without network. Crashes before provider,
  after retained provider acceptance, before local finalization, during publish, and after task
  acknowledgement recover without a second accepted send. Provider idempotency plus retained
  acceptance remains the external crash-window authority.
- H6 `legacy_0005`/`legacy_partial` advice outboxes are excluded from due/recovery selection even
  when a stale retained job points at one. Neither job nor outbox is mutated; operators receive only
  `operator_blocked` evidence. General job evidence exposes bounded status/attempt/lease/recovery/
  safe-failure facts and never recipient, body, provider id/error, financial reference, actor,
  idempotency key, or payload truth. Exhaustion retains the existing singular reachable task.
- The architecture runtime probe, focused generic/advice/eager/migration/crash suite, Django check,
  migration sync, and frontend gates pass. Ten PostgreSQL queue/claim/stale-recovery races pass in
  two final executions with one provider acceptance and one terminal chain. INT-COMM-002/003 and
  the H5 runtime finding are closed.

## 009H7 Communications Dispatcher Interface and Idempotency Closure

- `CommunicationDispatcher` now exposes the source-shaped `create_from_template`, idempotent
  `send`, and generic `retry_failed` interface. Generic HTTP and advice queueing retain one
  communications-owned job kind/communication/key identity; advice authority and final financial
  consumption remain private to the top-level process coordinator.
- Both generic and advice HTTP sends require a trimmed nonblank `Idempotency-Key` up to 255
  characters. The job binds exact communication/advice, frozen payload, and actor; exact replay is
  zero-write retained truth, while missing, changed, cross-actor, and cross-object use fails before
  communication/provider evidence writes.
- Migration 0009 preserves every retained H5 job id/outbox/advice/status/attempt/schedule/failure/
  timestamp while adding generic identity and provider-result fields. Only H6
  `frozen_before_dispatch`/`verified` outboxes can backfill or attach; legacy-partial origins remain
  excluded from job/replay truth.
- The disbursement owner no longer lazily imports or registers its process coordinator. Views/tasks
  enter top-level composition, business owners expose decisions only, and the communications owner
  contains template, job, idempotency, adapter, and delivery policy.
- Manual/no-provider mode now rejects instead of fabricating acceptance. Fake/configured adapters
  retain exact provider identity; generic acceptance is frozen on the job before final Communication
  mutation, and advice keeps its stronger outbox/attempt/final-chain evidence.
- RED/GREEN public probes, 57 focused tests plus six H6 migration regressions, Django check,
  migration sync, compilation, frontend typecheck/lint/331 tests/build, and two final PostgreSQL
  executions of all six five-caller races pass. No new source-silent assumption was required. H8
  and I2 were rechecked and are already concrete, so no speculative sharpening edit was made.

## 009H6 Legacy Advice Template Provenance Closure

- Communications migration 0008 records an explicit provenance origin for every outbox. Either
  deterministic 0005 legacy attempt kind becomes `legacy_0005`; attempt-less or checksum-incoherent
  rows become honestly `ambiguous_legacy`; only a non-legacy provider attempt plus a complete
  internally checksummed frozen snapshot becomes `frozen_before_dispatch`. The first two origins
  are `legacy_partial`, and database constraints bind every origin/status/full-or-null snapshot
  shape so a status flip or copied current template cannot upgrade history.
- Fresh migration 0005 application now labels its copied current-template facts `legacy_partial`
  immediately. Existing retained template snapshots remain reviewable but are never claimed as
  historical provenance; provider attempts, receipts, Communications, actions, audits, workflows,
  ids, rendered advice, and final links are preserved without resend or replacement.
- Migration 0008 clears the mutable template FK, every reconstructed template fact/source, and the
  checksum from partial rows. Current replay/finalization and portal artifact/download selection
  require verified frozen origin
  and reject both 0005 legacy attempt identities. A coherent origin/status tamper is database-
  rejected; an attempt/template mismatch fails through the public interface with zero provider
  calls. Reverse refuses when removing the origin marker would expose retained legacy history;
  clean post-0005 rows reverse/reapply unchanged.
- The template-drift review probe failed first. Five provenance/migration/public tests, every
  retained historical migration case, 29 advice tests, 12 portal/persistence tests, Django check,
  migration sync, compilation, and both PostgreSQL five-caller methods in two independent runs pass.
- 009H7 and 009H8 now explicitly preserve/exclude the H6 immutable origin contract while
  generalizing jobs and adding worker recovery; no speculative business rule or assumption was
  added.

## 009G6 Legal Migration Exception Fingerprint Closure

- The legal-owned migration guard now deep-snapshots each real Django `ProjectState` before an
  operation runs. This is required because the retained add operations mutate the nested constraint
  list in place and an ordinary Django state clone shares that list, which could erase the genuine
  before-state and hide the transition.
- Each of the four retained disbursements 0005 operation identities now freezes the exact expected
  constraint definition and accepts only a canonical complete `DocumentChecklist` state whose sole
  difference is that constraint. Fields, all options (including table/index/constraint definitions),
  bases, managers, and other-model footprints fail closed.
- The independent same-model option probe failed first. All four real operation indices pass, and a
  24-case matrix rejects one-property field/constraint/index/option/base/manager mutations across
  both remove and both add identities. The 20-test forward/reverse/reapply manifest and guard file,
  Django check, migration sync, compilation, and legal 0015 zero-SQL proof pass.
- Legal 0015, disbursements 0005, models, physical schema, rows, ids, APIs, and checklist behavior
  remain unchanged. 009H6 and 009H7 were rechecked and already contain concrete executable
  provenance, migration, interface, idempotency, adapter, dependency, race, and evidence contracts.

## Architecture Review 2026-07-18 15:45 — Migration, Communications Runtime, and MP14 Truth

- Independent review of 009G5, 009H4, 009H5, and 009I found that the legal migration exception
  checks only the expected constraint-name delta and can admit another mutation on the same model.
  `009G6` freezes the complete before/after `DocumentChecklist` model-state fingerprint.
- H4's legacy migration copies facts from the current mutable template and labels them verified,
  although the slice explicitly forbids reconstructing missing historical provenance that way.
  `009H6` labels copied history `legacy_partial` and keeps it outside current replay/portal truth.
- H5 retains useful durable jobs and bounded state, but it has no discoverable Celery application,
  enqueue hook, broker/schedule configuration, or dead-worker recovery. Its public surface also lacks
  the source `send` method and explicit `Idempotency-Key`; the default manual adapter reports sent
  without delivery, and a lazy import hides a `disbursements -> processes -> disbursements` cycle.
  `009H7` closes the interface/idempotency/adapter/dependency seams before `009H8` supplies the real
  worker runtime, on-commit scheduling, leasing, retry, and crash recovery.
- MP14 does not consume SAP completion, copies initiation/transfer timestamps onto unrelated stages,
  and chooses the first finance-like application in the browser. It also bypasses existing portal
  visual patterns and retained no promised real-browser screenshots. `009I2` restores explicit
  parent-owned application selection, exact owner stage truth, existing composition, and a declared
  trusted-browser contract. 009J now waits for this terminal correction.
- Thirty-two retained backend tests and three MP14 frontend tests pass. Five review-only probes
  reproduce the significant defects. Full evidence and traceability are in the newest entry of
  `docs/working/REVIEW_FINDINGS.md`; no production code changed in the review.

## 009H5 Communications Dispatcher Job and Dependency Closure

- `CommunicationDispatcher` is now the single owner for generic approved/effective template
  preparation, exact merge/render, pending Communication creation/audit, disbursement outbox,
  provider dispatch, finalization, durable job state, and retry selection. The legacy communication
  service delegates instead of retaining a second render/send policy.
- The §31.5 request now freezes one communications-owned job and returns queued truth with zero
  provider calls. Exact request replay resolves the same job; changed replay conflicts. Only the
  shallow `processes.disbursement_advice_delivery` coordinator composes locked disbursement
  authority/current facts with communications job/provider/final evidence; static proof rejects
  direct communications↔disbursements Python imports.
- Jobs expose queued/running/retrying/sent/failed, freeze actor/role/team/request/network and the
  009H4 outbox identity, retry safe timeout/rejection/malformed/crash outcomes at most three times
  with bounded exponential backoff, and create one operator task on honest exhaustion. General job
  evidence retains only safe failure codes, not recipient/render/provider/error/financial payloads.
- Manual, Fake, and Future adapters continue through the same idempotent provider seam. Accepted
  009H4 outbox truth finalizes once before the job becomes sent; queue creation alone cannot make
  MP14 advice available. Two five-caller queue races and two five-worker execution races passed on
  PostgreSQL with one job, one provider attempt, and one terminal chain.

## 009H4 Repair — Order-Independent Receipt Schema Proof

- Independent parallel coverage ran the receipt-owner migration test after an older approval
  migration boundary and reproduced a SQLite-only physical column-order change after reversing
  communications 0005. Receipt rows, ids, column names, constraint names, and the detailed 009H4
  type/null/default/FK/unique/check/index/definition manifests remained exact.
- The legacy 009H3A receipt signature now compares its exact column-name set in deterministic sorted
  order instead of treating ordinal position as a persistence contract. No production model,
  migration operation, schema value, API, frontend, provider, or financial behavior changed.
- The validator-compatible two-test sequence failed first and now passes. Forty focused migration,
  persistence, adapter, and public advice tests pass with only the two expected PostgreSQL skips;
  Django check, migration sync, compile, diff, protected-path, and debug-instrumentation audits pass.
- 009H5 and 009I were rechecked and already contain concrete fields, owner seams, role/current-truth
  rules, job/download contracts, failure cases, races, and browser evidence requirements.

## 009G5 Legal Migration State Guard Closure

- The legal-owned `migration_state_guard` now evaluates real Django `ProjectState` transitions for
  every operation in every repository migration. It compares the checklist model immediately before
  and after each operation, so module constants, imported classes, inheritance, and helper
  indirection cannot hide a cross-app mutation; database-only `RunPython` remains correctly inert.
- `shared` no longer contains legal/disbursement model names, migration filenames, or allowlist
  policy. Only the two historical disbursements 0005 class identities are retained, frozen by exact
  path/module/class plus operation position and expected constraint transition; renamed paths or
  classes, sibling operations, and changed model footprints fail closed.
- The architecture-review module-constant probe failed first and is retained. Twelve guard tests
  and the 27-test 009G4/credit/witness/communications/document-template/SAP migration set pass.
  Django check, migration sync, compile, and zero-operation `sqlmigrate` are green. Legal 0015,
  migration history, physical schema, rows, ids, APIs, checklist truth, and production behavior are
  unchanged.
- 009H4 and 009H5 were rechecked before completion. Both already contain concrete owner interfaces,
  exact evidence fields, migration/job contracts, failure cases, race requirements, and source
  references, so no speculative sharpening edit was needed.

## Architecture Review 2026-07-18 10:43 — Advice Evidence, Jobs, and Migration Guard

- 009H3A/BA/BB substantively move new advice template/provider/finalization policy into
  communications, retain one stable-key outbox/provider identity, mask general evidence, and prove
  the two intended crash families plus twice-run PostgreSQL races. Thirty-four retained focused
  tests pass. The source-defined generic dispatcher and queued/failed/retrying job lifecycle remain
  absent, however; template/render policy is duplicated in `communications/services.py`, provider
  calls run synchronously in HTTP, and the communications/disbursements persistence/runtime edges
  remain circular. `009H5` supplies one canonical dispatcher, top-level coordinator, durable async
  job, bounded retry, integration truth, and acyclic dependency direction.
- Review probes exposed two harder current-evidence gaps. A terminal advice row without an outbox
  calls the provider and commits a replacement outbox before conflicting, which is also the natural
  shape of every coherent pre-009H3A delivered row because migration 0004 did not backfill outboxes.
  Separately, changing a pre-receipt accepted outbox to another syntactically valid provider id/time
  lets replay create the receipt/Communication/audit/workflow chain from fabricated truth. The
  outbox also freezes only a template FK/code/version/checksum rather than all named provenance.
  `009H4` adds immutable provider/provenance evidence, honest legacy backfill/non-dispatch, protected
  terminal linkage, primitive cross-owner ids, exact schema manifests, and the real pre-commit crash.
- 009G4's legal-owned zero-operation state anchor and full checklist schema/row manifest are
  substantive. Its `shared` AST guard nevertheless contains business policy and misses ordinary
  module-level target constants because it recognizes only literal strings inside a top-level
  custom class. `009G5` evaluates actual legal model-state transitions at the legal/test owner seam
  while retaining only the exact historical 0005 exception and leaving migration 0015 unchanged.
- BR-054/M08-FR-010 are partial until H4/H5 close legacy/provider/job truth. INT-COMM-002/003 remain
  open for the async queue/retry owner. 009I now depends on G5/H5 and projects advice as issued only
  after the terminal communications owner proves accepted finalization; 009J remains dependent on
  009I. No new business rule or ADR was needed because the cited sources decide these boundaries.

## 009G4 Repair — Historical Credit Projection Isolation

- The new legal 0015 leaf depends on current disbursement/communications state, so a retained
  credit-ownership migration test that projected every leaf except known downstream apps silently
  pulled `credit.0001` into its intended pre-move `applications.0010` registry.
- The test now also excludes `legal_documents`; the projected registry again contains application-
  owned `EligibilityAssessment` and `LoanLimitAssessment`. Production migrations, models, rows,
  constraints, APIs, checklist behavior, and the 009G3 aggregate are unchanged.
- The exact coverage failure was reproduced. The two-test credit migration class passed repeatedly,
  the combined 15-test 009G4/credit/communications/document/SAP migration set passed, and Django
  check, migration sync, and compilation are green. Full coverage remains the independent gate.

## 009G4 Legal Checklist Migration Ownership Anchor

- Legal documents migration 0015 is an empty, zero-SQL state anchor over the current legal 0014,
  historical disbursements 0005 checklist replacement, current disbursements 0007, and current
  communications 0004 leaves. Future legal migrations therefore inherit the exact live checklist
  constraint state without rewriting applied history or replaying schema/data operations.
- The retained migration proof starts before disbursements 0005, preserves exact checklist/action
  ids and values, and compares the complete physical checklist-table schema through forward,
  reverse-to-the-anchor-dependencies, and reapply. Each live constraint is present exactly once;
  both Epic-009 placeholders remain absent.
- `shared.migration_state_guard` rejects custom downstream operations that target
  `legal_documents.DocumentChecklist`; only the two reviewed disbursements 0005 operation classes
  are allowlisted. A synthetic future-app mutation proves the guard fails closed.
- Six focused tests, seven adjacent migration-isolation tests, Django check, migration sync,
  compilation, pinned-Node frontend typecheck/lint/327 tests/build, and the zero-operation SQL
  manifest pass. Checklist behavior, APIs, rows, ids, statuses, and the 009G3 aggregate are
  unchanged. 009I and 009J were rechecked and remain concrete without speculative sharpening.

## 009H3BB Communications Finalization and Race Closure

- Source BR-054/M08-FR-010 requires borrower advice after disbursement; integrations §§10, 19.3,
  and 21 require template-backed Communication evidence, provider acceptance status, stable
  `communication_id` duplicate identity, safe retry, and no raw sensitive payload logging.
  Codebase-design §§20.6, 22.2, 26.3, 36.2, 40.1-40.2, and 42.4 place adapter, template, delivery,
  audit, idempotency, and redaction policy in the deep communications module without a reverse
  dependency on disbursements.
- `CommunicationDispatcher.finalize` now retains/reconciles the communications-owned receipt,
  protected Communication, digested/masked audit, workflow event, and delivery evidence under the
  financial context owner's transaction. It returns an immutable finalization decision;
  disbursements alone validates authority/current transfer-register-intent truth and saves its own
  action/link from that decision. The legacy module contains no receipt, Communication, audit,
  workflow, digest, or finalization implementation.
- Provider acceptance survives both forced pre-receipt and pre-Communication-commit failures.
  Atomic rollback leaves no partial local chain; an exact fresh-adapter retry consumes the retained
  outbox provider identity once, while changed recipient/template/render/provider/upstream facts
  conflict. General audit/workflow evidence contains recipient/content/provider/amount digests or
  masks only, never raw email, rendered advice, full UTR, provider id, or advice amount.
- The 30-test owner/public matrix and retained 009H3A migration test pass. Two separate PostgreSQL
  executions each ran both declared five-caller methods; every method logged one winner, four clean
  losers, one provider identity, one outbox/receipt/Communication/action/audit/workflow chain.
  No migration, public response, frontend, financial, register, checklist, repayment, schedule,
  interest, default, closure, or portal behavior changed.
- 009G4 and 009I were rechecked against this terminal identity. Their requirements already name the
  communications-owned accepted delivery and remain concrete, so no speculative edits were made.

## 009H3BA Repair — Historical Receipt Fixture Isolation

- Independent complete coverage found one retained migration-test error: the test reversed
  communications to `0003` and then called the current public advice dispatcher, which correctly
  queried the `0004` outbox table that the test had removed.
- The migration proof now creates one exact pre-transfer receipt through the projected historical
  disbursements model and compares every receipt value plus physical schema through forward,
  reverse, and reapply. This exercises the state-only owner transfer at its true historical seam.
- The exact failed test and the 29-test receipt-migration/communications/public set pass with two
  expected PostgreSQL-only final-race skips. Production dispatcher, migrations, models, public API,
  provider behavior, and financial truth are unchanged.

## 009H3BA Communications Dispatcher and Outbox Freeze

- `communications.modules.communication_dispatcher` now solely owns approved/effective template
  resolution, exact declared-variable and protected-value checks, rendering, full provenance
  checksum, durable outbox reconciliation, adapter dispatch, and provider-result validation.
  Communications imports no disbursement code; disbursements supplies one frozen primitive
  `DisbursementAdviceContext` after retaining authority and locked financial/current-truth checks.
- The unchanged 009H3A outbox commits pending recipient/digest, template identity/version/checksum,
  rendered snapshots, payload digest, communication/idempotency identity, and related entity before
  any provider call. Accepted provider truth is retained there before the transitional local final
  receipt transaction. Changed recipient/template/render/payload/entity facts conflict before
  redispatch; exact fresh-adapter recovery consumes the same logical provider identity.
- Manual/Fake/Future stable identity, provider rejection/retry, malformed results, accepted-result
  recovery, and full template provenance drift are green. Rejection/malformed output leaves only a
  pending outbox and fabricates no receipt, Communication, audit, workflow, or disbursement sent
  state. The focused owner/public suite passes 28 tests with two expected PostgreSQL-only BB skips;
  Django check, migration sync, Python compile, dependency, protected-path, and diff checks pass.
- No schema, migration, public response, frontend, money, transfer, account, register, checklist,
  repayment, schedule, interest, default, closure, or portal truth changed. 009H3BB remains the
  concrete terminal owner for receipt/Communication/audit/workflow finalization and twice-run races;
  009G4 was also rechecked and remains concrete without speculative edits.

## 009H3A Repair — Historical Migration Projection Closure

- Complete coverage exposed five retained migration-test errors after communications 0004 became a
  required downstream leaf of disbursements 0007 and therefore current application/credit state.
  Two old app-registry projections excluded finance/loan/SAP/disbursement descendants but not the
  newly downstream communications leaf, so projected models outran their correctly reversed schema.
- The credit-ownership and witness-evidence migration tests now exclude communications from those
  historical projections. The exact ordered failure is green, all six implicated migration tests
  pass, and the 23-test advice foundation/public API set remains green with two expected PostgreSQL
  skips. Production models, migration operations, adapters, and public behavior are unchanged.

## 009H3A Communications Advice Persistence and Provider Identity

- Communications now owns one complete advice outbox schema and the retained receipt Django model
  state. The outbox uniquely binds advice intent, communication identity, stable key, channel,
  frozen recipient/digest, template/version/checksum, rendered snapshots, payload digest, related
  entity, status, and an all-or-none provider-result tuple.
- Communications migration 0004 creates only `communication_delivery_outboxes`; its custom state
  operation transfers `DisbursementAdviceDeliveryReceipt` without database SQL. A genuine sent
  receipt keeps the exact physical table, constraint signature, and primary key through forward,
  reverse, and reapply, while the outbox schema appears exactly once only in the forward state.
- Manual and Fake adapters derive provider identity from only the stable idempotency key. Future is
  a replaceable transport adapter that forwards the same key contract. Changed payload and fresh
  instances preserve one identity/status; a provider rejection can be retried without fabricating
  an accepted result.
- A policy-free disbursements alias preserves legacy receipt imports, while the live 009H2 advice
  module uses the canonical communications model. Twenty-four focused foundation/009H2 tests pass
  with two expected PostgreSQL skips; public HTTP, authority, audit/secrecy, upstream, receipt, and
  financial-side-effect behavior remains unchanged. 009H3B owns all dispatcher/crash/race work.

## 009H3 Oversized-Slice Queue Rewrite — 2026-07-18

- Failed run `2026-07-18_010406_normal_run` passed its focused advice-owner, migration, and twice-
  run PostgreSQL evidence but changed 2,195 lines against the configured 2,000-line limit. No
  candidate production change was retained.
- Parent 009H3 is Superseded. 009H3A inherits 009H2 and owns the single communications migration,
  durable outbox/receipt model state, retained receipt table/ids/history, provider-key identity,
  adapters, and compatibility proof. Its target delta is 700-1,050 lines.
- 009H3B depends on 009H3A and owns the communications dispatcher, immutable disbursement context
  seam, pre-provider outbox freeze, crash/template/payload conflict closure, safe final ledgers, and
  twice-run five-caller races. Its target delta is 1,050-1,450 lines and it adds no migration.
- 009G4 and 009I now depend on terminal successor 009H3B. Every original 009H3 requirement, test,
  evidence category, and High-risk concern is allocated explicitly across the two successors.

## 009G3 Repair — Legacy Protected-Register Test Closure

- Full parallel coverage found one retained documentation test that attempted to delete the exact
  `LoanRegisterUpdate` now protected by `Disbursement.register_update`; the intended
  `ProtectedError` then surfaced as Django's secondary traceback-pickling error.
- The test now directly asserts deletion protection and uses a reversible register checksum change
  to retain its public checklist replay 409 assertion. Production models, migration 0007, transfer
  policy, and checklist policy remain unchanged.
- The exact red/green test, both impacted backend classes (61 tests), Django check, and migration
  sync pass. Complete parallel coverage and twice-run PostgreSQL acceptance remain independent
  orchestrator gates.
- 009H3 and 009G4 remain concrete after recheck; no sharpening edit was needed.

## 009G3 Repair — Protected Register Migration Closure

- Independent validation found that the protected `Disbursement.register_update` model relation
  had no migration, so migration drift failed and parallel coverage reached a schema without
  `register_update_id`. Disbursements migration 0007 now owns that exact schema change.
- Existing successful rows are linked only when their singular transfer, register, advice intent,
  document checksum, account/application/member/amount, action/digest, audit, and workflow facts
  agree. Missing, ambiguous, changed, or non-success register evidence aborts rather than receiving
  fabricated completion truth; reverse migration clears only the new owner link.
- Migration sync, fresh migration application, the exact prior coverage-crashing test, the protected
  register test, all 11 transfer-success tests, and Django check pass. Complete coverage and declared
  PostgreSQL validation remain independent orchestrator gates.
- 009H3 and 009G4 were rechecked and remain concrete; no sharpening edit was required.

## 009E5 Shared Safe Audit Text and Source-Bank Closure

- `shared.audit_text.safe_audit_text` is now the single reusable seam for bounded human-reviewable
  audit reasons. It rejects blanks, oversize/control text, contiguous or space/slash/hyphen/dot-
  formatted eight-plus-digit identifiers, every `field:vN:` prefix, legacy encryption markers,
  SHA-256-shaped lookup hashes, and caller-supplied protected ciphertext/hash values with one
  generic no-echo error.
- Public source-bank activation and replacement both use that seam before evidence writes; current
  resolution also fails closed when retained rationale no longer passes the same policy. Safe text
  remains exact across governance, version, and audit evidence with unchanged reason/context
  digests, author/request/role/team/network attribution, false-approval protections, predecessor
  history, unassigned Critical grant, and transaction behavior.
- Fifteen focused audit/encryption/source-bank tests and the complete 18-test initiation class pass.
  Both PostgreSQL five-caller first/replacement race methods pass in one authoritative run, each
  method independently executing a first-activation and replacement race.
- No API, schema, frontend, encryption, masking, permission, or business-authority change was made.
  Already-concrete 009G3 and 009G4 requirements were rechecked; no speculative sharpening was needed.

## Architecture Review 2026-07-17 21:08 — Register, Checklist, and Advice Ownership

- CR-009's deterministic malformed/authenticated-tamper split is substantive. 009E4, 009G2, and
  009H2 also close most prior rationale, post-transfer, replay, authority, current-contact/rendering,
  and audit findings; ten focused retained tests pass.
- Review reproduced two remaining hard safety/idempotency edges. Formatted bank identifiers and an
  unrelated `field:v2:` token pass the source-bank rationale validator into audit/version evidence;
  `009E5` centralises safe audit text. The same advice idempotency key produces two logical provider
  ids if payload changes after acceptance but before local receipt retention; `009H3` freezes a
  communications-owned outbox before dispatch and moves duplicated template/delivery policy to the
  source owner.
- 009G2 creates the register and pending advice atomically, but the true register flag can outlive a
  deletable register row. Its checklist route also requires signer=historical initiator rather than
  canonical current Senior Finance scope, and replay under-checks completion-owned ledgers. `009G3`
  restores owner-protected register truth, Stage-5 authority, and exact immutable reconciliation.
- The disbursements 0005 migration changes legal checklist state from the downstream app. `009G4`
  adds a legal-owned state anchor/guard without rewriting applied history. 009I/009J now depend on
  G4/H3 and project G3 register/transfer truth.

## 009H2 Advice Authority, Current Truth, and Delivery Closure

- `DisbursementWorkflow.send_advice` now consumes the exact 009G2 pending advice UUID as the
  protected communication id and provider/outbox idempotency key. Manual/Fake adapter payload and
  receipt identity/status/time remain stable across fresh instances and a post-acceptance database
  rollback; rejection leaves the same intent pending with no sent ledger.
- Auth §26.5 is restored in both catalogue and action scope: active Senior Manager Finance requires
  the exact initiating-maker plus current SAP-assignee relation; Credit Manager requires the
  canonical active-loan/application relation; CFC-only authority is denied. Effective multi-role
  users act only under a source-authorised role.
- First send and replay reconcile current canonical email, approved/effective template identity,
  version, variables and tokens, freshly rendered subject/body, provider id/status/time, sender
  role/team, transfer/register/intent, audit/action/workflow, and request/network evidence. Drift is
  zero-write conflict and cannot bless a historical delivery.
- Only the protected communication row retains the full recipient address. General audit evidence
  carries `b***@domain`, a SHA-256 recipient digest, protected owner/communication ids, and safe
  provider/upstream/request facts; neither full email nor full UTR enters audit/workflow evidence.
- The four architecture-defect probes plus Credit Manager coverage pass, the fresh-adapter rollback
  trace passes, 43 impacted backend tests pass, and both PostgreSQL five-caller race methods pass in
  two independent executions. No model migration or frontend change is required.
- The already-sharpened 009I and 009J Not Started slices were rechecked against this retained owner
  truth. Their exact 009H2 advice-currentness and 009G2 pending-or-sent identity dependencies remain
  concrete, so no speculative requirement edits were made.

## 009G2 Post-Disbursement Register, Checklist, and Replay Closure

- The public transfer-success transaction now creates one exact Loan Register update and one stable
  protected pending advice/outbox identity alongside the unique transfer, funded activation,
  history, audit, and workflow. Both new ledgers bind the exact disbursement/account/application/
  member/amount, normalized-reference digest, evidence file/checksum, transfer action/evidence
  digest, audit, and workflow; the register flag is true only with this coherent singular evidence.
- Source API §45.2 replay now returns `idempotency_replayed: true` with the retained original §31.4
  response. Exact replay writes nothing; changed payload/key/actor or changed register, advice,
  transfer, upload, authorisation, audit, workflow, account, or history evidence fails closed.
- The §27.7 Senior Manager Finance route now consumes a frozen post-transfer decision through the
  top-level process coordinator, preserving the legal-to-disbursement dependency boundary. Active
  explicit permission, effective Senior Finance role, and exact initiating-maker Stage-5 scope are
  all required. The first signature retains an immutable action/audit/workflow/version chain bound
  to the current transfer/register/advice identities; exact replay is zero-write and changed or
  stale replay conflicts.
- The action still sends no advice and creates no repayment, schedule, interest, default, closure,
  or borrower-visible truth. 009H2 owns durable delivery of the stable pending advice identity.

## 009E4 Source-Bank Rationale and Approval Evidence Closure

- The existing `source_bank_governance` deep module now retains each accepted first activation or
  replacement's exact printable rationale (maximum 500 characters) and a canonical sealed change
  context: action/kind, reason/digest, request, author, role/team, and request-network facts. Numeric
  bank-account content, protected bank tokens/hashes, control characters, blanks, and oversized
  rationales fail before any governance/version/audit write.
- Activation and predecessor-deactivation version rows identify the provisioner only as author;
  reviewer, approver, board-approval reference, approval reference, and approval timestamp remain
  empty. Migration 0005 clears the known false approval claim on legacy source-bank histories but
  cannot recover their original reason, so legacy rows remain honestly non-current.
- Current resolution exactly reconciles rationale/context digests, actor/request/network facts,
  canonical version/audit bodies and identities, effective ranges, and predecessor/successor facts.
  One-field rationale, digest, request, actor, role/team, network, version, audit, or false-approval
  drift fails closed.
- Six focused source-bank tests, 42 downstream/catalogue tests, and both PostgreSQL five-caller
  first/replacement race methods pass. Each race retains one complete reviewable winner and four
  clean conflicts. The Critical activation permission remains unassigned to every production role;
  A-126 is closed only for evidence mechanics, not for the still-unnamed business provisioner.

## Architecture Review 2026-07-17 16:56 — Post-Transfer Completion and Advice Truth

- 009E3 and 009F2 substantively close the prior amount/source-history/loan-owner and current bank/
  aggregate-integrity findings. The retained tests and twice-run PostgreSQL contracts are meaningful.
  Review found one remaining configuration-audit gap: source-bank changes retain only a reason hash
  and label the request/provisioner as approval. `009E4` restores reviewable safe rationale and honest
  author/request/approval attribution without assigning A-126's still-unknown provisioner role.
- 009G genuinely records one unique manual transfer and atomically funds/activates the loan, but its
  tests intentionally keep Loan Register, post-disbursement Senior Finance checklist, and advice
  intent absent. M08-FR-009/011 therefore have no executable path, data-model §34's post-success
  transaction is partial, and exact replay omits API §45.2's replay wrapper. `009G2` adds register
  evidence, stable pending advice/outbox identity, the public checklist signature, and exact replay.
- 009H genuinely renders/sends one protected advice, but the provider idempotency ledger is a fresh
  in-memory adapter instance and cannot survive acceptance followed by rollback. CFC-only authority
  is allowed while source-authorised Credit Manager is omitted; changed canonical email or rendered
  communication content still replays as 200; the full email is copied into audit evidence. `009H2`
  closes authority, stable delivery identity, current contact/rendered/provider truth, and masking.
- Four review-only probes reproduce §45.2, CFC role, canonical-email, and rendered-snapshot defects;
  14 retained public transfer/advice tests pass in the same isolated database. 009I/009J now consume
  the corrected 009H2/009G2 boundaries.

## 009H Disbursement Advice and Communication

- `DisbursementWorkflow.send_advice` owns source §31.5 behind one deep module. It requires the exact
  009G CFC checker or Senior Finance maker with the High send grant, locks the current transfer,
  active funded account, member/application, canonical email, template, and retained advice facts,
  and rejects inaccessible ids without disclosure.
- One approved effective borrower-email template must declare and use exactly the seven safe advice
  variables. The rendered snapshot uses server-owned application/account/amount/date facts and a
  masked UTR only. A Manual/Fake email adapter seam validates accepted delivery without network I/O;
  provider rejection creates no sent/link truth.
- Acceptance atomically retains one protected sent communication/link and singular safe action,
  audit, and workflow evidence. Exact actor/channel/recipient replay is zero-write/no-resend;
  changed or stale retained evidence conflicts. No money, transfer, account, register, checklist,
  repayment, schedule, or interest fact changes.
- Six public behavior tests cover success, replay, ledger drift, validation/template/provider
  failure, and permission/scope/stale-transfer denial. Two PostgreSQL five-caller methods prove one
  accepted communication and complete ledger; the sandbox socket is unavailable, so the declared
  capability delegates both authoritative twice-run executions to the orchestrator.

## 009J Sharpening Extract

- Initial Loan Account 360 wiring owns only the account list, header, KPI row, and Summary tab from
  exact 009C creation and 009G activation truth. Later ledger/schedule/interest/monitoring/default/
  closure data remains owned by Epic 010 and must not be inferred or newly mocked.
- Reuse `finance.loan_account.read` and the canonical loan-account scope selector. Safe projections
  carry account/application/member display facts, immutable terms, exact balances/status, SAP-safe
  display, and disbursement date only when current owner evidence proves them.

## 009G UTR Capture and Transfer Success

- `DisbursementWorkflow.mark_transfer_successful` owns the exact §31.4 POST. Active exact CFC
  checker or Senior Finance initiating maker scope plus the Critical mark-success grant is required;
  the action consumes the 009F2 typed approved decision and its terminal authorisation tuple.
- One normalized unique manual bank transfer and restricted current finance-evidence link are
  atomic with exact-amount funding, zero interest/charges, sanctioned-to-active account transition,
  tenure start, one append-only status history, and safe action/audit/workflow identities. Advice,
  Loan Register, checklist, repayment, schedule, interest, and borrower truth remain absent.
- Exact key/payload/actor replay returns the retained four-field projection only while the complete
  success ledger/file/account/history remains coherent. Changed/stale/duplicate/concurrent losers
  write nothing. A-127 records the source-silent five-minute future clock-skew tolerance.
- Eight public behavior tests and the 35-test initiation/authorisation/success set pass. Both
  PostgreSQL race methods passed in two separate executions, retaining one complete winner and four
  clean conflicts per round.

## 009I MP14 Sharpening Extract

- MP14 source requires own-only borrower finance status, sanctioned/final disbursement amounts,
  masked destination last four, completed date, optionally masked reference, and downloadable exact
  advice without internal authoriser/full-bank disclosure. The sharpened slice replaces every
  hard-coded MP14 value through one portal-self-scoped 009A-009H projection and one-use advice read.
- Borrower stages are documentation complete, SAP setup, payment initiated, CFC authorisation,
  transfer completed, and advice issued. Missing/mixed owner evidence shows the last safe stage or
  borrower-safe blocked state; it never infers success from mutable labels.

## 009F2 CFC Authorisation Integrity and Bank-Evidence Closure

- Initiation now freezes the exact application-owned beneficiary-bank decision manifest (bank,
  cancelled cheque, retained file/checksum, verifier, request, audit, workflow, and version) plus
  governed source-bank request/facts identities. The application owner re-resolves that immutable
  decision under locks; changed bank facts, a newer decision, duplicate/conflicting ledger, or
  changed terminal sanction fails closed.
- One typed `current_disbursement_evidence` decision now reconciles the singular initiation ledger,
  genuine loan-creation status/audit/workflow identities, complete current source-bank lifecycle,
  beneficiary-bank truth, unfunded account, and absence of later transfer/advice/register truth.
  CFC readiness scope and authorisation consume this same decision; 009G must request its approved
  form and extend it with the terminal-authorisation/transfer tuple instead of copying predicates.
- Database constraints now reject partial pending/terminal checker tuples, empty or overlong
  terminal comments, non-CFC terminal roles, same maker/checker, and any transfer/reference/time/
  advice/register truth before approval. Public responses and exact replay remain unchanged.
- Focused authorisation/initiation tests use a genuine legal/security/SAP/bank/loan initiation path.
  Borrower-bank drift denies scope and both decisions with zero writes; twice-run PostgreSQL
  five-caller approve/reject races retain one complete winner and no loser evidence.

## 009E3 Disbursement Amount and Source-Bank Governance Closure

- Public initiation now accepts any positive 18,2 amount no greater than immutable terms and
  sanction, freezes the exact lesser amount across the row/audit/workflow/CFC task, preserves exact
  changed-replay conflicts, and lets CFC approve that retained amount without claiming transfer.
- Initiation consumes a narrow `loan_account_lifecycle` decision that reconciles singular creation
  status-history/audit/workflow evidence. The full documentation/SAP/readiness/bank fixture now
  creates its loan through the public owner; equivalent-looking or changed creation evidence writes
  no disbursement.
- `config.source_bank_account.activate` is a canonical unassigned Critical permission. Activation
  pre-generates the governance identity and inserts an active row only with its version/audit proof.
  Replacement retains activation evidence, appends predecessor/deactivation version/audit facts,
  closes the effective range, and rejects incomplete, duplicate, changed, cross-linked, orphaned,
  or temporally incoherent chains.
- Two PostgreSQL tests each run five concurrent first activations and five replacements. Each round
  retains one complete winner and stable conflicts with no orphan governance/version/audit facts.
  A-126's mechanism is complete; the source-silent business provisioner remains intentionally open.

## Architecture Review 2026-07-17 11:45 — Initiation, Governance, and CFC Integrity

- 008M7 and 009D4 substantively close their current-tail/effective-role/applicable-signature targets.
  Focused retained tests pass, and no new Epic 008 corrective issue was confirmed.
- 009E2's typed owner and real legal/security/SAP/bank composition are substantive, but initiation
  rejects S38/S39's positive lesser amount, its full-path fixture inserts raw loan rows, and its new
  source-bank owner permits active rows without proof. Replacement mutates the prior status without
  closing effective history, and the declared Critical activation permission is absent from the
  production catalogue. `009E3` restores amount, loan-owner, catalogue, lifecycle, and race truth.
- 009F records atomic CFC approval/rejection and preserves a clean fixture's later-state boundary,
  but does not reconcile the current application-owned borrower-bank decision. It also allows a
  pending row preloaded with UTR/disbursed/register truth to be approved, while database constraints
  admit incomplete terminal and pending-success tuples. `009F2` restores current bank evidence,
  aggregate invariants, scope/action parity, and the full governed role matrix.
- Four review-only probes reproduce those gaps while four retained focused tests pass. 009G now waits
  for 009F2 and consumes its typed current-evidence decision before UTR/funding/activation.

## 009F CFC Authorisation/Rejection — Retained Implementation Truth

- `DisbursementWorkflow.authorise` is the only public terminal-decision interface. The exact §31.3
  POST accepts only `approved`/`rejected` plus bounded comments and returns the safe terminal state,
  still-pending transfer state, decision time, and server-owned next action.
- The owner locks the active governed CFC, disbursement and every retained initiation relation,
  reconciles the exact 009E2 request/comment/readiness and current source-bank governance/version/
  audit identities, and requires a distinct Senior Finance maker. It does not re-run upstream legal,
  security, approval, SAP, checklist, or readiness composition.
- One terminal action identity, checker facts, comments/evidence digests, audit, workflow transition,
  and CFC-task completion are retained atomically. Exact coherent replay writes nothing; changed,
  opposite, stale, replaced, missing, or concurrent losing decisions conflict without success facts.
- Approval/rejection leaves transfer pending and creates no UTR, transfer, funding, account status,
  advice, register, checklist, repayment, schedule, or borrower communication truth. Nine focused
  public behavior tests plus two real-owner PostgreSQL five-caller races run twice prove the contract.

## 009E2 Disbursement Contract and Owner-Proof Closure

- `disbursements.modules.disbursement_workflow` is the single public mutation owner. Initiation
  consumes `evaluate_for_initiation`, a typed decision carrying the canonical 23-check digest and
  narrow SAP, borrower-bank, and governed source-bank identities; the readiness GET remains redacted.
- Source-bank truth now requires one explicit Critical activation grant, reason/request evidence,
  immutable version/`config.changed` audit links, and unchanged exact SFPCL RBL source facts.
  Replacement retires and retains the old record while installing one singular current decision.
  No role is seeded with the authority, so A-126 remains fail-closed until governance explicitly
  grants a provisioner.
- API §45.2 replay returns the retained original response under `idempotency_replayed: true` without
  writes. Public blockers use the stable §7 classes, and generated/supplied request identity plus
  final-verification comment digest reconcile across the initiation audit, workflow, and CFC task.
- Genuine 008M7/009B3C/009D4 owners now reach public initiation without readiness/bank mocks.
  Unrelated signatures remain harmless; changed required signer or source-bank facts deny with zero
  initiation artifacts. Two PostgreSQL five-caller runs traverse the same real owners and retain one
  complete row/audit/workflow/task winner each.

## 009D4 Readiness Effective Roles and Signature Scope

- Readiness now resolves the active persisted actor through the central effective-role boundary,
  requires the explicit readiness permission, and ORs the source-defined scope of every effective
  Senior Finance, CFC, Credit Manager, CFO, and Auditor role. A governed authority is recognized
  only when its catalogue role and user are active; permission, intake assignment, an unknown
  authority string, or any role alone remains insufficient.
- Canonical scope remains source-specific: newest SAP assignee for Senior Finance, exact pending
  initiated-disbursement relation for CFC, active/monitoring loan states for Credit, portfolio detail
  for CFO, and the active explicit audit-read grant for Auditor. Multi-role actors receive the union,
  so fixed branch precedence cannot accidentally deny a valid narrower relation or widen access.
- Legal signature readiness now loads only the latest current documents named by applicable required
  PoA, tri-party, SH-4, Term Sheet, and Loan Agreement items. Unrelated and superseded signature
  history is ignored; every current required document still rejects missing, extra, wrong, duplicate,
  unresolved, or provenance-incoherent signer rows, including the exact approval-owned Term Sheet
  CFO/Director set.
- Auth §§15.6-15.8/19.3/26.5 supply the reader roles and object scopes; screen S32-S35/S38 and
  M06-FR-019/M08-FR-001-004 require exact signer/documentation blockers before payment. The public
  envelope, 23 codes/order, safe reasons, zero-write behavior, and retained query bound are unchanged.

## Architecture Review 2026-07-17 08:44 — Readiness and Initiation Closure

- 009D3 restores the named readiness seam and primary-role reader matrix, but still branches on
  `User.role_codes()`. An active governed CFO authority with the explicit readiness permission is
  rejected, and multiple effective roles are not unioned through the central authority boundary.
  Its signature owner also treats a valid signature on an unrelated current document as a failure.
  `009D4` restores effective-role scope and the exact five applicable document families after 008M7.
- 009E materially adds replay/race-safe manual initiation and a CFC task, but every success/race
  test replaces readiness and both bank owners. Exact replay diverges from API §45.2, public errors
  use private codes, initiation evidence omits request/comment traceability, and the workflow is
  fragmenting around private readiness dictionaries. `009E2` establishes one typed
  `disbursement_workflow` boundary and genuine owner-backed acceptance.
- A raw `BankAccount` row with mutable `sfpcl`/`RBL Bank`/`verified`/`active` labels is not the
  governed activation/verification owner that A-126 required. The assumption is reopened; 009E2
  must keep source-bank readiness failed unless a singular current governed decision exists, and
  must not invent the missing provisioner.

## 009E Payment Initiation (superseded contract details closed by 009E2)

- The original `disbursement_initiation` helper implements atomic manual-bank initiation behind the
  009E2 `disbursement_workflow` public owner and exact
  §31.2 POST. It requires active persisted Senior Manager Finance Critical authority/newest SAP
  assignment scope, consumes only the 009D3 composition interface for payment-gate truth, freezes
  the exact 23 ordered code/status digest (excluding `evaluated_at`), and locks the matching current
  beneficiary/source-bank evidence before writing.
- Generic source §12.3 bank ownership admits `sfpcl`, but its mutable labels alone never pass after
  009E2. The governed source-bank activation decision above is now required.
- Success retains one positive protected disbursement with `initiated/pending/pending`, manual mode,
  hashed idempotency identity, safe readiness/SAP/bank evidence ids, trimmed final verification,
  maker role/team/time, one audit, one workflow event, and one urgent CFC role task. Exact replay
  writes nothing; changed/stale/duplicate attempts conflict.
- The initiated row and its CFC task are the first canonical CFC readiness scope. Intake assignment,
  role, or permission alone remains insufficient. No CFC decision, transfer, UTR, advice, funding,
  activation, register update, checklist signature, or borrower communication is created.
- Two fresh PostgreSQL executions each ran both five-caller changed-request races: one complete
  row/audit/workflow/task winner and four zero-artifact conflicts. PostgreSQL-only lock targets were
  narrowed on nullable-join owner queries without changing their selected business rows.
- 009F was already concrete. 009G and 009H are now sharpened from §§31.4-31.5/§9/§19: transfer
  success owns unique UTR/evidence plus atomic funding/activation, while advice remains a later
  adapter/template action and cannot mutate financial truth.

## 009D3 Readiness Approval, Reader, and Boundary Closure

- Each ordered checklist approval now consumes the exact current ordered item-completion action
  identities. Current item decisions reconcile singular action/audit/workflow/version evidence,
  renderer/security/corrected-copy truth, and retained bodies; changed, reordered, duplicate, stale,
  or missing evidence invalidates that stage and every downstream stage.
- Signature readiness requires a non-empty exact current signer set for each applicable Term Sheet,
  Loan Agreement, PoA, tri-party, and SH-4 path. The approval owner supplies the exact S32 CFO/two-
  Director requirement; the legal owner reconciles mismatch resolution row, renderer, audit,
  version, and workflow truth and fails closed on malformed frozen approval facts.
- Read scope now admits active persisted Senior Finance, Credit Manager, CFO, and explicitly
  audit-scoped Auditor users only with the readiness permission and their canonical loan scope.
  Pre-009E CFC remains absent, Credit excludes recovery/closed/archive states, and origination
  assignment, role, permission, missing ids, or cross-object facts alone remain nondisclosing.
- `disbursements.modules.disbursement_readiness.evaluate` is again the sole readiness composition
  interface. It consumes the established typed security-evidence coordinator directly, retains 23
  ordered safe checks and exact 009B3C SAP truth, reaches only A-126 with genuine owners, and is
  zero-write with a complete-path bound of 250 queries. 009E/009F now declare their required
  PostgreSQL race capability and must consume/freeze this one canonical decision rather than
  reimplement owner predicates.

## 009B3C Current SAP Evidence and Adapter Contract Closure

- Repair `2026-07-16_231945_repair` restored the pre-existing genuine readiness integration fixture
  by supplying distinct request ids to its SAP send and completion actions. The new current-evidence
  contract intentionally requires that traceable audit context; no production predicate or public
  behavior was relaxed.
- `sap_workflow` now emits its immutable code decision only for one singular exact send tuple
  (audit/workflow/communication/task/delivery/workbook) and one singular exact completion tuple
  (audit/workflow/code/reuse/input digest). Every safe audit-body field is sealed and reconciled;
  file bytes are a genuine retained XLSX whose plaintext checksum matches delivery truth.
- Missing, extra, duplicate, changed, cross-linked, or rehashed semantically wrong evidence fails
  closed. The masked-code read, delivery capability, and workbook download all consume the same
  owner evidence, preserving existing 403/409 taxonomy without exposing code/capability/workbook.
- Manual, Fake, and Future share one local validation/idempotency contract. Exact replay returns the
  original reference; changed key/request/file/assignee/name/MIME/bytes/checksum, malformed status/
  reference/result, and Future bypass attempts are rejected before a second transport invocation.
  Denied public sends retain the draft and create no communication/task/audit/workflow/code truth.
- No schema, response shape, real SAP/email transport, Finance policy import, or parallel selector
  was introduced. Pre-closure ledgers without the complete sealed evidence remain honestly absent
  from downstream current truth.

## Architecture Review 2026-07-16 21:37 — Current SAP, Approval, and Reader Closure

- 009B3A/B substantively establish canonical SAP model/policy/adapter ownership without a Finance
  cycle. The shared adapter contract remains happy-path only, and a changed send-audit assignee still
  yields a current SAP code because the decision reconciles only part of the delivery evidence.
  `009B3C` requires one singular complete send/completion ledger and shared Manual/Fake/Future
  negative contracts.
- 009D2 substantively replaces shallow legal/security labels and origination assignment with owner
  decisions. Independent probes found all three approvals survive a changed current completion
  version, while Credit Manager, CFO, and Auditor are hard-rejected despite auth §26.5 read grants.
  Approval completion ids also lose order and sibling-ledger singularity. `009D3` restores exact
  current ordered approvals/signers, the full §19.3/§26.5 reader matrix, and the named deep readiness
  boundary. `009E` now waits for 009D3.

## 009B3B SAP Policy Owner Closure

Executable SAP policy and Manual/Fake/Future adapters now live only in `sap_workflow`; Finance keeps
the object-identical model alias, standard 409 taxonomy is restored, and downstream modules consume
only the immutable SAP decision. No schema, route, ciphertext context, or retained evidence changed.

## 009D2 Readiness Evidence and Loan Scope Closure

- Readiness now consumes the checklist owner's exact completion and ordered-approval reconciliation,
  the signature owner's current signer/mismatch decision, coordinated security terminal evidence,
  and the SAP owner's newest-request/completion decision. Mutable labels and stale/forged ledgers do
  not pass.
- Senior Manager Finance loan scope is the active assignee of the newest persisted SAP request for
  the exact application/member. CFC scope remains absent until 009E creates the source-defined
  initiated-disbursement relation; application intake assignment is never loan scope.
- Blank-cheque custody and cancelled-cheque linkage remain unconditional readiness requirements.
  Only SH-4 and CDSL use owner applicability. The source-bank check remains the honest A-126 blocker.

## Architecture Review 2026-07-16 14:37 — Owner, Evidence, and Loan-Scope Closure

- 009B2's public `sap_workflow` module still imports Finance models, encrypted storage, and the
  request/send/complete/read implementations. That facade leaves Finance as policy owner and creates
  a Finance↔SAP dependency. Oversized `009B3` is split into `009B3A`, which performs the state-only/
  non-destructive owner migration while preserving all tables/ids/ciphertext/digests/history, and
  `009B3B`, which keeps Manual/Fake/Future adapters in the SAP owner and removes executable
  SAP→Finance edges.
- 009D legal readiness trusts mutable item/checklist statuses and non-null approval ledger ids rather
  than exact current completion/approval identities. It also filters unverified signature rows, so
  one open mismatch can become `all([]) == true`, contrary to S34 and M06-FR-019.
- 009D security readiness checks shallow statuses and event-id presence instead of the coordinated
  terminal contracts for exact PoA ₹500 evidence, SH-4/CDSL facts, cheque custody/bank linkage,
  checksums, maker-checker identity, and event content. It authorises through application intake
  assignment rather than the separate loan/disbursement scope in auth §§19.3/26.5.
- `009D2` must reconcile all current source-owner evidence, ignore pending items only when the owner
  says they are inapplicable, evaluate every mismatch, use canonical loan scope, and prove a genuine
  all-pass public response without mocking owner projections. `009E` now depends on this closure.

Sources distilled while sharpening 009A on 2026-07-15: `implementation-roadmap.md` §14,
`integrations.md` §8/§33.1, `data-model.md` §19.1-19.2, `api-contracts.md` §29.1, and
`functional-spec.md` BR-047-BR-050/M07-FR-001-M07-FR-010.

## 009B3A Retained Model-State Truth

- `sap_workflow.models` is the canonical Django owner of `SapCustomerProfileRequest` and
  `SapCustomerCode`; both retain the exact Finance-era table, field, index, constraint, relation,
  id, ciphertext, checksum, digest, lifecycle, and evidence identities.
- `sap_workflow.0001_sap_model_owner_state` is one reversible state-only operation. It emits no
  schema/data SQL and rewrites only historical model ownership plus relation targets, including the
  existing nullable `LoanAccount.sap_customer_code` state.
- `finance.models` is a one-way, policy-free compatibility import whose exported names are identical
  canonical class objects. Executable Finance request/delivery/completion policy remains untouched
  until 009B3B moves it behind the SAP owner.
- Forward/reverse migration manifests compare exact synthetic encrypted tokens, file/delivery
  checksums, completion digest, all request/code foreign keys, audit/workflow identities, physical
  tables, and introspected constraints/indexes. The existing three request/code race tests pass
  twice on PostgreSQL, with two rounds per test.
- Repair `2026-07-16_192241_repair` made historical credit and witness migration-test projections
  exclude the new downstream `sap_workflow` leaf. This restores explicit pre-migration state/schema
  isolation; the SAP transfer operation and its zero-SQL runtime/model contract remain unchanged.
- Repair `2026-07-16_194722_repair` restored migration leaves after the historical legal-document
  ownership tests. Without that teardown, their reversed schema contaminated the following SAP
  transfer fixture in full-suite order even though the SAP test passed alone. The exact ordered
  repro and the 19-test migration set now pass; production migration/model behavior is unchanged.

## Architecture Review 2026-07-16 07:41 — SAP Delivery, Replay, Audit, and Owner

- Source codebase-design §§16.1/20.3-20.4/36.2 assigns SAP policy to
  `sap_workflow.modules.sap_customer_profile` behind one Manual/Fake/Future adapter contract. 009A/B
  currently implement it directly in `finance`; 009B2 restores the source owner before loan-account
  and readiness code consume SAP truth.
- Integrations §8.1 says the official Finance handoff includes the Excel details. An executable probe
  found a row marked `sent` while the communication remained pending, had no attachment/capability,
  linked only to completion, and the frozen assignee received 403 for the workbook. 009B2 makes exact
  checksum-verified Annexure delivery/assignee read prerequisite to `sent`.
- 009B reuse completion retains only the code link, so optional values omitted on first completion
  can be added later and still receive replay 200. 009B2 freezes the canonical accepted input/digest
  and makes any later supplied/omitted difference a zero-write 409.
- Auth-permissions §30 requires `sap.customer_code_created` plus role/team at action time. 009B2
  aligns create/send/confirm/reuse audit truth without exposing identity/bank/workbook plaintext.
- 009C now uses `loans.modules.loan_account_lifecycle` and the public SAP selector; 009D uses
  `disbursements.modules.disbursement_readiness`, matching codebase-design §§16.2-16.3.

## 009B2 Closed Contract and M07 Traceability

- `sap_workflow.modules.sap_customer_profile` is the public workflow owner. Its manual/fake adapter
  contract accepts exact decrypted Annexure-I bytes plus plaintext checksum and returns an
  idempotent delivery identity; retained Finance tables remain a compatibility/data-history seam.
- The frozen assignee obtains a short-lived, replaceable, one-use capability and reads the exact
  retained workbook through an audited nondisclosing route. The manual task contains neither file
  ids nor token material, and no real SAP/email service is called.
- Completion retains a canonical supplied/omitted-aware digest. New code emits
  `sap.customer_code_created`; reuse emits `sap.customer_code_reused`; create/send/read/download/
  denial evidence freezes safe actor role/team/request/network facts.

| Requirement | Retained implementation truth after 009B2 |
|---|---|
| M07-FR-001/002 | Public owner resolves one coherent active exact-member code; database uniqueness and reuse/race locks prevent duplicate customer identities. |
| M07-FR-003/004/005 | 009A retains the post-sanction request and encrypted genuine Annexure-I from canonical source facts. |
| M07-FR-006 | `sent` requires manual-adapter acceptance, a frozen delivery identity, and an assignee task/capability path for the exact workbook. |
| M07-FR-007 | Only the frozen active Senior Manager Finance assignee can complete the sent request; exact canonical replay is enforced. |
| M07-FR-008 | The completed request binds the active member code and originating application; downstream modules receive only the public immutable decision. |

## 009A SAP Customer Profile Request

- MVP is manual/file-first. After terminal sanction, a Credit Manager creates the request and a
  genuine Excel/Annexure-I artifact for an active Senior Manager Finance assignee; direct SAP API
  integration is future scope.
- `POST /api/v1/loan-applications/{id}/sap-customer-profile-request/` returns the request id,
  `draft` status, Excel file id, and assignee. Canonical borrower/application/sanction facts should
  be server-owned even though the illustrative API body lists them, so a caller cannot forge the
  source evidence.
- Required frozen facts are application number, legal name/type, PAN, registered address, folio,
  sanctioned amount/date, individual-only Aadhaar, and optional email/mobile/current verified-bank
  last-four plus IFSC. Full sensitive values are encrypted at rest and excluded from ordinary
  projections/log/audit evidence.
- The table stores application/member, status (`draft/sent/completed`), requester, assignee, frozen
  fields, linked Excel file, and sent/completed timestamps. Source idempotency identity is
  application plus active request; retries/concurrent creates must not duplicate request, file,
  workflow, or audit facts.
- INT-SAP-001/002/006 and R5-AC-001/002 require post-sanction creation, complete Excel details, and
  audit evidence. Code confirmation, duplicate-code blocking, reuse, and readiness belong to 009B+
  and must not be claimed by 009A.
- Source schema says Aadhaar is non-null while the integration payload says “individual only” and
  the platform supports FPC borrowers. Treat Aadhaar as conditionally required/encrypted for
  individuals and absent for FPCs; do not fabricate an FPC Aadhaar value.

## 009B SAP Request Send, Confirmation, and Reuse

- API §29.2 and integrations §8.2 make `draft -> sent` a real boundary: the Credit Manager sends the
  retained Excel request to its frozen Senior Manager Finance assignee through the communication/
  task adapter. No later slice owns this transition, so 009B must deliver it before confirmation.
- API §29.3 uses `/complete/` and fields `sap_customer_code`, optional `sap_vendor_code`,
  `created_at_sap`, `confirmation_document_id`, and `confirmation_notes`. Preserve this source
  vocabulary instead of inventing a `/confirm/` route or renamed payload fields.
- BR-047/048/050 and M07-FR-001/002/007/008 require one member-level unique active code, assigned
  Senior Manager Finance confirmation, and reuse instead of duplicate creation. Global code
  uniqueness and one-active-code-per-member are database-backed; request/code races retain exact
  winner evidence and zero loser artifacts.
- The source ties reuse to an existing outstanding loan, but Epic 009 has not yet created the loan-
  account owner and OC-019 leaves multi-active-loan semantics open. Reusing an already active code
  for the exact member is conservative; do not infer outstanding state from identity text or invent
  loan statuses. 009C+ may add governed outstanding-loan linkage without rewriting code history.
- Confirmation evidence is optional but recommended and must be a restricted request/application-
  scoped file. Send/complete/read responses and all audit/workflow/communication facts exclude the
  frozen Aadhaar, PAN, address, bank, storage, and signed-capability values.

## 009C Loan Account Creation

- API §30.1 fixes `POST /api/v1/loan-applications/{id}/create-loan-account/` with exactly
  `sanction_decision_id` and `loan_account_number`. Data-model §18.1 makes application and account
  number unique and requires the exact sanction link, positive amount, member, status, balances,
  loan type, rate type, and optional active SAP-code link.
- Initial `loan_account_status` is source vocabulary `sanctioned`; activation belongs only to
  successful disbursement (M08-FR-008). Before transfer, disbursed amount and all outstanding
  balances remain zero so account creation cannot claim a funded receivable.
- Create `loan_terms` atomically from the current terminal sanction/frozen review package: safe
  borrower/nominee/shareholding snapshots, short/long facility type, amount, purpose, governed
  interest/repayment/penalty/charge/security/dispute facts, and current Term Sheet/Loan Agreement
  links where their owner proves them. Missing required governed terms fail closed; do not fill the
  known terminal-sanction nulls with guessed rates or dates.
- `finance.loan_account.create` is source-defined Critical authority but no source role is granted
  it (A-121). Implement exact permission/object checks and explicit-grant tests without seeding a
  role grant. Replay is application + exact sanction + exact normalized account number; changed
  repeats conflict and PostgreSQL races retain one account/terms/status/audit/workflow winner.

### 009C retained implementation truth

- `loans.modules.loan_account_lifecycle` owns one atomic create/replay interface and the exact
  §30.1 HTTP route. Its initial migration creates protected account, nullable legal/SAP links,
  immutable one-to-one terms, append-only status history, positive/non-negative constraints,
  globally canonicalized account-number uniqueness, and future-compatible balance/status columns.
- Creation freezes safe borrower/nominee/active-shareholding facts only when they equal the current
  latest approved case snapshot. Governed dispute text comes from the frozen approval facts, never
  from unrelated sanction conditions precedent. The legal owner locks the newest Term Sheet and
  Loan Agreement first and rejects it if that current row is not executed, verified, and renderer-
  valid; it never falls back to an older eligible document.
- The public SAP owner now accepts a trusted `for_update` read so account creation locks the active
  code and completed-request decision without importing Finance models or adapter/storage details.
  Missing/inactive/cross-member/cross-application decisions retain an honest nullable account link.
- Success retains one `sanctioned` account with all balances zero, one terms row, one status-history
  row freezing application/member/sanction/SAP/terms/outcome provenance, one safe audit, and one
  workflow event. Exact replay writes nothing; changed application replay and globally equivalent
  case/whitespace account numbers conflict with no partial evidence.

## 009D Disbursement Readiness

- API §31.1 fixes a read-only
  `GET /api/v1/loan-accounts/{loan_account_id}/disbursement-readiness/` projection with one aggregate
  flag and ordered pass/fail checks. The API example names sanction, documentation, security, SAP,
  and verified bank; integrations §9.4 and M08 expand those into the complete pre-initiation gate.
- Consume current facts through the approval, legal/checklist, security, application-bank, SAP,
  loan-account, and configuration owners. Conditional exception/general-meeting, SH-4/CDSL, and
  signature checks must never disappear from the response or be inferred from copied status JSON.
- The source workflow orders readiness before Senior Manager Finance initiation and CFC
  authorisation. Those are 009E/009F actions, not readiness rows or synthetic pass conditions; the
  readiness GET creates no payment, approval, balance, account-state, task, communication, audit, or
  borrower truth.
- Fail closed when current relationships/evidence are absent, stale, cross-object, or incoherent.
  If no governed active source-bank configuration owner exists yet, return an honest failed
  `source_bank_account_configured` check rather than inventing an account.

### 009D retained implementation truth

- `disbursements.modules.disbursement_readiness.evaluate(actor, loan_account_id)` owns the shallow
  read-only coordinator and §31.1 route. The account resolver enforces active persisted Senior
  Manager Finance/CFC authority, exact application object scope, and a sanctioned account/terms
  projection; approval, legal, security, application-bank, SAP, and configuration owners retain
  their policy decisions behind bounded selectors in one transaction.
- The response always emits 23 stable source-ordered checks. Conditional exception/general-meeting
  and SH-4/CDSL paths pass only when inapplicable or their exact current owner evidence is terminal;
  current legal documents, ordered checklist signatures, bank decision, SAP linkage, and amount are
  independently fail-closed. Failed reasons are safe and no source evidence payload is returned.
- A-126 records the missing governed source-bank owner. Production truth therefore remains honestly
  blocked on that named check until 009E or a prerequisite supplies the source account lifecycle;
  tests prove the complete public passing contract through the owner decision seam without seeding
  or inventing an RBL account.

## 009E Payment Initiation

- API §31.2 fixes `POST /api/v1/loan-accounts/{id}/disbursements/initiate/`, required
  `Idempotency-Key`, amount, borrower-bank id, source-bank id, and final-verification comments. The
  response is only the disbursement id plus `initiated`/`pending`/`pending` initiation,
  authorisation, and bank-transfer statuses.
- Integrations §§9.1-9.6 define MVP as a manual RBL bank-portal record: Senior Manager Finance
  performs final verification and initiates; CFC authorisation, transfer success, UTR/evidence,
  register update, and borrower advice remain later actions. Initiation must consume the full 009D
  readiness pass, not reimplement or trust caller-supplied readiness.
- Data-model §19.3 retains account/application, amount, borrower/source bank, maker, later nullable
  checker/UTR/time/advice, initial statuses, and register flag. The amount cannot exceed sanction;
  success cannot occur before CFC authorisation. Auth-permissions assigns
  `finance.disbursement.initiate` to Senior Manager Finance and keeps CFC authorisation separate.

## 009F CFC Authorisation/Rejection

- API §31.3 fixes `POST /api/v1/disbursements/{id}/authorise/` with only decision and comments.
  Integrations §§9.1/9.2/9.6 make this the CFC's independent manual-bank approval/rejection record;
  it is not transfer execution and cannot create a UTR or activate/fund the account.
- Auth §§15.7/16.3/26.5 require active CFC authority with
  `finance.disbursement.authorise`; 009E's Senior Manager Finance maker must be a distinct user.
  The exact pending initiation/readiness/bank evidence is frozen and checked transactionally.
- §45 does not list authorisation as an idempotency-header endpoint. Exact terminal replay may return
  the retained result with no writes; changed/opposite decisions conflict. PostgreSQL races must
  retain one complete CFC decision/audit/workflow/task winner and no loser success evidence.

## 009H4 retained implementation truth

- Communications stores advice-intent identity as a primitive unique UUID and owns the canonical
  outbox, provider-attempt, receipt, and terminal Communication chain without a persistent import or
  FK to disbursement policy.
- Every dispatch freezes the complete template source/provenance/checksum and rendered payload.
  Accepted provider evidence is immutable and seals all ordered rejected sibling digests; replay
  rejects any changed, missing, duplicate, extra, or cross-linked retained fact.
- One communications migration preserves exact physical UUID columns/history, backfills singular
  coherent pre-outbox deliveries without calling transport, and leaves incomplete/ambiguous legacy
  history non-current. Its reverse refuses after runtime provider evidence exists.
- Finalization links the outbox to its receipt and Communication with protected one-to-one edges in
  the same transaction. Both crash windows and two PostgreSQL five-caller races recover to one
  provider acceptance and one complete local chain.

## 009I retained implementation truth

- MP14 reads one zero-write own-application projection rooted only in the active portal account's
  member. Current owner decisions prove sanction, initiation, CFC decision, post-transfer funding,
  and finalized advice; incoherent terminal claims fall back to safe blocked copy.
- The response is an allowlisted six-stage borrower timeline with decimal amounts, UTC timestamps,
  and destination/reference last four only. It never exposes SAP values, full UTR/account data,
  actors, comments, permissions, checksums, or internal evidence identities.
- Finalized advice is downloadable only through a 15-minute signed replacement capability bound to
  portal/member/application/account/advice/file/checksum/version and consumed once. Issuance and
  accepted/denied reads share the safe `portal.document.downloaded` audit vocabulary.
- Under A-133 the retained communications subject/body is the exact UTF-8 advice attachment until a
  governed document-template owner defines another artifact format.

## 009I2 portal stage and visual closure

- MP14 receives only the application id explicitly selected by the portal container; it does not
  fetch, rank, or infer an application from client-owned status strings.
- Documentation and SAP completion are independent owner booleans with independent owner times, so
  a proved stage can retain an honest null time. A later loan may reuse the member's active SAP code
  when its loan account binds that exact code identity.
- Payment, CFC, transfer, and advice stages retain their exact initiation, authorisation, transfer,
  and provider-accepted times. Queued or incoherent advice remains unavailable, and stale/mixed
  evidence stops at the last provable borrower-safe stage.
- Trusted browser acceptance uses real Django login, application list, and selection plus an exact
  MP14 status-route scenario seam for the three declared screenshot states; the orchestrator owns
  the twice-run browser gate and screenshot artifacts.

## 009H9A queued-advice migration provenance closure

- Communications migration 0008 now distinguishes a genuine H5 queued job from an unlinked
  attempt-less legacy row at the earliest truthful boundary. Verification requires the singular
  outbox/job edge, exact advice and payload identities, complete actor/request facts, pristine
  queued/zero-attempt state, no provider/receipt/final history, and an internally recomputed frozen
  template checksum.
- Missing jobs and one-field drift in job/outbox/advice/payload/actor/request/status/checksum or
  snapshot remain `legacy_partial / ambiguous_legacy`; migration 0008 clears their untrusted
  template facts and neither reconstructs history nor weakens H6's replay/download exclusions.
- A genuine queued fixture preserves every old job/outbox id, attempt, actor, request, digest,
  idempotency, snapshot, and timestamp through 0007-to-current, safe reverse, and reapply. No later
  migration, schema, provider/receipt/Communication, action/audit/workflow, API, or frontend change
  is part of this closure.

## 009H9B communication final-attempt and exception-queue closure

- `CommunicationDispatcher.retry_failed` now locks and terminalises both an expired running claim
  at its retained `max_attempts` and an already-exhausted queued/retrying row left by the prior
  recovery behaviour. Attempts never increment during recovery; exact-cap terminalisation sets
  `failed`/`worker_crash`, clears the claim/lease, retains provider acceptance, records recovery at
  most once, and never returns the row as due.
- One protected communications-owned exception row freezes the configured provider adapter, job
  type, related entity, safe failure code, exact retry count, assigned original actor, and nullable
  resolution facts. One urgent task points to the current-owner-only detail route. Projection omits
  recipient/content, provider id/error/secret, bank/UTR, key/payload/request, and actor-network facts.
- Current assigned generic/advice senders can list/detail their rows and manually close them with a
  version token. Unsupported post-cap retry, stale/foreign/resolved requests, and changed exhausted
  job evidence fail closed. Closure preserves failed attempts and accepted provider truth, never
  calls a provider or marks delivery sent, and appends one audit/workflow chain.
- Local focused tests cover exact/below/already-exhausted recovery, repeated scans, stale claims,
  generic/advice failure classes, redaction, authority/staleness, changed evidence, and accepted
  provider crash closure. Two PostgreSQL executions of the five-scanner/five-worker terminal race
  retain one job/exception/task/audit/workflow winner, no fourth attempt, and no provider call.

## 009L post-completion PostgreSQL proof — 2026-07-19

- The 009L run completed its full gates and twice-run browser contract, but its slice metadata did
  not request an independent PostgreSQL lane for the successful-transfer/SAP-posting race.
- Owner maintenance therefore executed the two exact
  `DisbursementTransferSuccessRaceTests` methods twice against separate PostgreSQL test databases at
  commit `de3d0f0c`. Both repetitions discovered and ran exactly two tests, reported `OK`, and
  destroyed their isolated databases. The tests retain one transfer winner and one initial-payment
  SAP posting obligation.
- No 009L product change or status rewrite was needed. Future financial slices declare exact
  `Trusted PostgreSQL Acceptance` labels/counts and the orchestrator runs each contract twice.
