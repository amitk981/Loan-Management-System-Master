# Risk Assessment

Risk level: High findings; Low review-mutation risk.

- Selected slice: architecture-review
- Mode: architecture_review
- Production code changed: no.
- Protected/source/orchestrator-owned paths changed: no.
- Queue changes: one numeric `Not Started` corrective added; `CR-012` and `010A` now depend on it.

## Principal Product Risks

- Exact Loan Account, assigned-SAP, and CFC collection projectors can reject incoherent evidence
  after their broader count/offset query has reported it. Retained probes show empty row bodies with
  `total_count: 1`, causing existence disclosure, incorrect pages, and stranded valid rows.
- The member portal treats a current SAP completion for another application as completing the
  requested application's SAP stage. This contradicts the 009L4 application-edge contract and can
  present a borrower-visible stage that Loan Account/readiness consumers reject.

Both are High binding source/slice-contract risks under M07-FR-010 and the Epic 009 nondisclosure
boundary. This review does not repair production code; 009L5 is the immediate corrective owner.

## Secondary Risks

- Lifecycle evidence has two scalar validators that can drift independently.
- The required staff-workspace/action/transport/error matrices remain incomplete.
- Delaying CR-012 and 010A behind 009L5 extends the queue but prevents browser evidence and servicing
  from certifying or consuming known incorrect Epic 009 truth.

## Controls

- Five retained review-only probes reproduce the findings without changing product files.
- Independent Standards and Spec passes converged on the selector defect; the Spec pass separately
  found the portal application edge.
- One root corrective groups the symptoms; no leaf proliferation or business rule was invented.
- Queue lint passes, no dependency is dangling/cyclic, and no `Blocked` slice needs re-parking.
- A-135 remains pending-only; no SAP posting-success authority or adapter was invented.
