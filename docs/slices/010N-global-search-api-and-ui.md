# Slice 010N: Global Search API and UI

## Status
Not Started

## Parent Epic
Epic 010: Servicing, Repayments, Interest, and Monitoring (cross-module search; placed here because members, applications, and loan accounts all exist by this point)
Epic file: `docs/epics/010-servicing-repayments-interest-monitoring.md`

## Goal
Implement the Global Search Results screen (S02): one search box that finds members, loan applications, and loan accounts by name/reference/number, with permission-aware results.

## User Value
Staff reach any member, application, or account in seconds without navigating module lists — the search screen the prototype already shows becomes real.

## Depends On
- 010M

## Source References
- docs/source/screen-spec.md screen S02 (Global Search Results)
- docs/source/api-contracts.md section 8.4 (search conventions), section 8.1 (pagination)
- docs/source/data-model.md section 30 (indexing strategy — search fields must be indexed)
- docs/source/auth-permissions.md (results restricted to what the role may view)

## Prototype Reference
- sfpcl-lms/src/pages/search/GlobalSearchResults.tsx

## Concrete Requirements
1. Backend: a search endpoint following §8.4 conventions across members (name, member number), loan applications (reference), and loan accounts (account number); results grouped by entity type, paginated, and filtered by the caller's permissions — a role without `view_members` gets no member results.
2. Database: add indexes for the searched columns per data-model §30 if not already present (non-destructive migration).
3. Frontend: wire `GlobalSearchResults.tsx` and the header search box to the API; empty-query, no-results, error, and unauthorized states with existing patterns.
4. No sensitive values (PAN, Aadhaar, bank numbers) in search results or as searchable inputs.
5. Privacy hardening (PRODUCTION_COMPLETION_BLUEPRINT.md §6.3 header-search row): all matching happens server-side — remove `Header.tsx`'s client-side search over mock member/application/account data (which today includes sensitive fields); no local search index of business or sensitive data may remain anywhere in the frontend.

## Owned Mock Removals
- `src/pages/search/GlobalSearchResults.tsx` — no `mockData` import or inline fixtures remain.
- `src/components/layout/Header.tsx` — search paths only; the notification dropdown rows and the final removal of the file's `mockData` import are owned by 010O.

## Test Cases
- Search by member name, application reference, and account number returns the seeded records.
- Permission filtering: restricted role's results exclude entity types it cannot view.
- Sensitive-value search returns nothing and leaks nothing.
- Query performance sanity: search uses indexed lookups (assert query plan or via test on seeded volume).

## Out of Scope
Full-text ranking engines, fuzzy matching beyond simple case-insensitive contains, audit explorer search (012D).

## Risk Level
Medium

## Acceptance Criteria
- Global search works end to end with permission-correct, paginated results.
- All gates pass; screenshots of results and empty state saved.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated
- [ ] Database rules followed
- [ ] Permissions tested
- [ ] Visual evidence saved
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Handoff updated
- [ ] State updated
- [ ] Commit created only after passing gates
