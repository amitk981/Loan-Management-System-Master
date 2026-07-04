import React, { useState, useEffect } from 'react';
import { Banknote, ChevronRight, Check, AlertTriangle, ShieldCheck, Download, FileText, Upload, Lock, RotateCcw, XCircle, Send, CheckCircle2 } from 'lucide-react';
import StatusBadge from '../../components/ui/StatusBadge';
import AlertBanner from '../../components/ui/AlertBanner';
import { loanApplications, members } from '../../data/mockData';
import { useRole } from '../../contexts/RoleContext';

const fmt = (n: number) => '₹' + n.toLocaleString('en-IN');

interface PaymentAuthorisationHubProps {
  onOpenApplication: (id: string) => void;
  initialSelectedId?: string;
}

type AuthStage = 'cfc_pending' | 'completed';

const STAGE_LABELS: Record<AuthStage, string> = {
  cfc_pending: 'Payment Initiated',
  completed: 'Transfer Executed',
};

const isTransferExecuted = (app: { status: string; disbursementStatus: string }) =>
  ['completed', 'disbursed', 'transfer_executed'].includes(app.disbursementStatus) ||
  ['disbursed', 'transfer_executed'].includes(app.status);

const getAuthorisationStatus = (app: { status: string; disbursementStatus: string }, stage?: AuthStage) => {
  if (stage === 'completed' || isTransferExecuted(app)) return 'transfer_executed';
  if (app.status === 'payment_authorized' || app.disbursementStatus === 'payment_authorized') return 'payment_authorized';
  return 'payment_initiated';
};

const PaymentAuthorisationHub: React.FC<PaymentAuthorisationHubProps> = ({ onOpenApplication, initialSelectedId }) => {
  const cfcQueue = loanApplications.filter(a =>
    ['pending_cfc_approval', 'payment_authorized', 'transfer_executed', 'completed', 'disbursed'].includes(a.disbursementStatus) ||
    ['payment_initiated', 'payment_authorized', 'transfer_executed', 'disbursed'].includes(a.status)
  );
  
  const initialApp = initialSelectedId ? cfcQueue.find(a => a.id === initialSelectedId || a.applicationNumber === initialSelectedId) : null;
  const [selected, setSelected] = useState<string | null>(
    initialApp?.id || cfcQueue.find(a => a.disbursementStatus === 'pending_cfc_approval' || a.status === 'payment_initiated')?.id || cfcQueue[0]?.id || null
  );

  const { currentUser, can } = useRole();
  const isAdmin = currentUser.role === 'admin';
  const isCfc = currentUser.role === 'cfc' || isAdmin;

  const app = cfcQueue.find(a => a.id === selected);
  const member = app ? members.find(m => m.id === app.memberId) : null;

  // CFC State
  const [stage, setStage] = useState<AuthStage>('cfc_pending');
  const [cfcComment, setCfcComment] = useState('');
  const [utrReference, setUtrReference] = useState('');
  const [cfcBankEvidence, setCfcBankEvidence] = useState(false);

  useEffect(() => {
    if (app) {
      if (isTransferExecuted(app)) {
        setStage('completed');
        setUtrReference('UTR202606241234'); // dummy
        setCfcBankEvidence(true);
      } else {
        setStage('cfc_pending');
        setCfcComment('');
        setUtrReference('');
        setCfcBankEvidence(false);
      }
    }
  }, [app]);

  const auditLog = (action: string, reason?: string) => {
    console.log({
      action,
      actor: currentUser.role,
      time: new Date().toISOString(),
      app_id: app?.id,
      reason,
    });
  };

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Payment Authorisation Queue</h1>
          <p className="text-sm text-slate-500 mt-0.5">Payment requests awaiting CFC action</p>
        </div>
      </div>

      {cfcQueue.length === 0 ? (
        <div className="card text-center py-8">
          <Check size={32} className="text-green-500 mx-auto mb-3" />
          <p className="text-slate-600 font-semibold">No payment requests pending authorisation</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Queue */}
          <div className="card p-0 overflow-hidden lg:col-span-1 h-[calc(100vh-160px)] overflow-y-auto">
            <div className="p-4 bg-slate-50 border-b border-slate-200">
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide">CFC Authorisation Queue ({cfcQueue.length})</p>
            </div>
            <div className="divide-y divide-slate-100">
              {cfcQueue.map(a => (
                <button
                  key={a.id}
                  onClick={() => setSelected(a.id)}
                  className={`w-full flex items-center gap-3 p-4 hover:bg-slate-50 transition-colors text-left ${selected === a.id ? 'bg-green-50 border-l-4 border-l-green-500' : ''}`}
                >
                  <ShieldCheck size={16} className={`${isTransferExecuted(a) ? 'text-green-600' : 'text-amber-600'} flex-shrink-0`} />
                  <div className="flex-1 min-w-0">
                    <div className="font-semibold text-slate-900 num text-sm">{a.applicationNumber}</div>
                    <div className="text-xs text-slate-500 truncate">{a.memberName}</div>
                    <div className="text-xs text-green-700 num font-medium">{fmt(a.requestedAmount)}</div>
                  </div>
                  <StatusBadge label={getAuthorisationStatus(a)} size="sm" />
                </button>
              ))}
            </div>
          </div>

          {/* Detail */}
          {app ? (
            <div className="lg:col-span-2 space-y-4">
              <div className="card">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <div className="flex items-center gap-2">
                      <h2 className="text-lg font-bold text-slate-900 num">{app.applicationNumber}</h2>
                      <StatusBadge label={getAuthorisationStatus(app, stage)} size="sm" />
                    </div>
                    <p className="text-sm text-slate-500">{app.memberName} · {fmt(app.requestedAmount)}</p>
                  </div>
                  <button onClick={() => onOpenApplication(app.id)} className="btn-secondary flex items-center gap-2 flex-shrink-0">
                    <FileText size={14} /> Full Application
                  </button>
                </div>

                <div className="grid grid-cols-2 gap-2 mb-4 max-w-sm">
                  {(Object.entries(STAGE_LABELS) as Array<[AuthStage, string]>).map(([s, label]) => (
                    <div
                      key={s}
                      className={`rounded-lg p-2 text-center text-xs font-medium ${
                        stage === s ? 'bg-green-100 text-green-700 border border-green-300' :
                        (Object.keys(STAGE_LABELS).indexOf(s) < Object.keys(STAGE_LABELS).indexOf(stage))
                          ? 'bg-green-50 text-green-600' : 'bg-slate-50 text-slate-400'
                      }`}
                    >
                      {label}
                    </div>
                  ))}
                </div>
              </div>

              {/* CFC Authorisation panel */}
              {(stage === 'cfc_pending' || stage === 'completed') && (
                <div className="card">
                  <h3 className="text-sm font-semibold text-slate-700 mb-3 flex items-center gap-2">
                    <ShieldCheck size={14} /> CFC Authorisation
                  </h3>
                  {stage === 'completed' ? (
                    <div className="flex flex-col gap-3">
                      <div className="flex items-center gap-2 text-green-700 bg-green-50 rounded-lg p-3 text-sm">
                        <Check size={16} /> Payment authorised and released successfully.
                      </div>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm mt-2">
                         <div><p className="text-xs text-slate-500">UTR / Bank Ref</p><p className="font-medium font-mono">{utrReference}</p></div>
                         <div><p className="text-xs text-slate-500">Bank Confirmation Attachment</p><p className="font-medium text-blue-600 hover:underline cursor-pointer">confirmation_pdf</p></div>
                      </div>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
                        <div><p className="text-xs text-slate-500">Payment Request ID</p><p className="font-medium">REQ-2948</p></div>
                        <div><p className="text-xs text-slate-500">Borrower</p><p className="font-medium">{app.memberName}</p></div>
                        <div><p className="text-xs text-slate-500">Application Reference</p><p className="font-medium">{app.applicationNumber}</p></div>
                        <div><p className="text-xs text-slate-500">Amount</p><p className="font-medium">{fmt(app.requestedAmount)}</p></div>
                        <div><p className="text-xs text-slate-500">Masked Bank Details</p><p className="font-medium">XXXX1234 / SBIN0001234</p></div>
                        <div><p className="text-xs text-slate-500">Initiated By</p><p className="font-medium">Senior Manager</p></div>
                        <div><p className="text-xs text-slate-500">Initiated Date</p><p className="font-medium">{new Date().toLocaleDateString('en-IN')}</p></div>
                        <div><p className="text-xs text-slate-500">Readiness Status</p><p className="font-medium text-green-600">All Gates Cleared</p></div>
                        <div className="col-span-2"><p className="text-xs text-slate-500">Supporting Documents</p><p className="font-medium text-blue-600 hover:underline cursor-pointer">View Package</p></div>
                      </div>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <div>
                          <label className="field-label">UTR / Bank Reference (Required for Auth)</label>
                          <input type="text" value={utrReference} onChange={e => setUtrReference(e.target.value.toUpperCase())} className="field-input" placeholder="e.g. UTR202606241234" />
                        </div>
                        <div>
                          <label className="field-label">Bank Confirmation Attachment</label>
                          <button onClick={() => setCfcBankEvidence(true)} className={`w-full flex items-center justify-center gap-2 border rounded-lg px-4 py-2.5 text-sm font-medium transition-colors ${cfcBankEvidence ? 'border-green-200 bg-green-50 text-green-700' : 'border-slate-200 bg-white text-slate-700 hover:bg-slate-50'}`}>
                            {cfcBankEvidence ? <Check size={14} /> : <Upload size={14} />} {cfcBankEvidence ? 'Evidence Uploaded' : 'Upload Bank Confirmation'}
                          </button>
                        </div>
                        <div className="sm:col-span-2">
                          <label className="field-label">Comment</label>
                          <input type="text" value={cfcComment} onChange={e => setCfcComment(e.target.value)} className="field-input" placeholder="Mandatory for return or reject..." />
                        </div>
                      </div>
                      <div className="flex flex-wrap gap-3">
                        {isCfc ? (
                          <>
                            <button className="btn-primary text-sm flex-[2]" disabled={!utrReference || !cfcBankEvidence} onClick={() => { setStage('completed'); auditLog('AUTHORISED_TRANSFER', utrReference); }}>Approve and mark transferred</button>
                            <button className="btn-secondary text-sm flex-1" disabled={!cfcComment} onClick={() => auditLog('RETURNED_TO_SM_FINANCE', cfcComment)}>Return to Senior Manager</button>
                            <button className="bg-red-600 hover:bg-red-700 text-white font-medium px-4 py-2 rounded-lg text-sm flex-1 disabled:opacity-50" disabled={!cfcComment} onClick={() => auditLog('REJECTED_PAYMENT', cfcComment)}>Reject payment request</button>
                          </>
                        ) : (
                          <div className="w-full bg-slate-50 border border-slate-200 text-slate-500 text-sm px-4 py-2.5 rounded-lg flex items-center gap-2">
                            <Lock size={14} /> CFC Authorisation required
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* 6. Disbursed panel */}
              {stage === 'completed' && (
                <div className="card">
                  <h3 className="text-sm font-semibold text-slate-700 mb-3 flex items-center gap-2">
                    <FileText size={14} /> Post-Disbursement & Borrower Advice
                  </h3>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm mb-4">
                    <div><p className="text-xs text-slate-500">Loan Account Number</p><p className="font-medium">L-003294</p></div>
                    <div><p className="text-xs text-slate-500">Disbursed Amount</p><p className="font-medium">{fmt(app.requestedAmount)}</p></div>
                    <div><p className="text-xs text-slate-500">Disbursement Date</p><p className="font-medium">{new Date().toLocaleDateString('en-IN')}</p></div>
                    <div><p className="text-xs text-slate-500">Borrower Communication Mode</p><p className="font-medium">Email + SMS</p></div>
                    <div><p className="text-xs text-slate-500">UTR / Bank Reference</p><p className="font-medium font-mono">{utrReference}</p></div>
                    <div><p className="text-xs text-slate-500">Bank Evidence</p><p className="font-medium text-blue-600 hover:underline cursor-pointer">confirmation_pdf</p></div>
                    <div><p className="text-xs text-slate-500">Disbursement Advice Status</p><p className="font-medium text-amber-600">Pending Generation</p></div>
                  </div>
                  <div className="space-y-2 mb-4">
                     {[
                       'Loan register updated',
                       'Monitoring schedule started',
                       'Senior Manager post-disbursement checklist signature'
                     ].map(item => (
                       <div key={item} className="flex items-center gap-2 text-sm text-slate-700">
                         <CheckCircle2 size={14} className="text-green-600" /> {item}
                       </div>
                     ))}
                  </div>
                  <div className="flex gap-3 flex-wrap">
                    <button className="btn-primary text-sm flex items-center gap-2 flex-[2] justify-center" onClick={() => auditLog('GENERATED_ADVICE')}><FileText size={14}/> Generate disbursement advice</button>
                    <button className="btn-secondary text-sm flex items-center gap-2 flex-1 justify-center" onClick={() => auditLog('DOWNLOAD_ADVICE')}><Download size={14}/> Download PDF</button>
                    <button className="btn-secondary text-sm flex items-center gap-2 flex-1 justify-center" onClick={() => auditLog('SENT_EMAIL')}><Send size={14}/> Send Email</button>
                    <button className="btn-secondary text-sm flex items-center gap-2 flex-1 justify-center" onClick={() => auditLog('SENT_SMS_SUMMARY')}><Send size={14}/> Send SMS summary</button>
                    <button className="btn-secondary text-sm flex items-center gap-2 flex-1 justify-center" onClick={() => auditLog('MARKED_HARD_COPY')}><Check size={14}/> Mark hard copy dispatched</button>
                  </div>
                </div>
              )}

            </div>
          ) : (
            <div className="lg:col-span-2 space-y-4">
               <div className="card text-center py-8">
                  <p className="text-slate-600 font-semibold">Select a payment request from the queue.</p>
               </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default PaymentAuthorisationHub;
