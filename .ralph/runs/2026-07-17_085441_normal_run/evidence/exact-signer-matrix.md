# Exact Current Applicable Signer Matrix

Only the latest current document for an applicable required checklist item participates. Earlier
versions and unrelated document types do not poison readiness. Every row below remains exact: an
extra party, wrong identity, or semantic duplicate identity on the required current document fails.

| Checklist item | Current document type | Exact parties / owner source |
|---|---|---|
| PoA | `power_of_attorney` | Borrower and nominee |
| Tri-party agreement | `tri_party_agreement` | Borrower and nominee, only when applicable |
| SH-4 | `sh4` | Borrower and the verified shareholder witness, only when applicable |
| Term Sheet | `term_sheet` | Borrower, nominee, and the exact approval-owned CFO/Director set |
| Loan Agreement | `loan_agreement` | Borrower and the verified shareholder witness |

`06-exact-signer-matrix-green.txt` proves a genuine retained documentation fixture fails for an
extra/wrong borrower identity on each of the five required current families and retains exact Term
Sheet authority checks. `05-unrelated-signature-green.txt` and the same genuine fixture prove a
valid borrower signature on current `final_checklist` history leaves readiness true. Current
mismatch rows still require their exact resolution document, audit, workflow, and version evidence.
