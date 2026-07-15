# Risk Assessment

Risk level: High

## Why this is high risk

The slice changes reversible protection for BO accounts, lookup hashes, retained-row migration,
sensitive reveal authority/object scope/rate/expiry/audit behavior, and nullable legal evidence.
Defects could disclose plaintext, make retained rows unreadable, bypass object scope, allow repeated
reveals, or accept terminal CDSL truth without evidence.

## Controls and residual risk

- AES-256-GCM authenticates ciphertext plus field/version/length/last-four metadata; current and
  explicitly previous key versions are the only decryptable versions.
- Encryption and lookup keys are dedicated settings and fail closed; tests remove both and prove
  changing `SECRET_KEY` cannot restore encryption.
- The former reversible helper is deleted from production. Its decryptor exists only in the data
  migration, which reconciles count, lookup hash, and last four before completing.
- The central sensitive owner validates payload, permission/role, canonical object scope, rate,
  expiry, and re-auth policy and writes plaintext-free success/denial audit. Reveal is serialised by
  the pledge lock and the HTTP response is no-store/no-cache.
- Security ordinary evidence remains separately redacted. An AST gate finds no executable
  security import of documents/legal/approvals.
- Pending null evidence is covered through public POST/PATCH; terminal null acceptance is a
  zero-terminal-write validation failure. Invocation, unpledge, balances, checklist completion,
  and readiness remain untouched.

Residual execution risk is the newly pinned dependency not being importable in the agent sandbox.
The backend and PostgreSQL gates must run after orchestrator dependency installation; logs record
the exact fail-closed import error. Standing owner approval applies and the veto list is empty.
