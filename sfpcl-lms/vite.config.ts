import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    // Unit tests live under src/. Playwright specs under e2e/ are run by
    // `npm run e2e`, never by vitest — keep vitest from importing @playwright/test.
    include: ['src/**/*.{test,spec}.{ts,tsx}'],
  },
})
