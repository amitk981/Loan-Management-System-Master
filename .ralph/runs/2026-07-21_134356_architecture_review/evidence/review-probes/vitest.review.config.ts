import { fileURLToPath, URL } from 'node:url';

export default {
  root: fileURLToPath(new URL('../../../../../', import.meta.url)),
  test: {
    environment: 'node',
    include: [
      '.ralph/runs/2026-07-21_134356_architecture_review/evidence/review-probes/servicing-replay-review.test.ts',
    ],
  },
};
