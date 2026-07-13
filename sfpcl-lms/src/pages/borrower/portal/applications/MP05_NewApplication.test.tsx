// @vitest-environment jsdom
import React from 'react';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
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
    expect(screen.getByText('As of 2026-07-13 · Rule portal-limit-v1')).toBeTruthy();
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

  it('creates, submits exactly once, and canonically refetches the returned amount', async () => {
    const profile = { member: {}, nominees: [{ nominee_id: 'nominee-1', nominee_name: 'Adult Nominee', relationship_to_borrower: 'spouse', age_at_application: 40, pan: { masked: null }, aadhaar: { masked: null }, kyc_status: 'verified' }], shareholdings: [], land_holdings: [], crop_plans: [], bank_accounts: [], cancelled_cheques: [], kyc_profile: null };
    const projection = { status: 'available', unavailable_reason: null, shareholding_based_limit_amount: '150000.00', land_based_limit_amount: '90000.00', final_eligible_loan_amount: '90000.00', requested_amount: '500000.00', amount_within_limit_flag: false, exception_required_flag: true, calculated_as_of_date: '2026-07-12', calculation_rule_version: 'stored-v1' };
    const application = { loan_application_id: 'application-1', required_loan_amount: '475000.00', application_status: 'draft' };
    const submitted = { ...application, application_status: 'submitted' };
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(ok(profile))
      .mockResolvedValueOnce(ok(projection))
      .mockResolvedValueOnce(ok(application))
      .mockResolvedValueOnce(ok(submitted))
      .mockResolvedValueOnce(ok({ ...projection, requested_amount: '475000.00' }));
    vi.stubGlobal('fetch', fetchMock);
    render(<RoleProvider><MP05_NewApplication onNavigateToApplication={vi.fn()} /></RoleProvider>);
    await screen.findByRole('button', { name: 'Nominee' }).then(button => button.click());
    fireEvent.change(await screen.findByRole('combobox'), { target: { value: 'nominee-1' } });
    fireEvent.click(screen.getByRole('button', { name: 'Documents' }));
    screen.getAllByRole('button', { name: 'Mark Uploaded' }).forEach(button => button.click());
    screen.getAllByRole('button', { name: 'Self-attested?' }).forEach(button => button.click());
    fireEvent.click(screen.getByRole('button', { name: 'Declarations' }));
    screen.getAllByRole('checkbox').forEach(box => box.click());
    fireEvent.click(screen.getByRole('button', { name: 'Review' }));
    fireEvent.click(screen.getByRole('button', { name: 'Submit Application' }));
    await screen.findByText('Application submitted for completeness check');

    const calls = fetchMock.mock.calls.map(([url, options]) => ({ url, method: options.method, body: options.body ?? null }));
    expect(calls.slice(2)).toEqual([
      { url: 'http://127.0.0.1:8000/api/v1/portal/applications/', method: 'POST', body: JSON.stringify({ nominee_id: 'nominee-1', required_loan_amount: '500000', declared_purpose: 'crop production', purpose_category: 'crop_production', loan_type_requested: 'short_term', borrower_request_notes: 'Grapes Kharif 2026', terms_acceptance_flag: true }) },
      { url: 'http://127.0.0.1:8000/api/v1/portal/applications/application-1/submit/', method: 'POST', body: '{}' },
      { url: 'http://127.0.0.1:8000/api/v1/portal/application-limit-projection/?requested_amount=475000', method: 'GET', body: null },
    ]);
  });

  it('shows independent 400, 403, and 409 errors without retry or projection refetch', async () => {
    for (const row of [
      { status: 400, code: 'VALIDATION_ERROR', message: 'Enter a valid amount.', field: true, submit: false },
      { status: 403, code: 'OBJECT_ACCESS_DENIED', message: 'Application access is denied.', field: false, submit: false },
      { status: 409, code: 'INVALID_STATE_TRANSITION', message: 'Application can no longer be submitted.', field: false, submit: true },
    ]) {
      cleanup();
      const profile = { member: {}, nominees: [{ nominee_id: 'nominee-1', nominee_name: 'Adult Nominee', relationship_to_borrower: 'spouse', age_at_application: 40, pan: { masked: null }, aadhaar: { masked: null }, kyc_status: 'verified' }], shareholdings: [], land_holdings: [], crop_plans: [], bank_accounts: [], cancelled_cheques: [], kyc_profile: null };
      const projection = { status: 'available', unavailable_reason: null, shareholding_based_limit_amount: '150000.00', land_based_limit_amount: '90000.00', final_eligible_loan_amount: '90000.00', requested_amount: '500000.00', amount_within_limit_flag: false, exception_required_flag: true, calculated_as_of_date: '2026-07-12', calculation_rule_version: 'stored-v1' };
      const draft = { loan_application_id: 'application-1', required_loan_amount: '500000.00', application_status: 'draft' };
      const failure = error(row.status, row.code, row.message, row.field ? { required_loan_amount: row.message } : undefined);
      const fetchMock = vi.fn()
        .mockResolvedValueOnce(ok(profile))
        .mockResolvedValueOnce(ok(projection))
        .mockResolvedValueOnce(row.submit ? ok(draft) : failure);
      if (row.submit) fetchMock.mockResolvedValueOnce(failure);
      vi.stubGlobal('fetch', fetchMock);
      render(<RoleProvider><MP05_NewApplication onNavigateToApplication={vi.fn()} /></RoleProvider>);
      await completeMountedApplication();
      fireEvent.click(screen.getByRole('button', { name: 'Submit Application' }));
      await screen.findByText(row.message);
      expect(screen.getByText('Requested Amount').parentElement?.textContent).toContain('₹5,00,000');
      expect(fetchMock.mock.calls.filter(([url]) => String(url).includes('application-limit-projection'))).toHaveLength(1);
      expect(fetchMock).toHaveBeenCalledTimes(row.submit ? 4 : 3);
    }
  });
});

async function completeMountedApplication() {
  fireEvent.click(await screen.findByRole('button', { name: 'Nominee' }));
  fireEvent.change(await screen.findByRole('combobox'), { target: { value: 'nominee-1' } });
  fireEvent.click(screen.getByRole('button', { name: 'Documents' }));
  screen.getAllByRole('button', { name: 'Mark Uploaded' }).forEach(button => button.click());
  screen.getAllByRole('button', { name: 'Self-attested?' }).forEach(button => button.click());
  fireEvent.click(screen.getByRole('button', { name: 'Declarations' }));
  screen.getAllByRole('checkbox').forEach(box => box.click());
  fireEvent.click(screen.getByRole('button', { name: 'Review' }));
}

function ok(data: unknown): Response {
  return { ok: true, status: 200, json: async () => ({ success: true, data, meta: {} }) } as Response;
}

function error(status: number, code: string, message: string, field_errors?: Record<string, string>): Response {
  return { ok: false, status, json: async () => ({ success: false, error: { code, message, field_errors } }) } as Response;
}
