# Spec Review

Fixed point: `85f142c2`

Reviewed slice contracts: 008I2, 008I3, 008I4, 008J, and 008K.

## Findings

1. **Critical — synthetic cheque JSON completes a checklist.**
   008K requires exact current application/package/member/bank/blank-cheque/cancelled-cheque ids.
   `_terminal_evidence` accepts a newest application-labelled `VersionHistory` JSON projection
   without resolving a current cheque row or those exact identities. The shipped test fabricates
   that ledger; the independent regression proved no cheque row existed and still received 200.
2. **High — status-only rows pass ordered approval.**
   Company Secretary approval checks `completion_status` but not one matching durable completion
   action per current item. The success helper bulk-updates all items, creates no item actions, and
   approval persists an empty completed-action list. The independent regression expected a
   zero-write 409 and received 200.
3. **High — the promised public terminal matrix is bypassed.**
   Only `final_checklist` and the synthetic cheque path complete publicly; ordered success bypasses
   PoA, tri-party, SH-4, CDSL, Term Sheet/Loan Agreement signatures, stamp/notary, and mismatch
   checks. Multi-role actions also freeze the first effective role instead of the authorising role.
4. **Medium — races prove counts, not exact winner/loser identities.**
   Changed-payload races do not bind the retained payload/request/workflow/action to the winner or
   prove each loser absent from all success evidence.

## Verified behavior

Exact §27/§28 routes, ₹500 PoA activation, nullable pending CDSL, masked ordinary reads, central
audited reveal, blank-cheque custody, strict stage ordering, and the zero-write finance-signature
blocker are substantive. No unrelated scope creep was found.

Corrective owner: `008K3-final-checklist-evidence-closure` (with boundary/hash proof in 008K2).
