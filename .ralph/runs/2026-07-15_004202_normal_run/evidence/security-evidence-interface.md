# Security / Legal Evidence Interface

## Executable dependency and lock direction

```text
security_instruments/views
        |
        v
processes.security_instrument_evidence
        |-- approvals: final sanction + assigned/read scope facts
        |-- legal_documents: checklist + current locked evidence facts
        `-- security_instruments: package, PoA, SH-4, CDSL policy owner

transaction lock order
  application/package -> retained security instrument -> legal document/checklist evidence
```

`security_instruments` imports neither approvals nor legal-documents executable code. Historical
migrations and Django string foreign-key labels remain because they preserve retained table/FK
identity; neither is an executable policy dependency. `legal_documents` may consume security
metadata as source §36.2 permits.

## Narrow evidence contract

The process issues one immutable `SecurityEvidenceAccess` containing only canonical owner
operations: approved facts, approval-read scope, Stage-4 scope, locked PoA/signature/SH-4/CDSL
evidence, and checklist projection. A caller cannot supply this access object to the process.
Security modules still decide applicability, exact ₹500 PoA stamp, maker-checker separation,
custody, pledge, replay, and terminal transitions.

Forged authority example:

```text
process.read_package(..., evidence_access=forged)
-> UncoordinatedEvidence("Caller-supplied evidence authority is forbidden.")
-> no actor/object lookup and no writes
```

Stale/cross-application example:

```text
process.update_poa(... legal ids from another application ...)
-> coordinator re-resolves locked legal owner rows for the package application
-> VALIDATION_ERROR / CONFLICT
-> no security, checklist, audit, version, or workflow success write
```

## Preserved public contracts

All §28 GET/POST/PATCH routes, request fields, success/action envelopes, errors, retained table ids,
masked reads, assigned-versus-unrelated read scope, and terminal replay behavior remain unchanged.
The coordinator is an internal seam and accepts no HTTP field. Read permission still grants no
mutation, reveal, download, invocation, release, checklist completion, or readiness.

## Shared evidence recorder

Package, PoA, SH-4, and CDSL audit/version/ordinary-workflow writes now cross one internal recorder.
It always adds actor role/team and request/IP/user-agent attribution and recursively redacts raw BO,
bank, cheque, PAN, and Aadhaar-like fields. Already-masked values remain reviewable. Terminal action
workflow events and consumed-document rows retain their existing identities and shapes.

## Race contract

Twice-run PostgreSQL acceptance covers PoA activation/downgrade, tri-party exact replay and changed
verification, SH-4 changed create/custody, and CDSL changed create/acceptance. Different material
payloads retain one terminal winner and no loser request in success audit/version evidence; exact
replays return the retained action identity without another material ledger write.
