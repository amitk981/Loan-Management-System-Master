import { describe, expect, it } from 'vitest';

import { requiredFixtureFamilies } from '../playwright.seed';

describe('Playwright fixture-family selection', () => {
  it('provisions every family for ordinary full-suite collection', () => {
    expect(requiredFixtureFamilies([])).toEqual(['staff', 'portal', 'epic009']);
  });

  it('provisions only Epic 009 for its targeted trusted command', () => {
    expect(
      requiredFixtureFamilies(['e2e/epic-009-staff-disbursement-closure.e2e.spec.ts']),
    ).toEqual(['epic009']);
  });

  it('provisions the union when Epic 009 and another spec are selected', () => {
    expect(
      requiredFixtureFamilies([
        'e2e/epic-009-staff-disbursement-closure.e2e.spec.ts',
        'e2e/member-portal.e2e.spec.ts',
      ]),
    ).toEqual(['staff', 'portal', 'epic009']);
  });
});
