# Scope and Authorisation Parity Matrix

| Mutation / actor | CFC scope | Approve/reject |
|---|---:|---:|
| Genuine current owner path, active primary CFC | allowed | allowed |
| Genuine current owner path, governed CFC on non-finance primary role | allowed | allowed |
| Changed beneficiary IFSC/current bank decision | denied | conflict, zero writes |
| Replaced/incoherent source governance | denied | conflict, zero writes |
| Changed loan-creation identity or initiation audit/workflow/task | denied | conflict, zero writes |
| Synthetic/missing application bank-owner manifest | denied | conflict |
| Inactive/unknown/missing governed authority | denied | forbidden |
| Same maker/checker | denied | forbidden |
| Exact terminal replay | terminal scope closed | original projection, zero writes |
| Changed/opposite replay | terminal scope closed | conflict, zero writes |

Both consumers call `resolve_current_disbursement_evidence`; the removed scope/authorisation copies
no longer make separate current-evidence decisions.
