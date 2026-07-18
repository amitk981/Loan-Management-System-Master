// @vitest-environment jsdom
import React from 'react';
import { cleanup, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { AuthSessionError } from '../../../../services/authSession';
import {
  downloadPortalDisbursementAdvice,
  fetchPortalApplications,
  fetchPortalDisbursementStatus,
  PortalDisbursementStatus,
} from '../../../../services/portalApi';
import MP14_DisbursementStatus from './MP14_DisbursementStatus';
import source from './MP14_DisbursementStatus.tsx?raw';

vi.mock('../../../../services/portalApi', async importOriginal => {
  const actual = await importOriginal<typeof import('../../../../services/portalApi')>();
  return {
    ...actual,
    fetchPortalApplications: vi.fn(),
    fetchPortalDisbursementStatus: vi.fn(),
    downloadPortalDisbursementAdvice: vi.fn(),
  };
});

const applicationsMock = vi.mocked(fetchPortalApplications);
const statusMock = vi.mocked(fetchPortalDisbursementStatus);
const downloadMock = vi.mocked(downloadPortalDisbursementAdvice);

beforeEach(() => {
  applicationsMock.mockResolvedValue({ items: [approvedApplication] });
  statusMock.mockResolvedValue(disbursedProjection);
  downloadMock.mockResolvedValue(undefined);
});

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

describe('MP14 disbursement status', () => {
  it('renders only the server projection and downloads through the portal boundary', async () => {
    render(<MP14_DisbursementStatus />);

    expect(screen.getByText('Loading disbursement status…')).toBeTruthy();
    expect((await screen.findAllByText('Loan amount transferred.')).length).toBeGreaterThan(0);
    expect(screen.getByText('₹4,00,000')).toBeTruthy();
    expect(screen.getByText('••••4321')).toBeTruthy();
    expect(screen.getByText('••••9876')).toBeTruthy();
    expect(screen.getByText('Advice issued')).toBeTruthy();
    expect(screen.queryByText('SAP-240042')).toBeNull();
    expect(screen.queryByText('RBL-ADVICE-9876')).toBeNull();

    await userEvent.click(screen.getByRole('button', { name: 'Download Advice' }));

    await waitFor(() => expect(downloadMock).toHaveBeenCalledWith('app-approved'));
  });

  it('contains no hard-coded production fixture or mock source', () => {
    expect(source).not.toContain('mockData');
    expect(source).not.toContain('SAP-240042');
    expect(source).not.toContain('UTR20240922001042');
    expect(source).not.toContain('18 Sep 2024');
    expect(source).not.toContain('₹5,00,000');
  });

  it('shows processing, blocked, empty, session, and safe error states', async () => {
    statusMock.mockResolvedValueOnce({
      ...disbursedProjection,
      status_code: 'cfc_authorisation_pending',
      status_label: 'Payment approval in progress.',
      disbursement_amount: null,
      disbursed_at: null,
      bank_reference_last4: null,
      advice_available: false,
      timeline: disbursedProjection.timeline.map((item, index) => ({
        ...item,
        status: index < 3 ? 'complete' : 'pending',
        completed_at: index < 3 ? item.completed_at : null,
      })),
    });
    const processing = render(<MP14_DisbursementStatus />);
    expect(await screen.findByText('Payment approval in progress.')).toBeTruthy();
    expect(screen.getByRole('button', { name: 'Advice unavailable' }).hasAttribute('disabled')).toBe(true);
    processing.unmount();

    statusMock.mockResolvedValueOnce({
      ...disbursedProjection,
      status_code: 'disbursement_blocked',
      status_label: 'Action required / SFPCL review needed.',
      disbursement_amount: null,
      disbursed_at: null,
      bank_reference_last4: null,
      advice_available: false,
    });
    const blocked = render(<MP14_DisbursementStatus />);
    expect(await screen.findByText('Action required / SFPCL review needed.')).toBeTruthy();
    blocked.unmount();

    applicationsMock.mockResolvedValueOnce({ items: [] });
    const empty = render(<MP14_DisbursementStatus />);
    expect(await screen.findByText('No approved application is in finance processing yet.')).toBeTruthy();
    empty.unmount();

    applicationsMock.mockRejectedValueOnce(new AuthSessionError('AUTH_REQUIRED', 'Expired.', 401));
    const expired = render(<MP14_DisbursementStatus />);
    expect(await screen.findByText('Your member portal session has expired. Please sign in again.')).toBeTruthy();
    expired.unmount();

    applicationsMock.mockRejectedValueOnce(new Error('offline'));
    render(<MP14_DisbursementStatus />);
    expect(await screen.findByText('Disbursement status could not be loaded. Please try again.')).toBeTruthy();
  });
});

const approvedApplication = {
  loan_application_id: 'app-approved', application_reference_number: 'LO-APPROVED', display_reference: 'LO-APPROVED',
  application_date: '2026-07-18', submitted_at: '2026-07-18T08:00:00Z', required_loan_amount: '400000.00',
  declared_purpose: 'Crop production', purpose_category: 'crop_production', loan_type_requested: 'short_term',
  application_status: 'approved_by_sanction_committee', current_stage: 'disbursement', completeness_status: 'complete',
  pending_with: 'SFPCL', borrower_action: 'Track finance processing', open_deficiency_count: 0,
  created_at: '2026-07-18T07:00:00Z', updated_at: '2026-07-18T09:00:00Z',
};

const disbursedProjection: PortalDisbursementStatus = {
  loan_application_id: 'app-approved',
  loan_account_id: 'loan-1',
  status_code: 'disbursed',
  status_label: 'Loan amount transferred.',
  sanctioned_amount: '400000.00',
  disbursement_amount: '400000.00',
  destination_account_last4: '4321',
  disbursed_at: '2026-07-18T10:00:00Z',
  bank_reference_last4: '9876',
  advice_available: true,
  timeline: [
    ['documentation_complete', 'Documents completed.'],
    ['sap_setup', 'Finance setup complete.'],
    ['payment_initiated', 'Payment processing started.'],
    ['cfc_authorisation', 'Payment approved.'],
    ['transfer_completed', 'Loan amount transferred.'],
    ['advice_issued', 'Advice issued'],
  ].map(([code, label]) => ({ code, label, status: 'complete', completed_at: '2026-07-18T10:00:00Z' })),
};
