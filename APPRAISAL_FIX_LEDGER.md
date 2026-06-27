# Appraisal Workbench — Fix Ledger

**Scope:** Gaps between the current `AppraisalWorkbench.tsx` implementation and the requirements in `docs/screen-spec.md` (S15–S20), `docs/functional-spec.md` (M04, BR-017–BR-025), and `docs/user-flows.md` (User Flow 4–6).

**Priority key:**
- `P0` — Workflow gate broken or spec requirement directly violated; fix before demo
- `P1` — Appraisal note content incomplete per spec; fix before sign-off
- `P2` — Outcome actions not wired; currently cosmetic stubs
- `P3` — UX / queue display gaps; improvement items

---

## P0 — Broken Gates

### [P0-01] TAT counter not tracked or displayed
**Spec references:** S19 ("system must track a two-day TAT"), M04-FR-003 ("track two-day TAT from application receipt"), BR-017 ("Loan Appraisal Note must be prepared within two days")
**Current behaviour:** `tatDaysRemaining` exists on the `LoanApplication` type and is present in mock data, but is never read or rendered anywhere in `AppraisalWorkbench.tsx`.
**Required behaviour:**
- Queue list rows must show a TAT chip (e.g. "2d left" in amber, "Overdue" in red).
- The detail panel header card must show a visible TAT counter: days elapsed, days remaining, and a red "TAT Breach" badge when remaining ≤ 0.
- Step 2 info banner should include "⏱ TAT: N days remaining" alongside the existing guidance text.

**File:** `sfpcl-lms/src/pages/appraisal/AppraisalWorkbench.tsx`
**Change:** In the queue row (around line 242–264) add `tatDaysRemaining` chip. In the header card (around line 272–291) add a TAT display row. Derive from `app.tatDaysRemaining`.

---

### [P0-02] Eligibility checklist (S15) does not gate the loan limit calculator (S18)
**Spec references:** S15 ("Eligibility Assessment — outcome must be complete before going to loan limit calculator"), user-flow 4 section 12.4 ("System requires entry / confirmation of active member, no default, land docs, KYC, bank statement, crop plan, loan purpose, borrower acceptance of terms, repayment capacity"), S18 ("Cannot calculate without share count, valuation config, land area"), functional-spec M04-FR-004 ("checklist for active membership, default status, land documents, KYC, bank statement, crop plan and loan purpose")
**Current behaviour:** In Step 2, `LoanLimitCalculator` is rendered first (lines 503–512), then `EligibilityChecklist` is rendered below it (lines 514–518). The `LoanLimitCalculator` is always accessible regardless of eligibility checklist state.
**Required behaviour:** The eligibility checklist must gate the loan limit calculator. Until all eligibility checks pass, the calculator section should show a locked state with a message: "Complete eligibility checklist to unlock loan limit calculation." The loan limit calculator becomes interactive only after `EligibilityChecklist` reports all items checked.

**File:** `sfpcl-lms/src/pages/appraisal/AppraisalWorkbench.tsx`
**Change:**
1. Move `EligibilityChecklist` above `LoanLimitCalculator` in Step 2 JSX.
2. Add `eligibilityComplete` state, driven by a callback from `EligibilityChecklist` (or derived from internal checklist items).
3. Wrap `LoanLimitCalculator` with a conditional: if `!eligibilityComplete`, render a locked placeholder instead.

**File:** `sfpcl-lms/src/components/loan/EligibilityChecklist.tsx`
**Change:** Add an `onComplete?: (allPassed: boolean) => void` prop so the parent can track checklist completeness.

---

### [P0-03] "Agrees to terms" and "loan purpose confirmed" checks missing from eligibility checklist
**Spec references:** S15 eligibility checklist row: "Agrees to terms — Capture declaration"; user-flow 4 section 12.5: "Agreement to terms — Applicant must agree to Term Sheet and Loan Agreement terms" and "Loan purpose — Must be crop production / agriculture-related only"
**Current behaviour:** The eligibility checklist component (S15 representation) presumably checks active membership, default, docs, KYC — but the borrower's declaration of purpose acceptance and "agrees to terms" are not discrete checklist rows in the appraisal workbench.
**Required behaviour:** Two additional checklist items must be shown in the eligibility section of Step 2:
1. "Loan purpose confirmed as agriculture / crop production" — show the application's `loanPurpose` field value alongside a "Confirm ✓" action.
2. "Borrower agrees to Term Sheet and Loan Agreement terms" — shown as a checkbox with date/user captured on confirmation.

**File:** `sfpcl-lms/src/components/loan/EligibilityChecklist.tsx`
**Change:** Add these two items to the rendered checklist with confirmation state.

---

## P1 — Appraisal Note Content Incomplete

### [P1-01] Borrower type not shown in appraisal note
**Spec reference:** S19 fields: "Member type — Auto-populated"; M04 Appraisal Fields item 2: "Borrower type"
**Current behaviour:** Header card shows borrower name and requested amount but not member type (individual / FPC / producer institution).
**Required behaviour:** Member type must appear in the header card alongside borrower name (e.g. "Rajesh Patil · Individual Farmer · ₹2,00,000").

**File:** `sfpcl-lms/src/pages/appraisal/AppraisalWorkbench.tsx` line ~285
**Change:** Add `app.memberType` display next to `app.memberName`.

---

### [P1-02] Crop plan summary section missing from Step 2
**Spec reference:** S19 section 6: "Purpose and crop plan"; M04 Appraisal Fields item 11: "Crop plan summary — From uploaded crop plan"
**Current behaviour:** Step 2 has bank observation and risk rationale fields, but no crop plan summary field. The crop plan document status is not surfaced.
**Required behaviour:** Add a "Crop Plan & Purpose" section in Step 2 that shows: the stated loan purpose, the crop name from the application, and a text field for "Crop plan observation notes" (mandatory before forwarding).

**File:** `sfpcl-lms/src/pages/appraisal/AppraisalWorkbench.tsx` (inside Step 2 `space-y-4`)
**Change:** Add a new card after the eligibility checklist with: `app.loanPurpose`, `app.cropName`, and a `cropObservation` textarea state. Add `cropObservation.trim().length > 5` to `canForwardToSanction` check.

---

### [P1-03] Interest rate basis not shown in appraisal note
**Spec reference:** S19 fields: "Interest / rate basis"; M04 Appraisal Fields item 16: "Interest / rate basis"
**Current behaviour:** The appraisal note has no field for interest rate or rate basis. The Credit Manager review package (Step 3) also omits this.
**Required behaviour:** Show the current configured floating interest rate (from policy/mock config) in Step 2 as a read-only display field in the "Required Appraisal Inputs" card, and include it in the Step 3 review package grid.

**File:** `sfpcl-lms/src/pages/appraisal/AppraisalWorkbench.tsx`
**Change:** Add an "Interest Rate" read-only field in Step 2 grid (around line 560) showing `app.interestRate || 'Floating — as per board-approved rate'`. Include it in the Step 3 review grid at line 755.

---

### [P1-04] Past borrowing and default history section missing from Step 3 Credit Manager review
**Spec reference:** S20 section 4: "Risk and borrower history"; S22 Sanction Case Detail section 6: "Past borrowing history"
**Current behaviour:** Step 3 (lines 748–790) shows recommended amount, eligible amount, tenure, risk rating, recommendation, and security. It does not show past borrowing history or the member's default status.
**Required behaviour:** Step 3 review package must include a "Borrower History" card showing: active member status, default status (no default / past default / current default), supply years, existing outstanding loans (from member record), and any prior SFPCL loan history.

**File:** `sfpcl-lms/src/pages/appraisal/AppraisalWorkbench.tsx` (Step 3, after the main review grid)
**Change:** Add a "Borrower & Default History" card using `member.defaultStatus`, `member.supplyYears`, `member.activeStatus`, and `app.memberType`.

---

## P2 — Workflow Outcomes Are Stubs

### [P2-01] PDF generation does nothing
**Spec reference:** S19 action: "Generate appraisal PDF" (produce a structured document)
**Current behaviour:** "Generate Draft PDF" button at line 676 calls `setAppraisalDraftSaved(true)` — it saves the draft state but generates no file. "Generate Appraisal PDF" in Step 2 similarly does nothing meaningful.
**Required behaviour:** At minimum, generate a structured JSON snapshot of the appraisal data (borrower info, limits, recommendation, risk, notes) and trigger a browser download as a `.json` file. A future iteration can replace this with a PDF renderer. The button label must change to reflect success: "Download Appraisal Snapshot ✓".

**File:** `sfpcl-lms/src/pages/appraisal/AppraisalWorkbench.tsx`
**Change:** Replace the onClick handler on the PDF button with a function that builds an appraisal data object and calls `URL.createObjectURL(new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' }))` to trigger download.

---

### [P2-02] Rejection Note not generated when Credit Manager rejects
**Spec reference:** S14 ("Generate formal rejection note"), S20 output: "Rejection Note generated", user-flow 6 section 14.4 ("System generates Rejection Note, sent via email or courier")
**Current behaviour:** Credit Manager reject button (line 827) calls `onUpdateStatus(app.id, 'rejected_by_credit_manager')` and sets `decisionStatus('rejected')`. No rejection note is produced.
**Required behaviour:** On rejection, the system must generate and offer download of a Rejection Note containing: application reference, borrower name, rejection stage (Credit Assessment), rejection reason (from `creditManagerComment`), required corrective action, and date. Follow the same stub-to-download pattern as [P2-01].

**File:** `sfpcl-lms/src/pages/appraisal/AppraisalWorkbench.tsx`
**Change:** In the reject `onClick` handler, after `setDecisionStatus('rejected')`, call a `generateRejectionNote(app, creditManagerComment)` helper that downloads the note as a structured file and shows a "Download Rejection Note" link in the outcome card.

---

### [P2-03] Return action does not update application status
**Spec reference:** S20 decision: "Return to Deputy Manager - Finance for correction" — distinct from internal step navigation; status should transition back to `appraisal_in_progress`
**Current behaviour:** "Return to appraisal" button (line 813) only sets `decisionStatus('returned')` as local UI state. It does not call `onUpdateStatus` and does not move the application back in the queue.
**Required behaviour:** Returning must call `onUpdateStatus(app.id, 'appraisal_in_progress')` so the application status is persisted back, the queue reflects the change, and the status badge updates accordingly.

**File:** `sfpcl-lms/src/pages/appraisal/AppraisalWorkbench.tsx` line 812–816
**Change:** Add `onUpdateStatus?.(app.id, 'appraisal_in_progress')` inside the return onClick handler alongside `setDecisionStatus('returned')`.

---

### [P2-04] Exception Register not triggered when exception is required
**Spec reference:** S25 Exception Register: "Created when loan exceeds maximum permissible limit or requires exception approval"; S20 Credit Manager decision: "Mark exception required and route accordingly"; functional-spec BR-028 ("Loan exceeding maximum permissible limit requires CFO + two Directors and Exception Register reason")
**Current behaviour:** When `requiresException` is true, the UI shows an "Exception" badge and restricts the recommendation dropdown, but no Exception Register entry is created and no link to `ExceptionRegister` / `RegistersHub` is surfaced.
**Required behaviour:** When forwarding with `requiresException === true`, show a pre-forward confirmation step that captures the exception reason (defaulting to `creditManagerComment`) and displays a summary of what will be logged: "Exception entry will be created in the Exception Register for CFO + 2 Directors review." After forwarding, show a reference to the exception record.

**File:** `sfpcl-lms/src/pages/appraisal/AppraisalWorkbench.tsx`
**Change:** Add an `exceptionReasonNote` state. When `requiresException && decisionStatus === null`, render an additional exception-reason input before the forward button. Log the exception data to console (stub for persistence) and show an "Exception registered" chip in the outcome card.

---

### [P2-05] "Request additional documents" missing from Credit Manager decision options
**Spec reference:** S20 decision options: "Request additional documents"
**Current behaviour:** Step 3 offers three decision actions: Return to appraisal, Reject, Forward to Sanction Committee. "Request additional documents" is not available.
**Required behaviour:** Add a fourth decision button "Request Documents" that sets `decisionStatus('documents_requested')` and calls `onUpdateStatus(app.id, 'appraisal_in_progress')` with a note that documents are pending. Show a confirmation chip listing what was requested (sourced from `creditManagerComment`).

**File:** `sfpcl-lms/src/pages/appraisal/AppraisalWorkbench.tsx` (Step 3 decision buttons, around line 808)
**Change:** Add "Request Documents" button between Return and Reject.

---

## P3 — Queue and UX Gaps

### [P3-01] Queue list shows no TAT information per item
**Spec reference:** S21 Sanction Committee Workbench columns include "TAT — Time pending"; same pattern applies to appraisal queue per S19 TAT requirement
**Current behaviour:** Queue rows (lines 228–264) show application number, member name, amount, and status badge. No TAT data shown.
**Required behaviour:** Add a small TAT chip below the status badge in each queue row: green if > 1 day remaining, amber if 1 day, red/bold if overdue (≤ 0).

**File:** `sfpcl-lms/src/pages/appraisal/AppraisalWorkbench.tsx` lines 252–262
**Change:** Add `<span className="text-[10px] ...">TAT: {a.tatDaysRemaining}d</span>` below the status badge in the queue row.

---

### [P3-02] Step 2 progress count uses wrong criteria
**Spec reference:** S19 validation: eligibility status, loan limit saved, recommended amount, risk rating, risk rationale, bank observations, conditions — all required
**Current behaviour:** Step 2 count in `workflowSteps` (lines 136–142) shows "N/5 fields" based on: noteText, riskRationale, bankObservation, securityProposed, recommendedAmountNumber. Missing: crop observation (see [P1-02]), eligibility checklist completion (see [P0-02]).
**Required behaviour:** After [P0-02] and [P1-02] are implemented, update the count to "N/7 fields" and add `eligibilityComplete` and `cropObservation.trim().length > 5` to the counter array.

**File:** `sfpcl-lms/src/pages/appraisal/AppraisalWorkbench.tsx` line 136–142
**Change:** Extend the array once the above gaps are fixed.

---

### [P3-03] SOP inconsistency warning missing from loan limit display
**Spec reference:** S18: "The screen must display a configuration warning until resolved: SOP references both 30% of valuation per share and 10% of valuation per share, and also refers to ₹200 per share as the current result. Confirm the operative rule before production use."
**Current behaviour:** `LoanLimitCalculator` renders the calculation but does not display this SOP warning banner.
**Required behaviour:** `LoanLimitCalculator` must show a dismissible amber `AlertBanner` reading "Loan limit formula unconfirmed — SOP references 30% and 10%/₹200 per share. Confirm operative rule before production. (M01-FR-006)"

**File:** `sfpcl-lms/src/components/loan/LoanLimitCalculator.tsx`
**Change:** Add an `AlertBanner` at the top of the component with the SOP inconsistency warning.

---

## Implementation Order

The recommended order of fixes to maximise value per session:

| Order | Item | Why first |
|---|---|---|
| 1 | P0-01 — TAT display | Visible immediately in queue; no logic change |
| 2 | P0-02 — Eligibility gates calculator | Core workflow control gate |
| 3 | P0-03 — Agrees to terms + purpose checks | Completes S15 eligibility surface |
| 4 | P1-01 — Borrower type in header | Trivial one-liner |
| 5 | P1-02 — Crop plan section | Adds mandatory appraisal field |
| 6 | P1-03 — Interest rate display | Read-only, low-risk |
| 7 | P1-04 — Past borrowing history in Step 3 | Completes S20 Credit Manager review |
| 8 | P2-03 — Return sets status | One-liner; fixes silent no-op |
| 9 | P2-01 — PDF download stub | Replaces no-op with something tangible |
| 10 | P2-02 — Rejection Note download | Same pattern as PDF; pairs with status update |
| 11 | P2-04 — Exception Register entry | Adds missing exception logging |
| 12 | P2-05 — Request documents action | Adds fourth decision path |
| 13 | P3-01 — Queue TAT chip | Quick UX improvement |
| 14 | P3-03 — SOP warning banner | Compliance reminder |
| 15 | P3-02 — Progress count update | Depends on P0-02 and P1-02 done first |
