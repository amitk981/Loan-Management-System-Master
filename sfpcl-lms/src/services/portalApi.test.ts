import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { clearStoredAuthSession, storedAuthSession } from './authSession';
import {
  createPortalApplicationDraft,
  fetchPortalApplicationDeficiencies,
  downloadPortalDocumentationAction,
  fetchPortalDocumentContent,
  fetchPortalApplication,
  fetchPortalApplications,
  fetchPortalDocumentationActions,
  fetchPortalDashboard,
  fetchPortalProduceSupply,
  fetchPortalProfile,
  submitPortalApplication,
  resubmitPortalApplicationDeficiencies,
  uploadPortalDeficiencyResponse,
  uploadPortalDocumentationAction,
  updatePortalApplicationDraft,
} from './portalApi';

const storage = new Map<string, string>();

beforeEach(() => {
  vi.stubGlobal('localStorage', {
    getItem: vi.fn((key: string) => storage.get(key) ?? null),
    setItem: vi.fn((key: string, value: string) => storage.set(key, value)),
    removeItem: vi.fn((key: string) => storage.delete(key)),
  });
  storage.clear();
  storedAuthSession({ accessToken: 'portal-access-token', refreshToken: 'portal-refresh-token' });
});

afterEach(() => {
  clearStoredAuthSession();
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe('portal member API client', () => {
  it('loads dashboard, profile, and produce supply using the stored portal bearer token', async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(ok({ member: { display_name: 'Ganesh Thorat' }, application_counts: { total: 1 }, pending_actions: { open_deficiencies: 1 }, loan_counts: { active: 0 }, notices: [] }))
      .mockResolvedValueOnce(ok({ member: { display_name: 'Ganesh Thorat', pan: { masked: '******234F' } }, nominees: [], shareholdings: [], land_holdings: [], crop_plans: [], bank_accounts: [], cancelled_cheques: [], kyc_profile: null }))
      .mockResolvedValueOnce(ok({ records: [], summary: {}, source_status: 'persisted_no_verified_records' }));
    vi.stubGlobal('fetch', fetchMock);

    await expect(fetchPortalDashboard()).resolves.toMatchObject({ member: { display_name: 'Ganesh Thorat' } });
    await expect(fetchPortalProfile()).resolves.toMatchObject({ member: { pan: { masked: '******234F' } } });
    await expect(fetchPortalProduceSupply()).resolves.toMatchObject({ source_status: 'persisted_no_verified_records' });

    expect(fetchMock).toHaveBeenNthCalledWith(1, 'http://127.0.0.1:8000/api/v1/portal/dashboard/', request());
    expect(fetchMock).toHaveBeenNthCalledWith(2, 'http://127.0.0.1:8000/api/v1/portal/profile/', request());
    expect(fetchMock).toHaveBeenNthCalledWith(3, 'http://127.0.0.1:8000/api/v1/portal/produce-supply/', request());
  });

  it('surfaces portal permission errors without substituting mock member data', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValueOnce(error(403, 'PERMISSION_DENIED')));

    await expect(fetchPortalDashboard()).rejects.toMatchObject({ code: 'PERMISSION_DENIED', status: 403 });
  });

  it('surfaces backend nominee field errors for portal forms', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValueOnce(error(
      400,
      'VALIDATION_ERROR',
      { nominee_id: 'Selected nominee must be at least 18 years old.' },
    )));

    await expect(createPortalApplicationDraft({ nominee_id: 'minor-nominee' })).rejects.toMatchObject({
      code: 'VALIDATION_ERROR',
      fieldErrors: { nominee_id: 'Selected nominee must be at least 18 years old.' },
    });
  });

  it('creates, updates, submits, lists, and reads portal applications with the stored bearer token', async () => {
    const application = {
      loan_application_id: 'app-1',
      display_reference: 'APP-1',
      application_status: 'draft',
      required_loan_amount: '250000.00',
      pending_with: 'Borrower',
      open_deficiency_count: 0,
      timeline: [],
      deficiencies: [],
    };
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(ok(application))
      .mockResolvedValueOnce(ok({ ...application, required_loan_amount: '300000.00' }))
      .mockResolvedValueOnce(ok({ ...application, application_status: 'submitted', pending_with: 'SFPCL' }))
      .mockResolvedValueOnce(ok({ items: [application] }))
      .mockResolvedValueOnce(ok(application));
    vi.stubGlobal('fetch', fetchMock);

    await expect(createPortalApplicationDraft({ nominee_id: 'nominee-1', required_loan_amount: '250000.00', declared_purpose: 'Crop production', purpose_category: 'crop_production' })).resolves.toMatchObject({ loan_application_id: 'app-1' });
    await expect(updatePortalApplicationDraft('app-1', { nominee_id: 'nominee-1', required_loan_amount: '300000.00' })).resolves.toMatchObject({ required_loan_amount: '300000.00' });
    await expect(submitPortalApplication('app-1')).resolves.toMatchObject({ application_status: 'submitted', pending_with: 'SFPCL' });
    await expect(fetchPortalApplications()).resolves.toMatchObject({ items: [{ loan_application_id: 'app-1' }] });
    await expect(fetchPortalApplication('app-1')).resolves.toMatchObject({ display_reference: 'APP-1' });

    expect(fetchMock).toHaveBeenNthCalledWith(1, 'http://127.0.0.1:8000/api/v1/portal/applications/', request('POST', {
      nominee_id: 'nominee-1',
      required_loan_amount: '250000.00',
      declared_purpose: 'Crop production',
      purpose_category: 'crop_production',
    }));
    expect(fetchMock).toHaveBeenNthCalledWith(2, 'http://127.0.0.1:8000/api/v1/portal/applications/app-1/', request('PATCH', {
      nominee_id: 'nominee-1',
      required_loan_amount: '300000.00',
    }));
    expect(fetchMock).toHaveBeenNthCalledWith(3, 'http://127.0.0.1:8000/api/v1/portal/applications/app-1/submit/', request('POST', {}));
    expect(fetchMock).toHaveBeenNthCalledWith(4, 'http://127.0.0.1:8000/api/v1/portal/applications/', request());
    expect(fetchMock).toHaveBeenNthCalledWith(5, 'http://127.0.0.1:8000/api/v1/portal/applications/app-1/', request());
  });

  it('loads deficiencies, uploads the exact server-owned multipart contract, and resubmits', async () => {
    const deficiencyProjection = {
      loan_application_id: 'app-1', application_status: 'incomplete_returned', resubmission_allowed: true,
      items: [{
        deficiency_id: 'def-1', item_code: 'six_month_bank_statement', deficiency_type: 'missing_document',
        description: 'Upload statement.', resolution_status: 'open', raised_at: '2026-07-15T10:00:00Z',
        upload_contract: { document_category: 'finance', sensitivity_level: 'confidential', allowed_extensions: ['pdf'], max_size_bytes: 5242880 }, response: null,
      }],
    };
    const fetchMock = vi.fn();
    vi.stubGlobal('fetch', fetchMock);
    fetchMock
      .mockResolvedValueOnce(ok(deficiencyProjection))
      .mockResolvedValueOnce(ok({ deficiency_id: 'def-1', response_status: 'responded', response: {}, document: {} }))
      .mockResolvedValueOnce(ok({ loan_application_id: 'app-1', application_status: 'submitted', completeness_status: 'not_started', current_stage: 'initial_loan_request', pending_with: 'SFPCL', resolved_deficiency_count: 1 }));

    const projection = await fetchPortalApplicationDeficiencies('app-1');
    const file = Object.assign(new Blob(['statement'], { type: 'application/pdf' }), {
      name: 'statement.pdf', lastModified: 0,
    }) as File;
    await uploadPortalDeficiencyResponse('app-1', projection.items[0], file, 'Corrected statement.');
    await resubmitPortalApplicationDeficiencies('app-1');

    expect(fetchMock.mock.calls[0][0]).toBe('http://127.0.0.1:8000/api/v1/portal/applications/app-1/deficiencies/');
    const uploadCall = fetchMock.mock.calls[1];
    expect(uploadCall[0]).toBe('http://127.0.0.1:8000/api/v1/portal/applications/app-1/deficiencies/def-1/upload/');
    expect(uploadCall[1]).toMatchObject({ method: 'POST', headers: { Accept: 'application/json', Authorization: 'Bearer portal-access-token' } });
    expect(uploadCall[1].headers).not.toHaveProperty('Content-Type');
    expect(uploadCall[1].body.get('file')).toMatchObject({ name: 'statement.pdf' });
    expect(uploadCall[1].body.get('document_category')).toBe('finance');
    expect(uploadCall[1].body.get('sensitivity_level')).toBe('confidential');
    expect(uploadCall[1].body.get('response_remark')).toBe('Corrected statement.');
    expect(fetchMock.mock.calls[2][0]).toBe('http://127.0.0.1:8000/api/v1/portal/applications/app-1/deficiencies/resubmit/');
  });

  it('loads documentation actions, uploads exact multipart data, and follows the safe download action', async () => {
    const projection = {
      loan_application_id: 'app-1',
      application_reference_number: 'LO-1',
      application_status: 'approved_by_sanction_committee',
      availability: 'available',
      unavailable_reason: null,
      actions: [{
        action_code: 'term_sheet',
        label: 'Term Sheet',
        section: 'Sanction',
        required: true,
        applicable: true,
        status: 'pending_borrower',
        updated_date: '2026-07-15',
        instruction: 'Sign and upload.',
        note: null,
        upload_allowed: true,
        reupload_allowed: false,
        download: { file_name: 'term-sheet.pdf', mime_type: 'application/pdf', action_url: '/api/v1/portal/applications/app-1/documentation-actions/term_sheet/download/' },
      }],
    };
    const uploadResult = { action_code: 'term_sheet', status: 'submitted', document: { document_id: 'doc-1', file_name: 'signed.pdf', mime_type: 'application/pdf', file_size_bytes: 128, checksum_sha256: 'abc', uploaded_at: '2026-07-15T10:00:00Z' } };
    const descriptor = { download_url: '/api/v1/portal/applications/app-1/documentation-actions/term_sheet/download/?content=1&expires_at=soon', expires_at: '2026-07-15T10:15:00Z' };
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(ok(projection))
      .mockResolvedValueOnce(ok(uploadResult))
      .mockResolvedValueOnce(ok(descriptor))
      .mockResolvedValueOnce({ ok: true, status: 200, blob: async () => new Blob(['term sheet']) });
    vi.stubGlobal('fetch', fetchMock);
    const file = Object.assign(new Blob(['signed bytes'], { type: 'application/pdf' }), {
      name: 'signed.pdf',
      lastModified: 0,
    }) as File;

    await expect(fetchPortalDocumentationActions('app-1')).resolves.toMatchObject({ actions: [{ action_code: 'term_sheet' }] });
    await expect(uploadPortalDocumentationAction('app-1', 'term_sheet', file, 'Signed by borrower.')).resolves.toMatchObject({ status: 'submitted' });
    await expect(downloadPortalDocumentationAction('/api/v1/portal/applications/app-1/documentation-actions/term_sheet/download/')).resolves.toEqual(descriptor);
    await expect(fetchPortalDocumentContent(descriptor.download_url)).resolves.toBeInstanceOf(Blob);

    expect(fetchMock).toHaveBeenNthCalledWith(1, 'http://127.0.0.1:8000/api/v1/portal/applications/app-1/documentation-actions/', request());
    const uploadCall = fetchMock.mock.calls[1];
    expect(uploadCall[0]).toBe('http://127.0.0.1:8000/api/v1/portal/applications/app-1/documentation-actions/term_sheet/upload/');
    expect(uploadCall[1]).toMatchObject({ method: 'POST', headers: { Accept: 'application/json', Authorization: 'Bearer portal-access-token' } });
    expect(uploadCall[1].headers).not.toHaveProperty('Content-Type');
    expect(uploadCall[1].body).toBeInstanceOf(FormData);
    expect(uploadCall[1].body.get('file')).toMatchObject({ name: 'signed.pdf', type: 'application/pdf', size: 12 });
    expect(uploadCall[1].body.get('notes')).toBe('Signed by borrower.');
    expect(fetchMock).toHaveBeenNthCalledWith(3, 'http://127.0.0.1:8000/api/v1/portal/applications/app-1/documentation-actions/term_sheet/download/', request());
    expect(fetchMock).toHaveBeenNthCalledWith(4, `http://127.0.0.1:8000${descriptor.download_url}`, {
      headers: { Authorization: 'Bearer portal-access-token' },
    });
  });
});

const request = (method = 'GET', body?: unknown) => expect.objectContaining({
  method,
  headers: expect.objectContaining({
    Accept: 'application/json',
    Authorization: 'Bearer portal-access-token',
    ...(body ? { 'Content-Type': 'application/json' } : {}),
  }),
  ...(body ? { body: JSON.stringify(body) } : {}),
});

function ok(data: unknown): Response {
  return { ok: true, status: 200, json: async () => ({ success: true, data, meta: {} }) } as Response;
}

function error(status: number, code: string, fieldErrors?: Record<string, string>): Response {
  return {
    ok: false,
    status,
    json: async () => ({ success: false, error: { code, message: 'Portal request failed.', field_errors: fieldErrors }, meta: {} }),
  } as Response;
}
