import { useEffect, useState } from 'react';
import { Check, FileText, RotateCcw, Save, Send, XCircle } from 'lucide-react';
import AlertBanner from '../../components/ui/AlertBanner';
import StageStepper from '../../components/ui/StageStepper';
import StatusBadge from '../../components/ui/StatusBadge';
import EligibilityChecklist from '../../components/loan/EligibilityChecklist';
import LoanLimitCalculator from '../../components/loan/LoanLimitCalculator';
import { useRole } from '../../contexts/RoleContext';
import { fetchStaffApplications, type StaffApplication } from '../../services/applicationIntakeApi';
import { AuthSessionError } from '../../services/authSession';
import {
  calculateLoanLimit, createAppraisal, fetchAppraisal, fetchEligibilityAssessment,
  fetchLoanLimitAssessment, fetchSanctionCase, projectAppraisalDraft, revalidateAppraisalPrerequisites, reviewAppraisal,
  runEligibilityAssessment, submitAppraisalForReview, submitAppraisalToSanction, updateAppraisal,
  type AppraisalDraft, type AppraisalNote, type AvailableAction, type EligibilityAssessment,
  type LoanLimitAssessment, type ReviewRequest, type SanctionSubmission,
} from '../../services/creditAssessmentApi';

type ViewStatus = 'loading' | 'success' | 'error' | 'denied';
type LimitForm = { shareholding_id: string; land_holding_ids: string; crop_plan_id: string; requested_amount: string; calculation_date: string };
type Action = 'eligibility' | 'limit' | 'save' | 'revalidate' | 'submit-review' | 'review' | 'sanction';
const actionCodes: Record<Exclude<Action, 'save'>, string> = { eligibility: 'credit.eligibility.run', limit: 'credit.loan_limit.calculate', revalidate: 'revalidate_appraisal_prerequisites', 'submit-review': 'credit.appraisal.submit_review', review: 'credit.appraisal.review', sanction: 'credit.appraisal.submit_sanction' };
const money = (value: string | null) => value == null ? '—' : `₹${Number(value).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
const label = (value: string) => value.replace(/_/g, ' ');
const has = (permissions: string[], permission: string) => permissions.includes(permission);

interface ViewProps {
  status: ViewStatus; message: string; messageType?: 'success' | 'error'; applications: StaffApplication[];
  selectedApplication: StaffApplication | null; eligibility: EligibilityAssessment | null;
  loanLimit: LoanLimitAssessment | null; appraisal: AppraisalNote | null;
  sanctionSubmission: SanctionSubmission | null; permissions: string[]; roleCodes: string[]; availableActions?: AvailableAction[];
  form: AppraisalDraft; limitForm?: LimitForm; remarks?: string; reviewDecision?: ReviewRequest['decision'];
  rejectionCategory?: string; rejectionMode?: string; detailedReason?: string; reapplyAllowed?: boolean;
  onSelect: (id: string) => void; onField: (field: string, value: unknown) => void;
  onAction: (action: Action) => void; onOpenApplication?: (id: string) => void;
}

export const AppraisalWorkbenchView: React.FC<ViewProps> = props => {
  const serverProjectsReview = (props.availableActions ?? []).some(action => action.enabled && (action.action_code === 'credit.appraisal.review' || action.action_code === 'credit.appraisal.submit_sanction'));
  const serverStage = serverProjectsReview || props.appraisal?.appraisal_status === 'review_pending' || props.appraisal?.appraisal_status === 'reviewed' || props.appraisal?.appraisal_status === 'rejected' || props.appraisal?.appraisal_status === 'submitted_to_sanction_committee' || props.sanctionSubmission
    ? 'review'
    : props.loanLimit || props.appraisal ? 'appraisal' : 'eligibility';
  const [visibleStage, setVisibleStage] = useState(serverStage);
  useEffect(() => setVisibleStage(serverStage), [props.selectedApplication?.loan_application_id, serverStage]);
  if (props.status === 'loading') return <div className="p-6"><AlertBanner type="info" title="Loading appraisal workbench" message="Loading stored credit-assessment facts from the staff API." /></div>;
  if (props.status === 'denied') return <div className="p-6"><AlertBanner type="warning" title="Appraisal access denied" message={props.message} /></div>;
  if (props.status === 'error') return <div className="p-6"><AlertBanner type="error" title="Appraisal unavailable" message={props.message} /></div>;
  if (!props.selectedApplication || props.applications.length === 0) return <div className="p-6"><div className="card text-center py-16"><Check size={32} className="text-green-500 mx-auto mb-3" /><p className="text-slate-600 font-semibold">Appraisal queue is clear</p><p className="text-slate-400 text-sm mt-1">No API-backed applications are available.</p></div></div>;

  const app = props.selectedApplication; const note = props.appraisal;
  const permissions = props.permissions;
  const serverAction = (action: Action) => (props.availableActions ?? []).find(item => action === 'save'
    ? item.action_code === (note ? 'credit.appraisal.update' : 'credit.appraisal.create')
    : item.action_code === actionCodes[action]);
  const serverAllows = (action: Action) => {
    const projected = serverAction(action);
    if (!projected?.enabled) return false;
    if (projected.required_permission && !has(permissions, projected.required_permission)) return false;
    return !projected.required_role || props.roleCodes.includes(projected.required_role);
  };
  const disabledReasons = (props.availableActions ?? []).filter(item => !item.enabled && item.disabled_reason);
  const canCreate = !note && serverAllows('save');
  const canEdit = Boolean(note) && serverAllows('save');
  const canSubmit = Boolean(note) && serverAllows('submit-review');
  const canRevalidate = Boolean(note) && serverAllows('revalidate');
  const canReview = Boolean(note) && serverAllows('review');
  const canSanction = Boolean(note) && serverAllows('sanction');
  const submitted = note?.appraisal_status === 'submitted_to_sanction_committee' || Boolean(props.sanctionSubmission);
  const steps = [
    { id: 'eligibility', label: 'Step 1', sublabel: 'Verify', state: props.eligibility ? 'completed' as const : 'in_progress' as const },
    { id: 'appraisal', label: 'Step 2', sublabel: 'Appraise', state: note?.appraisal_status === 'review_pending' || note?.appraisal_status === 'reviewed' || submitted ? 'completed' as const : visibleStage === 'appraisal' ? 'in_progress' as const : 'not_started' as const },
    { id: 'review', label: 'Step 3', sublabel: submitted ? 'Submitted' : 'Review', state: submitted ? 'completed' as const : visibleStage === 'review' ? 'in_progress' as const : 'not_started' as const },
  ];
  const limit = props.limitForm ?? { shareholding_id: '', land_holding_ids: '', crop_plan_id: '', requested_amount: app.required_loan_amount ?? '', calculation_date: '' };

  return (
    <div className="p-6 space-y-4">
      <div><h1 className="text-xl font-bold text-slate-900">Appraisal Workbench</h1><p className="text-sm text-slate-500 mt-0.5">{props.applications.length} API-backed application{props.applications.length === 1 ? '' : 's'} in the workbench</p></div>
      {props.message && <AlertBanner type={props.sanctionSubmission || props.messageType === 'success' ? 'success' : 'error'} title={props.sanctionSubmission ? 'Submitted to Sanction Committee' : props.messageType === 'success' ? 'Action updated' : 'Action failed'} message={props.message} />}
      {disabledReasons.length > 0 && <AlertBanner type="info" title="Unavailable actions" message={disabledReasons.map(item => `${item.label ?? item.action_code}: ${item.disabled_reason}`).join(' · ')} />}
      {props.sanctionSubmission && <AlertBanner type="success" title="Pending sanction case created" message={`Case ${props.sanctionSubmission.approval_case_id} · ${props.sanctionSubmission.submission_status}.`} />}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="card p-0 overflow-hidden lg:col-span-1">
          <div className="p-4 bg-slate-50 border-b border-slate-200"><p className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Queue ({props.applications.length})</p></div>
          <div className="divide-y divide-slate-100">{props.applications.map(item => (
            <button key={item.loan_application_id} onClick={() => props.onSelect(item.loan_application_id)} className={`w-full p-4 text-left hover:bg-slate-50 ${item.loan_application_id === app.loan_application_id ? 'bg-green-50 border-l-4 border-l-green-500' : ''}`}>
              <p className="font-semibold text-slate-900 num text-sm">{item.application_reference_number ?? item.loan_application_id.slice(0, 8)}</p>
              <p className="text-xs text-slate-500 truncate">{item.member.display_name}</p><p className="text-xs text-slate-400 num">{money(item.required_loan_amount)}</p>
            </button>
          ))}</div>
        </div>
        <div className="lg:col-span-2 space-y-4">
          <div className="card">
            <div className="flex items-start justify-between gap-3 mb-4">
              <div><div className="flex items-center gap-2"><h2 className="text-lg font-bold text-slate-900 num">{app.application_reference_number ?? app.loan_application_id.slice(0, 8)}</h2><StatusBadge label={note?.appraisal_status ?? app.application_status} size="sm" /></div><p className="text-sm text-slate-500">{app.member.display_name} · {money(app.required_loan_amount)}</p></div>
              {props.onOpenApplication && <button onClick={() => props.onOpenApplication?.(app.loan_application_id)} className="btn-secondary text-sm flex items-center gap-2"><FileText size={14} /> Full Application</button>}
            </div>
            <StageStepper steps={steps} onStepClick={id => setVisibleStage(id as typeof visibleStage)} />
          </div>

          {(visibleStage === 'eligibility' || visibleStage === 'appraisal') && <div className="space-y-4">
          <AlertBanner type="info" title={visibleStage === 'eligibility' ? 'Step 1: Verify stored eligibility' : 'Step 2: Prepare appraisal note'} message={visibleStage === 'eligibility' ? 'Review the server assessment and complete any available eligibility action.' : 'Review eligibility, calculate the stored limit, and prepare the appraisal recommendation.'} />
          <div className="card space-y-4">
            <div className="flex items-center justify-between"><h3 className="font-bold text-slate-900">Eligibility Assessment</h3>{props.eligibility && <StatusBadge label={props.eligibility.overall_result} size="sm" />}</div>
            {props.eligibility ? <EligibilityChecklist assessment={props.eligibility} /> : <p className="text-sm text-slate-500">No stored eligibility assessment is available.</p>}
            {serverAllows('eligibility') && has(permissions, 'credit.eligibility.run') && <button onClick={() => props.onAction('eligibility')} className="btn-secondary text-sm">Run Eligibility Assessment</button>}
          </div>

          {visibleStage === 'appraisal' && <><div className="card space-y-4">
            <div className="flex items-center justify-between"><h3 className="font-bold text-slate-900">Loan Limit Calculator</h3>{props.loanLimit && <StatusBadge label={props.loanLimit.exception_required_flag ? 'exception_required' : 'within_limit'} size="sm" />}</div>
            {props.loanLimit ? <LoanLimitCalculator assessment={props.loanLimit} /> : <p className="text-sm text-slate-500">No stored loan-limit assessment is available.</p>}
            {serverAllows('limit') && has(permissions, 'credit.loan_limit.calculate') && <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {textField('Shareholding ID', 'limit.shareholding_id', limit.shareholding_id, props.onField)}
              {textField('Land holding IDs (comma separated)', 'limit.land_holding_ids', limit.land_holding_ids, props.onField)}
              {textField('Crop plan ID', 'limit.crop_plan_id', limit.crop_plan_id, props.onField)}
              {textField('Requested amount', 'limit.requested_amount', limit.requested_amount, props.onField)}
              {textField('Calculation date', 'limit.calculation_date', limit.calculation_date, props.onField, 'date')}
              <div className="flex items-end"><button onClick={() => props.onAction('limit')} className="btn-secondary text-sm">Calculate Stored Loan Limit</button></div>
            </div>}
          </div>

          <div className="card space-y-4">
            <div className="flex items-center justify-between"><h3 className="font-bold text-slate-900">Appraisal Note</h3>{note && <StatusBadge label={note.appraisal_status} size="sm" />}</div>
            {!note && !canCreate && <p className="text-sm text-slate-500">No stored appraisal note is available, and your current permissions do not allow creation.</p>}
            {(note || canCreate) && <>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {areaField('Borrower summary', 'borrower_summary', props.form.borrower_summary, props.onField)}
                {areaField('Eligibility summary', 'eligibility_summary', props.form.eligibility_summary, props.onField)}
                {areaField('Loan-limit summary', 'loan_limit_summary', props.form.loan_limit_summary, props.onField)}
                {areaField('Repayment capacity notes', 'repayment_capacity_notes', props.form.repayment_capacity_notes, props.onField)}
                {textField('Recommended amount', 'recommended_amount', props.form.recommended_amount, props.onField)}
                {textField('Recommended tenure (months)', 'recommended_tenure_months', String(props.form.recommended_tenure_months ?? ''), props.onField, 'number')}
                {textField('Interest type', 'recommended_interest_type', props.form.recommended_interest_type, props.onField)}
                {areaField('Recommended security', 'recommended_security_summary', props.form.recommended_security_summary, props.onField)}
                {selectField('Recommendation', 'recommendation', props.form.recommendation, ['', 'approve', 'conditions', 'reject'], props.onField)}
                {selectField('Market risk', 'risk.market_risk_rating', props.form.risk_assessment.market_risk_rating, ['', 'low', 'medium', 'high'], props.onField)}
                {selectField('Operational risk', 'risk.operational_risk_rating', props.form.risk_assessment.operational_risk_rating, ['', 'low', 'medium', 'high'], props.onField)}
                {selectField('Borrower risk', 'risk.borrower_risk_rating', props.form.risk_assessment.borrower_risk_rating, ['', 'low', 'medium', 'high'], props.onField)}
                {selectField('Overall risk', 'risk.overall_risk_rating', props.form.risk_assessment.overall_risk_rating, ['', 'low', 'medium', 'high'], props.onField)}
                {areaField('Risk mitigation notes', 'risk.risk_mitigation_notes', props.form.risk_assessment.risk_mitigation_notes, props.onField)}
              </div>
              <div className="flex flex-wrap gap-2">
                {(canCreate || canEdit) && <button onClick={() => props.onAction('save')} className="btn-secondary text-sm flex items-center gap-2"><Save size={14} /> {note ? 'Save Appraisal Draft' : 'Create Appraisal Draft'}</button>}
                {canRevalidate && <button onClick={() => props.onAction('revalidate')} className="btn-secondary text-sm"><RotateCcw size={14} className="inline mr-2" />Revalidate Prerequisites</button>}
                {canSubmit && <button onClick={() => props.onAction('submit-review')} className="btn-primary text-sm"><Send size={14} className="inline mr-2" />Submit for Credit Review</button>}
              </div>
              {canSubmit && areaField('Submission remarks', 'remarks', props.remarks ?? '', props.onField)}
            </>}
            {note?.prerequisite_provenance && <p className="text-xs text-slate-500">Prerequisite provenance: <strong>{label(note.prerequisite_provenance)}</strong> · TAT: <strong>{label(note.tat_status)}</strong></p>}
            {note?.appraisal_status === 'rejected' && <AlertBanner type="error" title="Appraisal rejected" message={note.rejection_note ? `Rejection note ${label(note.rejection_note.note_status)} · ${label(note.rejection_note.rejection_reason_category)} · reapply ${note.rejection_note.reapply_allowed_flag ? 'allowed' : 'not allowed'}. Sanction submission is unavailable.` : 'No rejection-note summary is available. Sanction submission is unavailable.'} />}
          </div></>}
          </div>}

          {visibleStage === 'review' && <div className="space-y-4">
          <AlertBanner type="info" title="Step 3: Credit Manager review" message="Review the stored appraisal package and use only the actions enabled by the server." />
          {note?.appraisal_status === 'rejected' && <AlertBanner type="error" title="Appraisal rejected" message={note.rejection_note ? `Rejection note ${label(note.rejection_note.note_status)} · ${label(note.rejection_note.rejection_reason_category)} · reapply ${note.rejection_note.reapply_allowed_flag ? 'allowed' : 'not allowed'}. Sanction submission is unavailable.` : 'No rejection-note summary is available. Sanction submission is unavailable.'} />}
          {note && <div className="card space-y-4"><div className="flex items-center justify-between"><h3 className="font-bold text-slate-900">Credit Manager Review Package</h3><StatusBadge label={note.appraisal_status} size="sm" /></div><div className="grid grid-cols-2 sm:grid-cols-3 gap-3">{[['Recommended amount', money(note.recommended_amount)], ['Tenure', note.recommended_tenure_months ? `${note.recommended_tenure_months} months` : '—'], ['Overall risk', label(note.risk_assessment.overall_risk_rating)], ['Recommendation', label(note.recommendation)], ['Prepared by', note.prepared_by.full_name], ['TAT', label(note.tat_status)]].map(([caption, value]) => <div key={caption} className="bg-slate-50 rounded-lg p-3"><p className="text-xs text-slate-500">{caption}</p><p className="text-sm font-semibold text-slate-900 capitalize mt-0.5">{value}</p></div>)}</div><p className="text-sm text-slate-600">{note.borrower_summary}</p></div>}

          {note && <div className="card space-y-3"><h3 className="font-bold text-slate-900">Immutable Review History</h3>{note.review_history.length === 0 ? <p className="text-sm text-slate-500">No review decisions recorded.</p> : note.review_history.map(item => <div key={item.appraisal_review_decision_id} className="bg-slate-50 rounded-lg p-3"><div className="flex justify-between gap-2"><span className="text-sm font-semibold capitalize">{label(item.decision)}</span><span className="text-xs text-slate-500">{new Date(item.decided_at).toLocaleString('en-IN')}</span></div><p className="text-sm text-slate-600 mt-1">{item.review_comments}</p><p className="text-xs text-slate-400 mt-1">{item.reviewer.full_name} · {label(item.from_state)} → {label(item.to_state)}</p></div>)}</div>}

          {(canReview || canSanction) && <div className="card space-y-4">
            <h3 className="font-bold text-slate-900">Credit Manager Decision</h3>
            {canReview && selectField('Decision', 'reviewDecision', props.reviewDecision ?? 'reviewed', ['reviewed', 'returned', 'rejected'], props.onField)}
            {areaField(canSanction ? 'Sanction submission remarks' : 'Review comments', 'remarks', props.remarks ?? '', props.onField)}
            {canReview && props.reviewDecision === 'rejected' && <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {selectField('Rejection category', 'rejectionCategory', props.rejectionCategory ?? 'eligibility', ['missing_document', 'eligibility', 'default', 'purpose_mismatch', 'limit_issue', 'committee_rejection', 'other'], props.onField)}
              {selectField('Communication mode', 'rejectionMode', props.rejectionMode ?? 'email', ['email', 'courier', 'hard_copy', 'sms_summary'], props.onField)}
              {areaField('Detailed rejection reason', 'detailedReason', props.detailedReason ?? '', props.onField)}
              <label className="flex items-center gap-2 text-sm text-slate-700"><input type="checkbox" checked={props.reapplyAllowed ?? true} onChange={event => props.onField('reapplyAllowed', event.target.checked)} /> Reapplication allowed</label>
            </div>}
            {canReview && <button onClick={() => props.onAction('review')} className="btn-primary text-sm flex items-center gap-2">{props.reviewDecision === 'returned' ? <RotateCcw size={14} /> : props.reviewDecision === 'rejected' ? <XCircle size={14} /> : <Check size={14} />} Record Credit Review</button>}
            {canSanction && <button onClick={() => props.onAction('sanction')} className="btn-primary text-sm flex items-center gap-2"><Send size={14} /> Submit to Sanction Committee</button>}
          </div>}
          {submitted && <AlertBanner type="success" title="Submitted to Sanction Committee" message={props.sanctionSubmission ? `Pending case ${props.sanctionSubmission.approval_case_id} retained for Epic 007 navigation.` : 'The server reports this appraisal as submitted.'} />}
          </div>}
        </div>
      </div>
    </div>
  );
};

const emptyDraft = (amount = ''): AppraisalDraft => ({ borrower_summary: '', eligibility_summary: '', loan_limit_summary: '', recommended_amount: amount, recommended_tenure_months: null, recommended_interest_type: 'floating', recommended_security_summary: '', repayment_capacity_notes: '', risk_assessment: { market_risk_rating: '' as never, operational_risk_rating: '' as never, borrower_risk_rating: '' as never, overall_risk_rating: '' as never, risk_mitigation_notes: '' }, recommendation: '' });
const emptyLimit = (amount = ''): LimitForm => ({ shareholding_id: '', land_holding_ids: '', crop_plan_id: '', requested_amount: amount, calculation_date: new Date().toISOString().slice(0, 10) });
const missing = (error: unknown) => error instanceof AuthSessionError && error.status === 404;
const denied = (error: unknown) => error instanceof AuthSessionError && (error.status === 401 || error.status === 403);
const errorText = (error: unknown) => error instanceof AuthSessionError ? `${error.code}: ${error.message}${Object.entries(error.fieldErrors ?? {}).map(([field, value]) => ` ${field}: ${value}`).join('')}` : error instanceof Error ? error.message : 'Unable to complete the appraisal action.';

const AppraisalWorkbench: React.FC<{ onOpenApplication: (id: string) => void; initialSelectedId?: string }> = ({ onOpenApplication, initialSelectedId }) => {
  const { currentUser } = useRole();
  const [status, setStatus] = useState<ViewStatus>('loading'); const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState<'success' | 'error'>('error');
  const [applications, setApplications] = useState<StaffApplication[]>([]); const [selectedId, setSelectedId] = useState(initialSelectedId ?? '');
  const [eligibility, setEligibility] = useState<EligibilityAssessment | null>(null); const [loanLimit, setLoanLimit] = useState<LoanLimitAssessment | null>(null);
  const [appraisal, setAppraisal] = useState<AppraisalNote | null>(null); const [sanction, setSanction] = useState<SanctionSubmission | null>(null);
  const [form, setForm] = useState<AppraisalDraft>(emptyDraft()); const [limitForm, setLimitForm] = useState<LimitForm>(emptyLimit());
  const [remarks, setRemarks] = useState(''); const [reviewDecision, setReviewDecision] = useState<ReviewRequest['decision']>('reviewed');
  const [rejectionCategory, setRejectionCategory] = useState('eligibility'); const [rejectionMode, setRejectionMode] = useState('email');
  const [detailedReason, setDetailedReason] = useState(''); const [reapplyAllowed, setReapplyAllowed] = useState(true);

  const loadAssessments = async (id: string, applicationPool = applications) => {
    const values = await Promise.allSettled([fetchEligibilityAssessment(id), fetchLoanLimitAssessment(id), fetchAppraisal(id), fetchSanctionCase(id)]);
    const failure = values.find(result => result.status === 'rejected' && !missing(result.reason));
    if (failure?.status === 'rejected') throw failure.reason;
    const nextEligibility = values[0].status === 'fulfilled' ? values[0].value : null;
    const nextLimit = values[1].status === 'fulfilled' ? values[1].value : null;
    const nextAppraisal = values[2].status === 'fulfilled' ? values[2].value : null;
    const nextSanction = values[3].status === 'fulfilled' ? values[3].value : null;
    setEligibility(nextEligibility); setLoanLimit(nextLimit); setAppraisal(nextAppraisal); setSanction(nextSanction);
    if (nextSanction) setApplications(current => current.map(item => item.loan_application_id === id && nextSanction.application_status ? { ...item, application_status: nextSanction.application_status } : item));
    const selected = applicationPool.find(item => item.loan_application_id === id);
    setForm(nextAppraisal ? projectAppraisalDraft(nextAppraisal) : emptyDraft(selected?.required_loan_amount ?? ''));
    setLimitForm(emptyLimit(selected?.required_loan_amount ?? '')); setStatus('success');
  };

  useEffect(() => {
    let cancelled = false;
    fetchStaffApplications({ ordering: 'application_date', pageSize: 100 }).then(result => {
      if (cancelled) return;
      const queue = result.items.filter(item => ['reference_generated', 'submitted_to_sanction_committee'].includes(item.application_status));
      setApplications(queue); const id = queue.some(item => item.loan_application_id === initialSelectedId) ? initialSelectedId! : queue[0]?.loan_application_id ?? '';
      setSelectedId(id); if (!id) setStatus('success'); else loadAssessments(id, queue).catch(error => { setStatus(denied(error) ? 'denied' : 'error'); setMessage(errorText(error)); });
    }).catch(error => { if (!cancelled) { setStatus(denied(error) ? 'denied' : 'error'); setMessage(errorText(error)); } });
    return () => { cancelled = true; };
  // Initial route selection owns this load; later selection uses the explicit handler.
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialSelectedId]);

  const select = (id: string) => { setSelectedId(id); setStatus('loading'); setMessage(''); loadAssessments(id).catch(error => { setStatus(denied(error) ? 'denied' : 'error'); setMessage(errorText(error)); }); };
  const field = (name: string, value: unknown) => {
    if (name.startsWith('limit.')) return setLimitForm(current => ({ ...current, [name.slice(6)]: String(value) }));
    if (name.startsWith('risk.')) return setForm(current => ({ ...current, risk_assessment: { ...current.risk_assessment, [name.slice(5)]: value } }));
    if (name === 'remarks') return setRemarks(String(value)); if (name === 'reviewDecision') return setReviewDecision(value as ReviewRequest['decision']);
    if (name === 'rejectionCategory') return setRejectionCategory(String(value)); if (name === 'rejectionMode') return setRejectionMode(String(value));
    if (name === 'detailedReason') return setDetailedReason(String(value)); if (name === 'reapplyAllowed') return setReapplyAllowed(Boolean(value));
    setForm(current => ({ ...current, [name]: name === 'recommended_tenure_months' ? (value ? Number(value) : null) : value }));
  };
  const action = async (name: Action) => {
    if (!selectedId) return; setMessage(''); setMessageType('error');
    try {
      if (name === 'eligibility') await runEligibilityAssessment(selectedId);
      if (name === 'limit') await calculateLoanLimit(selectedId, { ...limitForm, land_holding_ids: limitForm.land_holding_ids.split(',').map(id => id.trim()).filter(Boolean) });
      if (name === 'save') await (appraisal ? updateAppraisal(selectedId, projectAppraisalDraft(form)) : createAppraisal(selectedId, projectAppraisalDraft(form)));
      if (name === 'revalidate' && appraisal) await revalidateAppraisalPrerequisites(appraisal.loan_appraisal_note_id);
      if (name === 'submit-review' && appraisal) await submitAppraisalForReview(appraisal.loan_appraisal_note_id, { remarks });
      if (name === 'review' && appraisal) await reviewAppraisal(appraisal.loan_appraisal_note_id, { decision: reviewDecision, review_comments: remarks, ...(reviewDecision === 'rejected' ? { rejection_reason_category: rejectionCategory, detailed_reason: detailedReason, reapply_allowed_flag: reapplyAllowed, communication_mode: rejectionMode } : {}) });
      if (name === 'sanction') await submitAppraisalToSanction(selectedId, { remarks });
      await loadAssessments(selectedId);
      setMessageType('success'); setMessage(name === 'sanction' ? 'The server created a pending sanction case.' : 'Stored server state updated.');
    } catch (error) { setMessageType('error'); setMessage(errorText(error)); }
  };

  const availableActions = [
    ...(eligibility?.available_actions ?? []),
    ...(loanLimit?.available_actions ?? []),
    ...(appraisal?.available_actions ?? []),
    ...(sanction?.available_actions ?? []),
  ];
  return <AppraisalWorkbenchView status={status} message={message} messageType={messageType} applications={applications} selectedApplication={applications.find(item => item.loan_application_id === selectedId) ?? null} eligibility={eligibility} loanLimit={loanLimit} appraisal={appraisal} sanctionSubmission={sanction} permissions={currentUser.permissions} roleCodes={currentUser.roleCodes} availableActions={availableActions} form={form} limitForm={limitForm} remarks={remarks} reviewDecision={reviewDecision} rejectionCategory={rejectionCategory} rejectionMode={rejectionMode} detailedReason={detailedReason} reapplyAllowed={reapplyAllowed} onSelect={select} onField={field} onAction={action} onOpenApplication={onOpenApplication} />;
};

const textField = (caption: string, name: string, value: string, onField: ViewProps['onField'], type = 'text') => <label><span className="field-label">{caption}</span><input className="field-input" type={type} value={value} onChange={event => onField(name, event.target.value)} /></label>;
const areaField = (caption: string, name: string, value: string, onField: ViewProps['onField']) => <label><span className="field-label">{caption}</span><textarea className="field-input resize-none" rows={3} value={value} onChange={event => onField(name, event.target.value)} /></label>;
const selectField = (caption: string, name: string, value: string, options: string[], onField: ViewProps['onField']) => <label><span className="field-label">{caption}</span><select className="field-input" value={value} onChange={event => onField(name, event.target.value)}>{options.map(option => <option key={option || 'blank'} value={option}>{option ? label(option) : 'Select'}</option>)}</select></label>;

export default AppraisalWorkbench;
