import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { AlertCircle, AlertOctagon, Check, CheckCircle2, FileText, Gavel, RefreshCw, Shield } from 'lucide-react';
import AlertBanner from '../../components/ui/AlertBanner';
import StatusBadge from '../../components/ui/StatusBadge';
import ApprovalPanel from '../../components/loan/ApprovalPanel';
import Modal from '../../components/ui/Modal';
import { useRole } from '../../contexts/RoleContext';
import { AuthSessionError } from '../../services/authSession';
import {
  fetchApprovalCase,
  fetchSanctionDecision,
  listApprovalCases,
  recordApprovalAction,
  recordGeneralMeetingApproval,
  uploadGeneralMeetingDocument,
  type ApprovalAvailableAction,
  type ApprovalCase,
  type SanctionDecision,
} from '../../services/sanctionApi';

type WorkbenchStatus = 'loading' | 'success' | 'empty' | 'unauthorized' | 'denied' | 'validation' | 'stale' | 'error';

interface SanctionWorkbenchProps {
  onOpenApplication: (id: string) => void;
  initialSelectedId?: string;
}

const money = (value: string | null | undefined) => value ? `₹${Number(value).toLocaleString('en-IN', { minimumFractionDigits: 2 })}` : '—';
const text = (value: unknown) => value === null || value === undefined || value === '' ? 'Not recorded' : String(value).replace(/_/g, ' ');
const truth = (value: unknown) => typeof value === 'boolean' ? (value ? 'Confirmed' : 'Not confirmed') : text(value);

const describeError = (error: unknown): { status: WorkbenchStatus; message: string } => {
  if (!(error instanceof AuthSessionError)) return { status: 'error', message: error instanceof Error ? error.message : 'The sanction workbench could not be loaded.' };
  const fields = Object.entries(error.fieldErrors ?? {}).map(([field, message]) => `${field}: ${message}`).join(' ');
  const status: WorkbenchStatus = error.status === 401 ? 'unauthorized' : error.code === 'OBJECT_ACCESS_DENIED' || error.status === 403 ? 'denied' : error.code === 'VALIDATION_ERROR' ? 'validation' : error.code === 'STALE_VERSION' ? 'stale' : 'error';
  return { status, message: `${error.code}: ${error.message}${fields ? ` ${fields}` : ''}` };
};

const authoritySummary = (item: ApprovalCase) => {
  const supplied = item.matrix_projection.authority_summary;
  if (typeof supplied === 'string' && supplied.trim()) return supplied;
  return 'Authority summary not projected by the approval case.';
};

const SanctionWorkbench: React.FC<SanctionWorkbenchProps> = ({ onOpenApplication, initialSelectedId }) => {
  const { currentUser } = useRole();
  const [cases, setCases] = useState<ApprovalCase[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(initialSelectedId ?? null);
  const [selected, setSelected] = useState<ApprovalCase | null>(null);
  const [filter, setFilter] = useState('pending');
  const [status, setStatus] = useState<WorkbenchStatus>('loading');
  const [message, setMessage] = useState('');
  const [busy, setBusy] = useState(false);
  const [decision, setDecision] = useState<SanctionDecision | null>(null);
  const [decisionFieldError, setDecisionFieldError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [showMeetingForm, setShowMeetingForm] = useState(false);
  const [meetingType, setMeetingType] = useState<'director' | 'director_relative' | 'committee_member'>('director_relative');
  const [meetingDescription, setMeetingDescription] = useState('');
  const [meetingDate, setMeetingDate] = useState('');
  const [meetingStatus, setMeetingStatus] = useState<'pending' | 'approved' | 'rejected'>('approved');
  const [meetingFiles, setMeetingFiles] = useState<{ notice: File | null; minutes: File | null; resolution: File | null }>({ notice: null, minutes: null, resolution: null });

  const loadDetail = useCallback(async (caseId: string) => {
    try {
      const detail = await fetchApprovalCase(caseId);
      setSelected(detail);
      setSelectedId(detail.approval_case_id);
      setMessage('');
      setStatus('success');
      setDecision(null);
      if (detail.current_status === 'approved' && currentUser.permissions.includes('approvals.sanction.read')) {
        try { setDecision(await fetchSanctionDecision(detail.loan_application_id)); }
        catch (error) { setMessage(describeError(error).message); }
      }
    } catch (error) {
      const next = describeError(error);
      setStatus(next.status); setMessage(next.message); setSelected(null);
    }
  }, [currentUser.permissions]);

  const loadQueue = useCallback(async (nextFilter = filter) => {
    setStatus('loading'); setMessage('');
    try {
      const items = await listApprovalCases(nextFilter);
      setCases(items);
      const requested = selectedId ? items.find(item => item.approval_case_id === selectedId || item.loan_application_id === selectedId || item.application_reference_number === selectedId) : null;
      const nextId = requested?.approval_case_id ?? items[0]?.approval_case_id ?? null;
      if (!nextId) { setSelected(null); setSelectedId(null); setStatus('empty'); return; }
      await loadDetail(nextId);
    } catch (error) {
      const next = describeError(error);
      setCases([]); setSelected(null); setStatus(next.status); setMessage(next.message);
    }
  }, [filter, loadDetail, selectedId]);

  useEffect(() => { void loadQueue(filter); }, [filter]); // eslint-disable-line react-hooks/exhaustive-deps

  const act = async (action: ApprovalAvailableAction['action_code'], comments: string) => {
    if (!selected) return false;
    setBusy(true); setMessage(''); setDecisionFieldError('');
    try {
      await recordApprovalAction(selected.approval_case_id, action, selected.version, comments);
      const refreshed = await fetchApprovalCase(selected.approval_case_id);
      setSelected(refreshed);
      setCases(previous => previous.map(item => item.approval_case_id === refreshed.approval_case_id ? refreshed : item));
      setStatus('success');
      if (refreshed.current_status === 'approved' && currentUser.permissions.includes('approvals.sanction.read')) {
        setDecision(await fetchSanctionDecision(refreshed.loan_application_id));
      }
      return true;
    } catch (error) {
      if (error instanceof AuthSessionError && error.details && Object.prototype.hasOwnProperty.call(error.details, 'general_meeting_approval')) {
        setSelected(previous => previous ? { ...previous, general_meeting_approval: (error.details?.general_meeting_approval ?? null) as ApprovalCase['general_meeting_approval'] } : previous);
      }
      const next = describeError(error);
      if (error instanceof AuthSessionError && error.fieldErrors?.comments) setDecisionFieldError(error.fieldErrors.comments);
      setStatus(next.status); setMessage(next.message);
      return false;
    } finally { setBusy(false); }
  };

  const canUploadMeetingFiles = currentUser.permissions.includes('documents.file.upload');
  const meetingAction = selected?.available_actions.find(action => action.action_code === 'record_general_meeting_approval');
  const canRecordMeeting = Boolean(meetingAction?.enabled && currentUser.permissions.includes(meetingAction.required_permission));

  const recordMeeting = async () => {
    if (!selected) return;
    setBusy(true); setMessage(''); setSuccessMessage('');
    try {
      const existing = selected.general_meeting_approval;
      const uploadedNewFiles = Boolean(meetingFiles.notice && meetingFiles.minutes && meetingFiles.resolution);
      let ids: string[] = [];
      if (meetingFiles.notice && meetingFiles.minutes && meetingFiles.resolution) {
        ids = await Promise.all([uploadGeneralMeetingDocument(selected.loan_application_id, meetingFiles.notice), uploadGeneralMeetingDocument(selected.loan_application_id, meetingFiles.minutes), uploadGeneralMeetingDocument(selected.loan_application_id, meetingFiles.resolution)]);
      } else if (existing) {
        ids = [existing.notice_document_id, existing.minutes_document_id, existing.resolution_document_id];
      }
      if (ids.length !== 3) return;
      const [notice, minutes, resolution] = ids;
      await recordGeneralMeetingApproval(selected.loan_application_id, {
        related_party_type: meetingType, related_party_user_id: null,
        relationship_description: meetingDescription.trim(), meeting_date: meetingDate,
        notice_document_id: notice, minutes_document_id: minutes, resolution_document_id: resolution,
        approval_status: meetingStatus,
      });
      await loadDetail(selected.approval_case_id);
      setShowMeetingForm(false); setSuccessMessage(uploadedNewFiles ? 'General meeting evidence recorded from three application-scoped legal uploads.' : 'General meeting evidence updated using the case’s existing referenceable legal documents.');
      setMeetingFiles({ notice: null, minutes: null, resolution: null });
    } catch (error) {
      const next = describeError(error); setStatus(next.status); setMessage(next.message);
    } finally { setBusy(false); }
  };

  const checklist = useMemo(() => selected ? [
    ['Eligibility verification', truth(selected.review_facts.eligibility.overall_result)],
    ['Loan amount assessment', `${money(selected.review_facts.loan_amounts.recommended_amount)} recommended / ${money(selected.review_facts.loan_amounts.eligible_amount)} eligible`],
    ['Purpose of loan', text(selected.review_facts.purpose.description || selected.review_facts.purpose.category)],
    ['Compliance checks', Object.values(selected.review_facts.compliance_checks).map(truth).join(', ')],
    ['Past borrowing history', text(selected.review_facts.borrowing_history)],
    ['Risk assessment', `${text(selected.review_facts.risk.overall_risk_rating)} — ${text(selected.review_facts.risk.risk_mitigation_notes)}`],
    ['Documentation completeness', `${truth(selected.review_facts.documentation_completeness.status)} / ${truth(selected.review_facts.documentation_completeness.document_check)}`],
    ['Approval authority', authoritySummary(selected)],
    ['Exception flag', selected.exception_condition_code ? `Flagged — ${text(selected.exception_reason)}` : 'No exception'],
    ['Conflict / related-party flag', selected.general_meeting_evidence_required || selected.excluded_approvers.length ? 'Flagged' : 'No conflict recorded'],
  ] : [], [selected]);

  const denied = status === 'unauthorized' || status === 'denied';

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div><h1 className="text-xl font-bold text-slate-900">Sanction Workbench</h1><p className="text-sm text-slate-500 mt-0.5">{cases.length} cases from the approval-case service</p></div>
        <select aria-label="Sanction case status" value={filter} onChange={event => setFilter(event.target.value)} className="field-input w-auto">
          <option value="pending">Pending my approval</option><option value="approved">Approved history</option><option value="rejected">Rejected history</option><option value="returned_for_clarification">Returned history</option><option value="blocked_by_conflict">Conflict-blocked history</option><option value="all">All readable cases</option>
        </select>
      </div>

      {status === 'loading' && <div className="card text-center py-16"><RefreshCw size={28} className="text-slate-400 mx-auto mb-3" /><p className="text-slate-600 font-semibold">Loading sanction workbench</p></div>}
      {status === 'empty' && <div className="card text-center py-16"><Check size={32} className="text-green-500 mx-auto mb-3" /><p className="text-slate-600 font-semibold">Sanction queue is clear</p><p className="text-sm text-slate-500 mt-1">No approval cases match this server filter.</p></div>}
      {successMessage && <AlertBanner type="success" title="Sanction record updated" message={successMessage} onDismiss={() => setSuccessMessage('')} />}
      {denied && <AlertBanner type="error" title={status === 'unauthorized' ? 'Sign-in required' : 'Sanction access denied'} message={message} />}
      {!denied && status !== 'loading' && status !== 'empty' && message && <AlertBanner type={status === 'validation' || status === 'stale' ? 'warning' : 'error'} title={status === 'stale' ? 'Case changed on the server' : 'Sanction action could not be completed'} message={message} />}

      {selected && status !== 'loading' && !denied && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="card p-0 overflow-hidden lg:col-span-1">
            <div className="p-4 bg-slate-50 border-b border-slate-200"><p className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Cases ({cases.length})</p></div>
            <div className="divide-y divide-slate-100">{cases.map(item => <button key={item.approval_case_id} onClick={() => void loadDetail(item.approval_case_id)} className={`w-full flex items-center gap-3 p-4 hover:bg-slate-50 text-left ${selectedId === item.approval_case_id ? 'bg-green-50 border-l-4 border-l-green-500' : ''}`}><div className="flex-1 min-w-0"><div className="flex items-center gap-2"><span className="font-semibold text-slate-900 num text-sm">{item.application_reference_number}</span>{item.exception_condition_code && <AlertOctagon size={12} className="text-violet-600" />}{item.general_meeting_evidence_required && <Shield size={12} className="text-amber-600" />}</div><div className="text-xs text-slate-400 num">Cycle {item.cycle_number} · {money(item.amount)}{item.approval_actions.length ? ` · ${item.approval_actions.length} decision(s) recorded` : ''}</div></div><StatusBadge label={item.current_status} size="sm" /></button>)}</div>
          </div>

          <div className="lg:col-span-2 space-y-4">
            <div className="card">
              <div className="flex items-start justify-between gap-3 mb-3"><div><div className="flex items-center gap-2 flex-wrap"><h2 className="text-lg font-bold text-slate-900 num">{selected.application_reference_number}</h2><StatusBadge label={selected.current_status} />{selected.exception_condition_code && <span className="text-xs bg-violet-100 text-violet-700 px-2 py-0.5 rounded font-semibold">Exception</span>}{selected.general_meeting_evidence_required && <span className="text-xs bg-amber-100 text-amber-700 px-2 py-0.5 rounded font-semibold">Special Case</span>}</div><p className="text-sm text-slate-500">Cycle {selected.cycle_number} · frozen policy {text(selected.loan_limit_provenance.policy_name)}</p></div><button onClick={() => onOpenApplication(selected.loan_application_id)} className="btn-secondary flex items-center gap-2"><FileText size={14} /> Full Application</button></div>
              <div className="grid grid-cols-3 gap-3"><div className="bg-slate-50 rounded-lg p-3"><p className="text-xs text-slate-500">Requested</p><p className="text-base font-bold num text-slate-900">{money(selected.review_facts.loan_amounts.requested_amount)}</p></div><div className="bg-slate-50 rounded-lg p-3"><p className="text-xs text-slate-500">Recommended</p><p className="text-base font-bold num text-slate-900">{money(selected.review_facts.loan_amounts.recommended_amount)}</p></div><div className="bg-slate-50 rounded-lg p-3"><p className="text-xs text-slate-500">Eligible</p><p className="text-base font-bold num text-slate-900">{money(selected.review_facts.loan_amounts.eligible_amount)}</p></div></div>
            </div>

            {selected.exception_condition_code && <AlertBanner type="exception" title="Exception case" message={selected.exception_reason || selected.reason_for_approval} />}
            {selected.general_meeting_evidence_required && <div className="card border-2 border-amber-300 bg-amber-50"><div className="flex items-start gap-3"><Shield size={20} className="text-amber-600 flex-shrink-0" /><div className="flex-1"><h3 className="font-semibold text-amber-900">Special Case Approval</h3><p className="text-sm text-amber-800 mt-1">Conflicted approvers are excluded. General meeting evidence is required before final sanction.</p>{selected.general_meeting_approval ? <div className="mt-3 text-sm text-amber-900"><p><strong>Status:</strong> {text(selected.general_meeting_approval.approval_status)}</p><p><strong>Meeting date:</strong> {selected.general_meeting_approval.meeting_date}</p><p><strong>Evidence scope:</strong> {text(selected.general_meeting_approval.evidence_scope)}</p><p><strong>Resolution:</strong> {selected.general_meeting_approval.resolution_document_id}</p></div> : <p className="text-sm text-amber-900 font-semibold mt-3">No general meeting evidence is recorded for this cycle.</p>}{canRecordMeeting && <button onClick={() => setShowMeetingForm(true)} className="btn-secondary mt-3">Record general meeting evidence</button>}</div></div></div>}

            <div className="card"><h3 className="text-sm font-semibold text-slate-700 mb-3 flex items-center gap-2"><CheckCircle2 size={14} /> Sanction Committee Checklist</h3><div className="border-t border-slate-100 pt-4"><div className="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-2">{checklist.map(([label, value]) => <div key={label} className="flex items-start gap-2 text-sm text-slate-700"><CheckCircle2 size={14} className="text-green-500 flex-shrink-0 mt-0.5" /><span><strong>{label}:</strong> {value}</span></div>)}</div></div></div>

            <div className="card"><h3 className="text-sm font-semibold text-slate-700 mb-3 flex items-center gap-2"><Gavel size={14} /> Sanction Committee Decision</h3><ApprovalPanel applicationNumber={selected.application_reference_number} amount={selected.amount} authoritySummary={authoritySummary(selected)} approvers={selected.required_approvers} excludedApprovers={selected.excluded_approvers} actions={selected.available_actions} permissions={currentUser.permissions} busy={busy} fieldError={decisionFieldError} onDecision={act} /></div>

            {decision && <div className="card border border-green-200"><h3 className="text-sm font-semibold text-green-800">Sanction decision</h3><p className="text-sm text-slate-700 mt-2">{decision.decision_reason}</p><p className="text-sm font-semibold text-slate-900 mt-1">{money(decision.sanctioned_amount)}</p></div>}
            {selected.conflict_block_reason && <div className="bg-amber-50 border border-amber-200 text-amber-800 text-sm px-4 py-3 rounded-lg flex gap-2"><AlertCircle size={16} />{selected.conflict_block_reason}</div>}
          </div>
        </div>
      )}

      <Modal isOpen={showMeetingForm} onClose={() => setShowMeetingForm(false)} title="Record General Meeting Approval" subtitle={selected?.application_reference_number} footer={<><button onClick={() => setShowMeetingForm(false)} className="btn-secondary">Cancel</button><button onClick={() => void recordMeeting()} disabled={busy || !meetingDescription.trim() || !meetingDate || (!selected?.general_meeting_approval && Object.values(meetingFiles).some(file => !file))} className="btn-primary">Record Evidence</button></>}>
        <div className="space-y-4">
          <div><label htmlFor="meeting-type" className="field-label">Special case type</label><select id="meeting-type" value={meetingType} onChange={event => setMeetingType(event.target.value as typeof meetingType)} className="field-input"><option value="director">Director</option><option value="director_relative">Director relative</option><option value="committee_member">Committee member</option></select></div>
          <div><label htmlFor="meeting-description" className="field-label">Relationship description <span className="text-red-500">*</span></label><textarea id="meeting-description" value={meetingDescription} onChange={event => setMeetingDescription(event.target.value)} className="field-input resize-none" rows={3} /></div>
          <div className="grid grid-cols-2 gap-3"><div><label htmlFor="meeting-date" className="field-label">General meeting date <span className="text-red-500">*</span></label><input id="meeting-date" type="date" value={meetingDate} onChange={event => setMeetingDate(event.target.value)} className="field-input" /></div><div><label htmlFor="meeting-status" className="field-label">Approval status</label><select id="meeting-status" value={meetingStatus} onChange={event => setMeetingStatus(event.target.value as typeof meetingStatus)} className="field-input"><option value="pending">Pending</option><option value="approved">Approved</option><option value="rejected">Rejected</option></select></div></div>
          {canUploadMeetingFiles ? (['notice', 'minutes', 'resolution'] as const).map(field => <div key={field}><label htmlFor={`meeting-${field}`} className="field-label">{field[0].toUpperCase() + field.slice(1)} document <span className="text-red-500">*</span></label><input id={`meeting-${field}`} type="file" accept="application/pdf" onChange={event => setMeetingFiles(previous => ({ ...previous, [field]: event.target.files?.[0] ?? null }))} className="field-input" /></div>) : <p className="text-sm text-slate-600">Existing referenceable evidence will be reused; you do not have document upload permission.</p>}
          <p className="text-xs text-slate-500">Each file is uploaded as restricted legal evidence for this exact application before its returned document id is referenced.</p>
        </div>
      </Modal>
    </div>
  );
};

export default SanctionWorkbench;
