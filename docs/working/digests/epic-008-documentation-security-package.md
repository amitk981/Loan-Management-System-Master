# Epic 008 Digest: Documentation, Legal Documents, and Security Package

Page-cited extraction of both SOP PDFs so 008A-008M implementation sessions do not re-search
whole PDFs (PRODUCTION_COMPLETION_BLUEPRINT.md §4.5 Stage A; Checkpoint 3). Prepared 2026-07-11.

Sources:
- `docs/source/Final SOP - Loan Disbursement V10 (1).pdf` — cited below as **V10 p.N** (33 pages;
  Stage 4 documentation is pp. 13-18; compliance tables pp. 23-28; annexure index p. 29;
  compliance matrix pp. 30-31)
- `docs/source/SFPCL_Loan Sanction- Doc & Disbursement-SOP_WhatsLoan-25052026.pdf` — cited as
  **Deck p.N** (12-page board deck; Stage 4 list p. 7, checklist signatures p. 8, statutory
  framework p. 10, top-10 errors p. 11)
- `docs/source/api-contracts.md` §26-§28, `docs/source/data-model.md` §16,
  `docs/source/functional-spec.md` §11.6 M06, `docs/source/auth-permissions.md` §12.7/§16.4
  remain the API/model/permission authority; this digest carries the SOP business facts only.

## 008H SH-4 Physical Security Closure (2026-07-14)

The retained `security_instruments` package now refreshes physical/demat applicability only from the
canonical frozen sanction mode and owns one protected SH-4 row under the same package lock. Compliance
prepares current pending/signed facts; a distinct active Company Secretary records terminal custody
only from the exact sanctioned borrower, verified shareholder witness, active physical shareholding,
current-renderer SH-4, non-legacy borrower/witness signatures, and adequate non-legacy maker/checker
stamp. Share count is nullable/positive/bounded but never reserved. Invocation/return remain null and
blocked. Package/checklist reads project metadata only; PoA, checklist completion/approval, file
access, package status, and readiness remain unchanged. Exact replay is zero-write, terminal custody
freezes consumed legal evidence behind one §6.3 action, and twice-run PostgreSQL create/custody races
retain one current row with attributable winner and zero loser success evidence.

## Architecture Review 2026-07-14 19:20 - Current Maker and Security Ownership

- 008D2/008E2 close their original adverse-authority, canonical-identity, nondisclosure, action,
  and race gaps, but a second actor can materially change pending stamp/notary/signature facts while
  the row retains the first maker id, then check their own change through another active role.
  `008G2` makes current material maker attribution honest, restores transport/domain and §6-§7
  contracts, freezes consumed tri-party signatures, and runs the missing public/PostgreSQL proof.
- 008F creates real package/PoA rows and projections, but the source-defined security tables and
  workflow are owned by `legal_documents`; mutable approved status alone creates a package, and
  Compliance can downgrade an active PoA to draft. `008F2` establishes the security-instruments
  owner, consumes canonical terminal sanction truth, and makes exact-draft activation terminal and
  evidence-bound before SH-4/CDSL extend the module.
- Independent regressions received HTTP 200 for fake-status package creation, active-PoA downgrade,
  and post-verification borrower-signature rewrite. 008G retained no PostgreSQL execution because
  its sole race was skipped and it declared no capability; its positive document was manually
  provenance-labelled rather than publicly generated.
- M06-FR-007/008/009 remain partial until F2/G2. M06-FR-016/017 retain substantive E2 identity and
  resolution behavior but remain current-maker partial until G2. No later checklist/readiness or
  full Term Sheet claim changes.

## 008F2 Security Boundary and Terminal PoA Closure (2026-07-14)

`security_instruments` owns the retained package/PoA tables and §28 routes through a state-only
transfer. Canonical latest-cycle sanction plus Stage-4 scope gates package truth. Compliance owns
draft/current-maker facts; a distinct active Company Secretary terminally activates the exact draft
and freezes renderer/file/checksum, stamp/notary/signature maker-checkers, PoA maker/checker, and
request context behind one durable §6.3 action. Consumed legal evidence cannot change. Public
generation and both PostgreSQL races passed twice. Pre-008F2 active rows remain honest legacy,
readable terminal evidence without invented action/snapshot; SH-4/CDSL/readiness stays A-110 pending.

## 008G2 Stage-4 Maker and Verification Contract Closure (2026-07-14)

Every pending stamp/notary/signature material edit now transfers current maker identity and retains
the prior maker in immutable old/new evidence; replay remains zero-write. New positive/adverse
stamp/notary and resolved-signature rows are database-constrained to distinct non-null maker/checker
ids. Migration marks only historical null-maker rows as legacy and leaves them ineligible for
change/new truth. Thin HTTP adapters check authority before strict request parsing; domain modules
depend on lower request contracts, not HTTP serializers. §26.6 returns the retained §6.3 action
identity, unresolved overwrite returns `SIGNATURE_MISMATCH_UNRESOLVED`, and verified tri-party
evidence freezes/guards exact consumed signature ids, names, makers, and times. The positive tracer
crosses genuine public DOCX/PDF generation; exact and changed five-worker PostgreSQL races passed
twice. F2/H sharpening consumes these precise seams.

## 008G Tri-party Verification Closure (2026-07-14)

The §26.6 action now verifies only a current-renderer `tri_party_agreement` when the approval-owned
frozen subsidiary route is complete/true and the exact document retains canonical maker-attributed
`signed` borrower and selected-nominee rows with no mismatch. Only a distinct Company Secretary may
verify. Exact replay is zero-write; corrected remarks retain complete old/new evidence. Existing
loan-document/checklist reads project metadata only and preserve every checklist, package, security,
file, repayment, and readiness fact. A-111 records why the API remark is retained on the document.

## 008F Power of Attorney Closure (2026-07-14)

The §28 security package is now one locked, protected parent per sanctioned application with PoA
always required and later-instrument flags/readiness honestly pending under A-110. One current PoA
retains canonical borrower, nominee, active Company Secretary attorney, explicit share-sale-on-
default authority, current renderer document, exact maker/checker stamp/notary, execution/effective
facts, and immutable Compliance preparer/Company Secretary verifier history. Activation consumes
locked legal-owner selectors and exact 008E2 frozen signature rows; mutable later names, resolved
mismatches, and A-108/A-109 null-maker history cannot supply execution. Checklist projection remains
metadata-only and never completes, approves, invokes, releases, downloads, or makes ready.

008H run-ahead is now concrete from §28.4/§17.3 and V10 §4.5: physical-only SH-4 binds the sanctioned
borrower, verified shareholder witness, active physical shareholding, current generated form, exact
borrower/witness signatures, adequate maker/checker stamp, and Company Secretary custody. It must
reuse the 008F package lock/serializer, reject invoked/returned states, preserve PoA/readiness truth,
and leave mixed/missing share mode blocked.

## 008D2 Verification Authority Closure (2026-07-14)

Compliance now owns only pending stamp/notary preparation, while Company Secretary owns every
positive or adverse verification outcome (`adequate`/`insufficient`, `completed`/`rejected`). New
verification requires a retained Compliance preparer with a different immutable user id; role
changes cannot collapse maker/checker identity. Exact maker/checker replay remains zero-write,
checker corrections retain both identities and full old/new ledgers, and preparers cannot downgrade
or replace verified evidence. Legacy rows with no truthful maker remain nullable history under
A-108 and cannot be changed without real preparation.

The documents app now exposes only a generic exact immutable-upload-provenance fact. Legal category,
Stage-4 role, same-application, and notary-purpose decisions live in `legal_documents`; metadata
never grants download. §26.9-§26.10 shape parsing uses a legal HTTP serializer seam while raw direct
module callers cross the same strict parser and business rules. The five-checker changed-outcome
PostgreSQL race passed twice with one current row and six attributable ledger entries.

## 008E2 Signature Identity and Lifecycle Closure (2026-07-14)

New captures resolve borrower, selected nominee, application witness, and active user ids/names from
their canonical owners, then freeze the canonical snapshot and immutable Compliance maker. Exact
replay uses retained facts after mutable display-name changes. Unresolved mismatches are capture-
immutable; only a distinct Company Secretary may resolve them, with one durable §6.3 workflow action
identity. Authorized unknown, wrong-stage, unrelated, and non-current signature ids share 404 while
missing action authority remains 403 before owner queries. Capture/checklist consumers use one
legal-owned application signature selector. A-109 keeps pre-attribution rows honestly nullable and
ineligible for changed capture or new resolution. Both five-worker PostgreSQL races passed twice.

## Architecture Review 2026-07-14 16:10 - Verification and Signature Authority

- 008B4's immutable renderer contract/file/checksum provenance and legacy exclusion are substantive.
  008C2's mandatory terminal coordinator, completion-preserving applicability/linkage lifecycle,
  owner facts, central read scope, audit attribution, and genuine final-sanction race are substantive.
- 008D has real locked replay/change/history/projection behavior and a genuine PostgreSQL race, but
  only positive `adequate`/`completed` states require Company Secretary authority. Compliance can
  record the checker-owned adverse `insufficient`/`rejected` outcomes or downgrade verification.
  `008D2` closes positive/adverse authority, maker-checker identity, and legal evidence ownership.
- 008E's evidence types, atomic Bank Verification Letter projection, and resolved-row immutability
  are substantive. An unresolved mismatch can nevertheless be overwritten by ordinary capture for
  the same signer; resolution queries leak absent-versus-inaccessible identity, party UUID/name
  snapshots are not canonical-owner validated, and the declared concurrency case has no race test.
  `008E2` closes those lifecycle/identity/nondisclosure/race gaps and the §6.3 action contract.
- M06-FR-001 is substantive. M06-FR-016/017 remain partial through 008E2; stamp/notary tracking
  advances M06-FR-008/015 but execution remains with PoA/agreement owners. M06-FR-013 and the full
  real M05 path remain A-101 configuration-blocked; A-107 remains the signed-copy evidence limit.

## Architecture Review 2026-07-14 12:50 - Renderer Provenance and Checklist Lifecycle

- 008B2's legal owner, direct authority, selector, retained-table transfer, nullable-only loan link,
  and PostgreSQL evidence are substantive. 008B3 genuinely validates every new DOCX/PDF, but
  retained pre-008B3 rows have no renderer-contract provenance and are returned by replay/checklist
  selectors before rendering. `008B4` makes legacy output explicit and aligns unknown-parent errors.
- 008C atomically creates the initial ordered checklist through the HTTP final-approval path, but
  the underlying approval writer still permits a terminal decision without the optional callback.
  Its PostgreSQL test races refresh after approval rather than final sanction completion.
- Checklist refresh recomputes completion state, calls the members ORM directly for cheque facts,
  treats pending false mismatch flags as verified matches, duplicates role authority, and drops
  request/role/team audit context. `008C2` closes those lifecycle, dependency, authority, fact, audit,
  and true final-sanction race gaps before 008D.
- M06-FR-001 remains partial until 008C2; M06-FR-013 remains A-101 configuration-blocked and is also
  legacy-provenance partial until 008B4. The initial applicability index is not later execution,
  verification, stamping, notarisation, security, approval, or disbursement readiness.

## 008D Stamp Duty and Notarisation Closure (2026-07-14)

The §26.9-§26.10 POST routes now retain one current stamp/notary row per current-renderer legal
document under a loan-document row lock. Exact replay is zero-write; every real create/change keeps
attributable audit, version, and workflow facts. Compliance may prepare pending records while only
Company Secretary authority may claim adequate/completed verification. Completed notarisation
evidence must have singular exact legal-upload provenance for the same application; metadata never
grants download. Loan-document and checklist reads project status only and preserve all checklist
completion/signature/approval facts. No ₹500/ad-valorem rule was encoded. The genuine five-worker
PostgreSQL changed-submission race passed twice with one current row and a complete six-entry ledger
(seed plus five changes).

## 008B4 Renderer Provenance Closure (2026-07-14)

Every new renderer success now freezes the versioned legal renderer contract, exact generated-file
identity, and post-validation stored SHA-256 as one all-or-none immutable provenance group. Current
truth requires that group to match the retained `DocumentFile`; flags, names, MIME types, prefixes,
and extensions never suffice. Pre-008B4 and mismatched rows remain honest `legacy_unverified`
history: list metadata labels them, replay conflicts without writes, and checklist selectors exclude
them. No automatic remediation/overwrite authority was invented under A-106. Compliance Team
callers with the route permission receive §7.5 404 for an absent parent, while missing-permission and
unrelated roles remain nondisclosing 403. Auth §15.4 is the source for Compliance Team access to
approved documentation applications. A-101 remains unchanged because provenance proves renderer
output only, not governed completeness of the real Term Sheet path.

## 008C Checklist Applicability Closure (2026-07-14)

Approved sanction finalisation now calls the legal checklist owner through a top-level transaction
coordinator/callback: approval rows, sanction/register evidence, checklist, items, audit, and workflow
either commit together or all roll back, without an `approvals -> legal_documents` import. New
approval review packages freeze the selected shareholding mode; existing/missing or repository
`mixed` modes remain explicit SH-4/CDSL blockers under A-105. Frozen active-member subsidiary flags
and application-linked cancelled-cheque mismatch flags are the only conditional authorities.

The §27.1 GET is metadata-only and preserves the pre-sanction 005D response on the shared route under
A-104. Generated-document ids come only from the legal selector and never confer completion or file
access. Checklist loan/signature ids remain database-null until 009C/008K install real protected FKs.
The declared five-worker PostgreSQL race passed twice with one checklist, eleven unique ordered items,
one creation audit, and no false applicability-change evidence.

## 008C2 Checklist Lifecycle and Authority Closure (2026-07-14)

The public approval writer can no longer accept a caller-supplied completion callback. Direct
terminal approval fails zero-write; the private top-level sanction-completion seam binds the legal
checklist in the same transaction. Canonical latest-cycle frozen terminal facts replace the cached
coherence flag, and the genuine five-worker final-sanction race passes twice with one decision, one
checklist, eleven items, and one creation ledger.

Refresh now owns only applicability and current-provenance linkage. It preserves checklist status,
signature facts, item completion/verifier/time/remarks, and creation-time label/order; a completed-
evidence applicability reversal conflicts atomically. Applicability and linkage have disjoint audit
snapshots/actions and full request/network/role/team attribution. Cancelled-cheque mismatch truth
comes through an application-owned seam: only unanimous verified boolean rows are authoritative;
missing, pending, malformed, or conflicting facts remain visibly blocked. Complete exact subsidiary
flags are likewise required. One approval-owned read resolver now handles permission, A-104 routing,
absent-parent disclosure, and sanctioned application/case scope before any checklist/item query.

## 008B2 Boundary Closure (2026-07-14)

`legal_documents` now owns the retained `loan_documents` model/table, authoritative generation
module, HTTP adapters, and application-scoped collection selector. `documents` retains only file,
template, provenance, and storage responsibilities. Direct and HTTP callers cross the same active-
actor/generate-or-read/template-reference/application-scope checks. Until 009C supplies the real
loan aggregate, A-102 database-constrains `loan_account_id` to `NULL` rather than accepting an
unconstrained UUID or the synthetic tracer model.

## 008B3 Renderer Closure (2026-07-14)

Legal generation now accepts only bounded genuine OPC/DOCX packages, resolves declared
placeholders across ordinary Word runs and legal content parts, preserves retained package parts,
and rejects missing, duplicate, undeclared, malformed, oversized, compressed-pathological, or
unreadable content before storage. PDF rendering is an in-process local adapter using pinned
ReportLab with a Unicode TrueType font and pinned pypdf structural/content reopening; no network
conversion service is permitted. Repair validation confirmed that shaped Unicode requires pypdf's
layout extraction and token-level host-font fallback for complete glyph coverage (including `₹`);
missing coverage fails before storage. A-103 records the conservative byte/entry/text/placeholder/page
limits and deployment font requirement. Rendering proves generated content only and never implies
execution, stamping, notarisation, checklist completion, or approval. A-101 remains open: the real
M05 writer's nullable governed terms explicitly block a full Term Sheet with zero writes, while the
fully populated frozen sanction fixture proves renderer capability only.

## Architecture Review 2026-07-14 09:31 - Generation Boundary and Output Proof

- 008A2's database identity lock, template-source provenance decision, strict selector, and borrower-
  variant resolver are substantive and its PostgreSQL races are genuine.
- 008B retains exact replay and frozen facts, but puts legal generation/`LoanDocument` ownership in
  the foundation `documents` app, whose public module trusts view-only generation/object checks and
  owns collection queries. `008B2` establishes the source-defined legal-documents deep boundary,
  direct-call authority, selector ownership, and honest nullable loan-account integrity before 008C.
- Current PDF acceptance checks only metadata; the Word fixture is plain UTF-8 text named `.docx`.
  `008B3` adds a bounded renderer adapter plus genuine DOCX/PDF content/Unicode proof and keeps
  malformed/pathological input zero-write.
- The real M05 terminal writer has no governed numeric rate, repayment date, penal-rate, fee, or
  dispute-clause source (A-079). The positive 13-field test inserts those facts directly, so it is a
  renderer projection test rather than a real M05-to-M06 tracer. A-101 keeps full Term Sheet
  generation explicitly configuration-blocked until governance identifies the immutable owners;
  M06-FR-013 remains partial rather than receiving invented legal/financial terms.

## Architecture Review 2026-07-14 06:42 - 008A Integrity Follow-up

- 008A delivers the exact §26.3 routes, immutable successor rows, metadata-only responses,
  attributable evidence, and a genuine five-request PostgreSQL successor race.
- Effective overlap validation locks only already-existing approved rows. Two different concurrent
  first versions for the same document/borrower identity can therefore both win; `008A2` adds a
  database-backed identity lock/constraint and a different-payload five-race test.
- Template-file resolution currently queries `DocumentFile` directly and treats global download
  permission plus existence as reference authority. `008A2` adds a documents-owned upload-
  provenance/sensitivity/permission decision and rejects application/loan-owned or unproven files.
- Source template variants say Individual/FPO, while repository members use `individual_farmer`,
  `fpc`, and `producer_institution`. A-097 forbids an implicit mapping; `008A2` owns the resolver and
  008B must fail unresolved variants closed.

## The documentation package (what exists and when)

Collected from the borrower at Stage 4 start (V10 p.13 §4.1): witness PAN/Aadhaar — the witness
must be an existing SFPCL shareholder; a cancelled cheque of the applicant's account (bank
details for SAP); one blank-dated cheque as security. Blank-dated cheque definition and default
use: V10 p.14 top.

Prepared by the Compliance Team (V10 p.14 §4.2; Deck p.7), then the complete set goes back to
the Sanction Committee for approval (V10 p.14 §4.2 intro — this second committee pass is the
008K sequence input):

| Instrument | Signatories | Stamp/notary | Applicability | SOP cite |
|---|---|---|---|---|
| Power of Attorney (in favour of CS; authorises share sale on default) | farmer AND nominee | ₹500 stamp paper, notarised | always | V10 p.14 §4.3; Deck p.7 |
| Declaration / Tri-party agreement (subsidiary deducts repayment from produce payments) | loan applicant (borrower) and nominee; parties: borrower + SFPCL + subsidiary | — | when borrower transacts with a subsidiary | V10 p.15 §4.4; p.14 §4.2 |
| Share Transfer Form SH-4 (held blank, returned on closure) | shareholder + valid witness | nominal stamp duty (V10 p.24) | physical shareholding only | V10 p.15 §4.5; p.7 glossary |
| CDSL pledge (online) | pledgor/pledgee BO accounts | — | demat shareholding only; future shares issued to borrower stand pledged too | V10 p.14 §4.2, pp.15-16 §4.6 |
| Term Sheet | applicant + nominee; countersigned by CFO (≤ ₹5,00,000) or CFO + 2 Directors (above) | — | always | V10 p.17 §4.9, p.18 §4.13 last bullet |
| Loan Agreement (after Term Sheet execution) | applicant + witness (witness mandatory) | ₹500 stamp paper, notarised; p.24 says agreements "stamped ad valorem" — see open decisions | always | V10 p.17 §4.10; p.29 item 6 |
| Bank Verification Letter | issuing bank (signed + stamped) | — | only on signature mismatch | V10 p.17 §4.11 |
| Checklist (index of all documents) | see 008K sequence | — | always | V10 p.18 §4.12 |

Term Sheet contents — 13 fields (V10 p.17 §4.9): borrower details, nominee details, shares held,
facility long/short term, amount, purpose, rate of interest, tenure of interest, repayment date,
penalty interest, other charges/fees, security, dispute resolution. Tenure classification:
1 year = short term, otherwise long term; extension at company discretion; floating interest,
changes communicated via SMS/e-mail (V10 p.21).

## Per-slice anchors

### 008A Document Template Model and Versioning
Annexure index (V10 p.29): A application form, B appraisal note, C PoA, D declaration/tri-party,
E term sheet, F loan agreement, G bank verification letter, H checklist, I SAP customer-code
Excel, J board/sanction committee register, K grievance form, L rejection note — with separate
Individual and FPO variants "wherever required". Templates live on the intranet today; the model
must version them (SOP itself is board-approved per revision, V10 p.33). Conflict: see Annexure
lettering in open decisions.

API/data extract added while sharpening 008A (2026-07-14): API contracts §26.3 names
`GET/POST /api/v1/document-templates/` and
`PATCH /api/v1/document-templates/{document_template_id}/`. The create shape carries
`template_code`, `template_name`, `document_type`, nullable/variant `borrower_type`,
`template_version`, `template_file_id`, `merge_fields`, `approval_status`, and `effective_from`.
Data model §16.2 additionally names nullable `effective_to` and `created_at`, makes template code
unique, indexes document type/borrower type/approval status, and makes the template file reference
nullable. Later generation is the separate §26.4 boundary; 008A must not generate a loan document.

### 008B Document Generation Shell
Generate from the 008A templates with borrower/nominee/loan facts; Individual vs FPO variant
selection (V10 p.29). Generated Term Sheet must carry all 13 §4.9 fields; Loan Agreement follows
Term Sheet execution (V10 p.17 §4.10).

API/model extract added while sharpening 008B (2026-07-14): API contracts §26.4 defines
`POST /api/v1/loan-applications/{loan_application_id}/loan-documents/generate/` with
`document_type`, `template_id`, and `output_format`, returning the loan-document id, generated
status, stored document id, and file name. Section 26.5 separately lists generated documents.
Data model §16.3 owns the immutable application/template/file linkage plus category, required
party, generation/execution/verification states, optional stamp/notary/custody/retention facts, and
creation time. Functional §15.1 requires approved-field generation for borrower variants,
borrower/loan/shareholding/nominee/witness facts, configurable clause/template history, PDF or Word
output, later signed-copy upload, and verification status. Generation must use application-owned
source facts and the exact approved/effective template; it must not fabricate missing nominee,
witness, appraisal, sanction, or repayment facts.

Implementation extract added 2026-07-14: §26.4 exact replay is retained by application, exact
template version, and output format. Generated legal metadata begins generated/pending/pending and
never implies execution, verification, checklist completion, or download. The source does not name
merge identifiers or a distinct persisted dispute-clause field; A-100 records the conservative
vocabulary and requires explicitly stored sanctioned text rather than generated legal wording.
Template upload provenance alone is insufficient: generation also verifies retained source-object
size/checksum before producing PDF/Word bytes.

### 008C Documentation Checklist Applicability
Applicability rules above: SH-4 iff physical shares; CDSL pledge iff demat; tri-party when a
subsidiary relationship exists; bank-verification letter iff mismatch; everything else always.
Checklist is an index of all package documents (V10 p.18 §4.12, Annexure H). Borrower
obligations view (V10 pp.27-28): KYC/CKYC consent, declarations (end-use, not wilful defaulter,
asset unencumbered), income/agri evidence (Satbara/7-12, crop details, 6-month bank statements),
security documents (SH-4 blank, undated cheque, NACH/ECS mandate, guarantor if required),
ongoing duties (notify address/bank/landholding/shareholding changes). NACH/ECS mandate appears
only in the p.27 obligations table, not in §4.2 — record as assumption when implementing.

API/model extract added while sharpening 008C (2026-07-14): API §27.1 defines only
`GET /api/v1/loan-applications/{loan_application_id}/document-checklist/`, returning checklist and
application ids, checklist status, ordered item code/label/required/applicable/completion facts, and
CS/Credit Manager/Sanction Committee/Senior Manager signature statuses. Data model §16.4 makes one
checklist unique per application and retains four signature ids; §16.5 owns item applicability,
completion, optional loan-document link, verification facts, and remarks. M06-FR-001 requires
automatic creation after sanction; no public refresh/update/approval route is defined here.

### 008D Stamp Duty and Notarisation Tracking
Maharashtra Stamp Act 1958, at execution, owner CS (V10 p.24; Deck p.10): loan agreements
stamped (₹500 per §4.10; "ad valorem" per p.24 — open decision), PoA and SH-4 nominal duty,
instruments executed with witnesses. CS maintains an instrument checklist, affixes electronic
stamps, logs into a register, keeps originals securely (V10 p.24). Disbursing before stamping
completes is a High error (Deck p.11 #5; V10 p.32 #5). Stamp rates vary by state; indicative
Maharashtra rates in Annexure J (V10 p.26 note 4).

API/model extract added while sharpening 008D (2026-07-14): API §26.9 POST records stamp amount,
physical/electronic type, nullable stamp number/purchase/execution dates, pending/adequate/
insufficient status, and remarks. API §26.10 POST records nullable notary identity/date,
pending/completed/rejected status, evidence document id, and remarks. Data model §16.7-§16.8 makes
each record one-to-one with a loan document and names CS verification/evidence facts. Auth §26.4
makes Compliance the recorder and Company Secretary the approver; neither endpoint grants evidence
download, checklist approval, or disbursement readiness.

### 008E Signature Mismatch Workflow
Credit Assessment Team verifies signature consistency across PAN card, cheque, and KYC documents
before disbursement (V10 p.17 §4.11). On mismatch, two resolution options: (1) Bank Verification
Letter signed and stamped by the bank confirming the cheque signature (Annexure G); (2) borrower
declaration on non-judicial stamp paper affirming the signature. Missing witness signatures on
agreements/SH-4 is a Critical error (V10 p.32 #4).

Implementation extract added 2026-07-14: §26.7 captures borrower/nominee/witness/user signer
identity and frozen name, wet-ink/digital/scanned method, pending/signed/mismatch state, signed time,
and mismatch flag. §26.8 accepts only bank-verification-letter or borrower-declaration resolution,
one evidence document id, and remarks. The retained evidence file must be linked by a same-
application current-renderer legal document of the exact type; declaration additionally consumes
the exact 008D adequate stamp record. Application-owned mismatch semantics prefer unanimous
verified legal-owner facts over intake cheque uncertainty. Projection owns only Bank Verification
Letter applicability and rolls back against completed evidence; it never completes or approves the
checklist or grants file/disbursement authority. A-107 records the absent signed-copy/bank-
attestation aggregate and the conservative retained-file interpretation.

### 008F Power of Attorney Workflow
PoA in favour of the Company Secretary authorising share-sale initiation on default; signed by
farmer AND nominee; ₹500 stamp; notarised (V10 p.14 §4.3, Annexure C). CS "acts under PoA for
stamping, handling SH-4 & blank-dated cheques" (V10 p.6 authority matrix row 4). Prepared by
Compliance / verified by CS (auth-permissions §16.4).

### 008G Tri-Party Agreement Workflow
Repayment mechanics the agreement encodes (V10 p.15 §4.4): borrower sells produce to subsidiary;
subsidiary deducts principal + interest + dues from the produce payment; subsidiary remits the
deduction to SFPCL which settles the loan. Signed by borrower and nominee; parties borrower +
SFPCL + engaged subsidiary; Annexure D. This is the contract 010E (subsidiary deduction
reconciliation) later relies on.

### 008H SH-4 Physical Share Security Workflow
Executed blank by shareholder + valid witness for physical holdings (V10 p.15 §4.5); held in
custody (CS / authorised Compliance custody, auth-permissions §16.4); invoked only with Sanction
Committee/Board approval (V10 p.31 recovery row; p.32 #9: using SH-4/undated cheques without
board approval is an error); returned with NOC on closure (V10 p.20 §6.1-II last bullet).

### 008I CDSL Pledge Workflow
V10 pp.15-16 §4.6-§4.8: pledgor and pledgee need CDSL BO accounts (same or different DPs);
pledgor files Pledge Request Form (PRF) in duplicate with its DP → unique Pledge Sequence No.
(PSN); pledgee accepts via its DP (or standing instructions make acceptance automatic); the loan
agreement number is recorded in the pledge request form; loan disbursement itself is outside the
depository system. Future shares issued to the borrower stand pledged as well (V10 p.14 §4.2).
Invocation on default: pledgee submits Invocation Request Form (IRF); securities move without
pledgor confirmation; pledgor is informed by its DP (§4.7). Unpledge on repayment: pledgor files
Unpledged Request Form (URF) in duplicate against the original PSN, part or full quantity;
pledgee's DP accepts/rejects; or the pledgee files the URF directly ("Auto Unpledged", no
pledgor instruction) (§4.8) — 011I consumes this.

### 008J Blank-Dated Cheque and Cancelled Cheque Custody
Cancelled cheque verifies account number/IFSC/branch for disbursement (V10 p.14 top; 004J owns
profile storage). Blank-dated cheque held as security; on default the lender may insert the date
and present it for recovery (V10 p.14) — but presentation requires Sanction Committee/Board
approval (auth-permissions §16.4; V10 p.31). Custody with CS (V10 p.6 row 4); certified by CS &
Accounts, collected at documentation stage, returned upon closure (V10 p.27 security row).

### 008K Final Documentation Approval Sequence
V10 p.18 §4.13 (Deck p.8): Compliance Team assembles file + checklist → CS reviews/approves →
Credit Assessment team (Credit Manager) approves → Sanction Committee (CFO and directors; any
one director signs the checklist per the authority matrix) → Treasury Team for disbursement;
Senior Manager - Finance signs the checklist only after actual disbursement. Signature meanings:
CS = all documents verified and attached; Credit Manager = loan limits reviewed and confirmed;
Sanction Committee = final approval per matrix; Sr Manager - Finance = loan disbursed. Term
Sheet countersignature: CFO if ≤ ₹5,00,000, CFO + 2 Directors above. The sequence is strictly
ordered — model it with 002H guards; 009D (disbursement readiness) consumes its completion.

### 008L / 008L2 Member Portal Documentation Actions
Borrower-side obligations and evidence (V10 pp.27-28): what the member must submit, who
certifies (field officer collects, credit officer verifies KYC; CS & Accounts certify security
docs), and cadences (re-KYC every 2 years; annual income/agri evidence refresh). Portal actions
must respect the signing rules above (applicant + nominee/witness signatures are wet-ink SOP
facts — the portal tracks status/uploads, it does not replace signatures; record as assumption).

### 008M Documentation Hub Frontend Wiring
Blockers that must be visible before disbursement: unstamped/unnotarised instruments (V10 p.24),
signature mismatch unresolved (§4.11), missing witness (p.32 #4), incomplete checklist
signatures in the §4.13 order, custody not recorded. Deck p.7-8 is the visual/stage reference.

## Cross-epic boundary notes
- Witness identity (PAN/Aadhaar, existing-shareholder rule) is Epic 004 data (004E/006Y2);
  Epic 008 consumes it in SH-4/agreement execution.
- SAP customer code email + Annexure I Excel is Epic 009 (V10 pp.18-19 §5.1-§5.3).
- Repayment/interest/DPD/capitalisation facts on V10 pp.20-22 belong to Epics 010-011
  (principal-first p.20; 30-April capitalisation p.20; grace/extension/non-payment notes
  pp.21-22; DPD buckets 1-2/2-3/3+ years and quarterly CFO MIS p.21; NOC + SH-4 + cheque return
  p.20; 8-year archive p.21).
- Compliance trackers (s.378ZJ/s.186 60%-or-100% free reserves/NBFC 50% test/KYC-AML 5-year
  retention/money-lending exemption/data protection/8-year records) are V10 pp.23-26 → Epic 011K-011M.
- Grievance escalation to CS with grievance form (V10 p.32) → 011N.

## Open decisions and conflicts (record, do not invent)
1. **Annexure lettering is internally inconsistent**: p.13 §3.1 calls the Credit Sanction
   Register "Annexure K"; the p.29 index says J = Board/Sanction Committee Register,
   K = Grievance Form, L = Rejection Note; p.26 note 4 says stamp-duty rates are "Annexure J";
   p.32 routes grievances to "Annexure L". This is the map's "Annexure K" open decision —
   resolve with the owner before fixing any register/template code (007H already carries this).
2. **Loan agreement stamp value**: §4.10 says ₹500 stamp paper; the p.24 compliance table says
   "stamped ad valorem". Configuration, not constant; owner confirms the operative rule.
3. **NACH/ECS mandate** appears only in the borrower-obligation table (p.27), not in the §4.2
   package list; no annexure exists for it. Confirm whether it is in MVP documentation scope.
4. Physical vs demat handling, custody locations, and SH-4/cheque invocation authority "pending
   client confirmation" rows in auth-permissions §16.4 remain open — treat invocation as
   blocked-behind-approval, never automatic.
