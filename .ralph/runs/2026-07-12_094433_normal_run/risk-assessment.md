# Risk Assessment

Risk level: High.

This changes protected member identity, approval authority, uniqueness, and audit history. Controls
are a dedicated unassigned approval permission, requester/checker separation, row locks and member
versions, protected values, masked history/audit, atomic approval, and hash uniqueness constraints.
One reversible migration adds the request table and constraints. No protected file was modified.
