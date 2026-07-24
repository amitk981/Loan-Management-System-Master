# Release Promotion (Owner Runbook)

Decided by the owner on 2026-07-03. This replaces the old model where the loop pushed
straight to `main`.

## The model in one picture

```
agents (Ralph loop) ──▶ staging ──▶ [owner reviews + promotes] ──▶ main ──▶ production
```

- **Agents own `staging`.** Every completed slice is merged into `staging` and pushed to
  GitHub automatically. Agents are blocked from touching `main`: `ralph-run.sh` refuses to
  run unless `staging` is checked out, and it only ever pushes `staging`.
- **The owner owns `main`.** Nothing reaches `main` — and therefore production — except by
  your explicit promotion. This matches deployment-ops.md §11.5 (release approval before
  production).

## How to promote (day-to-day, ~1 minute)

1. Open the repository on GitHub (`Loan-Management-System-Master`).
2. Click **Pull requests → New pull request**. Set base: `main`, compare: `staging`.
3. Create the pull request and wait for the **CI checks to turn green** (frontend and
   backend gates run automatically on every pull request).
4. Skim the description of what changed (the commit list names each slice).
5. For a field-key rotation, verify the custody, reconciliation, rollback, and backup-retention
   evidence in `docs/working/FIELD_ENCRYPTION_OPERATIONS.md` before merging.
6. Click **Merge pull request**. That is the release.

If checks are red, do not merge. Nothing is broken by waiting — staging simply holds the
work until a repair slice fixes it.

## One-time setup on GitHub (do once, ~10 minutes)

In the GitHub repository → **Settings → Branches → Add branch protection rule** for `main`:

- Require a pull request before merging.
- Require status checks to pass before merging (select the `frontend` and `backend` checks).
- Do not allow bypassing the above.

After this, even an accidental direct push to `main` is rejected by GitHub itself — the
safety no longer depends on anyone following rules.

## One-time setup on Netlify (do once, ~5 minutes)

In the Netlify site settings → **Build & deploy → Branches**:

- Production branch: `main` (only your promotions deploy the live site).
- Branch deploys: add `staging`. Netlify then publishes every staging update to its own
  preview URL (e.g. `staging--<site-name>.netlify.app`) so you can click through the app
  and see agent work live *before* promoting it.

## If a promotion goes wrong

1. On the merged pull request page, click **Revert**. Merge the revert pull request —
   production is back to the previous state within minutes.
2. Netlify alternative: site → **Deploys** → pick the previous deploy → **Publish deploy**
   (instant rollback of the live site without touching git).
3. File the bug as a change request (`docs/change-requests/`) so the fix flows through the
   normal gated pipeline. Never hot-fix `main` by hand.

## Rules

- Never push to `main` from a terminal — promotion happens only through GitHub pull requests.
- Never merge a red pull request.
- Promotion is one-way: `staging → main`. Do not merge `main` back into `staging`; if the
  branches ever disagree, ask an agent to diagnose before acting.
