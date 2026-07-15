// @vitest-environment jsdom
import { cleanup, render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import DocumentationHub from './DocumentationHub';
import { AuthSessionError } from '../../services/authSession';
import {
  fetchDocumentationQueue,
  fetchDocumentationWorkspace,
  submitDocumentationAction,
  type DocumentationAction,
  type DocumentationQueueRow,
  type DocumentationWorkspace,
} from '../../services/documentationWorkspaceApi';
import apiSource from '../../services/documentationWorkspaceApi.ts?raw';

vi.mock('../../services/documentationWorkspaceApi', async importOriginal => ({
  ...await importOriginal<typeof import('../../services/documentationWorkspaceApi')>(),
  fetchDocumentationQueue: vi.fn(),
  fetchDocumentationWorkspace: vi.fn(),
  submitDocumentationAction: vi.fn(),
  downloadStaffDocument: vi.fn(),
  openStaffDocumentBlob: vi.fn(),
}));

const action = (
  actionCode: string, label: string, actionUrl: string,
  options: Partial<DocumentationAction> = {},
): DocumentationAction => ({
  action_code: actionCode, label, enabled: true, disabled_reason: null,
  required_permission: `documents.${actionCode}`, action_url: actionUrl, method: 'POST', ...options,
});

const approvalAction = action(
  'approve_as_company_secretary',
  'Approve as Company Secretary',
  '/api/v1/document-checklists/checklist-1/approve-as-company-secretary/',
  { fields: [{ name: 'comments', label: 'Comments', type: 'textarea', required: true }] },
);

const item = (code: string, label: string) => ({
  checklist_item_id: `item-${code}`, item_code: code, item_label: label,
  required: true, applicable: true, status: 'pending', blocker: null,
  stamp_status: null, notarisation_status: null, poa_status: null,
  document: null, available_actions: [],
});

const queueRow: DocumentationQueueRow = {
  loan_application_id: 'application-1', application_reference_number: 'LO000001',
  borrower_name: 'API Borrower', sanctioned_amount: '400000.00', shareholding_mode: 'physical',
  required_document_summary: { complete: 1, required: 2 },
  poa_status: 'draft', tri_party_status: 'pending', sh4_status: 'held_in_custody',
  cdsl_pledge_status: 'not_required', term_sheet_status: 'complete',
  loan_agreement_status: 'pending', bank_verification_status: 'blocked',
  checklist_status: 'in_progress', current_owner: 'Compliance Team',
};

const generationAction = action(
  'generate_document',
  'Generate document',
  '/api/v1/loan-applications/application-1/loan-documents/generate/',
  {
    fixed_payload: { document_type: 'power_of_attorney', template_id: 'template-1' },
    fields: [{
      name: 'output_format', label: 'Output format', type: 'select',
      required: true, options: ['pdf', 'docx'],
    }],
  },
);

const workspace: DocumentationWorkspace = {
  snapshot_id: 'snapshot-1', loan_application_id: 'application-1',
  application_reference_number: 'LO000001', borrower_name: 'API Borrower',
  checklist_status: 'in_progress', bank_verification_status: 'blocked',
  pack_summary: { status: 'incomplete', available_count: 1, missing_count: 1, pending_review_count: 0 },
  blockers: [{ item_code: 'poa', label: 'Power of Attorney', reason: 'notarisation_pending' }],
  items: [
    {
      ...item('term_sheet', 'Term Sheet'),
      status: 'complete',
      document: {
        loan_document_id: 'doc-1', version: '2.0', generation_status: 'generated',
        execution_status: 'executed', verification_status: 'verified',
        download: { file_name: 'term-sheet.pdf', mime_type: 'application/pdf', action_url: '/api/v1/loan-applications/application-1/documentation-workspace/term_sheet/download/' },
      },
    },
    {
      ...item('poa', 'Power of Attorney'),
      blocker: 'notarisation_pending', stamp_status: 'adequate',
      notarisation_status: 'pending', poa_status: 'draft',
      available_actions: [generationAction],
    },
  ],
  security_workflows: Object.fromEntries([
    ['power_of_attorney', true, 'draft'], ['tri_party_agreement', true, 'pending'],
    ['sh4', true, 'held_in_custody'], ['cdsl_pledge', false, 'not_required'],
    ['blank_dated_cheque', true, 'held'], ['cancelled_cheque', true, 'complete'],
  ].map(([code, required, status]) => [code, { required, status, available_actions: [] }])) as DocumentationWorkspace['security_workflows'],
  approval_stages: ['company_secretary', 'credit_manager', 'sanction_committee', 'senior_manager_finance']
    .map((role, index) => ({ role, status: index === 3 ? 'blocked_until_disbursement' : 'pending' })),
  available_actions: [approvalAction],
  timeline: [{
    id: 'company_secretary_approval:0', entityType: 'document_checklist',
    entityId: 'application-1', eventType: 'Company Secretary Approved',
    timestamp: '2026-07-16T10:00:00+05:30', actorName: 'Checklist CS',
    actorRole: 'company_secretary', comment: 'All documents verified and attached.',
  }],
};

const pagination = { page: 1, page_size: 20, total_count: 1, total_pages: 1, has_next: false, has_previous: false };

async function renderHub(onOpenApplication = vi.fn()) {
  render(<DocumentationHub onOpenApplication={onOpenApplication} />);
  await screen.findByRole('heading', { name: 'Document Checklist' });
}

async function approve() {
  await userEvent.click(screen.getByRole('button', { name: 'Approvals' }));
  await userEvent.click(screen.getByRole('button', { name: 'Approve as Company Secretary' }));
  await userEvent.type(screen.getByLabelText('Comments'), 'All documents verified.');
  await userEvent.click(screen.getByRole('button', { name: 'Confirm action' }));
}

describe('008M2 documentation workspace contract', () => {
  beforeEach(() => {
    vi.mocked(fetchDocumentationQueue).mockResolvedValue({ items: [queueRow], pagination });
    vi.mocked(fetchDocumentationWorkspace).mockResolvedValue(workspace);
    vi.mocked(submitDocumentationAction).mockResolvedValue({ checklist_action_id: 'action-1' });
  });

  afterEach(() => { cleanup(); vi.clearAllMocks(); });

  it('uses the backend queue/detail contract without aggregate or file-list bypasses', () => {
    expect(apiSource).not.toContain('Promise.all'); expect(apiSource).not.toContain('/api/v1/document-files/');
    expect(apiSource).toContain('action_code'); expect(apiSource).toContain('/api/v1/documentation-workspaces/');
  });

  it('renders the S26 facts, blockers, workflows, timeline, and terminal status beside Download', async () => {
    await renderHub();
    expect(screen.getByText('400000.00')).toBeTruthy(); expect(screen.getByText(/Power of Attorney: Notarisation Pending/i)).toBeTruthy();
    expect(screen.getByText('Complete')).toBeTruthy(); expect(screen.getByRole('button', { name: 'Download' })).toBeTruthy();
    await userEvent.click(screen.getByRole('button', { name: 'Securities' }));
    for (const label of ['Power of Attorney', 'Tri-Party Agreement', 'SH-4', 'CDSL Pledge', 'Blank-Dated Cheque', 'Cancelled Cheque']) expect(screen.getByText(label)).toBeTruthy();
    await userEvent.click(screen.getByRole('button', { name: 'Audit Trail' }));
    expect(screen.getByText('All documents verified and attached.')).toBeTruthy();
  });

  it('posts a server-owned approval and refetches once without optimism', async () => {
    await renderHub(); await approve();
    await waitFor(() => expect(submitDocumentationAction).toHaveBeenCalledWith(approvalAction, { comments: 'All documents verified.' }));
    expect(fetchDocumentationWorkspace).toHaveBeenCalledTimes(2); expect(screen.getByRole('button', { name: 'Approve as Company Secretary' })).toBeTruthy();
  });

  it('posts the exact server-selected generation option and refetches once', async () => {
    await renderHub(); await userEvent.click(screen.getByRole('button', { name: 'Generate document' }));
    expect((screen.getByLabelText('Output format') as HTMLSelectElement).value).toBe('pdf');
    await userEvent.click(screen.getByRole('button', { name: 'Confirm action' }));
    expect(submitDocumentationAction).toHaveBeenCalledWith(generationAction, { output_format: 'pdf' }); expect(fetchDocumentationWorkspace).toHaveBeenCalledTimes(2);
  });

  it('renders a restricted item without content or mutation controls', async () => {
    vi.mocked(fetchDocumentationWorkspace).mockResolvedValueOnce({
      ...workspace,
      items: [{
        ...workspace.items[0],
        document: { ...workspace.items[0].document!, download: null },
        available_actions: [],
      }],
    });
    await renderHub();
    expect(screen.getByText('Restricted or no action available')).toBeTruthy(); expect(screen.queryByRole('button', { name: 'Download' })).toBeNull();
    expect(screen.queryByRole('button', { name: 'Generate document' })).toBeNull();
  });

  it('keeps a conflict visible with no optimistic change, retry, or refetch', async () => {
    vi.mocked(submitDocumentationAction).mockRejectedValueOnce(new AuthSessionError('CHECKLIST_APPROVAL_OUT_OF_ORDER', 'Approval facts changed.', 409));
    await renderHub(); await approve(); expect(await screen.findByText('Approval facts changed.')).toBeTruthy();
    expect(submitDocumentationAction).toHaveBeenCalledTimes(1); expect(fetchDocumentationWorkspace).toHaveBeenCalledTimes(1);
    expect(screen.getByRole('button', { name: 'Approve as Company Secretary' })).toBeTruthy();
  });

  it('renders queue failure without a false all-complete state', async () => {
    vi.mocked(fetchDocumentationQueue).mockRejectedValueOnce(new Error('Documentation queue failed.'));
    render(<DocumentationHub onOpenApplication={vi.fn()} />);
    expect(await screen.findByText('Documentation queue failed.')).toBeTruthy(); expect(screen.queryByText('All documentation is complete')).toBeNull();
  });

  it('keeps Download and Verify independent inside the Document Pack', async () => {
    const verifyAction = action('verify_document', 'Verify document', '/api/v1/loan-documents/doc-1/verify/');
    vi.mocked(fetchDocumentationWorkspace).mockResolvedValueOnce({
      ...workspace,
      items: [{ ...workspace.items[0], status: 'pending', available_actions: [verifyAction] }],
    });
    await renderHub();
    await userEvent.click(screen.getByRole('button', { name: 'View Document Pack' }));
    const dialog = screen.getByRole('heading', { name: 'Document Pack — LO000001' }).parentElement?.parentElement?.parentElement as HTMLElement;
    expect(within(dialog).getByRole('button', { name: 'Download' })).toBeTruthy(); expect(within(dialog).getByRole('button', { name: 'Verify document' })).toBeTruthy();
  });

  it('executes a returned security action instead of navigating away', async () => {
    const manageAction = action('manage_power_of_attorney', 'Manage Power Of Attorney', '/api/v1/security-packages/package-1/power-of-attorney/');
    vi.mocked(fetchDocumentationWorkspace).mockResolvedValueOnce({
      ...workspace,
      security_workflows: {
        ...workspace.security_workflows,
        power_of_attorney: { required: true, status: 'pending', available_actions: [manageAction] },
      },
    });
    const onOpenApplication = vi.fn();
    await renderHub(onOpenApplication); await userEvent.click(screen.getByRole('button', { name: 'Securities' }));
    await userEvent.click(screen.getByRole('button', { name: 'Manage Power Of Attorney' }));
    expect(submitDocumentationAction).toHaveBeenCalledWith(manageAction, {}); expect(onOpenApplication).not.toHaveBeenCalled();
  });

  it.each([
    ['record_signature', 'Record signature'],
    ['record_stamp', 'Record stamp'],
    ['record_notarisation', 'Record notarisation'],
    ['resolve_signature_mismatch', 'Resolve signature mismatch'],
    ['complete_item', 'Mark complete'],
  ])('executes the %s action family through its returned endpoint', async (code, label) => {
    const returned = action(code, label, `/api/v1/actions/${code}/`);
    vi.mocked(fetchDocumentationWorkspace).mockResolvedValueOnce({
      ...workspace,
      items: [{ ...workspace.items[0], available_actions: [returned] }],
    });
    await renderHub();
    await userEvent.click(screen.getByRole('button', { name: label }));
    expect(submitDocumentationAction).toHaveBeenCalledWith(returned, {});
  });
});
