import React, { useState } from 'react';
import {
  ChevronLeft, ExternalLink, AlertOctagon, Clock, Eye, EyeOff,
  CheckCircle2, XCircle, AlertTriangle, User, Users, Shield,
  FileText, Lock, Download, Plus, MessageSquare, History,
  ArrowRight, Banknote, Gavel, ClipboardList, BarChart2, Info
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
import { loanApplications, members, securities, auditEvents, documents } from '../../data/mockData';
import { useRole } from '../../contexts/RoleContext';

const fmt = (n: number) => '₹' + n.toLocaleString('en-IN');

const STAGE_MAP: Record<string, number> = {
  draft: 0, submitted: 0, incomplete: 0,
  reference_generated: 1, appraisal_pending: 2, credit_review: 2,
  pending_sanction: 3, sanctioned: 4, rejected_credit: 4, rejected_sanction: 4,
};

const COMPLETENESS_ITEMS = [
  { id: 'c00a', category: 'Application Data', label: 'Folio number present', required: true },
  { id: 'c00b', category: 'Application Data', label: 'Shares held present', required: true },
  { id: 'c00c', category: 'Application Data', label: 'Requested loan amount present', required: true },
  { id: 'c00d', category: 'Application Data', label: 'Loan purpose valid', required: true },
  { id: 'c00e', category: 'Application Data', label: 'Nominee details complete', required: true },
  { id: 'c00f', category: 'Application Data', label: 'Applicant signature present', required: true },
  { id: 'c01', category: 'Borrower KYC', label: 'PAN Card (self-attested)', required: true },
  { id: 'c02', category: 'Borrower KYC', label: 'Aadhaar Card (self-attested)', required: true },
  { id: 'c03', category: 'Borrower KYC', label: 'Recent photograph', required: true },
  { id: 'c04', category: 'Nominee KYC', label: 'Nominee PAN copy', required: true },
  { id: 'c05', category: 'Nominee KYC', label: 'Nominee Aadhaar copy', required: true },
  { id: 'c06', category: 'Shareholding', label: 'Folio / demat holding evidence', required: true },
  { id: 'c07', category: 'Land & Crop', label: '7/12 extract (current season)', required: true },
  { id: 'c08', category: 'Land & Crop', label: 'Crop plan / scale of finance evidence', required: true },
  { id: 'c09', category: 'Financial', label: 'Six-month bank statement', required: true },
  { id: 'c10', category: 'Financial', label: 'Repayment capacity evidence — Optional / appraisal support', required: false },
  { id: 'c11', category: 'Application Form', label: 'Signed application form (all pages)', required: true },
  { id: 'c12', category: 'Application Form', label: 'Nominee signature & consent', required: true },
  { id: 'c13', category: 'Other', label: 'Board Resolution — FPC / Producer Institution only', required: true },
];

const witnessData = {
  w1: {
    name: 'Rajan Marathe', dob: '1975-05-10', age: 49, gender: 'Male',
    relation: 'Neighbour', mobile: '9821234567', address: 'Village Panchkund, Nashik, MH 422001',
    identityType: 'Aadhaar', identityNumber: '****-****-7321',
    signatureObtained: true, date: '2024-09-18', memberNumber: 'FO-0442', shareholderVerification: 'Verified', panStatus: 'Verified', aadhaarStatus: 'Verified', required: true
  },
  w2: {
    name: 'Sunanda Patil', dob: '1968-11-22', age: 55, gender: 'Female',
    relation: 'Village member', mobile: '9922345678', address: 'Village Panchkund, Nashik, MH 422001',
    identityType: 'Aadhaar', identityNumber: '****-****-4490',
    signatureObtained: false, date: null, memberNumber: 'FO-0211', shareholderVerification: 'Pending', panStatus: 'Pending', aadhaarStatus: 'Uploaded', required: false
  },
};

interface ApplicationDetailProps {
  applicationId: string;
  onBack: () => void;
  onNavigateMember: (memberId: string) => void;
}

const ApplicationDetail: React.FC<ApplicationDetailProps> = ({
  applicationId, onBack, onNavigateMember,
}) => {
  const app = loanApplications.find(a => a.id === applicationId || a.applicationNumber === applicationId) || loanApplications[0];
  const member = members.find(m => m.id === app.memberId);
  const appDocs = documents.filter(d => d.applicationId === applicationId);
  const appSecurities = securities.filter(s => s.applicationId === applicationId);
  const { can, currentUser } = useRole();

  const [activeTab, setActiveTab] = useState(0);
  const [panRevealed, setPanRevealed] = useState(false);
  const [aadhaarRevealed, setAadhaarRevealed] = useState(false);
  const [nomineePanRevealed, setNomineePanRevealed] = useState(false);
  const [nomineeAadhaarRevealed, setNomineeAadhaarRevealed] = useState(false);

  const stageIndex = STAGE_MAP[app.status] ?? 0;
  const isCompletenessReadOnly = stageIndex > 1;

  // Derived state for the specific mock loan LO00000035 as requested
  const isLO35 = app.applicationNumber === 'LO00000035';
  
  // Hardcoded states driven by the prompt's instruction for this specific loan:
  const docsPending = app.documentationStatus !== 'complete';
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
  
  let stages = [
    { id: 's1', label: 'Submitted',    state: stageState(stageIndex > 0, stageIndex === 0), meta: '15 Apr 2026' },
    { id: 's2', label: 'Completeness', state: stageState(stageIndex > 1, stageIndex === 1), meta: 'Reference generated' },
    { id: 's3', label: 'Appraisal',    state: stageState(stageIndex > 2, stageIndex === 2), meta: 'Credit reviewed' },
    { id: 's4', label: 'Sanction',     state: stageState(stageIndex > 3, stageIndex === 3), meta: '20 Apr 2026' },
    { id: 's5', label: 'Documentation', state: (app.documentationStatus === 'complete' ? 'completed' : app.documentationStatus !== 'not_started' ? 'in_progress' : 'not_started') as StepState, meta: app.documentationStatus === 'complete' ? 'CS verified' : '' },
    { id: 's6', label: 'SAP Setup',    state: (app.sapCustomerCode ? 'completed' : app.documentationStatus === 'complete' ? 'in_progress' : 'not_started') as StepState, meta: app.sapCustomerCode ? `${app.sapCustomerCode} confirmed` : '' },
    { id: 's7', label: 'Disbursement', state: (app.disbursementStatus === 'completed' ? 'completed' : app.sapCustomerCode ? 'in_progress' : 'not_started') as StepState, meta: app.disbursementStatus === 'completed' ? 'Disbursed' : 'Pending' },
  ];

  if (isLO35 && docsPending) {
    stages = stages.map(s => {
      if (s.id === 's5') return { ...s, state: 'blocked', meta: '11 items pending' };
      if (s.id === 's6') return { ...s, state: 'not_started', meta: app.sapCustomerCode ? `${app.sapCustomerCode} confirmed` : '' };
      if (s.id === 's7') return { ...s, state: 'not_started', meta: 'Blocked' };
      return s;
    });
  }

  const TABS = [
    { id: 'overview',      label: 'Overview' },
    { id: 'completeness',  label: 'Completeness Check' },
    { id: 'applicant',     label: 'Applicant & Member' },
    { id: 'nominee',       label: 'Nominee' },
    { id: 'witness',       label: 'Witness', badge: 1 },
    { id: 'eligibility',   label: 'Eligibility & Limit' },
    { id: 'sanction',      label: 'Sanction & Approvals' },
    { id: 'documents',     label: 'Documents', badge: docsPending ? 11 : undefined },
    { id: 'security',      label: 'Security' },
    { id: 'disbursement',  label: 'Disbursement' },
    { id: 'audit',         label: 'Audit Trail' },
  ];

  // Specific Gate Checks
  const isReadyForPayment = app.status === 'sanctioned' && !docsPending && !!app.sapCustomerCode && app.disbursementStatus !== 'completed';

  let statusBadgeLabel = app.status;
  if (isLO35 && docsPending) {
    statusBadgeLabel = 'Sanctioned · Documentation Pending';
  } else if (app.status === 'sanctioned') {
    if (app.disbursementStatus === 'pending_disbursement' || app.disbursementStatus === 'pending_documentation') {
      statusBadgeLabel = 'Sanctioned · Pending Disbursement';
    } else if (app.disbursementStatus === 'ready_for_payment') {
      statusBadgeLabel = 'Ready for Payment';
    } else if (app.disbursementStatus === 'pending_cfc_approval') {
      statusBadgeLabel = 'Payment Authorisation Pending';
    } else if (app.disbursementStatus === 'completed') {
      statusBadgeLabel = 'Disbursed';
    }
  }

  let computedOwner = app.currentOwner;
  let nextAction = '';

  if (isLO35 && docsPending) {
    computedOwner = 'Compliance Team / Company Secretary';
    nextAction = 'Clear documentation blockers';
  } else if (app.documentationStatus === 'in_progress' || app.documentationStatus === 'not_started') {
    computedOwner = 'Compliance Team';
  } else if (app.documentationStatus === 'pending_signature') {
    computedOwner = 'Company Secretary';
  } else if (app.documentationStatus === 'complete' && !app.sapCustomerCode) {
    computedOwner = 'Senior Manager – Finance';
  } else if (app.documentationStatus === 'complete' && app.sapCustomerCode && app.disbursementStatus !== 'completed') {
    if (app.disbursementStatus === 'pending_cfc_approval') {
      computedOwner = 'Chief Financial Controller';
      nextAction = 'Authorise bank transfer';
    } else {
      computedOwner = 'Senior Manager – Finance';
      nextAction = 'Mark ready for payment';
    }
  } else if (app.disbursementStatus === 'completed') {
    computedOwner = 'Accounts';
  }

  const [completenessNote, setCompletenessNote] = useState('');

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-start gap-3">
        <button onClick={onBack} className="mt-1 text-slate-500 hover:text-slate-700">
          <ChevronLeft size={20} />
        </button>
        <div className="flex-1 flex items-start justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <h1 className="text-xl font-bold text-slate-900 num">{app.applicationNumber}</h1>
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
          {isLO35 && docsPending && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-sm font-semibold text-red-800 flex items-center gap-2"><AlertTriangle size={16}/> Disbursement blocked: 11 documentation items pending. Primary blocker: Borrower PAN / Aadhaar verification.</p>
            </div>
          )}
          {app.status === 'sanctioned' && !docsPending && sapMissing && (
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
        </div>

        {/* ── Tab 1: Completeness Check ── */}
        <div className="space-y-4">
          {isCompletenessReadOnly && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-sm text-blue-800 flex items-center gap-2">
              <Info size={16} /> Read-only — completeness was completed before appraisal.
            </div>
          )}

          <div className="card">
            <div className="flex items-center justify-between mb-3">
              <div>
                <h3 className="font-semibold text-slate-800 flex items-center gap-2">
                  <ClipboardList size={16} className="text-green-600" /> Application Completeness Check
                </h3>
                <p className="text-xs text-slate-500 mt-0.5">Performed by: Deputy Manager – Finance · {COMPLETENESS_ITEMS.length}/{COMPLETENESS_ITEMS.length} items reviewed</p>
              </div>
              <div className="flex items-center gap-3">
                <div className="text-right">
                  <p className="text-xs text-slate-400">Pass</p>
                  <p className="text-lg font-bold text-green-700">{COMPLETENESS_ITEMS.length}</p>
                </div>
                <div className="text-right">
                  <p className="text-xs text-slate-400">Deficiency</p>
                  <p className="text-lg font-bold text-red-600">0</p>
                </div>
              </div>
            </div>
            <div className="w-full bg-slate-100 rounded-full h-2">
              <div className="h-2 rounded-full transition-all bg-green-500 w-full" />
            </div>
          </div>

          {['Application Data', 'Borrower KYC', 'Nominee KYC', 'Shareholding', 'Land & Crop', 'Financial', 'Application Form', 'Other'].map(cat => {
            const items = COMPLETENESS_ITEMS.filter(i => i.category === cat);
            if (items.length === 0) return null;
            return (
              <div key={cat} className="card p-0 overflow-hidden">
                <div className="px-5 py-3 bg-slate-50 border-b border-slate-100">
                  <p className="text-xs font-semibold text-slate-600 uppercase tracking-wide">{cat}</p>
                </div>
                <div className="divide-y divide-slate-50">
                  {items.map(item => {
                    let displayLabel = item.label;
                    if (item.id === 'c06') displayLabel = app.shareMode === 'physical' ? 'Share certificate / folio evidence' : 'Demat holding evidence / folio reference';
                    const isNa = item.id === 'c13' && member?.memberType === 'individual';

                    return (
                      <div key={item.id} className="px-5 py-3">
                        <div className="flex items-center gap-3">
                          <div className="flex-1">
                            <div className="flex items-center gap-2">
                              <span className="text-sm font-medium text-slate-800">{displayLabel}</span>
                              {!item.required && <span className="text-xs text-slate-400 bg-slate-100 px-1.5 py-0.5 rounded">Optional</span>}
                            </div>
                          </div>
                          <div className="flex items-center gap-2 flex-shrink-0">
                            {isNa ? (
                              <span className="text-xs font-medium text-slate-500 bg-slate-100 px-2.5 py-1 rounded-lg">N/A</span>
                            ) : (
                              <StatusBadge label="Passed" size="sm" />
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

          <div className="card space-y-4">
            <h4 className="text-sm font-semibold text-slate-700">Completeness Check Note</h4>
            <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 text-sm text-slate-700">
              Completeness passed. Reference generated and application moved to appraisal.
            </div>
            
            <div className="border-t border-slate-100 pt-4 mt-4">
              <h4 className="text-sm font-semibold text-slate-700 mb-2">Deficiency History</h4>
              <p className="text-xs text-slate-500">No deficiencies recorded during completeness check.</p>
            </div>

            <div className="flex items-center gap-2 mt-4 pt-4 border-t border-slate-100">
              <span className="text-sm font-medium text-green-700 bg-green-50 px-4 py-2 rounded-lg flex items-center gap-2 border border-green-200">
                <CheckCircle2 size={16} /> Reference generated · {app.applicationNumber}
              </span>
            </div>
          </div>
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
              <StatusBadge label="Pending" size="sm" />
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
              {[
                { label: 'Full Name', value: 'Sudha Patil' },
                { label: 'Date of Birth', value: '15 March 1980' },
                { label: 'Age', value: '45 years' },
                { label: 'Gender', value: 'Female' },
                { label: 'Relationship to Borrower', value: 'Spouse' },
                { label: 'Mobile', value: '9900112233' },
                { label: 'Signature Status', value: 'Pending' },
                { label: 'PAN Document Status', value: 'Pending' },
                { label: 'Aadhaar Document Status', value: 'Uploaded' },
                { label: 'Address', value: 'Sr. No. 88, Igatpuri, Nashik' },
              ].map(({ label, value }) => (
                <div key={label} className="bg-slate-50 rounded-lg p-3">
                  <p className="text-xs text-slate-500 font-medium uppercase tracking-wide">{label}</p>
                  <p className={`text-sm font-semibold mt-0.5 ${value === 'Pending' ? 'text-amber-700' : 'text-slate-900'}`}>{value}</p>
                </div>
              ))}
            </div>
            <div className="border-t border-slate-100 pt-4 mt-2">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div className="flex items-center gap-3 bg-amber-50 border border-amber-100 rounded-lg p-3">
                  <div className="flex-1">
                    <p className="text-xs text-slate-500">Nominee PAN</p>
                    <p className="text-sm font-mono font-semibold text-slate-900">{nomineePanRevealed ? 'FGHIJ5678K' : '••••••••••'}</p>
                  </div>
                  <button onClick={() => handleReveal(setNomineePanRevealed, nomineePanRevealed, 'PAN')} className="text-xs text-amber-700 flex items-center gap-1 hover:underline">
                    {nomineePanRevealed ? <EyeOff size={12} /> : <Eye size={12} />} {nomineePanRevealed ? 'Hide' : 'Reveal'}
                  </button>
                </div>
                <div className="flex items-center gap-3 bg-amber-50 border border-amber-100 rounded-lg p-3">
                  <div className="flex-1">
                    <p className="text-xs text-slate-500">Nominee Aadhaar</p>
                    <p className="text-sm font-mono font-semibold text-slate-900">{nomineeAadhaarRevealed ? '778944447789' : '••••-••••-••••'}</p>
                  </div>
                  <button onClick={() => handleReveal(setNomineeAadhaarRevealed, nomineeAadhaarRevealed, 'Aadhaar')} className="text-xs text-amber-700 flex items-center gap-1 hover:underline">
                    {nomineeAadhaarRevealed ? <EyeOff size={12} /> : <Eye size={12} />} {nomineeAadhaarRevealed ? 'Hide' : 'Reveal'}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* ── Tab 4: Witness ── */}
        <div className="space-y-4">
          {[witnessData.w1, witnessData.w2].map((w, i) => (
            <div key={i} className="card space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="font-semibold text-slate-800 flex items-center gap-2">
                  <Users size={16} className="text-blue-600" /> Witness {i + 1}
                  {!w.required && <span className="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full ml-2">Optional / Not required</span>}
                </h3>
                {w.required && <StatusBadge label={w.signatureObtained ? 'signed' : 'pending'} size="sm" />}
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                {[
                  { label: 'Full Name', value: w.name },
                  { label: 'Witness Member / Folio', value: w.memberNumber },
                  { label: 'Shareholder Verification', value: w.shareholderVerification },
                  { label: 'Relationship', value: w.relation },
                  { label: 'PAN Document Status', value: w.panStatus },
                  { label: 'Aadhaar Document Status', value: w.aadhaarStatus },
                  { label: 'Signature Status', value: w.signatureObtained ? 'Signed' : 'Pending' },
                  { label: 'Signature Date', value: w.date ? new Date(w.date).toLocaleDateString('en-IN') : 'Pending' },
                ].map(({ label, value }) => (
                  <div key={label} className="bg-slate-50 rounded-lg p-3">
                    <p className="text-xs text-slate-500 font-medium uppercase tracking-wide">{label}</p>
                    <p className={`text-sm font-semibold mt-0.5 ${value === 'Pending' ? 'text-amber-700' : 'text-slate-900'}`}>{value}</p>
                  </div>
                ))}
              </div>
            </div>
          ))}
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
            {auditEvents.filter(e => e.entityId === applicationId || e.entityId === app.applicationNumber).map((ev, i) => (
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
