import { defineConfig, devices } from '@playwright/test';
import path from 'path';

// This config lives in sfpcl-lms/. The Django backend is one level up.
const repoRoot = path.resolve(__dirname, '..');

// The operator's Python interpreter for the backend (use the project venv, see
// e2e/README.md). Defaults to `python` on PATH.
const djangoPython = process.env.E2E_DJANGO_PYTHON || 'python';

// Isolated sqlite DB for the E2E dev server so the suite never touches the
// default local dev DB. settings.py honours SFPCL_DB_PATH.
const e2eDbPath = process.env.SFPCL_DB_PATH || path.join(repoRoot, 'sfpcl_credit', 'e2e.sqlite3');

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
      // deterministic E2E staff users, then serve the real API.
      command:
        `${manage} migrate --noinput && ` +
        `${manage} seed_role_catalogue && ` +
        `${manage} seed_e2e_users && ` +
        `${manage} runserver 127.0.0.1:8000 --noreload`,
      cwd: repoRoot,
      url: 'http://127.0.0.1:8000/api/v1/health/ready/',
      timeout: 120_000,
      reuseExistingServer: !process.env.CI,
      env: {
        SFPCL_DB_PATH: e2eDbPath,
        SFPCL_DEBUG: 'true',
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
