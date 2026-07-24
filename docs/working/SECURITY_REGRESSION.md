# Security and Privacy Regression Lane

Run from the repository root with the mandated backend interpreter:

```sh
/Users/amitkallapa/LMS/.ralph/venv/bin/python \
  sfpcl_credit/manage.py security_regression \
  --output security-regression-summary.json
```

The command executes the fixed source-control matrix in
`sfpcl_credit/security_regression/matrix.py`, isolated production-settings positive and negative
probes, a no-secret output check, `detect-secrets==1.5.0`, `pip-audit==2.10.1`, and npm
`10.8.2 audit`. Scanner versions are pinned in the executable lane policy because these tools are
not application dependencies approved by `DEPENDENCY_POLICY.md`; the runtime must provision the
exact executables. Dependency locks/pins are the scan inputs. A required scanner that is missing,
has the wrong version, cannot reach its advisory service, emits malformed output, or reports a
finding fails the lane. It is never converted to a skip.

The JSON result contains control pass/fail/skip counts, exact failing control IDs, approved skip
reasons (none currently), scanner versions, redacted scanner result metadata and report hashes,
production/no-secret checks, the complete control-to-test matrix, and a canonical SHA-256 over the
summary. Raw scanner output is deliberately excluded from the summary.

Production boot requires separate `SFPCL_SECRET_KEY`, `SFPCL_JWT_SIGNING_KEY`, field encryption,
and field lookup secrets. The JWT signing key falls back to the Django key only in non-production
development/test settings so existing local sessions remain compatible.

## Blocking findings exposed by 012F

| Finding ID | Control | Existing behavior | Required corrective boundary |
|---|---|---|---|
| `SECURITY-012F-LOGIN-RATE-LIMIT` | `SEC-AUTH-010` | Login does not expose an executable repeated-failure throttle/lockout proof. | Add bounded user/IP throttling with generic errors and denied-attempt audit evidence. |
| `SECURITY-012F-UPLOAD-FILENAME` | `SEC-WEB-004` | Document metadata retains the caller-provided filename; the storage adapter sanitises only its private storage name. | Reject or canonicalise traversal/control-character filenames at the public upload boundary and prove the returned/audited name is safe. |
| `SECURITY-012F-UPLOAD-CONTENT` | `SEC-WEB-005` | General and KYC upload paths do not consistently reject executable extensions/MIME mismatches. | Add one shared upload validation policy for permitted extension, MIME, size, and executable-content rejection. |

These are release-blocking findings, not silent skips. This test-focused slice does not implement
the unrelated product repairs or create corrective queue slices; the owner/orchestrator must route
them through the normal prepared-slice workflow.

## Controlled failure

`--force-failure <control-id>` exists only to prove command failure semantics. It accepts a known
matrix control ID, writes an exact failing summary, and exits non-zero. Unknown values are rejected
without being copied into output.
