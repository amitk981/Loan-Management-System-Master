// @vitest-environment jsdom
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { AuthSessionError } from './authSession';
import {
  downloadReportExport,
  fetchReport,
  fetchReportExport,
  requestReportExport,
} from './reportApi';

beforeEach(() => {
  localStorage.clear();
  localStorage.setItem('sfpcl_staff_auth_session', JSON.stringify({
    accessToken: 'report-token',
    refreshToken: 'report-refresh',
  }));
  vi.restoreAllMocks();
});

describe('reportApi', () => {
  it('round-trips source filters, backend ordering, and pagination', async () => {
    const fetchMock = vi.fn().mockResolvedValue(ok(
      [{
        loan_account_id: 'loan-1',
        loan_account_number: 'LN-REPORT-001',
        borrower_name: 'Seeded Report Member',
        total_outstanding: '125000.00',
      }],
      pagination,
    ));
    vi.stubGlobal('fetch', fetchMock);

    await expect(fetchReport('loan-portfolio', {
      asOfDate: '2026-06-30',
      status: 'active',
      ordering: '-total_outstanding',
      page: 2,
      pageSize: 10,
    })).resolves.toMatchObject({
      items: [{ loan_account_number: 'LN-REPORT-001' }],
      pagination: { page: 2, total_count: 11 },
    });

    expect(fetchMock).toHaveBeenCalledWith(
      'http://127.0.0.1:8000/api/v1/reports/loan-portfolio/?status=active&as_of_date=2026-06-30&ordering=-total_outstanding&page=2&page_size=10',
      expect.objectContaining({
        method: 'GET',
        headers: expect.objectContaining({
          Accept: 'application/json',
          Authorization: 'Bearer report-token',
        }),
      }),
    );
  });

  it('propagates backend denial without returning fallback rows or totals', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: false,
      status: 403,
      json: async () => ({
        success: false,
        error: { code: 'FORBIDDEN', message: 'Report permission and object scope are required.' },
      }),
    } as Response));

    await expect(fetchReport('dpd', { page: 1, pageSize: 20 }))
      .rejects.toMatchObject({ code: 'FORBIDDEN', status: 403 } satisfies Partial<AuthSessionError>);
  });

  it('preserves the backend export job identity and idempotency contract', async () => {
    const fetchMock = vi.fn().mockResolvedValue(okData({
      export_job_id: 'export-job-012dab',
      report_code: 'loan-portfolio' as const,
      format: 'xlsx',
      filters: { as_of_date: '2026-06-30' },
      status: 'queued',
      failure_code: null,
      idempotency_replayed: false,
      requested_at: '2026-07-25T05:30:00Z',
      started_at: null,
      completed_at: null,
    }));
    vi.stubGlobal('fetch', fetchMock);

    await expect(requestReportExport({
      reportCode: 'loan-portfolio',
      format: 'xlsx',
      filters: { as_of_date: '2026-06-30' },
    }, 'report-export-attempt-1')).resolves.toMatchObject({
      export_job_id: 'export-job-012dab',
      status: 'queued',
    });

    expect(fetchMock).toHaveBeenCalledWith(
      'http://127.0.0.1:8000/api/v1/reports/exports/',
      expect.objectContaining({
        method: 'POST',
        headers: expect.objectContaining({
          Authorization: 'Bearer report-token',
          'Idempotency-Key': 'report-export-attempt-1',
        }),
        body: JSON.stringify({
          report_code: 'loan-portfolio',
          format: 'xlsx',
          filters: { as_of_date: '2026-06-30' },
        }),
      }),
    );
  });

  it('refreshes only the preserved job and downloads only its audited completed capability', async () => {
    const completed = {
      export_job_id: 'export-job-012dab',
      report_code: 'loan-portfolio' as const,
      format: 'xlsx' as const,
      filters: {},
      status: 'completed' as const,
      failure_code: null,
      idempotency_replayed: false,
      requested_at: '2026-07-25T05:30:00Z',
      started_at: '2026-07-25T05:30:01Z',
      completed_at: '2026-07-25T05:30:02Z',
      checksum_sha256: 'safe-checksum',
      file_size_bytes: 128,
      download_url: '/api/v1/reports/exports/export-job-012dab/download/?token=signed',
      expires_at: '2026-07-25T05:45:02Z',
    };
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(okData(completed))
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        blob: async () => new Blob(['masked-export']),
      } as Response);
    vi.stubGlobal('fetch', fetchMock);

    await expect(fetchReportExport('export-job-012dab')).resolves.toEqual(completed);
    await expect(downloadReportExport(completed)).resolves.toBeInstanceOf(Blob);
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      'http://127.0.0.1:8000/api/v1/reports/exports/export-job-012dab/download/?token=signed',
      expect.objectContaining({
        headers: expect.objectContaining({ Authorization: 'Bearer report-token' }),
      }),
    );

    await expect(downloadReportExport({ ...completed, status: 'failed', download_url: undefined }))
      .rejects.toMatchObject({ code: 'EXPORT_NOT_READY' });
    await expect(downloadReportExport({
      ...completed,
      download_url: 'https://restricted.example/export.xlsx',
    })).rejects.toMatchObject({ code: 'INVALID_DOWNLOAD_ACTION' });
  });

  it('surfaces export permission denial without exposing backend details', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: false,
      status: 403,
      json: async () => ({
        success: false,
        error: {
          code: 'FORBIDDEN',
          message: 'Report read and export permissions are required.',
        },
      }),
    } as Response));

    await expect(requestReportExport({
      reportCode: 'loan-portfolio',
      format: 'xlsx',
      filters: {},
    }, 'denied-attempt')).rejects.toMatchObject({
      code: 'FORBIDDEN',
      status: 403,
    });
  });
});

const pagination = {
  page: 2,
  page_size: 10,
  total_count: 11,
  total_pages: 2,
  has_next: false,
  has_previous: true,
};

function ok(data: unknown, page: typeof pagination): Response {
  return {
    ok: true,
    status: 200,
    json: async () => ({ success: true, data, pagination: page }),
  } as Response;
}

function okData(data: unknown): Response {
  return {
    ok: true,
    status: 200,
    json: async () => ({ success: true, data }),
  } as Response;
}
