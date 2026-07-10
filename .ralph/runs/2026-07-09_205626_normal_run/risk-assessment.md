# Risk Assessment

Selected slice: `005F-deficiency-creation-and-resolution`

Risk level: Medium.

## Risk Drivers

- Adds one non-destructive database table and migration for application deficiencies.
- Adds staff mutation endpoints that affect application completeness status and audit/workflow
  evidence.
- Touches shared loan-application service/view code used by prior slices.
- No frontend behavior changed in this slice.

## Controls

- Return action is limited to submitted applications without a generated reference or register row.
- Deficiency item codes must match current 005E blocking checklist facts.
- Permission order follows existing application endpoints: auth, global permission, `404`, object
  scope, then validation/state.
- Out-of-scope actors create no deficiency, audit, workflow, register, reference, or sequence side
  effects.
- Successful return sets `completeness_status = incomplete` while keeping
  `application_status = submitted`; it does not generate `LO...` references or advance to credit
  assessment.
- Audit and response payloads are metadata-only; tests assert sensitive values and document storage
  keys are absent.

## Residual Risk

- A-040 records that 005F accepts `items[].item_code` rather than source §19.7 `deficiency_ids`
  because this slice creates the first deficiency records from 005E blocking facts.
- Real borrower response/re-upload, application resubmission, and communication delivery are
  deferred to later slices.
