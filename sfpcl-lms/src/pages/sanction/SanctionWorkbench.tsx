import React, { useState } from 'react';
import {
  Gavel, ChevronRight, Check, AlertOctagon, Shield, CheckCircle2,
  XCircle, AlertTriangle, MessageSquare, Download, Clock, Info,
  UserCheck, ArrowRight, Scale
} from 'lucide-react';
import StatusBadge from '../../components/ui/StatusBadge';
import AlertBanner from '../../components/ui/AlertBanner';
import ApprovalPanel from '../../components/loan/ApprovalPanel';
import { loanApplications } from '../../data/mockData';
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
}

const SanctionWorkbench: React.FC<SanctionWorkbenchProps> = ({ onOpenApplication }) => {
  const sanctionQueue = loanApplications.filter(a =>
    a.status === 'pending_sanction' || a.status === 'credit_review'
  );
  const exceptions = loanApplications.filter(a => a.isException);
  const specialCases = loanApplications.filter(a => a.specialCase);

  const [selected, setSelected] = useState<string | null>(sanctionQueue[0]?.id || null);
  const [sanctionDecision, setSanctionDecision] = useState<Record<string, 'approved' | 'rejected' | 'abstained' | null>>({});
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

  const isDirectorRole = currentUser.role === 'director';
  const isCFO = currentUser.role === 'cfo';
  const decision = selected ? sanctionDecision[selected] : null;
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
          title={`${exceptions.length} exception case${exceptions.length > 1 ? 's' : ''} require CFO + Director approval`}
          message={exceptions.map(e => `${e.applicationNumber}: ${e.exceptionReason}`).join(' | ')}
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
                  <StatusBadge label={a.status} size="sm" />
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
                      <StatusBadge label={app.status} />
                      {app.isException && <span className="text-xs bg-violet-100 text-violet-700 px-2 py-0.5 rounded font-semibold">Exception</span>}
                      {app.specialCase && <span className="text-xs bg-amber-100 text-amber-700 px-2 py-0.5 rounded font-semibold">Special Case</span>}
                    </div>
                    <p className="text-sm text-slate-500">{app.memberName} · {fmt(app.requestedAmount)}</p>
                  </div>
                  <button onClick={() => onOpenApplication(app.id)} className="text-xs text-green-600 hover:underline flex items-center gap-1">
                    Full view <ChevronRight size={12} />
                  </button>
                </div>

                <div className="grid grid-cols-3 gap-3">
                  <div className="bg-slate-50 rounded-lg p-3">
                    <p className="text-xs text-slate-500">Requested</p>
                    <p className="text-base font-bold num text-slate-900">{fmt(app.requestedAmount)}</p>
                  </div>
                  <div className="bg-slate-50 rounded-lg p-3">
                    <p className="text-xs text-slate-500">Eligible</p>
                    <p className="text-base font-bold num text-slate-900">{fmt(app.eligibleAmount)}</p>
                  </div>
                  <div className={`rounded-lg p-3 ${app.riskRating === 'high' || app.riskRating === 'very_high' ? 'bg-red-50' : app.riskRating === 'medium' ? 'bg-amber-50' : 'bg-green-50'}`}>
                    <p className="text-xs text-slate-500">Risk Rating</p>
                    <p className={`text-base font-bold capitalize ${app.riskRating === 'high' || app.riskRating === 'very_high' ? 'text-red-900' : app.riskRating === 'medium' ? 'text-amber-900' : 'text-green-900'}`}>
                      {app.riskRating || '—'}
                    </p>
                  </div>
                </div>

                {app.isException && (
                  <div className="mt-3">
                    <AlertBanner type="exception" title="Exception — Amount exceeds eligible limit" message={app.exceptionReason || ''} />
                  </div>
                )}
              </div>

              {/* Special Case Panel (S24) */}
              {app.specialCase && (
                <div className="card border-2 border-amber-300 bg-amber-50">
                  <div className="flex items-start gap-3">
                    <Shield size={20} className="text-amber-600 flex-shrink-0 mt-0.5" />
                    <div className="flex-1">
                      <h4 className="font-semibold text-amber-900 mb-3">Special Case Requirements (S24) — Full Quorum Required</h4>
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

                <ApprovalPanel
                  applicationNumber={app.applicationNumber}
                  requestedAmount={app.requestedAmount}
                  isException={app.isException}
                  isSpecialCase={app.specialCase}
                  approvers={[
                    { role: 'CFO', name: 'Suresh Nair', decision: 'pending' },
                    { role: 'Director 1', name: 'Anita Desai', decision: 'pending' },
                    ...(app.requestedAmount > 500000 ? [{ role: 'Director 2', name: 'Prakash Joshi', decision: 'pending' as const }] : []),
                  ]}
                  onDecision={(d, reason) => {
                    setSanctionDecision(p => ({ ...p, [app.id]: d as any }));
                  }}
                />

                {/* Decision action buttons */}
                {!decision && (
                  <div className="border-t border-slate-100 pt-4 mt-4">
                    <p className="text-xs text-slate-500 mb-3 font-medium uppercase tracking-wide">Your Decision</p>

                    {/* Reduced amount option */}
                    <div className="mb-4 space-y-2">
                      <label className="flex items-center gap-2 text-sm text-slate-700 cursor-pointer">
                        <input type="checkbox"
                          checked={!!reducedAmount[app.id]}
                          onChange={e => {
                            if (!e.target.checked) setReducedAmount(p => ({ ...p, [app.id]: '' }));
                            else setReducedAmount(p => ({ ...p, [app.id]: String(app.eligibleAmount) }));
                          }}
                          className="w-4 h-4 accent-green-600"
                        />
                        Approve at reduced amount (partial sanction)
                      </label>
                      {reducedAmount[app.id] !== undefined && reducedAmount[app.id] !== '' && (
                        <div className="ml-6 flex items-center gap-2">
                          <span className="text-sm text-slate-600">Sanction amount:</span>
                          <input
                            type="number"
                            value={sanctionedAmount[app.id] || ''}
                            onChange={e => setSanctionedAmount(p => ({ ...p, [app.id]: e.target.value }))}
                            placeholder={String(app.eligibleAmount)}
                            className="field-input text-sm w-36 py-1"
                          />
                        </div>
                      )}
                      <div>
                        <label className="block text-xs text-slate-500 mb-1">Conditions (if any)</label>
                        <input
                          type="text"
                          value={conditionsApplied[app.id] || ''}
                          onChange={e => setConditionsApplied(p => ({ ...p, [app.id]: e.target.value }))}
                          placeholder="e.g. Subject to CDSL pledge completion within 7 days…"
                          className="field-input text-sm py-1.5 w-full"
                        />
                      </div>
                    </div>

                    <div className="flex gap-3 flex-wrap">
                      {/* Approve */}
                      <button
                        onClick={() => setSanctionDecision(p => ({ ...p, [app.id]: 'approved' }))}
                        className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white text-sm px-4 py-2.5 rounded-xl font-semibold transition-colors"
                      >
                        <CheckCircle2 size={16} /> Approve
                      </button>

                      {/* Reject — requires reason */}
                      <button
                        onClick={() => setSanctionDecision(p => ({ ...p, [app.id]: 'rejected' }))}
                        className="flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white text-sm px-4 py-2.5 rounded-xl font-semibold transition-colors"
                      >
                        <XCircle size={16} /> Reject
                      </button>

                      {/* Abstain — Director only, conflict of interest */}
                      <button
                        onClick={() => setSanctionDecision(p => ({ ...p, [app.id]: 'abstained' }))}
                        className="flex items-center gap-2 bg-slate-400 hover:bg-slate-500 text-white text-sm px-4 py-2.5 rounded-xl font-semibold transition-colors"
                        title="For Directors with conflict of interest"
                      >
                        <Scale size={16} /> Abstain (Conflict of Interest)
                      </button>
                    </div>
                  </div>
                )}

                {/* Rejection reason form */}
                {decision === 'rejected' && (
                  <div className="border-t border-slate-100 pt-4 mt-4 space-y-3">
                    <div className="flex items-center gap-2 bg-red-50 border border-red-200 rounded-xl p-3">
                      <XCircle size={16} className="text-red-600 flex-shrink-0" />
                      <p className="text-sm font-semibold text-red-800">Rejection Reason — Required</p>
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-slate-600 mb-1.5">Reason Category</label>
                      <select
                        value={rejectionCategory[app.id] || ''}
                        onChange={e => setRejectionCategory(p => ({ ...p, [app.id]: e.target.value }))}
                        className="field-select text-sm py-2 w-full"
                      >
                        <option value="">Select a reason…</option>
                        {REJECTION_REASONS.map(r => <option key={r} value={r}>{r}</option>)}
                      </select>
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-slate-600 mb-1.5">Detailed Note (required)</label>
                      <textarea
                        rows={3}
                        value={rejectionNote[app.id] || ''}
                        onChange={e => setRejectionNote(p => ({ ...p, [app.id]: e.target.value }))}
                        placeholder="Provide detailed reason for rejection. This will be included in the rejection letter to the borrower."
                        className="field-input text-sm resize-none w-full"
                      />
                    </div>
                    <div className="flex gap-3">
                      <button
                        disabled={!rejectionCategory[app.id] || !rejectionNote[app.id]?.trim()}
                        className="btn-danger text-sm px-4 py-2 disabled:opacity-50"
                      >
                        Confirm Rejection & Generate Rejection Note
                      </button>
                      <button
                        onClick={() => setSanctionDecision(p => ({ ...p, [app.id]: null }))}
                        className="btn-secondary text-sm"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                )}

                {/* Abstain reason */}
                {decision === 'abstained' && (
                  <div className="border-t border-slate-100 pt-4 mt-4 space-y-3">
                    <div className="flex items-center gap-2 bg-slate-50 border border-slate-200 rounded-xl p-3">
                      <Scale size={16} className="text-slate-500 flex-shrink-0" />
                      <p className="text-sm font-semibold text-slate-700">Abstention Recorded — Conflict of Interest</p>
                    </div>
                    <textarea
                      rows={2}
                      value={abstainReason[app.id] || ''}
                      onChange={e => setAbstainReason(p => ({ ...p, [app.id]: e.target.value }))}
                      placeholder="State the nature of the conflict of interest (e.g., Director is a relative of the borrower)…"
                      className="field-input text-sm resize-none w-full"
                    />
                    <div className="flex gap-3">
                      <button className="btn-secondary text-sm px-4 py-2">Confirm Abstention</button>
                      <button onClick={() => setSanctionDecision(p => ({ ...p, [app.id]: null }))} className="btn-secondary text-sm">Cancel</button>
                    </div>
                  </div>
                )}

                {/* Approved confirmation */}
                {decision === 'approved' && (
                  <div className="border-t border-slate-100 pt-4 mt-4">
                    <div className="flex items-center gap-3 bg-green-50 border border-green-200 rounded-xl p-4">
                      <CheckCircle2 size={20} className="text-green-600 flex-shrink-0" />
                      <div className="flex-1">
                        <p className="text-sm font-semibold text-green-800">Application Approved</p>
                        <p className="text-xs text-green-700 mt-0.5">
                          Sanctioned amount: {sanctionedAmount[app.id] ? fmt(Number(sanctionedAmount[app.id])) : fmt(app.requestedAmount)}
                          {conditionsApplied[app.id] && ` · Conditions: ${conditionsApplied[app.id]}`}
                        </p>
                      </div>
                      <div className="flex gap-2">
                        <button className="flex items-center gap-1 text-xs bg-green-600 hover:bg-green-700 text-white px-3 py-1.5 rounded-lg">
                          <Download size={12} /> Sanction Letter
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default SanctionWorkbench;
