// @vitest-environment jsdom
import React from 'react';
import { cleanup, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { RoleProvider } from '../../../../contexts/RoleContext';
import { storedAuthSession } from '../../../../services/authSession';
import MP05_NewApplication from './MP05_NewApplication';
import source from './MP05_NewApplication.tsx?raw';
import browserContract from '../../../../../e2e/portal-application-limit-authority.e2e.spec.ts?raw';

const storage = new Map<string, string>();

beforeEach(() => {
  vi.stubGlobal('localStorage', {
    getItem: vi.fn((key: string) => storage.get(key) ?? null),
    setItem: vi.fn((key: string, value: string) => storage.set(key, value)),
    removeItem: vi.fn((key: string) => storage.delete(key)),
  });
  storage.clear();
  storedAuthSession({ accessToken: 'portal-token', refreshToken: 'refresh-token' });
});

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe('MP05 loan-limit display authority (006Z2 interim regression)', () => {
  it('keeps the trusted browser portal-entry fixture renderable before using the dashboard action', () => {
    for (const requiredMemberField of [
      'member_type',
      'folio_number',
      'membership_status',
      'kyc_status',
      'default_status',
      'share_summary',
      'active_member_status',
    ]) {
      expect(browserContract).toContain(requiredMemberField);
    }
    expect(browserContract).toContain(
      "getByRole('button', { name: 'New Loan Application', exact: true })",
    );
  });

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
    expect(source).toContain('PortalApplicationLimitView');
  });

  it('renders the approved three-card composition and server advisory only from the mounted projection', async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(ok({ member: {}, nominees: [], shareholdings: [], land_holdings: [], crop_plans: [], bank_accounts: [], cancelled_cheques: [], kyc_profile: null }))
      .mockResolvedValueOnce(ok({
      status: 'available', unavailable_reason: null,
      shareholding_based_limit_amount: '150000.00', land_based_limit_amount: '90000.00',
      final_eligible_loan_amount: '90000.00', requested_amount: '95000.00',
      amount_within_limit_flag: false, exception_required_flag: true,
      calculated_as_of_date: '2026-07-13', calculation_rule_version: 'portal-limit-v1',
    }));
    vi.stubGlobal('fetch', fetchMock);
    render(<RoleProvider><MP05_NewApplication onNavigateToApplication={vi.fn()} /></RoleProvider>);
    await screen.findByRole('button', { name: 'Continue' }).then(button => button.click());

    expect((await screen.findByText('Shareholding Limit')).parentElement?.textContent).toContain('₹1,50,000');
    expect(screen.getByText('Land-Based Limit').parentElement?.textContent).toContain('₹90,000');
    expect(screen.getByText('Maximum Permissible Limit').parentElement?.textContent).toContain('₹90,000');
    expect(screen.getByText(/configured exception\/credit workflow/i)).toBeTruthy();
  });

  it('mounts the real container with one borrower-scoped projection GET and no client fallback', async () => {
    const fetchMock = vi.fn((input: string | URL | Request) => Promise.resolve(
      String(input).includes('application-limit-projection')
        ? ok({ status: 'unavailable', unavailable_reason: 'verified_active_member_authority_not_available', shareholding_based_limit_amount: null, land_based_limit_amount: null, final_eligible_loan_amount: null, requested_amount: '500000.00', amount_within_limit_flag: null, exception_required_flag: null, calculated_as_of_date: null, calculation_rule_version: null })
        : ok({ member: {}, nominees: [], shareholdings: [], land_holdings: [], crop_plans: [], bank_accounts: [], cancelled_cheques: [], kyc_profile: null }),
    ));
    vi.stubGlobal('fetch', fetchMock);

    render(
      <React.StrictMode>
        <RoleProvider><MP05_NewApplication onNavigateToApplication={vi.fn()} /></RoleProvider>
      </React.StrictMode>,
    );

    await screen.findByRole('button', { name: 'Continue' }).then(button => button.click());
    await screen.findByText('Limit not yet available');
    await waitFor(() => expect(fetchMock.mock.calls.filter(
      ([input]) => String(input).includes('application-limit-projection'),
    )).toHaveLength(1));
    expect(fetchMock.mock.calls.filter(
      ([input]) => String(input).includes('application-limit-projection'),
    )[0]).toEqual([
      'http://127.0.0.1:8000/api/v1/portal/application-limit-projection/?requested_amount=500000',
      expect.objectContaining({ method: 'GET' }),
    ]);
    expect(source).not.toContain('sharesHeld *');
    expect(source).not.toContain('Math.min');
    expect(source).not.toContain('formatMoney');
    expect(source).not.toContain('export const PortalApplicationLimitView');
    expect(source).not.toContain('loadLimitProjection(500000)');
  });
});

function ok(data: unknown): Response {
  return { ok: true, status: 200, json: async () => ({ success: true, data, meta: {} }) } as Response;
}
