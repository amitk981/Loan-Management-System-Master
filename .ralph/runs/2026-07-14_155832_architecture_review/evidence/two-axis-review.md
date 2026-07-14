# Two-Axis Independent Review

## Standards

- **Hard — serializer seam bypassed.** `legal_documents/views.py:123-235` passes raw JSON into
  modules; shape/type/format/enum validation lives in `stamp_notary.py:112-177` and
  `signatures.py:203-264`, contrary to codebase-design §§6.3-6.4. Both modules duplicate HTTP parsing.
- **Hard — nonstandard action response.** The §26.8 mismatch-resolution action returns resource
  metadata, omitting transition fields required by API-contracts §6.3.
- **Hard — dependency-direction drift.** `documents/services.py:233-271` puts Stage-4 legal policy —
  roles, legal category, application relationship, evidence purpose — inside the lower-level
  documents app, reversing codebase-design §§36.1-36.2 ownership.
- **Judgement — repeated canonical query.** `signatures.py:311-322` and
  `document_checklist.py:389-405` duplicate the same application-wide signature projection instead
  of one selector (codebase-design §37.2).
- **Judgement — private cross-module seam.** `processes/sanction_completion.py:11-19` calls
  underscored `approval_actions._approve_case_with_completion`; the public process interface is
  correct and tested, so no standalone rename slice was created.
- **Judgement — authority duplication.** Role checks are spread across `document_authority.py`,
  `signatures.py`, and `stamp_notary.py`, rather than hidden behind the permission interface (§9.1).

## Spec

1. **High — 008E leaks inaccessible signature existence.** The slice requires unrelated scope to
   be nondisclosing. Resolution fetches by raw signature id before application scope; the view maps
   absent to 404 and existing wrong-stage/inaccessible to 403. Tests omit this comparison.
2. **High — Compliance can record CS-owned adverse stamp/notary decisions.** 008D permits Compliance
   to prepare pending facts and makes CS the verifier. The code role-gates only `adequate` and
   `completed`, allowing unverified `insufficient` and `rejected` outcomes.
3. **Medium — signature concurrency acceptance is absent.** 008E requires concurrent duplicate/
   changed attempts to retain one outcome and complete history. Its suite is an ordinary `TestCase`
   with no transactional/threaded race.

No evidence-backed scope creep was found. M06-FR-012/M06-FR-014 remain later-owner work and were not
claimed complete in the reviewed slices.

## Independent integration addendum

The root review reproduced an additional High lifecycle defect: same-identity ordinary capture can
overwrite an unresolved mismatch as `signed`, bypassing the only authorized resolution action. It
also confirmed the adverse stamp authority defect with executable regressions. These findings are
incorporated into 008E2 and 008D2 respectively.

Summary: Standards found 3 hard issues and 3 judgement calls; the worst is legal policy reversing
the documents/legal-documents dependency direction. Spec found 2 High and 1 Medium issue in the
isolated pass; root integration added one High mismatch-lifecycle finding, the worst overall.
