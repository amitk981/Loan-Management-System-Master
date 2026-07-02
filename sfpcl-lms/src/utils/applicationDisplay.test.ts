import { describe, expect, it } from 'vitest';
import { getApplicationReference, getApplicationStatusLabel, hasFormalLoanReference } from './applicationDisplay';
import type { LoanApplication } from '../types';

const baseApp = {
  applicationNumber: 'APP-001',
  intakeReference: 'INTAKE-001',
  officialReference: 'LO00000001',
  source: 'member_portal',
} as unknown as LoanApplication;

describe('hasFormalLoanReference', () => {
  it('is false before completeness passes', () => {
    expect(hasFormalLoanReference({ ...baseApp, status: 'draft' } as LoanApplication)).toBe(false);
    expect(hasFormalLoanReference({ ...baseApp, status: 'completeness_check' } as LoanApplication)).toBe(false);
  });

  it('is true once a reference is generated', () => {
    expect(hasFormalLoanReference({ ...baseApp, status: 'reference_generated' } as LoanApplication)).toBe(true);
    expect(hasFormalLoanReference({ ...baseApp, status: 'sanctioned' } as LoanApplication)).toBe(true);
  });
});

describe('getApplicationReference', () => {
  it('uses the intake reference before the formal reference exists', () => {
    expect(getApplicationReference({ ...baseApp, status: 'draft' } as LoanApplication)).toBe('INTAKE-001');
  });

  it('uses the official reference after generation', () => {
    expect(getApplicationReference({ ...baseApp, status: 'sanctioned' } as LoanApplication)).toBe('LO00000001');
  });
});

describe('getApplicationStatusLabel', () => {
  it('maps workflow statuses to user-facing labels', () => {
    expect(getApplicationStatusLabel({ ...baseApp, status: 'submitted' } as LoanApplication)).toBe('Pending Completeness');
    expect(getApplicationStatusLabel({ ...baseApp, status: 'sanctioned' } as LoanApplication)).toBe('Sanctioned');
    expect(getApplicationStatusLabel({ ...baseApp, status: 'deficiency_raised' } as LoanApplication)).toBe('Returned for Rectification');
  });
});
