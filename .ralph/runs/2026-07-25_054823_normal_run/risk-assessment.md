# Risk Assessment — 012DAB

## Rating

Medium, matching the prepared slice.

## Main Risks and Controls

- Export duplication: one attempt key is retained across request retries; a new key is created only
  when the user changes the owned report/register context.
- False download success: completed jobs without a download grant are labelled `finalizing` and
  remain refreshable; expired, failed, queued, and running jobs never render Download.
- Permission leakage: read-tab visibility uses canonical owner permissions, while every request,
  status read, and download remains backend-authoritative. 401/403 messages do not echo restricted
  backend detail.
- Sensitive leakage: the UI requests standard masked exports by default, does not request
  `sensitive_reason`, accepts only same-origin job-bound download capabilities, and never logs row
  values.
- Visual regression: the implementation reuses existing tabs, cards, table classes, alerts,
  badges, links, formatting, colours, and spacing. The page-local heterogeneous register
  composition is recorded as A-174.
- Scope/diff: no backend, schema, dependency, protected, source, state, or future-slice changes were
  made. The tracked product diff remains below the configured 2,000-line ceiling.
- Browser evidence: local Chrome aborted at process launch. No false screenshot exists; the exact
  three-test spec is left for authoritative trusted validation and two-run screenshot capture.

## Residual Risk

Trusted browser validation must still launch Chrome and produce both named screenshots twice.
The existing Vite chunk-size warning is unchanged and non-blocking.

