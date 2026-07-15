# Review Packet: 2026-07-14_124337_architecture_review

## Result

Success

## Slice and Range

Architecture review of `git diff 7d0106a6...87f2e93b`, covering completed slices 007T, 008B2,
008B3, and 008C. No production code changed.

## Standards

The isolated Standards pass found that checklist refresh rewrites the later completion lifecycle,
legal checklist facts cross directly into the members ORM and locally duplicate role/object policy,
checklist audit evidence drops mandatory request/actor context, and authorized unknown generation/
list parents use 400 instead of standard 404. A-104's state-dependent shared GET and A-102/A-104's
null-only future FKs were reviewed as explicit staged exceptions rather than newly live drift.

## Spec

The isolated Spec pass found that automatic checklist creation remains optional for direct final-
approval callers, the PostgreSQL test races refresh rather than sanction completion, refresh can
erase completion owned by later slices, and a pending cheque default is treated as a verified match.
Integration review additionally found that legacy pre-008B3 output has no immutable renderer
provenance and can satisfy exact replay/checklist selection before current validation.

## Traceability and Architecture Outcome

- M06-FR-001 says the checklist is automatic; 008C's optional lower-level hook does not establish
  that invariant. 008C2 makes the terminal coordinator mandatory and proves a true sanction race.
- Data-model §16.5 and 008C requirement 4 separate applicability from completion; 008C2 preserves
  completed/verified facts and conflicts rather than reopening them.
- Codebase-design §36.2 excludes a direct `legal_documents -> members` dependency; 008C2 consumes an
  owner-facing fact seam and one canonical object authority decision.
- Functional §15.1/M06-FR-013 require genuine legal output. 008B3 proves new output; 008B4 makes
  renderer provenance immutable and legacy replay/remediation honest.
- API §7.5 fixes 404 for absent resources; 008B4 adds the omitted authorized-unknown matrix.
- 007T's legacy-null and newest-request tests, 008B2's authority/selector/migration work, and 008B3's
  Unicode/extracted-content/bounds evidence remain substantive.

## Corrective Queue

1. 008B4 renderer provenance and replay contract closure — unblocked after complete 008B3.
2. 008C2 checklist lifecycle, authority, and side-effect closure — depends on 008B4 and complete 008C.
3. 008D stamp/notary tracking — now depends on 008C2 and is sharpened for both corrected seams.

No Blocked slice was stale. No ADR was required because existing codebase rules and A-104/A-105
already decide the architecture/intentional deferrals.

## Validation

- Frontend build, typecheck, lint, and 293/293 tests pass.
- Django check and migration sync pass.
- Backend 746/746 tests pass with 23 expected PostgreSQL-only skips.
- Coverage is 93%, exceeding the 85% floor.
- Queue drain, state JSON, `git diff --check`, protected paths, and review-only scope pass.

## Recommended Next Action

Run 008B4, then 008C2. Continue to 008D only after both corrections pass.
