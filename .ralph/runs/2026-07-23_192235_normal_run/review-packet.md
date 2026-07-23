# Review Packet: 2026-07-23_192235_normal_run

## Result
Ready for independent validation

## Slice

`011NA-member-portal-notices-grievances-and-notifications`

## Change Summary

- Added member-derived APIs for notices, audited document downloads, grievance create/list/detail,
  direct notifications/read state, and closure/NOC/security-return projections.
- Wired MP19, MP20, MP23, and consolidated MP21/MP22/MP24 to backend transport with loading, empty,
  validation, error, success, resolution, and mobile states while retaining existing UI patterns.
- Replaced fixture/contact/SLA claims with content-spec-derived help guidance and retained workflow
  truth.
- Added the exact trusted-browser spec and mobile screenshot output path.
- Documented the contracts and the fail-closed grievance owner/TAT configuration in A-167.

## Traceability

- Requirement 1: `portal_communications.list_notices` classifies the authenticated member's direct
  communications. Issued NOCs and interest invoices expose only the portal download action, which
  resolves a member-owned communication and delegates to the central signed/audited document owner.
  Other communication types remain listed without inventing a document that their owner has not
  retained.
- Requirement 2: MP24 creates, lists, selects through the detail route, and renders status plus the
  borrower-safe resolution summary. `GrievanceWorkflow` excludes assignee, internal notes, document
  ids, recovery notes, and staff history from borrower projections.
- Requirement 3: MP23 consumes only direct-user notification records and uses optimistic
  `read_state_version` when marking read.
- Requirement 4: ten help-guide sections are derived from the cited content specification and reuse
  the existing cards, alerts, fields, badges, and responsive layout.
- Requirement 5: MP20 consumes own loan closure, NOC, security-return, and CDSL-item facts. Its NOC
  action uses the same portal notice download contract.
- Requirement 6: every backend query derives identity from the active portal account; focused tests
  prove foreign grievance/notification/notice/closure isolation. Frontend tests cover all required
  async states and the declared E2E uses a 390×844 viewport.

## TDD Evidence

Saved RED/GREEN logs:

- `evidence/terminal-logs/portal-grievances-red.log`
- `evidence/terminal-logs/portal-grievances-green.log`
- `evidence/terminal-logs/portal-notifications-red.log`
- `evidence/terminal-logs/portal-notifications-green.log`
- `evidence/terminal-logs/portal-notices-closure-red.log`
- `evidence/terminal-logs/portal-notices-closure-green.log`

## Validation

- Backend focused owner/API regressions: 32 passed.
- Frontend focused tests: 15 passed.
- Django system check and migration consistency: passed.
- TypeScript, ESLint, production build: passed.
- Diff whitespace, protected-file check: passed.
- Changed-line budget: 1,997 / 2,000.
- Trusted browser: product assertions did not run because Chromium exited during launch; the exact
  logs and bounded retry are retained. No screenshot is claimed.

## Two-Axis Review

### Standards

- Fixed: restored the approved amber MP20 treatment after review identified an unapproved dynamic
  success-colour variant.
- Judgment call: MP24 retains the existing three-column grid after removing fabricated contact/SLA
  content, leaving the data surface in the original two-column span.
- Pending trusted validation: the exact browser spec uses a real portal login and intercepted feature
  projections; API ownership is proven separately. The required two passing runs/PNG remain absent
  because browser launch failed.

### Spec

- Fixed: MP24 grievance selection now calls the detail endpoint rather than treating list transport
  as the only integration.
- Reviewer focus: deficiency, rejection, sanction, and reminder communication owners do not all
  provide a retained downloadable document, so the portal does not fabricate download actions.
- Reviewer focus: MP23 does not yet interpret heterogeneous notification `action_url` values as
  portal navigation.

## Substantive Next-Run Risks

- Operations must configure the grievance owner role and positive TAT before enabling portal
  grievance creation.
- Trusted validation must rerun the exact E2E twice and produce the declared mobile PNG.
- If validation requires downloads for every listed communication type, governance/owner modules
  must first expose the retained document identity for those types.

## Recommended Next Action

Run independent validation, including the authoritative backend lane and the exact trusted-browser
contract. Do not promote if the browser assertions fail after infrastructure launches.
