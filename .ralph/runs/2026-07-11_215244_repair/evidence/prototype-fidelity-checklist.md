# Prototype Fidelity Checklist

- PASS: No production JSX, CSS, color, typography, spacing, card, badge, table, or layout changes.
- PASS: The existing S12 queue/detail/category/item/document composition is unchanged.
- PASS: Frontend changes are limited to the six-field action type and test/browser fixtures.
- PASS: The routed container still consumes backend `enabled` and `disabled_reason`; no workflow,
  reference, deficiency, rejection, or permission rule was added to React.
- PASS: Existing 150-test frontend suite, lint, typecheck, and production build are green.
- PASS: The trusted spec captures all nine declared names through the default routed container and
  derives every path from `RALPH_EVIDENCE_DIR`.
- LOCAL ENVIRONMENT NOTE: Chromium was denied macOS Mach-port registration before the test body.
  No screenshot was fabricated. The independent orchestrator runs the trusted contract twice and
  decides screenshot acceptance.
