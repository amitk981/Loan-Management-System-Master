# Risk Assessment

Risk level: High.

This slice changes eligibility ordering, object authority, optimistic provenance, transaction lock
order, and auditable evidence mutations. A defect could incorrectly qualify an inactive member,
leak an owned member, or preserve stale verified authority.

Controls: relaxation requires two independent persisted facts; authority is centralized and tested
for owner/unowned/global-permission/missing-permission/object denial; all evidence mutation paths
lock Member before evidence and increment Member version; service mutations write history/audit in
the same transaction; five active-member and five credit PostgreSQL races passed twice; 493 backend
tests and 204 frontend tests passed with 93% backend coverage. No migration, dependency, frontend,
source, protected-path, or external-service change was made.

Manual review required: yes, under the owner's standing High-risk approval and normal Ralph review.
