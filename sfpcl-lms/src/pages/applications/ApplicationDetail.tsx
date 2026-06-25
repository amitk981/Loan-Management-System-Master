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
import { loanApplications, members, securities, auditEvents } from '../../data/mockData';
import { useRole } from '../../contexts/RoleContext';

const fmt = (n: number) => '₹' + n.toLocaleString('en-IN');

const STAGE_MAP: Record<string, number> = {
  draft: 0, submitted: 0, incomplete: 0,
  reference_generated: 1, appraisal_pending: 2, credit_review: 2,
  pending_sanction: 3, sanctioned: 4, rejected_credit: 4, rejected_sanction: 4,
};

// ── S12: Completeness Checklist (13 items per spec) ────────────────────────
const COMPLETENESS_ITEMS = [
  { id: 'c01', category: 'Borrower KYC', label: 'PAN Card (Self-Attested)', required: true },
  { id: 'c02', category: 'Borrower KYC', label: 'Aadhaar Card (Self-Attested)', required: true },
  { id: 'c03', category: 'Borrower KYC', label: 'Recent Photograph', required: true },
  { id: 'c04', category: 'Nominee KYC', label: 'Nominee PAN Copy', required: true },
  { id: 'c05', category: 'Nominee KYC', label: 'Nominee Aadhaar Copy', required: true },
  { id: 'c06', category: 'Shareholding', label: 'Share Certificate / Folio Reference', required: true },
  { id: 'c07', category: 'Land & Crop', label: '7/12 Extract (current season)', required: true },
  { id: 'c08', category: 'Land & Crop', label: 'Crop Plan / Scale of Finance Evidence', required: true },
  { id: 'c09', category: 'Financial', label: '6-Month Bank Statement', required: true },
  { id: 'c10', category: 'Financial', label: 'Repayment Capacity Evidence', required: false },
  { id: 'c11', category: 'Application Form', label: 'Signed Application Form (all pages)', required: true },
  { id: 'c12', category: 'Application Form', label: 'Nominee Signature & Consent', required: true },
  { id: 'c13', category: 'Other', label: 'Board Resolution (FPC only)', required: false },
];

// ── S09: Witness data ─────────────────────────────────────────────────────
const witnessData = {
  w1: {
    name: 'Rajan Marathe', dob: '1975-05-10', age: 49, gender: 'Male',
    relation: 'Neighbour', mobile: '9821234567', address: 'Village Panchkund, Nashik, MH 422001',
    identityType: 'Aadhaar', identityNumber: '****-****-7321',
    signatureObtained: true, date: '2024-09-18',
  },
  w2: {
    name: 'Sunanda Patil', dob: '1968-11-22', age: 55, gender: 'Female',
    relation: 'Village member', mobile: '9922345678', address: 'Village Panchkund, Nashik, MH 422001',
    identityType: 'Aadhaar', identityNumber: '****-****-4490',
    signatureObtained: false, date: null,
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
  const app = loanApplications.find(a => a.id === applicationId) || loanApplications[0];
  const member = members.find(m => m.id === app.memberId);
  const appSecurities = securities.filter(s => s.applicationId === applicationId);
  const { can, currentUser } = useRole();

  const [activeTab, setActiveTab] = useState(0);
  const [panRevealed, setPanRevealed] = useState(false);
  const [aadhaarRevealed, setAadhaarRevealed] = useState(false);
  const [nomineeMinorWarning] = useState(false); // Would derive from nominee age

  // Completeness Check state
  const [completenessStatus, setCompletenessStatus] = useState<Record<string, 'pass' | 'deficiency' | 'na' | null>>(
    () => Object.fromEntries(COMPLETENESS_ITEMS.map(i => [i.id, null]))
  );
  const [deficiencyReasons, setDeficiencyReasons] = useState<Record<string, string>>({});
  const [completenessNote, setCompletenessNote] = useState('');
  const [referenceGenerated, setReferenceGenerated] = useState(
    ['reference_generated','appraisal_pending','credit_review','pending_sanction','sanctioned'].includes(app.status)
  );

  // Special Case state
  const [specialCaseAcknowledged, setSpecialCaseAcknowledged] = useState(false);

  const stageIndex = STAGE_MAP[app.status] ?? 0;
  type StepState = 'not_started' | 'in_progress' | 'completed' | 'blocked' | 'rejected' | 'exception';
  const stageState = (gt: boolean, eq: boolean): StepState => gt ? 'completed' : eq ? 'in_progress' : 'not_started';
  const stages = [
    { id: 's1', label: 'Submitted',    state: stageState(stageIndex > 0, stageIndex === 0) },
    { id: 's2', label: 'Reference',    state: stageState(stageIndex > 1, stageIndex === 1) },
    { id: 's3', label: 'Appraisal',    state: stageState(stageIndex > 2, stageIndex === 2) },
    { id: 's4', label: 'Sanction',     state: stageState(stageIndex > 3, stageIndex === 3) },
    { id: 's5', label: 'Documentation', state: (app.documentationStatus === 'complete' ? 'completed' : app.documentationStatus !== 'not_started' ? 'in_progress' : 'not_started') as StepState },
    { id: 's6', label: 'Disbursement', state: (app.disbursementStatus === 'completed' ? 'completed' : app.disbursementStatus !== 'pending_documentation' ? 'in_progress' : 'not_started') as StepState },
  ];

  const passCount = Object.values(completenessStatus).filter(s => s === 'pass').length;
  const defCount  = Object.values(completenessStatus).filter(s => s === 'deficiency').length;
  const totalRequired = COMPLETENESS_ITEMS.filter(i => i.required).length;
  const allRequiredPassed = COMPLETENESS_ITEMS.filter(i => i.required).every(i => completenessStatus[i.id] === 'pass' || completenessStatus[i.id] === 'na');

  const TABS = [
    { id: 'overview',      label: 'Overview' },
    { id: 'completeness',  label: 'Completeness Check', badge: defCount > 0 ? defCount : undefined },
    { id: 'applicant',     label: 'Applicant & Member' },
    { id: 'nominee',       label: 'Nominee' },
    { id: 'witness',       label: 'Witness' },
    { id: 'eligibility',   label: 'Eligibility & Limit' },
    { id: 'sanction',      label: 'Sanction & Approvals' },
    { id: 'documents',     label: 'Documents', badge: app.documentationStatus === 'in_progress' ? 1 : undefined },
    { id: 'security',      label: 'Security' },
    { id: 'disbursement',  label: 'Disbursement' },
    { id: 'audit',         label: 'Audit Trail' },
  ];

  // Compliance gate: check if disbursement is blocked
  const sapMissing = !app.sapCustomerCode;
  const docsPending = app.documentationStatus !== 'complete';

  return (
    <div className="p-6 space-y-4">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start gap-3">
          <button onClick={onBack} className="mt-1 text-slate-500 hover:text-slate-700">
            <ChevronLeft size={20} />
          </button>
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <h1 className="text-xl font-bold text-slate-900 num">{app.applicationNumber}</h1>
              <StatusBadge label={app.status} size="md" />
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
              <span>Applied {app.applicationDate}</span>
              {app.tatDaysRemaining !== undefined && app.tatDaysRemaining <= 1 && (
                <span className="flex items-center gap-1 text-amber-600 font-medium">
                  <Clock size={12} /> TAT: {app.tatDaysRemaining === 0 ? 'Overdue' : `${app.tatDaysRemaining}d`}
                </span>
              )}
            </div>
          </div>
        </div>
        <div className="flex flex-col items-end gap-1 text-sm text-slate-500">
          <span>Owner: <span className="font-medium text-slate-900">{app.currentOwner}</span></span>
          {app.sapCustomerCode && (
            <span>SAP: <span className="num font-medium text-slate-900">{app.sapCustomerCode}</span></span>
          )}
        </div>
      </div>

      {/* Compliance Gate Blockers */}
      {app.isException && app.exceptionReason && (
        <AlertBanner type="exception" title="Exception Case" message={app.exceptionReason} />
      )}
      {app.specialCase && !specialCaseAcknowledged && (
        <div className="flex items-start gap-3 bg-amber-50 border border-amber-300 rounded-xl p-4">
          <Shield size={18} className="text-amber-600 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="text-sm font-semibold text-amber-800">Special Case — Director / Relative / Committee Member</p>
            <p className="text-xs text-amber-700 mt-1">
              This borrower is a Director, Relative of Director, or Audit Committee Member. Full Sanction Committee quorum required.
              Conflict of interest must be declared. GM approval required if 2 directors unavailable.
            </p>
          </div>
          <button onClick={() => setSpecialCaseAcknowledged(true)}
            className="text-xs bg-amber-600 hover:bg-amber-700 text-white px-3 py-1.5 rounded-lg flex-shrink-0">
            Acknowledge
          </button>
        </div>
      )}
      {sapMissing && stageIndex >= 4 && (
        <AlertBanner type="warning" title="SAP Customer Code Missing — Disbursement Blocked"
          message="SM Finance must assign a SAP Customer Code before disbursement can be initiated. Go to Disbursement Hub → SAP Code Request." />
      )}
      {docsPending && stageIndex >= 3 && (
        <AlertBanner type="warning" title="Documentation Incomplete — Disbursement Blocked"
          message="All required documents must be collected, stamped, and notarised before disbursement." />
      )}
      {member?.kycStatus !== 'verified' && (
        <AlertBanner type="warning" title="KYC Not Verified"
          message={`Member KYC status is '${member?.kycStatus?.replace(/_/g, ' ')}'. No new loan can be sanctioned until KYC is verified.`} />
      )}
      {member?.activeStatus !== 'active' && (
        <AlertBanner type="error" title="Member Not Active"
          message="Member does not meet active member criteria (4-year supply rule). Loan is blocked." />
      )}

      {/* Stage stepper */}
      <div className="card py-5">
        <StageStepper steps={stages} />
      </div>

      {/* Tabs */}
      <Tabs tabs={TABS} activeIndex={activeTab} onChange={setActiveTab}>

        {/* ── Tab 0: Overview ── */}
        <div className="card space-y-5">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            {[
              { label: 'Requested Amount', value: fmt(app.requestedAmount) },
              { label: 'Eligible Amount', value: fmt(app.eligibleAmount) },
              { label: 'Loan Type', value: app.loanType === 'short_term' ? 'Short Term' : 'Long Term' },
              { label: 'Tenure', value: `${app.tenure} months` },
              { label: 'Purpose', value: app.purpose.replace(/_/g, ' ') },
              { label: 'Land Area', value: `${app.landAreaAcres} acres` },
              { label: 'Shares Held', value: `${app.sharesHeld} (${app.shareMode})` },
              { label: 'Risk Rating', value: app.riskRating || '—' },
            ].map(({ label, value }) => (
              <div key={label} className="bg-slate-50 rounded-lg p-3">
                <p className="text-xs text-slate-500 font-medium uppercase tracking-wide">{label}</p>
                <p className="text-sm font-semibold text-slate-900 mt-0.5 capitalize">{value}</p>
              </div>
            ))}
          </div>
          {app.sanctionDecision === 'approved' && app.sanctionedAt && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-sm text-green-800">
              <p className="font-semibold">Sanctioned on {new Date(app.sanctionedAt).toLocaleDateString('en-IN')}</p>
              {app.disbursedAmount && <p className="mt-0.5">Disbursed: {fmt(app.disbursedAmount)} on {app.disbursedAt ? new Date(app.disbursedAt).toLocaleDateString('en-IN') : '—'}</p>}
            </div>
          )}
        </div>

        {/* ── Tab 1: Completeness Check (S12) ── */}
        <div className="space-y-4">
          {/* Progress bar */}
          <div className="card">
            <div className="flex items-center justify-between mb-3">
              <div>
                <h3 className="font-semibold text-slate-800 flex items-center gap-2">
                  <ClipboardList size={16} className="text-green-600" /> Application Completeness Check
                </h3>
                <p className="text-xs text-slate-500 mt-0.5">Performed by: Deputy Manager – Finance · {passCount}/{COMPLETENESS_ITEMS.length} items reviewed</p>
              </div>
              <div className="flex items-center gap-3">
                <div className="text-right">
                  <p className="text-xs text-slate-400">Pass</p>
                  <p className="text-lg font-bold text-green-700">{passCount}</p>
                </div>
                <div className="text-right">
                  <p className="text-xs text-slate-400">Deficiency</p>
                  <p className="text-lg font-bold text-red-600">{defCount}</p>
                </div>
              </div>
            </div>
            <div className="w-full bg-slate-100 rounded-full h-2">
              <div
                className={`h-2 rounded-full transition-all ${defCount > 0 ? 'bg-red-500' : 'bg-green-500'}`}
                style={{ width: `${(passCount / COMPLETENESS_ITEMS.length) * 100}%` }}
              />
            </div>
          </div>

          {/* Checklist grouped by category */}
          {['Borrower KYC', 'Nominee KYC', 'Shareholding', 'Land & Crop', 'Financial', 'Application Form', 'Other'].map(cat => {
            const items = COMPLETENESS_ITEMS.filter(i => i.category === cat);
            return (
              <div key={cat} className="card p-0 overflow-hidden">
                <div className="px-5 py-3 bg-slate-50 border-b border-slate-100">
                  <p className="text-xs font-semibold text-slate-600 uppercase tracking-wide">{cat}</p>
                </div>
                <div className="divide-y divide-slate-50">
                  {items.map(item => {
                    const status = completenessStatus[item.id];
                    return (
                      <div key={item.id} className={`px-5 py-3 ${status === 'deficiency' ? 'bg-red-50' : ''}`}>
                        <div className="flex items-center gap-3">
                          <div className="flex-1">
                            <div className="flex items-center gap-2">
                              <span className="text-sm font-medium text-slate-800">{item.label}</span>
                              {!item.required && <span className="text-xs text-slate-400 bg-slate-100 px-1.5 py-0.5 rounded">Optional</span>}
                            </div>
                            {status === 'deficiency' && (
                              <input
                                type="text"
                                placeholder="Describe deficiency (required)…"
                                value={deficiencyReasons[item.id] || ''}
                                onChange={e => setDeficiencyReasons(p => ({ ...p, [item.id]: e.target.value }))}
                                className="mt-2 w-full text-xs border border-red-200 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-1 focus:ring-red-400 bg-white"
                              />
                            )}
                          </div>
                          <div className="flex items-center gap-2 flex-shrink-0">
                            <button
                              onClick={() => setCompletenessStatus(p => ({ ...p, [item.id]: 'pass' }))}
                              className={`flex items-center gap-1 text-xs px-2.5 py-1.5 rounded-lg font-medium transition-colors ${
                                status === 'pass' ? 'bg-green-600 text-white' : 'bg-slate-100 text-slate-500 hover:bg-green-50 hover:text-green-700'
                              }`}
                            >
                              <CheckCircle2 size={12} /> Pass
                            </button>
                            <button
                              onClick={() => setCompletenessStatus(p => ({ ...p, [item.id]: 'deficiency' }))}
                              className={`flex items-center gap-1 text-xs px-2.5 py-1.5 rounded-lg font-medium transition-colors ${
                                status === 'deficiency' ? 'bg-red-600 text-white' : 'bg-slate-100 text-slate-500 hover:bg-red-50 hover:text-red-700'
                              }`}
                            >
                              <XCircle size={12} /> Deficiency
                            </button>
                            {!item.required && (
                              <button
                                onClick={() => setCompletenessStatus(p => ({ ...p, [item.id]: 'na' }))}
                                className={`flex items-center gap-1 text-xs px-2.5 py-1.5 rounded-lg font-medium transition-colors ${
                                  status === 'na' ? 'bg-slate-500 text-white' : 'bg-slate-100 text-slate-500 hover:bg-slate-200'
                                }`}
                              >
                                N/A
                              </button>
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

          {/* Overall Note + Action */}
          <div className="card space-y-4">
            <h4 className="text-sm font-semibold text-slate-700">Completeness Check Note</h4>
            <textarea
              rows={3}
              placeholder="Add notes about overall completeness, missing items, or instructions to the borrower…"
              value={completenessNote}
              onChange={e => setCompletenessNote(e.target.value)}
              className="w-full field-input text-sm resize-none"
            />
            {defCount > 0 && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-sm font-semibold text-red-800 mb-2 flex items-center gap-2">
                  <AlertTriangle size={14} /> Deficiency Summary ({defCount} item{defCount > 1 ? 's' : ''})
                </p>
                <div className="space-y-1">
                  {COMPLETENESS_ITEMS.filter(i => completenessStatus[i.id] === 'deficiency').map(item => (
                    <div key={item.id} className="flex items-start gap-2 text-xs text-red-700">
                      <span className="font-medium">•</span>
                      <span>{item.label}{deficiencyReasons[item.id] ? `: ${deficiencyReasons[item.id]}` : ' — reason required'}</span>
                    </div>
                  ))}
                </div>
                <p className="text-xs text-red-600 mt-2 font-medium">Application will be returned to borrower as Incomplete.</p>
              </div>
            )}
            <div className="flex gap-3">
              {defCount > 0 ? (
                <button className="flex items-center gap-2 btn-danger text-sm px-4 py-2">
                  <XCircle size={14} /> Return as Incomplete
                </button>
              ) : (
                <button
                  disabled={!allRequiredPassed || referenceGenerated}
                  onClick={() => setReferenceGenerated(true)}
                  className={`flex items-center gap-2 text-sm px-4 py-2 rounded-lg font-medium transition-colors ${
                    allRequiredPassed && !referenceGenerated
                      ? 'bg-green-600 hover:bg-green-700 text-white'
                      : 'bg-slate-100 text-slate-400 cursor-not-allowed'
                  }`}
                >
                  <CheckCircle2 size={14} />
                  {referenceGenerated ? 'Reference Generated ✓' : 'Complete Check & Generate Reference'}
                </button>
              )}
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

              {/* Active member status */}
              <div className={`flex items-center gap-3 px-4 py-3 rounded-xl border ${
                member.activeStatus === 'active' ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'
              }`}>
                {member.activeStatus === 'active'
                  ? <CheckCircle2 size={16} className="text-green-600 flex-shrink-0" />
                  : <XCircle size={16} className="text-red-600 flex-shrink-0" />}
                <div>
                  <p className={`text-sm font-semibold ${member.activeStatus === 'active' ? 'text-green-800' : 'text-red-800'}`}>
                    {member.activeStatus === 'active' ? 'Active Member ✓' : 'Inactive Member — Loan Blocked'}
                  </p>
                  <p className={`text-xs ${member.activeStatus === 'active' ? 'text-green-600' : 'text-red-600'}`}>
                    {member.supplyYears >= 4
                      ? `${member.supplyYears} years supply on record — meets 4-year rule`
                      : `${member.supplyYears} year(s) supply — does not meet 4-year rule`}
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

              {/* Masked sensitive identifiers */}
              <div className="border-t border-slate-100 pt-4">
                <p className="text-xs text-slate-500 font-semibold uppercase tracking-wide mb-3 flex items-center gap-1">
                  <Lock size={12} /> Sensitive Identifiers — Masked
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div className="flex items-center gap-3 bg-amber-50 border border-amber-100 rounded-lg p-3">
                    <div className="flex-1">
                      <p className="text-xs text-slate-500">PAN</p>
                      <p className="text-sm font-mono font-semibold text-slate-900">{panRevealed ? member.pan : '**-***-****'}</p>
                    </div>
                    <button onClick={() => setPanRevealed(!panRevealed)} className="text-xs text-amber-700 flex items-center gap-1 hover:underline">
                      {panRevealed ? <EyeOff size={12} /> : <Eye size={12} />} {panRevealed ? 'Hide' : 'Reveal'}
                    </button>
                  </div>
                  <div className="flex items-center gap-3 bg-amber-50 border border-amber-100 rounded-lg p-3">
                    <div className="flex-1">
                      <p className="text-xs text-slate-500">Aadhaar</p>
                      <p className="text-sm font-mono font-semibold text-slate-900">{aadhaarRevealed ? member.aadhaar : '****-****-****'}</p>
                    </div>
                    <button onClick={() => setAadhaarRevealed(!aadhaarRevealed)} className="text-xs text-amber-700 flex items-center gap-1 hover:underline">
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

        {/* ── Tab 3: Nominee (S08) ── */}
        <div className="space-y-4">
          <div className="card space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold text-slate-800 flex items-center gap-2">
                <User size={16} className="text-green-600" /> Nominee Details
              </h3>
              <StatusBadge label="obtained" size="sm" />
            </div>

            {/* Minor-age guard */}
            {nomineeMinorWarning && (
              <div className="flex items-start gap-3 bg-red-50 border border-red-300 rounded-xl p-4">
                <AlertTriangle size={16} className="text-red-600 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-sm font-semibold text-red-800">Nominee is a Minor — Application Blocked</p>
                  <p className="text-xs text-red-700 mt-0.5">
                    The nominee must be an adult (18+). Please update the nominee before proceeding.
                    An alternative nominee or guardian details must be provided per SOP.
                  </p>
                </div>
              </div>
            )}

            <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
              {[
                { label: 'Full Name', value: 'Sudha Patil' },
                { label: 'Date of Birth', value: '15 March 1980' },
                { label: 'Age', value: '45 years' },
                { label: 'Gender', value: 'Female' },
                { label: 'Relationship to Borrower', value: 'Spouse' },
                { label: 'Mobile', value: '9900112233' },
                { label: 'PAN', value: 'BCDEF2345G' },
                { label: 'Aadhaar', value: '****-****-8812' },
                { label: 'Signature Obtained', value: 'Yes' },
              ].map(({ label, value }) => (
                <div key={label} className="bg-slate-50 rounded-lg p-3">
                  <p className="text-xs text-slate-500 font-medium uppercase tracking-wide">{label}</p>
                  <p className="text-sm font-semibold text-slate-900 mt-0.5">{value}</p>
                </div>
              ))}
            </div>

            <div className="border-t border-slate-100 pt-4">
              <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-3">KYC Documents</h4>
              <div className="flex gap-3 flex-wrap">
                {[
                  { label: 'PAN Copy', status: 'verified' },
                  { label: 'Aadhaar Copy', status: 'verified' },
                  { label: 'Photograph', status: 'pending_upload' },
                ].map((doc, i) => (
                  <div key={i} className="flex items-center gap-2 bg-slate-50 border border-slate-100 rounded-lg px-3 py-2">
                    <FileText size={13} className="text-slate-400" />
                    <span className="text-xs font-medium text-slate-700">{doc.label}</span>
                    <StatusBadge label={doc.status} size="sm" />
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* ── Tab 4: Witness (S09) ── */}
        <div className="space-y-4">
          {[witnessData.w1, witnessData.w2].map((w, i) => (
            <div key={i} className="card space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="font-semibold text-slate-800 flex items-center gap-2">
                  <Users size={16} className="text-blue-600" /> Witness {i + 1}
                </h3>
                <StatusBadge label={w.signatureObtained ? 'signed' : 'pending'} size="sm" />
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
                {[
                  { label: 'Full Name', value: w.name },
                  { label: 'Date of Birth', value: new Date(w.dob).toLocaleDateString('en-IN') },
                  { label: 'Age', value: `${w.age} years` },
                  { label: 'Gender', value: w.gender },
                  { label: 'Relationship', value: w.relation },
                  { label: 'Mobile', value: w.mobile },
                  { label: 'Identity Type', value: w.identityType },
                  { label: 'Identity Number', value: w.identityNumber },
                  { label: 'Signature Date', value: w.date ? new Date(w.date).toLocaleDateString('en-IN') : 'Pending' },
                ].map(({ label, value }) => (
                  <div key={label} className="bg-slate-50 rounded-lg p-3">
                    <p className="text-xs text-slate-500 font-medium uppercase tracking-wide">{label}</p>
                    <p className="text-sm font-semibold text-slate-900 mt-0.5">{value}</p>
                  </div>
                ))}
              </div>
              <div>
                <p className="text-xs text-slate-500 font-medium uppercase tracking-wide mb-1">Address</p>
                <p className="text-sm text-slate-800">{w.address}</p>
              </div>
              {!w.signatureObtained && (
                <div className="flex items-center gap-2 bg-amber-50 border border-amber-200 rounded-lg p-3 text-amber-700">
                  <AlertTriangle size={14} className="flex-shrink-0" />
                  <p className="text-xs font-medium">Witness signature not yet obtained. Required before documentation can be finalised.</p>
                </div>
              )}
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
            <h3 className="text-sm font-semibold text-slate-700 mb-4">Eligibility Checklist</h3>
            <EligibilityChecklist memberId={app.memberId} applicationId={applicationId} />
          </div>
        </div>

        {/* ── Tab 6: Sanction & Approvals (with Special Case panel) ── */}
        <div className="space-y-4">
          {/* Special Case panel (S24) */}
          {app.specialCase && (
            <div className="card border-l-4 border-l-amber-400">
              <div className="flex items-start gap-3">
                <Shield size={18} className="text-amber-600 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <h4 className="font-semibold text-slate-800 mb-2">Special Case Approval Requirements (S24)</h4>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm mb-4">
                    {[
                      { label: 'Special Case Type', value: 'Director / Relative / Committee Member' },
                      { label: 'Minimum Quorum', value: 'Full Sanction Committee' },
                      { label: 'Conflict Declaration', value: 'Required — before voting' },
                      { label: 'GM Approval', value: 'Required if 2 Directors unavailable' },
                    ].map(({ label, value }) => (
                      <div key={label} className="bg-amber-50 rounded-lg p-3">
                        <p className="text-xs text-slate-500">{label}</p>
                        <p className="text-sm font-semibold text-amber-800">{value}</p>
                      </div>
                    ))}
                  </div>
                  <div className="space-y-2">
                    <label className="flex items-center gap-2 text-sm text-slate-700 cursor-pointer">
                      <input type="checkbox" className="w-4 h-4 accent-amber-600" />
                      Conflict of interest declared by relevant committee member
                    </label>
                    <label className="flex items-center gap-2 text-sm text-slate-700 cursor-pointer">
                      <input type="checkbox" className="w-4 h-4 accent-amber-600" />
                      Full quorum present (3 of 3 approvers)
                    </label>
                    <label className="flex items-center gap-2 text-sm text-slate-700 cursor-pointer">
                      <input type="checkbox" className="w-4 h-4 accent-amber-600" />
                      GM approval obtained (if applicable)
                    </label>
                  </div>
                </div>
              </div>
            </div>
          )}
          <div className="card">
            <h3 className="text-sm font-semibold text-slate-700 mb-4">Sanction Committee Approval</h3>
            <ApprovalPanel
              applicationNumber={app.applicationNumber}
              requestedAmount={app.requestedAmount}
              isException={app.isException}
              isSpecialCase={app.specialCase}
              approvers={[
                { role: 'CFO', name: 'Suresh Nair', decision: app.sanctionDecision === 'approved' ? 'approved' : 'pending', timestamp: app.sanctionedAt ? new Date(app.sanctionedAt).toLocaleDateString('en-IN') : undefined },
                { role: 'Director 1', name: 'Anita Desai', decision: app.sanctionDecision === 'approved' ? 'approved' : 'pending' },
                ...(app.requestedAmount > 500000 ? [{ role: 'Director 2', name: 'Prakash Joshi', decision: 'pending' as const }] : []),
              ]}
            />
          </div>
        </div>

        {/* ── Tab 7: Documents ── */}
        <div className="card">
          <h3 className="text-sm font-semibold text-slate-700 mb-4">Document Checklist</h3>
          <DocumentChecklist applicationId={applicationId} />
        </div>

        {/* ── Tab 8: Security ── */}
        <div className="card">
          <h3 className="text-sm font-semibold text-slate-700 mb-4">Security Instruments</h3>
          {appSecurities.length === 0 ? (
            <p className="text-slate-400 text-sm">No security instruments recorded yet.</p>
          ) : (
            <div className="space-y-3">
              {appSecurities.map(sec => (
                <div key={sec.id} className="flex items-center gap-4 p-3 bg-slate-50 rounded-lg border border-slate-200">
                  <div className="flex-1">
                    <div className="font-semibold text-slate-900 text-sm capitalize">{sec.securityType.replace('_', ' ')}</div>
                    <div className="text-xs text-slate-500 mt-0.5">
                      {sec.executionDate ? `Executed: ${sec.executionDate}` : 'Not yet executed'}
                      {sec.custodian && ` · Custodian: ${sec.custodian}`}
                      {sec.psnNumber && ` · PSN: ${sec.psnNumber}`}
                    </div>
                    {sec.stampDutyStatus && sec.stampDutyStatus !== 'not_required' && (
                      <div className="text-xs text-slate-400 mt-0.5">
                        Stamp Duty: <span className={sec.stampDutyStatus === 'complete' ? 'text-green-600 font-medium' : 'text-amber-600 font-medium'}>{sec.stampDutyStatus}</span>
                        {sec.notarisationStatus && sec.notarisationStatus !== 'not_required' && ` · Notarisation: ${sec.notarisationStatus}`}
                      </div>
                    )}
                  </div>
                  <StatusBadge label={sec.status} size="sm" />
                </div>
              ))}
            </div>
          )}
        </div>

        {/* ── Tab 9: Disbursement ── */}
        <div className="card space-y-4">
          <h3 className="text-sm font-semibold text-slate-700">Disbursement Details</h3>
          {sapMissing && <AlertBanner type="warning" title="SAP Customer Code not assigned" message="SM Finance must assign a SAP Customer Code. Request via Disbursement Hub." />}
          {docsPending && <AlertBanner type="warning" title="Documentation incomplete" message="All documents must be complete before disbursement." />}
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
            {[
              { label: 'Disbursement Status', value: app.disbursementStatus.replace(/_/g, ' ') },
              { label: 'SAP Customer Code', value: app.sapCustomerCode || '⚠ Pending assignment' },
              { label: 'Bank Account', value: app.bankAccount || '—' },
              { label: 'Bank IFSC', value: app.bankIfsc || '—' },
              { label: 'Disbursed Amount', value: app.disbursedAmount ? fmt(app.disbursedAmount) : '—' },
              { label: 'Disbursed On', value: app.disbursedAt ? new Date(app.disbursedAt).toLocaleDateString('en-IN') : '—' },
            ].map(({ label, value }) => (
              <div key={label} className="bg-slate-50 rounded-lg p-3">
                <p className="text-xs text-slate-500 font-medium uppercase tracking-wide">{label}</p>
                <p className={`text-sm font-semibold mt-0.5 ${value.includes('⚠') ? 'text-amber-700' : 'text-slate-900'}`}>{value}</p>
              </div>
            ))}
          </div>
          {/* Disbursement Advice (S41) */}
          {app.disbursedAmount && (
            <div className="border border-green-200 rounded-xl bg-green-50 p-4 flex items-center gap-4">
              <div className="w-10 h-10 rounded-lg bg-green-100 flex items-center justify-center flex-shrink-0">
                <Banknote size={18} className="text-green-700" />
              </div>
              <div className="flex-1">
                <p className="text-sm font-semibold text-green-800">Disbursement Advice</p>
                <p className="text-xs text-green-600">
                  {fmt(app.disbursedAmount)} disbursed on {app.disbursedAt ? new Date(app.disbursedAt).toLocaleDateString('en-IN') : '—'} · Bank: {app.bankAccount} {app.bankIfsc}
                </p>
              </div>
              <button className="flex items-center gap-1 text-xs bg-green-600 hover:bg-green-700 text-white px-3 py-1.5 rounded-lg">
                <Download size={12} /> Download Advice
              </button>
            </div>
          )}
        </div>

        {/* ── Tab 10: Audit Trail (with before/after values) ── */}
        <div className="card p-0 overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
            <h3 className="font-semibold text-slate-800">Application Audit Trail</h3>
            <button className="flex items-center gap-1 text-xs text-green-700 hover:underline">
              <Download size={12} /> Export
            </button>
          </div>
          {/* Enhanced audit with before/after */}
          <div className="divide-y divide-slate-50">
            {auditEvents.filter(e => e.entityId === applicationId || true).map((ev, i) => (
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
