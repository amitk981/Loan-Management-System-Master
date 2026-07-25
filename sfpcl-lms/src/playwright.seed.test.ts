import { describe, expect, it } from 'vitest';

import { fixtureSeedCommands, requiredFixtureFamilies } from '../playwright.seed';

describe('Playwright fixture-family selection', () => {
  it('provisions every family for ordinary full-suite collection', () => {
    expect(requiredFixtureFamilies([])).toEqual(['staff', 'portal', 'epic009', 'critical']);
  });

  it('provisions only Epic 009 for its targeted trusted command', () => {
    expect(
      requiredFixtureFamilies(['e2e/epic-009-staff-disbursement-closure.e2e.spec.ts']),
    ).toEqual(['epic009']);
  });

  it('provisions all public-boundary fixture families for the critical UAT suite', () => {
    expect(
      requiredFixtureFamilies(['e2e/critical-uat-smoke.e2e.spec.ts']),
    ).toEqual(['staff', 'portal', 'epic009', 'critical']);
  });

  it('completes deterministic readiness preconditions before the critical public journey', () => {
    expect(
      fixtureSeedCommands('manage', ['e2e/critical-uat-smoke.e2e.spec.ts']),
    ).toContain(
      'manage seed_epic_009_e2e_fixture'
      + ' && manage seed_epic_009_e2e_fixture --make-ready'
      + ' && manage seed_epic_009_e2e_fixture --prepare-transfer'
      + ' && manage seed_critical_uat_e2e_fixture && ',
    );
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
