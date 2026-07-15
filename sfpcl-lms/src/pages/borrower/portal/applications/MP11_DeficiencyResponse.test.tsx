// @vitest-environment jsdom
import React from 'react';
import { cleanup, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { AuthSessionError } from '../../../../services/authSession';
import { fetchPortalApplicationDeficiencies, downloadPortalDeficiencyNote, resubmitPortalApplicationDeficiencies, savePortalDeficiencyResponseDraft, uploadPortalDeficiencyResponse } from '../../../../services/portalApi';
import MP11_DeficiencyResponse from './MP11_DeficiencyResponse';

vi.mock('../../../../services/portalApi', async importOriginal => {
  const actual = await importOriginal<typeof import('../../../../services/portalApi')>();
  return { ...actual, fetchPortalApplicationDeficiencies: vi.fn(), downloadPortalDeficiencyNote: vi.fn(), uploadPortalDeficiencyResponse: vi.fn(), resubmitPortalApplicationDeficiencies: vi.fn(), savePortalDeficiencyResponseDraft: vi.fn() };
});

const fetchMock = vi.mocked(fetchPortalApplicationDeficiencies);
const uploadMock = vi.mocked(uploadPortalDeficiencyResponse);
const resubmitMock = vi.mocked(resubmitPortalApplicationDeficiencies);
const saveDraftMock = vi.mocked(savePortalDeficiencyResponseDraft), noteMock = vi.mocked(downloadPortalDeficiencyNote);

beforeEach(() => {
  fetchMock.mockReset(); uploadMock.mockReset(); resubmitMock.mockReset();
  saveDraftMock.mockReset(); noteMock.mockReset();
  fetchMock.mockResolvedValue(projection);
  uploadMock.mockResolvedValue({ deficiency_id: 'def-1', response_status: 'responded', response: respondedItem.response, document: respondedItem.response!.document });
  resubmitMock.mockResolvedValue({ loan_application_id: 'app-returned', application_status: 'submitted', completeness_status: 'not_started', current_stage: 'initial_loan_request', pending_with: 'SFPCL', responded_deficiency_count: 1 });
  saveDraftMock.mockResolvedValue({ deficiency_id: 'def-1', response_remark: 'Corrected statement attached.', updated_at: '2026-07-15T10:00:00Z' });
  noteMock.mockResolvedValue(new Blob(['safe note'], { type: 'text/plain' }));
});

afterEach(() => { cleanup(); vi.clearAllMocks(); });

describe('MP11 deficiency response', () => {
  it('uploads a server-contracted response, refetches canonical state, and resubmits', async () => {
    fetchMock.mockResolvedValueOnce(projection).mockResolvedValueOnce({ ...projection, resubmission_allowed: true, items: [respondedItem] });
    const onResubmitted = vi.fn();
    render(<MP11_DeficiencyResponse applicationId="app-returned" onResubmitted={onResubmitted} />);
    expect(screen.getByText('Loading deficiency response…')).toBeTruthy();
    expect(await screen.findByText('Upload the missing six-month bank statement.')).toBeTruthy();
    expect(screen.getByRole('region', { name: 'Deficiency Response' })).toBeTruthy();
    expect(screen.getByText('Deficiency reason')).toBeTruthy();
    expect(screen.getByText('Requested correction')).toBeTruthy();
    expect(screen.getByRole('button', { name: 'Download deficiency note' })).toBeTruthy();
    expect((screen.getByRole('button', { name: 'Resubmit corrections' }) as HTMLButtonElement).disabled).toBe(true);
    const file = new File(['statement'], 'statement.pdf', { type: 'application/pdf' });
    await userEvent.upload(screen.getByLabelText('Replacement document'), file);
    await userEvent.type(screen.getByLabelText('Borrower response remark'), 'Corrected statement attached.');
    await userEvent.click(screen.getByRole('button', { name: 'Save response draft' }));
    await waitFor(() => expect(saveDraftMock).toHaveBeenCalledWith('app-returned', 'def-1', 'Corrected statement attached.'));
    await userEvent.click(screen.getByRole('button', { name: 'Upload response' }));
    await waitFor(() => expect(uploadMock).toHaveBeenCalledWith('app-returned', projection.items[0], file, 'Corrected statement attached.'));
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(2));
    expect(await screen.findByText('Response uploaded for SFPCL review.')).toBeTruthy();
    expect(screen.getByText('statement.pdf')).toBeTruthy();
    await userEvent.click(screen.getByRole('button', { name: 'Resubmit corrections' }));
    await waitFor(() => expect(resubmitMock).toHaveBeenCalledWith('app-returned'));
    expect(await screen.findByText('Corrections resubmitted for completeness review.')).toBeTruthy();
    expect(onResubmitted).toHaveBeenCalledTimes(1);
  });

  it('shows empty, validation, unauthorized, and generic error states without fixture fallback', async () => {
    fetchMock.mockResolvedValueOnce({ ...projection, items: [] });
    const empty = render(<MP11_DeficiencyResponse applicationId="app-returned" onResubmitted={vi.fn()} />);
    expect(await screen.findByText('No open deficiencies require a response.')).toBeTruthy();
    empty.unmount();
    fetchMock.mockRejectedValueOnce(new AuthSessionError('FORBIDDEN', 'Denied.', 403));
    const denied = render(<MP11_DeficiencyResponse applicationId="app-returned" onResubmitted={vi.fn()} />);
    expect(await screen.findByText('You are not authorised to respond to these deficiencies.')).toBeTruthy();
    denied.unmount();
    fetchMock.mockRejectedValueOnce(new Error('offline'));
    const failed = render(<MP11_DeficiencyResponse applicationId="app-returned" onResubmitted={vi.fn()} />);
    expect(await screen.findByText('Deficiency response could not be loaded. Please try again.')).toBeTruthy();
    failed.unmount();
    uploadMock.mockRejectedValueOnce(new AuthSessionError('VALIDATION_ERROR', 'Upload failed.', 400, { file: 'File must not exceed 5 MiB.' }));
    render(<MP11_DeficiencyResponse applicationId="app-returned" onResubmitted={vi.fn()} />);
    expect(await screen.findByText('Upload the missing six-month bank statement.')).toBeTruthy();
    const loadCountBeforeUpload = fetchMock.mock.calls.length;
    await userEvent.upload(screen.getByLabelText('Replacement document'), new File(['x'], 'statement.pdf', { type: 'application/pdf' }));
    await userEvent.click(screen.getByRole('button', { name: 'Upload response' }));
    expect(await screen.findByText('File must not exceed 5 MiB.')).toBeTruthy();
    expect(fetchMock).toHaveBeenCalledTimes(loadCountBeforeUpload);
  });
});

const document = { document_id: 'doc-1', file_name: 'statement.pdf', mime_type: 'application/pdf', file_size_bytes: 128, checksum_sha256: 'safe-checksum', uploaded_at: '2026-07-15T10:00:00Z', action_url: '/api/v1/portal/applications/app-returned/deficiencies/def-1/download/' };
const item = {
  deficiency_id: 'def-1', item_code: 'six_month_bank_statement', deficiency_type: 'missing_document', description: 'Upload the missing six-month bank statement.', resolution_status: 'open', raised_at: '2026-07-15T09:00:00Z',
  upload_contract: { document_category: 'finance', sensitivity_level: 'confidential', allowed_extensions: ['pdf', 'jpg', 'jpeg', 'png'], max_size_bytes: 5242880 }, response: null, draft: null,
};
const respondedItem = { ...item, response: { deficiency_response_id: 'response-1', response_status: 'responded' as const, response_remark: 'Corrected statement attached.', document, responded_at: '2026-07-15T10:00:00Z' } };
const projection = { loan_application_id: 'app-returned', application_status: 'incomplete_returned', application_reference_number: 'LA-RETURNED-L2', deficiency_note_action_url: '/api/v1/portal/applications/app-returned/deficiencies/note/', resubmission_allowed: false, items: [item] };
