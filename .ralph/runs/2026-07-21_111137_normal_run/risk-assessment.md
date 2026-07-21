# Risk Assessment

Risk level: High

- Selected slice: 010MA-servicing-account-and-repayment-frontend-wiring
- Mode: normal_run
- Manual review required: independent Ralph validation under the standing owner approval.

## Material Risks and Controls

- Financial truth divergence: schedule, ledger, receipt, allocation, statement-match, and subsidiary
  values are rendered from canonical decimal-string projections. The frontend performs no balance,
  allocation, or match calculation; exact Money formatting avoids JavaScript number coercion.
- Duplicate movement or replay: every direct capture receives one caller-stable idempotency key, the
  allocation derives a stable child key, and an exact capture replay stops before SAP/allocation so
  no second client mutation is issued. Validation and duplicate conflicts are visible with no retry
  or canonical refresh.
- Authority widening: combined posting requires an active `credit_manager` or `accounts_head` role
  and all three canonical create/SAP/allocation permissions. Backend reads retain canonical role,
  permission, object-scope, and nondisclosing 404 checks.
- Cross-loan or stale evidence: request sequence ownership prevents older ledger/repayment and
  statement responses from replacing a newer account/page. Each statement status owns truthful
  pagination, and account changes reset schedule/ledger pages.
- Projection leakage: the new repayment collection excludes remarks/narration and exposes only the
  retained allocation, SAP, statement relationship, and subsidiary reconciliation facts required by
  S44/S45.

## Change Bounds

- 19 product/documentation files; 1,708 changed product lines, below the configured 2,000-line hard
  limit. The increase beyond the 1,450 planning target came from bounded independent-review
  regressions and proof closure; 010MB interest/monitoring scope remains excluded.
- No database migration, dependency, package installation, protected-file edit, or source-document
  edit was introduced.

## Residual Validation Risk

- Local Playwright collection succeeds with the exact two declared scenarios. Chromium aborts with
  `SIGABRT` at sandboxed browser launch before test bodies execute, so local screenshots were not
  fabricated. The required out-of-sandbox twice-run browser contract and screenshots remain for the
  orchestrator's authoritative validation.
- The production build retains the repository's existing large-chunk warning; build completion is
  successful and this slice adds no dependency.
