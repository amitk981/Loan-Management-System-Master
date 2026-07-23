# Risk Assessment

Risk level: Medium

## Security and data-scope risks

- Portal identity is derived only from an active `PortalAccount`; member ids are never accepted from
  the notice, grievance, notification, closure, or download caller.
- Notice/download queries require both the authenticated member id and a borrower/member recipient
  type. Notification queries require an exact direct `recipient_user`; role/team broadcasts are not
  exposed. Foreign grievance detail and notification identifiers are nondisclosing.
- The document endpoint accepts only a member-owned communication linked to an issued NOC or
  interest-invoice document, then delegates bytes to the central signed capability and download
  audit seam. The focused test proves the `documents.file.downloaded` audit.
- Residual risk: deficiency, rejection, sanction, and reminder owners do not all retain a
  communication-linked `DocumentFile`. Those communications are listed honestly, but no download
  action is fabricated when a governed document does not exist.

## Business-rule and operational risks

- The source supplies no universal grievance TAT or owner. Creation therefore requires the explicit
  `SFPCL_PORTAL_GRIEVANCE_TAT_DAYS` and `SFPCL_PORTAL_GRIEVANCE_OWNER_ROLE_CODE` values and an active
  member-scoped grievance reader. Missing configuration fails closed with
  `409 CONFIGURATION_REQUIRED`; existing grievance reads remain available.
- Closure projections consume retained closure, NOC, security-return, and CDSL-item facts. An absent
  CDSL item remains `pending`; it is never presented as `not_applicable` without retained evidence.
- Notification related-action navigation remains a reviewer-focus item. Direct notifications expose
  the owner-provided label/URL in the API, but MP23 currently uses the row interaction for safe
  mark-read behavior rather than interpreting heterogeneous staff/portal route strings.

## Validation and infrastructure risks

- Focused owner regressions, frontend behavior tests, typecheck, lint, build, Django checks,
  migration consistency, diff whitespace, protected-file, and changed-line gates pass.
- The declared Playwright spec exists at the exact required path and writes the exact required PNG.
  Chromium exited during launch before page creation on both the exact run and its bounded retry;
  the repeat infrastructure probe failed identically. No screenshot was fabricated. Ralph trusted
  validation must rerun the spec twice and produce `member-portal-communications-mobile.png`.
- The browser spec validates the complete mobile UI contract with a real portal login but intercepts
  the four feature projections. Backend ownership and cross-member behavior are instead proven by
  focused authenticated API tests; independent validation should decide whether the trusted-browser
  lane requires an expanded live-data seed.
