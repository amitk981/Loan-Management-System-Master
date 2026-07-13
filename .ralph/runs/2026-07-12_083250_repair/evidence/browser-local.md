# Local Browser Evidence

- Collection: PASS — one Chromium test collected from `e2e/member-governance-closure.e2e.spec.ts`.
- Launch: BLOCKED by the expected macOS sandbox denial:
  `MachPortRendezvousServer ... Permission denied (1100)`.
- No screenshot was fabricated. Ralph's declared `localhost-e2e-server` trusted acceptance runs the
  test twice outside this sandbox and owns all five screenshot artifacts and encoded baselines.
