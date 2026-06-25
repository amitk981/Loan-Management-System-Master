import React, { useState } from 'react';
import {
  Scale, ChevronRight, FileText, Check, CheckCircle2, XCircle,
  AlertTriangle, User, Shield, RefreshCw, Clock, BarChart2,
  ArrowRight, Info, Lock, Leaf, BadgeCheck, FileDown, Save,
  Send, RotateCcw
} from 'lucide-react';
import StatusBadge from '../../components/ui/StatusBadge';
import AlertBanner from '../../components/ui/AlertBanner';
import LoanLimitCalculator from '../../components/loan/LoanLimitCalculator';
import EligibilityChecklist from '../../components/loan/EligibilityChecklist';
import { loanApplications, members } from '../../data/mockData';
import { useRole } from '../../contexts/RoleContext';

const fmt = (n: number) => '₹' + n.toLocaleString('en-IN');

// ── Risk Rating options per spec ──────────────────────────────────────────
const RISK_RATINGS = ['low', 'medium', 'high', 'very_high'] as const;

interface AppraisalWorkbenchProps {
  onOpenApplication: (id: string) => void;
}

const AppraisalWorkbench: React.FC<AppraisalWorkbenchProps> = ({ onOpenApplication }) => {
  const appraisalQueue = loanApplications.filter(a =>
    ['reference_generated', 'appraisal_pending', 'credit_review'].includes(a.status)
  );
  const [selected, setSelected] = useState<string | null>(appraisalQueue[0]?.id || null);
  const [noteText, setNoteText] = useState('');
  const [riskRating, setRiskRating] = useState<typeof RISK_RATINGS[number]>('low');
  const [appraisalStep, setAppraisalStep] = useState<'verification' | 'appraisal' | 'submitted'>('verification');
  const [recommendedAmount, setRecommendedAmount] = useState('');
  const [recommendedTenure, setRecommendedTenure] = useState('12');
  const [securityProposed, setSecurityProposed] = useState('SH-4 physical share transfer form, PoA, blank-dated cheque');
  const [bankObservation, setBankObservation] = useState('');
  const [riskRationale, setRiskRationale] = useState('');
  const [conditionsPrecedent, setConditionsPrecedent] = useState('');
  const [recommendation, setRecommendation] = useState<'approve' | 'approve_conditions' | 'exception' | 'reject'>('approve');
  const [creditManagerComment, setCreditManagerComment] = useState('');
  const [appraisalDraftSaved, setAppraisalDraftSaved] = useState(false);
  const { currentUser, can } = useRole();

  // ── S16 Active Member Verification ──────────────────────────────────────
  const [activeMemberVerified, setActiveMemberVerified] = useState(false);
  const [activeMemberNote, setActiveMemberNote] = useState('');

  // ── S17 KYC Verification ─────────────────────────────────────────────────
  const [kycVerified, setKycVerified] = useState(false);
  const [kycNote, setKycNote] = useState('');

  // Credit risk score ────────────────────────────────────────────────────────
  const [creditScoreVerified, setCreditScoreVerified] = useState(false);
  const [creditScore, setCreditScore] = useState('');

  const app = appraisalQueue.find(a => a.id === selected);
  const member = app ? members.find(m => m.id === app.memberId) : null;

  const isDMFinance = currentUser.role === 'deputy_manager_finance';
  const isCreditManager = currentUser.role === 'credit_manager';

  const canProceedToAppraisal = activeMemberVerified && kycVerified;
  const recommendedAmountNumber = Number(recommendedAmount || 0);
  const recommendedWithinLimit = app ? recommendedAmountNumber > 0 && recommendedAmountNumber <= app.eligibleAmount : false;
  const requiresException = app?.isException || recommendation === 'exception' || (recommendedAmountNumber > 0 && app ? recommendedAmountNumber > app.eligibleAmount : false);
  const canForwardToSanction =
    noteText.trim().length > 10 &&
    riskRating &&
    riskRationale.trim().length > 5 &&
    bankObservation.trim().length > 5 &&
    securityProposed.trim().length > 5 &&
    recommendedAmountNumber > 0 &&
    (recommendedWithinLimit || requiresException);

  const workflowSteps = [
    {
      step: 'verification' as const,
      label: 'Step 1',
      title: 'Verify',
      owner: 'DM Finance',
      description: activeMemberVerified && kycVerified ? 'Active member and KYC verified' : 'Complete active member and KYC checks',
      state: activeMemberVerified && kycVerified ? 'complete' : appraisalStep === 'verification' ? 'active' : 'available',
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
      ].filter(Boolean).length}/5 fields`,
    },
    {
      step: 'submitted' as const,
      label: 'Step 3',
      title: 'Forward',
      owner: isCreditManager ? 'Credit Manager' : 'Credit Manager review',
      description: appraisalStep === 'submitted' ? 'Forwarded for review / sanction routing' : 'Review package and forward after appraisal',
      state: appraisalStep === 'submitted' ? 'complete' : canForwardToSanction ? 'available' : 'locked',
      count: appraisalStep === 'submitted' ? 'Done' : 'Pending',
    },
  ];

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Appraisal Workbench</h1>
          <p className="text-sm text-slate-500 mt-0.5">
            {appraisalQueue.length} application{appraisalQueue.length !== 1 ? 's' : ''} pending appraisal
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
                  onClick={() => { setSelected(a.id); setAppraisalStep('verification'); setActiveMemberVerified(false); setKycVerified(false); }}
                  className={`w-full flex items-center gap-3 p-4 hover:bg-slate-50 transition-colors text-left ${
                    selected === a.id ? 'bg-green-50 ring-1 ring-inset ring-green-200' : ''
                  }`}
                >
                  <div className="flex-1 min-w-0">
                    <div className="font-semibold text-slate-900 num text-sm">{a.applicationNumber}</div>
                    <div className="text-xs text-slate-500 truncate">{a.memberName}</div>
                    <div className="text-xs text-slate-400 num">{fmt(a.requestedAmount)}</div>
                  </div>
                  <div className="flex flex-col items-end gap-1">
                    <StatusBadge label={a.status} size="sm" />
                    {a.isException && (
                      <span className="text-xs bg-violet-100 text-violet-700 px-1 py-0.5 rounded font-medium">EX</span>
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
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <div className="flex items-center gap-2">
                      <h2 className="text-lg font-bold text-slate-900 num">{app.applicationNumber}</h2>
                      <StatusBadge label={app.status} size="sm" />
                      {app.isException && (
                        <span className="text-xs bg-violet-100 text-violet-700 px-2 py-0.5 rounded font-medium">Exception</span>
                      )}
                    </div>
                    <p className="text-sm text-slate-500">{app.memberName} · {fmt(app.requestedAmount)}</p>
                  </div>
                  <button onClick={() => onOpenApplication(app.id)} className="text-xs text-green-600 hover:underline flex items-center gap-1">
                    Full view <ChevronRight size={12} />
                  </button>
                </div>

                {app.isException && (
                  <AlertBanner type="exception" title="Exception case — requested amount exceeds eligible limit" message={app.exceptionReason || ''} />
                )}
              </div>

              {/* ── STEP 1: Verification (S16 + S17) ── */}
              {(appraisalStep === 'verification') && (
                <div className="space-y-4">
                  {/* Role guidance */}
                  <div className="flex items-center gap-2 bg-blue-50 border border-blue-100 rounded-xl p-3 text-xs text-blue-700">
                    <Info size={14} className="flex-shrink-0" />
                    <span><strong>Step 1:</strong> Deputy Manager – Finance must complete Active Member Verification (S16) and KYC Verification (S17) before appraisal can proceed.</span>
                  </div>

                  {/* S16: Active Member Verification */}
                  <div className="card">
                    <div className="flex items-center gap-3 mb-4">
                      <div className={`w-9 h-9 rounded-lg flex items-center justify-center ${activeMemberVerified ? 'bg-green-100' : 'bg-amber-50'}`}>
                        <Leaf size={16} className={activeMemberVerified ? 'text-green-600' : 'text-amber-600'} />
                      </div>
                      <div>
                        <h4 className="font-semibold text-slate-800">S16: Active Member Verification</h4>
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
                      placeholder="Verification note — confirm supply records, relaxation applied (if any), subsidiary linkage…"
                      value={activeMemberNote}
                      onChange={e => setActiveMemberNote(e.target.value)}
                      className="field-input text-sm resize-none mb-3"
                    />

                    {member?.activeStatus !== 'active' ? (
                      <AlertBanner type="error" title="Member is NOT Active — Loan is Blocked"
                        message="Member does not meet the active member criteria. Cannot proceed with appraisal." />
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
                        <h4 className="font-semibold text-slate-800">S17: KYC Verification</h4>
                        <p className="text-xs text-slate-500">Verify PAN, Aadhaar, and CKYC against application documents</p>
                      </div>
                    </div>

                    {member && (
                      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 mb-4">
                        {[
                          { label: 'KYC Status', value: member.kycStatus.replace(/_/g, ' '), highlight: member.kycStatus !== 'verified' },
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
                    />

                    {member?.kycStatus !== 'verified' ? (
                      <AlertBanner type="warning" title="KYC Not Verified"
                        message="Member KYC must be verified before appraisal can proceed. Initiate re-KYC if needed." />
                    ) : (
                      <button
                        onClick={() => setKycVerified(true)}
                        disabled={kycVerified}
                        className={`flex items-center gap-2 text-sm px-4 py-2 rounded-lg font-medium transition-colors ${
                          kycVerified
                            ? 'bg-green-50 text-green-700 border border-green-200'
                            : 'bg-green-600 hover:bg-green-700 text-white'
                        }`}
                      >
                        <CheckCircle2 size={14} />
                        {kycVerified ? 'KYC Verified ✓' : 'Confirm KYC Verification'}
                      </button>
                    )}
                  </div>

                  {/* Proceed button */}
                  <div className="flex justify-end">
                    <button
                      disabled={!canProceedToAppraisal}
                      onClick={() => setAppraisalStep('appraisal')}
                      className={`flex items-center gap-2 text-sm px-5 py-2.5 rounded-xl font-semibold transition-colors ${
                        canProceedToAppraisal
                          ? 'bg-green-600 hover:bg-green-700 text-white shadow-sm'
                          : 'bg-slate-100 text-slate-400 cursor-not-allowed'
                      }`}
                    >
                      Proceed to Appraisal <ArrowRight size={16} />
                    </button>
                  </div>
                </div>
              )}

              {/* ── STEP 2: Appraisal Note ── */}
              {appraisalStep === 'appraisal' && (
                <div className="space-y-4">
                  <div className="flex items-center gap-2 bg-green-50 border border-green-100 rounded-xl p-3 text-xs text-green-700">
                    <CheckCircle2 size={14} className="flex-shrink-0" />
                    <span><strong>Step 2: Appraise.</strong> Verification complete. Prepare the Loan Appraisal Note with recommendation, risk rationale, bank observations, security and conditions precedent.</span>
                  </div>

                  {/* Loan limit */}
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

                  {/* Eligibility */}
                  <div className="card">
                    <h3 className="text-sm font-semibold text-slate-700 mb-4">Eligibility Checklist</h3>
                    <EligibilityChecklist memberId={app.memberId} applicationId={app.id} />
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

                  {/* Appraisal required fields */}
                  <div className="card">
                    <div className="flex items-start justify-between gap-3 mb-4">
                      <div>
                        <h3 className="text-sm font-semibold text-slate-700 flex items-center gap-2">
                          <Scale size={14} /> S19 Required Appraisal Inputs
                        </h3>
                        <p className="text-xs text-slate-500 mt-1">These fields make Step 2 functional and feed the Credit Manager review.</p>
                      </div>
                      <StatusBadge label={canForwardToSanction ? 'complete' : 'in_progress'} size="sm" />
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <div>
                        <label className="field-label">Recommended Amount</label>
                        <input
                          type="number"
                          value={recommendedAmount}
                          onChange={e => { setRecommendedAmount(e.target.value); setAppraisalDraftSaved(false); }}
                          className="field-input"
                          placeholder={String(app.eligibleAmount)}
                        />
                        {recommendedAmountNumber > app.eligibleAmount && (
                          <p className="text-xs text-amber-600 mt-1">Above eligible amount. Exception route will be required.</p>
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
                          <option value="approve">Approve</option>
                          <option value="approve_conditions">Approve with conditions</option>
                          <option value="exception">Exception required</option>
                          <option value="reject">Reject at credit assessment</option>
                        </select>
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
                        onClick={() => setAppraisalDraftSaved(true)}
                        className="btn-secondary text-sm flex items-center gap-2"
                      >
                        <FileDown size={14} />
                        Generate Appraisal PDF
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
                        <button className="btn-secondary text-sm" onClick={() => onOpenApplication(app.id)}>
                          View Full Application
                        </button>
                        <button
                          className="btn-primary text-sm disabled:opacity-50"
                          disabled={!canForwardToSanction}
                          onClick={() => setAppraisalStep('submitted')}
                        >
                          Continue to Forward →
                        </button>
                      </div>
                    </div>
                    {!canForwardToSanction && (
                      <div className="mt-4">
                        <AlertBanner
                          type="warning"
                          title="Step 2 is not complete"
                          message="Recommended amount, risk rationale, bank observations, proposed security and appraisal note are required before forwarding."
                        />
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* ── STEP 3: Submitted ── */}
              {appraisalStep === 'submitted' && (
                <div className="space-y-4">
                  <div className="flex items-center gap-2 bg-blue-50 border border-blue-100 rounded-xl p-3 text-xs text-blue-700">
                    <Send size={14} className="flex-shrink-0" />
                    <span><strong>Step 3: Forward.</strong> Review the appraisal package, capture Credit Manager comment, then forward to Sanction Committee or return/reject with reason.</span>
                  </div>

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
                      ].map(([label, value]) => (
                        <div key={label} className="rounded-lg bg-slate-50 border border-slate-100 p-3">
                          <p className="text-xs text-slate-500">{label}</p>
                          <p className="text-sm font-semibold text-slate-900 mt-1 capitalize break-words">{value}</p>
                        </div>
                      ))}
                    </div>
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mt-4">
                      <div className="rounded-lg border border-slate-100 p-3">
                        <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Risk Rationale</p>
                        <p className="text-sm text-slate-700 mt-2 whitespace-pre-wrap">{riskRationale}</p>
                      </div>
                      <div className="rounded-lg border border-slate-100 p-3">
                        <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Bank / Repayment Observations</p>
                        <p className="text-sm text-slate-700 mt-2 whitespace-pre-wrap">{bankObservation}</p>
                      </div>
                    </div>
                    {conditionsPrecedent && (
                      <div className="rounded-lg border border-amber-100 bg-amber-50 p-3 mt-4">
                        <p className="text-xs font-semibold text-amber-700 uppercase tracking-wide">Conditions Precedent</p>
                        <p className="text-sm text-amber-800 mt-2 whitespace-pre-wrap">{conditionsPrecedent}</p>
                      </div>
                    )}
                  </div>

                  <div className="card">
                    <h3 className="text-sm font-semibold text-slate-700 mb-3">S20 Credit Manager Decision</h3>
                    <textarea
                      rows={4}
                      value={creditManagerComment}
                      onChange={e => setCreditManagerComment(e.target.value)}
                      placeholder="Mandatory for rejection, return for correction, exception routing, or recommended amount differing from eligible amount."
                      className="field-input resize-none mb-4"
                    />
                    <div className="flex flex-wrap gap-3">
                      <button
                        onClick={() => setAppraisalStep('appraisal')}
                        className="btn-secondary text-sm flex items-center gap-2"
                      >
                        <RotateCcw size={14} />
                        Return to Appraise
                      </button>
                      <button
                        disabled={!creditManagerComment.trim()}
                        className="bg-amber-500 hover:bg-amber-600 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium px-4 py-2 rounded-lg transition-colors text-sm flex items-center gap-2"
                      >
                        <RefreshCw size={14} />
                        Request Correction
                      </button>
                      <button
                        disabled={recommendation === 'reject' && !creditManagerComment.trim()}
                        className="bg-red-600 hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium px-4 py-2 rounded-lg transition-colors text-sm flex items-center gap-2"
                      >
                        <XCircle size={14} />
                        Reject
                      </button>
                      <button
                        disabled={(requiresException || recommendedAmountNumber !== app.eligibleAmount) && !creditManagerComment.trim()}
                        className="btn-primary text-sm flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        <Send size={14} />
                        {requiresException ? 'Forward Exception to Sanction Committee' : 'Forward to Sanction Committee'}
                      </button>
                    </div>
                    <div className="mt-4 text-xs text-slate-500">
                      Forwarding preserves the appraisal note, risk rationale, recommended amount, conditions and document evidence for audit.
                    </div>
                  </div>

                  <div className="card text-center py-8">
                    <div className="w-14 h-14 rounded-full bg-green-100 flex items-center justify-center mx-auto mb-4">
                      <Check size={28} className="text-green-600" />
                    </div>
                    <h3 className="text-lg font-bold text-slate-900">Step 3 Ready</h3>
                    <p className="text-sm text-slate-500 mt-2">
                      {app.applicationNumber} is ready for Credit Manager action.
                    </p>
                    <div className="flex gap-3 justify-center mt-6">
                      <button onClick={() => onOpenApplication(app.id)} className="btn-secondary text-sm">View Application</button>
                      <button onClick={() => { setSelected(appraisalQueue.find(a => a.id !== selected)?.id || null); setAppraisalStep('verification'); }} className="btn-secondary text-sm">Next in Queue</button>
                    </div>
                  </div>
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
