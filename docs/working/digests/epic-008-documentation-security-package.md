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

### 008C Documentation Checklist Applicability
Applicability rules above: SH-4 iff physical shares; CDSL pledge iff demat; tri-party when a
subsidiary relationship exists; bank-verification letter iff mismatch; everything else always.
Checklist is an index of all package documents (V10 p.18 §4.12, Annexure H). Borrower
obligations view (V10 pp.27-28): KYC/CKYC consent, declarations (end-use, not wilful defaulter,
asset unencumbered), income/agri evidence (Satbara/7-12, crop details, 6-month bank statements),
security documents (SH-4 blank, undated cheque, NACH/ECS mandate, guarantor if required),
ongoing duties (notify address/bank/landholding/shareholding changes). NACH/ECS mandate appears
only in the p.27 obligations table, not in §4.2 — record as assumption when implementing.

### 008D Stamp Duty and Notarisation Tracking
Maharashtra Stamp Act 1958, at execution, owner CS (V10 p.24; Deck p.10): loan agreements
stamped (₹500 per §4.10; "ad valorem" per p.24 — open decision), PoA and SH-4 nominal duty,
instruments executed with witnesses. CS maintains an instrument checklist, affixes electronic
stamps, logs into a register, keeps originals securely (V10 p.24). Disbursing before stamping
completes is a High error (Deck p.11 #5; V10 p.32 #5). Stamp rates vary by state; indicative
Maharashtra rates in Annexure J (V10 p.26 note 4).

### 008E Signature Mismatch Workflow
Credit Assessment Team verifies signature consistency across PAN card, cheque, and KYC documents
before disbursement (V10 p.17 §4.11). On mismatch, two resolution options: (1) Bank Verification
Letter signed and stamped by the bank confirming the cheque signature (Annexure G); (2) borrower
declaration on non-judicial stamp paper affirming the signature. Missing witness signatures on
agreements/SH-4 is a Critical error (V10 p.32 #4).

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
