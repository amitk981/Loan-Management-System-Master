import { defineConfig, devices } from '@playwright/test';
import path from 'path';

// This config lives in sfpcl-lms/. The Django backend is one level up.
const repoRoot = path.resolve(__dirname, '..');

const ralphWorktreeSegment = `${path.sep}.ralph${path.sep}worktrees${path.sep}`;
const requiredDjangoPython = repoRoot.includes(ralphWorktreeSegment)
  ? path.resolve(repoRoot, '..', '..', 'venv', 'bin', 'python')
  : path.resolve(repoRoot, '.ralph', 'venv', 'bin', 'python');

// The operator's Python interpreter for the backend must be explicit. Falling
// back to python/python3 can target the wrong environment and seed the wrong DB.
const djangoPython = process.env.E2E_DJANGO_PYTHON;
if (!djangoPython) {
  throw new Error(
    `E2E_DJANGO_PYTHON is required. Set it to the Ralph venv interpreter, for example: ${requiredDjangoPython}`,
  );
}

// Isolated sqlite DB for the E2E dev server so the suite never touches the
// default local dev DB. settings.py honours SFPCL_DB_PATH.
const e2eDbPath = process.env.SFPCL_DB_PATH || path.join(repoRoot, 'sfpcl_credit', 'e2e.sqlite3');
const e2eStorageRoot =
  process.env.SFPCL_DOCUMENT_STORAGE_ROOT ||
  path.join(process.env.TMPDIR || '/tmp', 'sfpcl-e2e-document-storage', path.basename(repoRoot));

const manage = `"${djangoPython}" sfpcl_credit/manage.py`;

export default defineConfig({
  testDir: './e2e',
  testMatch: '**/*.e2e.spec.ts',
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: 0,
  workers: 1,
  reporter: [['list']],
  use: {
    baseURL: 'http://localhost:5173',
    timezoneId: 'Asia/Kolkata',
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  webServer: [
    {
      // Backend: migrate a fresh isolated DB, seed the role catalogue and the
      // deterministic E2E staff users, then serve the real API. The DB file is
      // deleted first so entity sequence numbers (MEM-000001, ...) are identical
      // every run — screenshot baselines depend on that determinism.
      command:
        `rm -f "${e2eDbPath}" && mkdir -p "${e2eStorageRoot}" && ` +
        `find "${e2eStorageRoot}" -type f -delete && ` +
        `${manage} migrate --noinput && ` +
        `${manage} seed_role_catalogue && ` +
        `${manage} seed_e2e_users && ` +
        `${manage} seed_portal_e2e_fixture && ` +
        `${manage} runserver 127.0.0.1:8000 --noreload`,
      cwd: repoRoot,
      url: 'http://127.0.0.1:8000/api/v1/health/ready/',
      timeout: 120_000,
      reuseExistingServer: !process.env.CI,
      env: {
        SFPCL_DB_PATH: e2eDbPath,
        SFPCL_DOCUMENT_STORAGE_ROOT: e2eStorageRoot,
        SFPCL_DEBUG: 'true',
        SFPCL_ALLOW_E2E_SEED: 'true',
      },
    },
    {
      // Frontend: production auth path only (VITE_ENABLE_DEMO_AUTH is left unset).
      command: 'npm run dev',
      cwd: __dirname,
      url: 'http://localhost:5173',
      timeout: 120_000,
      reuseExistingServer: !process.env.CI,
      env: {
        VITE_API_BASE_URL: 'http://127.0.0.1:8000',
      },
    },
  ],
});
