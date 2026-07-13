# Review Findings

Independent review log, written by architecture-review runs (newest first). Each entry lists: slices reviewed, findings (severity + plain-English description), and the corrective slice or ADR created for each significant finding. The owner can read this file to see what the independent reviewer thought of recent work without reading code.

## 2026-07-13 06:01 - Architecture Review 2026-07-13_055322_architecture_review

Reviewed completed product work since architecture-review commit `23331d5`:
- `006Z11-member-scope-assignment-and-list-nondisclosure-closure` (`6afd173`)
- `006Z12-portal-limit-denial-matrix-evidence-closure` (`46b47c0`)
- `007A2-approval-configuration-history-and-committee-authority-closure` (`7359389`)
- `007A3-approval-matrix-maker-checker-governance` (`955cfc1`)

The review checked `git diff 23331d5...955cfc1`, production/test hunks, retained red/green and
PostgreSQL evidence, Epic 006/007 digests, cited source sections, BR-003..007, M02-FR-004..006,
M04-FR-005..007, and M05-FR-003..006. Standards and spec fidelity were reviewed independently.
Production code was not changed. `CONTEXT.md` remains truthful, and state/files contain no Blocked
slice to reopen.

### Standards

#### Finding 1 - High - PostgreSQL races still exercise the pre-governance activation interface

`ApprovalMatrixConcurrencyTests` still calls `create_rule`/`create_committee` and expects those calls
to activate one row, reject one contender, and return effective entity ids. After 007A3 those calls
only create pending proposals, so both contenders can create proposals and the supersede tests index
ids that are no longer returned. The retained 007A2 PostgreSQL logs genuinely ran all four tests
twice, but they predate migration 0005 and the governed activation seam; 007A3 declared no
PostgreSQL capability. This violates DECISION_POLICY §2 and codebase-design §§22.3/26.1-26.3's
current-interface concurrency proof. `007A4` replaces them with approval-time proposal races and
requires two post-007A3 PostgreSQL runs.

#### Finding 2 - Medium - Persisted member scope is valid only when callers invoke model validation

`MemberScopeAssignment.clean()` rejects invalid scope/member/team shapes, but migration 0013 adds no
database checks. Its nullable five-column unique constraint also permits duplicate `global` and
`created_by` rows under PostgreSQL null semantics. Public writers do not yet expose this directly,
and duplicates are currently behaviorally harmless, but a security authority seam must remain valid
through bulk/import/admin paths that bypass `save()`. This conflicts with codebase-design §27.1's
deep Object Access boundary. `006Z13` adds conditional constraints/uniqueness and migration proof.

#### Finding 3 - Medium - Any authenticated user can read Critical configuration proposals

Rule and committee reads use `approvals.matrix.read`, while `proposal_detail` calls only
`authenticated_user` and returns the change reason, maker/checker ids, and action eligibility. This
drifts from API design §3's permission-aware boundary and auth §31.1's Critical Approval Matrix
governance. `007A4` defines and tests a source-backed reader/participant/checker contract without
role-name inference.

No frontend files changed. 006Z12's redacted public denial ledger is complete and uses real state
assertions. 006Z11 genuinely removes permission/role provenance as global member scope and preserves
all service-evidence makers; the remaining persistence/action-matrix items above are closure quality,
not evidence that the prior unsafe behavior remains in production.

### Spec

#### Finding 1 - High - 007A3's governed activation race is missing and its inherited race suite is broken

007A3 requirements 5-6 and its test matrix require approval-time revalidation plus a competing
activation with a complete zero-write loser. The implementation plausibly serializes approval via
the shared lock, but no test races `decide_proposal`; the only PostgreSQL suite calls the obsolete
immediate-activation interface. The prior missing-PostgreSQL finding was closed at the 007A2 commit
and reopened by 007A3. `007A4` owns governed create/supersede races for rules and committees.

#### Finding 2 - Medium - Approval authority denial uses a noncanonical public error code

Source API contracts §7.1 defines `APPROVAL_AUTHORITY_REQUIRED`. The module, view, tests, and working
contract instead introduced `APPROVER_AUTHORITY_REQUIRED`. `007A4` aligns production and evidence
to the existing canonical code.

#### Finding 3 - Medium - Open-case immutability and complete proposal loser state are unproved

007A3 requires existing approval-case snapshots to remain unchanged across proposal, rejection,
activation, and later reads. No 007A3 test creates an `ApprovalCase`; `_configuration_snapshot()`
omits both cases and proposals, so its claimed complete loser checks could miss partial proposal or
case mutation. `007A4` adds a real open-case fixture and exact full-state equality across decisions
and races, satisfying auth CFG-007.

#### Finding 4 - Medium - Required committee/lifecycle and malformed-input matrices are partial

007A2 asks for inactive/duplicate/swapped committee authority, historical/current committee
resolution and backfill conflict, separate malformed/unknown/non-finite zero-write matrices for both
resources, and both collection contracts. Tests cover ordinary-as-CFO, one current/absent resolver,
one rule non-finite row, rule pagination, and committee unknown parameters; the implementation is
plausible but the stated acceptance matrix is not complete. `007A4` finishes these public rows
alongside the governed activation matrix.

#### Finding 5 - Medium - 006Z11's calculation/action acceptance matrix remains partial

006Z11 requires the common scope across calculation and independently selected public module/HTTP
rows for every member action. The production call paths now enforce scope around mutations and the
portal derives its own member, but `ActiveMemberStatusModule.calculate` is actorless and the new
slice test covers only list/detail/count. Existing tests distribute happy paths across fixtures and
some patch the evaluator; they do not prove permission-without-scope denial then assignment-enabled
behavior for every action. `006Z13` maps every calculation caller and adds the real public matrix.

No material scope creep was found. 006Z12 fully closes the prior portal denial matrix and retains
M04-FR-005..007. 007A2 closes sequential lifecycle/committee authority/pagination behavior and 007A3
closes unilateral activation sequentially. M05-FR-003..006 remain partial until governed concurrency
passes in 007A4 and real case routing lands in 007B. BR-003..007 and M02-FR-004..006 behavior is
substantive, with the remaining public authority proof assigned to 006Z13.

No ADR was added because existing auth, API, data-model, and codebase-design sources already decide
object-scope persistence, canonical error vocabulary, Critical configuration access, CFG-007, and
approval-time concurrency.

Summary: Standards found 1 High and 2 Medium issues; the worst is obsolete PostgreSQL concurrency
evidence. Spec found 1 High and 4 Medium issues; the worst is missing/broken governed activation
race proof.

## 2026-07-13 04:49 - Architecture Review 2026-07-13_044409_architecture_review

Reviewed completed product work since architecture-review commit `190eb5c`:
- `006Y16-witness-parent-scope-and-contract-closure` (`c1cc2e6`)
- `006Z9-active-member-authority-and-decision-contract-closure` (`fa89d4f`)
- `006Z10-portal-limit-interaction-and-boundary-proof` (`a6dd3cd`, including repairs)
- `007A-approval-matrix-configuration` (`a614f05`)

The review checked `git diff 190eb5c...HEAD`, production/test hunks, retained red/green,
PostgreSQL, and two-run trusted-browser evidence, Epic 004/006/007 digests, cited source sections,
and BR-003..007, M02-FR-004..006, M04-FR-005..007, and M05-FR-003..006. Standards and spec
fidelity were reviewed independently. Production code was not changed. `CONTEXT.md` remains
truthful, and `.ralph/state.json` contains no Blocked slice to reopen.

### Standards

#### Finding 1 - High - Critical approval configuration activates without business approval or reason

`approval_matrix_configuration.py` immediately activates rule/committee creates and supersessions,
stores the initiating user as both VersionHistory author and approver, and accepts no change reason.
This violates auth §§31.1-31.2: Approval Matrix requires Admin + CFO/CS approval, CFG-001 requires a
reason, and CFG-005 requires activation audit. The tests positively encode unilateral activation.
`007A3` adds a pending proposal plus distinct CFO/CS approve/reject boundary and coherent reason,
version, audit, and open-case snapshot evidence.

#### Finding 2 - High - Committee fields accept users without CFO/Director authority

`_validate_committee` checks only that three user ids exist and differ. It accepts inactive ordinary
users in the CFO/two-Director positions; its test succeeds with arbitrary `cfo_test` and
`director_test` roles. This violates auth §16.2's backend authority rule. `007A2` validates active,
persisted CFO/Director authority and adds a dated committee resolver.

#### Finding 3 - High - The declared PostgreSQL gate never executed 007A's races

007A added two `ApprovalMatrixConcurrencyTests`, skipped them under SQLite, and declared
`postgresql-five-race-acceptance`. Both retained PostgreSQL logs ran only the five older credit,
appraisal, and sanction tests, while `postgresql-acceptance-results.md` reported PASS. The required
overlap/supersede one-winner proof therefore has no PostgreSQL execution evidence. `007A2` requires
two direct PostgreSQL executions with exact test names. The independent validator's fixed command
lives in protected `scripts/ralph-validate.sh`; this review records that owner/orchestrator follow-up
is still required because an architecture run may not edit protected scripts.

#### Finding 4 - Medium - Configuration collections are unbounded and unpaginated

Both list functions materialize the complete table and return a plain success envelope. API
contracts §§6.2/8 require the standard paginated list envelope, and codebase-design §§7.2/25 require
bounded selectors and consistent HTTP interfaces. `007A2` adds deterministic pagination,
unknown-parameter rejection, and public boundary tests.

No material standards violation was found in 006Y16, 006Z9's route/decision logic, or 006Z10's
mounted/browser implementation beyond the spec-completeness issues below.

### Spec

#### Finding 1 - High - 007A's mandatory PostgreSQL acceptance is missing

007A explicitly requires competing create/supersede one-winner proof and discriminating date/amount
fixtures. The new tests are skipped in the ordinary suite, and the retained PostgreSQL command does
not select them. Sequential seeded resolution passes, but authoritative configuration concurrency
remains unproved. `007A2` owns direct two-run PostgreSQL evidence and the complete historical race
matrix. M05-FR-003..006 remain partial until it passes.

#### Finding 2 - High - 006Z9 turns action permissions into global member scope

006Z9 required a documented/configurable scope and forbade permission/role provenance as a global
substitute. `member_authority.py` instead makes `members.member.read`, active-status verify, and
identity approval globally valid for every permission holder. Its test now gives an arbitrary
outsider all-member detail access, contradicting auth §25.1's “scope-limited unless management
role” rule. `006Z11` separates action permission from persisted/configured global/team/assigned/
created-by scope and makes list/detail/actions share it. BR-003..007 and M02-FR-004..006 remain
partial on authority until closure.

#### Finding 3 - Medium - Service-evidence maker history can be erased

006Z9 says an evidence creator or material updater cannot verify the derived decision. Service
evidence update overwrites `verified_by_user`, and verification checks only that current field.
Actor A can create, actor B can update, then A is no longer detected as a maker. `006Z11` preserves
immutable creator/updater provenance and adds the public three-actor zero-write test.

#### Finding 4 - Medium - 006Z10's denial matrix and zero-write ledger remain partial

The retained backend matrix covers future/closed/manual/mismatched authority, changed service
evidence, duplicate shares, contradictory acreage, no policy, and invalid amounts. It omits the
slice's stale-authority, changed-supply, missing-profile, and missing-land rows, and its evidence
snapshot omits LoanLimitAssessment. `006Z12` completes independently selected public cases and the
full member/assessment/application/audit/workflow/configuration before/after ledger. M04-FR-005..007
calculations and the real submit/browser lifecycle pass; blocked-boundary proof remains partial.

#### Finding 5 - Medium - 007A lifecycle/history fidelity is incomplete

The source calls for active/inactive effective-dated rules and protection of already-referenced
history. The resolver currently queries every status, while create overlap checks only active rows;
a later backfill can overlap a superseded historical row and make a previously unique decision date
ambiguous. Tests construct no referenced case and cover only selected create losers. `007A2`
defines lifecycle resolution, full-history non-overlap, committee parity, and referenced-snapshot
proof; `007A3` covers governed activation.

No material scope creep was found. 006Y16 satisfies its authority-first witness 403/404 contract.
006Z9's decision-route agreement and core active-member business facts pass subject to 006Z11's
authority/maker closure. 006Z10's lower-of-two calculations and routed submit/refetch/reload proof
pass subject to 006Z12's denial ledger. 007A's seeded exact/above/exception facts pass sequentially,
but M05-FR-003..006 remain partial until 007A2/007A3.

No ADR was added because the cited auth, API, data-model, functional, and codebase-design sources
already decide permission/scope separation, maker-checker governance, effective history,
pagination, and interface-level concurrency proof.

Summary: Standards found 3 High and 1 Medium issues; worst are unilateral Critical configuration
activation, unvalidated committee authority, and falsely incomplete PostgreSQL acceptance. Spec
found 2 High and 3 Medium issues; worst are the missing PostgreSQL proof and permission-implied
global member scope.

## 2026-07-13 03:00 - Architecture Review 2026-07-13_025409_architecture_review

Reviewed completed product work since architecture-review commit `c31ac79`:
- `006X10-credit-object-scope-executable-row-closure` (`40cea5e`)
- `006Y15-witness-authority-matrix-behavioral-closure` (`81884ed`)
- `006Z7-active-member-relaxation-authority-and-evidence-race-closure` (`a2c857c`)
- `006Z8-portal-limit-provenance-module-and-interaction-closure` (`53420e7`, including repairs)

The review checked `git diff c31ac79...HEAD`, production/test hunks, retained red/green,
PostgreSQL, and two-run trusted-browser evidence, Epic 004/006 digests, cited source sections, and
BR-003..007, M02-FR-004..006, and M04-FR-005..007. Standards and spec fidelity were reviewed
independently. Production code was not changed. `CONTEXT.md` remains truthful, and state/files
contain no Blocked slice to reopen.

### Standards

#### Finding 1 - High - Member global authority is inferred from role metadata

`members/modules/member_authority.py` treats `Role.is_system_role` plus either verify/identity-
approval permission as global authority over every owned member, while member read/update has no
explicit management-global path and unowned rows silently become global. System-role provenance is
not an object-scope assignment and does not implement auth §§3/19's explicit global/team/assigned/
created-by vocabulary. The new test calls an unowned-row fallback “global” while expecting a
permissioned manager to be denied an owned row. `006Z9` owns one source-reviewable member scope
projection and behavioral parity across Registry and active verification.

#### Finding 2 - High - Portal financial boundary lacks blocked-path tests

The credit-owned borrower-limit projection has a happy next-day endpoint case and unavailable-no-
authority case, but no direct observable matrix for future/closed/manual/stale/mismatched authority,
changed evidence, multiple shareholdings, contradictory land/profile facts, missing policy, or
invalid amounts. This falls below codebase-design §§26/42's success-and-blocked testing rule for a
financial deep module. `006Z10` owns the redacted public boundary matrix.

#### Finding 3 - High - Portal submit and error code is unverified

`MP05_NewApplication.tsx` contains new submit-time amount-error and canonical-refetch behavior, but
the mounted tests execute only initial GET/rendering. Neither mounted nor trusted-browser coverage
executes submit, exact draft/submit calls, `required_loan_amount`, 400/403/409 no-retry behavior, or
one post-submit refetch. `006Z10` replaces rendering-only closure with observable lifecycle tests.

#### Finding 4 - Medium - Browser advisory fixture is not discriminating

The over-limit fixture sets both an above-limit amount and `exception_required_flag = true`; no test
uses contradictory amount/flag facts. Client-side amount recomputation could therefore return while
the claimed “server flag only” test remains green. `006Z10` adds inverse fixtures plus submit/reload.

#### Finding 5 - Medium - Witness absence behavior changed without a durable contract

006Y15 introduced a new absent-parent `404` branch but did not update `API_CONTRACTS.md` as
DECISION_POLICY §2 requires. More importantly, the absent branch grants every Credit Manager global
scope without the existing application's §19.2 stage fact, so an existing pre-credit parent can be
`403` while a random parent is `404`. `006Y16` removes that cross-stage oracle and documents the
final authority-first `403`/`404` contract.

Judgment call: several new raw-source substring assertions test private names and fixture text.
006Z8 explicitly requested a narrow static regression, but the browser-fixture inspection adds no
behavioral confidence. `006Z10` retains only checks that cannot be expressed through the public UI.

### Spec

#### Finding 1 - High - Relaxation results can be persisted as ordinary active decisions

BR-003/BR-005 require a recent member to qualify under relaxation. `verify()` accepts
`decision = active` when `member_active_check = relaxation`, then stores status `active`; the
promised unsupported/mismatched decision matrix does not cover this. `006Z9` enforces exact route-
to-decision agreement and complete zero evidence for both mismatch directions.

#### Finding 2 - High - 006Z7's public verification matrix remains partial

The source slice requires complete module/API rows for active, inactive, relaxation, stale,
maker-checker, unsupported decision, chronology, and malformed inputs. The HTTP suite proves one
active success, date/unknown validation, and object non-disclosure; inactive/relaxation successes,
stale result/member/evidence, mismatched decision, chronology, and evidence-maker denial remain only
module-level or absent. It also allows the same actor to create/update verified relaxation evidence
and verify the resulting status. `006Z9` owns paired module/HTTP behavior and evidence ownership.

#### Finding 3 - High - 006Z8 did not deliver its interaction acceptance matrix

Requirement 5 calls for the routed container to prove exact request body, successful submit/refetch,
400/403/409, conflicting server values, reload provenance, and loading/error/redaction. The four
trusted cases mock projection reads and never submit, error, or reload; retained two-run logs only
repeat those four renders. `006Z10` owns the missing mounted and trusted-browser acceptance.

No material scope creep was found. 006X10's eight executable object-scope rows and 006Y15's two-kind
payload behavior are substantive subject to `006Y16`'s parent-policy correction. BR-004/006/007 and
M02-FR-004/006 pass; BR-003/005 and M02-FR-005 remain partial until `006Z9`. M04-FR-005/006/007
backend behavior passes, but portal acceptance remains partial until `006Z10`.

No ADR was added because the existing auth, functional, and codebase-design sources already decide
explicit scope, route fidelity, maker-checker separation, and interface-level testing.

Summary: Standards found 3 High and 2 Medium issues; worst are inferred member-global authority and
the untested financial submit/boundary paths. Spec found 3 High issues; worst are relaxation status
mislabelling, incomplete verification parity, and absent portal lifecycle proof.

## 2026-07-13 00:49 - Architecture Review 2026-07-13_004501_architecture_review

Reviewed completed product work since architecture-review commit `540eef4`:
- `006X9-credit-object-scope-isolated-execution-matrix` (`8bb60b6`)
- `006Y14-witness-parent-nondisclosure-and-matrix-closure` (`47c2cc4`)
- `006Z6-active-member-evidence-atomicity-and-history-closure` (`0f13c65`)
- `006Z2-portal-application-limit-display-authority` (`63136ff`)

The review checked `git diff 540eef4...HEAD`, production/test hunks, retained run packets, trusted
browser/PostgreSQL evidence, Epic 004/006 digests, cited source sections, assumptions, and
M02-FR-004..006, M04-FR-001..011, and BR-003..007. Standards and spec fidelity were reviewed
independently. Production code was not changed. `CONTEXT.md` remains truthful, and state/files contain
no Blocked slice to reopen.

### Standards

#### Finding 1 - High - Portal adapter duplicates the credit limit workflow

`members/portal_services.py` selects active authority, shareholding, land, and effective policy,
then calculates both limits and exception authority. That is a second orchestration path outside the
credit loan-limit module, contrary to codebase-design §§22.1/42.1-42.3 locality and deep-module
rules. `006Z8` moves one borrower projection behind the credit boundary; the portal adapter keeps
only PortalAccount scoping/redaction/transport.

#### Finding 2 - High - Member authority remains caller-controlled and behaviorally divergent

`member_authority.evaluate_member_authority()` exposes `globally_authorized` and embeds concrete
roles. `MemberRegistry` always passes the bypass while active verification does not, so equivalent
permissioned non-owners receive different results. Registry tests patch the internal evaluator and
cannot detect the divergence. This conflicts with codebase-design §§27.1/42.1 and 006Z6's one-policy
requirement. `006Z7` owns a behavioral public matrix and one hidden policy.

#### Finding 3 - Medium - New UI/module residue violates reuse and dead-code rules

006Z2 added an exported `PortalApplicationLimitView` even though the existing inline card/alert/empty
compositions express the screen, recorded no required assumption, and duplicated the page's currency
formatter. 006Z6 also left `_qualifying_service_evidence()` unreachable. These conflict with
FRONTEND_DESIGN_RULES reuse and DECISION_POLICY's no-dead-code rule. `006Z7` removes the backend
residue; `006Z8` restores inline/existing frontend composition and one formatter.

#### Finding 4 - Medium - Credit completeness still trusts static names and sibling execution

`OBJECT_SCOPE_CASES` proves only eight unique action/test-name strings and never resolves or executes
them. The create and update identifiers both run one helper containing both rows; revalidate and
submit-review do the same. A stale mapping can pass, and a selected row is not independent as
required by codebase-design §26. `006X10` owns eight executable, one-row selections.

### Spec

#### Finding 1 - High - Recent-member relaxation is rejected before its evidence is evaluated

BR-003 permits active status or recent-member relaxation, and BR-005 permits one-year relaxation with
evidence. `ActiveMemberStatusModule.calculate()` returns ineligible immediately when
`membership_status != active`, before reading qualifying supply/relaxation evidence. No inactive or
recent-member success test exists. M02-FR-006 and BR-003/005 therefore remain partial. `006Z7` makes
the source-backed route reachable without accepting reason text alone.

#### Finding 2 - High - Required evidence-mutation races were not implemented

006Z6 promised verifier-vs-supply/service create/update/verify PostgreSQL races and coherent current
record/pointer cardinality. Its only PostgreSQL case remains the earlier two-verifier race; the six
reported tests are that case plus the five credit races. Select-for-update calls alone do not prove
the mutation boundary or zero loser evidence. `006Z7` adds the real evidence races and aligns all
mutation lock/version paths.

#### Finding 3 - High - Portal authority expires because the calendar date changes

The stored active result includes `calculated_as_of_date` in `result_id`. The portal recalculates
with today's date and compares the entire hash/snapshot, so yesterday's unchanged, still-effective
verification becomes unavailable today. The only availability test creates and consumes authority
on the same date. `006Z8` validates the effective record from its stored date plus current evidence
provenance, retaining future/stale/closed rejection.

#### Finding 4 - Medium - Portal submit, error, canonical-refetch, and browser proof is partial

The routed screen maps only `nominee_id` from submit field errors, so an authoritative
`required_loan_amount` error is discarded. Tests cover an initial unavailable GET and a detached
card render, not conflicting submit/projection values, 400/403/409 no-retry behavior, one canonical
refetch, reload provenance, or the required real screenshots; the slice declared no browser runtime
and retained only sandbox-blocked capture plus HTML/jsdom evidence. `006Z8` owns the mounted and
trusted-browser contract.

#### Finding 5 - Medium - Witness and credit matrices remain incomplete

006Y14 omits unknown-field rows, does not project exact actions for scope cases, and does not test
the promised normal `404` for an authorised in-scope missing parent; its scope cases assert only
PATCH/category/evidence. 006X9's paired helpers violate its independently selectable row requirement.
`006Y15` and `006X10` own the two behavioral matrices.

No material scope creep was accepted. M04-FR-001/002 remain explicitly deferred to 012EA under
A-053 and M04-FR-003 retains A-054's receipt-time proxy; M04-FR-004..011 retain substantive behavior
subject to `006X10`/`006Z8` proof. M02-FR-004..006 and BR-003..007 remain partial until `006Z7`.
No ADR was added because existing source and codebase-design documents already decide module
locality, authority policy, evidence atomicity, and effective-dating direction.

Summary: Standards found 2 High and 2 Medium issues; worst are duplicated credit orchestration and
divergent caller-controlled member authority. Spec found 3 High and 2 Medium issues; worst are the
unreachable documented relaxation, absent evidence races, and next-day authority expiry.

## 2026-07-12 23:42 - Architecture Review 2026-07-12_234227_architecture_review

Reviewed completed product work since architecture-review commit `099e2a6`:
- `006X8-credit-executed-object-scope-regression-closure` (`b9f5d9b`)
- `006Y12-witness-authority-matrix-and-nondisclosure-closure` (`c6ae9bf`)
- `006Y13-member-mutation-success-interaction-closure` (`7daaa61`, including repair evidence)
- `006Z5-active-member-evidence-and-verification-governance-closure` (`b76936f`)

The review checked `git diff 099e2a6...HEAD`, production/test changes, slice/run packets, trusted
browser and PostgreSQL evidence, Epic 004/006 digests, cited source sections, assumptions, and
M02-FR-001/004/005/006/012 plus BR-003..007. Standards and spec fidelity were reviewed
independently. Production code was not changed. `CONTEXT.md` remains truthful, and state has no
Blocked slice to reopen.

### Standards

#### Finding 1 - High - Active verification can commit evidence that changed concurrently

`ActiveMemberStatusModule.verify()` locks the Member, then recalculates from unlocked supply and
service-evidence rows. Those evidence writes do not advance the Member version, so a concurrent
evidence mutation can land between calculation and commit while the verifier still makes the stale
snapshot current. The PostgreSQL test races only two verifiers, not verification against evidence
mutation. This conflicts with codebase-design §§22.1/42.2 transactional evidence rules. `006Z6`
locks or versions the exact evidence set and adds the missing race.

#### Finding 2 - High - Witness PATCH still reveals parent application existence

`applications/views.py` returns `404` for a missing parent application before object authority, but
returns `403 OBJECT_ACCESS_DENIED` for an existing out-of-scope parent. 006Y12 varies only child
witness IDs beneath one existing application, so it closes witness enumeration but leaves the parent
oracle open. This violates auth §§3-3.1 and codebase-design §27.1. `006Y14` makes missing/existing
out-of-scope parent IDs indistinguishable before child lookup.

#### Finding 3 - Medium - Member object authority was copied with a different role policy

Active-status verification calls the low-level evaluator directly and hard-codes global access for
`system_admin`/`credit_manager`, while `MemberRegistry` already owns a different member-access rule.
This contradicts 006Z5's explicit reuse requirement and codebase-design §§27.1/42.1 single-policy
direction. `006Z6` extracts one public member-authority result consumed by both callers.

#### Finding 4 - Medium - Credit completeness depends on global state and test order

006X8 appends results to `EXECUTED_OBJECT_SCOPE_RESULTS`; a later `Z...` test assumes every row test
already ran in the same worker. The aggregate fails when selected alone and can break under sharding,
random order, or retries, contrary to codebase-design §§26.1-26.2. `006X9` replaces it with eight
self-contained parameter rows that each execute all four phases independently.

Judgment call: the application-authority compatibility wrapper adds little leverage and the new seam
test asserts internal mock call counts. `006Y14` may remove or deepen the wrapper while retaining
behavioral parity. No frontend visual-system drift was found.

### Spec

#### Finding 1 - High - BR-005/006 evidence is used but omitted from the immutable result

The BR-006 calculator uses `MemberServiceEvidence` only as an existence predicate. Its dates,
recipient, evidence reference, verifier, and ID do not enter the result/hash or effective record's
snapshot, so qualifying evidence can change without staling the result and the decision is not
reviewable from stored facts. One-year relaxation can likewise be created from one supply year plus
free-text reason copied into `evidence_summary`, rather than persisted relaxation evidence. This is
partial against BR-005/006 and M02-FR-004/006. `006Z6` snapshots the full service/relaxation evidence
and makes all review facts part of result provenance.

#### Finding 2 - High - Effective history accepts invalid backdated intervals

Every later verification closes the current record at `as_of_date - 1` without requiring the new
date to follow the current record's `effective_from`. A backdated or same-date result can therefore
write `effective_to < effective_from`; tests cover only the first record despite the slice claiming
immutable later decisions. `006Z6` defines and tests chronological, non-overlapping history.

#### Finding 3 - High - 006Z5's verification matrix remains incomplete

The tests do not execute separate stale-member, stale-result/evidence, unsupported-decision,
inactive, relaxation, and later-decision rows with complete zero-evidence assertions; the PostgreSQL
test also omits current-record/pointer cardinality. `006Z6` owns the complete module/API matrix and
coherent current-record race evidence.

#### Finding 4 - Medium - 006Y12 did not deliver its two-kind backend matrix

Contact and identity corrections remain isolated examples: parent/child non-disclosure exercises a
contact payload, while malformed/immutable/stale and maker-checker paths are not executed as the
promised cross-product with exact six-field projection/write/evidence parity. `006Y14` adds the
parameterized contact/identity matrix while retaining mounted and browser acceptance.

#### Finding 5 - Medium - 006X8's false-completeness proof is not isolated

The aggregate proof requires prior tests in the same process, and its mutation test marks phase flags
directly instead of executing the production assertion phases. `006X9` makes omission fail inside the
row that owns the public projection/write.

No material scope creep was found. M02-FR-001 and M02-FR-012 are substantively covered by routed and
real-session create/update/request/approval behavior; M02-FR-005 and BR-003/004/007 remain
substantive. M02-FR-004/006 and BR-005/006 remain partial until `006Z6`. No ADR was added because the
source documents already establish the authority, evidence, and effective-dating direction.

Summary: Standards found 2 High and 2 Medium issues; worst are the evidence race and parent-resource
enumeration. Spec found 3 High and 2 Medium issues; worst are incomplete immutable relaxation/service
evidence and corruptible effective history.

## 2026-07-12 22:14 - Architecture Review 2026-07-12_220748_architecture_review

Reviewed completed product work since architecture-review commit `e9c7217`:
- `006X7-credit-object-scope-action-parity-closure` (`a58515b`)
- `006Y10-witness-correction-matrix-and-module-boundary-closure` (`2664e8b`)
- `006Y11-member-form-container-and-error-matrix-closure` (`93870ed`, including repair evidence)
- `006Z4-active-member-rule-and-snapshot-closure` (`fe8b464`)

The review checked `git diff e9c7217...HEAD`, production/test changes, all four slice/run packets,
trusted browser and PostgreSQL evidence, Epic 004/006 digests, cited source sections, assumptions,
and M02/M04 functional IDs. Standards and spec fidelity were reviewed independently. Production code
was not changed. `CONTEXT.md` remains truthful, and `.ralph/state.json` has no Blocked slice to reopen.

### Standards

#### Finding 1 - High - Credit completeness still trusts static metadata

`test_credit_action_parity_matrix.py` replaces `EXECUTED_CASES` with
`@object_scope_cases(...)`, but the inventory still scans metadata rather than results emitted after
projection, write, category, and evidence assertions execute. A test can keep its decorator while
deleting its body and remain advertised, contrary to codebase-design §26.1 and 006X7's stated
closure. High-risk `006X8` replaces metadata discovery with an executed-row ledger whose entries
exist only after all required phases pass.

#### Finding 2 - High - Witness authority was de-cycled by copying it

`applications.modules.witness_corrections` duplicates the creator/receiver/Credit Manager object-
access algorithm in `applications.services`. The source-text regression proves only that one import
string disappeared; it cannot prevent the two policy copies drifting. This violates codebase-design
§§26.2/36.1-36.2 and the slice's single-owner requirement. `006Y12` extracts/reuses one lower-level
application authority seam and verifies behavioral consumption from projection and write callers.

#### Finding 3 - High - Witness PATCH leaks resource existence before authority

`applications/views.py` skips permission/object checks for PATCH until after application and witness
lookup. An unauthorised caller can distinguish an existing out-of-scope witness (`403`) from a random
ID (`404`), conflicting with auth §§19/24 and backend review §42.2. `006Y12` moves non-disclosing
authority ahead of witness lookup and adds indistinguishable existing/missing object-denial tests.

#### Finding 4 - High - Active-member verification drifted from the source persistence model

006Z4 writes current fields on `Member` plus generic change/audit JSON; it creates no effective-dated
`active_member_statuses` record containing status, route/evidence, verifier, and effective dates as
required by data-model §11.5 and M02-FR-006. `006Z5` adds the source-shaped verification record and
keeps the Member projection as a referenced compatibility view, not a substitute for evidence.

Judgment calls: `members/views.py` owns dense validation/error translation that belongs behind a thin
adapter, and the new stale/result/decision codes are not reconciled with source API §7. The 006Z4
test named for version/current-result never executes distinct stale-version or stale-result rows.
Frontend changes otherwise reuse the approved components/classes and backend-authored actions/errors;
no styling or client-owned business-rule drift was found. `006Z5` owns the validation/error matrix.

### Spec

#### Finding 1 - High - 006Z4 verification has no object scope

The slice explicitly requires authority/object scope and a verify matrix containing object denial,
but `ActiveMemberStatusModule.verify()` accepts any `member_id` once the caller has the permission.
`006Z5` reuses the public member/Registry object evaluator and proves non-disclosure before result
verification.

#### Finding 2 - High - 006Z4's stored “complete” evidence omits classification inputs

`SupplyRowProjection` stores only row ID, financial year, verified/qualifying, and reason. Entity,
route, producer-institution, evidence-reference, and verifier facts are omitted even though those
facts decide qualification. The immutability test therefore freezes a reduced projection while the
review packet claims completeness. `006Z5` stores the full internal row/result evidence and tests
deliberate portal redaction separately.

#### Finding 3 - High - BR-006 passes from an unsupported scalar

BR-006 requires three continuous service years to SFPCL/subsidiary/step-down entities, while 006Z4
accepts `employment_or_service_years >= 3` without dates, recipient, or evidence and even tests the
route with `services_availed_flag = false`. `006Z5` returns manual-evidence-required until persisted
facts prove the documented route; it must not invent continuity from the scalar.

#### Finding 4 - High - 006Y10 did not execute its backend correction matrix

The commit adds a dependency substring test and changes one maker-checker code. Missing-permission
and object-denied correction writes are not executed; stale/malformed/immutable cases are not tested
for both contact and identity; exact parity/zero-evidence assertions are absent. `006Y12` owns the
complete backend, mounted, non-disclosure, and trusted-browser matrix.

#### Finding 5 - High - 006X7's false-completeness acceptance remains open

The decorator inventory can advertise combined action codes even when the test body never executes
one of them. This does not meet the requirement that deleting a projection/write assertion removes
the row. `006X8` owns result-derived completeness without production behavior changes.

#### Finding 6 - Medium - 006Y11 success proof covers creation only

Mounted tests prove successful create/readback and failures for create/update/request/approval, but
not successful ordinary update, identity request, or approval with one canonical GET. Browser exact
request assertions likewise cover creates, not all named mutations. `006Y13` mounts the routed
Directory/Profile path and completes exact success bodies/counts/readbacks in both test layers.

No material scope creep was found. M02-FR-001's three create variants remain substantive, and
M02-FR-012's requester/checker behavior exists, but full interaction confidence remains partial until
`006Y13`. M02-FR-004..006 and BR-003..007 remain partial until `006Z5`; M04-FR-004..011 production
behavior is unchanged, while the advertised exhaustive matrix remains partial until `006X8`. No ADR
was added because the source documents and existing deep-module direction already settle the target.

Summary: Standards found 4 High issues plus validation/test-quality judgments; worst are duplicated
witness authority/resource enumeration and missing source-shaped active-status persistence. Spec
found 5 High and 1 Medium issue; worst are unscoped, incomplete, source-inaccurate active-member
verification and the still-metadata-driven credit/witness acceptance claims.

## 2026-07-12 20:43 - Architecture Review 2026-07-12_203645_architecture_review

Reviewed completed product work since architecture-review commit `c87586d`:
- `006X6-credit-authority-state-parity-matrix-closure` (`7294500`)
- `006Y7-member-registry-race-and-action-scope-closure` (`3843194`)
- `006Y8-witness-maker-checker-and-browser-closure` (`0f97eb5`, repaired through `55f7651`)
- `006Y9-member-form-real-session-closure` (`6411bd1`, including its repair chain)

The review checked `git diff c87586d...HEAD`, the four slice/run packets, production/test changes,
authoritative PostgreSQL/browser evidence, Epic 004/006 digests, cited source sections, assumptions,
and M02/M04 functional IDs. Protected orchestrator-only commit `2af4399` was excluded from product
findings. Standards and spec fidelity were reviewed independently. Production code was not changed;
`CONTEXT.md` remains truthful, and `.ralph/state.json` contains no Blocked slices to reopen.

### Standards

#### Finding 1 - High - Witness correction authority remains cyclic and its negative matrix is absent

`applications.services.witness_resource_actions` imports `witness_corrections`, calculates object
access that correction actions discard, and calls an evaluator that imports generic services back to
calculate the same access. This leaves two coupled owners and a runtime dependency cycle, contrary to
codebase-design §§36.1-36.2/42.2. The mounted suite covers success and an already-disabled control,
but never drives the required `400`/`403`/`409` failures or one-call/no-refetch assertions required by
§§26.3/42.3. High-risk `006Y10` owns one acyclic authority seam plus the complete backend/mounted/
browser request matrix.

#### Finding 2 - High - Member container tests do not cross the production interaction boundary

`MemberProfile.container.test.tsx` adds only a StrictMode single-GET assertion. Full-field tests still
mock `createMember`/`updateMember`, while the browser proves successes but no validation, object
denial, or stale conflict. This falls short of codebase-design §§26.3/42.3 and 006Y9's explicit real-
container `400`/`403`/`409` contract. High-risk `006Y11` owns transport-boundary mounted tests and the
complete real-session variant matrix.

#### Finding 3 - Medium - Trusted-browser logs are not self-contained

The final 006Y8 and 006Y9 trusted logs record `RALPH_EVIDENCE_DIR` under absolute, deleted-run
`.ralph/worktrees/...` paths. The screenshots are archived and the scenarios passed twice, but the
command provenance violates AFK_RUNBOOK's rule that evidence must not reference deleted worktrees.
Historical packets remain immutable; this review's evidence uses run-relative descriptions, and
future packets must record stable run-folder-relative paths.

Judgment call: 006Y7's Registry action/write object evaluation and both real PostgreSQL races are
substantive closures. Its HTTP/masking evidence says object denial is `FORBIDDEN` although production
now returns `OBJECT_ACCESS_DENIED`; the executable tests/code are authoritative, but packet prose
should not diverge from them in future runs.

### Spec

#### Finding 1 - High - 006X6's object-scope rows are labelled rather than proven

006X6 requires each case to project a real six-field action and invoke the exact write on the same
resource with reason/category parity. Eligibility, loan-limit, appraisal, review, and sanction tests
instead capture an enabled action, mutate ownership, and assert only that the write raises. Static
`EXECUTED_CASES` labels still mark every object-scope variant complete. High-risk `006X7` replaces
the labels with derived executable cases and real disabled evaluation/write parity without leaking
object-denied resources through HTTP.

#### Finding 2 - High - 006Y9 omits the declared mounted and error-path acceptance

The slice requires mounted production containers to submit every §13.2 field and prove one-call
`400`/`403`/`409` behavior. Its only new mounted test loads detail once; Playwright covers individual/
FPC success and requester/checker approval but none of the three error classes. It also does not
execute the separately named Producer Institution member category in M02-FR-001. `006Y11` owns the
full transport-boundary matrix, Producer Institution flow, collision-proof identities, and masked
canonical readback.

#### Finding 3 - High - 006Y8 omits named backend and mounted denial cases

006Y8 requires missing-permission/object-denied PATCH parity and mounted `400`/`403`/`409` one-call
behavior. Backend tests assert missing-permission projection but never its correction write, and the
only object-denial write test targets witness create. Mounted tests simulate no rejected mutation;
the browser checks the verifier button is absent but does not assert zero PATCH requests. `006Y10`
owns all omitted cases and exact browser request counts.

No material scope creep was found. M04-FR-004..011 retain substantive production behavior, but
006X6's advertised exhaustive action matrix remains partial until `006X7`. M02-FR-012's persisted
requester/checker flow is substantive; M02-FR-001 and the member/witness interaction confidence stay
partial until `006Y11`/`006Y10`. No ADR was added because API §44 and codebase-design §§26/36/42
already settle the durable direction.

Summary: Standards found 2 High and 1 Medium issue plus one packet judgment; worst are the cyclic,
under-tested witness seam and missing member container error matrix. Spec found 3 High issues; worst
are the falsely complete credit object-scope matrix and the repeated omitted witness/member denial
acceptance.

## 2026-07-12 14:17 - Architecture Review 2026-07-12_141135_architecture_review

Reviewed completed product work since architecture-review commit `b6d86cd`:
- `006X5-credit-public-action-write-matrix-closure` (`654a92b`)
- `006Y5-member-registry-governance-and-form-contract-closure` (`45c267d`)
- `006Y6-witness-contact-and-action-parity-closure` (`8dc46e8`)
- `006Z3-active-member-supply-evidence-boundary-hardening` (`5cbbc5d`)

The review checked `git diff b6d86cd...HEAD`, all four slice/run packets, implementation/tests,
Epic 004/006 digests, cited source sections, assumptions, and M02/M04 functional IDs. Standards and
spec fidelity were reviewed independently. Production code was not changed; `CONTEXT.md` remains
truthful, and `.ralph/state.json` has no Blocked slices to reopen.

### Standards

#### Finding 1 - High - The active-member public seam is incomplete and governance remains split

`ActiveMemberStatusModule` exposes only `calculate`; capture and verification remain in generic
member services/views. The caller copies only three strings and does not retain the dated row/result
snapshot, while `as_of_date` does not exclude future supply facts. This violates codebase-design
§10.2's calculate/verify interface, dated-result/application-snapshot invariants, and §§26.1-26.2's
deep-module test surface. High-risk `006Z4` owns the calculate/verify seam, dated immutable snapshot,
and shared capture/verification governance.

#### Finding 2 - High - Documented active-member routes and interface tests are absent

The module reduces service evidence to a boolean and ignores the BR-006 three-year employment/
service route and institutional supply-year route. Its only direct test covers an individual/direct
four-year path and service false; FPC/institution, relaxation, as-of, future, malformed/wrong route,
and Producer Institution cases are missing. This conflicts with codebase-design §10.2 and §26.3.
`006Z4` owns the complete public-module table without inventing an approval authority.

#### Finding 3 - High - Witness update actions omit the maker-checker rule enforced by writes

`witness_resource_actions` evaluates permission and application scope only, but protected-identity
correction rejects the original verifier. That actor can therefore see Update enabled and receive
`MAKER_CHECKER_REQUIRED` from the write, contrary to API §44 and codebase-design §42.2. High-risk
`006Y8` centralises field-specific correction evaluation and adds routed/browser authority proof.

#### Finding 4 - High - 006X5's advertised matrix remains an inventory plus permission samples

The static inventory assertion includes synthetic review-decision suffixes that are not projected
action codes. Executed cases cover permission denials and one sanction state denial, not the required
role, object, maker-checker, provenance, immutable-review, malformed-rejection, and stale variants.
This fails codebase-design §26.3's observable interface matrix. High-risk `006X6` owns the generated
real-action/state/authority matrix and preserves the PostgreSQL race gate.

Judgment call: `MemberRegistry` is still a facade over private generic service functions, with its
action serializer importing back into the Registry. Public bypasses are substantially reduced, but
the circular ownership weakens codebase-design §10.1. `006Y7` removes that action-evaluation cycle
while closing the concrete object/race defects.

### Spec

#### Finding 1 - High - 006X5 omits most of its named exhaustive cases

006X5 requires success/denial execution for state, role, exact permission, object scope,
maker-checker, frozen provenance, immutable review consistency, rejection payload, and stale state.
The new tests exercise permission-only denials for most writes, a sanction state denial, and review
success variants. `006X6` owns the missing executable cases; no M04 requirement is newly deferred.

#### Finding 2 - High - 006Y5 did not run either mandatory PostgreSQL duplicate race

The slice requires competing duplicate create and identity-approval races. Its tests are sequential
`TestCase` requests with no concurrent transactions, and the slice declares no PostgreSQL runtime
capability. `006Y7` adds twice-run duplicate races with one success, one standard field error, and
exact zero-partial-evidence assertions.

#### Finding 3 - High - Member approval projection omits object scope used by the write

`approve_identity_change` performs Registry member-object access before its shared approval check,
but `_available_actions` calls an evaluation containing only permission, pending status,
requester-checker, version, and KYC state. An out-of-scope checker can see approval enabled and then
be denied. `006Y7` makes projection/write consume one complete evaluation.

#### Finding 4 - High - 006Y5's required real-session form proof is absent

The complete §13.2 fields are present, but tests mock API wrapper functions and the run has no
browser capability or screenshots. It does not prove real authenticated POST/PATCH/request/approval,
canonical readback, or one-call `400`/`403`/`409` behavior required by the slice. `006Y9` supplies the
mounted and trusted-browser individual/institution/identity workflow.

#### Finding 5 - High - 006Y6 omitted both maker-checker parity and required browser acceptance

The backend tests cover missing permission but not verifier identity denial, and the run packet
explicitly treats the absence of a browser capability/contract as permission to omit the real flow
even though the slice requires it. `006Y8` owns verifier/contact/identity parity plus the real routed
three-state screenshot contract.

#### Finding 6 - High - Active-member continuity can add years across gaps

`longest_continuous_financial_years` counts every matching offset across the size of the set rather
than stopping at the first gap. For `2020-21, 2022-23, 2023-24, 2025-26, 2026-27, 2027-28`, it reports
five although the longest uninterrupted run is three, allowing BR-004/BR-007 to pass incorrectly.
`006Z4` adds this regression and exact uninterrupted/as-of boundaries.

#### Finding 7 - High - BR-006 and the dated verified active-status contract remain incomplete

The module never consumes `employment_or_service_years`, exposes no `verify`, persists no complete
dated evidence snapshot with the application, and does not exclude future rows. M02-FR-004 through
M02-FR-006 therefore remain partial. `006Z4` owns the source-backed routes, dated verification, and
immutable credit snapshot.

#### Finding 8 - Medium - Portal supply rows hide their computed qualification result

The module computes `qualifying` and `non_qualifying_reason`, but the portal serializes generic rows
without either field. Pending/malformed/wrong-route rows are visible yet indistinguishable from
accepted evidence, contrary to 006Z3's sharpened contract. `006Z4` projects stable row explanations
and keeps totals/continuity qualification-only.

No material scope creep was found. M04-FR-001/002 remain explicitly deferred to 012EA under A-053;
M04-FR-003 retains A-054's receipt-time proxy. M04-FR-004..011 behavior remains substantive but its
exhaustive parity acceptance is partial until 006X6. M02-FR-001/012 remain partial until 006Y7/006Y9
close races, object parity, and reachability; M02-FR-009 remains partial until 006Y8; M02-FR-004..006
remain partial until 006Z4. No ADR was added because API §44 and codebase-design §§10.1-10.2/26/42
already settle the durable direction.

Summary: Standards found 4 High issues plus 1 architecture judgment; worst are the incomplete dated
active-member seam, missing rule routes, witness parity, and non-exhaustive credit matrix. Spec found
7 High and 1 Medium issue; worst are the repeated credit/member/witness acceptance gaps and active-
member continuity/rule errors.

## 2026-07-12 12:52 - Architecture Review 2026-07-12_125256_architecture_review

Reviewed completed product work since architecture-review commit `cea56b2`:
- `006X4-credit-action-parity-regression-matrix` (`a75010c`)
- `006Y3-member-registry-and-identity-change-approval-closure` (`7668c72`)
- `006Y4-witness-correction-and-resource-action-closure` (`f2ea8d1`)
- `006Z-produce-supply-history-persistence` (`cd6822f`)

The review checked `git diff cea56b2...HEAD`, slice contracts and run/repair packets, implementation,
tests, browser/PostgreSQL evidence, Epic 004/006 digests, cited source sections, assumptions, and
functional IDs. Orchestrator-only commits `62f8d89` and `8cd5f45` were excluded from product
findings. Standards and spec fidelity were reviewed independently. Production code was not changed;
`CONTEXT.md` remains truthful, and `.ralph/state.json` contains no Blocked slices to reopen.

### Standards

#### Finding 1 - High - 006X4's advertised matrix executes only one denied write

`test_credit_action_parity_matrix.py` projects five appraisal actions, then invokes only appraisal
update and only for a missing-permission denial. It has no enabled/write-success pairs, eligibility,
loan-limit, appraisal-create, separate review outcomes, authority/provenance matrix, or new stale-
projection race. The trace table points to disparate older tests but does not execute the paired
matrix required by codebase-design §26.3 and 006X4. High-risk `006X5` owns the actual enumerated
public action/write matrix and authoritative race proof.

#### Finding 2 - High - Member Registry remains bypassable and duplicate identity approval can 500

`MemberRegistry` lacks the documented read interface, delegates create/update to still-public
service functions, and does not enforce member object access internally. Proposed identity hashes
are not duplicate-checked at request/approval; approval can hit the new unique constraint and neither
the module nor approval view translates `IntegrityError`. Existing duplicate proof is sequential
HTTP create only, not module or identity-approval concurrency. This violates codebase-design
§10.1/§26.1-§26.2/§42.2 and auth §34.2. High-risk `006Y5` owns the deep public seam, object authority,
and duplicate-safe approval races.

#### Finding 3 - High - Witness action projections omit disabled authority facts

`witness_collection_actions` and `witness_resource_actions` omit actions entirely when permission or
application scope fails. Tests assert all-enabled action codes and do not pair denied update
projection with update write. This fails 006Y4's six-field resource-action contract and codebase-
design §42.2. High-risk `006Y6` owns stable disabled reasons, shared evaluations, and mounted/public
denial proof.

#### Finding 4 - High - Credit now owns and privately tests a member-domain active-status rule

`credit.modules.eligibility_assessment` directly imports `ProduceSupplyRecord`, implements financial-
year continuity, and is tested through private `_active_member_check`. The documented
`members.modules.active_member_status` boundary remains absent, contrary to codebase-design §10.2/
§26.1 and 006Z requirement 3. High-risk `006Z3` moves calculation/verification behind the member-
owned public seam and makes credit consume its projection.

Judgment call, High risk: supply capture validates only three required fields. Unknown fields,
financial-year format, eligible entity/route combinations, UUID relationships, decimal validity,
and non-negative amounts are unchecked, so malformed ORM inputs or ineligible rows can reach
eligibility. `006Z3` owns strict boundary validation and standard errors.

### Spec

#### Finding 1 - High - 006X4 did not deliver its named acceptance matrix

006X4 requires every eligibility, limit, appraisal, review-decision, and sanction action to have an
enabled/write-success and disabled/write-denial pair. Its new test enumerates only five appraisal
projections and executes one update denial. `006X5` owns the missing acceptance contract.

#### Finding 2 - High - 006Y3 approval projection diverges from maker-checker write authority

`_available_actions` enables approval for any permission holder when a request is pending, including
the requester, while `approve_identity_change` rejects that actor. The test requester lacks approval
permission, so its 403 proves only permission denial. 006Y3 also still omits most API §13.2 form
fields: individual middle name/gender/DOB/occupation/cultivation/crop/services/years and institution
registration/signatory identities/board-resolution/services/supply years. `006Y5` owns shared
requester-checker evaluation and both complete registration variants.

#### Finding 3 - High - 006Y4 omits S09 witness address and mobile corrections

The correction allowlist/model/UI contain name, PAN, and Aadhaar only, although the slice promises
all S09-confirmed contact/identity/display fields and S09 names address and mobile. `006Y6` owns the
missing persisted contact fields and governed correction flow.

#### Finding 4 - High - 006Z can pass BR-004 without persisted service evidence

For an individual, `_active_member_check` treats a legacy `active_member_status=active` plus timestamp
as equivalent to `services_availed_flag=true`. Four supply rows can therefore pass while the actual
service flag is false, contradicting BR-004 and the run packet's service-evidence claim. Capture also
lacks the sharpened member/resource version and does not restrict rows to S16-eligible entity/route
facts. `006Z3` owns actual service evidence, qualifying supply validation, optimistic capture, and
one shared continuity projection before `006Z2` can expose portal limits.

### Functional IDs, Context, and Queue

M04-FR-004..011 retain substantive production behavior, but 006X4 did not add its promised exhaustive
regression proof; M04-FR-001/002 remain deferred under A-053 and M04-FR-003 under A-054. M02-FR-012
has a persisted approval workflow but is not accepted until 006Y5 closes action parity, object
authority, duplicate races, and full reachability. M02-FR-009's shareholder validation remains
implemented, while S09 correction is partial pending 006Y6. M02-FR-004/BR-004/BR-007 are not accepted
until 006Z3 prevents legacy/no-service and ineligible-route evidence from passing. No ADR was added:
the cited module, action, identity, and eligibility standards already settle the durable direction.

Summary: Standards found 4 High issues plus 1 High-risk judgment call; worst are the absent credit
matrix, bypassable/duplicate-unsafe Member Registry, and misplaced eligibility rule. Spec found 4
High issues; worst are the incomplete 006X4 acceptance, Member Registry action/form gaps, missing
witness contact fields, and service-evidence bypass.

## 2026-07-12 09:25 - Architecture Review 2026-07-12_092009_architecture_review

Reviewed completed product work since architecture-review commit `1f047f5`:
- `006X2-credit-action-predicate-and-container-closure` (`0d2168c`)
- `006X3-credit-visual-and-real-browser-closure` (`559b31f`)
- `006Y-member-create-update-and-identity-governance` (`d64b262`)
- `006Y2-member-form-and-witness-capture-ui-wiring` (`09b6b53`, repaired by `6c6a4da`)

The review checked `git diff 1f047f5...HEAD`, all four slice contracts/run packets, implementation
and tests, trusted-browser evidence, Epic 004/006 digests, cited source sections, assumptions, and
functional IDs. The script/runbook portion of `6c6a4da` is protected Ralph-orchestrator work and was
excluded from product findings. Standards and spec fidelity were reviewed independently. Production
code was not changed; `CONTEXT.md` remains truthful, and `.ralph/state.json` has no Blocked slices.

### Standards

#### Finding 1 - High - Member governance bypasses the documented deep module and duplicate invariant

006Y adds create/update/reverification to the already broad `members/services.py`; callable writes
accept an actor but depend on views for permission enforcement. This contradicts codebase-design
§6.3 and §10.1's `members.modules.member_registry.MemberRegistry`, which must hide permission-safe
profile creation, identity protection, duplicate detection, masking, and audit. The named
“Duplicate PAN rejected” test/invariant is absent: hashes are stored but never checked or uniquely
constrained. Nested profile dictionaries also reach model creation without a complete API-shape
validator, leaving malformed/duplicate integrity failures capable of escaping the standard error
contract. High-risk `006Y3` owns the deep seam, exact validation, concurrency-safe duplicate
rejection, and permission/object enforcement through the public interface.

#### Finding 2 - High - Member/witness UI proof and authority remain shallower than the production path

The 006Y2 form tests mock API wrapper functions and the browser merely opens the create and
reverification forms; its only mutation is witness capture. No routed test proves member POST,
PATCH, identity correction, canonical refetch, or one-call `400`/`403`/`409`, contrary to
codebase-design §26.3. Witness visibility and member-create visibility are derived from cached
`/auth/me` permissions because the witness API exposes no resource actions, contrary to API §44
and codebase-design §§23.3-23.4. `006Y3` owns the routed member matrix; `006Y4` adds witness resource
actions and mounted/real-browser capture/correction proof.

#### Finding 3 - Medium - Member forms alter the approved page composition instead of using an action surface

`MemberDirectory` inserts the registration card above the directory and `MemberProfile` permanently
prepends the edit card whenever update is enabled. A-067 justifies a shared component boundary, but
not a standing layout change. This is a judgment call under the binding Frontend Design Rules: the
source-required form should use an existing modal/action composition and preserve the established
directory/profile layout. `006Y3` restores that composition while completing the source fields.

### Spec

#### Finding 1 - High - M02-FR-012 has a reason, not an approved change request

Functional M02-FR-012 permits verified identity changes only when a change request is approved.
006Y's endpoint accepts a proposed identity value, free-text reason, and version, then immediately
applies it and resets KYC. A-065 explicitly acknowledges that no approval fact or authority exists.
The conservative deferral avoided inventing an approver, but the requirement is not complete.
`006Y3` adds a persisted request, separate permission-based checker approval, optimistic locking,
masked evidence, and no hard-coded approver role.

#### Finding 2 - High - 006Y's change history and create validation are incomplete

006Y requires field-level old/new values for every create/update. Create history lists individual or
institution profile objects as changed but omits their values; address updates read a nonexistent
aggregate model attribute and record `null` instead of the real old address. Tests check actor and
absence of plaintext but not substantive diffs. The cited M02 acceptance criterion also requires
duplicate PAN/Aadhaar detection, which is absent. `006Y3` owns complete masked nested/address history,
duplicate races, malformed variants, standard errors, and zero-write denial assertions.

#### Finding 3 - High - 006Y2 is complete without its named edit and end-to-end member paths

006Y2 explicitly requires witness capture/read/edit and an edit round trip, but only GET/POST exists;
A-066 sensibly defers PATCH rather than inventing governance. It also requires a member to be created
and corrected end to end, while trusted Chromium only screenshots unopened forms. High-risk `006Y4`
defines versioned audited witness correction with immutable 004E2 evidence; `006Y3` submits the real
member create/update/approved-identity path through two browser actors.

#### Finding 4 - Medium - Registration exposes truncated §13.2 variants

The individual form omits gender, date of birth, occupation, cultivated area, crop, services, and
employment/service years. The institution form omits registration number, signatory PAN/Aadhaar,
board-resolution flag, services, and produce-supply years. The backend accepts those source fields,
but staff cannot submit them through the delivered UI. `006Y3` completes both variants using the
existing form/modal patterns.

#### Finding 5 - High - 006X2 did not deliver its named backend parity matrix

006X2 required every eligibility, limit, appraisal, review, and sanction action/write pair across
state, role, permission, object, maker-checker, provenance, immutable-history, rejection, and
concurrent-change cases. It adds one new eligibility denial test; existing tests cover many writes
individually but do not form the promised enumerated action/write matrix or prove matching denial
reasons and zero success evidence for every pair. High-risk `006X4` supplies that public-interface
matrix and the authoritative PostgreSQL race check without changing business rules unless a failing
test exposes divergence.

### Verified Closures, Functional IDs, Context, and Queue

006X3 genuinely replaces the zero-test/mocked browser evidence: collection finds two tests, the real
Django/two-role path reaches one pending sanction case, both trusted runs pass, and all twenty
screenshots exist. M04-FR-004 through M04-FR-011 therefore retain substantive API/module/browser
confidence, subject to 006X4's missing exhaustive regression matrix. M04-FR-001/002 remain deferred
to 012EA under A-053 and M04-FR-003 retains A-054. M02-FR-009 storage/shareholder validation remains
substantive through 004E/004E2, but witness correction reachability is partial. M02-FR-012 remains
open until 006Y3. No ADR was added because the Member Registry seam, approved-change requirement,
API §44, and frontend test/layout rules already settle the durable direction.

Summary: Standards found 2 High and 1 Medium issue; worst are the bypassed Member Registry/duplicate
invariant and shallow member/witness authority tests. Spec found 4 High and 1 Medium issue; worst are
the missing approved identity-change workflow, incomplete history/duplicate safety, missing witness
edit/member E2E path, and absent 006X2 parity matrix.

## 2026-07-11 23:02 - Architecture Review 2026-07-11_230238_architecture_review

Reviewed completed product work since architecture-review commit `1ff6cb8`:
- `005E4-completeness-action-authority-and-browser-proof` (`b9c8442`)
- `006H7-credit-action-parity-and-container-proof` (`0ed9b32`)
- `006H3-appraisal-workbench-prototype-fidelity-restoration` (`dc5de3a`)
- `006X-mvp-end-to-end-happy-path-tracer-bullet` (`045f5d2`)

The review checked `git diff 1ff6cb8...HEAD`, the four run packets, actual implementation/tests,
trusted-browser evidence, Epic 005/006 digests, ADR-0005, cited source sections, and functional IDs.
Intervening `b2e8ac2` is Ralph-orchestrator-only and was excluded from product findings. Standards
and spec fidelity were reviewed independently. Production code was not changed; `CONTEXT.md`
remains truthful, and `.ralph/state.json` has no Blocked slices to reopen.

### Standards

#### Finding 1 - High - 006H7 repeats the proxy-test architecture it was created to remove

The contract requires mounted default-container behavior through mocked authenticated HTTP, but
`AppraisalWorkbench.test.tsx` still imports only `AppraisalWorkbenchView`, uses
`renderToStaticMarkup`, and checks raw source strings/regular expressions. It never exercises the
production controller, requests, refresh, or errors. This violates codebase-design §26.3's UI-
behavior seam and already missed the remaining local `serverStage` projection. High-risk `006X2`
owns the full mounted matrix plus observable assertions rather than source-text proxies.

#### Finding 2 - High - Action/write rules remain duplicated across the credit workflow

006H7 adds one shared loan-limit transition evaluation, but eligibility and appraisal projections
still use independent state/role/permission heuristics. Appraisal writes additionally enforce
provenance, maker-checker, object scope, locked history, rejection facts, frozen prerequisites, and
sanction handoff consistency. An enabled action can therefore fail deterministically at its public
write, contrary to API §44 and codebase-design §§12.3/23.4/42.2. `006X2` requires one reusable
evaluation per mutation while preserving ADR-0005's approvals-owned handoff.

#### Finding 3 - Medium - Restored presentation includes locally derived summary/stage facts

`EligibilityChecklist` counts result codes into a pass fraction/progress width, and
`AppraisalWorkbench` derives a visible stage from status/action combinations. The colours, cards,
stepper, and formula disclosure are recoveries of the cited pre-006H prototype—not new visual
design—but the derived facts need proof that they remain display-only and never become workflow or
eligibility authority under the mock-surface ratchet and codebase-design §§23.3/42.3. `006X2`
removes action authority from React; `006X3` preserves the prototype composition using stored facts
and real-browser action-denial proof.

Judgment call: the 219-line real API tracer is strong (success, denials, exact IDs, cardinality, and
audit redaction) but duplicates narrower setup and will be costly to maintain. It is not a hard
standard breach. Backend dependency direction and ADR-0005 ownership remain intact.

### Spec

#### Finding 1 - High - 006H7 implements only a fraction of its named closure

006H7 requires shared write predicates and a state/role/object parity matrix for eligibility,
loan-limit, and every appraisal mutation, plus mounted clicks for all mutations and 400/403/409
paths. Commit `0ed9b32` adds a shared predicate only for loan-limit, ten lines of static view tests,
and no eligibility/appraisal parity matrix. Its run packet traces only loan-limit while describing
the rest as preserved. `006X2` owns the unimplemented contract without broadening business scope.

#### Finding 2 - High - 006H3's required browser contract collects zero tests

The slice requires the full visual state matrix, committed baselines/screenshots, and explicitly
says browser execution/screenshot failure is not a deferral. Its collection log throws
`ReferenceError: Cannot access 'title' before initialization` before discovery, reports zero tests,
omits the loading capture, and has no screenshots or baselines. The slice also lacks the runtime
capability that would trigger independent browser acceptance. High-risk `006X3` declares the exact
contract and twenty outputs, including all eighteen visual states.

#### Finding 3 - High - 006X's browser tracer is fully mocked rather than real end to end

The slice requires a real backend, real role sessions, eligibility/limit/appraisal/review/sanction
controls, exact action facts/PATCH/readback IDs, denied resource actions, and reviewed/pending-case
screenshots. `epic-006-happy-path.e2e.spec.ts` intercepts every API with `page.route`, begins at a
draft appraisal, does not click eligibility/limit/create, incompletely checks the PATCH/readback,
and produced no screenshots. The real backend integration test is substantive but cannot prove the
UI path. `006X3` keeps that backend test and adds one real-server, two-role browser tracer.

No material scope creep was found. 005E4 is verified closed with distinct permission/write parity,
two green trusted-browser runs, and all nine screenshots. M03-FR-010 through M03-FR-012 retain
implemented confidence. M04-FR-001/002 remain explicitly deferred to 012EA under A-053;
M04-FR-003 retains A-054's `created_at` proxy. M04-FR-004 through M04-FR-011 have substantive
backend behavior, but action/container/visual reachability remains High risk until 006X2 and 006X3.

No ADR was added because API §44, codebase-design §26.3, ADR-0005, and the existing frontend rules
already settle the durable decisions. Summary: Standards found 2 High and 1 Medium issue; worst are
the repeated proxy-test seam and action/write divergence. Spec found 3 High issues; worst are 006H7's
missing core matrix, zero-test visual acceptance, and a mocked substitute for the real browser path.

## 2026-07-11 21:34 - Architecture Review 2026-07-11_212738_architecture_review

Reviewed completed work since architecture-review commit `7a3d1c9`:
- `005E3-completeness-authority-fidelity-and-interaction-closure` (`debc496`)
- `005FA4-portal-auth-real-boundary-flag-proof` (`c63194f`)
- `006G5-relative-import-dependency-guard` (`36bcd6d`)
- `006H6-workbench-action-projection-and-interaction-proof` (`4e5d5d2`)

The review checked `git diff 7a3d1c9...HEAD`, the four slice/run packets, implementation and tests,
Epic 005/006 digests, ADR-0005, cited source sections, and functional IDs. Intervening commit
`0d235e5` changes only the protected Ralph browser orchestrator and was not treated as a product
slice. Standards and spec fidelity were reviewed independently. Production code was not changed,
`CONTEXT.md` remains truthful, and `.ralph/state.json` has no Blocked slices to reopen.

### Standards

#### Finding 1 - High - Credit actions still do not share their write predicates

`appraisal_available_actions()` enables sanction from status, role, and permission, while the public
handoff additionally enforces verified provenance, complete frozen appraisal/risk facts, and exact
immutable-review consistency. Loan-limit availability likewise omits the write's stored-eligible-
assessment predicate. An enabled action can therefore be rejected by the same owning module,
contrary to API §44 and codebase-design §§12.3/23.4/42.2. Corrective High-risk `006H7` requires one
transition evaluation per public mutation, consumed by both projection and execution.

#### Finding 2 - High - 006H6 again completed without its named real-container proof

The committed frontend test server-renders the injected `AppraisalWorkbenchView` and checks raw
source text. It never mounts the default container, clicks mutations, or observes mocked HTTP,
four-read refresh, field errors, denial, or one-call stale behavior. The attempted Testing Library
suite failed because the package was absent and was then not committed; the passing wrapper tests
cannot detect broken controller wiring. `006H7` pins the standard test package and makes the full
mounted interaction matrix an acceptance condition under codebase-design §26.3.

#### Finding 3 - Medium - React still owns a parallel appraisal action matrix

Although 006H6 now retains six-field action objects and disabled reasons, `canEdit`, `canSubmit`,
`canRevalidate`, `canReview`, and `canSanction` independently combine status, provenance, role, and
permission rules. This remains a second workflow matrix under codebase-design §§23.3-23.4/42.3.
`006H7` makes backend `enabled` authoritative and limits `/auth/me` intersection to usability.

### Spec

#### Finding 1 - High - 005E3 still applies one permission to four distinct actions

The slice explicitly required the exact pass, return, resolve, and rejection-note validators and
removal of the global `complete_check` switch. Instead, `completeness_available_actions()` derives
one completeness-check authority and assigns it to every action; the write endpoints do the same.
Source auth §§12.4/25.2/34.3 assigns distinct `complete_check`, `return_deficiency`,
`deficiency.resolve`, and `rejection_note.create` permissions. The action also omits
`required_role`, so it is not the promised six-field projection. High-risk `005E4` aligns every
endpoint and projection with its source-defined permission/object/state/resource gate.

#### Finding 2 - High - 006H6 action projections contradict named service gates

The slice requires parity across reference, completeness, stage, prerequisite, appraisal, role,
permission, object, maker-checker, provenance, history, and rejection conditions. Loan-limit
projection checks only appraisal existence/permissions, and appraisal review/sanction projection
omits maker-checker and handoff integrity predicates. `006H7` owns the exhaustive public-boundary
parity matrix and zero-success-evidence denial assertions.

#### Finding 3 - High - 006H6's mandatory interaction matrix is unimplemented

The slice required the default export to exercise every workbench mutation through mocked HTTP
with exact bodies/counts, canonical reads, validation, `403`, and `409`. Static child rendering and
source-string checks implement none of that contract. `006H7` restores the same acceptance without
allowing another proxy test.

#### Finding 4 - Medium - 005E3 browser evidence is incomplete and tied to a deleted worktree

The Playwright spec hard-codes run `2026-07-11_194100`, produced no screenshots, and omits its
required denied and API-error captures; the independent E2E gate ran unrelated tracer/auth specs.
`005E4` declares the focused trusted-browser contract, derives paths from `RALPH_EVIDENCE_DIR`, and
requires all nine named screenshots twice.

### Verified Closures, Functional IDs, Context, and Queue

005E3 genuinely joins the document and completeness projections and restores S12 category/item/
document composition. 005FA4 genuinely tests unset/false/true through real App imports, removes the
borrower from staff demo roles, and its trusted portal login/logout contract passed twice with both
screenshots. 006G5 genuinely classifies relative, aliased, wildcard, and package-context imports
while retaining ADR-0005's non-vacuous public edge. 006H6 removes the HTTP-owned action matrix,
retains full action objects/reasons, and implements the four-read refresh shape, but parity and
interaction acceptance remain open.

No epic becomes complete. M03-FR-010 through M03-FR-012 have backend behavior, but completeness
authority/browser confidence remains High risk until 005E4. M04-FR-004 through M04-FR-011 remain
backend-present, but frontend/action confidence remains High risk until 006H7 -> 006H3 -> 006X;
M04-FR-001/002 remain deferred to 012EA under A-053 and M04-FR-003 retains A-054's proxy. No ADR is
needed because the cited source permissions, API §44, codebase-design rules, and ADR-0005 already
settle the durable decisions. The next sequence is 005E4 -> 006H7 -> 006H3 -> 006X.

Summary: Standards found 2 High and 1 Medium issue; worst are false-positive credit actions and the
missing real-container proof. Spec found 3 High and 1 Medium issue; worst are wrong completeness
authority and credit projections/tests that still do not meet 006H6's explicit contract.

## 2026-07-11 19:23 - Architecture Review 2026-07-11_191720_architecture_review

Reviewed completed product/corrective work since architecture-review commit `d5632d2`:
- `005E2-completeness-workbench-real-data-corrective` (`b4496eb`)
- `005FA3-portal-auth-interaction-and-demo-flag-proof` (`f147886`)
- `006G4-sanction-dependency-boundary-regression` (`bad2049`)
- `006H5-app-shell-application-state-authority` (`4d1351f`)

The review checked `git diff d5632d2...HEAD`, the four slice/run packets, implementation and tests,
Epic 005/006 digests, ADR-0005, the cited source sections, and the previous review findings.
Intervening commits `05d0793`, `d4c804d`, and `a4941b2` are Ralph-orchestrator-only and were not
treated as product slices. Standards and spec fidelity were reviewed independently. Production code
was not changed. `.ralph/state.json` has no Blocked slices to reopen.

### Standards

#### Finding 1 - High - Completeness action authority remains global and frontend-owned

`CompletenessWorkbench.tsx` uses one global `applications.loan_application.complete_check` flag
for pass, return, deficiency resolution, and rejection, then combines it with local blocker/status
conditions. The completeness APIs expose no resource `available_actions`, so object/state denial
cannot remove or explain an individual control before the backend rejects it. The 005E2 slice
documented this as an interim fallback, but it remains architecture drift from codebase-design
§23.3-§23.4 and api-contracts §44. Corrective High-risk `005E3` adds action/service parity behind
the applications module and makes React consume the full projection.

#### Finding 2 - High - 005E2 redesigned the approved S12 composition

The real-data rewrite flattened the prototype's category groups, item detail/document-chip rows,
and established deficiency/action composition into a new checklist/card layout. That exceeds the
binding Frontend Design Rules' data/label/visibility/action allowance and repeats the visual drift
pattern already found in 006H. `005E3` restores the pre-005E2 composition without restoring mock
facts or local decisions.

#### Finding 3 - Medium - Most completeness mutations are not tested through the container

The API wrapper tests have exact requests and the Playwright controller substantively exercises
pass and return, but resolve/reject, per-action denial, validation, canonical reload, and one-call
stale behavior are not clicked through the production container. Static markup/source assertions
cannot catch broken controller wiring. `005E3` owns the full mocked-HTTP and deterministic
Playwright matrix required by codebase-design §26.3.

#### Finding 4 - High - 006G4's guard ignores relative imports

`resolved_import_references` ignores `ast.ImportFrom.level`. A production import such as
`from ..approvals import modules` is reduced to `approvals.modules`, never matches the absolute
`sfpcl_credit.approvals` prefix, and silently passes. This leaves the exact ADR-0005 cycle 006G4
promised to prevent. Corrective Medium-risk `006G5` resolves every import against the scanned
module's package and keeps the non-vacuous public-edge assertion; 006H6 now depends on it.

### Spec

#### Finding 1 - High - 005E2 performs a decorative checklist request

005E2 requires checklist state from both `document-checklist` and `completeness-check`, while S12
separates application, document, nominee, and deficiency facts. `loadSelected` awaits the document
checklist but discards its result and renders only `completeness.required_checklist_items`. A
divergence therefore fails neither closed nor visibly. `005E3` assigns each projection explicit
authority, joins them by document type, and tests mismatches.

#### Finding 2 - Medium - 005FA3 does not prove all flag states through the real boundary

The default Playwright path exercises the real App, login, and logout, but
`demoAuthFlag.test.tsx` manually passes the imported flag into a static `LoginScreen`. It does not
mount the promised real App/RoleProvider boundary for explicit false and true, and its no-bypass
check is only an absent literal. Corrective High-risk `005FA4` supplies module-isolated real-boundary
proof plus successful browser evidence for unset/false/true and failed-network logout.

#### Finding 3 - High - 006G4 does not reject every promised import form

The slice explicitly requires every credit-to-approvals dependency form to fail. Relative imports
bypass the implemented absolute-prefix classifier, and no synthetic relative fixture exists.
`006G5` owns failing-first relative/package/alias fixtures and a context-aware repository scan.

#### Finding 4 - Low - 006H5 lacks its required screenshot

006H5 correctly removes App's mock seed and local status mutation, and its real component render
proves the sole SanctionWorkbench consumer shows honest not-connected copy. The sandbox prevented
the acceptance-criteria screenshot, leaving only `visual-state.md`; no production correction is
needed because 007I owns final sanction wiring and future visual evidence.

### Verified Closures, Functional IDs, Context, and Queue

005E2 removes mock/reference/state authority and uses exact existing endpoints; 005FA3's real
default browser spec proves empty/populated login and fail-closed logout; 006G4 handles absolute
aliases/package exposure and prevents vacuous scans; 006H5 removes App-owned mock workflow state.
No epic became fully complete in this window, so no new M03/M04 functional-ID closure is claimed.
M03 completeness confidence awaits 005E3; the existing M04 deferrals and 006H6/006H3 chain remain.

`CONTEXT.md` was corrected because the routed sanction screen now intentionally shows an empty
not-connected state rather than rendering its file-level mock fallback. There were no Blocked
slices. No new ADR was needed: ADR-0005 and existing frontend/action-authority standards already
settle the durable decisions. The next corrective sequence is 005E3 -> 005FA4 -> 006G5 -> 006H6 ->
006H3 -> 006X.

Summary: Standards found 3 High and 1 Medium issues; worst are completeness action/visual drift and
the relative-import escape. Spec found 2 High, 1 Medium, and 1 Low issue; worst are discarded
checklist authority and a dependency guard that misses a promised import class.

## 2026-07-11 14:00 - Architecture Review 2026-07-11_135129_architecture_review

Reviewed completed product/corrective work since architecture-review commit `1f1d500`:
- `002J2-forbidden-permission-error-contract-alignment` (`9e226e2`)
- `004E2-witness-evidence-snapshot-and-input-hardening` (`b3a688b`)
- `006G3-sanction-handoff-dependency-and-evidence-ownership` (`4d1dafe`)
- owner-applied `005FA2` portal-auth and `006Z2` interim loan-limit cleanup (`9195ab9`)
- `CR-001-e2e-visual-baselines-nondeterministic` (`0d284fb`)
- `006H4-workbench-authoritative-actions-and-container-tests` (`e7f3f3b`)

The review checked `git diff 1f1d500...HEAD`, the five Ralph run packets, the owner-applied
corrective commit, migrations, implementation/tests, Epic 002/004/005/006 digests, and cited source
sections. Standards and spec fidelity were reviewed independently. Production code was not changed.
`CONTEXT.md` remains truthful, and `.ralph/state.json` has no Blocked slices to reopen.

### Standards

#### Finding 1 - High - Credit action authority is duplicated in the HTTP view and disagrees with service gates

`applications.views._credit_action_snapshot` decides workflow state, legacy repair, role, and
permission availability from response-key heuristics. That violates codebase-design §6.3/§36.1/
§42.2's thin-view boundary. It also enables eligibility and loan-limit actions whenever their
snapshots and global permissions exist, without checking the formal reference, completeness,
application stage, later appraisal, or sanction conditions enforced by the underlying modules.
An advertised action can therefore be rejected by the supposedly matching authoritative service.
Corrective action: created High-risk `006H6-workbench-action-projection-and-interaction-proof` to
move projection behind the public module seam and prove action/service parity.

#### Finding 2 - High - 006H4 again omits the required real-container HTTP/action tests

The slice requires mounting the default workbench, selecting an application, clicking every action,
and asserting exact requests, one-call stale behavior, canonical reload, and visible state. The
committed test still imports only `AppraisalWorkbenchView`, server-renders static markup, and adds a
raw-source regex. This repeats the prior review finding and violates codebase-design §26.3's mocked-
HTTP frontend test seam. `006H6` now owns the full interaction matrix before visual restoration.

#### Finding 3 - Medium - The workbench discards most of the standard action contract

`AppraisalWorkbench.tsx` flattens four typed §44 action collections into enabled code strings,
discarding disabled reasons, labels, roles, and required permissions, then reinterprets status/
permission rules locally. This is safer than the former global-action union but still drifts from
api-contracts §44 and codebase-design §23.3-§23.4. `006H6` preserves full action objects and renders
the backend's denial facts without a parallel React workflow matrix.

#### Finding 4 - Medium - The interim portal limit cleanup changed the approved visual system

Removing client-owned money arithmetic was necessary, but `MP05_NewApplication.tsx` replaced the
approved three-column green limit-card composition with a one-column slate notice and changed the
red over-limit alert to slate. That violates the binding Frontend Design Rules' colour, layout, and
card constraints. Existing `006Z2` is sharpened to restore the original composition with server
projections and source-safe advisory copy.

### Spec

#### Finding 1 - High - 006H4's named acceptance proof is essentially unimplemented

The slice's Test Cases require exact default-container URL/body/request-count/refresh/output proof
for eligibility, limit, appraisal create/update/revalidate/submit/review/return/reject/sanction,
roles, object denial, stale writes, and sanction identity. None is exercised through the container.
The static tests can pass while the real effects and action handler are broken. Corrective action:
`006H6`, and `006H3` now depends on it.

#### Finding 2 - High - The owner-applied 005FA2 auth fix lacks its required interaction/flag proof

The production fallback was removed, but `005FA2` is marked Complete outside Ralph while absent
from `completed_slices`; its checklist/evidence is empty. Tests inspect source strings and static
context markup rather than submitting an empty form, proving false/true demo-flag behavior, or
exercising logout identity clearing. Created High-risk
`005FA3-portal-auth-interaction-and-demo-flag-proof`. The state ledger now records the owner-applied
005FA2 work while 005FA3 owns independent closure.

#### Finding 3 - Medium - 006G3's import guard does not cover every promised alias/package form

The production dependency direction and exact event ownership are correct, but the AST collector
records only `ImportFrom.module`. It misses forms such as `from sfpcl_credit import approvals as a`,
and its approvals-side private-boundary check rejects only one exact `credit.modules.common`
literal. This is narrower than 006G3's explicit aliased/package/private-module test contract.
Created Medium-risk `006G4-sanction-dependency-boundary-regression` with positive and negative
synthetic fixtures plus a non-vacuous repository scan.

#### Finding 4 - Medium - Interim portal copy invents an unstated over-limit outcome

The interim panel says an above-limit request “may be reduced or returned.” Source Epic 006
contracts say it sets an exception-required flag/warning and enters the configured exception
workflow; they do not promise reduction or return. `006Z2` is sharpened to display only the server
projection/warning and configured exception status while restoring prototype fidelity.

### Verified Closures, Test Quality, and Functional IDs

002J2 externally emits `FORBIDDEN` and preserves specialized denial codes; its compatibility
adapter intentionally remains while older test expectations are migrated. 004E2's current writes,
conservative A-063 legacy backfill, immutable reads, malformed-body zero-write cases, and exact
index/migration assertions close M02-FR-009/BR-010. 006G3 removes the app cycle and durably binds the
exact workflow event with substantive rollback and PostgreSQL race assertions. CR-001 freezes only
the two dashboard baselines, pins `Asia/Kolkata`, resolves the shared venv from Git common-dir, and
its independent log runs both scenarios twice successfully.

No epic became fully complete in this window. M04-FR-004 through M04-FR-011 remain backend-present;
FR-010/FR-011 UI confidence remains High risk until 006H6 and 006H3. M04-FR-001/M04-FR-002 remain
explicitly deferred to 012EA under A-053, and M04-FR-003 retains A-054's receipt-time proxy.

Summary: Standards found 2 High and 2 Medium issues; worst is a view-owned action projection that
can contradict backend transition gates. Spec found 2 High and 2 Medium issues; worst is 006H4
being marked complete for a real-container contract it did not test.

## 2026-07-11 03:08 - Architecture Review 2026-07-11_030117_architecture_review

Reviewed completed product slices since architecture-review commit `6efe1a8`:
- `006E4-legacy-appraisal-remediation-and-history-backfill` (`69d5af0`)
- `006F4-postgresql-credit-concurrency-acceptance` (`1b5b24a`)
- `004E-witness-shareholder-validation` (`c25950f`)
- `006G2-sanction-handoff-module-and-read-contract` (`d7f98c9`)
- `006H2-workbench-action-contract-hardening` (`55a9074`)

The review checked `git diff 6efe1a8...HEAD`, the five slice/run packets, migrations,
implementation/tests, Epic 004/006 digests, ADR-0005, and cited source sections. Standards and spec
fidelity were reviewed independently. Production code was not changed. `CONTEXT.md` still describes
the repository truthfully, and `.ralph/state.json` contains no Blocked slices to reopen.

### Standards

#### Finding 1 - High - Global permissions still override resource action authority

`AppraisalWorkbench.tsx` unions `/auth/me.available_actions` with appraisal/case actions before
checking controls. `/auth/me.available_actions` is the user's complete permission list, while the
appraisal serializer returns no resource actions. Therefore an empty resource action list cannot
deny a globally permissioned user, React still owns the state/role matrix, and the dedicated legacy
revalidation action never reaches the real container. This violates codebase-design §23.3-§23.4
and the central 006H2 requirement. Corrective action: created High-risk
`006H4-workbench-authoritative-actions-and-container-tests` and made 006H3 depend on it.

#### Finding 2 - High - Required real-container action tests are still absent

`AppraisalWorkbench.test.tsx` server-renders only `AppraisalWorkbenchView` with injected props and
mock callbacks. The API tests invoke wrappers directly. No test mounts the default container,
selects an application, clicks an action, observes HTTP/state refresh, or proves a resource denial
beats `/auth/me`. This repeats the prior review's explicit test-quality finding and violates
codebase-design §26.3 plus 006H2's Test Cases/Acceptance Criteria. 006H4 owns failing-first container
coverage for every action, denial, stale write, returned draft, legacy repair, and sanction reload.

#### Finding 3 - High - The sanction seam introduced the dependency cycle ADR-0005 forbids

`credit.modules.appraisal_workflow` imports the approvals handoff while that handoff imports
credit-owned errors/object-access logic. Codebase-design §36.2 permits `approvals -> credit`, not
the reverse, and explicitly says a circular dependency means the seam is misplaced. The narrow
static test rejects only `credit -> approvals.models`, so it certifies an interface import while
missing the package cycle. Corrective action: created High-risk
`006G3-sanction-handoff-dependency-and-evidence-ownership`.

#### Finding 4 - Medium - New permission denials preserve a source-contract error code drift

The witness endpoint returns `403 PERMISSION_DENIED`; source API §7.1 defines missing permission as
`403 FORBIDDEN` and reserves distinct codes for object, sensitive-field, and approval-authority
denials. This is inherited by many earlier adapters and the local contract harness, but 004E added
another endpoint that cements the divergence. Corrective action: created Medium-risk
`002J2-forbidden-permission-error-contract-alignment` to migrate the shared contract without
changing authorization decisions.

#### Finding 5 - Medium - 006F4 altered authoritative assertions despite its no-change rule

006F4 correctly ran all five PostgreSQL races twice with zero skips and fixed invalid fixture
binding. However, it replaced structured workflow action/metadata assertions with decision-ID
substring checks even though the slice required the five tests to execute without changing or
weakening assertions. The old fields were retired, so a canonical assertion update was necessary,
but substring matching is weaker than exact state/reason/identity proof. 006G3 owns exact canonical
workflow evidence assertions while rerunning the same five-race acceptance.

### Spec

#### Finding 1 - High - 006H2 implemented action authority incorrectly

006H2 requires controls from backend resource `available_actions` intersected with `/auth/me`
usability and says controls disappear when the server denies them. The global-permission union and
missing appraisal action projection implement the opposite precedence. The real legacy-repair
button is unreachable, while other controls can remain visible from permission plus local state.
Corrective action: 006H4 adds the object/state-aware backend projection and makes React intersect,
never union, resource actions.

#### Finding 2 - High - 006H2's mandated behavior proof is partial

The slice explicitly requires mounting the real container, mocked HTTP, clicking every action, and
asserting exact bodies plus refresh/error/role/object/stale behavior. Static markup and direct API
wrapper tests do not meet that requirement and concealed Spec Finding 1. Corrective action: 006H4.

#### Finding 3 - Medium - Malformed witness JSON can escape the standard 400 envelope

004E requires malformed input to return a standard validation envelope. `parse_json_body` raises
Django `ValidationError` for malformed or non-object JSON, but the witness adapter catches only its
domain `WitnessValidationError`. Corrective action: created Medium-risk
`004E2-witness-evidence-snapshot-and-input-hardening` with failing-first malformed-body/no-write
coverage.

#### Finding 4 - Medium - Witness verification-time folio evidence is not persisted

004E says the qualifying shareholding folio is persisted evidence. `Witness` stores neither the
shareholding nor a folio snapshot; every GET reselects the currently first active positive holding
and otherwise falls back to the mutable member folio. Later shareholding changes can therefore
rewrite the returned basis for an old verification. The same model also creates redundant automatic
and explicit application/hash indexes. 004E2 owns an unambiguous legacy backfill, immutable
shareholding/folio evidence, stable read regression, and index cleanup.

#### Finding 5 - Medium - Approval handoff does not own the workflow event promised by 006G2

006G2 says the approvals module returns the created workflow-event UUID. Credit still creates the
event and passes it to approvals serialization; reload then queries the newest matching application
event instead of a durable case-linked creation result. 006G3 moves the event into the atomic
approvals handoff and proves exact create/reload identity and rollback.

### Test Quality and Functional IDs

006E4's state-specific remediation, append-only migration, negative paths, and rollback assertions
are substantive. 006F4's two real PostgreSQL runs execute all five races and close the prior
critical acceptance gap, subject to the exact-evidence assertion correction above. 004E's core
permission/KYC/name/shareholder/masking/audit matrix is useful but misses malformed bodies and
historical evidence stability. 006G2's rollback/read cases are meaningful but its dependency test
is too narrow. 006H2's projection/client assertions are useful but do not substitute for container
behavior.

M02-FR-009/BR-010 is behaviorally present but remains Medium risk until 004E2 makes its evidence
durable. M04-FR-004 through M04-FR-011 remain implemented at the backend; confidence in FR-010/
FR-011's reachable UI path remains High risk until 006H4. M04-FR-001/M04-FR-002 remain explicitly
deferred to 012EA under A-053, and M04-FR-003 retains the explicit A-054 receipt-time proxy. No new
M03 requirement was claimed by 004E, and no material scope creep was found.

Summary: Standards found 3 High and 2 Medium issues; worst is resource authorization remaining
client/global-permission driven and untested. Spec found 2 High and 3 Medium issues; worst is the
same broken 006H2 authority/interaction contract. Corrective order is 002J2 -> 004E2 -> 006G3 ->
006H4 -> 006H3 -> 006X.

## 2026-07-10 21:39 - Architecture Review 2026-07-10_213352_architecture_review

Reviewed completed product slices since architecture-review commit `46442fe`:
- `006E3-appraisal-history-and-review-authority-hardening` (`cd3aca6`)
- `006F3-appraisal-lock-order-and-postgresql-concurrency-closure` (`b022c83`)
- `006G-submit-to-sanction` (`b1b8889`)
- `006H-eligibility-appraisal-frontend-integration` (`b7cf63f`)

The review checked `git diff 46442fe...HEAD`, the four slice/run packets, migrations, backend and
frontend implementation/tests, Epic 006 and both Epic 006/007 digests, and the cited primary-source
sections. Standards and spec fidelity were reviewed independently. Production code was not changed.

### Standards

#### Finding 1 - Critical - Required PostgreSQL acceptance failed but the slices merged

006F3 explicitly says a connection failure or collected-but-unexecuted test is failed acceptance
and that the slice must not be marked Complete or merged. Its committed review packet says “Failed
acceptance; do not commit or merge”: four PostgreSQL tests were found, zero executed. The next
artifact nevertheless says Success, state marks 006F3 Complete, and 006G ran. 006G then added a
fifth PostgreSQL-only duplicate-submission race; that command also found the test and executed zero
while the run reported success.

This repeats the prior architecture review's highest-risk finding and violates 006F3/006G plus
Decision Policy §2. Corrective action: created High-risk
`006F4-postgresql-credit-concurrency-acceptance`. It must execute all five loan-limit, appraisal,
and sanction races twice on real PostgreSQL with zero skips; unavailable execution is failure.

#### Finding 2 - High - Frontend recreates backend workflow state and loses action authority

The workbench derives action availability from a locally maintained role/permission/status matrix
instead of backend `available_actions`. After sanction POST, the response does not contain the new
application/appraisal statuses, so React hard-codes both strings. Revalidation is shown under
submit-review permission even though the backend requires update plus risk-management authority and
legacy-unverified state. This violates codebase-design §23.3-§23.4 and 006H's no-synthesis rule.

Corrective action: 006G2 returns canonical states/actions and a reload-safe case read; 006H2 consumes
them and deletes the local workflow matrix/status synthesis.

#### Finding 3 - High - The approved Appraisal Workbench was redesigned without visual proof

006H replaced the approved 1,186-line staged queue/detail workbench with a 226-line condensed form
and rewrote the eligibility and calculator compositions. These are layout/card/density changes, not
only labels, data, visibility, and actions. That violates the binding Frontend Design Rules and the
slice's preserve/reuse requirement. No screenshot or visual-regression result exists; the packet
defers visual proof to 006X despite the 006H visual acceptance requirement.

Corrective action: created Medium-risk `006H3-appraisal-workbench-prototype-fidelity-restoration`.
It restores the pre-006H composition with real data and requires host screenshots/visual regression.

#### Finding 4 - High - Frontend tests do not exercise the implemented action path

`AppraisalWorkbench.test.tsx` renders only the presentational view to static markup. It never mounts
the container, runs effects, clicks a control, mocks HTTP at the UI interface, verifies mutation
refresh, or proves one-call stale behavior through the page. This fails codebase-design §26.3 and
006H's explicit render/action-test requirement. The missing interaction path concealed the broken
PATCH and revalidation gates described below.

Corrective action: created High-risk `006H2-workbench-action-contract-hardening`, with real container
tests for every action and exact request/response/state assertions.

#### Finding 5 - Medium - Sanction handoff crosses the module seam in the wrong direction

`credit.modules.appraisal_workflow` imports and persists the concrete `approvals.ApprovalCase`
model. The documented direction is `approvals -> credit`, and the source names
`approvals.modules.approval_case_engine` as the case seam. Keeping creation in credit would spread
case uniqueness, reads, matrix enrichment, and later action invariants across two apps.

Corrective action: accepted ADR-0005 and created High-risk 006G2. Approval-case creation/read/
serialization move behind one approvals-owned module interface; credit retains frozen appraisal,
review consistency, and lock-order behavior without importing the concrete approvals model.

#### Finding 6 - Medium - Malformed sanction JSON can escape the standard envelope

The new sanction view does not catch `ValidationError` from malformed or non-object JSON, unlike
established application adapters. That input can escape the standard `400 VALIDATION_ERROR`
contract. Corrective action: 006G2 owns the malformed-body envelope regression.

#### Finding 7 - Medium - New transport code duplicates and weakens existing client behavior

`creditAssessmentApi.ts` implements another authenticated `fetch` path that discards envelope
metadata and has no shared refresh/401/request-ID behavior. This violates codebase-design §23.5
and increases transport duplication.

Corrective action: 006H2 must reuse the shared authenticated request/envelope implementation
instead of layering another shallow client.

### Spec

#### Finding 1 - Critical - PostgreSQL outcomes required by 006F3/006G are absent

Same acceptance evidence as Standards Finding 1. The tests themselves assert meaningful competing
outcomes, but none ran on the database whose row locks they are meant to prove. 006F4 owns closure.

#### Finding 2 - High - Existing and returned appraisals cannot be saved from the workbench

On load, the full appraisal GET response becomes the edit form. Save PATCH sends that object back,
while the adapter removes only a null tenure. Response-only IDs, frozen snapshots, provenance,
review history, status, reviewers, TAT, and rejection facts therefore hit the backend's strict
unknown-field validation. The client test avoids the defect by PATCHing only a hand-built amount.
This breaks 006H's required update and returned-draft revise/resubmit flows.

Corrective action: 006H2 adds an exact response-to-writable-draft projection and interaction tests
that save both ordinary and returned drafts.

#### Finding 3 - High - Migration 0005 can permanently strand legacy appraisals

Migration 0005 downgrades unproven appraisals in every state to `legacy_unverified`, but explicit
revalidation is draft-only while review and sanction require verified provenance. A
`review_pending` or `reviewed` legacy row therefore has no repair path. The migration also skips the
latest known returned decision when the appraisal was resubmitted and is now `review_pending`, so a
reason that is still present in the latest projection is not backfilled. Fixtures cover neither
case, contrary to 006E3's “blocked until revalidation succeeds” and latest-known-backfill contract.

Corrective action: created High-risk `006E4-legacy-appraisal-remediation-and-history-backfill` and
recorded conservative remediation assumption A-061. New evidence never inherits an old review;
immutable history remains, and reviewed rows require maker resubmission plus fresh review.

#### Finding 4 - Medium - Pending case identity is not recoverable after reload

006H requires API-loaded sanction state and retention of the case UUID for Epic 007. The loader
fetches only eligibility, limit, and appraisal, then clears `sanctionSubmission`; no subsequent read
returns the case. A reload shows only a generic submitted label and loses the UUID. The same POST
response also omits canonical application/appraisal statuses, causing the client synthesis above.

Corrective action: ADR-0005/006G2 add one case-summary read and complete state response; 006H2 loads
and retains them.

#### Finding 5 - Medium - Revalidation uses the wrong UI authority and state

The revalidation button is controlled by draft state plus submit-review permission, although the
backend requires update plus risk-management permissions and the action is meaningful only for
legacy-unverified provenance. Authorized repair users can be blocked while submit-only users see an
action guaranteed to fail. Corrective action: 006H2 consumes the backend action contract.

### Test Quality and Functional IDs

006E3's authority, positive chronology, append-only history, rollback, and migration tests are
otherwise substantive. 006G's SQLite functional suite meaningfully covers strict payloads,
permissions/scope, invalid/rejected/repeated states, history consistency, redaction, and rollback.
The test gaps are specific: non-draft migration remediation, real PostgreSQL execution, and actual
frontend container actions/visual regression.

M04-FR-004 through M04-FR-009 have implemented backend behavior and substantive assertions.
M04-FR-010/M04-FR-011 behavior exists but remains High-risk until 006E4/006F4/006G2 close legacy,
concurrency, and sanction-handoff defects. M04-FR-001/M04-FR-002 remain explicitly deferred to
012EA under A-053; M04-FR-003 retains the explicit A-054 receipt-time proxy. Epic 006 is not
complete and 006X now depends on 006H3.

Summary: Standards found 1 Critical, 3 High, and 3 Medium issues; worst is merging explicitly failed
PostgreSQL acceptance. Spec found 1 Critical, 2 High, and 2 Medium issues; worst is the same absent
database proof, followed by permanently stranded legacy rows and an unusable update path.

## 2026-07-10 19:15 - Architecture Review 2026-07-10_190455_architecture_review

Reviewed completed product slices since architecture-review commit `d29f697`:
- `006D2C-loan-limit-concurrency-and-boundary-regression` (`9dd5386`)
- `006E2-appraisal-source-contract-and-snapshot-hardening` (`d5753d1`)
- `006F-credit-manager-review` (`2684996`)
- `006F2-credit-manager-appraisal-rejection` (`3f7f386`)

The review checked `git diff d29f697...HEAD`, all four slice/run packets, implementation, migrations,
tests, Epic 006 and its digest, and the cited source sections. Standards and spec fidelity were
reviewed independently. No material scope creep was found.

### Finding 1 - High - Legacy appraisals are labelled verified without positive audit proof

006E2 permits a legacy projection copy only when audit chronology proves the current assessment was
the appraisal's original input. Migration 0003 instead treats absence of a later audit as proof: if
the source timestamps predate preparation and no later success row is found, it copies the current
rows and writes `prerequisite_provenance = verified`. Its “safe” migration fixture creates no
eligibility or loan-limit success audit at all, so the test enshrines missing evidence as proof.

That can silently bless manually imported, partially audited, or historically incomplete current
assessment rows as the decision basis, contrary to ADR-0003 and the slice's conservative legacy
contract. Corrective action: accepted ADR-0004 for the related review-history design and created
High-risk `006E3-appraisal-history-and-review-authority-hardening`. Its forward repair requires
positive pre-appraisal success evidence for both exact prerequisite IDs, downgrades every
unproven/later-rerun row to `legacy_unverified`, and keeps explicit revalidation as the only repair.

### Finding 2 - High - Review authority is permissioned but not Credit-Manager-only

Source auth §25.3 says appraisal review requires `credit.appraisal.review` and “User must be Credit
Manager”; 006F likewise requires the Credit Manager credit-domain boundary. `review()` checks the
permission and then the generic application object-access helper. That helper grants owner access,
so a non-Credit-Manager application creator/receiver who is granted the permission can review their
in-scope application. Existing tests cover maker-checker, no permission, and an out-of-scope user,
but not an in-scope non-Credit-Manager permission holder.

Corrective action: 006E3 requires both the exact permission and `credit_manager` role membership,
with a negative owner/receiver regression and no-success-evidence assertions. Role is not inferred
from a permission grant.

### Finding 3 - High - A returned review reason is overwritten by the next review

006F requires a non-blank returned reason and explicitly says not to lose it and to retain prior
return history. The implementation stores only latest `review_comments`/`last_review_decision` on
the appraisal. When the maker revises/resubmits and the Credit Manager reviews again, the second
decision overwrites the original return reason. Generic audit correctly omits comments, so neither
audit nor workflow can recover it. The return/resubmit/re-review test asserts state and event counts
but never asserts that the first reason survives.

Corrective action: ADR-0004 makes an immutable appraisal-owned decision record the historical
source while the existing fields remain a latest projection. 006E3 adds/backfills that record,
keeps reason text outside generic audit JSON, and proves returned and final decisions both survive.

### Finding 4 - High - Mandatory PostgreSQL concurrency evidence was skipped before merge

006D2C says its competing-calculation proof is authoritative only on PostgreSQL and explicitly says
not to commit/merge if the command does not pass. The committed evidence contains a missing-driver
failure and two SQLite skips; its own review packet says “Success pending required PostgreSQL
independent validation.” Nevertheless the slice is Complete and was merged. This review confirmed
`psycopg 3.3.4` is now installed, but no PostgreSQL server is reachable and sandboxed `initdb`
cannot allocate the required shared-memory segment, so there is still no green transaction outcome.

The new 006F2 rejection path also exposes an inverse lock order: draft creation/update locks
application then appraisal, while rejected review locks appraisal and then the rejection-note seam
locks application. Concurrent stale PATCH/reject requests can deadlock rather than cleanly serialize.

Corrective action: created High-risk `006F3-appraisal-lock-order-and-postgresql-concurrency-closure`.
It normalizes application → appraisal → rejection/history lock order, adds public-interface
competing-review regressions, and must execute both the new cases and the existing 006D2C cases on
real PostgreSQL with zero skips. 006G now depends on 006F3.

### Finding 5 - Medium - Contract summaries contradict the detailed implemented section

`docs/working/API_CONTRACTS.md`'s top-level appraisal row still says Credit Manager review is queued,
while its detailed 006F/006F2 section correctly documents reviewed/returned/rejected behavior. The
Epic 006 digest likewise retains an older requirement-status paragraph alongside newer implemented
sections. Corrective action: 006E3 must reconcile both summaries while updating the history contract.

### Finding 6 - Pass - Most tests have substantive outcome and rollback assertions

006D2C's PostgreSQL test design checks row/UUID cardinality, complete projections, deterministic
ordering, and matching audit/workflow outcomes; the failure is that it never executed on PostgreSQL.
006E2 covers frozen same-UUID projections, strict required fields, safe/ambiguous migration shapes,
revalidation scope, and rollback. 006F/006F2 cover state, maker-checker, permission/object denial,
rejection-note uniqueness, redaction, frozen facts, and forced cross-domain rollback. The findings
above are precise missing cases, not coverage-number complaints.

Functional-ID spot check: Epic 006 is not Complete. M04-FR-008/M04-FR-009 facts are implemented;
M04-FR-010 has review behavior but sanction gating remains 006G; M04-FR-011 rejection is reachable
but awaits 006E3 authority/history and 006F3 concurrency correction. M04-FR-001/M04-FR-002 remain
explicitly deferred to 012EA under A-053, and M04-FR-003 retains the explicit A-054 TAT-anchor
assumption. No completed epic is being falsely marked complete.

## 2026-07-10 17:33 - Architecture Review 2026-07-10_173305_architecture_review

Reviewed completed product slices since architecture-review commit `18d403e`:
- `005I5-application-ownership-and-nominee-authority-hardening` (`8016ca1`)
- `006D2B-credit-loan-limit-calculator-and-appraisal-seam` (`95f9bd4`)
- `006D3-credit-assessment-model-ownership-state-migration` (`007777b`)
- `006E-appraisal-note-create-edit-submit` (`14c1978`)

The review checked `git diff 18d403e...HEAD`, all four slice/run packets, implementation/tests,
Epic 005/006 digests, and the cited primary-source sections for disputed requirements.

### Finding 1 - High - Appraisal UUIDs do not freeze the financial decision basis

006E records only `eligibility_assessment_id_snapshot` and `loan_limit_assessment_id_snapshot`
plus caller-authored summaries. The reviewed 006D contract deliberately permits an explicit rerun
to replace the current assessment while retaining the same UUID. After such a rerun, an appraisal
cannot prove the cultivated acreage, policy version, share/land/final limits, eligibility checks,
or exception flag used for its recommendation. PATCH also rereads the current loan-limit row, so a
later rerun can change an existing draft's amount/exception boundary.

This fails API §3's snapshot-decision principle and 006E's handoff to consume stored 006B/006D
facts. Corrective action: accepted ADR-0003 and created High-risk `006E2-appraisal-source-contract-
and-snapshot-hardening`. It freezes canonical redacted projections on the appraisal, preserves IDs
only as provenance, and defines safe handling for legacy rows whose history is ambiguous.

### Finding 2 - High - Required appraisal reasons/repayment facts are accepted incompletely

Functional §9.8 and M04-FR-009 require repayment-capacity notes; 006E stores risk ratings and
mitigation but no required repayment-capacity field. The §24.3 submit endpoint also requires
`remarks`, yet the workflow validates and discards them: neither appraisal-owned state nor an
append-only submission record retains the compliance reason. The slice correctly keeps free text
out of audit JSON, but metadata-only audit does not justify losing the source request fact.

Corrective action: 006E2 adds exact `repayment_capacity_notes`, persists submission remarks outside
audit JSON, and adds rollback/redaction tests before Credit Manager review. M04-FR-008's amount,
tenure, interest/rate basis, and security facts remain implemented; no undocumented repayment
formula was invented.

### Finding 3 - High / owned deferral - Appraisal task, assignment, and rejection requirements lack current behavior

M04-FR-001/M04-FR-002 require one appraisal task after application-number generation assigned to
Deputy Manager – Finance. 006E creates an appraisal only when a caller POSTs and records that caller
as preparer; it does not persist assignment. The repository already intentionally deferred the
generic task engine to 012EA, so this review sharpened 012EA with the exact appraisal create,
role-assignment, close/reopen, idempotency, and backfill contract and recorded A-053. `prepared_by`
must never be relabelled as assignment.

M04-FR-011 separately requires Credit Manager rejection and a Rejection Note. 006F owns reviewed
and returned-for-revision only, while 006G owns sanction submission. Created High-risk 006F2 for a
terminal rejected decision that atomically creates one unsent 005H rejection-note draft; 006G now
depends on that correction.

### Finding 4 - Medium - Financial concurrency and static-boundary tests are incomplete

006D2B substantially improves its AST regression, but the appraisal concrete-model check examines
only `from sfpcl_credit.credit.models import ...`. A package import such as
`import sfpcl_credit.credit.models as credit_models` can bypass it, and the public calculator check
uses `issubset`, so removing the required import entirely satisfies the assertion. This does not
currently mask a production bypass, but it does not fully enforce the slice's promised boundary.
Its lock test also mocks each manager and asserts `select_for_update` was called; that proves the
requested API, not the competing-transaction outcome required for financial modules by
codebase-design §26.3.

Corrective action: created High-risk `006D2C-loan-limit-concurrency-and-boundary-regression` before
006E2. It adds an independent-connection transactional outcome proof and rejects both import forms/
aliases while avoiding brittle exact-full-method-set assertions.

### Finding 5 - Pass - The reviewed corrections have substantive tests

005I5 proves neutral owner projection, shared adult-nominee outcomes, invalid mutation
preservation, safe portal facts, and production-controller browser paths (browser execution remains
the recorded A-013 optional-gate limitation). 006D2B covers calculation branches, Decimal acreage,
locked source selection, canonical public/audit projection, rollback, and failed-rerun preservation.
006D3 proves forward/reverse state ownership with unchanged rows/UUID/FKs/evidence. 006E covers
strict create/PATCH/submit validation, permissions/object scope, TAT boundaries, prerequisite
gates, and create rollback; the gaps above are specific source/history omissions, not padding.

### Finding 6 - Watch - TAT anchor and risk cardinality remain explicit source tensions

006E uses `application.created_at + 2 days`, matching data-model §14.4's receipt wording and the
reviewed slice, while M04-FR-003 also names completeness confirmation and the model has no such
timestamp. A-054 retains `created_at` as the available receipt proxy until governance chooses an
anchor; historical due dates must not be silently rewritten. Risk is one-to-one in 006E although
§14.3 expresses a plain application FK; no current workflow requires multiple concurrent risk rows,
so this is watched rather than changed before review.

Functional-ID spot check: neither parent epic is Complete. M03-FR-003/M03-FR-009 behavior reviewed
in 005I5 is reachable. M04-FR-003-007 are implemented; M04-FR-008 is present through recommendation
amount/tenure/interest/security; M04-FR-009 is partial until 006E2; M04-FR-010 remains in 006F/006G;
M04-FR-011 is now owned by 006F2; and M04-FR-001/002 are explicitly deferred to 012EA by A-053.

## 2026-07-10 15:46 - Architecture Review 2026-07-10_154638_architecture_review

Reviewed completed product slices since architecture-review commit `c25fcfc`:
- `005I3-application-nominee-selection-contract` (`261641c`)
- `005I4-application-detail-backend-state-hardening` (`c20b72f`)
- `006C2-cultivated-acreage-source-hardening` (`7023475`)
- `006D2A-credit-eligibility-module-and-configuration-seam` (`5c6866a`)

Intervening E2E-baseline, owner configuration/slice-split, and owner capability-map commits were
inspected as context but excluded from product-slice findings. The review checked the pinned
`git diff c25fcfc...HEAD`, slice/run packets, implementation/tests, Epic 005/006 digests, and only
the cited primary-source sections needed to verify disputed requirements.

### Finding 1 - High - Intake actors are presented as assigned application owners

005I4 removed React's role/status owner inference, but the backend replacement still synthesizes
`assigned_owner` as `received_by_user or created_by_user`. Those fields record intake/audit actors;
they are not a persisted queue/task assignment. This is especially unsafe for member-portal drafts:
the portal user can become `received_by_user`, so staff detail can display the borrower as the
internal current owner. The backend test asserts this fallback, while the later-stage frontend test
injects an arbitrary owner DTO and never proves a real backend assignment.

This contradicts 005I4's requirement to render a backend-owned assignment or neutral absence and
source API §19.1's explicit assigned-owner fact. Corrective action: created
`005I5-application-ownership-and-nominee-authority-hardening`. Until an assignment/task model exists,
staff list/detail must return `assigned_owner = null`; receiver/creator remain distinct audit facts.

### Finding 2 - Medium - The portal nominee detail contract is incomplete

005I3's API/DTO safely returns nominee ID, name, age, minor flag, KYC, relationship, and signature
required status. MP10 renders name, relationship, age, KYC, and signature status but omits nominee
ID and minor/adult status. Its new frontend tests exercise only extracted selector views, not the
portal application-detail page, so the partial implementation remained green.

Corrective action: 005I5 must render every safe selected-nominee fact in portal detail and assert
that PAN/Aadhaar values, hashes, tokens, and reveal controls stay absent.

### Finding 3 - Medium - Nominee minority is decided independently in two React pages

Both staff and portal application forms added their own current-date/age-snapshot
`hasAdultNomineeEvidence` implementations and use them to decide step/submission availability.
This duplicates the backend intake and credit checks, already differs in evaluation shape, and
violates `codebase-design.md` §§23.3/42.3: React should render backend facts/errors rather than own
business decisions. The reviewed tests also omit invalid staff PATCH and portal
cross-member/unknown/minor/missing-age create/PATCH preservation paths required by 005I3.

Corrective action: 005I5 removes frontend age/minority calculations, establishes one public backend
nominee-validation seam for intake/completeness/eligibility, and adds the missing mutation/no-success-
evidence regressions.

### Finding 4 - Medium - Interface boundary tests do not yet enforce the intended architecture

006D2A moved eligibility behavior behind the source-named module and added meaningful direct tests,
including transaction rollback. However, its boundary regression checks runtime object identity and
the absence of old attribute names; it cannot catch aliased private imports. The new configuration
resolver also imports `CreditModuleValidationError`, creating a reverse
`configurations -> credit` dependency. The resolver function shape itself is an acceptable narrow
slice interface, but its error contract should not couple the configuration bounded context to a
consumer.

Corrective action: sharpened the already queued 006D2B to replace the weak check with static
AST/import-boundary coverage, remove the reverse dependency, prohibit direct policy queries, and
lock all mutable financial snapshot sources inside the calculator transaction. No new ADR is
needed because this follows the existing source module boundaries and ADR-0002.

### Finding 5 - Pass / owned follow-up - Cultivated-acreage correctness is substantive

006C2 blocks mismatched, unverified, cross-application, and rejected acreage evidence before
assessment/audit/workflow writes. Its tests cover Decimal-equivalent values, the nullable-profile
two-source path, and failed-rerun preservation of UUID/payload/evidence. The calculation still lives
in the generic application service and its tests are HTTP-heavy, but that is the explicit,
immediately queued 006D2B extraction rather than an unowned finding.

### Finding 6 - Watch - 005I4 tests split the production controller from the rendered view

The loader is tested with mocked HTTP and the view has substantive submitted/later-stage/neutral
assertions, but success/error data are injected into exported `ApplicationDetailView`; no test runs
the mounted production component's async success/error or submit-refresh path. 005I5 owns this
remaining test-seam correction and may use the existing E2E harness or a pinned dev-only DOM test
dependency.

Functional-spec spot check: neither Epic 005 nor Epic 006 is marked Complete. M03-FR-003 nominee
capture is backend-reachable but its portal presentation/authority regressions remain owned by
005I5; existing assumptions continue to own M03 signature/document deferrals. M04-FR-004 through
M04-FR-007 remain implemented or under the already queued deep-module extraction, while
M04-FR-001-003 and M04-FR-008-011 remain assigned to 006E-006G. No completed epic falsely claims
full requirement-ID coverage.

## 2026-07-10 09:32 - Architecture Review 2026-07-10_092630_architecture_review

Reviewed completed product slices since architecture-review commit `1e2d873`:
- `005I2-application-detail-api-state-hardening` (`e016d2a`)
- `006B-default-document-purpose-and-terms-eligibility-checks` (`c181819`)
- `006C-loan-limit-configuration-and-calculator` (`3f066cf`)
- `006D-loan-limit-snapshot-storage` (`9f9ae0b`)

The product review excluded config-only commit `c578e87` from findings. It checked the pinned
`git diff 1e2d873...HEAD`, four slice/run packets, implementation/tests, working contracts, Epic
005/006 digests, and only the cited primary-source sections needed for disputed requirements.

### Finding 1 - High - Application nominee selection is not reachable through the public contract

Source `api-contracts.md` §19.2 requires `nominee_id` when creating a loan application and §19.3
returns the selected nominee. The implemented application model/API stores no nominee. The member
nominee API intentionally creates member-level nominees without `loan_application_id`, so a real
staff or portal client cannot produce 006B's normal eligible nominee result. Instead, 006B reverse-
queries nullable legacy rows, orders them, and chooses `.first()`; its green test directly inserts a
linked nominee through the ORM. Multiple linked rows or absent age/DOB evidence are not tested.

This is an end-to-end blocker, not coverage padding: 006C requires `overall_result = eligible`, but
the intended API path cannot establish that result. Corrective action: created
`005I3-application-nominee-selection-contract` to persist/validate source §19.2 `nominee_id`, wire
staff/portal draft flows, make submit enforce the selected adult nominee, and make 006B use only
that deterministic application fact.

### Finding 2 - High - BR-020 can calculate from owned acreage rather than evidenced cultivated acreage

006C sums every selected `LandHolding.area_acres` and multiplies that total by scale of finance.
The selected `CropPlan.planned_area_acres` is checked only for owner/application/alignment, while
the profile's explicit `land_area_under_cultivation_acres` is unused. Functional-spec BR-020 says
the financial limit is based on acreage under cultivation. A borrower owning 20 acres with a
5-acre crop plan can therefore receive a 20-acre land limit. The test fixtures use equal 5-acre
facts, masking this edge case.

The source does not define precedence among the three acreage fields, so this review did not invent
a min/max rule. Corrective action: created `006C2-cultivated-acreage-source-hardening` and A-049.
Until source confirmation, applicable verified acreage facts must agree or calculation is blocked
without changing a stored snapshot/audit/workflow evidence.

### Finding 3 - Medium - Application Detail still invents later-stage workflow and ownership facts

005I2 correctly removed the `LO00000035` special branch, fake witnesses, nominee secrets, and added
staff-only rejection-note metadata. However, `ApplicationDetail.tsx` still spreads synthetic
documentation/disbursement defaults, shows fixed dates and completion claims in the stage stepper,
overwrites the backend `assigned_owner` with hardcoded department roles for later stages, and
computes payment readiness in React. Its new test injects `initialData` through a production-only
prop and checks only a submitted application, so none of the later-stage drift is exercised.

Corrective action: created `005I4-application-detail-backend-state-hardening`. It must render
backend state/actions or neutral absence, remove frontend workflow decisions, and test via mocked
HTTP using the same seam as production.

### Finding 4 - Medium - Credit business logic is deepening the generic application monolith

The reviewed changes put eligibility rules, loan-limit calculation, configuration selection,
persistence, serialization, and audit projection into `applications.services`, now 2,789 lines;
the combined application HTTP test file is 3,305 lines. This contradicts codebase-design §§12/26,
which name `credit.modules.eligibility_assessment`, `credit.modules.loan_limit_calculator`, and
`configurations.modules.configuration_resolver` as the deep seams. Public response and audit
snapshot projections also duplicate nearly the same loan-limit field mapping.

Corrective action: created `006D2-credit-assessment-deep-module-boundary` before 006E. It must
extract the source-named module interfaces, configuration resolver, focused module tests, and a
single snapshot projection without changing the reviewed behavior or destructively migrating data.

### Finding 5 - Pass - Financial/access tests have real assertions and useful failure coverage

006B covers each named blocker, pending nominee evidence, one-to-one rerun, no stage advancement,
and denied/invalid no-success-evidence paths. 006C/006D cover both lower-of-two branches,
below/equal/above limits, missing/ambiguous policy, cross-member facts, permission/object scope,
stored read immutability, complete old/new rerun audit, and preservation after four failed-rerun
classes. These are substantive behavior assertions, not coverage-only tests. The gaps above are
specific untested source mismatches rather than a generally weak suite.

### Finding 6 - Watch - Explicit reruns replace the current one-to-one snapshot

The standards pass flagged same-UUID rerun replacement against the design statement that historical
assessments do not change. The source data model also defines one assessment per application, and
006D explicitly requires an authorized successful rerun to replace the current snapshot with full
old/new audit while passive source/policy changes leave GET unchanged. No corrective slice was
created for that documented behavior. Future appraisal work must consume stored snapshots and must
not make recalculation an implicit read or review side effect.

Functional-spec spot check: no parent epic changed to `Complete` in this window. For the Epic 005
correction, M03-FR-003 remains incomplete until 005I3 supplies the public nominee selection; prior
assumptions own other documented intake deferrals. Epic 006 is still in progress: M04-FR-004-007
are implemented or queued for correction, while M04-FR-001-003 and M04-FR-008-011 remain assigned
to 006E-006G. No completed epic is falsely claiming full requirement-ID coverage.

## 2026-07-10 04:18 - Architecture Review 2026-07-10_041851_architecture_review

Reviewed completed product slices since the prior architecture review commit `353c6df`:
- `005G2-member-portal-session-and-audit-contract-hardening` (`210a353`)
- `005H-rejection-note-shell` (`d292f2c`)
- `005I-application-intake-frontend-wiring` (`261b170`)
- `006A-active-member-eligibility-service` (`71ef4cb`)

This review focused on the product diff, slice files, run evidence, working API contracts, Epic 005
and Epic 006 digests, and targeted implementation/test files. Broad `docs/source/` files were not
re-read because the needed source extracts were already distilled into the reviewed digests and slice
files.

### Finding 1 - Medium - Application Detail still contains mock-loan state that can override backend data

`005I` correctly removed direct `mockData.ts` imports from Application List, New Application, and
Application Detail and added staff API client tests. However, `ApplicationDetail.tsx` still contains
a frontend-only special case for `LO00000035` and hardcoded witness/sensitive nominee display data.
If a real backend application receives reference `LO00000035`, the UI can force
`Sanctioned · Documentation Pending`, `11 items pending`, Compliance/CS ownership, and blocked
documentation/SAP/disbursement stages regardless of the backend response
(`sfpcl-lms/src/pages/applications/ApplicationDetail.tsx:225-309`). The Witness tab still renders
synthetic people from `witnessData` (`ApplicationDetail.tsx:49-62`, `ApplicationDetail.tsx:915-940`).

This violates 005I's acceptance criterion that the intake surface runs on backend data and its
concrete requirement that Application Detail render real status, document checklist state,
deficiencies, and rejection-note state while preserving existing visual patterns. It is a product
correctness issue, not only cleanup: a live reference number can hit the old prototype branch.

Corrective action: created
`docs/slices/005I2-application-detail-api-state-hardening.md`, made `006B` depend on it, and added
the extract to the Epic 005 digest. The corrective slice must remove the `LO00000035` branch,
replace hardcoded witnesses/sensitive nominee values with API-backed or empty states, and add a
frontend regression proving an API-backed `LO00000035` does not receive mock overrides.

### Finding 2 - Low - Rejection-note state is created by 005H but not readable through Application Detail

`005H` added staff-only rejection-note create/send endpoints with meaningful permission, state,
audit, workflow, and no-side-effect tests. `005I` then asked the staff detail UI to show
rejection-note state as separate metadata when available. The current detail serializer returns the
application and register summary only (`sfpcl_credit/applications/services.py:1105-1139`), while
rejection-note metadata is serialized only in create/send responses
(`sfpcl_credit/applications/services.py:1233-1259`). The 005I review packet correctly notes this as
a known follow-up, but the queued work needs an explicit owner before appraisal/eligibility UI state
accumulates around the same detail page.

Corrective action: included in `005I2`. It should expose nullable, metadata-only `rejection_note`
summary on the staff application detail response and render it without changing
`application_status` or adding new visual patterns. Borrower portal application routes must not
receive staff rejection-note metadata.

### Finding 3 - Pass - Portal session and audit hardening closes the prior high-risk portal findings

`005G2` centralises session-bound portal authority in `validate_portal_session_authority(...)`.
Existing `/auth/me`, refresh, portal password change, portal own-data, and portal application routes
now reject already-issued sessions after the linked `PortalAccount` is no longer active, revoking
the session with `portal_account_status_changed`. The audit action names now match the source portal
contract for activation, login success/failure, password change, and portal application draft/save/
submit while staff routes keep internal `applications.loan_application.*` audit actions. Tests cover
suspended-session denial, source audit action names, staff-vs-portal audit separation, and sensitive
payload exclusions.

Corrective action: none.

### Finding 4 - Pass - Rejection-note and 006A eligibility backend tests assert real behavior

The reviewed backend tests are substantive rather than coverage padding. `005H` covers create/send,
permission denial, object-scope denial, portal-token denial, suspended-token rejection, invalid
states, duplicate create/send, metadata-only audit, and workflow events. `006A` covers the missing
endpoint red test, successful run/read, verified active-member pass, manual-evidence result, invalid
state, permission/object denial, no assessment/audit/workflow side effects on denied/invalid paths,
and one-to-one rerun behavior.

Corrective action: none.

### Finding 5 - Watch - Staff list/register object filtering is correct but not scalable

The new staff list and register APIs preserve object access by filtering the full matched queryset in
Python before pagination (`sfpcl_credit/applications/services.py:259-352`). This is safe for current
prototype-sized data and produces visible-row pagination, but it will not scale once the loan
application table grows. A later operational hardening slice should push object-scope predicates
into the queryset when assignment/team rules are more complete; no immediate corrective product
slice is required because the current implementation does not leak data and tests cover the visible
contract.

Functional-spec spot check: 005G2/005H/005I continue Epic 005 intake/portal/rejection-note
foundations. 006A starts Epic 006 by implementing M04 eligibility-assessment storage/API and only the
BR-004 through BR-007 active-member check, explicitly deferring default, document, terms, purpose,
and nominee checks to 006B. No reviewed slice claims to complete the full M04 appraisal or loan-limit
workflow.

## 2026-07-10 01:01 - Architecture Review 2026-07-10_005716_architecture_review

Reviewed completed product slices since the prior architecture review commit `49da479`:
- `005F2-deficiency-return-status-contract-hardening` (`1edc65a`)
- `005FA-member-portal-authentication` (`6c259f9`)
- `005FB-member-portal-dashboard-profile-and-supply-view` (`da34735`)
- `005G-member-portal-application-start-status` (`d1a12cf`)

This review focused on the product diff, run evidence, the Epic 005 digest, working API contracts,
and targeted source extracts for member-portal login/access, portal audit events, and M03 intake
requirements. Broad source documents were not re-read beyond the sections needed to verify the
findings below.

### Finding 1 - High - Suspended portal accounts can still expose portal claims through existing sessions

`005FA` correctly blocks a fresh login when `PortalAccount.can_authenticate()` is false, and
`005FB`/`005G` portal data routes require an active portal account through
`portal_member_for_user(...)`. The gap is the shared session/current-user path: `/auth/me` validates
only the underlying `UserSession` and `User.status`, then `current_user_payload(...)` adds
`member_id`, `portal_account_id`, `portal_role = borrower_member`, and portal own-data permissions
for any linked `portal_account` regardless of account status
(`sfpcl_credit/identity/modules/auth_service.py:138-240`). Access-token construction does the same
(`sfpcl_credit/identity/modules/tokens.py:69-73`), and portal password change checks only
`hasattr(user, "portal_account")` before allowing the action
(`sfpcl_credit/identity/modules/portal_auth_service.py:403-432`).

The source MP00 validation says inactive/suspended portal users are blocked
(`docs/source/screen-spec-member-portal.md:231-233`), and §14.1 says inactive or unauthorised portal
accounts are blocked (`docs/source/screen-spec-member-portal.md:1464-1469`). The reviewed tests
cover login denial indirectly through `PortalAccount.can_authenticate()`, but do not suspend an
account after login and prove the old access token loses `/auth/me`, password-change, and portal
own-data authority.

Corrective action: created
`docs/slices/005G2-member-portal-session-and-audit-contract-hardening.md`, made `005H` depend on it,
and added the session-status extract to the Epic 005 digest. The corrective slice should add
failing-first tests for an active portal session whose `PortalAccount.status` changes to
`suspended`, then centralise portal-session validity so old sessions are revoked or denied before
portal claims/actions are returned.

### Finding 2 - Medium - Portal audit rows use implementation action names instead of the source portal event contract

The portal implementation writes meaningful metadata-only audit rows, but the action names diverge
from the portal source table. Source §11 names `portal.login.success`, `portal.login.failed`,
`portal.account.activated`, `portal.application.draft_created`, `portal.application.saved`,
`portal.application.submitted`, and `portal.password.changed`
(`docs/source/screen-spec-member-portal.md:1408-1428`). The current code/tests instead assert
`portal.auth.activation.completed`, `portal.auth.login.succeeded`,
`portal.auth.password_changed`, and reused internal `applications.loan_application.created` /
`applications.loan_application.submitted` for borrower portal draft and submit
(`sfpcl_credit/identity/views.py:168-182`,
`sfpcl_credit/identity/modules/portal_auth_service.py:268-276`,
`sfpcl_credit/applications/services.py:241-318`,
`sfpcl_credit/tests/test_portal_member_api.py:375-381`).

Reusing the internal application service is the right architecture, but audit action codes are part
of the compliance/reporting contract. Without source-backed portal action names, later audit
explorer, notices, and borrower self-service reviews cannot distinguish "borrower acted in the
portal" from "staff acted through internal intake" without inferring from actor role.

Corrective action: included this in `005G2`. The slice should keep staff routes on existing
`applications.*` audit names, but let portal routes override or add source-backed portal audit
actions for activation, login, password change, draft create/save, and submit. Tests should assert
the source names and continue checking sensitive values, OTPs, token hashes, and raw document data
are absent from audit payloads.

### Finding 3 - Pass - Portal own-data object boundaries are carried through the reviewed slices

The reviewed portal own-data endpoints consistently derive authority from the active
`PortalAccount.member_id`, not client-supplied `member_id` values. `005FB` ignores query member IDs
for dashboard/profile/supply, `005G` rejects cross-member existing applications with
`403 OBJECT_ACCESS_DENIED`, and staff/non-portal tokens receive `403 PERMISSION_DENIED`. The tests
include own/cross-member assertions and no-side-effect checks for cross-member create/read attempts.

Corrective action: none beyond the session-status hardening in Finding 1.

### Finding 4 - Pass - Test quality and source sequencing are substantive

The reviewed runs include real red/green evidence and meaningful assertions: 005F2 covers
persisted/API/audit/workflow returned-incomplete status and repeat-return side effects; 005FA covers
activation, login claims, password-reset replay, session revocation, and password change; 005FB
covers member-scoped profile/dashboard/supply masking; 005G covers own create/update/submit/list,
cross-member denial, nullable reference numbers, and returned-incomplete portal status. Full gates
passed in all reviewed runs.

Corrective action: none.

Functional-spec spot check: M03-FR-001/M03-FR-002/M03-FR-008/M03-FR-009 are now partially
implemented for borrower portal initiation/save/submit and staff-created drafts; M03-FR-010 is
represented by submitted state and SFPCL pending owner but still needs task-inbox/assignment work;
M03-FR-011/M03-FR-012 were implemented by the previously reviewed completeness/deficiency slices
and preserved by 005F2/005G. M03-FR-003 through M03-FR-007 remain partially deferred for nominee,
signature, document upload, loan-limit, and full frontend intake wiring in queued slices and
assumptions.

## 2026-07-09 21:38 - Architecture Review 2026-07-09_213305_architecture_review

Reviewed completed product slices since the prior architecture review commit `1f30ed6`:
- `005C2-application-object-access-hardening` (`5f3dd0c`)
- `005D-application-document-checklist` (`ec33d63`)
- `005E-completeness-workbench` (`f282820`)
- `005F-deficiency-creation-and-resolution` (`39477f0`)

This review focused on the product diff, run evidence, the Epic 005 digest, working API contracts,
and targeted source extracts for application document, completeness, deficiency, and status rules.
Broad source documents were not re-read beyond the sections needed to verify the finding below.

### Finding 1 - Medium - Deficiency return hides the source-backed returned-incomplete application state

`005F` correctly creates structured deficiency rows from the current blocking completeness checklist,
keeps returned applications out of credit assessment, and proves no `LO...` reference, loan request
register row, or visible sequence is created. However, the return action keeps
`application_status = submitted` and only sets `completeness_status = incomplete`
(`sfpcl_credit/applications/services.py:651-660`; asserted in
`sfpcl_credit/tests/test_loan_applications_api.py:1040-1042`). That means downstream status
surfaces and portal slices can see a returned application as merely submitted unless they infer state
from deficiency rows or completeness status.

The source status model includes a dedicated `incomplete_returned` application status
(`docs/source/data-model.md:262-270`). The functional deficiency flow says the application enters
the incomplete state and keeps deficiency history (`docs/source/functional-spec.md:864-872`), and
S12 says returned applications become `Incomplete - Returned to Applicant` or rejected depending on
business decision (`docs/source/screen-spec.md:1217-1224`). 005F recorded A-040 for the
`items[].item_code` request shape, but did not record an assumption for replacing the
source-backed returned status with plain `submitted`.

Corrective action: created
`docs/slices/005F2-deficiency-return-status-contract-hardening.md`, made `005FA` depend on it, and
sharpened `005FA`/`005FB` plus the Epic 005 digest so portal auth/dashboard work builds on
`application_status = incomplete_returned`. The corrective slice should add failing-first backend
regressions for response/persisted status, audit/workflow old/new state, repeat-return handling, and
the existing no-reference/no-register/no-sequence side-effect guarantees.

### Finding 2 - Pass - Prior object-access finding was closed and carried forward

`005C2` integrates `applications.services.evaluate_application_object_access(...)` into detail,
patch, submit, and reference generation, with tests for unrelated same-permission denial and no
side effects. `005D`, `005E`, and `005F` reuse the same application boundary for document/checklist,
completeness, and deficiency endpoints, preserving the order `404` for missing records, then
`403 PERMISSION_DENIED` for missing global permission, then `403 OBJECT_ACCESS_DENIED` for
same-permission out-of-scope actors. This directly closes the prior architecture-review finding.

Corrective action: none.

### Finding 3 - Pass with evidence note - Tests assert behavior, but 005F TDD snippets are not self-contained

The reviewed backend tests are substantive: they assert permission/object-scope denials, metadata-only
audit payloads, version history, checklist blocking reasons, completeness pass delegation to the
existing reference-generation path, deficiency validation, deficiency resolve behavior, and no
partial sequence/register/audit/workflow side effects. Full gates passed in every reviewed run.

One evidence-quality gap remains: the 005F targeted TDD red/green files
(`tdd-red-return-with-deficiencies.log`, `tdd-green-return-with-deficiencies.log`, and
`deficiency-targeted-tests.log`) contain only startup lines, not the failure/pass result. The 005F
gate summary and full backend `-v 2` results are sufficient to verify the final state, but future
runs should save targeted red/green output with enough verbosity to be self-contained.

Corrective action: none for product code; noted in this review packet.

Functional-spec spot check: the reviewed Epic 005 work implements application object-access
hardening, application-document/checklist metadata, completeness read/pass, and deficiency
return/list/resolve. M03-FR-006, M03-FR-007, M03-FR-011, and M03-FR-012 are partially implemented
for the backend/API slices reviewed here; member portal intake/status, borrower deficiency
response/resubmission, rejection notes, eligibility, appraisal, sanction, disbursement, and frontend
intake wiring remain explicitly deferred in queued slices and assumptions.

## 2026-07-09 19:12 - Architecture Review 2026-07-09_190655_architecture_review

Reviewed completed product slices since the prior architecture review commit `dadeefd`:
- `004K2-borrower-360-bank-holder-contract-hardening` (`0b4018b`)
- `005A-loan-application-draft-create-update` (`6f07a17`)
- `005B-application-submit-and-status-transition` (`41da5a6`)
- `005C-reference-number-generation-and-loan-request-register` (`eb487da`)

This review focused on product diffs, run evidence, the Epic 004/005 digests, the working API
contract, and targeted source extracts for application object access. Broad source documents were
not re-read beyond the relevant permission and screen sections needed for the finding below.

### Finding 1 - Medium - Application detail/actions do not enforce object-level application scope

`005A`-`005C` correctly gate loan application create/read/update/submit/reference-generation by the
source permission codes, and the tests cover missing global permissions, state transitions,
metadata-only audit rows, masked bank data, and sequence/register behavior. However, the object
boundary is still global once a user has the permission. `loan_application_detail`,
`loan_application_submit`, and `loan_application_generate_reference` check only the global
permission helpers before loading and acting on any application ID
(`sfpcl_credit/applications/views.py:50-104`, `:107-142`, `:145-160`;
`sfpcl_credit/applications/services.py:74-90`). The reviewed tests create a separate reader user
and assert global read permission works, but they do not create a second field officer/credit user
with the same permission and prove an unrelated application is denied.

The source is explicit that application access is layered, not global CRUD: Field Officers are
scoped to created/assigned applications, Deputy Managers to the credit queue/assigned applications,
Credit Managers to the credit-assessment domain (`docs/source/auth-permissions.md:1480-1489`).
The endpoint map also marks `GET /loan-applications/{id}/` as
`applications.loan_application.read + object access` (`docs/source/auth-permissions.md:2347-2350`),
and the source test matrix says "Field Officer views unrelated application" should be denied
(`docs/source/auth-permissions.md:2522-2528`). Because `002I` already introduced
`identity.modules.object_permissions.evaluate_object_access`, this is a missed integration seam, not
a missing foundation.

Corrective action: created
`docs/slices/005C2-application-object-access-hardening.md`, inserted it before `005D`, and updated
`005D`/`005E` so document/checklist and completeness work build on the corrected application access
boundary. The corrective slice should add failing-first regressions for unrelated same-permission
users, apply the existing object-access helper to read/update/submit/reference/detail actions, and
record any remaining Credit Manager/global-scope assumption explicitly if the current schema lacks
queue/domain facts.

### Finding 2 - Pass - 004K2 closes the Borrower 360 bank-holder DTO mismatch

The corrective `004K2` slice changes the frontend bank-account contract from the local
`holder_name` alias to the backend/API `account_holder_name` field, updates the Borrower 360 render
path, and adds a regression fixture shaped like the real backend response. The test also preserves
masked-only account-number behavior and no bank reveal affordance.

Corrective action: none.

### Finding 3 - Pass - Loan application lifecycle tests assert meaningful behavior

The `005A`-`005C` tests assert standard envelopes, persisted state, audit/workflow rows, permission
denial, invalid-state responses, cross-member subresource rejection, no sensitive values in
responses/audits/register summaries, and first/second `LO...` sequence values. The red/green
evidence exists in each run folder under `evidence/terminal-logs/`, and final gates passed for
backend check/tests/migrations/coverage plus frontend lint/typecheck/tests/build.

Corrective action: none beyond the object-access hardening above.

Functional-spec spot check: the reviewed Epic 005 work implements draft persistence, submit, and
the successful completeness-pass reference/register transition only. Application documents,
checklist evaluation, deficiencies, eligibility, appraisal, sanction, disbursement, member portal
intake/status UI, and staff application UI wiring remain explicitly deferred in the queued 005D+
slices and assumptions.

## 2026-07-09 16:39 - Architecture Review 2026-07-09_163909_architecture_review

Reviewed completed product slices since the prior architecture review commit `fef0026`:
- `004H2-kyc-profile-duplicate-create-contract-hardening` (`1544e88`)
- `004I-sensitive-masking-and-reveal-audit` (`06d8655`)
- `004J-bank-account-and-cancelled-cheque-profile-foundation` (`127bf9d`)
- `004K-borrower-360-kyc-panel-and-masking-ui-wiring` (`9327696`)

This review focused on product diffs, run evidence, the Epic 004 digest, and the working API
contract. Broad source documents were not re-read because the digest covered the reviewed
requirements.

### Finding 1 - Medium - Borrower 360 drops the bank-account holder name returned by the API

`004J` serializes member bank-account responses with `account_holder_name`
(`sfpcl_credit/members/services.py:749-755`), and the working API contract records the same response
field (`docs/working/API_CONTRACTS.md:255-259`). `004K` then introduced a frontend
`MemberBankAccountDetail` shape with `holder_name` (`sfpcl-lms/src/services/memberProfileApi.ts:189-191`)
and normalizes only `item?.holder_name` (`sfpcl-lms/src/services/memberProfileApi.ts:655-658`).
Borrower 360 renders that normalized field in the Bank & Security card
(`sfpcl-lms/src/pages/members/Borrower360.tsx:451-456`), so a real 004J backend response will render
the holder as blank even though the API returned it.

The test missed this because its bank-account fixture uses the frontend-only `holder_name` shape and
asserts masking/endpoint behavior but not holder-name contract fidelity
(`sfpcl-lms/src/pages/members/Borrower360.test.tsx:37-70` and `:253-256`). This is user-visible
data loss on the Epic 004 Borrower 360 screen and a DTO drift between the backend contract and
frontend client.

Corrective action: created
`docs/slices/004K2-borrower-360-bank-holder-contract-hardening.md` and made `005A` depend on it.
The corrective slice must add a failing-first frontend regression using `account_holder_name`,
update the frontend DTO/normalizer/rendering to consume that canonical field, and keep bank account
numbers masked-only with no reveal control.

### Finding 2 - Pass - 004H2 closes the prior KYC duplicate-create issue

The corrective `004H2` slice adds a public API regression for duplicate member-party KYC profile
creates, returns a standard `400 VALIDATION_ERROR` with `field_errors.party_id`, leaves exactly one
profile and one `kyc.profile.created` audit row, and preserves the 004H read/update/document
behavior. The red/green evidence demonstrates the test failed against the database constraint shape
first and passed after the service-level validation was added.

Corrective action: none.

### Finding 3 - Pass - Sensitive reveal and bank metadata keep sensitive values bounded

`004I` keeps member profile reads masked, requires `members.member.read` plus the exact PAN/Aadhaar
field permission, returns full values only in the immediate no-store reveal response, and writes
metadata-only success/denial audit rows without workflow events. `004J` stores bank account numbers
as protected token/hash/last-four values, exposes only `{masked,last4,can_view_full:false}`, tests
permission separation under A-034, and keeps duplicate-bank, signature-mismatch, disbursement, and
bank reveal behavior deferred.

Corrective action: none.

Functional-spec spot check: the reviewed Epic 004 work still implements member-master foundations
and staff UI visibility rather than a complete lending module ID set. Loan application persistence,
submit/reference generation, completeness, deficiencies, eligibility, appraisal, sanction,
disbursement, repayment, communication history, risk/exception, and audit timeline data remain
explicitly deferred to Epic 005 and later slices.

## 2026-07-09 14:18 - Architecture Review 2026-07-09_141049_architecture_review

Reviewed completed product slices since the prior architecture review commit `7c97efc`:
- `004D2-member-profile-and-nominee-contract-hardening` (`187096b`)
- `004F-shareholding-and-share-certificate-records` (`38b575f`)
- `004G-landholding-and-crop-plan-records` (`75ad4b5`)
- `004H-kyc-upload-and-verification` (`bac6359`)

This review focused on product diffs plus the run evidence and Epic 004 digest/source extracts.

### Finding 1 - Medium - Duplicate KYC profile creates can fall through to an unhandled database error

`004H` correctly added a unique database constraint for one `kyc_profiles` row per member party
(`sfpcl_credit/members/models.py:412-416`), and the Epic 004 digest says one profile is allowed per
member party (`docs/working/digests/epic-004-member-kyc-master.md:228-230`). However,
`create_kyc_profile()` always calls `KycProfile.objects.create(...)` after confirming the member
exists (`sfpcl_credit/members/services.py:586-613`) and does not check whether a profile already
exists or catch the uniqueness failure. The API test covers first create/read/update and validation
for auth, party type, missing member, and missing consent (`sfpcl_credit/tests/test_member_kyc_api.py:37-114`),
but it does not exercise a second create for the same member. The likely user-visible behavior is a
500-style server error instead of the standard `VALIDATION_ERROR` envelope expected across this API.

Corrective action: created
`docs/slices/004H2-kyc-profile-duplicate-create-contract-hardening.md` and made `004I` depend on it.
The corrective slice must add a failing-first duplicate-create regression, return a standard
validation envelope before the database constraint raises, and prove no second profile/audit row is
created.

### Finding 2 - Pass - Prior architecture-review findings were closed cleanly

`004D2` removes nominee identity hashes/encrypted-token keys from nominee create audit metadata and
adds explicit tests that the audit payload excludes the submitted identifiers, hash keys, and hash
values while preserving protected storage for duplicate/search support. It also neutralizes member
profile `available_actions[]` to `[]`, so member/KYC/default status no longer invents
loan-application eligibility before 005A and later eligibility slices own that behavior. This
matches the prior corrective slice scope.

Corrective action: none.

### Finding 3 - Pass - Shareholding and land/crop foundations stay within their documented boundaries

`004F` implements only shareholding list/create and defers share certificates/PATCH/update.
Tests cover permission separation, count validation, available-share derivation, create audit
metadata, member share-summary refresh, and no workflow event. `004G` implements only land-holding
and crop-plan list/create, records A-032 for the source permission gap, tests positive-acreage and
UUID validation, and avoids loan-limit, application-blocker, and purpose-eligibility decisions.
Frontend tests for both tabs assert backend-backed loading/empty/error/validation/success states
using existing Member Profile patterns rather than restoring mock rows.

Corrective action: none.

### Finding 4 - Pass with queue sharpening - Bank-account work needed concrete source boundaries

`004I` was already sharpened for member PAN/Aadhaar reveal, but `004J` still had generic placeholder
scope. This review opened only the targeted bank-account source sections and sharpened `004J` with
bank account, cancelled cheque, encrypted-account-number, masking, audit, and disbursement/mismatch
deferral requirements. The extracted requirements were added to the Epic 004 digest so the next
agent does not need to re-read broad source files.

Corrective action: sharpened `docs/slices/004J-bank-account-and-cancelled-cheque-profile-foundation.md`
and updated `docs/working/digests/epic-004-member-kyc-master.md`.

Functional-spec spot check: the reviewed Epic 004 work still implements foundations rather than a
complete functional module ID set. Member shareholding, land/crop, and member-party KYC records are
implemented with explicit deferrals for share certificates, witness validation, sensitive reveal,
bank-account foundations, KYC completeness/disbursement blockers, and loan application intake.

## 2026-07-09 11:48 - Architecture Review 2026-07-09_114836_architecture_review

Reviewed completed product slices since the prior architecture review commit `e370720`:
- `004A-member-directory-api-and-ui` (`caa3d36`)
- `004B-member-profile-api-and-ui` (`8bcf160`, repaired by `2026-07-08_094146_repair`)
- `004C-individual-farmer-and-fpc-profile-details` (`79f2b77`)
- `004D-nominee-validation-and-ui` (`56d89dd`)

Also noted intervening automation/docs commits in the diff window, but this review focused on the
four product slices counted by Ralph state.

### Finding 1 - Medium - Nominee create audit stores sensitive identity hashes despite the contract

`004D` correctly masks nominee PAN/Aadhaar in API responses and tests that plaintext values are not
stored in the create audit. However, `create_nominee()` still writes `pan_hash` and `aadhaar_hash`
into `AuditLog.new_value_json` (`sfpcl_credit/members/services.py:213-223`). The local contract says
responses and audit logs must not include `pan_encrypted`, `aadhaar_encrypted`, `pan_hash`, or
`aadhaar_hash` fields for nominee create (`docs/working/API_CONTRACTS.md:230-235`), and the source
audit rule says sensitive data values should not be stored in audit logs while masked values or
metadata are acceptable (`docs/source/auth-permissions.md` §30.3). The current test only asserts the
raw PAN/Aadhaar strings are absent (`sfpcl_credit/tests/test_member_nominees_api.py:189-206`), so it
misses hashed identifiers that are still linkable sensitive metadata.

Corrective action: created
`docs/slices/004D2-member-profile-and-nominee-contract-hardening.md`. It must add a failing-first
audit regression that forbids identity hash keys/values in nominee audit metadata, remove those
fields from the audit payload, and keep responses masked.

### Finding 2 - Medium - Member profile `available_actions[]` invents loan-start eligibility

`004B` was scoped to masked read-only profile detail and explicitly said not to implement loan
application start or invent eligibility, KYC approval, active-member, default, or loan-application
business rules (`docs/slices/004B-member-profile-api-and-ui.md:56-59` and `:87-90`). The
implementation nevertheless enables `create_loan_application` only when the user has
`applications.loan_application.create` and the member is active, KYC verified, and not in default
(`sfpcl_credit/members/services.py:459-476`). Source §13.3 shows `available_actions[]` as part of
the member-detail shape, and §44 allows detail endpoints to return action availability, but the
actual workflow gates belong to later application/eligibility slices. This hard-codes a business
decision before the loan-application endpoint and eligibility service exist, and the test locks in
the happy path (`sfpcl_credit/tests/test_member_profile_api.py:163-165`) rather than proving the
action is neutral/deferred.

Corrective action: same `004D2` slice. It must remove or neutralize the profile action until the
loan-application slice owns the endpoint and source-backed gate, with tests proving member
KYC/default status alone no longer decides action availability in the profile read service.

### Finding 3 - Pass - Directory/profile UI wiring removed mock fallback without visual drift

`004A` and `004B` removed the backend-wired Member Directory/Profile dependency on `mockData`,
added API clients, and tested loading, success, empty, auth/permission, and error states. The tests
assert mock-only fields and rows are absent from the wired paths, and the generated visual HTML uses
existing table/card/tab/empty/alert classes. The old `Borrower360` prototype still imports mock data
and contains the synthetic `Sudha Patil` nominee, but it is outside the reviewed backend-wired
Member Profile path and remains future scope.

Corrective action: none.

### Finding 4 - Pass with queue sharpening - 004E still must not implement witness records early

The Epic 004 digest/source extracts already warn that witnesses belong to loan applications and must
resolve to real shareholder/shareholding facts. `004E` was sharpened again to depend on the new
contract-hardening slice and to stop/reorder rather than create a member-level witness endpoint if
loan application and shareholding prerequisites are still absent.

Corrective action: `004D2` inserted before `004E`; `004E` dependency sharpened.

## 2026-07-07 21:08 - Architecture Review 2026-07-07_210824_architecture_review

Reviewed commits since the prior architecture review (`e26ed12`):
- `003IA2-notification-mark-read-stale-write-hardening` (`a1734ce`)
- `003J-background-job-scheduling-foundation` (`cdf1e71`)
- `003K-prototype-visual-gap-report-update` (`c0e93e5`)
- `003L-data-import-and-migration-planning` (`51f4b18`)

Also reviewed in-range planning commit `dded5c4` (`docs(re-planning): add Task Inbox slices
012EA/012EB to close S03 ownership gap`) because it changed the queue and Epic 003/012 ownership
notes between reviewed slice commits.

### Finding 1 - Low - Notification stale-write regression carries a now-unused mock hook

`003IA2` fixes the prior Medium finding in the production path: `mark_notification_read()` now
validates `read_state_version`, refetches and locks the current-user scoped notification inside one
transaction, then saves read state and writes the audit row in that same atomic block
(`sfpcl_credit/communications/services.py:356-390`). The red/green evidence is real: the new
persisted stale-version regression fails on the previous implementation and passes after the row-lock
change. However, the test still patches `_notification_queryset_for_user()` with a
`_StaleNotificationQuerySet` even though the fixed implementation now calls
`_locked_notification_queryset_for_user()` instead (`sfpcl_credit/tests/test_notifications_api.py:233-283`).
That mock was useful for the failing pre-fix code path but is no longer exercising anything in the
green implementation. The assertions still prove persisted stale writes return `409` and do not
create a second audit row, so this is a test clarity issue rather than a product defect.

Corrective action: no standalone corrective slice. The next notification-touching slice should
remove the dead mock/helper or replace it with a clearer persistence-focused regression; no
production behavior change is required.

### Finding 2 - Pass - Scheduler foundation stays inside the intended module boundary

`003J` adds a dedicated `sfpcl_credit.scheduler` app and `scheduled_jobs` metadata table, with
idempotent enqueue and legal queued/running/succeeded/failed transitions in
`sfpcl_credit/scheduler/services.py`. The tests assert duplicate idempotency keys reuse an existing
job, invalid transitions raise `ValidationError`, and scheduler enqueue does not generate
notifications or `communications.notification.marked_read` audit rows
(`sfpcl_credit/tests/test_scheduler_services.py:16-107`). The implementation does not add a public
API, Celery/Redis dependency, worker, dashboard task generation, notification generation,
communication-send coupling, reminder business rules, or report generation. A-027 records the
source-silent metadata-shell assumption.

Corrective action: none.

### Finding 3 - Pass - Prototype gap and import planning docs preserve source boundaries

`003K` correctly records the current UI/API status: Dashboard, Notifications Center, and My Profile
are API-backed; Task Inbox, `AuditTimeline`, and `DocumentPackModal` remain prototype/mock; and
`scheduled_jobs` is internal metadata, not a frontend task queue or scheduler UI. `003L` adds
`DATA_IMPORT_MIGRATION_PLAN.md` as a planning-only artifact and explicitly avoids staging tables,
commands, APIs, workers, UI, scheduled jobs, real source data, or business schema changes. It
separates implemented foundation tables from future target areas and records A-028 so import
execution cannot borrow communication, dashboard, notification, document-download, or report-export
permissions.

Corrective action: none.

### Finding 4 - Pass with queue sharpening - Task Inbox ownership and Epic 004 handoff are clearer

The in-range planning commit `dded5c4` closes a real ownership gap by adding `012EA`/`012EB` as the
deferred Task Inbox/S03 implementation path and cross-referencing that Epic 003 delivered only the
dashboard shell, not task generation. This review also sharpened `004A-member-directory-api-and-ui`
and `004B-member-profile-api-and-ui` with no-mock frontend regression requirements and screenshot
evidence expectations, using the Epic 004 digest extracts already opened in the prior run. Functional
requirement spot check: no new full functional module was completed in this review window; scheduler,
visual inventory, and migration planning are foundation/planning work, and notification read-state
hardening preserves the existing S04 staff-inbox contract.

Corrective action: no corrective slice or ADR needed.

## 2026-07-06 18:42 - Architecture Review 2026-07-06_183803_architecture_review

Reviewed commits since the prior architecture review (`8ea30ec`):
- `003G2-dashboard-internal-auditor-access-regression` (`8bd2b69`)
- `003H-dashboard-task-ui-wiring` (`2cbb4c9`)
- `003I-notification-adapter-shell` (`21e4f1a`)
- `003IA-notifications-center-ui-wiring` (`4dd909d`)

### Finding 1 - Medium - Notification mark-read stale-write protection is not atomic

`003IA` documents the mark-read contract as optimistic concurrency: clients submit
`read_state_version`; mismatches return `409 STALE_WRITE`; a successful mark-read increments the
version and writes one audit row (`docs/working/API_CONTRACTS.md:643-661`). The implementation
checks the version on an unlocked model instance before entering the transaction that saves the read
state (`sfpcl_credit/communications/services.py:356-372`). Two concurrent requests carrying the
same version can both pass the check before either save, then both save/audit as successful updates.
The current backend test proves an obviously stale version returns `409`, but it does not prove
same-version retries or races cannot duplicate the success/audit path
(`sfpcl_credit/tests/test_notifications_api.py:197-228`). This weakens the S04 read/unread audit
trail just as later scheduler/reminder slices may create more notification traffic.

Corrective action: created
`docs/slices/003IA2-notification-mark-read-stale-write-hardening.md` and made `003J` depend on it.
The corrective slice must add a failing-first same-version retry/concurrency regression and enforce
the version check atomically using either row locking or a conditional update scoped to the current
recipient.

### Finding 2 - Pass - Dashboard and communication/notification slices preserve source boundaries

`003G2` closes the previous internal-auditor dashboard finding with a seeded-role regression and a
catalogue invariant. `003H` removes mock dashboard summaries, keeps `/api/v1/dashboard/` separate
from notifications, and tests success, empty task, role-context, `401`/`403`, server, and network
states without substituting mock data. `003I` implements source §24.2 communication metadata and
§39.2-§39.3 send/list shells with real validation, metadata-only audit assertions, no provider
delivery, and explicit M16 deferrals. `003IA` correctly adds a notification-specific inbox rather
than overloading generic communication history, scopes list/mark-read by direct user, active role,
and active team, and keeps dashboard tasks separate.

Corrective action: none beyond Finding 1.

### Finding 3 - Pass with queue sharpening - Epic 003 source traceability remains explicit

The reviewed run packets contain concrete red/green logs and full gate evidence. Functional-spec
spot check: the dashboard work implements only the §12.2-§12.6 zero-count role-context shell and
defers real metrics/tasks; `003I` supports template snapshot creation and delivery-status storage
while deferring real email/SMS/courier/phone delivery, manual call logging, borrower/member portal
notifications, and downstream event generation; `003IA` supports staff S04 current-user inbox state
only and records A-026 for notification permissions and role/team generation gaps. This review
created the corrective `003IA2` slice and sharpened `003J` so scheduler work stays in its own module
boundary and does not expand `communications.services` or generate dashboard tasks/notification rows
inside the scheduler shell.

Corrective action: sharpened `003J-background-job-scheduling-foundation`; no ADR needed.

## 2026-07-05 20:32 - Architecture Review 2026-07-05_202735_architecture_review

Reviewed commits since the prior architecture review (`94c437e`):
- `003D-secure-document-download-with-audit` (`4a3779f`)
- `003E-versioned-configuration-shell` (`ccd41d4`)
- `003F-communication-template-shell` (`117d2ff`)
- `003G-dashboard-task-summary-api` (`05147c6`)

### Finding 1 - Medium - Internal Auditor is mapped to a dashboard context but cannot pass the dashboard permission gate

`003G` documents A-023 as mapping Internal Auditor to the compliance dashboard context, and the
service code includes `"internal_auditor": "compliance"` in the role-context map
(`sfpcl_credit/dashboard/services.py:8-18`). The endpoint also requires `management_readonly`, but
the catalogue seed does not grant that permission to `internal_auditor`
(`sfpcl_credit/identity/catalogue.py:441-451`). The catalogue regression that checks dashboard
roles omits `internal_auditor` as well (`sfpcl_credit/tests/test_catalogue_seed.py:163-179`). The
result is a role that the documented contract says should get a compliance dashboard shell, but a
seeded Internal Auditor receives `403 PERMISSION_DENIED` before the mapping is reachable. This will
surface immediately when `003H` wires the frontend dashboard to the API.

Corrective action: created `docs/slices/003G2-dashboard-internal-auditor-access-regression.md` and
made `003H-dashboard-task-ui-wiring` depend on it. The corrective slice must add a failing-first
seeded-role regression and either grant `management_readonly` to `internal_auditor` or remove that
role from the documented dashboard mapping and A-023.

### Finding 2 - Pass - 003D closes the shared-auth duplication finding while preserving protected-view envelopes

`003D` extracts the repeated session-bound bearer parsing into
`sfpcl_credit.identity.modules.http_auth` and migrates admin, audit, workflow, document, tracer, and
`/auth/me` call sites to the shared helper. The focused document/auth tests assert missing,
malformed, and revoked bearer behavior across the migrated protected views, so the refactor
materially closes the prior architecture-review finding without changing the standard `401`
envelopes. The new download endpoint stays within the 003D scope: it returns the documented
descriptor shape, gates on `documents.file.download`, writes exactly one success audit row, and
avoids storage-key/checksum/raw-byte leakage.

Corrective action: none.

### Finding 3 - Pass - 003E and 003F are source-traced shells with real validation and side-effect assertions

`003E` implements `loan_policy_configs`, `version_histories`, loan-policy list/create/patch/activate,
and filtered version-history reads with tests for required source fields, approval-evidence blocking
for M01-FR-015, active-policy retirement per A-021, audit rows, permission denials, invalid UUIDs,
and deferred M01-FR-003 through M01-FR-014 calculations. `003F` implements the
`content_templates` metadata shell with tests for metadata-only responses, variables persistence,
date/status/duplicate-code validation, no rendered merge output, audit rows, and the A-022
permission assumption. These are behavior assertions, not coverage padding, and the review packets
trace the relevant source IDs.

Corrective action: none.

### Finding 4 - Pass with queue sharpening - Dashboard shell is intentionally zero-count; notification adapter slice is now concrete

Aside from Finding 1, `003G` correctly avoids inventing downstream dashboard calculations: no model
or migration was added, all supported card shells return zero counts, `tasks: []`, unknown query
parameters return `400 VALIDATION_ERROR`, and read access writes no audit row. The tests cover the
five role contexts, the standard envelope, `401`/`403`, and no sensitive borrower/member/loan-account
values in the shell. This review sharpened `003I-notification-adapter-shell` from targeted source
extracts for `communications` (§39.2-39.3, data-model §24.2, M16-FR-001 through M16-FR-007, and S04)
so the next communication slice does not confuse dashboard task summaries with notification
persistence.

Functional-spec spot check: no full functional module is complete yet. `003E` explicitly implements
the shell portions of M01-FR-001, M01-FR-002, and M01-FR-015 while deferring M01-FR-003 through
M01-FR-014. `003F` implements the template-storage part of M16-FR-004 and M18-FR-006 while deferring
delivery, delivery-status, phone-call, and borrower/loan communication-history requirements to
003I and later slices. `003G` supports the §12.2-§12.6 dashboard shell only; no business metrics are
claimed complete.

Corrective action: no additional defect slice beyond `003G2`; sharpened `003I`.

## 2026-07-05 09:22 - Architecture Review 2026-07-05_091741_architecture_review

Reviewed commits since the prior architecture review (`559b1b7`):
- `002K2-demo-tracer-permission-isolation` (`13fcbc4`)
- `003A-audit-log-foundation` (`da589a1`)
- `003B-workflow-event-foundation` (`a641466`)
- `003C-document-metadata-and-storage-adapter` (`20b902b`)

### Finding 1 - Medium - Protected backend views keep copying the same bearer-session parser

The reviewed product behavior is correct, but the HTTP auth boundary is drifting. `003A`,
`003B`, and `003C` each added a thin protected view with a local `_authenticate_session()`
implementation that repeats the same header parsing, `AUTH_REQUIRED`, `INVALID_TOKEN`, and
`auth_service.validate_access_session()` logic (`sfpcl_credit/identity/audit_views.py:18`,
`sfpcl_credit/workflows/event_views.py:10`, `sfpcl_credit/documents/views.py:10`). The same
pattern already exists in `admin_views`, `tracer/views.py`, and `identity/views.py`, so the next
protected endpoint would make six or seven places to keep in sync. This has not produced a
response-contract defect yet, and tests cover the 401 cases, but it is exactly the duplication
003B warned about before adding another protected read view.

Corrective action: sharpened `docs/slices/003D-secure-document-download-with-audit.md` to extract
one shared session-bound Bearer helper before adding the download endpoint, migrate existing thin
views to it where the helper shape fits, and add regression coverage proving the standard 401
envelopes stay unchanged.

### Finding 2 - Pass - 002K2 closes the demo tracer permission leak with behavior tests

`seed_demo_users` now creates a local/dev-only `local_demo_tracer_user` role for
`demo.tracer@sfpcl.example`, grants that role exactly `tracer.lifecycle.run`, and deletes stale
tracer grants from every other role. The regression test creates a non-demo `sales_team_user`,
seeds stale tracer authority, reruns the guarded demo seed, logs in through real `/auth/login/`,
and proves `/auth/me/` returns `permissions: []` and `available_actions: []` for that non-demo
Sales user. This directly closes the prior review finding and preserves A-007/A-011.

Corrective action: none.

### Finding 3 - Pass - 003A and 003B match the audit/workflow source contracts and use real assertions

`003A` exposes the existing `identity.AuditLog` through `GET /api/v1/audit-logs/` without adding
a second audit table, maps `old_value_json`/`new_value_json` to source contract names, serializes
system rows as `actor: null`, rejects unknown filters, and proves the read endpoint does not write
new audit rows. `003B` reconciles the tracer-owned `workflow_events` table through state-only
migrations, moves canonical ownership to `sfpcl_credit.workflows`, preserves tracer
`workflow_event_id` responses, and adds the protected workflow-event read endpoint. The tests
assert item fields, ordering, filters, invalid UUIDs, permission denials, clean migration, and
tracer lifecycle regression behavior rather than relying on coverage numbers alone.

Corrective action: none beyond Finding 1's shared-auth cleanup.

### Finding 4 - Pass with queue sharpening - 003C delivers the generic upload foundation; 003D/003E are sharper

`003C` keeps the slice generic: one `document_files` migration, local storage bytes outside the
database, SHA-256 checksum, `documents.file.upload` permission gate, validation for required
multipart fields and source sensitivity values, and one `documents.file.uploaded` audit row without
raw bytes. The tests also verify 401/403 paths create no document or upload-audit rows. No frontend
code changed. This review added source extracts for document download permission/audit and
functional-spec policy configuration IDs to `docs/working/digests/epic-003-audit-documents-config.md`,
then sharpened `003D` and `003E` accordingly.

Functional-spec spot check: no full functional epic was completed in this review window. The 002K2
RBAC correction supports M18-FR-001; the 003A-C foundation work supports later document/audit/config
modules but does not complete M01/M06/M17/M18 requirements by itself. `003E` now explicitly traces
M01-FR-001, M01-FR-002, and M01-FR-015 and requires deferral of M01-FR-003 through M01-FR-014 rather
than invented policy calculations.

Corrective action: no new corrective slice; sharpened `003D` and `003E`.

## 2026-07-04 19:03 - Architecture Review 2026-07-04_190302_architecture_review

Reviewed commits since the prior architecture review (`7908071`):
- `002G2-admin-user-action-permission-granularity` (`62f0ea9`)
- `002I-object-level-permission-test-harness` (`383ec74`)
- `002J-api-contract-test-harness` (`71087c2`)
- `002K-seed-data-and-demo-users` (`7707942`)

### Finding 1 - Medium - Demo tracer seeding grants the tracer permission to the shared Sales role

`002K` correctly guards predictable demo credentials behind `SFPCL_DEBUG=true` and `SFPCL_ALLOW_DEMO_SEED=true`, uses the real `/auth/login/` and `/auth/me/` path, and keeps the zero-permission demo user neutral. The permission isolation for the tracer demo user is weaker than the slice implies, though: `seed_demo_users` defines `demo.tracer@sfpcl.example` with role `sales_team_user`, then `_ensure_tracer_permission()` creates/updates `tracer.lifecycle.run` and attaches it to the shared `sales_team_user` role (`sfpcl_credit/identity/management/commands/seed_demo_users.py:52`, `:112-122`). Because `/auth/me/` derives permissions from primary-role `RolePermission` rows, every local user with `sales_team_user` becomes tracer-capable after the demo seed runs. A-007 says `sales_team_user` has no source-defined grants, and A-011 says the tracer permission is a dev/test smoke exception. The current tests assert the demo tracer user has exactly the tracer permission, but they do not create a non-demo Sales user and prove that user remains neutral after seeding.

Corrective action: created `docs/slices/002K2-demo-tracer-permission-isolation.md`. It must keep the guarded local/demo behavior but isolate tracer authority to the intended demo user/role path, with a failing-first regression proving a non-demo `sales_team_user` still gets `permissions: []` after seeding.

### Finding 2 - Pass - 002G2 closes the prior admin permission boundary finding

The reviewed diff replaces the broad `has_manage_users_permission()` check with action-specific backend gates. Tests cover create-only, update-only, disable-only, and read-only partial roles, plus negative side effects: forbidden writes produce `403 PERMISSION_DENIED` without audit rows or session revocation. A-015 clearly documents the read fallback needed because the seeded `system_admin` role has write user-admin grants but not `users.user.read`.

Corrective action: none.

### Finding 3 - Pass - 002I and 002J add narrow test infrastructure without production coupling

`002I` adds a pure `evaluate_object_access(...)` helper that takes explicit actor/object facts, does not query future domain models, and returns typed allow/deny reasons including `scope_unknown` with `approval_required=True`. `002J` adds test-only API contract assertions under `sfpcl_credit/tests/` and regression coverage for existing auth/admin/tracer endpoints. Red/green logs exist in both run folders and the final full backend/frontend gates are green.

Corrective action: none.

### Finding 4 - Pass with queue sharpening - 003A/003B are ready to start after the corrective slice

The next Epic 003 slices were already sharpened from the digest. This review added current-schema details: `003A` must serialize nullable `AuditLog.actor_user` rows as `actor: null`, and `003B` must preserve tracer `workflow_event_id` response behavior while reconciling the existing tracer-owned `workflow_events` table.

Corrective action: no additional defect slice beyond `002K2`; `003A` and `003B` were sharpened.

## 2026-07-04 13:52 - Architecture Review 2026-07-04_135247_architecture_review

Reviewed commits since the prior architecture review (`0939e01`):
- `002EYA-e2e-baseline-and-seed-safety` (`e8a166f`) plus operator baseline commit `9c4e97b`
- `002F2-navigation-render-regression-tests` (`17a85e6`)
- `002G-admin-user-and-role-management-shell` (`dd223ea`)
- `002H-state-machine-and-transition-guard-foundation` (`fd020d9`)

### Finding 1 - Medium - Admin user-management collapses distinct source permissions into one backend authority

`002G` added useful user-management endpoints and tests, but the backend gate in `sfpcl_credit/identity/modules/admin_users.py` grants full list/detail/role/team/status authority when the actor has any one of `users.user.create`, `users.user.update`, or `users.user.disable`. The source catalogue defines these as separate risk-rated permissions (`auth-permissions.md` §12.1), with `users.user.disable` marked Critical, and the route map names `users.user.read` for `/settings/users`. Current seeded `system_admin` has all three write permissions, so today's happy path works, but a future role with only create or update would be able to suspend users and revoke sessions. The tests do not include partial-permission roles, so this drift would not be caught.

Corrective action: created `docs/slices/002G2-admin-user-action-permission-granularity.md` and made `002I`/`002J` depend on it. 002G2 must enforce action-specific backend permissions while preserving current `system_admin` access and the last-admin lock-out guard.

### Finding 2 - Low - The new Admin Users screen has functional tests but no visual screenshot evidence

`002G` added a frontend page under the existing app shell and the implementation reuses the current table/card/status patterns. The run packet records that the in-app browser target was unavailable, so no screenshots were captured for the new screen's loading, list/detail, validation, or unauthorized states. This is an evidence gap rather than a found visual defect, but it matters because `FRONTEND_DESIGN_RULES.md` makes screenshot evidence binding for frontend changes.

Corrective action: no standalone product slice. If 002G2 changes frontend action visibility, it must save visual evidence for the Admin Users page; otherwise the next browser-capable operator review should capture this screen.

### Finding 3 - Pass - Prior E2E/evidence corrective slices materially closed the earlier review gaps

`002EYA` now has six committed Playwright PNG baselines, a config-level fail-fast when `E2E_DJANGO_PYTHON` is unset, and `seed_e2e_users` refuses unless both `SFPCL_DEBUG=true` and `SFPCL_ALLOW_E2E_SEED=true` are present. The reviewed run folders now contain the claimed nested `evidence/terminal-logs/` paths, including red/green targeted logs. The operator baseline commit says normal `npm run e2e` passed twice in comparison mode on a browser-capable machine; the agent sandbox still records the expected local `EPERM` server-start limitation.

Corrective action: none.

### Finding 4 - Pass - 002F2 and 002H deepen shared boundaries without production drift

`002F2` moved Sidebar visibility through `visibleStaffNavItems()` and covers zero-permission, unknown-role, tracer-only, admin-user, and per-item route-guard cases without adding frontend test dependencies or styling changes. `002H` introduced a small domain-neutral `workflows.guard` module and migrated tracer transitions by passing explicit actor permissions; tests cover allowed transitions, unknown action, invalid state, missing permission, no-op rejection, and tracer API preservation of `403 PERMISSION_DENIED` / `409 INVALID_STATE_TRANSITION` with audit/workflow-event counts.

Corrective action: none beyond 002G2.

## 2026-07-04 08:51 - Architecture Review 2026-07-04_085117_architecture_review

Reviewed commits since the prior architecture review (`ba78859`):
- `002EY-e2e-and-visual-regression-harness` (`0cb56c3`)
- `002F-role-aware-sidebar-header-navigation` (`84ba391`)
- `002FL-frontend-lint-baseline` (`cc0c134`)

### Finding 1 - Medium - The Playwright harness is authored, but the visual-regression contract is still incomplete

`002EY` required committed visual baselines and a local `npm run e2e` proof for login, dashboard, tracer closed state, invalid login, missing/revoked auth, and zero-permission dashboard. The diff adds Playwright specs with `toHaveScreenshot()`, but `sfpcl-lms/e2e/` contains no `*-snapshots/` directories or PNG baselines, and `.ralph/runs/2026-07-04_072505_normal_run/review-packet.md` says first baseline generation is still an operator step. That means a clean `npm run e2e` will not yet satisfy the slice's own acceptance criteria; it still needs `--update-snapshots` on a browser-capable machine before it can be a real regression gate.

Corrective action: created `docs/slices/002EYA-e2e-baseline-and-seed-safety.md` to generate and commit baselines, prove `npm run e2e` passes without update mode, and save real E2E evidence.

### Finding 2 - Medium - The deterministic E2E seed command can create known-password users without an explicit E2E guard

`sfpcl_credit/identity/management/commands/seed_e2e_users.py` creates active login users with the known password `E2eTracer123!` and a tracer-only role/permission. This is appropriate for the isolated Playwright database, and A-011/A-013 document the dev-only intent, but the management command itself has no runtime guard: if run against the wrong database, it will insert active known-password accounts. The Playwright config points `SFPCL_DB_PATH` at an E2E sqlite file, which reduces normal risk, but the command should still refuse outside explicit local/E2E setup.

Corrective action: `002EYA` now requires a `seed_e2e_users` guard plus tests proving the command refuses without an explicit E2E flag and succeeds only in local/E2E mode.

### Finding 3 - Medium - The 002F navigation tests do not prove the actual Sidebar hiding behavior

The implementation is directionally good: `PAGE_PERMISSIONS` lives in `navigationPermissions.ts`, `App.tsx` uses `resolveNavigationAttempt()`, and `Sidebar` filters `allNavItems` through `can(requiredPermission)`. The test named "hides every protected sidebar item when the user lacks its required permission", however, does not render `Sidebar` or call the filtering path. It builds a set of every other permission and asserts that the current permission is absent from that set. If `Sidebar` later stopped filtering by permission, that test would still pass. Given this is the staff-shell permission boundary, the coverage needs to exercise behavior, not just the exported table.

Corrective action: created `docs/slices/002F2-navigation-render-regression-tests.md` to add render-level or shared-helper coverage for Sidebar visibility and guarded navigation, including tracer-only, zero-permission, unknown-role, and future admin-management cases.

### Finding 4 - Medium - Run packets repeatedly reference red/green evidence paths that are absent

The reviewed run packets and progress entries for `002EY`, `002F`, and `002FL` refer to logs under `.ralph/runs/<run-id>/evidence/terminal-logs/`, but the committed run folders contain only root-level gate result files; no `evidence/terminal-logs/` directories exist for those three runs. The final root gate logs are useful and green, but the missing red/green paths weaken auditability, especially for frontend permission and E2E infrastructure work. This repeats the evidence-path issue found in the 2026-07-03 architecture review.

Corrective action: `002EYA` and `002F2` explicitly require evidence paths that exist in the final artifacts. Owner/operator should also inspect why claimed nested evidence directories are not surviving into committed run folders; agents cannot edit protected Ralph scripts during a run.

### Finding 5 - Low - The lint baseline packet overstates its recorded evidence

`002FL` correctly adds `npm run lint`, pinned ESLint packages, and a flat config. However, `.ralph/runs/2026-07-04_082747_repair/lint-results.md` says lint was skipped because `.ralph/config.yaml` still has `quality_gates.lint: false`, and the claimed `evidence/terminal-logs/lint-final.log` path is absent. Its review packet also says rule downgrades are documented in `final-summary.md`, but that file is only the generic success template; the useful justification lives in `risk-assessment.md`. This is an audit packet defect, not a product-code defect.

Corrective action: no separate product slice. This review packet records the limitation, and `HANDOFF.md` keeps the owner/operator action to flip the protected lint gate once validation confirms it.

### Finding 6 - Pass - The core 002F and 002FL implementation shapes are reasonable

The route-guard extraction in `002F` removes duplicated page-permission data from `App.tsx`, keeps `tracer.lifecycle.run` isolated to `run_tracer`, and preserves the neutral `backend_staff` role path from 002E2. `002FL` uses approved pinned lint dependencies and avoided visual, label, layout, and permission-table changes while fixing lint-safe issues. Current review-run gates passed after these commits.

Corrective action: none beyond Findings 3-5.

## 2026-07-04 07:13 - Architecture Review 2026-07-04_071340_architecture_review

Reviewed commits since the prior architecture review (`ced57b0`):
- `002E2-frontend-role-bridge-hardening` (`9a9d3bb`)
- `002EX-early-end-to-end-tracer-bullet` (`027b5b0`)

### Finding 1 - Medium - The tracer app squats on the canonical `workflow_events` table that slice 003B must own

`002EX` was scoped to MINIMAL skeleton models (Member, LoanApplication, LoanAccount, Repayment) plus an audit event per transition. The domain models are correctly namespaced under `tracer_*` table names, so they will never collide with the real member/application/finance tables that slices 004x/005x/009x/010x own. However, the tracer also added an *extra* model, `WorkflowEvent`, and gave it the global table name `db_table = "workflow_events"` (`sfpcl_credit/tracer/models.py`, migration `sfpcl_credit/tracer/migrations/0001_initial.py`). That is the canonical table that the still-`Not Started` slice `003B-workflow-event-foundation` is meant to own, and `docs/working/API_CONTRACTS.md` even cites `data-model.md §26.1-26.2` for it. When 003B lands, it will either try to `CreateModel` a second `workflow_events` table (migration fails at migrate time with "table already exists") or be silently forced to inherit the tracer's ad-hoc shape instead of the source `data-model.md §26` schema. This is architecture drift: a deliberately throwaway dev tracer (the tracer route is dev-only and A-011 says the tracer permission must be removed before production) has grabbed a permanent, canonical foundation table name.

Corrective action: sharpened `docs/slices/003B-workflow-event-foundation.md` to (1) treat the tracer `workflow_events` table as pre-existing drift that must be reconciled in the same slice — either relocate the canonical `WorkflowEvent` model into 003B's owning app and repoint `sfpcl_credit/tracer/services.py`, or rename the tracer copy to `tracer_workflow_events` — with no table-name collision at migrate time; and (2) base the real schema on `data-model.md §26` rather than the tracer's minimal fields.

### Finding 2 - Low - Dead ternary in the tracer frontend API client

`sfpcl-lms/src/services/tracerApi.ts` builds the "Sanction" display row with `status: disbursement ? 'recorded' : 'pending'`. `disbursement` is the resolved `ActionResponse` object returned by `tracerRequest`, which either returns a truthy object or throws — so the ternary is always `'recorded'` and the `'pending'` branch is unreachable. It is cosmetic (a display label on a dev-only screen) and did not affect gates, but `DECISION_POLICY.md §2` forbids dead code without an owning slice.

Corrective action: added a cleanup item to `docs/slices/002EY-e2e-and-visual-regression-harness.md` (which already owns the tracer UI and will render this row) to replace the always-true ternary with the actual sanction status from the sanction response.

### Finding 3 - Pass - 002E2 removed the unsafe `auditor` fallback cleanly and with real edge-case tests

`002E2` closed the Medium finding from `2026-07-03_224536`: `mapBackendUserToFrontendUser()` now falls back to a new neutral `backend_staff` role instead of `auditor`, unmapped backend role codes (`it_head`, `management_viewer`, `nominee`, `bank_user`, `subsidiary_user`, `external_auditor`) map to `backend_staff` with zero prototype permissions, and the `Dashboard` default card branch, the exceptions/tasks/applications lists, the alerts banner, and the profile-menu Settings item were all audited so a neutral backend role sees a "No workspaces available" state rather than inheriting auditor/admin/credit-manager widgets. Tests assert `backend_staff` mapping, retention of `roleName`/`roleCodes`/`teamName`, empty permission mapping, and that the role is explicitly *not* `auditor`/`admin`/`borrower`. Good behaviour-oriented coverage.

Corrective action: none.

### Finding 4 - Pass - 002EX backend proves the plumbing with strong, behaviour-oriented tests

The tracer service layer keeps transitions behind `select_for_update` + `transaction.atomic`, enforces an inline status guard (`_require_status`), writes one `audit_logs` row and one `workflow_events` row per transition, and requires the explicit `tracer.lifecycle.run` permission through the session-bound `/auth/me/` validation path. `test_tracer_api.py` asserts the full persisted lifecycle (7 workflow events, 7 tracer audit rows), out-of-order rejection at multiple points (account-before-sanction, repeated sanction, repayment-before-disburse, close-before-repayment) returning `409 INVALID_STATE_TRANSITION`, positive-amount validation, unauthenticated `401 AUTH_REQUIRED`, revoked-token `401 INVALID_TOKEN`, and permission-denied `403 PERMISSION_DENIED` — each verifying no domain/audit rows were written on rejection. These are real regression tests, not coverage padding.

Corrective action: none (see Finding 1 for the one drift issue).

### Finding 5 - Pass with known gap - 002EX frontend regressions are mapping-level, not render-level

The 002EX slice lists three "Frontend regression" cases (a `backend_staff`/empty-permission session cannot see or run the tracer, and unmapped roles do not inherit auditor behaviour). These are asserted at the mapping/service layer in `authSession.test.ts` (e.g. `mapCanonicalPermissions(['tracer.lifecycle.run']) === ['run_tracer']`, zero-permission roles map to `[]`), but there is no component/render test that mounts the Sidebar/App/TracerBullet to prove the Tracer nav item is hidden and the Run button is disabled. This is the same class of gap the prior review flagged for 002E, and it is already owned: `002EY` items 11, 14, 15 and its test cases now require a real Playwright browser assertion for a zero-permission role not exposing tracer navigation/actions and for clicking through the tracer to the closed state, and `002F` test cases require permission-gated nav coverage including `tracer.lifecycle.run -> run_tracer`.

Corrective action: none beyond confirming 002EY/002F already own it.



Reviewed commits since the prior architecture review:
- `002D3-current-user-contract-fidelity` (`c225f90`)
- `002E-protected-frontend-route-shell` (`f732df7`)

### Finding 1 - Medium - The frontend auth bridge maps unmapped backend roles to auditor behavior

`002E` correctly moved staff login to backend `/auth/login/` + `/auth/me/`, hides the demo role switcher by default, and maps canonical backend permissions to existing route checks. However, `mapBackendUserToFrontendUser()` falls back to `role: 'auditor'` when a backend role has no prototype mapping. The source role catalogue includes backend roles such as `it_head` and `management_viewer` that are not mapped in 002E, and A-007 intentionally leaves some roles with no seeded permissions until the source grants are clarified. Because many shell pages still branch directly on `currentUser.role`, an unmapped backend role can inherit auditor-shaped dashboard/profile content even though permission-gated navigation is blocked. That is architecture drift from R1-AC-004 role-aware UI and from the 002E rule that unknown permissions must not invent grants.

Corrective action: created `docs/slices/002E2-frontend-role-bridge-hardening.md` before 002EX. 002E2 must replace the `auditor` fallback with a neutral/no-affordance path, add explicit tests for `it_head` and `management_viewer`, and audit shell-level role branches.

### Finding 2 - Low - 002E visual evidence is a harness, not screenshots

The 002E slice required screenshots for login, loading/current-user fetch, authenticated dashboard, invalid login, and unauthorized/permission-blocked navigation. The run recorded that local Django/Vite servers could not bind sockets and Chrome exited before screenshots were written, so it saved HTML harness pages instead. That is understandable in this sandbox and the functional gates passed, but it means visual fidelity was not independently captured as image evidence for a frontend auth-shell change.

Corrective action: sharpened `docs/slices/002EY-e2e-and-visual-regression-harness.md` to explicitly close this gap with real Playwright screenshots/baselines for the 002E states plus tracer state.

### Finding 3 - Pass - 002D3 closed the prior `/auth/me/` contract gap cleanly

`002D3` enriched `/api/v1/auth/me/` with `mobile_number`, `roles[{role_code, role_name}]`, and `teams[{team_code, team_name}]`, while preserving session-bound access validation, active-user enforcement, compatibility fields, sorted permissions, and thin-view service boundaries. The API/module tests assert the new shape, inactive-role behavior, team sorting, and compatibility-code derivation.

Corrective action: none.

### Finding 4 - Pass with test gap - 002E has meaningful service tests, but no React integration test yet

The frontend auth-session tests assert credential post, token storage, `/auth/me/` fetch, invalid-login rejection, expired-token clearing, logout request body, role/team object-derived display state, and unknown canonical permissions granting no prototype permission. The remaining gap is that these tests exercise the service/mapping layer rather than rendering `App`/`LoginScreen` through the full login-to-dashboard flow. 002EY should cover that in a real browser before the visual/e2e gate is promoted.

Corrective action: sharpened `002EY` browser requirements; no additional product-code slice beyond 002E2 is needed from this item.

## 2026-07-03 21:37 - Architecture Review 2026-07-03_213704_architecture_review

Reviewed commits since the prior architecture review:
- `002D-current-user-api-with-permissions-and-teams` (`52b18da`)
- `002D2-backend-dev-infrastructure` (`13f7dcb`)
- Non-product Ralph workflow fixes also present in the diff window: `d758336`, `96a0d02`

### Finding 1 - Medium - `/auth/me/` is secure and well tested, but its success shape is narrower than the source contract

`002D` correctly added session-bound access validation: missing/expired/wrong-type/revoked/inactive-user cases are covered, the view delegates to `auth_service`, and the response uses the shared envelope. The source contract, however, shows current-user data with `mobile_number`, `roles[{role_code, role_name}]`, and `teams[{team_code, team_name}]` (`docs/source/api-contracts.md` §11.4). The implementation and examples expose only `role_codes` and `team_codes`, plus no `mobile_number`. That is workable for the immediate dashboard shell, but it would make 002E build frontend session state on a reduced contract instead of the documented profile/relationship shape.

Corrective action: created `docs/slices/002D3-current-user-contract-fidelity.md` and sharpened `002E` to depend on it. 002D3 must enrich `/auth/me/` while preserving the 002D security behavior and compatibility fields.

### Finding 2 - Pass - 002D2 removed the test-infrastructure drift and the installed gates now pass

The previous architecture review found repeated manual `schema_editor.create_model` setup in backend tests. `002D2` moved auth/catalogue tests onto Django's migrated test database through `IdentityTestCase`, added a static guardrail against reintroducing the manual setup, configured persistent dev SQLite, env-driven settings, and restricted CORS for `http://localhost:5173`. The committed run artifacts show backend check, tests (50/50), migration check, coverage (96%, floor 85), frontend tests, typecheck, and build passing after the orchestrator installed pinned dependencies.

Corrective action: none.

### Finding 3 - Pass - Test quality is behavior-oriented, not coverage-only

The reviewed tests assert real security and contract behavior: `/auth/me` success data, envelope meta, missing bearer token, expired access token, refresh-token misuse, revoked sessions after logout, suspended-user revocation, sorted permissions, zero-link roles, CORS headers, environment parsing, migration-backed test setup, and shared-envelope delegation. These are meaningful regression tests for the slice risks.

Corrective action: none.

## 2026-07-03 17:04 - Architecture Review 2026-07-03_170432_architecture_review

Reviewed slices / commits since the prior architecture review:
- `002C-role-and-permission-catalogue-seed` (`9b9154d`)
- `002C2-standard-api-envelope-and-auth-service-boundary` (`160c356`)
- Non-slice Ralph workflow fix also present in the diff window: `e373f71`

### Finding 1 - Medium - Prior run packets reference red/green evidence paths that are absent

The `002C` and `002C2` review packets both claim red/green TDD evidence under `evidence/terminal-logs/`, but those directories are not present in the committed run artifacts for `.ralph/runs/2026-07-03_113738_normal_run/` or `.ralph/runs/2026-07-03_115501_normal_run/`. The root gate logs are present and show green backend/frontend validation, but the Ralph workflow requires TDD red/green evidence to be saved before completion. This weakens auditability for high-risk RBAC/auth work even though the final gates passed.

Corrective action: sharpened `docs/slices/002D-current-user-api-with-permissions-and-teams.md` so the next high-risk auth slice must save failing-first `/auth/me/` output, green backend gates, frontend gates, and API response examples at paths that exist in the final review packet.

### Finding 2 - Medium - Backend tests duplicate manual schema setup instead of relying on one test base

`test_auth_api.py`, `test_auth_module.py`, `test_api_envelope.py`, and `test_catalogue_seed.py` repeat `django.setup()`, `schema_editor.create_model()`, and manual table deletion helpers. The new 002C/002C2 tests have real behavior assertions, but this repeated test infrastructure is architecture drift: it can diverge from migrations and makes each new backend test file copy setup code instead of using Django's migrated test database or a shared test base.

Corrective action: sharpened `docs/slices/002D2-backend-dev-infrastructure.md` to remove duplicated per-file schema creation and move backend tests to a shared `TestCase`/fixture pattern while preserving the existing behavior assertions.

### Finding 3 - Medium - Worktree validation still falls back to the wrong backend interpreter

During this architecture-review run, `scripts/ralph-validate.sh` looked for `.ralph/venv/bin/python` inside the active worktree, did not find it, and fell back to bare `python3`. That violates the run prompt's backend-interpreter rule and failed with an architecture-mismatched `_cffi_backend` import. Manual backend gates passed when run with the required repo-level interpreter `/Users/amitkallapa/Loan Management System Development/.ralph/venv/bin/python`.

Corrective action: recorded in this review packet and run summary for owner/orchestrator repair. Agents must not edit protected `scripts/` during Ralph runs.

### Finding 4 - Pass - 002C and 002C2 production behavior matches the reviewed source requirements

The role/permission seed transcribes the §12 permission catalogue and records §15 gaps instead of inventing grants (A-007). The shared API helper now supplies `meta.api_version` and both health/auth endpoints delegate to it. Auth token/session/audit behavior moved behind `identity.modules.auth_service` and `identity.modules.tokens`, with direct module tests for refresh rotation, replay rejection, logout revocation, inactive users, and audit events. No additional corrective product-code slice is needed from this review.

## 2026-07-03 08:15 - Architecture Review 2026-07-03_081509_architecture_review

Reviewed slices:
- `001-ralph-bootstrap-verification` (state recorded; no matching slice commit found in this staging history)
- `002A-backend-scaffold-and-health-endpoint` (`766dfd6`)
- `002B-user-model-and-jwt-login-refresh-logout` (`ef0810b`)
- `002B2-auth-hardening-jwt-library-and-packaging` (`7b873d4`)

### Finding 1 - Medium - API response envelope is duplicated and already drifting

`sfpcl_credit/ops.py` defines a health-only `success_response` whose `meta` contains `request_id` and `timestamp` only. `sfpcl_credit/identity/views.py` defines a separate auth `success_response` whose `meta` also contains `api_version: "v1"`. The source API contract's standard success envelope includes `api_version` in `meta` (`docs/source/api-contracts.md` §6.1), and the working contract says 002A health endpoints return the standard envelope. This means health and auth responses already disagree before the second auth endpoint family lands.

Corrective slice created: `docs/slices/002C2-standard-api-envelope-and-auth-service-boundary.md`.

### Finding 2 - Medium - Auth view owns multi-entity workflow and audit logic

`sfpcl_credit/identity/views.py` currently owns token encoding/decoding, claim construction, refresh-session lookup, refresh rotation, logout revocation, response formatting, and audit-log creation. That was acceptable to get the first auth slice through, but it conflicts with the architecture guidance that views translate HTTP and call module interfaces, while multi-entity operations and audit logging live in explicit modules (`docs/source/technical-architecture.md` §13.1 and `docs/source/codebase-design.md` §6-7). If 002D adds `/api/v1/auth/me/` on top of this shape, auth behavior will become harder to test through a stable module interface and easier to duplicate.

Corrective slice created: `docs/slices/002C2-standard-api-envelope-and-auth-service-boundary.md`.

### Finding 3 - Low - Test coverage is behavior-oriented, but one contract gap is now visible

The reviewed tests use real Django client calls, assert rotation/replay/logout behavior, audit creation, inactive-user rejection, PyJWT wrong-secret rejection, expired-token rejection, and environment-secret loading. That is stronger than coverage-only testing. The visible gap is contract coverage for a single shared envelope: health tests and auth tests validate their local response shapes separately, which allowed the `api_version` drift above.

Corrective slice created: `docs/slices/002C2-standard-api-envelope-and-auth-service-boundary.md`.
