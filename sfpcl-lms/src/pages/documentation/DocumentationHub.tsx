import React, { useCallback, useEffect, useRef, useState } from 'react';
import { AlertTriangle, Check, ClipboardList, FileText, FolderOpen, Lock, RefreshCw, Shield } from 'lucide-react';
import DocumentChecklist from '../../components/loan/DocumentChecklist';
import DocumentPackModal from '../../components/loan/DocumentPackModal';
import Modal from '../../components/ui/Modal';
import StageStepper, { type Step } from '../../components/ui/StageStepper';
import StatusBadge from '../../components/ui/StatusBadge';
import Tabs from '../../components/ui/Tabs';
import { fetchStaffApplications, type StaffApplication } from '../../services/applicationIntakeApi';
import { AuthSessionError } from '../../services/authSession';
import { downloadStaffDocument, fetchDocumentationWorkspace, openStaffDocumentBlob, submitDocumentationAction, type DocumentationAction, type DocumentationItem, type DocumentationWorkspace } from '../../services/documentationWorkspaceApi';

interface DocumentationHubProps { onOpenApplication: (id: string) => void; initialSelectedId?: string }

const display = (value: string) => value.replace(/_/g, ' ').replace(/\b\w/g, char => char.toUpperCase());
const workflowLabel = (code: string) => ({ power_of_attorney: 'Power of Attorney', tri_party_agreement: 'Tri-Party Agreement', sh4: 'SH-4', cdsl_pledge: 'CDSL Pledge', blank_dated_cheque: 'Blank-Dated Cheque', cancelled_cheque: 'Cancelled Cheque' }[code] ?? display(code));
const actionLabel = (action: string) => ({ approve_as_company_secretary: 'Approve as Company Secretary', approve_as_credit_manager: 'Approve as Credit Manager', approve_as_sanction_committee: 'Approve as Sanction Committee', generate_document: 'Generate document', complete_item: 'Mark complete', verify_document: 'Verify document' }[action] ?? display(action));

const DocumentationHub: React.FC<DocumentationHubProps> = ({ onOpenApplication, initialSelectedId }) => {
  const [queue, setQueue] = useState<StaffApplication[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [workspace, setWorkspace] = useState<DocumentationWorkspace | null>(null);
  const [loading, setLoading] = useState(true);
  const [workspaceLoading, setWorkspaceLoading] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [forbidden, setForbidden] = useState(false);
  const [packOpen, setPackOpen] = useState(false);
  const [pendingAction, setPendingAction] = useState<DocumentationAction | null>(null);
  const [comments, setComments] = useState('');
  const [lastActionId, setLastActionId] = useState<string | null>(null);
  const requestSequence = useRef(0);

  useEffect(() => {
    let active = true; setLoading(true);
    fetchStaffApplications({ applicationStatus: 'approved_by_sanction_committee', pageSize: 100 })
      .then(result => {
        if (!active) return;
        setQueue(result.items);
        const selected = result.items.find(item => item.loan_application_id === initialSelectedId || item.application_reference_number === initialSelectedId) ?? result.items[0];
        setSelectedId(selected?.loan_application_id ?? null);
      })
      .catch(reason => active && setError(reason instanceof Error ? reason.message : 'Documentation queue could not be loaded.'))
      .finally(() => active && setLoading(false));
    return () => { active = false; };
  }, [initialSelectedId]);

  const loadWorkspace = useCallback(async (applicationId: string) => {
    const sequence = ++requestSequence.current; setWorkspaceLoading(true); setError(null); setForbidden(false);
    try { const result = await fetchDocumentationWorkspace(applicationId); if (sequence === requestSequence.current) setWorkspace(result); } catch (reason) {
      if (sequence !== requestSequence.current) return;
      setWorkspace(null); if (reason instanceof AuthSessionError && reason.status === 403) setForbidden(true); else setError(reason instanceof Error ? reason.message : 'Documentation workspace could not be loaded.');
    } finally { if (sequence === requestSequence.current) setWorkspaceLoading(false); }
  }, []);

  useEffect(() => {
    if (selectedId) void loadWorkspace(selectedId); else setWorkspace(null);
  }, [loadWorkspace, selectedId]);

  const runAction = async (action: DocumentationAction, payload: Record<string, unknown>) => {
    if (!selectedId) return;
    setBusy(true); setError(null);
    try { const result = await submitDocumentationAction(action, payload);
      setLastActionId(typeof result.checklist_action_id === 'string' ? result.checklist_action_id : null);
      setPendingAction(null); setComments(''); await loadWorkspace(selectedId);
    } catch (reason) { setError(reason instanceof Error ? reason.message : 'Documentation action could not be completed.'); } finally { setBusy(false); }
  };

  const startAction = (action: DocumentationAction) => {
    if (action.action === 'generate_document') {
      void runAction(action, { document_type: action.document_type, template_id: action.template_id, output_format: action.output_formats?.[0] });
      return;
    }
    if (action.action.startsWith('manage_')) {
      if (selectedId) onOpenApplication(selectedId);
      return;
    }
    setComments(''); setPendingAction(action);
  };

  const confirmAction = () => {
    if (!pendingAction || !comments.trim()) return;
    const payload = pendingAction.action === 'complete_item' ? { loan_document_id: pendingAction.loan_document_id, remarks: comments.trim() } : pendingAction.action === 'verify_document' ? { verification_status: 'verified', remarks: comments.trim() } : { comments: comments.trim() };
    void runAction(pendingAction, payload);
  };

  const download = async (item: DocumentationItem) => {
    const action = item.document?.download; if (!action) return; setError(null);
    try { openStaffDocumentBlob(await downloadStaffDocument(action)); } catch (reason) { setError(reason instanceof Error ? reason.message : 'The document could not be downloaded.'); }
  };

  const approvalSteps: Step[] = (workspace?.approval_stages ?? []).map((stage, index) => ({ id: stage.role, label: display(stage.role), sublabel: index === 3 ? 'Post-disbursement' : undefined, state: stage.status === 'signed' ? 'completed' : index === (workspace?.approval_stages.findIndex(row => row.status === 'pending') ?? -1) ? 'in_progress' : 'not_started' }));

  if (loading) return <div className="card text-sm text-slate-500">Loading documentation queue…</div>;

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Documentation Hub</h1>
          <p className="text-sm text-slate-500 mt-0.5">{queue.length} application{queue.length !== 1 ? 's' : ''} pending documentation</p>
        </div>
      </div>

      {error && <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">{error}</div>}
      {forbidden && <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg text-sm text-amber-800 flex items-center gap-2"><Lock size={15} /> You are not authorised to open this documentation workspace.</div>}
      {lastActionId && !error && <div className="p-3 bg-green-50 border border-green-200 rounded-lg text-sm text-green-800">Action accepted. The canonical documentation snapshot was refreshed.</div>}

      {queue.length === 0 ? (
        <div className="card text-center py-16"><Check size={32} className="text-green-500 mx-auto mb-3" /><p className="text-slate-600 font-semibold">All documentation is complete</p></div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-[300px_minmax(0,1fr)] gap-6">

          <div className="card p-0 overflow-hidden">
            <div className="p-4 bg-slate-50 border-b border-slate-200"><p className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Doc Queue ({queue.length})</p></div>
            <div className="divide-y divide-slate-100">
              {queue.map(a => (
                <button key={a.loan_application_id} onClick={() => setSelectedId(a.loan_application_id)} className={`w-full flex items-start gap-3 p-4 hover:bg-slate-50 transition-colors text-left border-l-4 ${selectedId === a.loan_application_id ? 'bg-green-50 border-l-green-500' : 'bg-white border-l-transparent'}`}>
                  <FolderOpen size={16} className="text-amber-500 flex-shrink-0 mt-0.5" />
                  <div className="min-w-0"><div className="font-semibold text-slate-900 text-sm truncate">{a.application_reference_number || 'Reference pending'}</div><div className="text-xs text-slate-500 truncate mt-0.5">{a.member.display_name}</div></div>
                </button>
              ))}
            </div>
          </div>

          <div className="space-y-4 min-w-0">
            {workspaceLoading ? (
              <div className="card py-12 text-center text-sm text-slate-500">Loading canonical documentation snapshot…</div>
            ) : workspace ? (
              <>
                {/* App header card */}
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
                      <button
                        className="btn-secondary flex items-center gap-2 flex-shrink-0"
                        onClick={() => setPackOpen(true)}
                      >
                        <FolderOpen size={14} />
                        View Document Pack
                      </button>
                      <button className="btn-secondary flex items-center gap-2" onClick={() => void loadWorkspace(workspace.loan_application_id)} disabled={workspaceLoading}>
                        <RefreshCw size={14} /> Refresh
                      </button>
                    </div>
                  </div>

                  {/* Stage stepper */}
                  <div className="mt-4">
                    <StageStepper steps={approvalSteps} />
                  </div>
                </div>

                {workspace.blockers.length > 0 && (
                  <div className="flex items-start gap-2 bg-red-50 border border-red-200 rounded-lg px-4 py-3">
                    <AlertTriangle size={16} className="text-red-600 flex-shrink-0 mt-0.5" />
                    <p className="text-sm text-red-800 font-medium">Disbursement blocked: {workspace.blockers.map(row => `${row.label}: ${display(row.reason)}`).join(' · ')}</p>
                  </div>
                )}

                {/* Tab panel */}
                <div className="card p-0 overflow-hidden">
                  <Tabs tabs={[
                    { id: 'checklist', label: 'Checklist', badge: workspace.blockers.length ? `${workspace.blockers.length} pending` : undefined, badgeStyle: workspace.blockers.length ? 'warning' : undefined },
                    { id: 'documents', label: 'Documents' },
                    { id: 'security', label: 'Securities' },
                    { id: 'approvals', label: 'Approvals' },
                    { id: 'audit', label: 'Audit Trail' },
                  ]}>
                    {/* ─ Tab 0: Checklist ─ */}
                    <div className="p-5">
                      <div className="mb-3 flex items-center justify-between">
                        <div>
                          <h3 className="text-sm font-semibold text-slate-900 flex items-center gap-2">
                            <ClipboardList size={14} /> Document Checklist
                          </h3>
                          <p className="text-xs text-slate-500 mt-0.5">All required items before disbursement can proceed.</p>
                        </div>
                      </div>
                      <DocumentChecklist items={workspace.items} busy={busy} onDownload={item => void download(item)} onAction={startAction} />
                    </div>

                    {/* ─ Tab 1: Documents ─ */}
                    <div className="p-5 space-y-2">
                      {workspace.items.map(item => <div key={item.item_code} className="rounded-lg border border-slate-200 bg-white p-3 flex items-center justify-between gap-3"><div><p className="text-sm font-medium text-slate-900">{item.item_label}</p><p className="text-xs text-slate-500 mt-0.5">{item.document ? `Template version ${item.document.version}` : 'No current generated document'}</p></div><StatusBadge label={!item.applicable ? 'not_required' : item.status} size="sm" /></div>)}
                    </div>

                    {/* ─ Tab 2: Securities ─ */}
                    <div className="p-5">
                      <div className="mb-4 flex items-center justify-between">
                        <h3 className="text-sm font-semibold text-slate-900 flex items-center gap-2">
                          <Shield size={14} /> Security Instruments
                        </h3>
                      </div>
                      <div className="space-y-2">{Object.entries(workspace.security_workflows).map(([code, workflow]) => <div key={code} className="rounded-lg border border-slate-200 bg-white"><div className="flex items-center gap-3 p-3"><div className="w-8 h-8 rounded-lg bg-slate-100 flex items-center justify-center"><Shield size={14} className="text-slate-500" /></div><div className="flex-1"><div className="text-sm font-medium text-slate-900">{workflowLabel(code)}</div><div className="text-xs text-slate-500 mt-0.5">{workflow.required ? 'Required for this sanctioned package' : 'Not applicable'}</div></div><StatusBadge label={workflow.status} size="sm" />{workflow.available_actions.map(action => <button key={action.action} className="btn-secondary text-xs" onClick={() => startAction(action)}>{actionLabel(action.action)}</button>)}</div></div>)}</div>
                    </div>

                    {/* ─ Tab 3: Approvals (S35) ─ */}
                    <div className="p-5 space-y-4">
                      <div className="border border-slate-200 rounded-xl p-4 bg-slate-50"><StageStepper steps={approvalSteps} /></div>
                      {workspace.available_actions.map(action => <button key={action.action} className="btn-primary text-xs" onClick={() => startAction(action)} disabled={busy}>{actionLabel(action.action)}</button>)}
                    </div>

                    {/* ─ Tab 4: Audit Trail ─ */}
                    <div className="p-5 space-y-4">
                      <div className="text-center py-8 text-slate-400 text-sm">No audit events recorded yet.</div>
                    </div>
                  </Tabs>
                </div>
              </>
            ) : <div className="card py-12 text-center text-sm text-slate-400">Select an authorised application to view its documentation.</div>}
          </div>
        </div>
      )}

      {workspace && <DocumentPackModal isOpen={packOpen} onClose={() => setPackOpen(false)} applicationReference={workspace.application_reference_number || 'Reference pending'} borrowerName={workspace.borrower_name} checklistStatus={workspace.checklist_status} blockerCount={workspace.blockers.length} summary={workspace.pack_summary} items={workspace.items} onDownload={item => void download(item)} onAction={startAction} />}
      <Modal isOpen={Boolean(pendingAction)} onClose={() => !busy && setPendingAction(null)} title={pendingAction ? actionLabel(pendingAction.action) : 'Documentation action'} subtitle="The server will revalidate the current locked documentation snapshot." footer={<><button className="btn-secondary" onClick={() => setPendingAction(null)} disabled={busy}>Cancel</button><button className="btn-primary" onClick={confirmAction} disabled={busy || !comments.trim()}>Confirm action</button></>}>
        <label className="block text-sm font-medium text-slate-700">Action comments<textarea aria-label="Action comments" className="input-field mt-2 min-h-24" value={comments} onChange={event => setComments(event.target.value)} /></label>
      </Modal>
    </div>
  );
};

export default DocumentationHub;
