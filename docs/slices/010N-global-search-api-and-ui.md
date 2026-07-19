# Slice 010N: Global Search API and UI

## Status
Not Started

## Parent Epic
Epic 010: Servicing, Repayments, Interest, and Monitoring (cross-module search; placed here because members, applications, and loan accounts all exist by this point)
Epic file: `docs/epics/010-servicing-repayments-interest-monitoring.md`

## Goal
Implement the complete Global Search Results screen (S02): one server-owned search that finds every
source-defined member, application, account, document, repayment, compliance, and authorised audit
result without exposing records or sensitive lookup values outside the caller's scope.

## User Value
Staff reach every source-supported record group in seconds without navigating module lists, while
sensitive exact matching stays hashed, masked, permission-scoped, and absent from browser indexes.

## Depends On
- 010M

## Runtime Capabilities

- `localhost-e2e-server`

## Trusted Browser Acceptance

- Spec: `e2e/global-search.e2e.spec.ts`
- Screenshot: `global-search-results.png`
- Screenshot: `global-search-empty.png`

## Source References
- docs/source/screen-spec.md screen S02 (Global Search Results)
- docs/source/api-contracts.md section 8.4 (search conventions), section 8.1 (pagination)
- docs/source/data-model.md section 30 (indexing strategy — search fields must be indexed)
- docs/source/auth-permissions.md (results restricted to what the role may view)
- `docs/working/digests/epic-010-servicing-repayments-interest-monitoring.md` §010M–010O

## Prototype Reference
- sfpcl-lms/src/pages/search/GlobalSearchResults.tsx

## Concrete Requirements
1. Backend: implement the §8.4 endpoint over all S02 inputs: borrower/FPC name, application and loan
   references, folio, number of shares, PAN, Aadhaar last four, mobile, email, SAP customer code,
   cheque number, CDSL pledge sequence, SH-4 reference, and bank-account last four.
2. Group results exactly as S02 requires: Members, Loan Applications, Loan Accounts, Documents,
   Repayments, Compliance records, and Audit logs for explicitly authorised users. Each group is
   independently permission/object scoped, paginated, deterministically ordered, and capped.
3. PAN/Aadhaar matching is exact and server-side through the established keyed-hash/search-token
   owner; suffix searches use scoped stored suffixes. Never scan/decrypt raw values, return raw
   PAN/Aadhaar/bank/cheque data, or log the submitted query. Sensitive identifiers stay masked, but
   the permission-scoped application number, folio number, and SAP code required by S02 remain
   visible as result identifiers.
4. Add measured indexes/search tokens for the contracted fields per data-model §30 using at most one
   non-destructive migration. No general full-text engine or duplicated cross-domain search table.
5. Wire `GlobalSearchResults.tsx` and the header search box to the grouped API, including loading,
   empty-query, partial-group, no-results, safe error, and unauthorised states with existing patterns.
6. Remove `Header.tsx` client-side search over mock business/sensitive data. No local browser search
   index, cached raw query, or sensitive result payload may remain.
7. Render every S02 result card field from server-owned projections: title; the applicable visible
   application/folio/SAP identifier; current stage and risk status; requested, sanctioned, or
   outstanding amount where applicable; current workflow owner; last-updated date and user; and only
   permission-valid quick actions (`Open`, `View documents`, `View loan account`). Missing or denied
   fields/actions are omitted without leaking their existence.

## Owned Mock Removals
- `src/pages/search/GlobalSearchResults.tsx` — no `mockData` import or inline fixtures remain.
- `src/components/layout/Header.tsx` — search paths only; the notification dropdown rows and the final removal of the file's `mockData` import are owned by 010O.

## Test Cases
- Parameterised coverage maps every one of the 15 S02 inputs to its correct grouped, masked result.
- Permission filtering removes whole unauthorised groups and cross-object records without leaking
  counts or match existence; audit results require their separate restricted authority.
- PAN/Aadhaar exact or suffix lookup returns only authorised masked records through search tokens;
  raw values never appear in response, browser state, logs, audit payloads, or query plans.
- Result-card contract tests cover title, visible source identifier, status/risk, applicable amount,
  owner, last-updated actor/date, and permission-filtered quick actions for every result group.
- Invalid/short sensitive queries, injection/wildcard attempts, unknown fields, and excessive request
  rate fail safely; indexed-query evidence covers representative volume without table scans.

## Out of Scope
Full-text ranking engines, fuzzy matching beyond source-defined matching, unrestricted audit-explorer
functionality (012D), raw-sensitive display, and a duplicated cross-domain search datastore.

## Evidence Required
Saved RED/GREEN selector/API/permission and frontend request/render output; indexed-query or query-plan
evidence on representative fixtures; sensitive-search denials and mock-index removal proof; both
trusted-browser screenshots from two passing contract runs; focused reverse-consumer and full gates.

## Risk Level
High

## Acceptance Criteria
- Global search works end to end with permission-correct, paginated results.
- S02 result cards expose the required non-sensitive identifiers and fields while masking sensitive
  values and suppressing unauthorised quick actions.
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
- [ ] Ralph owns mechanical bookkeeping; record only substantive unresolved risks/decisions in `review-packet.md` and `HANDOFF` if needed
- [ ] Commit created only after passing gates
