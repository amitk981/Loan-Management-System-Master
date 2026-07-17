# Epic 009 Digest — SAP, Loan Account, and Disbursement

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
