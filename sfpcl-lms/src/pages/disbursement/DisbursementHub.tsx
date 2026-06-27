import React, { useState, useEffect } from 'react';
import { Banknote, ChevronRight, Check, AlertTriangle, Building2, ShieldCheck, Download, FileText, Upload, Lock, RotateCcw, XCircle, Send, CheckCircle2 } from 'lucide-react';
import StatusBadge from '../../components/ui/StatusBadge';
import AlertBanner from '../../components/ui/AlertBanner';
import { loanApplications, members } from '../../data/mockData';
import { useRole } from '../../contexts/RoleContext';

const fmt = (n: number) => '₹' + n.toLocaleString('en-IN');

interface DisbursementHubProps {
  onOpenApplication: (id: string) => void;
  initialSelectedId?: string;
}

type DisbStage = 'sap_pending' | 'bank_verify' | 'ready' | 'initiated';

const STAGE_LABELS: Record<DisbStage, string> = {
  sap_pending: 'SAP Pending',
  bank_verify: 'SAP Confirmed',
  ready: 'Disbursement Ready',
  initiated: 'Payment Initiated',
};

const statusForStage = (stage: DisbStage) => {
  switch (stage) {
    case 'sap_pending': return 'sap_customer_code_pending';
    case 'bank_verify': return 'sap_customer_code_confirmed';
    case 'ready': return 'disbursement_ready';
    case 'initiated': return 'payment_initiated';
    default: return 'sap_customer_code_pending';
  }
};

const getDisbursementStatus = (app: { status: string; disbursementStatus: string; sapCustomerCode?: string }, selectedStage?: DisbStage) => {
  if (selectedStage) return statusForStage(selectedStage);
  if (['payment_initiated', 'payment_authorized', 'transfer_executed', 'disbursed'].includes(app.status)) return app.status;
  if (['payment_initiated', 'payment_authorized', 'transfer_executed', 'disbursed'].includes(app.disbursementStatus)) return app.disbursementStatus;
  if (app.status === 'disbursement_ready' || app.disbursementStatus === 'disbursement_ready' || app.disbursementStatus === 'ready_for_payment') return 'disbursement_ready';
  if (app.status === 'sap_customer_code_confirmed' || app.disbursementStatus === 'sap_customer_code_confirmed' || app.sapCustomerCode) return 'sap_customer_code_confirmed';
  return 'sap_customer_code_pending';
};

const DisbursementHub: React.FC<DisbursementHubProps> = ({ onOpenApplication, initialSelectedId }) => {
  const allSMQueue = loanApplications.filter(a =>
    ['sanctioned', 'disbursement_ready', 'sap_customer_code_pending', 'sap_customer_code_confirmed', 'payment_initiated'].includes(a.status) &&
    a.documentationStatus === 'complete' && 
    !['completed', 'disbursed', 'pending_cfc_approval', 'payment_authorized', 'transfer_executed'].includes(a.disbursementStatus)
  );
  
  const initialApp = initialSelectedId ? allSMQueue.find(a => a.id === initialSelectedId || a.applicationNumber === initialSelectedId) : null;
  const [selected, setSelected] = useState<string | null>(
    initialApp?.id || allSMQueue[0]?.id || null
  );

  const { currentUser, can } = useRole();
  const isAdmin = currentUser.role === 'admin';
  const isSeniorManager = currentUser.role === 'senior_manager_finance' || isAdmin;

  // State
  const [stage, setStage] = useState<DisbStage>('sap_pending');
  
  // SAP State
  const [sapConfirmed, setSapConfirmed] = useState(false);
  const [sapCodeInput, setSapCodeInput] = useState('');
  const [sapComments, setSapComments] = useState('');
  
  // Bank Verify State
  const [bankVerified, setBankVerified] = useState(false);
  const [bankComments, setBankComments] = useState('');
  
  // Ready State
  const [readyForPayment, setReadyForPayment] = useState(false);
  const [readinessChecks, setReadinessChecks] = useState<Record<string, boolean>>({});
  
  // Payment Initiation State
  const [paymentMode, setPaymentMode] = useState('RTGS');
  const [paymentNarration, setPaymentNarration] = useState('');
  const [sfpclAccount, setSfpclAccount] = useState('RBL Bank - 100029384756');

  const app = allSMQueue.find(a => a.id === selected);
  const member = app ? members.find(m => m.id === app.memberId) : null;

  useEffect(() => {
    if (app) {
      if (app.status === 'payment_initiated' || app.disbursementStatus === 'payment_initiated') {
        setStage('initiated');
        setSapConfirmed(true);
        setSapCodeInput(app.sapCustomerCode || 'SAP-240039');
      } else if (app.status === 'disbursement_ready' || app.disbursementStatus === 'disbursement_ready' || app.disbursementStatus === 'ready_for_payment') {
        setStage('ready');
        setSapConfirmed(true);
        setSapCodeInput(app.sapCustomerCode || 'SAP-240039');
      } else if (app.sapCustomerCode || app.status === 'sap_customer_code_confirmed' || app.disbursementStatus === 'sap_customer_code_confirmed' || app.id === 'l003' || app.id === 'app005') { 
        setStage('bank_verify');
        setSapConfirmed(true);
        setSapCodeInput(app.sapCustomerCode || 'SAP-230035');
      } else {
        setStage('sap_pending');
        setSapConfirmed(false);
        setSapCodeInput('');
      }
      setBankVerified(false);
      setReadyForPayment(false);
      setPaymentMode('RTGS');
      setPaymentNarration('Disbursement for ' + app.applicationNumber);
    }
  }, [app?.id]);

  const auditLog = (action: string, reason?: string) => {
    console.log({
      action,
      actor: currentUser.role,
      time: new Date().toISOString(),
      app_id: app?.id,
      reason,
    });
  };

  const sapQueue = allSMQueue.filter(a => {
    if (a.id === selected) return stage === 'sap_pending';
    return !a.sapCustomerCode;
  });

  const readyQueue = allSMQueue.filter(a => {
    if (a.id === selected) return stage === 'bank_verify' || stage === 'ready';
    return !!a.sapCustomerCode;
  });

  const initQueue = allSMQueue.filter(a => {
    if (a.id === selected) return stage === 'initiated';
    return false;
  });

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900">SAP & Disbursement Hub</h1>
          <p className="text-sm text-slate-500 mt-0.5">Finance files pending SAP setup, readiness review, or payment initiation</p>
        </div>
      </div>

      {allSMQueue.length === 0 ? (
        <div className="card text-center py-8">
          <Check size={32} className="text-green-500 mx-auto mb-3" />
          <p className="text-slate-600 font-semibold">No applications pending disbursement</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Queues */}
          <div className="card p-0 overflow-hidden lg:col-span-1 flex flex-col h-[calc(100vh-160px)]">
            <div className="overflow-y-auto">
              
              {sapQueue.length > 0 && (
                <>
                  <div className="p-4 bg-slate-50 border-y border-slate-200">
                    <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide">SAP Customer Code Queue ({sapQueue.length})</p>
                  </div>
                  <div className="divide-y divide-slate-100">
                    {sapQueue.map(a => (
                      <button
                        key={a.id}
                        onClick={() => setSelected(a.id)}
                        className={`w-full flex items-center gap-3 p-4 hover:bg-slate-50 transition-colors text-left ${selected === a.id ? 'bg-green-50 border-l-4 border-l-green-500' : ''}`}
                      >
                        <Banknote size={16} className="text-green-600 flex-shrink-0" />
                        <div className="flex-1 min-w-0">
                          <div className="font-semibold text-slate-900 num text-sm">{a.applicationNumber}</div>
                          <div className="text-xs text-slate-500 truncate">{a.memberName}</div>
                          <div className="text-xs text-green-700 num font-medium">{fmt(a.requestedAmount)}</div>
                        </div>
                        <StatusBadge label={selected === a.id ? getDisbursementStatus(a, stage) : getDisbursementStatus(a)} size="sm" />
                      </button>
                    ))}
                  </div>
                </>
              )}

              {readyQueue.length > 0 && (
                <>
                  <div className="p-4 bg-slate-50 border-y border-slate-200">
                    <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Disbursement Readiness Queue ({readyQueue.length})</p>
                  </div>
                  <div className="divide-y divide-slate-100">
                    {readyQueue.map(a => (
                      <button
                        key={a.id}
                        onClick={() => setSelected(a.id)}
                        className={`w-full flex items-center gap-3 p-4 hover:bg-slate-50 transition-colors text-left ${selected === a.id ? 'bg-green-50 border-l-4 border-l-green-500' : ''}`}
                      >
                        <Banknote size={16} className="text-green-600 flex-shrink-0" />
                        <div className="flex-1 min-w-0">
                          <div className="font-semibold text-slate-900 num text-sm">{a.applicationNumber}</div>
                          <div className="text-xs text-slate-500 truncate">{a.memberName}</div>
                          <div className="text-xs text-green-700 num font-medium">{fmt(a.requestedAmount)}</div>
                        </div>
                        <StatusBadge label={selected === a.id ? getDisbursementStatus(a, stage) : getDisbursementStatus(a)} size="sm" />
                      </button>
                    ))}
                  </div>
                </>
              )}

              {initQueue.length > 0 && (
                <>
                  <div className="p-4 bg-slate-50 border-y border-slate-200">
                    <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Payment Initiation Queue ({initQueue.length})</p>
                  </div>
                  <div className="divide-y divide-slate-100">
                    {initQueue.map(a => (
                      <button
                        key={a.id}
                        onClick={() => setSelected(a.id)}
                        className={`w-full flex items-center gap-3 p-4 hover:bg-slate-50 transition-colors text-left ${selected === a.id ? 'bg-green-50 border-l-4 border-l-green-500' : ''}`}
                      >
                        <Banknote size={16} className="text-green-600 flex-shrink-0" />
                        <div className="flex-1 min-w-0">
                          <div className="font-semibold text-slate-900 num text-sm">{a.applicationNumber}</div>
                          <div className="text-xs text-slate-500 truncate">{a.memberName}</div>
                          <div className="text-xs text-green-700 num font-medium">{fmt(a.requestedAmount)}</div>
                        </div>
                        <StatusBadge label="payment_initiated" size="sm" />
                      </button>
                    ))}
                  </div>
                </>
              )}
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
                      <StatusBadge label={getDisbursementStatus(app, stage)} size="sm" />
                    </div>
                    <p className="text-sm text-slate-500">{app.memberName} · {fmt(app.requestedAmount)}</p>
                  </div>
                  <button onClick={() => onOpenApplication(app.id)} className="btn-secondary flex items-center gap-2 flex-shrink-0">
                    <FileText size={14} /> Full Application
                  </button>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mb-4">
                  {(Object.entries(STAGE_LABELS) as Array<[DisbStage, string]>).map(([s, label]) => (
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

              {/* 1. SAP Code panel */}
              {(stage === 'sap_pending' || sapConfirmed) && (
                <div className="card">
                  <h3 className="text-sm font-semibold text-slate-700 mb-3 flex items-center gap-2">
                    <Building2 size={14} /> SAP Customer Code Setup
                  </h3>
                  {sapConfirmed ? (
                    <div className="flex flex-col gap-3">
                      <div className="flex items-center gap-2 text-green-700 bg-green-50 rounded-lg p-3 text-sm">
                        <Check size={16} /> SAP code confirmed: <span className="font-bold num">{sapCodeInput}</span>
                      </div>
                      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-sm">
                        <div><p className="text-xs text-slate-500">Status</p><p className="font-medium">Reused</p></div>
                        <div><p className="text-xs text-slate-500">Confirmed By</p><p className="font-medium">Senior Manager</p></div>
                        <div><p className="text-xs text-slate-500">Date</p><p className="font-medium">{new Date().toLocaleDateString('en-IN')}</p></div>
                        <div><p className="text-xs text-slate-500">Evidence</p><p className="font-medium text-blue-600 hover:underline cursor-pointer">Email Ref #882</p></div>
                      </div>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <div>
                          <label className="field-label">SAP Customer Code</label>
                          <input type="text" value={sapCodeInput} onChange={e => setSapCodeInput(e.target.value)} className="field-input" placeholder="e.g. SAP-240042" />
                        </div>
                        <div>
                          <label className="field-label">Status</label>
                          <select className="field-select"><option>New Request</option><option>Reused Code</option></select>
                        </div>
                        <div>
                          <label className="field-label">Requested by</label>
                          <input type="text" disabled value="Credit Manager" className="field-input bg-slate-50" />
                        </div>
                        <div>
                          <label className="field-label">Confirmation Evidence</label>
                          <button className="w-full flex items-center justify-center gap-2 border rounded-lg px-4 py-2.5 text-sm font-medium transition-colors border-slate-200 bg-white text-slate-700 hover:bg-slate-50">
                            <Upload size={14} /> Upload confirmation
                          </button>
                        </div>
                        <div className="sm:col-span-2">
                          <label className="field-label">Finance comments</label>
                          <input type="text" value={sapComments} onChange={e => setSapComments(e.target.value)} className="field-input" placeholder="Optional comments..." />
                        </div>
                      </div>
                      <div className="flex gap-3">
                        {isSeniorManager ? (
                          <>
                            <button className="btn-primary text-sm flex-1" disabled={!sapCodeInput} onClick={() => { setSapConfirmed(true); setStage('bank_verify'); auditLog('CONFIRMED_SAP_CODE'); }}>Confirm SAP code</button>
                            <button className="btn-secondary text-sm flex-1" onClick={() => auditLog('MARKED_REUSED_CODE')}>Mark existing code reused</button>
                            <button className="btn-secondary text-sm flex-1" onClick={() => auditLog('RETURNED_SAP_REQUEST', sapComments)}>Return SAP request</button>
                          </>
                        ) : (
                          <div className="w-full bg-slate-50 border border-slate-200 text-slate-500 text-sm px-4 py-2.5 rounded-lg flex items-center gap-2">
                            <Lock size={14} /> Senior Manager Finance action required
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* 2. Bank verification panel */}
              {(stage === 'bank_verify' || bankVerified) && (
                <div className="card">
                  <h3 className="text-sm font-semibold text-slate-700 mb-3 flex items-center gap-2">
                    <ShieldCheck size={14} /> Bank Verification
                  </h3>
                  {bankVerified ? (
                    <div className="flex items-center gap-2 text-green-700 bg-green-50 rounded-lg p-3 text-sm">
                      <Check size={16} /> Bank verification complete. SAP customer code is confirmed.
                    </div>
                  ) : (
                    <div className="space-y-4">
                      <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
                        <div className="flex gap-2">
                          <AlertTriangle size={16} className="text-amber-600 flex-shrink-0 mt-0.5" />
                          <div className="text-sm text-amber-800">
                            <p className="font-semibold">Bank verification required before payment can be initiated.</p>
                            <p className="mt-1">Confirm account holder name, account number, IFSC and signature mismatch clearance.</p>
                          </div>
                        </div>
                      </div>
                      <div className="grid grid-cols-2 sm:grid-cols-5 gap-4 text-sm">
                        <div><p className="text-xs text-slate-500">Borrower</p><p className="font-medium">{app.memberName}</p></div>
                        <div><p className="text-xs text-slate-500">A/C Name</p><p className="font-medium">{app.memberName}</p></div>
                        <div><p className="text-xs text-slate-500">Account</p><p className="font-medium">XXXXX1234</p></div>
                        <div><p className="text-xs text-slate-500">IFSC</p><p className="font-medium">SBIN0001234</p></div>
                        <div><p className="text-xs text-slate-500">Bank/Branch</p><p className="font-medium">SBI / Main</p></div>
                        <div><p className="text-xs text-slate-500">Name Match</p><p className="font-medium text-green-600">Exact Match</p></div>
                        <div><p className="text-xs text-slate-500">Signature</p><p className="font-medium text-green-600">Cleared</p></div>
                        <div><p className="text-xs text-slate-500">Letter Reqd</p><p className="font-medium">No</p></div>
                        <div className="col-span-2"><p className="text-xs text-slate-500">Cancelled Cheque</p><p className="font-medium text-blue-600 hover:underline cursor-pointer">View PDF</p></div>
                      </div>
                      <div className="sm:col-span-2">
                        <label className="field-label">Verification comment</label>
                        <input type="text" value={bankComments} onChange={e => setBankComments(e.target.value)} className="field-input" placeholder="Mandatory for return..." />
                      </div>
                      <div className="flex gap-3 flex-wrap">
                        {isSeniorManager ? (
                          <>
                            <button className="btn-primary text-sm flex-1" onClick={() => { setBankVerified(true); setStage('ready'); auditLog('BANK_VERIFIED'); }}>Verify bank details</button>
                            <button className="btn-secondary text-sm flex-1" disabled={!bankComments} onClick={() => auditLog('RETURNED_BANK_VERIFY', bankComments)}>Return for bank correction</button>
                            <button className="btn-secondary text-sm flex-1 flex items-center justify-center gap-2" onClick={() => auditLog('UPLOAD_BANK_EVIDENCE')}><Upload size={14} /> Upload bank verification evidence</button>
                            <button className="btn-secondary text-sm flex-1 text-red-600 hover:bg-red-50" onClick={() => auditLog('ADDED_FINANCE_BLOCKER')}>Add finance blocker</button>
                          </>
                        ) : (
                          <div className="w-full bg-slate-50 border border-slate-200 text-slate-500 text-sm px-4 py-2.5 rounded-lg flex items-center gap-2">
                            <Lock size={14} /> Senior Manager Finance action required
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* 3. Disbursement Ready panel */}
              {(stage === 'ready' || readyForPayment) && (
                <div className="card">
                  <h3 className="text-sm font-semibold text-slate-700 mb-3 flex items-center gap-2">
                    <Check size={14} /> Disbursement Readiness Review
                  </h3>
                  {readyForPayment ? (
                    <div className="flex items-center gap-2 text-green-700 bg-green-50 rounded-lg p-3 text-sm">
                      <Check size={16} /> All readiness gates cleared. Payment can be initiated.
                    </div>
                  ) : (
                    <div className="space-y-4">
                      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
                        {[
                          { id: 'sanction', label: 'Sanction approved', autoOk: true },
                          { id: 'docs', label: 'Documentation checklist complete', autoOk: true },
                          { id: 'cs', label: 'Company Secretary sign-off complete', autoOk: true },
                          { id: 'cm', label: 'Credit Manager sign-off complete', autoOk: true },
                          { id: 'sc', label: 'Sanction Committee final approval', autoOk: true },
                          { id: 'sap', label: 'SAP customer code created / reused', autoOk: sapConfirmed },
                          { id: 'bank_details', label: 'Borrower bank details entered', autoOk: true },
                          { id: 'cheque', label: 'Cancelled cheque verified', autoOk: bankVerified },
                          { id: 'bvl', label: 'Bank verification letter resolved', autoOk: true },
                          { id: 'exceptions', label: 'No blocking exceptions', autoOk: true },
                          { id: 'amount', label: 'Disbursement amount within sanction', autoOk: true },
                        ].map(item => {
                          const ok = item.autoOk || readinessChecks[item.id];
                          return (
                            <button
                              key={item.id}
                              disabled={item.autoOk || !isSeniorManager}
                              onClick={() => setReadinessChecks(prev => ({ ...prev, [item.id]: !prev[item.id] }))}
                              className={`rounded-lg border p-3 text-left w-full transition-colors ${ok ? 'bg-green-50 border-green-100' : 'bg-amber-50 border-amber-100 hover:bg-amber-100'}`}
                            >
                              <p className="text-xs text-slate-500">{item.label}</p>
                              <p className={`text-sm font-semibold mt-0.5 ${ok ? 'text-green-800' : 'text-amber-800'}`}>{ok ? 'Verified ✓' : 'Tap to verify'}</p>
                            </button>
                          );
                        })}
                      </div>
                      
                      {!bankVerified && (
                        <div className="bg-slate-50 border border-slate-200 text-slate-700 text-sm px-4 py-3 rounded-lg flex items-center gap-2">
                          <Lock size={16} className="text-slate-500" />
                          <span className="font-semibold text-slate-900">Payment locked — complete bank verification</span>
                        </div>
                      )}
                      
                      <div className="flex gap-3 flex-wrap">
                        {isSeniorManager ? (
                          <>
                            <button className="btn-primary text-sm flex-[2]" disabled={!sapConfirmed || !bankVerified} onClick={() => { setReadyForPayment(true); setStage('initiated'); auditLog('MARKED_DISBURSEMENT_READY'); }}>Mark disbursement ready</button>
                            <button className="btn-secondary text-sm flex-1" onClick={() => auditLog('RETURNED_TO_DOCUMENTATION')}>Return to documentation</button>
                            <button className="btn-secondary text-sm flex-1" onClick={() => auditLog('RETURNED_TO_SAP')}>Return to SAP setup</button>
                            <button className="btn-secondary text-sm flex-1 text-red-600 hover:bg-red-50" onClick={() => auditLog('ADDED_FINANCE_BLOCKER')}>Add finance blocker</button>
                          </>
                        ) : (
                          <div className="w-full bg-slate-50 border border-slate-200 text-slate-500 text-sm px-4 py-2.5 rounded-lg flex items-center gap-2">
                            <Lock size={14} /> Senior Manager Finance action required
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* 4. Payment Initiated panel */}
              {stage === 'initiated' && (
                <div className="card">
                  <h3 className="text-sm font-semibold text-slate-700 mb-3 flex items-center gap-2">
                    <Banknote size={14} /> Payment Initiation
                  </h3>
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
                      <div><p className="text-xs text-slate-500">Borrower</p><p className="font-medium">{app.memberName}</p></div>
                      <div><p className="text-xs text-slate-500">Application Reference</p><p className="font-medium">{app.applicationNumber}</p></div>
                      <div><p className="text-xs text-slate-500">SAP Customer Code</p><p className="font-medium">{sapCodeInput}</p></div>
                      <div><p className="text-xs text-slate-500">Sanctioned Amount</p><p className="font-medium">{fmt(app.requestedAmount)}</p></div>
                      <div><p className="text-xs text-slate-500">Masked Bank Account</p><p className="font-medium">XXXXX1234</p></div>
                      <div><p className="text-xs text-slate-500">IFSC</p><p className="font-medium">SBIN0001234</p></div>
                      <div><p className="text-xs text-slate-500">Initiated By</p><p className="font-medium">Senior Manager</p></div>
                      <div><p className="text-xs text-slate-500">Initiation Date</p><p className="font-medium">{new Date().toLocaleDateString('en-IN')}</p></div>
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                      <div>
                        <label className="field-label">Disbursement Amount</label>
                        <input type="text" value={fmt(app.requestedAmount)} disabled className="field-input bg-slate-50" />
                      </div>
                      <div>
                        <label className="field-label">Payment Mode</label>
                        <select value={paymentMode} onChange={e => setPaymentMode(e.target.value)} className="field-select"><option>RTGS</option><option>NEFT</option></select>
                      </div>
                      <div>
                        <label className="field-label">SFPCL/RBL Bank Account</label>
                        <select value={sfpclAccount} onChange={e => setSfpclAccount(e.target.value)} className="field-select"><option>RBL Bank - 100029384756</option></select>
                      </div>
                      <div className="sm:col-span-3">
                        <label className="field-label">Payment Narration</label>
                        <input type="text" value={paymentNarration} onChange={e => setPaymentNarration(e.target.value)} className="field-input" />
                      </div>
                    </div>
                    <div className="flex gap-3">
                      {isSeniorManager ? (
                        <>
                          <button className="btn-primary text-sm flex-1" disabled={!paymentNarration.includes(app.applicationNumber)} onClick={() => { auditLog('INITIATED_PAYMENT_SENT_TO_CFC'); setSelected(null); }}>Initiate payment & Send to CFC</button>
                          <button className="btn-secondary text-sm flex-1" onClick={() => auditLog('SAVED_PAYMENT_DRAFT')}>Save payment draft</button>
                          <button className="btn-secondary text-sm flex-1 text-red-600 hover:bg-red-50" onClick={() => auditLog('CANCELLED_INITIATION')}>Cancel initiation</button>
                        </>
                      ) : (
                        <div className="w-full bg-slate-50 border border-slate-200 text-slate-500 text-sm px-4 py-2.5 rounded-lg flex items-center gap-2">
                          <Lock size={14} /> Senior Manager Finance action required
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}

            </div>
          ) : (
            <div className="lg:col-span-2 space-y-4">
               <div className="card text-center py-8">
                  <p className="text-slate-600 font-semibold">Select an application from the queue to process.</p>
               </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default DisbursementHub;
