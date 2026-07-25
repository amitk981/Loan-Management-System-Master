// @vitest-environment jsdom
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { AuthSessionError } from './authSession';
import { fetchReport } from './reportApi';

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
