# Risk Assessment

Slice: `005C2-application-object-access-hardening`

Risk level: Medium.

Why: This changes authorization behavior for existing loan-application detail and mutating endpoints. The change is security-positive but can block actors who previously had only global permission and no application scope.

Controls:
- TDD red regression captured same-permission unrelated access returning `200` before the fix.
- Green tests cover read, patch, submit, and reference-generation object denials.
- Side-effect assertions cover no update/submit/reference success audit rows, workflow events, register rows, application references, or visible sequence advancement on denial.
- Existing missing-global-permission behavior remains `403 PERMISSION_DENIED`.
- Credit Manager credit-assessment-domain access is explicit and covered by test.
- No database migration and no frontend behavior changes.

Residual risk:
- Current assignment facts are limited to `created_by_user` and `received_by_user`; future queue/team assignment slices should replace or extend this with explicit assignment tables.
- No denial audit is written because the project has no existing application authorization-denial audit convention; A-038 records this.
