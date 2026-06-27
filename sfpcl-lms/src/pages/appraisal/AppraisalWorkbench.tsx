import React, { useState, useEffect } from 'react';
import {
  Scale, ChevronRight, FileText, Check, CheckCircle2, XCircle,
  AlertTriangle, Clock, BarChart2,
  ArrowRight, Info, Lock, Leaf, BadgeCheck, FileDown, Save,
  Send, RotateCcw, Download, Wheat
} from 'lucide-react';
import StatusBadge from '../../components/ui/StatusBadge';
import AlertBanner from '../../components/ui/AlertBanner';
import LoanLimitCalculator from '../../components/loan/LoanLimitCalculator';
import EligibilityChecklist from '../../components/loan/EligibilityChecklist';
import { loanApplications as mockApplications, members } from '../../data/mockData';
import type { LoanApplication } from '../../types';
import { useRole } from '../../contexts/RoleContext';

const fmt = (n: number) => '₹' + n.toLocaleString('en-IN');

const FLOATING_RATE = '12.5% p.a. (floating — board-approved rate)';

const downloadJson = (filename: string, data: object) => {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
};

const TatChip: React.FC<{ daysRemaining: number | undefined; referenceGeneratedAt?: string }> = ({ daysRemaining, referenceGeneratedAt }) => {
  if (!referenceGeneratedAt) return <span className="text-xs text-slate-400">TAT not started</span>;
  if (daysRemaining === undefined) return null;
  if (daysRemaining <= 0) return (
    <span className="inline-flex items-center gap-1 text-xs font-semibold bg-red-100 text-red-700 px-2 py-0.5 rounded-full">
      <Clock size={10} /> TAT Breach
    </span>
  );
  if (daysRemaining === 1) return (
    <span className="inline-flex items-center gap-1 text-xs font-semibold bg-amber-100 text-amber-700 px-2 py-0.5 rounded-full">
      <Clock size={10} /> 1 day left
    </span>
  );
  return (
    <span className="inline-flex items-center gap-1 text-xs font-semibold bg-green-100 text-green-700 px-2 py-0.5 rounded-full">
      <Clock size={10} /> {daysRemaining}d left
    </span>
  );
};

const formatBadge = (status: string) => {
  if (status === 'reference_generated') return 'Verification pending';
  if (status === 'appraisal_in_progress') return 'Application Complete / Appraisal In Progress';
  if (status === 'appraisal_pending') return 'Appraisal draft pending';
  if (status === 'pending_credit_manager_review' || status === 'credit_review') return 'Pending Credit Manager Review';
  return status.replace(/_/g, ' ');
};

const RISK_RATINGS = ['low', 'medium', 'high', 'very_high'] as const;

interface AppraisalWorkbenchProps {
  onOpenApplication: (id: string) => void;
  initialSelectedId?: string;
  applications?: LoanApplication[];
  onUpdateStatus?: (id: string, newStatus: string) => void;
}

const AppraisalWorkbench: React.FC<AppraisalWorkbenchProps> = ({ onOpenApplication, initialSelectedId, applications, onUpdateStatus }) => {
  const loanApplications = applications ?? mockApplications;
  const appraisalQueue = loanApplications.filter(a =>
    ['reference_generated', 'appraisal_in_progress', 'appraisal_pending', 'pending_credit_manager_review', 'credit_review'].includes(a.status)
  );
  const initialApp = initialSelectedId ? appraisalQueue.find(a =>
    a.id === initialSelectedId ||
    a.applicationNumber === initialSelectedId ||
    a.intakeReference === initialSelectedId ||
    a.officialReference === initialSelectedId
  ) : appraisalQueue[0];
  const [selected, setSelected] = useState<string | null>(initialApp?.id || null);
  const [noteText, setNoteText] = useState('');
  const [riskRating, setRiskRating] = useState<typeof RISK_RATINGS[number]>(initialApp?.isException ? 'high' : 'low');

  const [appraisalStep, setAppraisalStep] = useState<'verification' | 'appraisal' | 'submitted'>(
    initialApp?.status === 'reference_generated' ? 'verification' :
    (initialApp?.status === 'appraisal_in_progress' || initialApp?.status === 'appraisal_pending') ? 'appraisal' : 'submitted'
  );
  const [recommendedAmount, setRecommendedAmount] = useState('');
  const [recommendedTenure, setRecommendedTenure] = useState('12');
  const [securityProposed, setSecurityProposed] = useState('SH-4 physical share transfer form, PoA, blank-dated cheque');
  const [bankObservation, setBankObservation] = useState('');
  const [riskRationale, setRiskRationale] = useState('');
  const [conditionsPrecedent, setConditionsPrecedent] = useState('');
  const [recommendation, setRecommendation] = useState<'approve' | 'approve_conditions' | 'exception' | 'reject'>('approve');
  const [creditManagerComment, setCreditManagerComment] = useState('');
  const [appraisalDraftSaved, setAppraisalDraftSaved] = useState(false);
  const [decisionStatus, setDecisionStatus] = useState<null | 'forwarded' | 'returned' | 'rejected' | 'documents_requested'>(null);

  // New state for ledger fixes
  const [eligibilityComplete, setEligibilityComplete] = useState(false);
  const [cropObservation, setCropObservation] = useState('');
  const [showExceptionConfirm, setShowExceptionConfirm] = useState(false);
  const [exceptionRegistered, setExceptionRegistered] = useState(false);
  const [pdfDownloaded, setPdfDownloaded] = useState(false);

  const { currentUser, can } = useRole();

  // S16 Active Member Verification
  const [activeMemberVerified, setActiveMemberVerified] = useState(initialApp?.status !== 'reference_generated');
  const [activeMemberRelaxationRecorded, setActiveMemberRelaxationRecorded] = useState(false);
  const [activeMemberNote, setActiveMemberNote] = useState('');

  // S17 KYC Verification
  const [kycVerified, setKycVerified] = useState(initialApp?.status !== 'reference_generated' || members.find(m => m.id === initialApp?.memberId)?.kycStatus === 'verified');
  const [kycNote, setKycNote] = useState('');

  // Credit risk score
  const [creditScoreVerified, setCreditScoreVerified] = useState(false);
  const [creditScore, setCreditScore] = useState('');

  const app = appraisalQueue.find(a => a.id === selected);
  const member = app ? members.find(m => m.id === app.memberId) : null;

  // Auto-select first queue item when sidebar is clicked with no pre-selected app
  useEffect(() => {
    if (!selected && appraisalQueue.length > 0) {
      const first = appraisalQueue[0];
      setSelected(first.id);
      setAppraisalStep(
        first.status === 'reference_generated' ? 'verification' :
        (first.status === 'appraisal_in_progress' || first.status === 'appraisal_pending') ? 'appraisal' : 'submitted'
      );
    }
  }, []);

  useEffect(() => {
    setDecisionStatus(null);
    setShowExceptionConfirm(false);
    setExceptionRegistered(false);
    setPdfDownloaded(false);
    if (app?.status === 'pending_credit_manager_review' || app?.status === 'credit_review') {
      setRecommendedAmount(String(app.requestedAmount));
      setRecommendation(app.isException ? 'exception' : 'approve');
      setRiskRationale('High risk due to requested amount exceeding eligible limit. Member has strong repayment history and adequate subsidiary income to service the loan.');
      setBankObservation('6-month statement shows regular dairy receipts averaging ₹45,000/month. No bounce history.');
      setNoteText('Appraisal note summary:\n- Member seeks ₹3.5L for crop production.\n- Eligible limit is ₹64k based on 3.2 acres.\n- Exception recommended based on strong dairy income.');
    }
  }, [app?.id]);

  const isDMFinance = currentUser.role === 'deputy_manager_finance';
  const isCreditManager = currentUser.role === 'credit_manager';

  const allowedToPrepareAppraisal = can('do_appraisal') && !['admin', 'auditor', 'cfo', 'director', 'cfc', 'accounts', 'sales_team_user', 'sanction_committee'].includes(currentUser.role);
  const isAdmin = currentUser.role === 'admin';
  const canProceedToAppraisal = isAdmin || (activeMemberVerified && kycVerified && allowedToPrepareAppraisal);
  const recommendedAmountNumber = Number(recommendedAmount || 0);
  const recommendedWithinLimit = app ? recommendedAmountNumber > 0 && recommendedAmountNumber <= app.eligibleAmount : false;
  const requiresException = app?.isException || recommendation === 'exception' || (recommendedAmountNumber > 0 && app ? recommendedAmountNumber > app.eligibleAmount : false);
  const canForwardToSanction = isAdmin || (noteText.trim().length > 10 &&
    riskRating &&
    riskRationale.trim().length > 5 &&
    bankObservation.trim().length > 5 &&
    securityProposed.trim().length > 5 &&
    recommendedAmountNumber > 0 &&
    cropObservation.trim().length > 5 &&
    (recommendedWithinLimit || requiresException));

  const handleRecordRelaxation = () => {
    if (can('approve_sanction')) {
      setActiveMemberVerified(true);
    } else {
      setActiveMemberRelaxationRecorded(true);
    }
  };

  const handleGeneratePdf = () => {
    if (!app) return;
    const data = {
      appraisalSnapshot: {
        applicationNumber: app.applicationNumber,
        memberName: app.memberName,
        memberType: app.memberType,
        requestedAmount: app.requestedAmount,
        eligibleAmount: app.eligibleAmount,
        recommendedAmount: recommendedAmountNumber,
        recommendedTenure: `${recommendedTenure} months`,
        interestRate: FLOATING_RATE,
        riskRating,
        riskRationale,
        bankObservation,
        cropObservation,
        securityProposed,
        conditionsPrecedent,
        recommendation,
        requiresException,
        noteText,
        generatedAt: new Date().toISOString(),
        generatedBy: currentUser.name,
      },
    };
    downloadJson(`appraisal-${app.applicationNumber}-${Date.now()}.json`, data);
    setPdfDownloaded(true);
    setAppraisalDraftSaved(true);
  };

  const handleForwardToSanction = () => {
    if (!app) return;
    console.log({ action: 'FORWARDED', actor: currentUser.role, time: new Date().toISOString(), reason: creditManagerComment, app: app.id, exception: requiresException });
    if (requiresException && !exceptionRegistered) {
      setShowExceptionConfirm(true);
      return;
    }
    setDecisionStatus('forwarded');
    onUpdateStatus?.(app.id, 'pending_sanction_committee_approval');
  };

  const handleConfirmException = () => {
    if (!app) return;
    console.log({ action: 'EXCEPTION_REGISTERED', app: app.id, reason: creditManagerComment, time: new Date().toISOString() });
    setExceptionRegistered(true);
    setShowExceptionConfirm(false);
    setDecisionStatus('forwarded');
    onUpdateStatus?.(app.id, 'pending_sanction_committee_approval');
  };

  const handleReject = () => {
    if (!app) return;
    const rejectionNote = {
      rejectionNote: {
        applicationReference: app.applicationNumber,
        borrowerName: app.memberName,
        rejectionStage: 'Credit Assessment',
        rejectionReason: creditManagerComment,
        correctiveAction: 'Applicant may reapply after rectifying the flagged issues.',
        date: new Date().toISOString(),
        rejectedBy: currentUser.name,
      },
    };
    console.log({ action: 'REJECTED', actor: currentUser.role, time: new Date().toISOString(), reason: creditManagerComment, app: app.id });
    downloadJson(`rejection-note-${app.applicationNumber}-${Date.now()}.json`, rejectionNote);
    setDecisionStatus('rejected');
    onUpdateStatus?.(app.id, 'rejected_by_credit_manager');
  };

  const workflowSteps = [
    {
      step: 'verification' as const,
      label: 'Step 1',
      title: 'Verify',
      owner: 'DM Finance',
      description: activeMemberVerified && kycVerified ? 'Active member and KYC verified' : 'Complete active member and KYC checks',
      state: (activeMemberVerified && kycVerified) || isAdmin ? 'complete' : appraisalStep === 'verification' ? 'active' : 'available',
      count: `${Number(activeMemberVerified) + Number(kycVerified)}/2 checks`,
    },
    {
      step: 'appraisal' as const,
      label: 'Step 2',
      title: 'Appraise',
      owner: 'DM Finance',
      description: canForwardToSanction ? 'Appraisal note is ready to forward' : 'Enter recommendation, risk, security and conditions',
      state: appraisalStep === 'submitted' || canForwardToSanction ? 'complete' : appraisalStep === 'appraisal' ? 'active' : canProceedToAppraisal ? 'available' : 'locked',
      count: canForwardToSanction ? 'Ready' : `${[
        noteText.trim().length > 10,
        riskRationale.trim().length > 5,
        bankObservation.trim().length > 5,
        securityProposed.trim().length > 5,
        recommendedAmountNumber > 0,
        eligibilityComplete,
        cropObservation.trim().length > 5,
      ].filter(Boolean).length}/7 fields`,
    },
    {
      step: 'submitted' as const,
      label: 'Step 3',
      title: 'Review',
      owner: 'Credit Manager',
      description: decisionStatus === 'forwarded' ? 'Forwarded to Sanction Committee' : decisionStatus === 'returned' ? 'Returned to appraisal' : decisionStatus === 'rejected' ? 'Rejected' : decisionStatus === 'documents_requested' ? 'Documents requested' : 'Review package and record decision',
      state: appraisalStep === 'submitted' ? 'complete' : canForwardToSanction ? 'available' : 'locked',
      count: decisionStatus ? 'Done' : 'Pending',
    },
  ];

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Appraisal Workbench</h1>
          <p className="text-sm text-slate-500 mt-0.5">
            {appraisalQueue.length} application{appraisalQueue.length !== 1 ? 's' : ''} in appraisal workbench
            {' · '}Logged in as: <span className="font-semibold text-slate-700">{currentUser.role.replace(/_/g, ' ')}</span>
          </p>
        </div>
      </div>

      <div className="card">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {workflowSteps.map((item, i) => {
            const isLocked = item.state === 'locked';
            const isActive = item.state === 'active';
            const isComplete = item.state === 'complete';
            return (
              <button
                key={item.step}
                type="button"
                disabled={isLocked}
                onClick={() => !isLocked && setAppraisalStep(item.step)}
                className={`text-left rounded-lg border p-4 transition-colors ${
                  isActive ? 'border-green-500 bg-green-50 shadow-sm' :
                  isComplete ? 'border-green-200 bg-white' :
                  isLocked ? 'border-slate-200 bg-slate-50 opacity-70 cursor-not-allowed' :
                  'border-slate-200 bg-white hover:border-green-200 hover:bg-green-50'
                }`}
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <div className={`text-xs font-semibold ${isLocked ? 'text-slate-400' : 'text-green-700'}`}>
                      {item.label}
                    </div>
                    <div className={`mt-1 font-bold ${isLocked ? 'text-slate-500' : 'text-slate-900'}`}>
                      {item.title}
                    </div>
                  </div>
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                    isComplete ? 'bg-green-600 text-white' :
                    isActive ? 'bg-green-100 text-green-700' :
                    isLocked ? 'bg-slate-100 text-slate-400' : 'bg-amber-50 text-amber-600'
                  }`}>
                    {isComplete ? <CheckCircle2 size={16} /> : isLocked ? <Lock size={15} /> : i === 1 ? <FileText size={15} /> : i === 2 ? <Send size={15} /> : <BadgeCheck size={15} />}
                  </div>
                </div>
                <div className="mt-3 text-sm text-slate-600">{item.description}</div>
                <div className="mt-3 flex items-center justify-between gap-3 text-xs">
                  <span className="text-slate-500">Owner: {item.owner}</span>
                  <span className={`font-semibold ${isComplete ? 'text-green-700' : isLocked ? 'text-slate-400' : 'text-amber-700'}`}>{item.count}</span>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {appraisalQueue.length === 0 ? (
        <div className="card text-center py-16">
          <Check size={32} className="text-green-500 mx-auto mb-3" />
          <p className="text-slate-600 font-semibold">Appraisal queue is clear</p>
          <p className="text-slate-400 text-sm mt-1">All applications have been appraised.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Queue panel */}
          <div className="card p-0 overflow-hidden lg:col-span-1">
            <div className="p-4 bg-slate-50 border-b border-slate-200">
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Queue ({appraisalQueue.length})</p>
            </div>
            <div className="divide-y divide-slate-100">
              {appraisalQueue.map(a => (
                <button
                  key={a.id}
                  onClick={() => {
                    setSelected(a.id);
                    setDecisionStatus(null);
                    setShowExceptionConfirm(false);
                    setExceptionRegistered(false);
                    setPdfDownloaded(false);
                    const nextStep = a.status === 'reference_generated' ? 'verification' : (a.status === 'appraisal_in_progress' || a.status === 'appraisal_pending') ? 'appraisal' : 'submitted';
                    setAppraisalStep(nextStep);
                    setActiveMemberVerified(a.status !== 'reference_generated');
                    setActiveMemberRelaxationRecorded(false);
                    const kycStatus = members.find(m => m.id === a.memberId)?.kycStatus;
                    setKycVerified(a.status !== 'reference_generated' || kycStatus === 'verified');
                    setRiskRating(a.isException ? 'high' : 'low');
                    setCropObservation('');
                  }}
                  className={`w-full flex items-center gap-3 p-4 hover:bg-slate-50 transition-colors text-left ${
                    selected === a.id ? 'bg-green-50 border-l-4 border-l-green-500' : ''
                  }`}
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-0.5">
                      <div className="font-semibold text-slate-900 num text-sm">{a.applicationNumber}</div>
                      {a.isException && (
                        <span className="text-[10px] bg-violet-100 text-violet-700 px-1.5 py-0.5 rounded font-bold tracking-wide">EX</span>
                      )}
                    </div>
                    <div className="text-xs text-slate-500 truncate">{a.memberName}</div>
                    <div className="text-xs text-slate-400 num">{fmt(a.requestedAmount)}</div>
                  </div>
                  <div className="flex flex-col items-end gap-1">
                    <StatusBadge label={formatBadge(a.status)} size="sm" />
                    {a.referenceGeneratedAt && (
                      <TatChip daysRemaining={a.tatDaysRemaining} referenceGeneratedAt={a.referenceGeneratedAt} />
                    )}
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Detail panel */}
          {app && (
            <div className="lg:col-span-2 space-y-4">

              {/* Header card */}
              <div className="card">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <div className="flex items-center gap-2 flex-wrap">
                      <h2 className="text-lg font-bold text-slate-900 num">{app.applicationNumber}</h2>
                      <StatusBadge label={app.status} size="sm" />
                      {app.isException && (
                        <span className="text-xs bg-violet-100 text-violet-700 px-2 py-0.5 rounded font-medium">Exception</span>
                      )}
                    </div>
                    <p className="text-sm text-slate-600 mt-0.5">
                      {app.memberName}
                      <span className="mx-1.5 text-slate-300">·</span>
                      <span className="text-slate-500 capitalize">{app.memberType === 'fpc' ? 'FPC' : app.memberType.replace(/_/g, ' ')}</span>
                      <span className="mx-1.5 text-slate-300">·</span>
                      <span className="font-medium text-slate-700">{fmt(app.requestedAmount)}</span>
                    </p>
                    {app.referenceGeneratedAt && (
                      <div className="flex items-center gap-2 mt-2">
                        <TatChip daysRemaining={app.tatDaysRemaining} referenceGeneratedAt={app.referenceGeneratedAt} />
                        <span className="text-xs text-slate-400">TAT starts from LO# generation · {new Date(app.referenceGeneratedAt).toLocaleDateString('en-IN')}</span>
                      </div>
                    )}
                  </div>
                  <button onClick={() => onOpenApplication(app.id)} className="btn-secondary flex items-center gap-2 flex-shrink-0">
                    <FileText size={14} /> Full Application
                  </button>
                </div>

                {app.isException && (
                  <AlertBanner type="exception" title="Exception case — requested amount exceeds eligible limit" message={app.exceptionReason || ''} />
                )}
              </div>

              {/* ── STEP 1: Verification (S16 + S17) ── */}
              {(appraisalStep === 'verification') && (
                <div className="space-y-4">
                  {(!activeMemberVerified || !kycVerified) && (
                    <AlertBanner type="warning" title="Verification Incomplete"
                      message="Complete active-member and KYC verification before appraisal." />
                  )}

                  {/* S16: Active Member Verification */}
                  <div className="card">
                    <div className="flex items-center gap-3 mb-4">
                      <div className={`w-9 h-9 rounded-lg flex items-center justify-center ${activeMemberVerified ? 'bg-green-100' : 'bg-amber-50'}`}>
                        <Leaf size={16} className={activeMemberVerified ? 'text-green-600' : 'text-amber-600'} />
                      </div>
                      <div>
                        <h4 className="font-semibold text-slate-800">Active Member Verification</h4>
                        <p className="text-xs text-slate-500">Verify member meets 4-year supply rule or 1-year relaxation</p>
                      </div>
                    </div>

                    {member && (
                      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 mb-4">
                        {[
                          { label: 'Active Status', value: member.activeStatus, highlight: member.activeStatus !== 'active' },
                          { label: 'Supply Years', value: `${member.supplyYears} years` },
                          { label: '4-Year Rule Met', value: member.supplyYears >= 4 ? 'Yes ✓' : 'No ✗', highlight: member.supplyYears < 4 },
                          { label: 'Default Status', value: member.defaultStatus.replace(/_/g, ' '), highlight: member.defaultStatus !== 'no_default' },
                          { label: 'KYC Status', value: member.kycStatus.replace(/_/g, ' '), highlight: member.kycStatus !== 'verified' },
                          { label: 'Subsidiary', value: member.subsidiaryLinkage || 'Direct' },
                        ].map(({ label, value, highlight }) => (
                          <div key={label} className={`rounded-lg p-2.5 ${highlight ? 'bg-red-50 border border-red-100' : 'bg-slate-50'}`}>
                            <p className="text-xs text-slate-500">{label}</p>
                            <p className={`text-sm font-semibold mt-0.5 ${highlight ? 'text-red-700' : 'text-slate-900'}`}>{value}</p>
                          </div>
                        ))}
                      </div>
                    )}

                    <textarea
                      rows={2}
                      placeholder={member?.supplyYears !== undefined && member.supplyYears < 4 ? "Enter relaxation reason and attach evidence" : "Verification note — confirm supply records, relaxation applied (if any), subsidiary linkage…"}
                      value={activeMemberNote}
                      onChange={e => setActiveMemberNote(e.target.value)}
                      className="field-input text-sm resize-none mb-3"
                      disabled={isCreditManager || activeMemberVerified}
                    />

                    {isCreditManager && !activeMemberVerified ? (
                      <div className="bg-slate-50 border border-slate-200 text-slate-700 text-sm px-4 py-3 rounded-lg flex items-center gap-2 mt-2">
                        <Lock size={16} className="text-slate-500" />
                        <span className="font-semibold text-slate-900">Locked — Deputy Manager – Finance action required</span>
                      </div>
                    ) : member?.activeStatus !== 'active' ? (
                      <AlertBanner type="error" title="Member is NOT Active — Loan is Blocked"
                        message="Member does not meet the active member criteria. Cannot proceed with appraisal." />
                    ) : (member?.supplyYears !== undefined && member.supplyYears < 4) ? (
                      <div className="space-y-3">
                        <div className="flex items-center gap-2 bg-amber-50 border border-amber-200 rounded-lg p-3 text-sm text-amber-800">
                          <AlertTriangle size={16} className="text-amber-600 flex-shrink-0" />
                          <span>4-year supply rule not met. Record approved relaxation before appraisal.</span>
                        </div>
                        <button
                          onClick={handleRecordRelaxation}
                          disabled={activeMemberVerified || activeMemberRelaxationRecorded || !activeMemberNote.trim()}
                          className={`flex items-center gap-2 text-sm px-4 py-2 rounded-lg font-medium transition-colors ${
                            activeMemberVerified || activeMemberRelaxationRecorded
                              ? 'bg-amber-50 text-amber-700 border border-amber-200'
                              : 'bg-green-600 hover:bg-green-700 text-white disabled:opacity-50 disabled:cursor-not-allowed'
                          }`}
                        >
                          {activeMemberVerified ? <CheckCircle2 size={14} /> : <Clock size={14} />}
                          {activeMemberVerified ? 'Active Status Verified ✓' : activeMemberRelaxationRecorded ? 'Relaxation approval pending' : 'Record relaxation evidence'}
                        </button>
                      </div>
                    ) : (
                      <div className="flex gap-3">
                        <button
                          onClick={() => setActiveMemberVerified(true)}
                          disabled={activeMemberVerified}
                          className={`flex items-center gap-2 text-sm px-4 py-2 rounded-lg font-medium transition-colors ${
                            activeMemberVerified
                              ? 'bg-green-50 text-green-700 border border-green-200'
                              : 'bg-green-600 hover:bg-green-700 text-white'
                          }`}
                        >
                          <CheckCircle2 size={14} />
                          {activeMemberVerified ? 'Active Status Verified ✓' : 'Verify Active Member Status'}
                        </button>
                      </div>
                    )}
                  </div>

                  {/* S17: KYC Verification */}
                  <div className="card">
                    <div className="flex items-center gap-3 mb-4">
                      <div className={`w-9 h-9 rounded-lg flex items-center justify-center ${kycVerified ? 'bg-green-100' : 'bg-amber-50'}`}>
                        <BadgeCheck size={16} className={kycVerified ? 'text-green-600' : 'text-amber-600'} />
                      </div>
                      <div>
                        <h4 className="font-semibold text-slate-800">KYC Verification</h4>
                        <p className="text-xs text-slate-500">Verify PAN, Aadhaar, and CKYC against application documents</p>
                      </div>
                    </div>

                    {member && (
                      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 mb-4">
                        {[
                          { label: 'KYC Status', value: member.kycStatus === 'verified' ? 'Verified' : 'Pending confirmation', highlight: member.kycStatus !== 'verified' },
                          { label: 'PAN', value: '**-***-****' },
                          { label: 'Aadhaar', value: '****-****-****' },
                          { label: 'CKYC Ref', value: member.kycStatus === 'verified' ? 'On Record' : 'Pending' },
                          { label: 'Re-KYC Due', value: member.kycStatus === 'rekyc_due' ? 'Yes — Overdue' : 'No', highlight: member.kycStatus === 'rekyc_due' },
                          { label: 'PAN-Aadhaar Link', value: 'Linked ✓' },
                        ].map(({ label, value, highlight }) => (
                          <div key={label} className={`rounded-lg p-2.5 ${highlight ? 'bg-red-50 border border-red-100' : 'bg-slate-50'}`}>
                            <p className="text-xs text-slate-500">{label}</p>
                            <p className={`text-sm font-semibold mt-0.5 ${highlight ? 'text-red-700' : 'text-slate-900'}`}>{value}</p>
                          </div>
                        ))}
                      </div>
                    )}

                    {/* KYC document checklist */}
                    <div className="space-y-2 mb-4">
                      {[
                        { doc: 'PAN Card — self-attested copy', verified: true },
                        { doc: 'Aadhaar Card — self-attested copy', verified: true },
                        { doc: 'CKYC Reference Number cross-checked', verified: member?.kycStatus === 'verified' },
                        { doc: 'Photograph matches applicant', verified: true },
                      ].map((item, i) => (
                        <div key={i} className={`flex items-center gap-3 p-2.5 rounded-lg ${item.verified ? 'bg-green-50' : 'bg-amber-50'}`}>
                          {item.verified
                            ? <CheckCircle2 size={14} className="text-green-600 flex-shrink-0" />
                            : <AlertTriangle size={14} className="text-amber-600 flex-shrink-0" />}
                          <span className="text-sm text-slate-700">{item.doc}</span>
                          <StatusBadge label={item.verified ? 'verified' : 'pending'} size="sm" />
                        </div>
                      ))}
                    </div>

                    <textarea
                      rows={2}
                      placeholder="KYC verification note — confirm document match, CKYC reference, any anomalies…"
                      value={kycNote}
                      onChange={e => setKycNote(e.target.value)}
                      className="field-input text-sm resize-none mb-3"
                      disabled={isCreditManager || kycVerified}
                    />

                    {isCreditManager && !kycVerified ? (
                      <div className="bg-slate-50 border border-slate-200 text-slate-700 text-sm px-4 py-3 rounded-lg flex items-center gap-2 mt-2">
                        <Lock size={16} className="text-slate-500" />
                        <span className="font-semibold text-slate-900">Locked — Deputy Manager – Finance action required</span>
                      </div>
                    ) : member?.kycStatus !== 'verified' ? (
                      <AlertBanner type="warning" title="KYC Not Verified"
                        message="Member KYC must be verified before appraisal can proceed. Initiate re-KYC if needed." />
                    ) : (member?.kycStatus === 'verified' && kycVerified) ? (
                      <div className="flex gap-3 items-center justify-between mt-4 pt-4 border-t border-slate-100">
                        <span className="text-xs text-slate-500">KYC verified · 15/6/2026 · {currentUser.name}</span>
                        <button className="flex items-center gap-2 text-sm px-4 py-2 rounded-lg font-medium bg-slate-50 border border-slate-200 hover:bg-slate-100 text-slate-700 transition-colors">
                          View KYC evidence
                        </button>
                      </div>
                    ) : (
                      (can('do_completeness_check') || can('manage_compliance')) && (
                        <button
                          onClick={() => setKycVerified(true)}
                          disabled={kycVerified}
                          className="flex items-center gap-2 text-sm px-4 py-2 rounded-lg font-medium transition-colors bg-green-600 hover:bg-green-700 text-white"
                        >
                          <CheckCircle2 size={14} />
                          Confirm KYC Verification
                        </button>
                      )
                    )}
                  </div>

                  {/* Proceed button */}
                  <div className="flex items-center justify-end gap-3 mt-4">
                    {!canProceedToAppraisal && (
                      <span className="text-sm font-semibold text-slate-500 flex items-center gap-1.5">
                        <Lock size={14} /> Locked — complete Step 1 checks first
                      </span>
                    )}
                    <button
                      disabled={!canProceedToAppraisal}
                      onClick={() => setAppraisalStep('appraisal')}
                      className={`flex items-center gap-2 text-sm px-5 py-2.5 rounded-xl font-semibold transition-colors ${
                        canProceedToAppraisal
                          ? 'bg-green-600 hover:bg-green-700 text-white shadow-sm'
                          : 'bg-slate-100 text-slate-400 cursor-not-allowed'
                      }`}
                    >
                      {canProceedToAppraisal ? 'Proceed to Appraisal' : 'Complete verification first'} <ArrowRight size={16} />
                    </button>
                  </div>
                </div>
              )}

              {/* ── STEP 2: Appraisal Note ── */}
              {appraisalStep === 'appraisal' && (
                <div className="space-y-4">
                  <div className="flex items-center gap-2 bg-green-50 border border-green-100 rounded-xl p-3 text-xs text-green-700">
                    <CheckCircle2 size={14} className="flex-shrink-0" />
                    <span><strong>Step 2: Prepare appraisal note.</strong> Complete eligibility checklist first, then calculate limits and add recommendation, risk, repayment observations, security and conditions.</span>
                  </div>

                  {/* S15: Eligibility Checklist — FIRST, gates the calculator */}
                  <div className="card">
                    <h3 className="text-sm font-semibold text-slate-700 mb-4">Eligibility Checklist (S15)</h3>
                    <EligibilityChecklist
                      memberId={app.memberId}
                      applicationId={app.id}
                      onComplete={setEligibilityComplete}
                    />
                  </div>

                  {/* S18: Loan Limit Calculation — gated until eligibility passes */}
                  <div className="card">
                    <h3 className="text-sm font-semibold text-slate-700 mb-4">Loan Limit Calculation (S18)</h3>
                    {eligibilityComplete ? (
                      <LoanLimitCalculator
                        sharesHeld={app.sharesHeld}
                        shareMode={app.shareMode}
                        landAreaAcres={app.landAreaAcres}
                        requestedAmount={app.requestedAmount}
                        readonly
                      />
                    ) : (
                      <div className="flex items-center gap-3 p-4 bg-slate-50 border border-slate-200 rounded-lg">
                        <Lock size={16} className="text-slate-400 flex-shrink-0" />
                        <div>
                          <p className="text-sm font-semibold text-slate-600">Loan limit calculation is locked</p>
                          <p className="text-xs text-slate-400 mt-0.5">Complete the eligibility checklist above to unlock loan limit calculation.</p>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* P1-02: Crop Plan & Purpose */}
                  <div className="card">
                    <div className="flex items-center gap-3 mb-4">
                      <div className="w-9 h-9 rounded-lg flex items-center justify-center bg-green-50">
                        <Wheat size={16} className="text-green-600" />
                      </div>
                      <div>
                        <h3 className="text-sm font-semibold text-slate-700">Crop Plan & Purpose</h3>
                        <p className="text-xs text-slate-500">Verify loan purpose aligns with agricultural / crop production activity</p>
                      </div>
                    </div>
                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 mb-4">
                      <div className="rounded-lg bg-slate-50 p-2.5">
                        <p className="text-xs text-slate-500">Loan Purpose</p>
                        <p className="text-sm font-semibold text-slate-900 capitalize mt-0.5">{String(app.purpose).replace(/_/g, ' ')}</p>
                      </div>
                      <div className="rounded-lg bg-slate-50 p-2.5">
                        <p className="text-xs text-slate-500">Loan Type</p>
                        <p className="text-sm font-semibold text-slate-900 capitalize mt-0.5">{app.loanType === 'short_term' ? 'Short-term (1 yr)' : 'Long-term'}</p>
                      </div>
                      <div className="rounded-lg bg-slate-50 p-2.5">
                        <p className="text-xs text-slate-500">Crop Plan</p>
                        <p className="text-sm font-semibold text-green-700 mt-0.5">Submitted ✓</p>
                      </div>
                    </div>
                    <div>
                      <label className="field-label">Crop Plan Observation Notes <span className="text-red-500">*</span></label>
                      <textarea
                        rows={3}
                        value={cropObservation}
                        onChange={e => setCropObservation(e.target.value)}
                        className="field-input resize-none"
                        placeholder="Summarise crop plan viability — crop type, acreage, expected yield, seasonal alignment, any concerns with the stated agricultural purpose."
                      />
                      {cropObservation.trim().length > 0 && cropObservation.trim().length <= 5 && (
                        <p className="text-xs text-amber-600 mt-1">Please enter a meaningful observation (minimum 6 characters).</p>
                      )}
                    </div>
                  </div>

                  {/* Credit Risk Rating */}
                  <div className="card">
                    <h3 className="text-sm font-semibold text-slate-700 mb-3 flex items-center gap-2">
                      <BarChart2 size={14} /> Credit Risk Rating
                    </h3>
                    <div className="flex gap-3 mb-3">
                      {RISK_RATINGS.map(r => (
                        <button
                          key={r}
                          onClick={() => setRiskRating(r)}
                          className={`flex-1 py-2 rounded-lg text-xs font-semibold transition-colors capitalize ${
                            riskRating === r
                              ? r === 'low' ? 'bg-green-600 text-white'
                                : r === 'medium' ? 'bg-amber-500 text-white'
                                : r === 'high' ? 'bg-orange-600 text-white'
                                : 'bg-red-600 text-white'
                              : 'bg-slate-100 text-slate-500 hover:bg-slate-200'
                          }`}
                        >
                          {r.replace('_', ' ')}
                        </button>
                      ))}
                    </div>
                    <div className="flex items-center gap-2 text-xs text-slate-500">
                      <Info size={12} />
                      Low = standard approval · Medium/High = flag to Credit Manager · Very High = exception route
                    </div>
                  </div>

                  {/* Required Appraisal Inputs */}
                  <div className="card">
                    <div className="flex items-start justify-between gap-3 mb-4">
                      <div>
                        <h3 className="text-sm font-semibold text-slate-700 flex items-center gap-2">
                          <Scale size={14} /> Required Appraisal Inputs
                        </h3>
                        <p className="text-xs text-slate-500 mt-1">These fields make Step 2 functional and feed the Credit Manager review.</p>
                      </div>
                      <StatusBadge label={canForwardToSanction ? 'complete' : 'Draft incomplete'} size="sm" />
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <div>
                        <label className="field-label">Recommended Amount</label>
                        <input
                          type="number"
                          value={recommendedAmount}
                          onChange={e => {
                            const val = Number(e.target.value);
                            setRecommendedAmount(e.target.value);
                            if (val > (app?.eligibleAmount || 0) && recommendation !== 'exception' && recommendation !== 'reject') {
                              setRecommendation('exception');
                            }
                            setAppraisalDraftSaved(false);
                          }}
                          className="field-input"
                          placeholder={String(app?.eligibleAmount)}
                        />
                        {recommendedAmountNumber > (app?.eligibleAmount || 0) && (
                          <p className="text-xs text-amber-600 mt-1">Requested amount exceeds eligible limit by {fmt(recommendedAmountNumber - (app?.eligibleAmount || 0))}.</p>
                        )}
                      </div>
                      <div>
                        <label className="field-label">Recommended Tenure (months)</label>
                        <input
                          type="number"
                          value={recommendedTenure}
                          onChange={e => { setRecommendedTenure(e.target.value); setAppraisalDraftSaved(false); }}
                          className="field-input"
                          min={1}
                        />
                      </div>
                      <div>
                        <label className="field-label">Recommendation</label>
                        <select
                          value={recommendation}
                          onChange={e => { setRecommendation(e.target.value as typeof recommendation); setAppraisalDraftSaved(false); }}
                          className="field-select"
                        >
                          {recommendedAmountNumber > (app?.eligibleAmount || 0) ? (
                            <>
                              <option value="exception">Exception approval required</option>
                              <option value="reject">Reject at credit assessment</option>
                            </>
                          ) : (
                            <>
                              <option value="approve">Standard approval</option>
                              <option value="approve_conditions">Approve with conditions</option>
                              <option value="exception">Exception approval required</option>
                              <option value="reject">Reject at credit assessment</option>
                            </>
                          )}
                        </select>
                      </div>
                      <div>
                        <label className="field-label">Interest Rate Basis</label>
                        <input
                          value={FLOATING_RATE}
                          readOnly
                          className="field-input bg-slate-50 text-slate-600 cursor-default"
                        />
                      </div>
                      <div>
                        <label className="field-label">Security Proposed</label>
                        <input
                          value={securityProposed}
                          onChange={e => { setSecurityProposed(e.target.value); setAppraisalDraftSaved(false); }}
                          className="field-input"
                          placeholder="SH-4, CDSL pledge, PoA, blank cheque"
                        />
                      </div>
                      <div className="sm:col-span-2">
                        <label className="field-label">Bank Statement / Repayment Capacity Observations</label>
                        <textarea
                          rows={3}
                          value={bankObservation}
                          onChange={e => { setBankObservation(e.target.value); setAppraisalDraftSaved(false); }}
                          className="field-input resize-none"
                          placeholder="Summarise six-month bank statement observations, repayment capacity, crop proceeds and subsidiary deduction expectation."
                        />
                      </div>
                      <div className="sm:col-span-2">
                        <label className="field-label">Risk Rationale</label>
                        <textarea
                          rows={3}
                          value={riskRationale}
                          onChange={e => { setRiskRationale(e.target.value); setAppraisalDraftSaved(false); }}
                          className="field-input resize-none"
                          placeholder="Explain the selected risk rating using member history, KYC, land/crop evidence, default status and repayment capacity."
                        />
                      </div>
                      <div className="sm:col-span-2">
                        <label className="field-label">Conditions Precedent / Deficiencies</label>
                        <textarea
                          rows={2}
                          value={conditionsPrecedent}
                          onChange={e => { setConditionsPrecedent(e.target.value); setAppraisalDraftSaved(false); }}
                          className="field-input resize-none"
                          placeholder="List any condition to be completed before sanction/documentation. Use 'None' if not applicable."
                        />
                      </div>
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 mt-4">
                      {[
                        ['Recommended', recommendedAmountNumber ? fmt(recommendedAmountNumber) : 'Pending'],
                        ['Eligible', fmt(app.eligibleAmount)],
                        ['Tenure', `${recommendedTenure || '—'} months`],
                        ['Route', requiresException ? 'Exception' : recommendation.replace('_', ' ')],
                      ].map(([label, value]) => (
                        <div key={label} className="rounded-lg bg-slate-50 border border-slate-100 p-3">
                          <p className="text-xs text-slate-500">{label}</p>
                          <p className="text-sm font-semibold text-slate-900 mt-1 capitalize">{value}</p>
                        </div>
                      ))}
                    </div>
                    <div className="flex flex-wrap items-center justify-between gap-3 mt-4 border-t border-slate-100 pt-4">
                      <button
                        onClick={() => setAppraisalDraftSaved(true)}
                        className="btn-secondary text-sm flex items-center gap-2"
                      >
                        <Save size={14} />
                        {appraisalDraftSaved ? 'Draft Saved' : 'Save Appraisal Draft'}
                      </button>
                      <button
                        onClick={handleGeneratePdf}
                        disabled={!canForwardToSanction}
                        className={`text-sm flex items-center gap-2 ${canForwardToSanction ? 'btn-secondary' : 'bg-slate-100 text-slate-400 px-4 py-2 rounded-lg cursor-not-allowed border border-transparent'}`}
                      >
                        {pdfDownloaded ? <CheckCircle2 size={14} /> : <FileDown size={14} />}
                        {pdfDownloaded ? 'Appraisal Snapshot Downloaded ✓' : 'Download Appraisal Snapshot'}
                      </button>
                    </div>
                  </div>

                  {/* Appraisal note */}
                  <div className="card">
                    <h3 className="text-sm font-semibold text-slate-700 mb-3 flex items-center gap-2">
                      <FileText size={14} /> Loan Appraisal Note (DM Finance → Credit Manager)
                    </h3>
                    <textarea
                      rows={6}
                      value={noteText}
                      onChange={e => setNoteText(e.target.value)}
                      placeholder={`Summarise:
- Loan purpose and member background
- Active member and KYC verification findings
- Shareholding vs land-based limit calculation
- Security details (share pledge / PoA / SH-4)
- Risk rating justification
- Recommendation to Credit Manager…`}
                      className="field-input resize-none text-sm"
                    />
                    <div className="flex items-center justify-between mt-4">
                      <button onClick={() => setAppraisalStep('verification')} className="text-xs text-slate-400 hover:text-slate-600">
                        ← Back to Verification
                      </button>
                      <div className="flex gap-3">
                        <button className="btn-secondary text-sm flex items-center gap-2" onClick={() => onOpenApplication(app.id)}>
                          <FileText size={14} /> Full Application
                        </button>
                        {allowedToPrepareAppraisal ? (
                          <button
                            className={`text-sm flex items-center gap-2 px-4 py-2 rounded-lg font-semibold transition-colors ${canForwardToSanction ? 'bg-green-600 hover:bg-green-700 text-white shadow-sm' : 'bg-slate-100 text-slate-400 cursor-not-allowed'}`}
                            disabled={!canForwardToSanction}
                            onClick={() => setAppraisalStep('submitted')}
                          >
                            {canForwardToSanction ? 'Submit to Credit Manager' : 'Complete appraisal first'}
                          </button>
                        ) : (
                          <button className="bg-slate-100 text-slate-400 px-4 py-2 rounded-lg text-sm font-semibold opacity-50 cursor-not-allowed" disabled>
                            Submit to Credit Manager
                          </button>
                        )}
                      </div>
                    </div>
                    {!canForwardToSanction && (
                      <div className="mt-4">
                        <AlertBanner
                          type="warning"
                          title="Step 2 is not complete"
                          message="Eligibility checklist, crop plan observation, recommended amount, risk rationale, bank observations, proposed security and appraisal note are all required before forwarding."
                        />
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* ── STEP 3: Credit Manager Review ── */}
              {appraisalStep === 'submitted' && (
                <div className="space-y-4">
                  <div className="flex items-center gap-2 bg-blue-50 border border-blue-100 rounded-xl p-3 text-xs text-blue-700">
                    <Send size={14} className="flex-shrink-0" />
                    <span><strong>Step 3: Credit Manager review.</strong> Review appraisal package, record decision reason, then forward, return, request documents, or reject.</span>
                  </div>

                  {/* P1-04: Borrower & Default History */}
                  {member && (
                    <div className="card">
                      <h3 className="text-sm font-semibold text-slate-700 mb-3">Borrower & Default History</h3>
                      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                        {[
                          { label: 'Active Status', value: member.activeStatus, badge: member.activeStatus !== 'active' ? 'rejected' : 'approved' },
                          { label: 'Default Status', value: member.defaultStatus.replace(/_/g, ' '), badge: member.defaultStatus !== 'no_default' ? (member.defaultStatus === 'current_default' ? 'rejected' : 'pending') : 'approved' },
                          { label: 'Supply Years', value: `${member.supplyYears} yrs`, badge: member.supplyYears >= 4 ? 'approved' : 'pending' },
                          { label: 'Member Type', value: app.memberType === 'fpc' ? 'FPC' : app.memberType.replace(/_/g, ' '), badge: 'neutral' },
                          { label: 'Subsidiary', value: member.subsidiaryLinkage || 'Direct', badge: 'neutral' },
                          { label: 'KYC Status', value: member.kycStatus.replace(/_/g, ' '), badge: member.kycStatus === 'verified' ? 'approved' : 'pending' },
                        ].map(({ label, value, badge }) => (
                          <div key={label} className="rounded-lg bg-slate-50 p-3">
                            <p className="text-xs text-slate-500">{label}</p>
                            <p className={`text-sm font-semibold capitalize mt-1 ${badge === 'rejected' ? 'text-red-700' : badge === 'pending' ? 'text-amber-700' : badge === 'approved' ? 'text-green-700' : 'text-slate-900'}`}>
                              {value}
                            </p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className="card">
                    <div className="flex items-start justify-between gap-4 mb-4">
                      <div>
                        <h3 className="font-bold text-slate-900">Credit Manager Review Package</h3>
                        <p className="text-sm text-slate-500 mt-1">{app.applicationNumber} · {app.memberName}</p>
                      </div>
                      <StatusBadge label={requiresException ? 'exception_required' : 'credit_review'} size="sm" />
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                      {[
                        ['Recommended Amount', fmt(recommendedAmountNumber)],
                        ['Eligible Amount', fmt(app.eligibleAmount)],
                        ['Recommended Tenure', `${recommendedTenure} months`],
                        ['Risk Rating', riskRating.replace('_', ' ')],
                        ['Recommendation', recommendation.replace('_', ' ')],
                        ['Security', securityProposed],
                        ['Interest Rate', FLOATING_RATE],
                      ].map(([label, value]) => (
                        <div key={label} className="rounded-lg bg-slate-50 border border-slate-100 p-3">
                          <p className="text-xs text-slate-500">{label}</p>
                          <p className="text-sm font-semibold text-slate-900 mt-1 capitalize break-words">{value}</p>
                        </div>
                      ))}
                    </div>
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mt-4">
                      <div className={`rounded-lg border p-3 ${!riskRationale.trim() ? 'border-red-100 bg-red-50' : 'border-slate-100'}`}>
                        <p className={`text-xs font-semibold uppercase tracking-wide ${!riskRationale.trim() ? 'text-red-700' : 'text-slate-500'}`}>Risk Rationale</p>
                        <p className={`text-sm mt-2 whitespace-pre-wrap ${!riskRationale.trim() ? 'text-red-600 font-medium' : 'text-slate-700'}`}>
                          {riskRationale.trim() ? riskRationale : 'Risk rationale missing'}
                        </p>
                      </div>
                      <div className={`rounded-lg border p-3 ${!bankObservation.trim() ? 'border-red-100 bg-red-50' : 'border-slate-100'}`}>
                        <p className={`text-xs font-semibold uppercase tracking-wide ${!bankObservation.trim() ? 'text-red-700' : 'text-slate-500'}`}>Bank / Repayment Observations</p>
                        <p className={`text-sm mt-2 whitespace-pre-wrap ${!bankObservation.trim() ? 'text-red-600 font-medium' : 'text-slate-700'}`}>
                          {bankObservation.trim() ? bankObservation : 'Bank / repayment observations missing'}
                        </p>
                      </div>
                    </div>
                    {cropObservation.trim() && (
                      <div className="rounded-lg border border-green-100 bg-green-50 p-3 mt-4">
                        <p className="text-xs font-semibold text-green-700 uppercase tracking-wide">Crop Plan Observations</p>
                        <p className="text-sm text-green-900 mt-2 whitespace-pre-wrap">{cropObservation}</p>
                      </div>
                    )}
                    {conditionsPrecedent && (
                      <div className="rounded-lg border border-amber-100 bg-amber-50 p-3 mt-4">
                        <p className="text-xs font-semibold text-amber-700 uppercase tracking-wide">Conditions Precedent</p>
                        <p className="text-sm text-amber-800 mt-2 whitespace-pre-wrap">{conditionsPrecedent}</p>
                      </div>
                    )}
                  </div>

                  {!decisionStatus && !showExceptionConfirm ? (
                    <>
                      <div className="card">
                        <h3 className="text-sm font-semibold text-slate-700 mb-3">Credit Manager Decision</h3>
                        <textarea
                          rows={4}
                          value={creditManagerComment}
                          onChange={e => setCreditManagerComment(e.target.value)}
                          placeholder="Mandatory for rejection, return for correction, exception routing, or recommended amount differing from eligible amount."
                          className="field-input resize-none mb-4"
                        />
                        {(!riskRationale.trim() || !bankObservation.trim() || !noteText.trim()) && (
                          <div className="mb-4">
                            <AlertBanner type="error" title="Appraisal package incomplete" message="Return to appraisal before forwarding." />
                          </div>
                        )}
                        <div className="flex flex-wrap gap-3">
                          {/* Return */}
                          <button
                            disabled={!creditManagerComment.trim()}
                            onClick={() => {
                              console.log({ action: 'RETURNED', actor: currentUser.role, time: new Date().toISOString(), reason: creditManagerComment, app: app.id });
                              setDecisionStatus('returned');
                              onUpdateStatus?.(app.id, 'appraisal_in_progress');
                            }}
                            className="btn-secondary text-sm flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                            <RotateCcw size={14} />
                            Return to appraisal
                          </button>

                          {can('do_completeness_check') ? (
                            <>
                              {/* Request Documents */}
                              <button
                                disabled={!creditManagerComment.trim()}
                                onClick={() => {
                                  console.log({ action: 'DOCUMENTS_REQUESTED', actor: currentUser.role, time: new Date().toISOString(), reason: creditManagerComment, app: app.id });
                                  setDecisionStatus('documents_requested');
                                  onUpdateStatus?.(app.id, 'appraisal_in_progress');
                                }}
                                className="btn-secondary text-sm flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                              >
                                <FileDown size={14} />
                                Request Documents
                              </button>

                              {/* Reject */}
                              <button
                                disabled={!creditManagerComment.trim()}
                                onClick={handleReject}
                                className="bg-red-600 hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium px-4 py-2 rounded-lg transition-colors text-sm flex items-center gap-2"
                              >
                                <XCircle size={14} />
                                Reject
                              </button>

                              {/* Forward to Sanction */}
                              <button
                                disabled={!creditManagerComment.trim() || !riskRationale.trim() || !bankObservation.trim() || !noteText.trim() || !recommendedAmountNumber || (requiresException && recommendation !== 'exception')}
                                onClick={handleForwardToSanction}
                                className="btn-primary text-sm flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed ml-auto"
                              >
                                <Send size={14} />
                                Forward to Sanction Committee
                              </button>
                            </>
                          ) : (
                            <div className="text-sm text-amber-700 bg-amber-50 p-2 rounded border border-amber-200 ml-auto">
                              Waiting for Credit Manager review and forwarding.
                            </div>
                          )}
                        </div>
                        {requiresException && (
                          <div className="mt-3 text-xs text-violet-600 font-medium flex justify-end">
                            Exception approval required — forwarding will create an Exception Register entry.
                          </div>
                        )}
                        <div className="mt-4 text-xs text-slate-500">
                          Forwarding preserves the appraisal note, risk rationale, recommended amount, conditions and document evidence for audit.
                        </div>
                      </div>

                      <div className="card text-center py-8">
                        <div className="w-14 h-14 rounded-full bg-slate-100 flex items-center justify-center mx-auto mb-4">
                          <Check size={28} className="text-slate-400" />
                        </div>
                        <h3 className="text-lg font-bold text-slate-900">Ready for Credit Manager review</h3>
                        <p className="text-sm text-slate-500 mt-2">
                          Complete review decision to move this case forward.
                        </p>
                      </div>
                    </>
                  ) : showExceptionConfirm ? (
                    /* P2-04: Exception Register pre-confirmation */
                    <div className="card border-violet-200 bg-violet-50">
                      <div className="flex items-start gap-3 mb-4">
                        <div className="w-10 h-10 rounded-full bg-violet-100 flex items-center justify-center flex-shrink-0">
                          <AlertTriangle size={18} className="text-violet-700" />
                        </div>
                        <div>
                          <h3 className="font-bold text-violet-900">Confirm Exception Registration</h3>
                          <p className="text-sm text-violet-700 mt-1">
                            This case requires exception approval. Forwarding will create an entry in the Exception Register for CFO + 2 Directors review.
                          </p>
                        </div>
                      </div>
                      <div className="bg-white rounded-lg border border-violet-100 p-3 mb-4 space-y-2 text-sm">
                        <div className="flex justify-between"><span className="text-slate-500">Application</span><span className="font-semibold">{app.applicationNumber}</span></div>
                        <div className="flex justify-between"><span className="text-slate-500">Borrower</span><span className="font-semibold">{app.memberName}</span></div>
                        <div className="flex justify-between"><span className="text-slate-500">Requested</span><span className="font-semibold">{fmt(recommendedAmountNumber)}</span></div>
                        <div className="flex justify-between"><span className="text-slate-500">Eligible Limit</span><span className="font-semibold">{fmt(app.eligibleAmount)}</span></div>
                        <div className="flex justify-between"><span className="text-slate-500">Exception Reason</span><span className="font-semibold text-violet-700">{creditManagerComment}</span></div>
                      </div>
                      <p className="text-xs text-violet-600 mb-4">An Exception Register entry will be logged and routed to CFO + 2 Directors for countersignature before sanction committee review proceeds.</p>
                      <div className="flex gap-3">
                        <button
                          onClick={() => setShowExceptionConfirm(false)}
                          className="btn-secondary text-sm"
                        >
                          Cancel
                        </button>
                        <button
                          onClick={handleConfirmException}
                          className="btn-primary text-sm flex items-center gap-2 ml-auto"
                        >
                          <Send size={14} />
                          Confirm & Forward with Exception
                        </button>
                      </div>
                    </div>
                  ) : (
                    /* Decision outcome card */
                    <div className="card text-center py-8">
                      <div className={`w-14 h-14 rounded-full flex items-center justify-center mx-auto mb-4 ${
                        decisionStatus === 'forwarded' ? 'bg-green-100' :
                        decisionStatus === 'rejected' ? 'bg-red-100' :
                        decisionStatus === 'documents_requested' ? 'bg-blue-100' : 'bg-amber-100'
                      }`}>
                        {decisionStatus === 'forwarded' ? <Check size={28} className="text-green-600" /> :
                         decisionStatus === 'rejected' ? <XCircle size={28} className="text-red-600" /> :
                         decisionStatus === 'documents_requested' ? <FileDown size={28} className="text-blue-600" /> :
                         <RotateCcw size={28} className="text-amber-600" />}
                      </div>
                      <h3 className="text-lg font-bold text-slate-900">
                        {decisionStatus === 'forwarded' ? 'Forwarded to Sanction Committee' :
                         decisionStatus === 'rejected' ? 'Rejected — Rejection Note Downloaded' :
                         decisionStatus === 'documents_requested' ? 'Documents Requested' :
                         'Returned to appraisal'}
                      </h3>
                      <p className="text-sm text-slate-500 mt-2">
                        {decisionStatus === 'forwarded' ? `${app.applicationNumber} was forwarded ${requiresException ? 'with exception route' : 'for standard sanction'}.` :
                         decisionStatus === 'rejected' ? 'A rejection note has been downloaded. Applicant to be notified.' :
                         decisionStatus === 'documents_requested' ? `Additional documents requested. ${app.memberName} to be notified.` :
                         `Action completed by ${currentUser.role.replace(/_/g, ' ')}.`}
                      </p>
                      {exceptionRegistered && (
                        <div className="inline-flex items-center gap-2 mt-3 bg-violet-50 border border-violet-200 text-violet-700 text-xs font-semibold px-3 py-1.5 rounded-full">
                          <BadgeCheck size={12} /> Exception entry registered for CFO + Directors review
                        </div>
                      )}
                      {decisionStatus === 'rejected' && (
                        <div className="inline-flex items-center gap-2 mt-3 bg-slate-50 border border-slate-200 text-slate-600 text-xs font-semibold px-3 py-1.5 rounded-full">
                          <Download size={12} /> rejection-note-{app.applicationNumber}.json
                        </div>
                      )}
                      <div className="flex gap-3 justify-center mt-6">
                        <button onClick={() => { setSelected(appraisalQueue.find(a => a.id !== selected)?.id || null); setAppraisalStep('verification'); }} className="btn-secondary text-sm">Next in Queue</button>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default AppraisalWorkbench;
