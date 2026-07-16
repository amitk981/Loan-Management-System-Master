import React, { useCallback, useEffect, useRef, useState } from 'react';
import { AlertTriangle, Check, ClipboardList, FolderOpen, Lock, RefreshCw, Shield } from 'lucide-react';
import AuditTimeline from '../../components/loan/AuditTimeline';
import DocumentChecklist from '../../components/loan/DocumentChecklist';
import DocumentPackModal from '../../components/loan/DocumentPackModal';
import Modal from '../../components/ui/Modal';
import StageStepper, { type Step } from '../../components/ui/StageStepper';
import StatusBadge from '../../components/ui/StatusBadge';
import Tabs from '../../components/ui/Tabs';
import { AuthSessionError } from '../../services/authSession';
import {
  downloadStaffDocument,
  fetchDocumentationQueue,
  fetchDocumentationWorkspace,
  openStaffDocumentBlob,
  submitDocumentationAction,
  type DocumentationAction,
  type DocumentationItem,
  type DocumentationQueueRow,
  type DocumentationWorkspace,
  type Pagination,
} from '../../services/documentationWorkspaceApi';

interface DocumentationHubProps { onOpenApplication: (id: string) => void; initialSelectedId?: string }

const display = (value: string) => value.replace(/_/g, ' ')
  .replace(/\b\w/g, character => character.toUpperCase());

const workflowLabel = (code: string) => ({
  power_of_attorney: 'Power of Attorney',
  tri_party_agreement: 'Tri-Party Agreement',
  sh4: 'SH-4',
  cdsl_pledge: 'CDSL Pledge',
  blank_dated_cheque: 'Blank-Dated Cheque',
  cancelled_cheque: 'Cancelled Cheque',
}[code] ?? display(code));

const emptyPagination: Pagination = {
  page: 1, page_size: 20, total_count: 0, total_pages: 1,
  has_next: false, has_previous: false,
};

const DocumentationHub: React.FC<DocumentationHubProps> = ({
  onOpenApplication,
  initialSelectedId,
}) => {
  const [queue, setQueue] = useState<DocumentationQueueRow[]>([]);
  const [pagination, setPagination] = useState<Pagination>(emptyPagination);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [workspace, setWorkspace] = useState<DocumentationWorkspace | null>(null);
  const [loading, setLoading] = useState(true); const [queueError, setQueueError] = useState<string | null>(null);
  const [workspaceLoading, setWorkspaceLoading] = useState(false); const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null); const [forbidden, setForbidden] = useState(false);
  const [packOpen, setPackOpen] = useState(false);
  const [pendingAction, setPendingAction] = useState<DocumentationAction | null>(null);
  const [actionValues, setActionValues] = useState<Record<string, string>>({});
  const [actionFiles, setActionFiles] = useState<Record<string, File>>({});
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [actionAccepted, setActionAccepted] = useState(false);
  const workspaceSequence = useRef(0);
  const queueSequence = useRef(0);

  const loadQueue = useCallback(async (page: number) => {
    const sequence = ++queueSequence.current;
    setLoading(true);
    setQueueError(null);
    try {
      const result = await fetchDocumentationQueue(page, 20);
      if (sequence !== queueSequence.current) return;
      setQueue(result.items);
      setPagination(result.pagination);
      setSelectedId(current => {
        const requested = result.items.find(item => (
          item.loan_application_id === initialSelectedId
          || item.application_reference_number === initialSelectedId
        ));
        const retained = result.items.find(item => item.loan_application_id === current);
        return (requested ?? retained ?? result.items[0])?.loan_application_id ?? null;
      });
    } catch (reason) {
      if (sequence !== queueSequence.current) return;
      setQueue([]);
      setPagination(emptyPagination);
      setSelectedId(null);
      setQueueError(reason instanceof Error ? reason.message : 'Documentation queue could not be loaded.');
    } finally {
      if (sequence === queueSequence.current) setLoading(false);
    }
  }, [initialSelectedId]);

  useEffect(() => {
    void loadQueue(1);
    return () => { queueSequence.current += 1; };
  }, [loadQueue]);

  const loadWorkspace = useCallback(async (applicationId: string) => {
    const sequence = ++workspaceSequence.current;
    setWorkspaceLoading(true);
    setError(null);
    setForbidden(false);
    try {
      const result = await fetchDocumentationWorkspace(applicationId);
      if (sequence === workspaceSequence.current) setWorkspace(result);
    } catch (reason) {
      if (sequence !== workspaceSequence.current) return;
      setWorkspace(null);
      if (reason instanceof AuthSessionError && reason.status === 403) {
        setForbidden(true);
      } else {
        setError(reason instanceof Error ? reason.message : 'Documentation workspace could not be loaded.');
      }
    } finally {
      if (sequence === workspaceSequence.current) setWorkspaceLoading(false);
    }
  }, []);

  useEffect(() => {
    if (selectedId) void loadWorkspace(selectedId);
    else setWorkspace(null);
  }, [loadWorkspace, selectedId]);

  const runAction = async (
    action: DocumentationAction,
    payload: Record<string, string | File>,
  ) => {
    if (!selectedId) return;
    setBusy(true);
    setError(null);
    setFieldErrors({});
    setActionAccepted(false);
    try {
      await submitDocumentationAction(action, payload);
      setPendingAction(null);
      setActionValues({});
      setActionFiles({});
      setActionAccepted(true);
      await loadWorkspace(selectedId);
    } catch (reason) {
      if (reason instanceof AuthSessionError) setFieldErrors(reason.fieldErrors ?? {});
      setError(reason instanceof Error ? reason.message : 'Documentation action could not be completed.');
    } finally {
      setBusy(false);
    }
  };

  const startAction = (action: DocumentationAction) => {
    if (!action.enabled) return;
    const fields = action.fields ?? [];
    if (fields.length === 0) {
      void runAction(action, {});
      return;
    }
    setActionValues(Object.fromEntries(fields.map(field => [field.name, field.options?.[0] ?? ''])));
    setActionFiles({});
    setFieldErrors({});
    setPendingAction(action);
  };

  const confirmAction = () => {
    if (!pendingAction) return;
    const missing = Object.fromEntries(
      (pendingAction.fields ?? [])
        .filter(field => field.required && (
          field.type === 'file' ? !actionFiles[field.name] : !actionValues[field.name]?.trim()
        ))
        .map(field => [field.name, `${field.label} is required.`]),
    );
    if (Object.keys(missing).length > 0) {
      setFieldErrors(missing);
      return;
    }
    const payload: Record<string, string | File> = Object.fromEntries(Object.entries(actionValues)
      .filter(([, value]) => value !== '')
      .map(([name, value]) => [
        name,
        pendingAction.fields?.find(field => field.name === name)?.type === 'datetime-local'
          ? new Date(value).toISOString()
          : value,
      ]));
    Object.assign(payload, actionFiles);
    void runAction(pendingAction, payload);
  };

  const download = async (item: DocumentationItem) => {
    const action = item.document?.download;
    if (!action) return;
    setError(null);
    try {
      openStaffDocumentBlob(await downloadStaffDocument(action));
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'The document could not be downloaded.');
    }
  };

  const approvalSteps: Step[] = (workspace?.approval_stages ?? []).map((stage, index) => ({
    id: stage.role,
    label: display(stage.role),
    sublabel: index === 3 ? 'Post-disbursement' : undefined,
    state: stage.status === 'signed'
      ? 'completed'
      : index === (workspace?.approval_stages.findIndex(row => row.status === 'pending') ?? -1)
        ? 'in_progress'
        : 'not_started',
  }));
  const selectedQueueRow = queue.find(item => item.loan_application_id === selectedId);

  if (loading) {
    return <div className="card text-sm text-slate-500">Loading documentation queue…</div>;
  }

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Documentation Hub</h1>
          <p className="text-sm text-slate-500 mt-0.5">
            {pagination.total_count} application{pagination.total_count !== 1 ? 's' : ''} pending documentation
          </p>
        </div>
      </div>

      {queueError ? (
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
          {queueError}
        </div>
      ) : queue.length === 0 ? (
        <div className="card text-center py-16">
          <Check size={32} className="text-green-500 mx-auto mb-3" />
          <p className="text-slate-600 font-semibold">All documentation is complete</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-[300px_minmax(0,1fr)] gap-6">
          <div className="card p-0 overflow-hidden">
            <div className="p-4 bg-slate-50 border-b border-slate-200">
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide">
                Doc Queue ({pagination.total_count})
              </p>
            </div>
            <div className="divide-y divide-slate-100">
              {queue.map(item => (
                <button
                  key={item.loan_application_id}
                  onClick={() => setSelectedId(item.loan_application_id)}
                  className={`w-full flex items-start gap-3 p-4 hover:bg-slate-50 transition-colors text-left border-l-4 ${selectedId === item.loan_application_id ? 'bg-green-50 border-l-green-500' : 'bg-white border-l-transparent'}`}
                >
                  <FolderOpen size={16} className="text-amber-500 flex-shrink-0 mt-0.5" />
                  <div className="min-w-0">
                    <div className="font-semibold text-slate-900 text-sm truncate">
                      {item.application_reference_number || 'Reference pending'}
                    </div>
                    <div className="text-xs text-slate-500 truncate mt-0.5">{item.borrower_name}</div>
                    <div className="text-xs text-slate-400 mt-1">
                      {item.shareholding_mode ? display(item.shareholding_mode) : 'Share route blocked'} · {item.required_document_summary.complete}/{item.required_document_summary.required} complete
                    </div>
                    <div className="text-xs text-slate-400 mt-1">Owner: {item.current_owner}</div>
                  </div>
                </button>
              ))}
            </div>
            {pagination.total_pages > 1 && (
              <div className="p-3 border-t border-slate-200 flex items-center justify-between">
                <button className="btn-secondary text-xs" disabled={!pagination.has_previous} onClick={() => void loadQueue(pagination.page - 1)}>Previous</button>
                <span className="text-xs text-slate-500">{pagination.page} of {pagination.total_pages}</span>
                <button className="btn-secondary text-xs" disabled={!pagination.has_next} onClick={() => void loadQueue(pagination.page + 1)}>Next</button>
              </div>
            )}
          </div>

          <div className="space-y-4 min-w-0">
            {error && <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">{error}</div>}
            {forbidden && <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg text-sm text-amber-800 flex items-center gap-2"><Lock size={15} /> You are not authorised to open this documentation workspace.</div>}
            {actionAccepted && !error && <div className="p-3 bg-green-50 border border-green-200 rounded-lg text-sm text-green-800">Action accepted. The canonical documentation snapshot was refreshed.</div>}
            {workspaceLoading ? (
              <div className="card py-12 text-center text-sm text-slate-500">Loading canonical documentation snapshot…</div>
            ) : workspace ? (
              <>
                <div className="card">
                  <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                    <button className="text-left" onClick={() => onOpenApplication(workspace.loan_application_id)}>
                      <div className="flex flex-wrap items-center gap-2">
                        <h2 className="text-lg font-bold text-slate-900">{workspace.application_reference_number || 'Reference pending'}</h2>
                        <StatusBadge label={workspace.checklist_status} size="sm" />
                      </div>
                      <p className="text-sm text-slate-500 mt-0.5">{workspace.borrower_name}</p>
                    </button>
                    <div className="flex flex-wrap gap-2 self-start">
                      <button className="btn-secondary flex items-center gap-2 flex-shrink-0" onClick={() => setPackOpen(true)}><FolderOpen size={14} /> View Document Pack</button>
                      <button className="btn-secondary flex items-center gap-2" onClick={() => void loadWorkspace(workspace.loan_application_id)} disabled={workspaceLoading}><RefreshCw size={14} /> Refresh</button>
                    </div>
                  </div>
                  {selectedQueueRow && (
                    <div className="mt-4 grid grid-cols-2 lg:grid-cols-4 gap-3 text-xs text-slate-500">
                      <div>Sanctioned amount<br /><span className="font-semibold text-slate-800">{selectedQueueRow.sanctioned_amount ?? 'Blocked'}</span></div>
                      <div>Shareholding<br /><span className="font-semibold text-slate-800">{selectedQueueRow.shareholding_mode ? display(selectedQueueRow.shareholding_mode) : 'Blocked'}</span></div>
                      <div>Bank verification<br /><span className="font-semibold text-slate-800">{display(selectedQueueRow.bank_verification_status)}</span></div>
                      <div>Current owner<br /><span className="font-semibold text-slate-800">{selectedQueueRow.current_owner}</span></div>
                    </div>
                  )}
                  <div className="mt-4"><StageStepper steps={approvalSteps} /></div>
                </div>

                {workspace.blockers.length > 0 && (
                  <div className="flex items-start gap-2 bg-red-50 border border-red-200 rounded-lg px-4 py-3">
                    <AlertTriangle size={16} className="text-red-600 flex-shrink-0 mt-0.5" />
                    <p className="text-sm text-red-800 font-medium">Disbursement blocked: {workspace.blockers.map(row => `${row.label}: ${display(row.reason)}`).join(' · ')}</p>
                  </div>
                )}

                <div className="card p-0 overflow-hidden">
                  <Tabs tabs={[
                    { id: 'checklist', label: 'Checklist', badge: workspace.blockers.length ? `${workspace.blockers.length} pending` : undefined, badgeStyle: workspace.blockers.length ? 'warning' : undefined },
                    { id: 'documents', label: 'Documents' },
                    { id: 'security', label: 'Securities' },
                    { id: 'approvals', label: 'Approvals' },
                    { id: 'audit', label: 'Audit Trail' },
                  ]}>
                    <div className="p-5">
                      <div className="mb-3">
                        <h3 className="text-sm font-semibold text-slate-900 flex items-center gap-2"><ClipboardList size={14} /> Document Checklist</h3>
                        <p className="text-xs text-slate-500 mt-0.5">All required items before disbursement can proceed.</p>
                      </div>
                      <DocumentChecklist items={workspace.items} busy={busy} onDownload={item => void download(item)} onAction={startAction} />
                    </div>

                    <div className="p-5 space-y-2">
                      {workspace.items.map(item => <div key={item.item_code} className="rounded-lg border border-slate-200 bg-white p-3 flex items-center justify-between gap-3"><div><p className="text-sm font-medium text-slate-900">{item.item_label}</p><p className="text-xs text-slate-500 mt-0.5">{item.document ? `Template version ${item.document.version}` : 'No current generated document'}</p></div><StatusBadge label={!item.applicable ? 'not_required' : item.status} size="sm" /></div>)}
                    </div>

                    <div className="p-5">
                      <h3 className="text-sm font-semibold text-slate-900 flex items-center gap-2 mb-4"><Shield size={14} /> Security Instruments</h3>
                      <div className="space-y-2">
                        {Object.entries(workspace.security_workflows).map(([code, workflow]) => (
                          <div key={code} className="rounded-lg border border-slate-200 bg-white">
                            <div className="flex items-center gap-3 p-3">
                              <div className="w-8 h-8 rounded-lg bg-slate-100 flex items-center justify-center"><Shield size={14} className="text-slate-500" /></div>
                              <div className="flex-1"><div className="text-sm font-medium text-slate-900">{workflowLabel(code)}</div><div className="text-xs text-slate-500 mt-0.5">{workflow.required ? 'Required for this sanctioned package' : 'Not applicable'}</div></div>
                              <StatusBadge label={workflow.status} size="sm" />
                              {workflow.available_actions.map(action => <button key={action.action_key} className="btn-secondary text-xs" onClick={() => startAction(action)} disabled={!action.enabled || busy} title={action.disabled_reason ?? undefined}>{action.label}</button>)}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="p-5 space-y-4">
                      <div className="border border-slate-200 rounded-xl p-4 bg-slate-50"><StageStepper steps={approvalSteps} /></div>
                      {workspace.available_actions.map(action => <button key={action.action_key} className="btn-primary text-xs" onClick={() => startAction(action)} disabled={!action.enabled || busy} title={action.disabled_reason ?? undefined}>{action.label}</button>)}
                    </div>

                    <div className="p-5"><AuditTimeline events={workspace.timeline} /></div>
                  </Tabs>
                </div>
              </>
            ) : !forbidden && !error ? (
              <div className="card py-12 text-center text-sm text-slate-400">Select an authorised application to view its documentation.</div>
            ) : null}
          </div>
        </div>
      )}

      {workspace && <DocumentPackModal isOpen={packOpen} onClose={() => setPackOpen(false)} applicationReference={workspace.application_reference_number || 'Reference pending'} borrowerName={workspace.borrower_name} checklistStatus={workspace.checklist_status} blockerCount={workspace.blockers.length} summary={workspace.pack_summary} items={workspace.items} onDownload={item => void download(item)} onAction={startAction} />}
      <Modal
        isOpen={Boolean(pendingAction)}
        onClose={() => !busy && setPendingAction(null)}
        title={pendingAction?.label ?? 'Documentation action'}
        subtitle="The server will revalidate the current locked documentation snapshot."
        footer={<><button className="btn-secondary" onClick={() => setPendingAction(null)} disabled={busy}>Cancel</button><button className="btn-primary" onClick={confirmAction} disabled={busy}>Confirm action</button></>}
      >
        <div className="space-y-4">
          {(pendingAction?.fields ?? []).map(field => (
            <label key={field.name} className="block text-sm font-medium text-slate-700">
              {field.label}
              {field.type === 'textarea' ? (
                <textarea aria-label={field.label} className="input-field mt-2 min-h-24" value={actionValues[field.name] ?? ''} onChange={event => setActionValues(values => ({ ...values, [field.name]: event.target.value }))} />
              ) : field.type === 'select' ? (
                <select aria-label={field.label} className="input-field mt-2" value={actionValues[field.name] ?? ''} onChange={event => setActionValues(values => ({ ...values, [field.name]: event.target.value }))}>{(field.options ?? []).map(option => <option key={option} value={option}>{display(option)}</option>)}</select>
              ) : field.type === 'file' ? (
                <input aria-label={field.label} type="file" accept=".pdf,.jpg,.jpeg,.png,.doc,.docx" className="mt-1.5 block w-full text-sm text-slate-500" onChange={event => {
                  const file = event.target.files?.[0];
                  setActionFiles(files => {
                    if (file) return { ...files, [field.name]: file };
                    const next = { ...files }; delete next[field.name]; return next;
                  });
                }} />
              ) : (
                <input aria-label={field.label} type={field.type} className="input-field mt-2" value={actionValues[field.name] ?? ''} onChange={event => setActionValues(values => ({ ...values, [field.name]: event.target.value }))} />
              )}
              {fieldErrors[field.name] && <span className="text-xs text-red-600 mt-1 block">{fieldErrors[field.name]}</span>}
            </label>
          ))}
        </div>
      </Modal>
    </div>
  );
};

export default DocumentationHub;
