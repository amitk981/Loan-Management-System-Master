# Validation Failure Summary

The validator was stopped before full gates because the trusted outside-sandbox Playwright loop
proved the documentation spec green and exposed one remaining exact assertion mismatch in the
deficiency spec.

## Remaining demonstrated browser failure

- `member-portal-deficiency-response.e2e.spec.ts:50`
  - After `Resubmit corrections`, the routed application refresh succeeds and MP11 unmounts, but
    `getByText('submitted', { exact: true })` times out because the rendered status badge is
    presentation-cased (`Submitted`).
  - Assert the uniquely scoped rendered submitted status or another canonical returned-to-review
    surface without weakening the following assertion that the exact Deficiency Response heading is gone.

Preserve all four earlier selector repairs. The documentation spec already passes. Run the exact
two-spec command as the focused feedback loop before allowing full validation.
