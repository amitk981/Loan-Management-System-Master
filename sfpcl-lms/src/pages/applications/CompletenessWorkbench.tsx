import React, { useCallback, useEffect, useMemo, useState } from 'react';
import {
  AlertTriangle,
  ArrowRight,
  CheckCircle2,
  ClipboardList,
  FileText,
  Info,
  RefreshCw,
  Send,
  XCircle,
} from 'lucide-react';
import StatusBadge from '../../components/ui/StatusBadge';
import { useRole } from '../../contexts/RoleContext';
import { AuthSessionError } from '../../services/authSession';
import {
  createApplicationRejectionNote,
  fetchApplicationCompleteness,
  fetchApplicationDeficiencies,
  fetchApplicationDocumentChecklist,
  fetchStaffApplications,
  passApplicationCompleteness,
  resolveApplicationDeficiency,
  returnApplicationWithDeficiencies,
  type ApplicationCompleteness,
  type ApplicationDeficiency,
  type StaffApplication,
} from '../../services/applicationIntakeApi';

type LoadStatus = 'loading' | 'success' | 'empty' | 'error' | 'unauthorized' | 'validation' | 'stale';
type BusyAction = 'pass' | 'return' | 'reject' | `resolve:${string}` | null;

interface CompletenessWorkbenchProps {
  initialSelectedId?: string;
  onOpenApplication: (id: string) => void;
  onOpenAppraisal: (id: string) => void;
}

interface CompletenessWorkbenchViewProps {
  status: LoadStatus;
  message: string;
  applications: StaffApplication[];
  selectedId: string | null;
  completeness: ApplicationCompleteness | null;
  deficiencies: ApplicationDeficiency[];
  canAct: boolean;
  comment: string;
  reasons: Record<string, string>;
  rejectionCategory: string;
  reapplyAllowed: boolean;
  busyAction: BusyAction;
  onSelect: (id: string) => void;
  onCommentChange: (value: string) => void;
  onReasonChange: (itemCode: string, value: string) => void;
  onRejectionCategoryChange: (value: string) => void;
  onReapplyAllowedChange: (value: boolean) => void;
  onPass: () => void;
  onReturn: () => void;
  onReject: () => void;
  onResolve: (deficiencyId: string) => void;
  onRetry: () => void;
  onOpenApplication: (id: string) => void;
  onOpenAppraisal: (id: string) => void;
}

const COMPLETE_CHECK_PERMISSION = 'applications.loan_application.complete_check';

const documentLabel = (code: string) => code
  .replace(/_/g, ' ')
  .replace(/\b\w/g, letter => letter.toUpperCase())
  .replace(/\bPan\b/g, 'PAN')
  .replace(/\bKyc\b/g, 'KYC');

const money = (value: string | null) => value
  ? `₹${Number(value).toLocaleString('en-IN', { maximumFractionDigits: 2 })}`
  : '—';

const date = (value?: string | null) => value
  ? new Date(value).toLocaleDateString('en-IN')
  : '—';

const queueStatusLabel = (status: string) => status === 'submitted'
  ? 'Pending Completeness'
  : status === 'incomplete_returned'
    ? 'Returned for Rectification'
    : status.replace(/_/g, ' ');

const errorState = (error: unknown): { status: LoadStatus; message: string } => {
  if (!(error instanceof AuthSessionError)) {
    return { status: 'error', message: 'Completeness data could not be loaded. Please retry.' };
  }
  if (error.status === 401 || error.status === 403) {
    return { status: 'unauthorized', message: 'You are not authorised to access this completeness review.' };
  }
  if (error.status === 409) {
    return { status: 'stale', message: 'This application changed on the server. Refresh before taking another action.' };
  }
  if (error.status === 400) {
    const fields = Object.entries(error.fieldErrors ?? {})
      .map(([field, value]) => `${field}: ${typeof value === 'string' ? value : JSON.stringify(value)}`)
      .join(' · ');
    return { status: 'validation', message: fields || error.message };
  }
  return { status: 'error', message: error.message };
};

const CompletenessWorkbench: React.FC<CompletenessWorkbenchProps> = ({
  initialSelectedId,
  onOpenApplication,
  onOpenAppraisal,
}) => {
  const { currentUser } = useRole();
  const [status, setStatus] = useState<LoadStatus>('loading');
  const [message, setMessage] = useState('');
  const [applications, setApplications] = useState<StaffApplication[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [completeness, setCompleteness] = useState<ApplicationCompleteness | null>(null);
  const [deficiencies, setDeficiencies] = useState<ApplicationDeficiency[]>([]);
  const [comment, setComment] = useState('');
  const [reasons, setReasons] = useState<Record<string, string>>({});
  const [rejectionCategory, setRejectionCategory] = useState('missing_document');
  const [reapplyAllowed, setReapplyAllowed] = useState(true);
  const [busyAction, setBusyAction] = useState<BusyAction>(null);

  const loadSelected = useCallback(async (applicationId: string) => {
    setStatus('loading');
    setMessage('');
    try {
      const [, nextCompleteness, nextDeficiencies] = await Promise.all([
        fetchApplicationDocumentChecklist(applicationId),
        fetchApplicationCompleteness(applicationId),
        fetchApplicationDeficiencies(applicationId),
      ]);
      setCompleteness(nextCompleteness);
      setDeficiencies(nextDeficiencies.items);
      setReasons(Object.fromEntries(nextCompleteness.required_checklist_items
        .filter(item => !item.complete)
        .map(item => [item.document_type, ''])));
      setStatus('success');
    } catch (error) {
      const next = errorState(error);
      setStatus(next.status);
      setMessage(next.message);
      setCompleteness(null);
      setDeficiencies([]);
    }
  }, []);

  const loadQueue = useCallback(async () => {
    setStatus('loading');
    setMessage('');
    try {
      const [submitted, returned] = await Promise.all([
        fetchStaffApplications({ applicationStatus: 'submitted', ordering: 'application_date', pageSize: 100 }),
        fetchStaffApplications({ applicationStatus: 'incomplete_returned', ordering: 'application_date', pageSize: 100 }),
      ]);
      const queue = [...submitted.items, ...returned.items];
      setApplications(queue);
      if (queue.length === 0) {
        setSelectedId(null);
        setCompleteness(null);
        setDeficiencies([]);
        setStatus('empty');
        return;
      }
      const selected = queue.find(item =>
        item.loan_application_id === initialSelectedId
        || item.application_reference_number === initialSelectedId)
        ?? queue[0];
      setSelectedId(selected.loan_application_id);
      await loadSelected(selected.loan_application_id);
    } catch (error) {
      const next = errorState(error);
      setStatus(next.status);
      setMessage(next.message);
      setApplications([]);
    }
  }, [initialSelectedId, loadSelected]);

  useEffect(() => {
    void loadQueue();
  }, [loadQueue]);

  const refreshAfterAction = useCallback(async () => {
    if (!selectedId) return;
    const detail = await fetchApplicationCompleteness(selectedId);
    const history = await fetchApplicationDeficiencies(selectedId);
    setCompleteness(detail);
    setDeficiencies(history.items);
    setApplications(items => items.map(item => item.loan_application_id === selectedId
      ? {
          ...item,
          application_reference_number: detail.application_reference_number,
          application_status: detail.application_status,
          current_stage: detail.current_stage,
          completeness_status: detail.completeness_status,
        }
      : item));
    setStatus('success');
    setMessage('');
  }, [selectedId]);

  const runAction = useCallback(async (action: Exclude<BusyAction, null>, task: () => Promise<unknown>) => {
    setBusyAction(action);
    setMessage('');
    try {
      await task();
      await refreshAfterAction();
    } catch (error) {
      const next = errorState(error);
      setStatus(next.status);
      setMessage(next.message);
    } finally {
      setBusyAction(null);
    }
  }, [refreshAfterAction]);

  const pass = () => selectedId && runAction('pass', () => passApplicationCompleteness(selectedId));
  const returnWithDeficiencies = () => selectedId && completeness && runAction('return', () =>
    returnApplicationWithDeficiencies(selectedId, {
      communication_mode: 'email',
      message: comment,
      items: completeness.blocking_document_types.map(itemCode => ({
        item_code: itemCode,
        remarks: reasons[itemCode]?.trim() || undefined,
      })),
    }));
  const reject = () => selectedId && runAction('reject', () => createApplicationRejectionNote(selectedId, {
    rejection_stage: 'completeness',
    rejection_reason_category: rejectionCategory,
    detailed_reason: comment,
    reapply_allowed_flag: reapplyAllowed,
    communication_mode: 'email',
  }));
  const resolve = (deficiencyId: string) => runAction(`resolve:${deficiencyId}`, () =>
    resolveApplicationDeficiency(deficiencyId, { resolution_notes: comment }));

  const canAct = currentUser.permissions.includes(COMPLETE_CHECK_PERMISSION);

  return (
    <CompletenessWorkbenchView
      status={status}
      message={message}
      applications={applications}
      selectedId={selectedId}
      completeness={completeness}
      deficiencies={deficiencies}
      canAct={canAct}
      comment={comment}
      reasons={reasons}
      rejectionCategory={rejectionCategory}
      reapplyAllowed={reapplyAllowed}
      busyAction={busyAction}
      onSelect={id => {
        setSelectedId(id);
        setComment('');
        void loadSelected(id);
      }}
      onCommentChange={setComment}
      onReasonChange={(itemCode, value) => setReasons(current => ({ ...current, [itemCode]: value }))}
      onRejectionCategoryChange={setRejectionCategory}
      onReapplyAllowedChange={setReapplyAllowed}
      onPass={pass}
      onReturn={returnWithDeficiencies}
      onReject={reject}
      onResolve={resolve}
      onRetry={loadQueue}
      onOpenApplication={onOpenApplication}
      onOpenAppraisal={onOpenAppraisal}
    />
  );
};

export const CompletenessWorkbenchView: React.FC<CompletenessWorkbenchViewProps> = ({
  status,
  message,
  applications,
  selectedId,
  completeness,
  deficiencies,
  canAct,
  comment,
  reasons,
  rejectionCategory,
  reapplyAllowed,
  busyAction,
  onSelect,
  onCommentChange,
  onReasonChange,
  onRejectionCategoryChange,
  onReapplyAllowedChange,
  onPass,
  onReturn,
  onReject,
  onResolve,
  onRetry,
  onOpenApplication,
  onOpenAppraisal,
}) => {
  const selected = applications.find(item => item.loan_application_id === selectedId) ?? null;
  const checklist = completeness?.required_checklist_items ?? [];
  const completeCount = checklist.filter(item => item.complete).length;
  const blockers = completeness?.blocking_document_types ?? [];
  const openDeficiencies = deficiencies.filter(item => item.resolution_status === 'open');
  const readyCount = applications.filter(item => item.completeness_status === 'complete').length
    + (completeness?.can_generate_reference ? 1 : 0);
  const showStateAlert = ['error', 'unauthorized', 'validation', 'stale'].includes(status);

  if (status === 'loading') {
    return <div className="p-6"><div className="card text-center py-16 text-slate-500">Loading completeness queue…</div></div>;
  }
  if (status === 'empty') {
    return (
      <div className="p-6">
        <div className="card text-center py-16">
          <CheckCircle2 size={32} className="text-green-500 mx-auto mb-3" />
          <p className="text-slate-600 font-semibold">Completeness queue is clear</p>
          <p className="text-slate-400 text-sm mt-1">No submitted or returned applications are waiting for review.</p>
        </div>
      </div>
    );
  }
  if (!selected || !completeness) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-sm text-red-800">
          <p>{message || 'Completeness data could not be loaded.'}</p>
          <button onClick={onRetry} className="btn-secondary mt-3 flex items-center gap-2"><RefreshCw size={14} /> Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-4">
      <div>
        <h1 className="text-xl font-bold text-slate-900">Application Completeness Check</h1>
        <p className="text-sm text-slate-500 mt-0.5">S12 review · {applications.length} application{applications.length === 1 ? '' : 's'} awaiting completeness decision</p>
      </div>

      {!canAct && (
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 text-sm text-amber-800 flex items-center gap-2">
          <Info size={16} /> Read-only. Your signed-in account does not have completeness-check permission.
        </div>
      )}
      {showStateAlert && (
        <div className={`${status === 'stale' ? 'bg-amber-50 border-amber-200 text-amber-800' : 'bg-red-50 border-red-200 text-red-800'} border rounded-lg p-3 text-sm flex items-start justify-between gap-3`}>
          <span>{message}</span>
          <button onClick={onRetry} className="font-semibold">Refresh</button>
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        {[
          ['Applications in Queue', applications.length],
          ['Ready for Reference', readyCount],
          ['Checklist Items Pending', blockers.length],
          ['Open Deficiencies', openDeficiencies.length],
        ].map(([label, value]) => (
          <div key={label} className="card">
            <p className="text-xs text-slate-500 font-medium uppercase tracking-wide">{label}</p>
            <p className="text-2xl font-bold text-slate-900 mt-1 num">{value}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="card p-0 overflow-hidden lg:col-span-1">
          <div className="p-4 bg-slate-50 border-b border-slate-200">
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Completeness Queue ({applications.length})</p>
          </div>
          <div className="divide-y divide-slate-100">
            {applications.map(item => (
              <button
                key={item.loan_application_id}
                onClick={() => onSelect(item.loan_application_id)}
                className={`w-full block p-4 hover:bg-slate-50 transition-colors text-left ${selectedId === item.loan_application_id ? 'bg-green-50 border-l-4 border-l-green-500' : ''}`}
              >
                <p className="font-semibold text-slate-900 num text-sm truncate">{item.application_reference_number || item.loan_application_id}</p>
                <p className="text-xs text-slate-500 truncate mt-1">{item.member.display_name}</p>
                <p className="text-xs text-slate-400 num mt-1">{money(item.required_loan_amount)}</p>
                <div className="mt-2"><StatusBadge label={queueStatusLabel(item.application_status)} family={item.application_status === 'submitted' ? 'info' : 'blocked'} size="sm" /></div>
              </button>
            ))}
          </div>
        </div>

        <div className="lg:col-span-2 space-y-4">
          <div className="card space-y-4">
            <div className="flex items-start justify-between gap-4">
              <div>
                <div className="flex items-center gap-2 flex-wrap">
                  <h2 className="text-lg font-bold text-slate-900 num">{completeness.application_reference_number || selected.loan_application_id}</h2>
                  <StatusBadge label={queueStatusLabel(completeness.application_status)} />
                </div>
                <p className="text-sm text-slate-500 mt-0.5">{completeness.member.display_name} · Applied {date(selected.application_date)}</p>
              </div>
              <button onClick={() => onOpenApplication(selected.loan_application_id)} className="btn-secondary flex items-center gap-2"><FileText size={14} /> Full Application</button>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {[
                ['Folio', completeness.member.folio_number || '—'],
                ['Member Type', documentLabel(completeness.member.member_type)],
                ['KYC Status', completeness.member.kyc_status || '—'],
                ['Requested Amount', money(selected.required_loan_amount)],
                ['Purpose', selected.declared_purpose || documentLabel(selected.purpose_category)],
                ['Nominee Status', documentLabel(completeness.nominee_selection_status)],
                ['Completeness', documentLabel(completeness.completeness_status)],
                ['Current Stage', documentLabel(completeness.current_stage)],
              ].map(([label, value]) => (
                <div key={label} className="bg-slate-50 rounded-lg p-3">
                  <p className="text-xs text-slate-500 font-medium uppercase tracking-wide">{label}</p>
                  <p className="text-sm font-semibold text-slate-900 mt-0.5 truncate">{value}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="card p-0 overflow-hidden">
            <div className="px-5 py-3 bg-slate-50 border-b border-slate-100 flex items-center justify-between">
              <p className="text-xs font-semibold text-slate-600 uppercase tracking-wide flex items-center gap-2"><ClipboardList size={15} /> Mandatory Completeness Checklist</p>
              <span className="text-xs text-slate-500">{completeCount}/{checklist.length} verified</span>
            </div>
            <div className="divide-y divide-slate-100">
              {checklist.map(item => (
                <div key={item.document_type} className={`px-5 py-4 ${item.complete ? 'bg-green-50/30' : 'bg-red-50'}`}>
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="text-sm font-semibold text-slate-800">{documentLabel(item.document_type)}</p>
                      <p className="text-xs text-slate-500 mt-1">Submission: {documentLabel(item.submission_status || 'missing')} · Verification: {documentLabel(item.verification_status || 'pending')}</p>
                      {!item.complete && <p className="text-xs text-red-700 mt-1">{documentLabel(item.reason_code || 'incomplete')}</p>}
                    </div>
                    <StatusBadge label={item.complete ? 'complete' : 'deficiency_raised'} size="sm" />
                  </div>
                  {!item.complete && canAct && (
                    <input
                      value={reasons[item.document_type] || ''}
                      onChange={event => onReasonChange(item.document_type, event.target.value)}
                      placeholder="Optional deficiency remark"
                      className="mt-3 w-full text-xs border border-red-200 rounded px-2.5 py-1.5 bg-white text-red-800"
                    />
                  )}
                </div>
              ))}
            </div>
          </div>

          <div className="card space-y-4">
            <div className="flex items-center justify-between gap-3">
              <h3 className="font-semibold text-slate-800">Deficiency history</h3>
              <StatusBadge label={openDeficiencies.length ? 'deficiency_raised' : 'complete'} size="sm" />
            </div>
            {deficiencies.length === 0 ? (
              <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 text-sm text-slate-700">No deficiencies have been recorded for this application.</div>
            ) : deficiencies.map(item => (
              <div key={item.deficiency_id} className="bg-slate-50 border border-slate-200 rounded-lg p-3 flex items-start justify-between gap-3">
                <div>
                  <p className="text-sm font-semibold text-slate-800">{documentLabel(item.item_code)}</p>
                  <p className="text-xs text-slate-600 mt-1">{item.description}</p>
                  {item.remarks && <p className="text-xs text-slate-500 mt-1">{item.remarks}</p>}
                  {item.resolution_notes && <p className="text-xs text-green-700 mt-1">{item.resolution_notes}</p>}
                </div>
                <div className="flex flex-col items-end gap-2">
                  <StatusBadge label={item.resolution_status} size="sm" />
                  {canAct && item.resolution_status === 'open' && (
                    <button disabled={!comment.trim() || busyAction !== null} onClick={() => onResolve(item.deficiency_id)} className="btn-secondary text-xs">Resolve</button>
                  )}
                </div>
              </div>
            ))}

            {canAct && (
              <>
                <textarea
                  value={comment}
                  onChange={event => onCommentChange(event.target.value)}
                  rows={2}
                  placeholder="Required communication, rejection reason, or resolution notes"
                  className="w-full text-sm border border-slate-200 rounded-lg px-3 py-2 text-slate-700 resize-none"
                />
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <label className="text-xs text-slate-600">Rejection category
                    <select value={rejectionCategory} onChange={event => onRejectionCategoryChange(event.target.value)} className="mt-1 w-full border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-700">
                      <option value="missing_document">Missing document</option>
                      <option value="eligibility">Eligibility</option>
                      <option value="purpose_mismatch">Purpose mismatch</option>
                      <option value="other">Other</option>
                    </select>
                  </label>
                  <label className="text-sm text-slate-700 flex items-center gap-2 pt-5">
                    <input type="checkbox" checked={reapplyAllowed} onChange={event => onReapplyAllowedChange(event.target.checked)} /> Reapplication allowed
                  </label>
                </div>
                <div className="border-t border-slate-100 pt-4 flex items-center justify-end gap-3 flex-wrap">
                  {completeness.can_generate_reference && (
                    <button disabled={busyAction !== null} onClick={onPass} className="btn-primary flex items-center gap-2"><ArrowRight size={14} /> Generate reference number</button>
                  )}
                  {blockers.length > 0 && (
                    <button disabled={!comment.trim() || busyAction !== null} onClick={onReturn} className="btn-secondary flex items-center gap-2"><Send size={14} /> Return for deficiency</button>
                  )}
                  {completeness.application_status === 'submitted' && (
                    <button disabled={!comment.trim() || busyAction !== null} onClick={onReject} className="btn-destructive flex items-center gap-2"><XCircle size={14} /> Recommend rejection</button>
                  )}
                </div>
              </>
            )}

            {completeness.application_reference_number && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <p className="text-sm font-semibold text-green-800 flex items-center gap-2"><CheckCircle2 size={15} /> Reference generated · {completeness.application_reference_number}</p>
                <button onClick={() => onOpenAppraisal(selected.loan_application_id)} className="btn-secondary mt-3 flex items-center gap-2"><ArrowRight size={14} /> Open appraisal</button>
              </div>
            )}
            {status === 'validation' && <p className="text-xs text-red-700 flex items-center gap-1"><AlertTriangle size={13} /> {message}</p>}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CompletenessWorkbench;
