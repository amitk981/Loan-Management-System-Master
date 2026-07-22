import { fileURLToPath, URL } from 'node:url';

export default {
  root: fileURLToPath(new URL('../../../../../', import.meta.url)),
  test: {
    environment: 'node',
    include: [
      '.ralph/runs/2026-07-22_055158_architecture_review/evidence/review-probes/terminal-repair-review.test.ts',
    ],
  },
};
