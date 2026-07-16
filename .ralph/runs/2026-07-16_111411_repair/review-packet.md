# Review Packet: 2026-07-16_111411_repair

## Result

Ready for independent Ralph validation.

## Slice

009B2-sap-delivery-replay-audit-and-owner-seam-closure

## Diagnosis and repair

The retained review probes proved two exact defects: `sent` produced no assignee workbook path, and
a reused-code completion accepted newly added optional fields as HTTP 200 replay. The new public SAP
owner/manual adapter requires exact decrypted workbook acceptance before `sent`, provides a signed
one-use assignee capability, and freezes a supplied/omitted-aware completion digest.

## Traceability

- The source says manual SAP handoff includes the Excel and is owned by the frozen Senior Manager
  Finance (`integrations.md` §§8.1-8.5). The code delivers exact retained bytes behind the manual
  adapter/capability boundary, verified by
  `test_sent_assignee_reads_exact_retained_workbook_through_delivery_capability` and the capability
  matrix tests.
- The source defines `sap_workflow.modules.sap_customer_profile` and one Manual/Fake/Future adapter
  seam (`codebase-design.md` §§16.1/20.3-20.4/36.2). The installed public owner, adapter contract,
  downstream decision, and dependency guards are verified by
  `test_manual_and_fake_adapters_share_the_public_contract` and
  `test_http_and_downstream_dependencies_use_public_sap_owner`.
- The source requires exact assigned-Finance confirmation, uniqueness/reuse, and stored member/
  application linkage (BR-047-050, M07-FR-001-008). Existing locks/constraints remain; the canonical
  digest closes changed optional replay, verified by
  `test_reuse_changed_optional_payload_conflicts_without_loser_artifacts` and twice-run PostgreSQL
  request/code/member races.
- The source mandates `sap.customer_code_created` plus actor role/team and complete safe audit context
  (`auth-permissions.md` §§30.1-30.3). New/reuse/read/capability/download/denial matrices and recursive
  secret scans are verified by `test_create_send_complete_read_and_download_audits_freeze_safe_context`.

## Changed boundaries

- Public owner and adapter: `sfpcl_credit/sap_workflow/`.
- Existing Finance tables gain delivery reference/checksum/snapshot, capability version/expiry/
  consumption, and completion digest through one migration.
- New authenticated capability issue and binary Annexure-I download routes; existing create/send/
  complete/masked-read routes retain standard envelopes.
- API contracts, Epic 009 M07 traceability, and 009C/009D owner-consumption requirements are updated.

## Validation

- RED: `evidence/terminal-logs/sap-contract-red.log`.
- GREEN: 51 focused SAP tests, Django check, migration drift, two PostgreSQL race passes, 980 backend
  tests with 51 expected skips at 91% coverage, frontend build/typecheck/lint, and 322 frontend tests.
- Sanitized examples and ownership/migration notes: `evidence/sap-contract-evidence.md`.

## Recommended Next Action

Run independent Ralph validation, commit/merge/push only if green, then execute sharpened 009C.
