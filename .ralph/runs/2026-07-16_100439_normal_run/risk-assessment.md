# Risk Assessment

Risk level: High (as declared by slice 008M4).

## Material risks and controls

- Cross-domain authority drift: action decisions/execution now live behind owner-issued callbacks;
  AST guards reject process imports in owner adapters and reject concrete owner executors/payload
  reconstruction in the composition root.
- Stale or caller-forged actions: 008M3 opaque actor/application/snapshot HMAC binding and current
  locked re-read remain; stale/tampered actions are nondisclosing and zero-write.
- Queue amplification or disclosure: approval-owned scope is applied before count/page projection;
  tests add forty inaccessible rows and retain the same count and query cost.
- Invented legal identity: no governed PoA attorney selector exists, so A-125 withholds creation
  rather than selecting an arbitrary Company Secretary.
- Frontend auth/error drift: all JSON, pagination, multipart, and blob calls now share the session,
  request-id, refresh, and structured-envelope transport.
- Visual regression: the invented facts grid is removed and no new styling was added. Local Chromium
  cannot acquire macOS bootstrap services, so the orchestrator's twice-run five-screenshot contract
  remains authoritative; no screenshot was fabricated.

No dependency, migration, database constraint, external integration, or public API-shape change was
introduced. Standing high-risk approval applies and is not revoked.
