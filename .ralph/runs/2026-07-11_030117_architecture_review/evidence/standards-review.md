# Independent Standards Review

1. **High — action authority is bypassed.** `AppraisalWorkbench.tsx` unions
   `/auth/me.available_actions` with resource actions. The former is the user's permission list, so
   a resource returning no actions cannot hide a control; React's status/role checks remain workflow
   rules. This violates codebase-design §23.3-§23.4 and 006H2.
2. **High — required UI behavior coverage is absent.** `AppraisalWorkbench.test.tsx` only static-
   renders the view and injects callbacks; API tests invoke wrappers directly. The real container is
   never mounted/clicked, violating codebase-design §26.3 and 006H2.
3. **High — circular business-app dependency.** Credit imports approvals while the approvals
   handoff imports credit errors/access logic, violating codebase-design §36.2.
4. **Medium — nonstandard permission code.** Witness denial adds `PERMISSION_DENIED` although
   source API §7.1 defines `FORBIDDEN` for missing permission.
5. **Medium — authoritative assertions changed.** 006F4 replaced retired structured workflow
   assertions with weaker trigger-reason substring checks despite its no-change/no-weakening rule.

Judgement call: witness queryset/pagination/serialization composition in the HTTP view is shallow
and should move behind the application-owned module seam when 004E2 corrects the substantive
evidence defects.

