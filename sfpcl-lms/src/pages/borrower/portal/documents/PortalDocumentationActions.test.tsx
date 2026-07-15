// @vitest-environment jsdom
import React from 'react';
import { cleanup, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { AuthSessionError } from '../../../../services/authSession';
import {
  downloadPortalDocumentationAction,
  fetchPortalDocumentContent,
  fetchPortalApplications,
  fetchPortalDocumentationActions,
  uploadPortalDocumentationAction,
} from '../../../../services/portalApi';
import MP07_DocumentChecklist from './MP07_DocumentChecklist';
import MP13_DocumentationActions from './MP13_DocumentationActions';
import mp07Source from './MP07_DocumentChecklist.tsx?raw';
import mp13Source from './MP13_DocumentationActions.tsx?raw';
vi.mock('../../../../services/portalApi', async importOriginal => {
  const actual = await importOriginal<typeof import('../../../../services/portalApi')>();
  return {
    ...actual,
    fetchPortalApplications: vi.fn(),
    fetchPortalDocumentationActions: vi.fn(),
    uploadPortalDocumentationAction: vi.fn(),
    downloadPortalDocumentationAction: vi.fn(),
    fetchPortalDocumentContent: vi.fn(),
  };
});
const listMock = vi.mocked(fetchPortalApplications);
const projectionMock = vi.mocked(fetchPortalDocumentationActions);
const uploadMock = vi.mocked(uploadPortalDocumentationAction);
const downloadMock = vi.mocked(downloadPortalDocumentationAction);
const contentMock = vi.mocked(fetchPortalDocumentContent);
beforeEach(() => {
  listMock.mockResolvedValue({ items: [approvedApplication] });
  projectionMock.mockResolvedValue(projection);
  uploadMock.mockResolvedValue({
    action_code: 'term_sheet', status: 'submitted',
    document: { document_id: 'doc-upload', file_name: 'signed.pdf', mime_type: 'application/pdf', file_size_bytes: 12, checksum_sha256: 'safe-checksum', uploaded_at: '2026-07-15T10:00:00Z' },
  });
  downloadMock.mockResolvedValue({ download_url: '/safe-download', expires_at: '2026-07-15T10:15:00Z' });
  contentMock.mockResolvedValue(new Blob(['term sheet']));
  vi.stubGlobal('open', vi.fn());
});
afterEach(() => {
  cleanup();
  vi.clearAllMocks();
  vi.unstubAllGlobals();
});
describe('member portal documentation actions', () => {
  it('removes inline business fixtures from both screens', () => {
    for (const source of [mp07Source, mp13Source]) {
      expect(source).not.toContain('mockData');
      expect(source).not.toContain('const myDocuments = [');
      expect(source).not.toContain('const actions = [');
      expect(source).not.toContain('123456');
      expect(source).not.toContain('987654');
    }
  });
  it('renders server-owned actions and performs one canonical refetch after upload', async () => {
    projectionMock
      .mockResolvedValueOnce(projection)
      .mockResolvedValueOnce({
        ...projection,
        actions: projection.actions.map(action => action.action_code === 'term_sheet'
          ? { ...action, status: 'submitted', upload_allowed: false, reupload_allowed: true }
          : action),
      });
    render(<MP13_DocumentationActions />);
    expect(screen.getByText('Loading documentation actions…')).toBeTruthy();
    expect(await screen.findByText('Term Sheet')).toBeTruthy();
    expect(screen.getByText('Blank-Dated Cheque')).toBeTruthy();
    expect(screen.queryByRole('button', { name: 'Upload Blank-Dated Cheque' })).toBeNull();
    await userEvent.click(screen.getByRole('button', { name: 'Upload Term Sheet' }));
    expect(screen.getByText('Click to select file or drag and drop')).toBeTruthy();
    expect(screen.getByText('PDF, JPG, PNG · Max 5 MB')).toBeTruthy();
    const file = new File(['signed bytes'], 'signed.pdf', { type: 'application/pdf' });
    await userEvent.upload(screen.getByLabelText('Document file'), file);
    await userEvent.type(screen.getByLabelText('Notes (optional)'), 'Signed by borrower.');
    await userEvent.click(screen.getByRole('button', { name: 'Upload' }));
    await waitFor(() => expect(uploadMock).toHaveBeenCalledWith('app-approved', 'term_sheet', file, 'Signed by borrower.'));
    await waitFor(() => expect(projectionMock).toHaveBeenCalledTimes(2));
    expect(await screen.findByText('Document uploaded for SFPCL review.')).toBeTruthy();
    expect(screen.getByRole('button', { name: 'Re-upload Term Sheet' })).toBeTruthy();
    for (const secret of ['******', '9876543210', 'enc:v1:', 'storage_key', 'checklist_item_id']) {
      expect(document.body.textContent).not.toContain(secret);
    }
  });
  it('shows complete status with its retained download and no upload controls', async () => {
    projectionMock.mockResolvedValueOnce({
      ...projection,
      actions: projection.actions.map(action => action.action_code === 'term_sheet'
        ? {
            ...action,
            status: 'complete',
            upload_allowed: false,
            reupload_allowed: false,
          }
        : action),
    });

    render(<MP07_DocumentChecklist />);

    expect(await screen.findByText('Complete', { exact: true })).toBeTruthy();
    expect(screen.getByRole('button', { name: 'Download Term Sheet' })).toBeTruthy();
    expect(screen.queryByRole('button', { name: 'Upload Term Sheet' })).toBeNull();
    expect(screen.queryByRole('button', { name: 'Re-upload Term Sheet' })).toBeNull();
  });
  it('keeps the object URL alive after browser navigation starts', async () => {
    const createObjectURL = vi.fn(() => 'blob:term-sheet');
    const revokeObjectURL = vi.fn();
    vi.stubGlobal('URL', { createObjectURL, revokeObjectURL });
    render(<MP07_DocumentChecklist />);

    await userEvent.click(
      await screen.findByRole('button', { name: 'Download Term Sheet' }),
    );

    await waitFor(() => expect(contentMock).toHaveBeenCalledWith('/safe-download'));
    expect(createObjectURL).toHaveBeenCalledTimes(1);
    expect(window.open).toHaveBeenCalledWith(
      'blob:term-sheet', '_blank', 'noopener,noreferrer',
    );
    expect(revokeObjectURL).not.toHaveBeenCalled();
  });
  it('shows own-application empty and session-expired states without fixture fallback', async () => {
    listMock.mockResolvedValueOnce({ items: [] });
    const { unmount } = render(<MP07_DocumentChecklist />);
    expect(await screen.findByText('No sanctioned application has documentation actions yet.')).toBeTruthy();
    expect(screen.queryByText('PAN Card Copy')).toBeNull();
    unmount();
    listMock.mockRejectedValueOnce(new AuthSessionError('AUTH_REQUIRED', 'Session expired.', 401));
    render(<MP07_DocumentChecklist />);
    expect(await screen.findByText('Your member portal session has expired. Please sign in again.')).toBeTruthy();
  });
  it('shows forbidden, server-error, and canonical blocked states', async () => {
    listMock.mockRejectedValueOnce(new AuthSessionError('FORBIDDEN', 'Denied.', 403));
    const first = render(<MP07_DocumentChecklist />);
    expect(await screen.findByText('You are not authorised to view these documentation actions.')).toBeTruthy();
    first.unmount();
    listMock.mockRejectedValueOnce(new Error('offline'));
    const second = render(<MP07_DocumentChecklist />);
    expect(await screen.findByText('Documentation actions could not be loaded. Please try again.')).toBeTruthy();
    second.unmount();
    projectionMock.mockResolvedValueOnce({ ...projection, availability: 'blocked',
      unavailable_reason: 'Documentation actions are available after sanction.', actions: [] });
    render(<MP07_DocumentChecklist />);
    expect(await screen.findByText('Documentation actions are available after sanction.')).toBeTruthy();
  });
  it('shows server validation and keeps canonical status after a failed upload', async () => {
    uploadMock.mockRejectedValueOnce(new AuthSessionError(
      'VALIDATION_ERROR', 'Upload failed.', 400, { file: 'File must not exceed 5 MiB.' },
    ));
    render(<MP07_DocumentChecklist />);
    expect(await screen.findByText('Term Sheet')).toBeTruthy();
    await userEvent.click(screen.getByRole('button', { name: 'Upload Term Sheet' }));
    await userEvent.upload(screen.getByLabelText('Document file'), new File(['x'], 'signed.pdf', { type: 'application/pdf' }));
    await userEvent.click(screen.getByRole('button', { name: 'Upload' }));
    expect(await screen.findByText('File must not exceed 5 MiB.')).toBeTruthy();
    expect(projectionMock).toHaveBeenCalledTimes(1);
    expect(screen.getByRole('button', { name: 'Upload Term Sheet' })).toBeTruthy();
  });
});
const approvedApplication = {
  loan_application_id: 'app-approved', application_reference_number: 'LO-APPROVED', display_reference: 'LO-APPROVED',
  application_date: '2026-07-15', submitted_at: '2026-07-15T08:00:00Z', required_loan_amount: '400000.00',
  declared_purpose: 'Crop production', purpose_category: 'crop_production', loan_type_requested: 'short_term',
  application_status: 'approved_by_sanction_committee', current_stage: 'credit_assessment', completeness_status: 'complete',
  pending_with: 'SFPCL', borrower_action: 'Complete documentation', open_deficiency_count: 0,
  created_at: '2026-07-15T07:00:00Z', updated_at: '2026-07-15T09:00:00Z',
};
const projection = {
  loan_application_id: 'app-approved', application_reference_number: 'LO-APPROVED',
  application_status: 'approved_by_sanction_committee', availability: 'available' as const, unavailable_reason: null,
  actions: [
    { action_code: 'term_sheet', label: 'Term Sheet', section: 'Sanction', required: true, applicable: true, status: 'pending_borrower', updated_date: '2026-07-15', instruction: 'Sign and upload.', note: null, upload_allowed: true, reupload_allowed: false, download: { file_name: 'term-sheet.pdf', mime_type: 'application/pdf', action_url: '/api/v1/portal/applications/app-approved/documentation-actions/term_sheet/download/' } },
    { action_code: 'blank_dated_cheque', label: 'Blank-Dated Cheque', section: 'Security', required: true, applicable: true, status: 'submitted', updated_date: '2026-07-15', instruction: 'Submit the original physically.', note: null, upload_allowed: false, reupload_allowed: false, download: null },
    { action_code: 'cdsl_pledge', label: 'CDSL Pledge', section: 'Security', required: false, applicable: false, status: 'not_required', updated_date: '2026-07-15', instruction: 'Status only.', note: null, upload_allowed: false, reupload_allowed: false, download: null },
  ],
};
