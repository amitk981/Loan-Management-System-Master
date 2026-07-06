import React, { useState, useEffect } from 'react';
import {
  Gavel, ChevronRight, FileText, Check, AlertOctagon, Shield, CheckCircle2,
  XCircle, AlertTriangle, MessageSquare, Download, Clock, Info,
  UserCheck, ArrowRight, Scale, AlertCircle
} from 'lucide-react';
import StatusBadge from '../../components/ui/StatusBadge';
import AlertBanner from '../../components/ui/AlertBanner';
import ApprovalPanel from '../../components/loan/ApprovalPanel';
import { loanApplications as mockApplications } from '../../data/mockData';
import type { LoanApplication } from '../../types';
import { useRole } from '../../contexts/RoleContext';

const fmt = (n: number) => '₹' + n.toLocaleString('en-IN');

// Rejection reason categories per spec
const REJECTION_REASONS = [
  'Member does not meet active member criteria (4-year supply rule)',
  'KYC documents expired or not verified',
  'Loan amount exceeds eligible limit — exception not approved',
  'Nominee is a minor',
  'Existing default on record — recovery pending',
  'Insufficient land documentation (7/12 missing)',
  'Credit risk rating assessed as Very High',
  'Board Resolution not obtained (FPC)',
  'Member has another active loan — exposure limit exceeded',
  'Other (specify below)',
];

interface SanctionWorkbenchProps {
  onOpenApplication: (id: string) => void;
  initialSelectedId?: string;
  applications?: LoanApplication[];
  onUpdateStatus?: (id: string, newStatus: string) => void;
}

const SanctionWorkbench: React.FC<SanctionWorkbenchProps> = ({ onOpenApplication, initialSelectedId, applications, onUpdateStatus }) => {
  const { can } = useRole();
  const loanApplications = applications ?? mockApplications;
  const sanctionQueue = loanApplications.filter(a =>
    ['pending_sanction_committee_approval', 'pending_sanction', 'under_sanction_review', 'clarification_requested'].includes(a.status)
  );
  const exceptions = loanApplications.filter(a => a.isException);
  const specialCases = loanApplications.filter(a => a.specialCase);

  const initialApp = initialSelectedId ? sanctionQueue.find(a => a.id === initialSelectedId || a.applicationNumber === initialSelectedId) : null;
  const [selected, setSelected] = useState<string | null>(
    initialApp?.id || sanctionQueue[0]?.id || null
  );
  const [slotDecisions, setSlotDecisions] = useState<Record<string, Record<string, { decision: string, reason: string, timestamp: string }>>>({});
  const [abstainReason, setAbstainReason] = useState<Record<string, string>>({});
  const [rejectionCategory, setRejectionCategory] = useState<Record<string, string>>({});
  const [rejectionNote, setRejectionNote] = useState<Record<string, string>>({});
  const [conditionsApplied, setConditionsApplied] = useState<Record<string, string>>({});
  const [reducedAmount, setReducedAmount] = useState<Record<string, string>>({});
  const [sanctionedAmount, setSanctionedAmount] = useState<Record<string, string>>({});
  const [gmApprovalObtained, setGmApprovalObtained] = useState<Record<string, boolean>>({});
  const [conflictDeclared, setConflictDeclared] = useState<Record<string, boolean>>({});

  const { currentUser } = useRole();
  const app = sanctionQueue.find(a => a.id === selected);

  useEffect(() => {
    if (!app || !onUpdateStatus) return;
    const decs = slotDecisions[app.id] || {};
    const cfoApproved = decs['CFO']?.decision === 'approved';
    const reqDirs = app.requestedAmount > 500000 ? 2 : 1;
    const dirDecisions = reqDirs === 2
      ? [decs['Director 1']?.decision, decs['Director 2']?.decision]
      : [decs['Director 1']?.decision];
    const dirsApproved = dirDecisions.every(d => d === 'approved');
    if (cfoApproved && dirsApproved) onUpdateStatus(app.id, 'sanctioned');
  }, [app, onUpdateStatus, slotDecisions]);

  const isDirectorRole = currentUser.role === 'director' || currentUser.role === 'admin';
  const isCFO = currentUser.role === 'cfo' || currentUser.role === 'admin';

  const getDisplayStatus = (a: any) => {
    const decs = slotDecisions[a.id] || {};
    const cfoDecision = decs['CFO']?.decision;
    const reqDirs = a.requestedAmount > 500000 ? 2 : 1;
    const dirDecisions = reqDirs === 2 
      ? [decs['Director 1']?.decision, decs['Director 2']?.decision] 
      : [decs['Director 1']?.decision];

    const cfoApproved = cfoDecision === 'approved';
    const dirsApproved = dirDecisions.every(d => d === 'approved');

    if (cfoApproved && dirsApproved) return 'sanctioned';
    if (cfoApproved) return 'cfo_approved';
    
    return a.status;
  };
  const quorumRequired = app && app.requestedAmount > 500000 ? 3 : 2;

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Sanction Workbench</h1>
          <p className="text-sm text-slate-500 mt-0.5">
            {sanctionQueue.length} pending · {exceptions.length} exception{exceptions.length !== 1 ? 's' : ''} · {specialCases.length} special case{specialCases.length !== 1 ? 's' : ''}
          </p>
        </div>
        <div className="flex gap-2">
          {exceptions.length > 0 && (
            <span className="flex items-center gap-1.5 text-xs bg-violet-100 text-violet-700 border border-violet-200 px-3 py-1.5 rounded-lg font-semibold">
              <AlertOctagon size={12} /> {exceptions.length} Exception{exceptions.length > 1 ? 's' : ''}
            </span>
          )}
          {specialCases.length > 0 && (
            <span className="flex items-center gap-1.5 text-xs bg-amber-100 text-amber-700 border border-amber-200 px-3 py-1.5 rounded-lg font-semibold">
              <Shield size={12} /> {specialCases.length} Special Case{specialCases.length > 1 ? 's' : ''}
            </span>
          )}
        </div>
      </div>

      {exceptions.length > 0 && (
        <AlertBanner
          type="exception"
          title={`${exceptions.length} exception case${exceptions.length > 1 ? 's' : ''} require escalated approval.`}
          message={
            <div className="flex flex-col gap-1 mt-1">
              {exceptions.map(e => (
                <div key={e.id}>
                  • {e.applicationNumber}: {e.requestedAmount > (e.eligibleAmount ?? 0) ? 'Exceeds eligible limit — CFO + 2 Directors + Exception Register.' : 'Above ₹5,00,000 — CFO + 2 Directors.'}
                </div>
              ))}
            </div>
          }
        />
      )}
      {specialCases.length > 0 && (
        <AlertBanner
          type="warning"
          title={`${specialCases.length} special case${specialCases.length > 1 ? 's' : ''} — Director/Relative/Committee Member borrowers`}
          message="Full quorum required. Conflict of interest must be declared before voting. GM approval needed if 2 Directors unavailable."
        />
      )}

      {/* Role guidance */}
      {isDirectorRole && (
        <div className="flex items-center gap-2 bg-blue-50 border border-blue-100 rounded-xl p-3 text-xs text-blue-700">
          <Info size={14} className="flex-shrink-0" />
          <span>You are logged in as a <strong>Director</strong>. For special cases where you have a conflict of interest, click <strong>Abstain</strong> and state the reason.</span>
        </div>
      )}

      {sanctionQueue.length === 0 ? (
        <div className="card text-center py-16">
          <Check size={32} className="text-green-500 mx-auto mb-3" />
          <p className="text-slate-600 font-semibold">Sanction queue is clear</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Queue */}
          <div className="card p-0 overflow-hidden lg:col-span-1">
            <div className="p-4 bg-slate-50 border-b border-slate-200">
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Pending ({sanctionQueue.length})</p>
            </div>
            <div className="divide-y divide-slate-100">
              {sanctionQueue.map(a => (
                <button
                  key={a.id}
                  onClick={() => setSelected(a.id)}
                  className={`w-full flex items-center gap-3 p-4 hover:bg-slate-50 transition-colors text-left ${selected === a.id ? 'bg-green-50 border-l-4 border-l-green-500' : ''}`}
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-slate-900 num text-sm">{a.applicationNumber}</span>
                      {a.isException && <AlertOctagon size={12} className="text-violet-600" />}
                      {a.specialCase && <Shield size={12} className="text-amber-600" />}
                    </div>
                    <div className="text-xs text-slate-500 truncate">{a.memberName}</div>
                    <div className="text-xs text-slate-400 num">{fmt(a.requestedAmount)} · {a.requestedAmount <= 500000 ? 'CFO+1Dir' : 'CFO+2Dir'}</div>
                  </div>
                  {getDisplayStatus(a) === 'cfo_approved' ? (
                    <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-amber-50 text-amber-700 whitespace-nowrap">
                      CFO approved · Director pending
                    </span>
                  ) : (
                    <StatusBadge label={getDisplayStatus(a)} size="sm" />
                  )}
                </button>
              ))}
            </div>
          </div>

          {/* Detail */}
          {app && (
            <div className="lg:col-span-2 space-y-4">
              {/* Header */}
              <div className="card">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <div className="flex items-center gap-2 flex-wrap">
                      <h2 className="text-lg font-bold text-slate-900 num">{app.applicationNumber}</h2>
                      {getDisplayStatus(app) === 'cfo_approved' ? (
                        <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-amber-50 text-amber-700 whitespace-nowrap">
                          CFO approved · Director approval pending
                        </span>
                      ) : (
                        <StatusBadge label={getDisplayStatus(app)} />
                      )}
                      {app.isException && <span className="text-xs bg-violet-100 text-violet-700 px-2 py-0.5 rounded font-semibold">Exception</span>}
                      {app.specialCase && <span className="text-xs bg-amber-100 text-amber-700 px-2 py-0.5 rounded font-semibold">Special Case</span>}
                    </div>
                    <p className="text-sm text-slate-500">{app.memberName} · {fmt(app.requestedAmount)}</p>
                  </div>
                  <button onClick={() => onOpenApplication(app.id)} className="btn-secondary flex items-center gap-2 flex-shrink-0">
                    <FileText size={14} /> Full Application
                  </button>
                </div>

                <div className="grid grid-cols-3 gap-3">
                  <div className="bg-slate-50 rounded-lg p-3">
                    <p className="text-xs text-slate-500">Requested</p>
                    <p className="text-base font-bold num text-slate-900">{fmt(app.requestedAmount)}</p>
                  </div>
                  <div className="bg-slate-50 rounded-lg p-3">
                    <p className="text-xs text-slate-500">Eligible</p>
                    <p className="text-base font-bold num text-slate-900">{fmt(app.eligibleAmount ?? 0)}</p>
                  </div>
                  <div className={`rounded-lg p-3 ${(app.riskRating as string) === 'high' ? 'bg-red-50' : app.riskRating === 'medium' ? 'bg-amber-50' : 'bg-green-50'}`}>
                    <p className="text-xs text-slate-500">Risk Rating</p>
                    <p className={`text-base font-bold capitalize ${(app.riskRating as string) === 'high' ? 'text-red-900' : app.riskRating === 'medium' ? 'text-amber-900' : 'text-green-900'}`}>
                      {app.riskRating || '—'}
                    </p>
                  </div>
                </div>

                {app.isException && (
                  <div className="mt-3">
                    <AlertBanner type="exception" title="Exception — Amount exceeds eligible limit" message={app.exceptionReason || ''} />
                    {(app.riskRating as string) === 'high' && (
                      <AlertBanner type="warning" title="High Risk" message="This application is marked as high risk by Credit Manager." />
                    )}
                  </div>
                )}
              </div>

              {/* Special Case Panel (S24) */}
              {app.specialCase && (
                <div className="card border-2 border-amber-300 bg-amber-50">
                  <div className="flex items-start gap-3">
                    <Shield size={20} className="text-amber-600 flex-shrink-0 mt-0.5" />
                    <div className="flex-1">
                      <h4 className="font-semibold text-amber-900 mb-3">Special Case Requirements — Full Quorum Required</h4>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-4">
                        {[
                          { label: 'Case Type', value: 'Director / Relative / Committee Member' },
                          { label: 'Required Quorum', value: '3 of 3 (CFO + 2 Directors)' },
                          { label: 'Conflict Declaration', value: 'Mandatory before voting' },
                          { label: 'GM Approval Fallback', value: 'Required if 2 Directors absent' },
                        ].map(({ label, value }) => (
                          <div key={label} className="bg-white/60 rounded-lg p-2.5">
                            <p className="text-xs text-amber-700">{label}</p>
                            <p className="text-sm font-semibold text-amber-900">{value}</p>
                          </div>
                        ))}
                      </div>

                      {/* Pre-conditions */}
                      <div className="space-y-2 mb-3">
                        <label className="flex items-center gap-2 text-sm text-amber-800 cursor-pointer">
                          <input
                            type="checkbox"
                            checked={conflictDeclared[app.id] || false}
                            onChange={e => setConflictDeclared(p => ({ ...p, [app.id]: e.target.checked }))}
                            className="w-4 h-4 accent-amber-600"
                          />
                          Conflict of interest declared by relevant committee member(s)
                        </label>
                        <label className="flex items-center gap-2 text-sm text-amber-800 cursor-pointer">
                          <input
                            type="checkbox"
                            checked={gmApprovalObtained[app.id] || false}
                            onChange={e => setGmApprovalObtained(p => ({ ...p, [app.id]: e.target.checked }))}
                            className="w-4 h-4 accent-amber-600"
                          />
                          GM approval obtained (required if 2 Directors not available)
                        </label>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Sanction Decision Panel */}
              <div className="card">
                <h3 className="text-sm font-semibold text-slate-700 mb-1 flex items-center gap-2">
                  <Gavel size={14} /> Sanction Committee Decision
                </h3>
                <p className="text-xs text-slate-400 mb-4">
                  Quorum: {quorumRequired === 3 ? 'CFO + 2 Directors (amount > ₹5 lakh)' : 'CFO + 1 Director (amount ≤ ₹5 lakh)'}
                </p>

                {/* Compact Pre-checks */}
                <div className="border-t border-slate-100 pt-4 mt-4 mb-4">
                  <p className="text-xs text-slate-500 mb-2 font-medium uppercase tracking-wide">Pre-Sanction Checks</p>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-2">
                    {[
                      'Eligibility verified',
                      'Requested amount within eligible limit',
                      'Loan purpose: agriculture / crop production',
                      'Risk assessment reviewed',
                      'Past borrowing/default reviewed',
                      'Compliance checks reviewed',
                      'Documentation readiness reviewed',
                      'Approval authority confirmed',
                      'Exception flag reviewed',
                      'Conflict / related-party flag reviewed',
                    ].map(check => (
                      <div key={check} className="flex items-center gap-2 text-sm text-slate-700">
                        <CheckCircle2 size={14} className="text-green-500 flex-shrink-0" />
                        <span className="truncate" title={check}>{check}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <ApprovalPanel
                  applicationNumber={app.applicationNumber}
                  requestedAmount={app.requestedAmount}
                  eligibleAmount={app.eligibleAmount}
                  isException={app.isException}
                  isSpecialCase={app.specialCase}
                  approvers={[
                    { role: 'CFO', name: 'Suresh Nair' },
                    { role: 'Director 1', name: 'Anita Desai' },
                    ...(app.requestedAmount > 500000 ? [{ role: 'Director 2', name: 'Prakash Joshi' }] : []),
                  ].map(a => ({
                    ...a,
                    decision: slotDecisions[app.id]?.[a.role]?.decision as any || 'pending',
                    reason: slotDecisions[app.id]?.[a.role]?.reason || '',
                    timestamp: slotDecisions[app.id]?.[a.role]?.timestamp || '',
                    evidence: slotDecisions[app.id]?.[a.role]?.decision ? true : false,
                  }))}
                  onDecision={(d, reason, slotRole) => {
                    if (!slotRole) return;
                    setSlotDecisions(prev => ({
                      ...prev,
                      [app.id]: {
                        ...(prev[app.id] || {}),
                        [slotRole]: { decision: d, reason, timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }
                      }
                    }));
                  }}
                />
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default SanctionWorkbench;
