import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { clearStoredAuthSession, storedAuthSession } from './authSession';
import {
  createApplicationWitness,
  createApplicationRejectionNote,
  createStaffApplicationDraft,
  fetchApplicationDeficiencies,
  fetchApplicationCompleteness,
  fetchApplicationDetail,
  fetchApplicationDocumentChecklist,
  fetchApplicationWitnesses,
  fetchLoanRequestRegister,
  fetchStaffApplications,
  passApplicationCompleteness,
  resolveApplicationDeficiency,
  returnApplicationWithDeficiencies,
  submitStaffApplication,
  updateStaffApplicationDraft,
} from './applicationIntakeApi';

const storage = new Map<string, string>();

beforeEach(() => {
  vi.stubGlobal('localStorage', {
    getItem: vi.fn((key: string) => storage.get(key) ?? null),
    setItem: vi.fn((key: string, value: string) => storage.set(key, value)),
    removeItem: vi.fn((key: string) => storage.delete(key)),
  });
  storage.clear();
  storedAuthSession({ accessToken: 'staff-access-token', refreshToken: 'staff-refresh-token' });
});

afterEach(() => {
  clearStoredAuthSession();
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe('application intake API client', () => {
  it('reads and creates witnesses through the application-scoped contract', async () => {
    const witness = { witness_id: 'witness-1', witness_name: 'Test Witness' };
    const payload = { member_id: 'member-1', witness_name: 'Test Witness', pan: 'ABCDE1234F', aadhaar: '123412341234' };
    const fetchMock = vi.fn().mockResolvedValueOnce(ok([witness])).mockResolvedValueOnce(ok(witness));
    vi.stubGlobal('fetch', fetchMock);

    await expect(fetchApplicationWitnesses('app-1')).resolves.toEqual([witness]);
    await expect(createApplicationWitness('app-1', payload)).resolves.toEqual(witness);

    expect(fetchMock).toHaveBeenNthCalledWith(1, 'http://127.0.0.1:8000/api/v1/loan-applications/app-1/witnesses/', request());
    expect(fetchMock).toHaveBeenNthCalledWith(2, 'http://127.0.0.1:8000/api/v1/loan-applications/app-1/witnesses/', request('POST', payload));
  });
  it('loads staff applications and register rows from staff endpoints with pagination', async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(ok([application], pagination))
      .mockResolvedValueOnce(ok([registerRow], pagination));
    vi.stubGlobal('fetch', fetchMock);

    await expect(fetchStaffApplications({
      search: 'Ramesh',
      applicationStatus: 'incomplete_returned',
      ordering: '-application_date',
      page: 2,
      pageSize: 20,
    })).resolves.toMatchObject({
      items: [{ loan_application_id: 'app-1', application_status: 'incomplete_returned' }],
      pagination: { page: 2, total_count: 21 },
    });
    await expect(fetchLoanRequestRegister({ search: 'LO00000001' })).resolves.toMatchObject({
      items: [{ application_reference_number: 'LO00000001' }],
    });

    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      'http://127.0.0.1:8000/api/v1/loan-applications/?search=Ramesh&application_status=incomplete_returned&ordering=-application_date&page=2&page_size=20',
      request(),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      'http://127.0.0.1:8000/api/v1/loan-request-register/?search=LO00000001',
      request(),
    );
  });

  it('creates, updates, submits, and reads application detail using staff APIs', async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(ok(application))
      .mockResolvedValueOnce(ok({ ...application, required_loan_amount: '300000.00' }))
      .mockResolvedValueOnce(ok({ ...application, application_status: 'submitted' }))
      .mockResolvedValueOnce(ok(application))
      .mockResolvedValueOnce(ok({ loan_application_id: 'app-1', items: [checklistItem] }))
      .mockResolvedValueOnce(ok({ loan_application_id: 'app-1', items: [deficiency] }));
    vi.stubGlobal('fetch', fetchMock);

    await expect(createStaffApplicationDraft({ member_id: 'member-1', nominee_id: 'nominee-1', required_loan_amount: '250000.00' })).resolves.toMatchObject({ loan_application_id: 'app-1' });
    await expect(updateStaffApplicationDraft('app-1', { nominee_id: 'nominee-1', required_loan_amount: '300000.00' })).resolves.toMatchObject({ required_loan_amount: '300000.00' });
    await expect(submitStaffApplication('app-1')).resolves.toMatchObject({ application_status: 'submitted' });
    await expect(fetchApplicationDetail('app-1')).resolves.toMatchObject({ member: { display_name: 'Ramesh Patil' } });
    await expect(fetchApplicationDocumentChecklist('app-1')).resolves.toMatchObject({ items: [{ document_type: 'borrower_pan' }] });
    await expect(fetchApplicationDeficiencies('app-1')).resolves.toMatchObject({ items: [{ item_code: 'borrower_pan' }] });

    expect(fetchMock).toHaveBeenNthCalledWith(1, 'http://127.0.0.1:8000/api/v1/loan-applications/', request('POST', { member_id: 'member-1', nominee_id: 'nominee-1', required_loan_amount: '250000.00' }));
    expect(fetchMock).toHaveBeenNthCalledWith(2, 'http://127.0.0.1:8000/api/v1/loan-applications/app-1/', request('PATCH', { nominee_id: 'nominee-1', required_loan_amount: '300000.00' }));
    expect(fetchMock).toHaveBeenNthCalledWith(3, 'http://127.0.0.1:8000/api/v1/loan-applications/app-1/submit/', request('POST', {}));
    expect(fetchMock).toHaveBeenNthCalledWith(4, 'http://127.0.0.1:8000/api/v1/loan-applications/app-1/', request());
    expect(fetchMock).toHaveBeenNthCalledWith(5, 'http://127.0.0.1:8000/api/v1/loan-applications/app-1/document-checklist/', request());
    expect(fetchMock).toHaveBeenNthCalledWith(6, 'http://127.0.0.1:8000/api/v1/loan-applications/app-1/deficiencies/', request());
  });

  it('surfaces permission and object access errors without fallback data', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValueOnce(error(403, 'OBJECT_ACCESS_DENIED')));

    await expect(fetchApplicationDetail('app-1')).rejects.toMatchObject({
      code: 'OBJECT_ACCESS_DENIED',
      status: 403,
    });
  });

  it('uses the existing completeness, deficiency, resolution, and rejection contracts exactly', async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(ok(completeness))
      .mockResolvedValueOnce(ok({ ...application, application_reference_number: 'LO00000042' }))
      .mockResolvedValueOnce(ok({ ...application, application_status: 'incomplete_returned', items: [deficiency] }))
      .mockResolvedValueOnce(ok({ ...deficiency, resolution_status: 'resolved' }))
      .mockResolvedValueOnce(ok({ rejection_note_id: 'note-1', note_status: 'draft' }));
    vi.stubGlobal('fetch', fetchMock);

    await expect(fetchApplicationCompleteness('app-1')).resolves.toMatchObject({ blocking_document_types: ['borrower_pan'] });
    await expect(passApplicationCompleteness('app-1')).resolves.toMatchObject({ application_reference_number: 'LO00000042' });
    await expect(returnApplicationWithDeficiencies('app-1', {
      communication_mode: 'email',
      message: 'Please submit the missing document.',
      items: [{ item_code: 'borrower_pan', remarks: 'Current PAN copy is missing.' }],
    })).resolves.toMatchObject({ application_status: 'incomplete_returned' });
    await expect(resolveApplicationDeficiency('def-1', { resolution_notes: 'Verified replacement.' })).resolves.toMatchObject({ resolution_status: 'resolved' });
    await expect(createApplicationRejectionNote('app-1', {
      rejection_stage: 'completeness',
      rejection_reason_category: 'missing_document',
      detailed_reason: 'Mandatory documents were not supplied.',
      reapply_allowed_flag: true,
      communication_mode: 'email',
    })).resolves.toMatchObject({ rejection_note_id: 'note-1' });

    expect(fetchMock).toHaveBeenNthCalledWith(1, 'http://127.0.0.1:8000/api/v1/loan-applications/app-1/completeness-check/', request());
    expect(fetchMock).toHaveBeenNthCalledWith(2, 'http://127.0.0.1:8000/api/v1/loan-applications/app-1/completeness-check/pass/', request('POST', {}));
    expect(fetchMock).toHaveBeenNthCalledWith(3, 'http://127.0.0.1:8000/api/v1/loan-applications/app-1/return-with-deficiencies/', request('POST', {
      communication_mode: 'email',
      message: 'Please submit the missing document.',
      items: [{ item_code: 'borrower_pan', remarks: 'Current PAN copy is missing.' }],
    }));
    expect(fetchMock).toHaveBeenNthCalledWith(4, 'http://127.0.0.1:8000/api/v1/deficiencies/def-1/resolve/', request('POST', { resolution_notes: 'Verified replacement.' }));
    expect(fetchMock).toHaveBeenNthCalledWith(5, 'http://127.0.0.1:8000/api/v1/loan-applications/app-1/rejection-note/', request('POST', {
      rejection_stage: 'completeness',
      rejection_reason_category: 'missing_document',
      detailed_reason: 'Mandatory documents were not supplied.',
      reapply_allowed_flag: true,
      communication_mode: 'email',
    }));
  });
});

const application = {
  loan_application_id: 'app-1',
  application_reference_number: null,
  member: {
    member_id: 'member-1',
    display_name: 'Ramesh Patil',
    member_type: 'individual_farmer',
    folio_number: 'FOL-005A',
  },
  application_date: '2026-07-10',
  required_loan_amount: '250000.00',
  requested_tenure_months: 12,
  declared_purpose: 'Crop production',
  purpose_category: 'crop_production',
  application_status: 'incomplete_returned',
  current_stage: 'initial_loan_request',
  completeness_status: 'incomplete',
  assigned_owner: { user_id: 'user-1', full_name: 'Deputy Manager Finance' },
  tat: { due_at: null, status: 'blocked' },
};

const registerRow = {
  loan_request_register_entry_id: 'register-1',
  loan_application_id: 'app-1',
  application_reference_number: 'LO00000001',
  borrower_name: 'Ramesh Patil',
  folio_number: 'FOL-005A',
  member_type: 'individual_farmer',
  requested_amount: '250000.00',
  register_status: 'reference_generated',
  current_stage: 'credit_assessment',
  current_owner_role: 'credit_manager',
};

const checklistItem = {
  document_type: 'borrower_pan',
  complete: false,
  reason_code: 'missing_metadata',
};

const deficiency = {
  deficiency_id: 'def-1',
  item_code: 'borrower_pan',
  resolution_status: 'open',
  description: 'Borrower PAN is missing.',
};

const completeness = {
  loan_application_id: 'app-1',
  application_reference_number: null,
  application_status: 'submitted',
  current_stage: 'initial_loan_request',
  completeness_status: 'not_started',
  member: application.member,
  nominee: null,
  nominee_selection_status: 'valid',
  required_checklist_items: [checklistItem],
  blocking_document_types: ['borrower_pan'],
  can_generate_reference: false,
};

const pagination = {
  page: 2,
  page_size: 20,
  total_count: 21,
  total_pages: 2,
  has_next: false,
  has_previous: true,
};

const request = (method = 'GET', body?: unknown) => expect.objectContaining({
  method,
  headers: expect.objectContaining({
    Accept: 'application/json',
    Authorization: 'Bearer staff-access-token',
    ...(body ? { 'Content-Type': 'application/json' } : {}),
  }),
  ...(body ? { body: JSON.stringify(body) } : {}),
});

function ok(data: unknown, page = pagination): Response {
  return { ok: true, status: 200, json: async () => ({ success: true, data, pagination: page, meta: {} }) } as Response;
}

function error(status: number, code: string): Response {
  return {
    ok: false,
    status,
    json: async () => ({ success: false, error: { code, message: 'Staff request failed.' }, meta: {} }),
  } as Response;
}
