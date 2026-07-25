// @vitest-environment jsdom
import { cleanup, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import ReportsMIS from './ReportsMIS';
import { AuthSessionError } from '../../services/authSession';
import {
  downloadReportExport,
  fetchReport,
  fetchReportExport,
  requestReportExport,
} from '../../services/reportApi';

const currentUser = {
  permissions: ['reports.portfolio.read', 'finance.loan_account.read', 'reports.export'],
  isBackendSession: true,
};

vi.mock('../../contexts/RoleContext', () => ({
  useRole: () => ({
    currentUser,
    can: (permission: string) => (
      permission === 'view_reports'
        ? currentUser.permissions.some(value => value.startsWith('reports.') && value.endsWith('.read'))
        : permission === 'export_registers' && currentUser.permissions.includes('reports.export')
    ),
  }),
}));

vi.mock('../../services/reportApi', async importOriginal => ({
  ...await importOriginal<typeof import('../../services/reportApi')>(),
  fetchReport: vi.fn(),
  requestReportExport: vi.fn(),
  fetchReportExport: vi.fn(),
  downloadReportExport: vi.fn(),
}));

beforeEach(() => {
  currentUser.permissions = ['reports.portfolio.read', 'finance.loan_account.read', 'reports.export'];
  vi.mocked(fetchReport).mockReset().mockResolvedValue({
    items: [{
      loan_account_id: 'loan-report-1',
      loan_account_number: 'LN-REPORT-001',
      borrower_name: 'Seeded Report Member',
      loan_account_status: 'active',
      sanctioned_amount: '150000.00',
      disbursed_amount: '150000.00',
      principal_outstanding: '125000.00',
      interest_outstanding: '5000.00',
      total_outstanding: '130000.00',
      loan_type: 'short_term',
      repayment_date: '2026-09-30',
      created_at: '2026-04-01T10:00:00Z',
    }],
    pagination: {
      page: 1,
      page_size: 20,
      total_count: 1,
      total_pages: 1,
      has_next: false,
      has_previous: false,
    },
  });
  vi.mocked(requestReportExport).mockReset();
  vi.mocked(fetchReportExport).mockReset();
  vi.mocked(downloadReportExport).mockReset();
});

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

describe('ReportsMIS report wiring', () => {
  it('renders reconciled portfolio rows and totals from the backend page', async () => {
    render(<ReportsMIS />);

    expect(screen.getByText('Loading report results…')).toBeTruthy();
    expect(await screen.findByText('LN-REPORT-001')).toBeTruthy();
    expect(screen.getByText('Seeded Report Member')).toBeTruthy();
    expect(screen.getByText('1 record')).toBeTruthy();
    expect(screen.getByText('₹1,30,000.00')).toBeTruthy();
    expect(fetchReport).toHaveBeenCalledWith('loan-portfolio', {
      asOfDate: undefined,
      status: undefined,
      ordering: '-created_at',
      page: 1,
      pageSize: 20,
    });
  });

  it('preserves active filters while backend sorting and pagination change', async () => {
    vi.mocked(fetchReport).mockImplementation(async (_code, query = {}) => ({
      items: [{
        loan_account_id: `loan-report-${query.page ?? 1}`,
        loan_account_number: `LN-REPORT-00${query.page ?? 1}`,
        borrower_name: 'Seeded Report Member',
        loan_account_status: 'active',
        sanctioned_amount: '150000.00',
        disbursed_amount: '150000.00',
        principal_outstanding: '125000.00',
        interest_outstanding: '5000.00',
        total_outstanding: '130000.00',
        loan_type: 'short_term',
        repayment_date: '2026-09-30',
        created_at: '2026-04-01T10:00:00Z',
      }],
      pagination: {
        page: query.page ?? 1,
        page_size: 20,
        total_count: 21,
        total_pages: 2,
        has_next: (query.page ?? 1) === 1,
        has_previous: (query.page ?? 1) === 2,
      },
    }));
    render(<ReportsMIS />);
    expect(await screen.findByText('LN-REPORT-001')).toBeTruthy();

    await userEvent.type(screen.getByLabelText('As of date'), '2026-06-30');
    await userEvent.type(screen.getByLabelText('Account status'), 'active');
    await userEvent.click(screen.getByRole('button', { name: 'Apply filters' }));
    await waitFor(() => expect(fetchReport).toHaveBeenLastCalledWith('loan-portfolio', {
      asOfDate: '2026-06-30',
      status: 'active',
      ordering: '-created_at',
      page: 1,
      pageSize: 20,
    }));

    await userEvent.click(screen.getByRole('button', { name: 'Sort by Total outstanding' }));
    await waitFor(() => expect(fetchReport).toHaveBeenLastCalledWith('loan-portfolio', {
      asOfDate: '2026-06-30',
      status: 'active',
      ordering: 'total_outstanding',
      page: 1,
      pageSize: 20,
    }));

    await userEvent.click(screen.getByRole('button', { name: 'Next' }));
    await waitFor(() => expect(fetchReport).toHaveBeenLastCalledWith('loan-portfolio', {
      asOfDate: '2026-06-30',
      status: 'active',
      ordering: 'total_outstanding',
      page: 2,
      pageSize: 20,
    }));
    expect(await screen.findByText('LN-REPORT-002')).toBeTruthy();
  });

  it('renders empty and backend-denied states without stale report facts', async () => {
    const view = render(<ReportsMIS />);
    expect(await screen.findByText('LN-REPORT-001')).toBeTruthy();

    vi.mocked(fetchReport).mockResolvedValueOnce({
      items: [],
      pagination: {
        page: 1,
        page_size: 20,
        total_count: 0,
        total_pages: 1,
        has_next: false,
        has_previous: false,
      },
    });
    await userEvent.click(screen.getByRole('button', { name: 'Sort by Loan account' }));
    expect(await screen.findByText('No report results')).toBeTruthy();
    expect(screen.queryByText('Seeded Report Member')).toBeNull();

    vi.mocked(fetchReport).mockRejectedValueOnce(
      new AuthSessionError('FORBIDDEN', 'Scoped report denied.', 403),
    );
    await userEvent.click(screen.getByRole('button', { name: 'Apply filters' }));
    expect(await screen.findByText('Report access denied')).toBeTruthy();
    expect(screen.queryByText('Seeded Report Member')).toBeNull();

    currentUser.permissions = [];
    view.rerender(<ReportsMIS />);
    expect(screen.getByText('Access Restricted')).toBeTruthy();
    expect(screen.queryByText('Seeded Report Member')).toBeNull();
  });

  it('preserves backend job identity through queued, running, and ready states before audited download', async () => {
    vi.mocked(requestReportExport).mockResolvedValue(exportJob('queued'));
    vi.mocked(fetchReportExport)
      .mockResolvedValueOnce(exportJob('running'))
      .mockResolvedValueOnce(exportJob('completed'))
      .mockResolvedValueOnce({
        ...exportJob('completed'),
        download_url: '/api/v1/reports/exports/export-job-1/download/?token=signed',
        expires_at: '2026-07-25T06:00:00Z',
      });
    vi.mocked(downloadReportExport).mockResolvedValue(new Blob(['masked-export']));
    vi.stubGlobal('URL', {
      ...URL,
      createObjectURL: vi.fn(() => 'blob:masked-export'),
      revokeObjectURL: vi.fn(),
    });
    const click = vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => undefined);

    render(<ReportsMIS />);
    expect(await screen.findByText('LN-REPORT-001')).toBeTruthy();
    await userEvent.click(screen.getByRole('button', { name: 'Export' }));
    expect(await screen.findByText('Export queued')).toBeTruthy();
    expect(screen.getByText(/export-job-1/)).toBeTruthy();
    expect(requestReportExport).toHaveBeenCalledWith({
      reportCode: 'loan-portfolio',
      format: 'xlsx',
      filters: { ordering: '-created_at' },
    }, expect.any(String));

    await userEvent.click(screen.getByRole('button', { name: 'Refresh export status' }));
    expect(await screen.findByText('Export running')).toBeTruthy();
    expect(screen.queryByRole('button', { name: 'Download export' })).toBeNull();

    await userEvent.click(screen.getByRole('button', { name: 'Refresh export status' }));
    expect(await screen.findByText('Export finalizing')).toBeTruthy();
    expect(screen.queryByRole('button', { name: 'Download export' })).toBeNull();
    await userEvent.click(screen.getByRole('button', { name: 'Refresh export status' }));
    expect(await screen.findByText('Export ready')).toBeTruthy();
    await userEvent.click(screen.getByRole('button', { name: 'Download export' }));
    await waitFor(() => expect(downloadReportExport).toHaveBeenCalled());
    expect(click).toHaveBeenCalled();
    expect(screen.getByText(/masked by default/i)).toBeTruthy();
  });

  it('surfaces backend export denial without leaking a job or stale success', async () => {
    vi.mocked(requestReportExport).mockRejectedValue(
      new AuthSessionError('FORBIDDEN', 'Restricted backend detail.', 403),
    );
    render(<ReportsMIS />);
    expect(await screen.findByText('LN-REPORT-001')).toBeTruthy();

    await userEvent.click(screen.getByRole('button', { name: 'Export' }));
    expect(await screen.findByText('Export permission denied')).toBeTruthy();
    expect(screen.getByText('The backend did not authorize this export request.')).toBeTruthy();
    expect(screen.queryByText('Restricted backend detail.')).toBeNull();
    expect(screen.queryByRole('button', { name: 'Download export' })).toBeNull();

    vi.mocked(requestReportExport).mockRejectedValue(
      new AuthSessionError('VALIDATION_ERROR', 'Report export request failed validation.', 400),
    );
    await userEvent.click(screen.getByRole('button', { name: 'Export' }));
    expect(await screen.findByText('Export validation failed')).toBeTruthy();

    vi.mocked(requestReportExport).mockResolvedValue(exportJob('failed'));
    await userEvent.click(screen.getByRole('button', { name: 'Export' }));
    expect(await screen.findByText('Export failed')).toBeTruthy();
    expect(screen.queryByRole('button', { name: 'Download export' })).toBeNull();
    const keys = vi.mocked(requestReportExport).mock.calls.map(call => call[1]);
    expect(new Set(keys).size).toBe(1);
  });
});

const exportJob = (status: 'queued' | 'running' | 'completed' | 'failed') => ({
  export_job_id: 'export-job-1',
  report_code: 'loan-portfolio' as const,
  format: 'xlsx' as const,
  filters: {},
  status,
  failure_code: status === 'failed' ? 'RENDER_FAILED' : null,
  idempotency_replayed: false,
  requested_at: '2026-07-25T05:30:00Z',
  started_at: status === 'queued' ? null : '2026-07-25T05:30:01Z',
  completed_at: status === 'completed' || status === 'failed' ? '2026-07-25T05:30:02Z' : null,
});
