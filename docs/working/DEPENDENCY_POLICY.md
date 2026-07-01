# Dependency Policy

New dependencies are not allowed by default during Ralph AFK runs.

An agent may add a dependency only when:
- Existing tools cannot reasonably solve the problem.
- The dependency is necessary for the selected slice.
- The package is maintained.
- The license is acceptable.
- The security and bundle-size risks are low.
- The reason is documented in the run summary or an ADR.

Any dependency addition is at least Medium risk. Large frameworks, auth systems, ORMs, payment libraries, state-management libraries, or production infrastructure packages require human review.
