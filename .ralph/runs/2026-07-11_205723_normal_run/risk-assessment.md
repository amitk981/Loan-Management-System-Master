# Risk Assessment

Risk level: High (owner standing approval; no veto recorded).

- Authentication and portal-boundary code is security-sensitive. The production change narrows an
  existing demo-only selector by removing the borrower role; it does not alter backend auth, token
  formats, credential handling, API contracts, persistence, or production styling.
- The red real-boundary test demonstrated the prior risk concretely: `VITE_ENABLE_DEMO_AUTH=true`
  could select a synthetic borrower and enter protected portal UI without portal credentials.
- Mitigation: unset/false/true module isolation now renders the actual App/RoleProvider boundary;
  the true case asserts no borrower identity, portal claims/actions, protected dashboard, or logout
  surface. Existing browser interactions assert zero calls for empty login, exactly one request for
  populated login, and local token/protected-content removal after failed-network logout.
- Residual risk: Chromium cannot launch under the coding sandbox's macOS Mach-port restrictions, so
  screenshots are not locally present. The declared trusted browser acceptance runs twice outside
  the sandbox and remains the final browser authority.
- No dependency, schema, backend, data migration, sensitive fixture, or external-service risk was
  introduced. No protected or forbidden path was modified.
