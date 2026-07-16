# Focused Green Evidence

- Seed-to-staff-workspace HTTP regression: 1 passed.
- Affected backend files: 39 tests passed, 8 expected skips.
- DocumentationHub frontend: 16 tests passed.
- Playwright collection: one Chromium test collected from
  `e2e/staff-documentation-workspace.e2e.spec.ts`.

Local browser execution reached launch and then stopped before page creation with the documented
macOS sandbox error:

```text
FATAL mach_port_rendezvous ... bootstrap_check_in ... Permission denied (1100)
```

No screenshot was fabricated; independent browser validation remains authoritative.
