# Review Packet: 2026-07-12_105158_normal_run

## Result
Complete pending independent Ralph validation.

## Changes and traceability

Witnesses now have optimistic versions, masked correction history, a governed detail PATCH, and
resource-owned actions. Application Detail consumes those actions and canonically refetches.

- S09 plus data-model §10.5/§29-§30 says identity is protected and verification evidence is
  governed. Code changes name/PAN/Aadhaar while freezing verification evidence, verified by
  `test_witness_correction_is_versioned_masked_audited_and_preserves_evidence`.
- Auth §12.2/§15.4/§26.4/§34 omits an exact update atom; A-069 records the narrow
  `members.witness.update` decision and independent identity editor rule.
- API §6-§8/§44 requires standard envelopes/resource actions. List/detail project six-field
  actions from the same permission/object evaluations used by writes.

## Gates

Frontend: 173 tests, typecheck, lint, build. Backend: 418 tests, check, migration sync, 94%
coverage. Playwright collects both governance tests. Ralph owns four screenshot outputs.

## Risk / rollback

High due to protected identity and authority. Migration is additive; roll back code then schema.
