# Browser Repair Diagnosis

## Exact independent failure

The prior independent trusted-browser run completed real Django login, application listing,
selection of `LO000008L4`, and the application-detail GET in every case. Each case then spent its
entire 30-second timeout waiting for this locator:

```text
getByRole('navigation').getByRole('button', {
  name: 'Disbursement Status',
  exact: true
})
```

The approved borrower sidebar defines that button's accessible label as `Disbursement`.
`Disbursement Status` is the MP14 page heading and portal header section label. The spec therefore
confused the destination's navigation label with its page title.

## Ranked hypotheses

1. Stale/mismatched accessible name in the trusted-browser locator. Confirmed by the exact
   `borrowerNavItems` entry in `src/components/layout/Sidebar.tsx`.
2. Borrower role hydration rendered staff navigation. Rejected: the same navigation successfully
   exposed `My Applications`, and all real portal requests succeeded.
3. The sidebar collapsed after application selection. Rejected: it defaults expanded and the
   selected-detail action does not mutate its local collapse state.
4. The selected-detail view unmounted the sidebar. Rejected: `MemberPortalLayout` continues to wrap
   every `BorrowerPortal` tab.

## Minimal repair

Only the three identical locators in `e2e/portal-disbursement-status.spec.ts` now use the existing
accessible name `Disbursement`. No production path, route seam, scenario fixture, visual assertion,
or source contract changed.
