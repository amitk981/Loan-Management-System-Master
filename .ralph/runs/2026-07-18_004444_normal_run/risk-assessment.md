# Risk Assessment

Risk level: High (change-request classification); Low production-behavior risk

- Selected slice: `CR-010-backend-pending-age-parallel-ci-flake`
- Mode: `normal_run`
- Independent Ralph validation is required before commit.

## Scope and controls

- No production model, service, endpoint, serializer, API shape, migration, permission, frontend,
  or source document changed.
- The approvals change is test-only. Explicit clock values make the previously intermittent
  10-to-11 and 2-to-3 second changes deterministic, while deep-copied payloads remove only
  `pending_age` before exact comparison.
- The sole dependency change is a pinned development/test package, `tblib==3.1.0`, already present
  in the Ralph virtual environment. It enables Django's documented remote traceback serialization
  path and is not installed as a production dependency.
- The infrastructure regression proves the requirements pin and an actual
  `RemoteTestResult` assertion/traceback pickle round trip.

## Residual risk

- The coding sandbox deliberately did not run the complete suite in parallel because the slice
  forbids repeating the non-authoritative Rosetta worker probe. The orchestrator's configured
  complete parallel coverage command remains the acceptance authority.
- A development dependency can affect CI environment resolution, mitigated by an exact existing
  version pin, `pip check`, the infrastructure class, and the independent install/coverage gates.
- Full-suite interactions outside the two impacted classes remain for the orchestrator's coverage
  gate; both directly impacted classes pass in full.
