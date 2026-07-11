import { describe, expect, it } from 'vitest';
import source from './MP05_NewApplication.tsx?raw';

describe('MP05 loan-limit display authority (006Z2 interim regression)', () => {
  it('computes no loan limit client-side', () => {
    // Pre-fix the screen derived shareholdingLimit = sharesHeld * valuationPerShare
    // (the source formula is shares x 30% of valuation), hard-coded the land-based
    // limit, and gated submission on the local Math.min of the two.
    expect(source).not.toContain('landBasedLimit');
    expect(source).not.toContain('maximumPermissibleLimit');
    expect(source).not.toContain('675000');
    expect(source).not.toContain('shareholdingLimit');
  });

  it('explains that the limit is server-determined during credit assessment', () => {
    expect(source).toContain('determined by SFPCL during credit assessment');
  });
});
