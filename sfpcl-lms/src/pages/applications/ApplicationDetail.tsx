import React, { useEffect, useState } from 'react';
import {
  ChevronLeft, ExternalLink, AlertOctagon, Clock, Eye, EyeOff,
  CheckCircle2, XCircle, AlertTriangle, User, Users, Shield,
  Lock, Download, MessageSquare, History,
  ArrowRight, ClipboardList, Info, Send
} from 'lucide-react';
import Tabs from '../../components/ui/Tabs';
import StageStepper from '../../components/ui/StageStepper';
import StatusBadge from '../../components/ui/StatusBadge';
import AlertBanner from '../../components/ui/AlertBanner';
import LoanLimitCalculator from '../../components/loan/LoanLimitCalculator';
import EligibilityChecklist from '../../components/loan/EligibilityChecklist';
import ApprovalPanel from '../../components/loan/ApprovalPanel';
import DocumentChecklist from '../../components/loan/DocumentChecklist';
import AuditTimeline from '../../components/loan/AuditTimeline';
import { useRole } from '../../contexts/RoleContext';
import { COMPLETENESS_CATEGORIES, COMPLETENESS_ITEMS } from './completenessChecklist';
import { getApplicationReference, getApplicationStatusLabel, hasFormalLoanReference } from '../../utils/applicationDisplay';
import {
  fetchApplicationDeficiencies,
  fetchApplicationDetail,
  fetchApplicationDocumentChecklist,
  type ApplicationDeficiency,
  type ApplicationDocumentChecklistItem,
  type ApplicationNomineeSummary,
  type StaffApplication,
  type StaffApplicationRejectionNote,
} from '../../services/applicationIntakeApi';
import type { AuditEvent, DocumentRecord, LoanApplication, Member, SecurityInstrument } from '../../types';

const fmt = (n: number) => '₹' + n.toLocaleString('en-IN');

const STAGE_MAP: Record<string, number> = {
  draft: 0, 
  submitted: 1, incomplete: 1, incomplete_returned: 1, deficiency_raised: 1,
  returned_for_rectification: 1, completeness_check: 1, rejected_completeness: 1,
  reference_generated: 2, appraisal_in_progress: 2, appraisal_pending: 2,
  pending_credit_manager_review: 2, credit_review: 2,
  pending_sanction_committee_approval: 3, pending_sanction: 3,
  under_sanction_review: 3, clarification_requested: 3,
  sanctioned: 4, rejected_by_credit_manager: 4, rejected_credit: 4,
  rejected_by_sanction_committee: 4, rejected_sanction: 4,
  documentation_in_progress: 4, documentation_deficiency_raised: 4,
  pending_final_checklist_approvals: 4,
  disbursement_ready: 5, sap_customer_code_pending: 5,
  sap_customer_code_confirmed: 5, payment_initiated: 6,
  payment_authorized: 6, transfer_executed: 6, disbursed: 6,
};

const emptyMember: Member = {
  id: '',
  memberType: 'individual',
  name: 'Loading member',
  folioNumber: '—',
  sharesHeld: 0,
  shareMode: 'physical',
  aadhaar: '••••-••••-••••',
  pan: '••••••••••',
  mobile: '—',
  email: '—',
  address: 'Member master address on file',
  activeStatus: 'active',
  kycStatus: 'verified',
  supplyYears: 0,
  defaultStatus: 'no_default',
  registeredOn: '',
  currentExposure: 0,
};

const emptyApplication: LoanApplication = {
  id: '',
  applicationNumber: 'Loading',
  intakeReference: 'Loading',
  officialReference: undefined,
  source: 'assisted_entry',
  applicationDate: new Date().toISOString().slice(0, 10),
  memberId: '',
  memberName: 'Loading member',
  memberType: 'individual',
  nomineeId: '',
  requestedAmount: 0,
  purpose: 'crop_production',
  loanType: 'short_term',
  tenure: 12,
  sharesHeld: 0,
  shareMode: 'physical',
  landAreaAcres: 0,
  status: 'draft',
  documentationStatus: 'not_started',
  disbursementStatus: 'pending_documentation',
  eligibleAmount: 0,
  shareholdingLimit: 0,
  landBasedLimit: 0,
  isException: false,
  currentOwner: '—',
  currentOwnerRole: 'deputy_manager_finance',
  submittedAt: '',
  tatDaysRemaining: undefined,
};

const toDisplayApplication = (application: StaffApplication): LoanApplication => ({
  ...emptyApplication,
  id: application.loan_application_id,
  applicationNumber: application.application_reference_number ?? application.loan_application_id.slice(0, 8),
  intakeReference: application.application_reference_number ? undefined : application.loan_application_id.slice(0, 8),
  officialReference: application.application_reference_number ?? undefined,
  applicationDate: application.application_date,
  memberId: application.member.member_id,
  memberName: application.member.display_name,
  memberType: application.member.member_type === 'fpc' ? 'fpc' : application.member.member_type === 'producer_institution' ? 'producer_institution' : 'individual',
  nomineeId: application.nominee?.nominee_id ?? '',
  requestedAmount: Number(application.required_loan_amount ?? 0),
  purpose: application.purpose_category === 'agriculture_activity' ? 'agriculture_activity' : 'crop_production',
  loanType: application.loan_type_requested === 'long_term' ? 'long_term' : 'short_term',
  tenure: application.requested_tenure_months ?? 12,
  status: application.application_status as LoanApplication['status'],
  currentOwner: application.assigned_owner?.full_name ?? '—',
  submittedAt: application.submitted_at ?? '',
});

const toDisplayMember = (application: StaffApplication): Member => ({
  ...emptyMember,
  id: application.member.member_id,
  memberType: application.member.member_type === 'fpc' ? 'fpc' : application.member.member_type === 'producer_institution' ? 'producer_institution' : 'individual',
  name: application.member.display_name,
  folioNumber: application.member.folio_number,
  activeStatus: application.member.membership_status === 'active' ? 'active' : 'under_review',
  kycStatus: application.member.kyc_status === 'verified' ? 'verified' : 'pending',
});

const toDisplayDocuments = (items: ApplicationDocumentChecklistItem[]): DocumentRecord[] =>
  items.map((item, index) => ({
    id: item.latest_application_document_id ?? `${item.document_type}-${index}`,
    applicationId: '',
    documentType: mapDocumentType(item.document_type),
    requiredFlag: item.required_flag === 'optional' ? 'optional' : 'mandatory',
    status: item.complete ? 'verified' : item.reason_code === 'missing_metadata' ? 'pending_upload' : 'under_review',
    version: 1,
  }));

const mapDocumentType = (documentType: string): DocumentRecord['documentType'] => {
  const map: Record<string, DocumentRecord['documentType']> = {
    borrower_pan: 'pan',
    borrower_aadhaar_ovd: 'aadhaar',
    nominee_pan: 'nominee_pan',
    nominee_aadhaar_ovd: 'nominee_aadhaar',
    share_certificate_copy: 'share_certificate',
    land_document_7_12: 'land_712',
    crop_plan: 'crop_plan',
    six_month_bank_statement: 'bank_statement',
  };
  return map[documentType] ?? 'loan_agreement';
};

interface ApplicationDetailProps {
  applicationId: string;
  onBack: () => void;
  onNavigateMember: (memberId: string) => void;
  initialActiveTab?: number;
  initialData?: {
    application: StaffApplication;
    checklistItems: ApplicationDocumentChecklistItem[];
    deficiencies: ApplicationDeficiency[];
  };
}

const ApplicationDetail: React.FC<ApplicationDetailProps> = ({
  applicationId, onBack, onNavigateMember, initialActiveTab = 0, initialData,
}) => {
  const { can, currentUser } = useRole();
  const [app, setApp] = useState<LoanApplication>(() => initialData ? toDisplayApplication(initialData.application) : emptyApplication);
  const [member, setMember] = useState<Member>(() => initialData ? toDisplayMember(initialData.application) : emptyMember);
  const [appDocs, setAppDocs] = useState<DocumentRecord[]>(() => initialData ? toDisplayDocuments(initialData.checklistItems) : []);
  const [appSecurities] = useState<SecurityInstrument[]>([]);
  const [auditEvents] = useState<AuditEvent[]>([]);
  const [apiDeficiencies, setApiDeficiencies] = useState<ApplicationDeficiency[]>(() => initialData?.deficiencies ?? []);
  const [rejectionNote, setRejectionNote] = useState<StaffApplicationRejectionNote | null>(() => initialData?.application.rejection_note ?? null);
  const [nominee, setNominee] = useState<ApplicationNomineeSummary | null>(() => initialData?.application.nominee ?? null);
  const [loadStatus, setLoadStatus] = useState<'loading' | 'success' | 'error'>(initialData ? 'success' : 'loading');
  const [loadMessage, setLoadMessage] = useState('');

  useEffect(() => {
    if (initialData) return;
    let cancelled = false;
    setLoadStatus('loading');
    Promise.all([
      fetchApplicationDetail(applicationId),
      fetchApplicationDocumentChecklist(applicationId),
      fetchApplicationDeficiencies(applicationId),
    ])
      .then(([application, checklist, deficiencies]) => {
        if (cancelled) return;
        setApp(toDisplayApplication(application));
        setMember(toDisplayMember(application));
        setAppDocs(toDisplayDocuments(checklist.items));
        setApiDeficiencies(deficiencies.items);
        setRejectionNote(application.rejection_note ?? null);
        setNominee(application.nominee ?? null);
        setLoadStatus('success');
        setLoadMessage('');
      })
      .catch(error => {
        if (cancelled) return;
        setLoadStatus('error');
        setLoadMessage(error instanceof Error ? error.message : 'Unable to load application.');
      });
    return () => {
      cancelled = true;
    };
  }, [applicationId, initialData]);

  const isDisbursed = ['completed', 'disbursed', 'transfer_executed'].includes(app.disbursementStatus) || ['disbursed', 'transfer_executed'].includes(app.status);

  const [activeTab, setActiveTab] = useState(initialActiveTab);
  const [panRevealed, setPanRevealed] = useState(false);
  const [aadhaarRevealed, setAadhaarRevealed] = useState(false);

  const stageIndex = STAGE_MAP[app.status] ?? 0;
  const isCompletenessReadOnly = stageIndex > 1;

  const pendingDocumentCount = appDocs.filter(doc => doc.requiredFlag !== 'optional' && doc.status !== 'verified').length;
  const docsPending = pendingDocumentCount > 0;
  const sapMissing = !app.sapCustomerCode;
  
  // Specific role gates
  const isCompliance = currentUser.role === 'compliance_team';
  const isCS = currentUser.role === 'company_secretary';
  const isSMFinance = currentUser.role === 'senior_manager_finance';
  const isCFC = currentUser.role === 'cfc';
  const isDMFinance = currentUser.role === 'deputy_manager_finance';
  const isCredit = currentUser.role === 'credit_manager';
  const isAuditor = currentUser.role === 'auditor';

  const canEditCompleteness = !isCompletenessReadOnly && (isDMFinance || isCredit) && !isAuditor;

  const handleReveal = (setter: React.Dispatch<React.SetStateAction<boolean>>, currentVal: boolean, type: string) => {
    if (isAuditor && !currentVal) {
      alert("Read-only access — sensitive data reveal is logged.");
    }
    setter(!currentVal);
  };

  type StepState = 'not_started' | 'in_progress' | 'completed' | 'blocked' | 'rejected' | 'exception';
  const stageState = (gt: boolean, eq: boolean): StepState => gt ? 'completed' : eq ? 'in_progress' : 'not_started';
  
  const stages = [
    { id: 's1', label: 'Submitted',    state: stageState(stageIndex > 0, stageIndex === 0), meta: '15 Apr 2026' },
    { id: 's2', label: 'Completeness', state: stageState(stageIndex > 1, stageIndex === 1), meta: 'Reference generated' },
    { id: 's3', label: 'Appraisal',    state: stageState(stageIndex > 2, stageIndex === 2), meta: 'Credit reviewed' },
    { id: 's4', label: 'Sanction',     state: stageState(stageIndex > 3, stageIndex === 3), meta: '20 Apr 2026' },
    { id: 's5', label: 'Documentation', state: (app.documentationStatus === 'complete' ? 'completed' : app.documentationStatus !== 'not_started' ? 'in_progress' : 'not_started') as StepState, meta: app.documentationStatus === 'complete' ? 'CS verified' : '' },
    { id: 's6', label: 'SAP Setup',    state: (app.sapCustomerCode ? 'completed' : app.documentationStatus === 'complete' ? 'in_progress' : 'not_started') as StepState, meta: app.sapCustomerCode ? `${app.sapCustomerCode} confirmed` : '' },
    { id: 's7', label: 'Disbursement', state: (isDisbursed ? 'completed' : app.sapCustomerCode ? 'in_progress' : 'not_started') as StepState, meta: isDisbursed ? 'Disbursed' : 'Pending' },
  ];

  const TABS = [
    { id: 'overview',      label: 'Overview' },
    { id: 'completeness',  label: 'Completeness Check' },
    { id: 'applicant',     label: 'Applicant & Member' },
    { id: 'nominee',       label: 'Nominee' },
    { id: 'witness',       label: 'Witness' },
    { id: 'eligibility',   label: 'Eligibility & Limit' },
    { id: 'sanction',      label: 'Sanction & Approvals' },
    { id: 'documents',     label: 'Documents', badge: pendingDocumentCount || undefined },
    { id: 'security',      label: 'Security' },
    { id: 'disbursement',  label: 'Disbursement' },
    { id: 'audit',         label: 'Audit Trail' },
  ];

  // Specific Gate Checks
  const isReadyForPayment = ['sanctioned', 'disbursement_ready', 'sap_customer_code_confirmed'].includes(app.status) && !docsPending && !!app.sapCustomerCode && !isDisbursed;

  let statusBadgeLabel = getApplicationStatusLabel(app);
  if (['sanctioned', 'documentation_in_progress', 'pending_final_checklist_approvals', 'disbursement_ready', 'sap_customer_code_pending', 'sap_customer_code_confirmed', 'payment_initiated', 'payment_authorized', 'transfer_executed', 'disbursed'].includes(app.status)) {
    if (app.disbursementStatus === 'pending_disbursement' || app.disbursementStatus === 'pending_documentation') {
      statusBadgeLabel = 'Sanctioned · Pending Disbursement';
    } else if (app.disbursementStatus === 'ready_for_payment' || app.disbursementStatus === 'disbursement_ready') {
      statusBadgeLabel = 'Disbursement Ready';
    } else if (app.disbursementStatus === 'pending_cfc_approval') {
      statusBadgeLabel = 'Payment Authorisation Pending';
    } else if (isDisbursed) {
      statusBadgeLabel = 'Disbursed';
    }
  }

  let computedOwner = app.currentOwner;

  if (stageIndex < 4) {
    computedOwner = app.currentOwner;
  } else if (app.documentationStatus === 'in_progress' || app.documentationStatus === 'documentation_in_progress' || app.documentationStatus === 'not_started') {
    computedOwner = 'Compliance Team';
  } else if (app.documentationStatus === 'pending_signature') {
    computedOwner = 'Company Secretary';
  } else if (app.documentationStatus === 'complete' && !app.sapCustomerCode) {
    computedOwner = 'Senior Manager – Finance';
  } else if (app.documentationStatus === 'complete' && app.sapCustomerCode && !isDisbursed) {
    if (app.disbursementStatus === 'pending_cfc_approval') {
      computedOwner = 'Chief Financial Controller';
    } else {
      computedOwner = 'Senior Manager – Finance';
    }
  } else if (isDisbursed) {
    computedOwner = 'Accounts';
  }

  const [completenessNote, setCompletenessNote] = useState('');
  const [completenessSubmitted, setCompletenessSubmitted] = useState(false);
  const [deficiencyNoticeSent, setDeficiencyNoticeSent] = useState(false);

  // For submitted apps being reviewed for the first time, items start as 'pending'
  const isInCompletenessReview = stageIndex === 0 && (app.status === 'submitted' || app.status === 'draft');

  const [itemOverrides, setItemOverrides] = useState<Record<string, 'passed' | 'deficiency' | 'pending'>>({});
  const [deficiencyNotes, setDeficiencyNotes] = useState<Record<string, string>>({});

  const getItemStatus = (id: string): 'passed' | 'deficiency' | 'pending' =>
    (itemOverrides[id] as 'passed' | 'deficiency' | 'pending') ?? (isInCompletenessReview ? 'pending' : 'passed');

  const markPassed = (id: string) => { if (canEditCompleteness) setItemOverrides(prev => ({ ...prev, [id]: 'passed' })); };
  const markDeficiency = (id: string) => { if (canEditCompleteness) setItemOverrides(prev => ({ ...prev, [id]: 'deficiency' })); };
  const clearItem = (id: string) => { if (canEditCompleteness) setItemOverrides(prev => ({ ...prev, [id]: 'pending' })); };

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-start gap-3">
        <button onClick={onBack} className="mt-1 text-slate-500 hover:text-slate-700">
          <ChevronLeft size={20} />
        </button>
        <div className="flex-1 flex items-start justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <h1 className="text-xl font-bold text-slate-900 num">{getApplicationReference(app)}</h1>
              <StatusBadge label={statusBadgeLabel} size="md" />
              {app.isException && (
                <span className="flex items-center gap-1 text-xs bg-violet-100 text-violet-700 px-2 py-1 rounded-full font-semibold">
                  <AlertOctagon size={12} /> Exception
                </span>
              )}
              {app.specialCase && (
                <span className="flex items-center gap-1 text-xs bg-amber-100 text-amber-700 px-2 py-1 rounded-full font-semibold">
                  <Shield size={12} /> Special Case
                </span>
              )}
            </div>
            <div className="flex items-center gap-3 mt-0.5 text-sm text-slate-500 flex-wrap">
              <span>{app.memberName}</span>
              <span>·</span>
              <span className="num">{fmt(app.requestedAmount)} requested</span>
              <span>·</span>
              <span>Applied {new Date(app.applicationDate).toLocaleDateString('en-IN')}</span>
              {app.tatDaysRemaining !== undefined && app.tatDaysRemaining <= 1 && (
                <>
                  <span>·</span>
                  <span className="flex items-center gap-1 text-amber-600 font-medium">
                    <Clock size={12} /> TAT: {app.tatDaysRemaining === 0 ? 'Overdue' : `${app.tatDaysRemaining}d`}
                  </span>
                </>
              )}
            </div>
          </div>
          <div className="flex flex-col items-end gap-1 text-sm text-slate-500">
            <span>Owner: <span className="font-medium text-slate-900">{computedOwner}</span></span>
          </div>
        </div>
      </div>

      {loadStatus === 'loading' && (
        <AlertBanner type="info" title="Loading application" message="Loading application details from the staff API." />
      )}
      {loadStatus === 'error' && (
        <AlertBanner type="warning" title="Application unavailable" message={loadMessage || 'Unable to load application.'} />
      )}
      {app.isException && app.exceptionReason && (
        <AlertBanner type="exception" title="Exception Case" message={app.exceptionReason} />
      )}
      
      <div className="card py-5">
        <StageStepper steps={stages} />
      </div>

      <Tabs tabs={TABS} activeIndex={activeTab} onChange={setActiveTab}>

        {/* ── Tab 0: Overview ── */}
        <div className="space-y-4">
          {isReadyForPayment && app.disbursementStatus !== 'pending_cfc_approval' && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <p className="text-sm font-semibold text-green-800">Ready for payment: documentation complete, SAP code confirmed and bank verification cleared.</p>
            </div>
          )}
          {['sanctioned', 'disbursement_ready', 'sap_customer_code_pending'].includes(app.status) && !docsPending && sapMissing && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-sm font-semibold text-red-800 flex items-center gap-2"><AlertTriangle size={16}/> Disbursement blocked: SAP code pending.</p>
            </div>
          )}
          
          <div className="card space-y-5">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              {app.isException && app.eligibleAmount && app.eligibleAmount < app.requestedAmount && (
                <div className="bg-slate-50 rounded-lg p-3 border border-violet-200">
                  <p className="text-xs text-slate-500 font-medium uppercase tracking-wide">Sanctioned Amount</p>
                  <p className="text-sm font-semibold text-slate-900 mt-0.5">{fmt(app.requestedAmount)}</p>
                  <div className="flex items-center gap-1 mt-1">
                    <span className="text-xs font-semibold bg-violet-100 text-violet-700 px-1.5 py-0.5 rounded">Exception approved</span>
                  </div>
                  <p className="text-xs text-slate-500 mt-1">Ref: EX-2026-015</p>
                </div>
              )}

              {[
                { label: 'Requested Amount', value: fmt(app.requestedAmount) },
                { label: 'Eligible Amount', value: fmt(app.eligibleAmount || 0) },
                { label: 'Loan Type', value: app.loanType === 'short_term' ? 'Short Term' : 'Long Term' },
                { label: 'Tenure', value: `${app.tenure} months` },
                { label: 'Purpose', value: app.purpose.replace(/_/g, ' ') },
                { label: 'Land Area', value: `${app.landAreaAcres} acres` },
                { label: 'Shares Held', value: `${app.sharesHeld} (${app.shareMode})` },
                { label: 'Risk Rating', value: app.riskRating || '—' },
              ].filter(item => !(item.label === 'Requested Amount' && app.isException && app.eligibleAmount && app.eligibleAmount < app.requestedAmount)).map(({ label, value }) => (
                <div key={label} className="bg-slate-50 rounded-lg p-3">
                  <p className="text-xs text-slate-500 font-medium uppercase tracking-wide">{label}</p>
                  <p className="text-sm font-semibold text-slate-900 mt-0.5 capitalize">{value}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Deficiency Communication Log — shown when deficiency has been raised */}
          {apiDeficiencies.length > 0 && (
            <div className="card p-0 overflow-hidden">
              <div className="px-5 py-3 bg-amber-50 border-b border-amber-200 flex items-center gap-2">
                <MessageSquare size={15} className="text-amber-600" />
                <h3 className="text-sm font-semibold text-amber-800">Deficiency Communication Log</h3>
              </div>
              <div className="divide-y divide-slate-100">
                {apiDeficiencies.map(entry => (
                  <div key={entry.deficiency_id} className="px-5 py-4">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap mb-1">
                          <span className="text-xs px-1.5 py-0.5 rounded font-semibold bg-slate-100 text-slate-600">{entry.item_code.replace(/_/g, ' ')}</span>
                          <span className="text-xs text-slate-400">{entry.resolution_status}</span>
                        </div>
                        <p className="text-sm text-slate-700">{entry.description}</p>
                        {entry.remarks && <p className="text-xs text-slate-400 mt-1">{entry.remarks}</p>}
                      </div>
                      <div className="text-right flex-shrink-0">
                        <p className="text-xs text-slate-500">{entry.raised_at ? new Date(entry.raised_at).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' }) : '—'}</p>
                        <span className="inline-block mt-1 text-[10px] px-1.5 py-0.5 rounded font-medium bg-slate-100 text-slate-500">{entry.resolution_status}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              <div className="px-5 py-3 bg-amber-50 border-t border-amber-100">
                <p className="text-xs text-amber-700 font-medium">Pending: borrower rectification for open deficiency items.</p>
              </div>
            </div>
          )}

          {rejectionNote && (
            <div className="card p-0 overflow-hidden">
              <div className="px-5 py-3 bg-slate-50 border-b border-slate-100 flex items-center gap-2">
                <MessageSquare size={15} className="text-slate-500" />
                <h3 className="text-sm font-semibold text-slate-800">Rejection Note</h3>
                <StatusBadge label={rejectionNote.note_status} size="sm" />
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 p-5">
                {[
                  { label: 'Stage', value: rejectionNote.rejection_stage.replace(/_/g, ' ') },
                  { label: 'Reason Category', value: rejectionNote.rejection_reason_category.replace(/_/g, ' ') },
                  { label: 'Communication Mode', value: rejectionNote.communication_mode.replace(/_/g, ' ') },
                  { label: 'Reapply Allowed', value: rejectionNote.reapply_allowed_flag ? 'Yes' : 'No' },
                ].map(({ label, value }) => (
                  <div key={label} className="bg-slate-50 rounded-lg p-3">
                    <p className="text-xs text-slate-500 font-medium uppercase tracking-wide">{label}</p>
                    <p className="text-sm font-semibold text-slate-900 mt-0.5 capitalize">{value}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* ── Tab 1: Completeness Check ── */}
        <div className="space-y-4">
          {isCompletenessReadOnly && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-sm text-blue-800 flex items-center gap-2">
              <Info size={16} /> Read-only — completeness was completed before appraisal.
            </div>
          )}

          {(() => {
            const naItems = COMPLETENESS_ITEMS.filter(i => i.id === 'share_certificate' && app.shareMode !== 'physical');
            const naIds = new Set(naItems.map(i => i.id));
            const reviewableItems = COMPLETENESS_ITEMS.filter(i => !naIds.has(i.id));
            const passedCount = reviewableItems.filter(i => getItemStatus(i.id) === 'passed').length;
            const deficiencyCount = reviewableItems.filter(i => getItemStatus(i.id) === 'deficiency').length;
            const pendingCount = reviewableItems.filter(i => getItemStatus(i.id) === 'pending').length;
            const reviewedCount = passedCount + deficiencyCount;
            const progressPct = Math.round((reviewedCount / reviewableItems.length) * 100);
            return (
              <div className="card">
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <h3 className="font-semibold text-slate-800 flex items-center gap-2">
                      <ClipboardList size={16} className="text-green-600" /> Application Completeness Check
                    </h3>
                    {isInCompletenessReview && canEditCompleteness ? (
                      <p className="text-xs text-amber-700 mt-0.5 font-medium">In review — {reviewedCount} of {reviewableItems.length} items reviewed · Use Pass / Flag buttons on each item</p>
                    ) : (
                      <p className="text-xs text-slate-500 mt-0.5">Performed by: Deputy Manager – Finance · {reviewableItems.length}/{reviewableItems.length} items reviewed</p>
                    )}
                  </div>
                  <div className="flex items-center gap-4">
                    {isInCompletenessReview && (
                      <div className="text-right">
                        <p className="text-xs text-slate-400">Pending</p>
                        <p className="text-lg font-bold text-amber-600">{pendingCount}</p>
                      </div>
                    )}
                    <div className="text-right">
                      <p className="text-xs text-slate-400">Passed</p>
                      <p className="text-lg font-bold text-green-700">{passedCount}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-xs text-slate-400">Deficient</p>
                      <p className="text-lg font-bold text-red-600">{deficiencyCount}</p>
                    </div>
                  </div>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all ${deficiencyCount > 0 ? 'bg-red-400' : 'bg-green-500'}`}
                    style={{ width: isInCompletenessReview ? `${progressPct}%` : '100%' }}
                  />
                </div>
                {isInCompletenessReview && (
                  <p className="text-xs text-slate-400 mt-1">{progressPct}% reviewed</p>
                )}
              </div>
            );
          })()}

          {COMPLETENESS_CATEGORIES.map(cat => {
            const items = COMPLETENESS_ITEMS.filter(i => i.category === cat);
            if (items.length === 0) return null;
            return (
              <div key={cat} className="card p-0 overflow-hidden">
                <div className="px-5 py-3 bg-slate-50 border-b border-slate-100">
                  <p className="text-xs font-semibold text-slate-600 uppercase tracking-wide">{cat}</p>
                </div>
                <div className="divide-y divide-slate-50">
                  {items.map(item => {
                    const displayLabel = item.label;
                    const isNa = item.id === 'share_certificate' && app.shareMode !== 'physical';
                    const status = isNa ? 'na' : getItemStatus(item.id);

                    let evidence: React.ReactNode = null;
                    if (!isNa) {
                      switch (item.id) {
                        case 'folio_number': evidence = member?.folioNumber ? `Folio ${member.folioNumber}` : null; break;
                        case 'shares_present': evidence = `${app.sharesHeld} shares · ${app.shareMode === 'physical' ? 'Physical' : 'Demat'}`; break;
                        case 'active_member': evidence = member?.activeStatus === 'active' ? 'Active member' : 'Not an active member'; break;
                        case 'loan_purpose': evidence = app.purpose === 'crop_production' || app.purpose === 'agriculture_activity' ? 'Crop production' : app.purpose.replace(/_/g, ' '); break;
                        case 'existing_default': evidence = member?.defaultStatus === 'no_default' ? 'No existing defaults' : 'Existing default found'; break;
                        case 'loan_amount': evidence = `₹${app.requestedAmount.toLocaleString('en-IN')} requested`; break;
                        case 'nominee_fields': evidence = app.nomineeId ? `Nominee ref: ${app.nomineeId}` : null; break;
                        case 'nominee_age': evidence = "Not minor (from docs)"; break;
                        case 'applicant_signature':
                        case 'nominee_signature': evidence = "Physical form verified"; break;
                        case 'borrower_kyc':
                        case 'nominee_kyc':
                        case 'land_712':
                        case 'crop_plan':
                        case 'bank_statement': {
                          const requiredDocs = item.id === 'borrower_kyc' ? ['pan', 'aadhaar'] :
                                               item.id === 'nominee_kyc' ? ['nominee_pan', 'nominee_aadhaar'] :
                                               item.id === 'land_712' ? ['land_712'] :
                                               item.id === 'crop_plan' ? ['crop_plan'] :
                                               ['bank_statement'];
                          evidence = (
                            <div className="flex gap-1.5 flex-wrap mt-1">
                              {requiredDocs.map(dtype => {
                                const doc = appDocs.find(d => d.documentType === dtype);
                                const isUploaded = doc && ['uploaded', 'verified', 'complete', 'under_review', 'signed'].includes(doc.status);
                                return (
                                  <span key={dtype} className={`text-[10px] px-1.5 py-0.5 rounded font-medium border ${isUploaded ? 'bg-slate-50 border-slate-200 text-slate-600' : 'bg-red-50 border-red-200 text-red-600'}`}>
                                    {dtype.replace(/_/g, ' ')} {isUploaded ? 'uploaded' : 'missing'}
                                  </span>
                                );
                              })}
                            </div>
                          );
                          break;
                        }
                      }
                    }

                    return (
                      <div key={item.id} className={`px-5 py-3 ${status === 'deficiency' ? 'bg-red-50' : status === 'passed' ? 'bg-green-50/40' : ''}`}>
                        <div className="flex items-start gap-3">
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 flex-wrap">
                              <span className="text-sm font-medium text-slate-800">{displayLabel}</span>
                              {!item.required && <span className="text-xs text-slate-400 bg-slate-100 px-1.5 py-0.5 rounded">Optional</span>}
                            </div>
                            {evidence && <div className="mt-1 text-xs font-medium text-slate-600">{evidence}</div>}
                            {status === 'deficiency' && (
                              <>
                                <p className="text-xs text-red-600 mt-1 font-medium">{item.deficiencyReason}</p>
                                {canEditCompleteness && (
                                  <input
                                    type="text"
                                    value={deficiencyNotes[item.id] || ''}
                                    onChange={e => setDeficiencyNotes(prev => ({ ...prev, [item.id]: e.target.value }))}
                                    placeholder="Add note for borrower (e.g. Aadhaar copy is blurred)"
                                    className="mt-1.5 w-full text-xs border border-red-200 rounded px-2.5 py-1.5 bg-white text-red-800 placeholder-red-300 focus:outline-none focus:ring-1 focus:ring-red-300"
                                  />
                                )}
                              </>
                            )}
                            {status === 'pending' && canEditCompleteness && !evidence && (
                              <p className="text-xs text-slate-400 mt-0.5">Not yet reviewed</p>
                            )}
                            {status === 'pending' && canEditCompleteness && evidence && (
                              <p className="text-xs text-amber-600 mt-1 italic">Review required</p>
                            )}
                          </div>
                          <div className="flex items-center gap-2 flex-shrink-0 pt-0.5">
                            {isNa ? (
                              <span className="text-xs font-medium text-slate-500 bg-slate-100 px-2.5 py-1 rounded-lg">N/A</span>
                            ) : status === 'passed' ? (
                              <>
                                <StatusBadge label="Passed" size="sm" />
                                {canEditCompleteness && (
                                  <button onClick={() => markDeficiency(item.id)} className="text-xs text-slate-400 hover:text-red-600 px-1.5 py-1 rounded hover:bg-red-50 transition-colors">Flag</button>
                                )}
                              </>
                            ) : status === 'deficiency' ? (
                              <>
                                <StatusBadge label="deficiency_raised" size="sm" />
                                {canEditCompleteness && (
                                  <button onClick={() => clearItem(item.id)} className="text-xs text-slate-400 hover:text-slate-700 px-1.5 py-1 rounded hover:bg-slate-100 transition-colors">Clear</button>
                                )}
                              </>
                            ) : (
                              canEditCompleteness ? (
                                <div className="flex gap-1">
                                  <button
                                    onClick={() => markPassed(item.id)}
                                    className="text-xs px-2.5 py-1 rounded border border-green-200 text-green-700 bg-white hover:bg-green-50 font-medium transition-colors flex items-center gap-1"
                                  >
                                    <CheckCircle2 size={11} /> Pass
                                  </button>
                                  <button
                                    onClick={() => markDeficiency(item.id)}
                                    className="text-xs px-2.5 py-1 rounded border border-red-200 text-red-600 bg-white hover:bg-red-50 font-medium transition-colors flex items-center gap-1"
                                    title="Flag deficiency"
                                  >
                                    <AlertTriangle size={11} /> <span className="hidden sm:inline">Flag deficiency</span><span className="sm:hidden">Flag</span>
                                  </button>
                                </div>
                              ) : (
                                <span className="text-xs text-amber-600 bg-amber-50 border border-amber-100 px-2 py-0.5 rounded font-medium">Pending</span>
                              )
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })}

          {(() => {
            const naIds = new Set(COMPLETENESS_ITEMS.filter(i => i.id === 'share_certificate' && app.shareMode !== 'physical').map(i => i.id));
            const reviewable = COMPLETENESS_ITEMS.filter(i => !naIds.has(i.id));
            const deficiencyItems = reviewable.filter(i => getItemStatus(i.id) === 'deficiency');
            const pendingItems = reviewable.filter(i => getItemStatus(i.id) === 'pending');
            const allRequiredPassed = reviewable.filter(i => i.required).every(i => getItemStatus(i.id) === 'passed');
            const hasDeficiencies = deficiencyItems.length > 0;

            return (
              <div className="card space-y-4">
                <h4 className="text-sm font-semibold text-slate-700">Completeness Check Note</h4>

                {isInCompletenessReview && canEditCompleteness ? (
                  <>
                    <textarea
                      value={completenessNote}
                      onChange={e => setCompletenessNote(e.target.value)}
                      rows={2}
                      placeholder="Add an internal note (optional) — e.g. Borrower called on 27 Jun, will resubmit 7/12 by 30 Jun"
                      className="w-full text-sm border border-slate-200 rounded-lg px-3 py-2 text-slate-700 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-green-300 resize-none"
                    />

                    {hasDeficiencies && (
                      <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 space-y-3">
                        <p className="text-sm font-semibold text-amber-800 flex items-center gap-2">
                          <AlertTriangle size={15} /> {deficiencyItems.length} deficien{deficiencyItems.length === 1 ? 'cy' : 'cies'} flagged
                        </p>
                        <ul className="text-xs text-amber-700 space-y-1 list-disc list-inside">
                          {deficiencyItems.map(i => (
                            <li key={i.id}>{i.label}{deficiencyNotes[i.id] ? ` — ${deficiencyNotes[i.id]}` : ''}</li>
                          ))}
                        </ul>
                        {deficiencyNoticeSent ? (
                          <div className="flex items-center gap-2 text-sm font-medium text-amber-700 bg-amber-100 border border-amber-200 rounded-lg px-3 py-2">
                            <CheckCircle2 size={14} /> Deficiency notice sent to borrower · {new Date().toLocaleDateString('en-IN')}
                          </div>
                        ) : null}
                      </div>
                    )}

                    <div className="flex flex-col items-end gap-2 border-t border-slate-100 pt-4 mt-4">
                      <div className="flex items-center gap-3 flex-wrap">
                        <button
                          disabled={!allRequiredPassed || hasDeficiencies || completenessSubmitted}
                          onClick={() => setCompletenessSubmitted(true)}
                          className="btn-primary flex items-center gap-2"
                        >
                          <ArrowRight size={14} /> Generate loan reference
                        </button>
                        <button
                          disabled={!hasDeficiencies || !completenessNote.trim() || completenessSubmitted || deficiencyNoticeSent}
                          onClick={() => setDeficiencyNoticeSent(true)}
                          className="btn-secondary flex items-center gap-2"
                          title={!completenessNote.trim() ? "Internal comment required" : ""}
                        >
                          <Send size={14} /> Return for deficiency
                        </button>
                        <button
                          disabled={!completenessNote.trim() || completenessSubmitted || hasDeficiencies}
                          onClick={() => alert("Rejection recommended")}
                          className="btn-destructive flex items-center gap-2"
                          title={hasDeficiencies ? "Use Return for Deficiency for missing items" : !completenessNote.trim() ? "Reason required" : ""}
                        >
                          <XCircle size={14} /> Recommend rejection
                        </button>
                      </div>
                      {!allRequiredPassed && !hasDeficiencies && <span className="text-[10px] text-slate-400 font-medium">Complete all mandatory checks before generating the loan reference.</span>}
                    </div>

                    {completenessSubmitted && (
                      <div className="flex items-center gap-2 mt-4 pt-4 border-t border-slate-100">
                        <span className="text-sm font-medium text-green-700 bg-green-50 px-4 py-2 rounded-lg flex items-center gap-2 border border-green-200">
                          <CheckCircle2 size={16} /> {hasFormalLoanReference(app) ? `Reference generated · ${getApplicationReference(app)}` : 'Reference generated'}
                        </span>
                      </div>
                    )}
                  </>
                ) : (
                  <>
                    <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 text-sm text-slate-700">
                      Completeness passed. Reference generated and application moved to appraisal.
                    </div>
                    <div className="border-t border-slate-100 pt-4 mt-4">
                      <h4 className="text-sm font-semibold text-slate-700 mb-2">Deficiency History</h4>
                      <p className="text-xs text-slate-500">No deficiencies recorded during completeness check.</p>
                    </div>
                    <div className="flex items-center gap-2 mt-4 pt-4 border-t border-slate-100">
                      <span className="text-sm font-medium text-green-700 bg-green-50 px-4 py-2 rounded-lg flex items-center gap-2 border border-green-200">
                        <CheckCircle2 size={16} /> Reference generated · {getApplicationReference(app)}
                      </span>
                    </div>
                  </>
                )}
              </div>
            );
          })()}
        </div>

        {/* ── Tab 2: Applicant & Member ── */}
        <div className="card space-y-4">
          {member ? (
            <>
              <div className="flex items-start justify-between">
                <h3 className="text-sm font-semibold text-slate-700">Member Profile</h3>
                <button onClick={() => onNavigateMember(member.id)} className="text-xs text-green-600 flex items-center gap-1 hover:underline">
                  Full profile <ExternalLink size={12} />
                </button>
              </div>

              <div className={`flex items-center gap-3 px-4 py-3 rounded-xl border ${
                member.activeStatus === 'active' ? 'bg-green-50 border-green-200' : 'bg-amber-50 border-amber-200'
              }`}>
                {member.activeStatus === 'active'
                  ? <CheckCircle2 size={16} className="text-green-600 flex-shrink-0" />
                  : <AlertTriangle size={16} className="text-amber-600 flex-shrink-0" />}
                <div>
                  <p className={`text-sm font-semibold ${member.activeStatus === 'active' ? 'text-green-800' : 'text-amber-800'}`}>
                    {member.activeStatus === 'active' && member.supplyYears < 4 ? 'Active Member · Eligible under configured service route' : (member.activeStatus === 'active' ? 'Active Member ✓' : 'Active status requires review')}
                  </p>
                  <p className={`text-xs ${member.activeStatus === 'active' ? 'text-green-600' : 'text-amber-600'}`}>
                    {member.activeStatus === 'active' && member.supplyYears < 4 ? `${member.supplyYears} years evidence confirmed under active policy.` : `${member.supplyYears} year(s) supply — does not meet the configured active-member rule.`}
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
                {[
                  { label: 'Name', value: member.name },
                  { label: 'Folio', value: member.folioNumber },
                  { label: 'Member Type', value: member.memberType.toUpperCase() },
                  { label: 'Mobile', value: member.mobile },
                  { label: 'KYC Status', value: member.kycStatus.replace(/_/g, ' ') },
                  { label: 'Supply Years', value: `${member.supplyYears} years` },
                  { label: 'Shares Held', value: `${member.sharesHeld} (${member.shareMode})` },
                  { label: 'Default Status', value: member.defaultStatus.replace(/_/g, ' ') },
                  { label: 'Current Exposure', value: fmt(member.currentExposure) },
                ].map(({ label, value }) => (
                  <div key={label} className="bg-slate-50 rounded-lg p-3">
                    <p className="text-xs text-slate-500 font-medium uppercase tracking-wide">{label}</p>
                    <p className="text-sm font-semibold text-slate-900 mt-0.5">{value}</p>
                  </div>
                ))}
              </div>

              <div className="border-t border-slate-100 pt-4">
                <p className="text-xs text-slate-500 font-semibold uppercase tracking-wide mb-3 flex items-center gap-1">
                  <Lock size={12} /> Sensitive Identifiers — Masked
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div className="flex items-center gap-3 bg-amber-50 border border-amber-100 rounded-lg p-3">
                    <div className="flex-1">
                      <p className="text-xs text-slate-500">PAN</p>
                      <p className="text-sm font-mono font-semibold text-slate-900">{panRevealed ? member.pan : '••••••••••'}</p>
                    </div>
                    <button onClick={() => handleReveal(setPanRevealed, panRevealed, 'PAN')} className="text-xs text-amber-700 flex items-center gap-1 hover:underline">
                      {panRevealed ? <EyeOff size={12} /> : <Eye size={12} />} {panRevealed ? 'Hide' : 'Reveal'}
                    </button>
                  </div>
                  <div className="flex items-center gap-3 bg-amber-50 border border-amber-100 rounded-lg p-3">
                    <div className="flex-1">
                      <p className="text-xs text-slate-500">Aadhaar</p>
                      <p className="text-sm font-mono font-semibold text-slate-900">{aadhaarRevealed ? member.aadhaar : '••••-••••-••••'}</p>
                    </div>
                    <button onClick={() => handleReveal(setAadhaarRevealed, aadhaarRevealed, 'Aadhaar')} className="text-xs text-amber-700 flex items-center gap-1 hover:underline">
                      {aadhaarRevealed ? <EyeOff size={12} /> : <Eye size={12} />} {aadhaarRevealed ? 'Hide' : 'Reveal'}
                    </button>
                  </div>
                </div>
              </div>
              <div>
                <p className="text-xs text-slate-500 font-medium uppercase tracking-wide mb-1">Address</p>
                <p className="text-sm text-slate-800">{member.address}</p>
              </div>
            </>
          ) : (
            <p className="text-slate-400 text-sm">Member data not available.</p>
          )}
        </div>

        {/* ── Tab 3: Nominee ── */}
        <div className="space-y-4">
          <div className="card space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold text-slate-800 flex items-center gap-2">
                <User size={16} className="text-green-600" /> Nominee Details
              </h3>
              <StatusBadge label={nominee?.kyc_status ?? 'Unavailable'} size="sm" />
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
              {[
                { label: 'Full Name', value: nominee?.nominee_name ?? 'Not available' },
                { label: 'Age', value: nominee?.age_at_application != null ? String(nominee.age_at_application) : 'Not available' },
                { label: 'Minor Status', value: nominee ? (nominee.minor_flag ? 'Minor' : 'Adult') : 'Not available' },
                { label: 'Relationship to Borrower', value: nominee?.relationship_to_borrower ?? 'Not available' },
                { label: 'KYC Status', value: nominee?.kyc_status?.replace(/_/g, ' ') ?? 'Not available' },
                { label: 'Signature Required', value: nominee ? (nominee.signature_required_flag ? 'Required' : 'Not required') : 'Not available' },
              ].map(({ label, value }) => (
                <div key={label} className="bg-slate-50 rounded-lg p-3">
                  <p className="text-xs text-slate-500 font-medium uppercase tracking-wide">{label}</p>
                  <p className="text-sm font-semibold mt-0.5 text-slate-900">{value}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* ── Tab 4: Witness ── */}
        <div className="space-y-4">
          <div className="card space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold text-slate-800 flex items-center gap-2">
                <Users size={16} className="text-blue-600" /> Witness Details
              </h3>
              <StatusBadge label="Unavailable" size="sm" />
            </div>
            <p className="text-sm text-slate-500">No API-backed witness details are available for this application yet.</p>
          </div>
        </div>

        {/* ── Tab 5: Eligibility & Limit ── */}
        <div className="space-y-4">
          <div className="card">
            <h3 className="text-sm font-semibold text-slate-700 mb-4">Loan Limit Calculation</h3>
            <LoanLimitCalculator
              sharesHeld={app.sharesHeld}
              shareMode={app.shareMode}
              landAreaAcres={app.landAreaAcres}
              requestedAmount={app.requestedAmount}
              readonly
            />
          </div>
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-semibold text-slate-700">Eligibility Checklist</h3>
              <div className="flex items-center gap-2">
                <span className="text-xs font-semibold bg-violet-100 text-violet-700 px-2 py-1 rounded-full">Above eligible limit</span>
                <span className="text-xs font-medium text-slate-600 bg-slate-100 px-3 py-1 rounded-full">10 checks passed · 1 exception approved</span>
              </div>
            </div>
            <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 text-sm text-amber-800 mb-4">
              <strong>Loan limit policy requires confirmation.</strong> Policy version: POL-2026-01 · Formula: shares × ₹2,000 × 30% · Land cap: ₹20,000/acre
            </div>
            <EligibilityChecklist memberId={app.memberId} applicationId={applicationId} />
          </div>
        </div>

        {/* ── Tab 6: Sanction & Approvals ── */}
        <div className="space-y-4">
          <div className="card border-l-4 border-l-violet-400">
            <div className="flex items-start gap-3">
              <AlertOctagon size={18} className="text-violet-600 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <h4 className="font-semibold text-slate-800 mb-2">Exception Override Details</h4>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm mb-4">
                  {[
                    { label: 'Exception Register', value: 'EX-2026-015' },
                    { label: 'Exception Reason', value: app.exceptionReason },
                    { label: 'Required Authority', value: 'CFO + 2 Directors + Exception Register' },
                    { label: 'Approval Status', value: 'Approved (20 Apr 2026)' },
                  ].map(({ label, value }) => (
                    <div key={label} className="bg-violet-50 rounded-lg p-3">
                      <p className="text-xs text-slate-500">{label}</p>
                      <p className="text-sm font-semibold text-violet-800">{value}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
          <div className="card">
            <h3 className="text-sm font-semibold text-slate-700 mb-4">Sanction Committee Approval</h3>
            <ApprovalPanel
              applicationNumber={app.applicationNumber}
              requestedAmount={app.requestedAmount}
              isException={app.isException}
              isSpecialCase={app.specialCase}
              approvers={[
                { role: 'CFO', name: 'Suresh Nair', decision: 'approved', timestamp: '20 Apr 2026, 09:45 AM', comment: 'Approved for limit override.' },
                { role: 'Director 1', name: 'Anita Desai', decision: 'approved', timestamp: '20 Apr 2026, 09:50 AM' },
                { role: 'Director 2', name: 'Prakash Joshi', decision: 'approved', timestamp: '20 Apr 2026, 10:00 AM' },
              ]}
            />
          </div>
        </div>

        {/* ── Tab 7: Documents ── */}
        <div className="card">
          <h3 className="text-sm font-semibold text-slate-700 mb-4">Document Checklist</h3>
          <DocumentChecklist 
            applicationId={app.id} 
            shareMode={app.shareMode}
            readOnly={!can('manage_documentation')}
          />
        </div>

        {/* ── Tab 8: Security ── */}
        <div className="card">
          <h3 className="text-sm font-semibold text-slate-700 mb-4">Security Instruments</h3>
          <div className="space-y-3">
            <div className="flex items-center gap-4 p-3 bg-slate-50 rounded-lg border border-slate-200">
              <div className="flex-1">
                <div className="font-semibold text-slate-900 text-sm">CDSL Pledge</div>
                <div className="text-xs text-slate-500 mt-0.5">
                  Executed: 2026-04-22 · Custodian: Company Secretary · PSN: CDSL-2026-00234
                </div>
              </div>
              <StatusBadge label="Pledged" size="sm" />
            </div>
            <div className="flex items-center gap-4 p-3 bg-slate-50 rounded-lg border border-slate-200">
              <div className="flex-1">
                <div className="font-semibold text-slate-900 text-sm">SH-4 Physical Share Security</div>
                <div className="text-xs text-slate-500 mt-0.5">Not required for Demat shares</div>
              </div>
              <StatusBadge label="Not required" size="sm" />
            </div>
            <div className="flex items-center gap-4 p-3 bg-slate-50 rounded-lg border border-slate-200">
              <div className="flex-1">
                <div className="font-semibold text-slate-900 text-sm">Blank-dated Cheque</div>
                <div className="text-xs text-slate-500 mt-0.5">Pending custody verification</div>
              </div>
              <StatusBadge label="Pending" size="sm" />
            </div>
            <div className="flex items-center gap-4 p-3 bg-slate-50 rounded-lg border border-slate-200">
              <div className="flex-1">
                <div className="font-semibold text-slate-900 text-sm">Power of Attorney</div>
                <div className="text-xs text-slate-500 mt-0.5">Pending notarisation</div>
              </div>
              <StatusBadge label="Pending" size="sm" />
            </div>
          </div>
        </div>

        {/* ── Tab 9: Disbursement ── */}
        <div className="card space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-slate-700">Disbursement Authorisation</h3>
            <span className="text-sm font-medium text-amber-700 bg-amber-50 px-3 py-1.5 rounded border border-amber-200">
              Blocked — documentation pending
            </span>
          </div>
          
          <div className="bg-slate-50 p-4 rounded-lg border border-slate-200 mb-4">
            <h4 className="text-sm font-semibold text-slate-800 mb-3">Readiness Checklist</h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
              <div className="flex items-center gap-2"><CheckCircle2 size={16} className="text-green-600" /> Sanction approved</div>
              <div className="flex items-center gap-2"><CheckCircle2 size={16} className="text-green-600" /> Exception approval</div>
              <div className="flex items-center gap-2"><CheckCircle2 size={16} className="text-green-600" /> SAP code confirmed</div>
              <div className="flex items-center gap-2"><XCircle size={16} className="text-amber-600" /> Documentation checklist pending</div>
              <div className="flex items-center gap-2"><XCircle size={16} className="text-amber-600" /> Security pending</div>
              <div className="flex items-center gap-2"><XCircle size={16} className="text-amber-600" /> Bank verification pending</div>
              <div className="flex items-center gap-2"><XCircle size={16} className="text-amber-600" /> Final sign-offs pending</div>
              <div className="flex items-center gap-2"><AlertTriangle size={16} className="text-red-600" /> Payment blocker open</div>
            </div>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
            {[
              { label: 'SAP Customer Code', value: app.sapCustomerCode || '⚠ Pending assignment' },
              { label: 'Bank Account', value: app.bankAccount || '—' },
              { label: 'Bank IFSC', value: app.bankIfsc || '—' },
            ].map(({ label, value }) => (
              <div key={label} className="bg-slate-50 rounded-lg p-3">
                <p className="text-xs text-slate-500 font-medium uppercase tracking-wide">{label}</p>
                <p className={`text-sm font-semibold mt-0.5 ${value.includes('⚠') ? 'text-amber-700' : 'text-slate-900'}`}>{value}</p>
              </div>
            ))}
          </div>

          <div className="border-t border-slate-100 pt-4 flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-800">Action: Mark Ready for Payment</p>
              <p className="text-xs text-slate-500 mt-1">Complete required gates before payment can proceed.</p>
            </div>
            <div>
              <button disabled className="btn-primary px-4 py-2 text-sm opacity-50 cursor-not-allowed">
                Mark Ready for Payment
              </button>
            </div>
          </div>
        </div>

        {/* ── Tab 10: Audit Trail ── */}
        <div className="card p-0 overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
            <h3 className="font-semibold text-slate-800">Application Audit Trail</h3>
            <button className="flex items-center gap-1 text-xs text-green-700 hover:underline">
              <Download size={12} /> Export
            </button>
          </div>
          <div className="divide-y divide-slate-50">
            {auditEvents.filter(e =>
              e.entityId === applicationId ||
              e.entityId === app.id ||
              e.entityId === app.applicationNumber ||
              e.entityId === app.intakeReference ||
              e.entityId === app.officialReference
            ).map((ev, i) => (
              <div key={i} className="flex gap-4 px-6 py-4 hover:bg-slate-50">
                <div className="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <History size={14} className="text-slate-500" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-sm font-semibold text-slate-900">{ev.eventType}</span>
                    {ev.previousState && (
                      <span className="flex items-center gap-1 text-xs text-slate-400">
                        <span className="bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded">{ev.previousState}</span>
                        <ArrowRight size={10} />
                        <span className="bg-green-100 text-green-700 px-1.5 py-0.5 rounded">{ev.newState}</span>
                      </span>
                    )}
                  </div>
                  {ev.comment && <p className="text-xs text-slate-500 mt-0.5">{ev.comment}</p>}
                  {ev.reason && <p className="text-xs text-red-500 mt-0.5">{ev.reason}</p>}
                  <p className="text-xs text-slate-400 mt-0.5">
                    {ev.actorName} · {ev.actorRole.replace(/_/g, ' ')} · {new Date(ev.timestamp).toLocaleString('en-IN')}
                  </p>
                </div>
              </div>
            ))}
          </div>
          <AuditTimeline entityId={applicationId} />
        </div>
      </Tabs>
    </div>
  );
};

export default ApplicationDetail;
