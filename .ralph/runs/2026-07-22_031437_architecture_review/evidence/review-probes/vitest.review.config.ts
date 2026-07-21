import { fileURLToPath, URL } from 'node:url';

export default {
  root: fileURLToPath(new URL('../../../../../', import.meta.url)),
  test: {
    environment: 'node',
    include: [
      '.ralph/runs/2026-07-22_031437_architecture_review/evidence/review-probes/product-boundary-review.test.ts',
    ],
  },
};
