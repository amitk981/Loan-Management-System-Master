const fs = require('fs');
const path = require('path');

const code = `import React, { useState } from 'react';
import {
  CheckCircle2, FileText, Download, Archive, Shield,
  AlertTriangle, BadgeCheck, Clock, ChevronRight, Unlock, Upload, Send, FileCheck
} from 'lucide-react';
import StatusBadge from '../../components/ui/StatusBadge';
import { useRole } from '../../contexts/RoleContext';

type ClosureTab = 'closure' | 'noc' | 'security_return' | 'archive';

interface ClosureLoan {
  id: string;
  loanNo: string;
  borrower: string;
  sanctioned: number;
  outstanding: number;
  status: string;
  repaidOn: string | null;
  nocStatus: string;
}

const closureLoans: ClosureLoan[] = [
  { id: 'la001', loanNo: 'LO00000031', borrower: 'Asha Bhosale',    sanctioned: 200000, outstanding: 0,     status: 'fully_repaid', repaidOn: '10 May 2025', nocStatus: 'not_ready' },
  { id: 'la002', loanNo: 'LO00000028', borrower: 'Vijay Patil',     sanctioned: 350000, outstanding: 12000, status: 'not_eligible',  repaidOn: null,        nocStatus: 'not_ready' },
  { id: 'la003', loanNo: 'LO00000025', borrower: 'Radha Kisan Org', sanctioned: 500000, outstanding: 0,     status: 'closed',       repaidOn: '28 Mar 2025', nocStatus: 'issued' },
];

const LoanClosureHub: React.FC = () => {
  const { currentUser } = useRole();
  const role = currentUser.role;

  const canAccess = ['admin', 'credit_manager', 'senior_manager_finance', 'deputy_manager_finance', 'accounts_team', 'cfo', 'auditor', 'compliance_team', 'company_secretary'].includes(role);
  const canComply = ['compliance_team', 'company_secretary'].includes(role);

  const [activeTab, setActiveTab] = useState<ClosureTab>('closure');
  const [selectedLoan, setSelectedLoan] = useState<ClosureLoan>(closureLoans[0]);
  
  const [nocGenerated, setNocGenerated] = useState(false);
  const [nocSent, setNocSent] = useState(false);
  const [nocDispatched, setNocDispatched] = useState(false);
  const [nocAck, setNocAck] = useState(false);

  const [sh4Returned, setSh4Returned] = useState(false);
  const [chequeReturned, setChequeReturned] = useState(false);
  const [cdslUnpledgeStart, setCdslUnpledgeStart] = useState(false);
  const [cdslUnpledged, setCdslUnpledged] = useState(false);
  const [poaReturned, setPoaReturned] = useState(false);
  const [securityReturnConfirmed, setSecurityReturnConfirmed] = useState(false);
  
  const [archiveCompleted, setArchiveCompleted] = useState(false);
  const [loanMarkedClosed, setLoanMarkedClosed] = useState(false);
  const [closureNotes, setClosureNotes] = useState('');

  if (!canAccess) {
    return <div className="p-6 text-red-600">Access Denied. You do not have permission to view this module.</div>;
  }

  const tabs: { id: ClosureTab; label: string }[] = [
    { id: 'closure',         label: 'Closure Checklist' },
    { id: 'noc',             label: 'NOC Generation' },
    { id: 'security_return', label: 'Security Return / Unpledge' },
    { id: 'archive',         label: 'Archive' },
  ];

  const nocComplete = selectedLoan.nocStatus === 'issued' || nocAck;
  const securityComplete = selectedLoan.status === 'closed' || securityReturnConfirmed;
  const archiveComplete = selectedLoan.status === 'closed' || archiveCompleted;
  const closedComplete = selectedLoan.status === 'closed' || loanMarkedClosed || archiveCompleted;

  const closureChecklist = [
    { item: 'All principal repaid',                         done: selectedLoan.outstanding === 0 },
    { item: 'All interest repaid (incl. capitalised)',      done: selectedLoan.outstanding === 0 },
    { item: 'Penal interest (if any) cleared',              done: selectedLoan.outstanding === 0 },
    { item: 'Closing balance confirmed in SAP',             done: selectedLoan.outstanding === 0 },
    { item: 'Security documents accounted',                 done: selectedLoan.outstanding === 0 },
    { item: 'Compliance checklist complete',                done: selectedLoan.outstanding === 0 },
    { item: 'NOC issued to borrower',                       done: nocComplete },
    { item: 'SH-4 / CDSL pledge released',                  done: securityComplete },
    { item: 'Blank cheque returned',                        done: securityComplete },
    { item: 'Loan record archived',                         done: archiveComplete },
  ];

  const completedCount = closureChecklist.filter(c => c.done).length;
  const publicationImpact = [
    { label: 'Borrower Communication', status: nocComplete ? 'published' : nocGenerated ? 'ready_to_publish' : 'not_ready', note: nocGenerated ? 'Closure/NOC status is staged for the borrower portal.' : 'Publish after NOC generation.' },
    { label: 'NOC Register', status: nocComplete ? 'updated' : 'pending', note: nocComplete ? 'NOC reference and issue date are visible in the register preview.' : 'Waiting for NOC issue.' },
    { label: 'Security Register', status: securityComplete ? 'returned' : 'held', note: securityComplete ? 'SH-4, cheque, PoA and CDSL release states are complete.' : 'Security remains in custody.' },
    { label: 'Archive Register', status: archiveComplete ? 'archived' : loanMarkedClosed ? 'ready' : 'pending', note: archiveComplete ? 'Archive ID and retention date are staged.' : 'Archive after closure checklist completion.' },
    { label: 'Audit Trail', status: 'updated', note: 'Local prototype events show closure, NOC, security return and archive actions.' },
  ];

  const isEligible = selectedLoan.outstanding === 0;

  const getLoanStatus = (loan: ClosureLoan) => {
    if (loan.outstanding > 0) return 'Not Eligible';
    if (loan.status === 'closed') return 'Closed';
    if (archiveCompleted) return 'Archived';
    if (loanMarkedClosed) return 'Ready to Archive';
    if (!securityComplete) return 'Security Return Pending';
    if (!nocComplete) return 'NOC Pending';
    if (loan.status === 'fully_repaid') return 'Closure In Progress';
    return 'Fully Repaid';
  };

  const currentLoanStatus = getLoanStatus(selectedLoan);

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-xl font-bold text-slate-900">Loan Closure & Archive</h1>
        <p className="text-sm text-slate-500 mt-1">Manage NOC generation, security return, CDSL unpledge and record archival for fully-repaid loans.</p>
      </div>

      {/* Loan selector */}
      <div className="grid grid-cols-3 gap-3 mb-6">
        {closureLoans.map(loan => (
          <button
            key={loan.id}
            onClick={() => {
              if (loan.outstanding === 0) setSelectedLoan(loan);
            }}
            disabled={loan.outstanding > 0}
            className={\`text-left border rounded-xl p-4 transition-all \${
              selectedLoan.id === loan.id
                ? 'border-green-300 bg-green-50'
                : loan.outstanding > 0
                ? 'border-slate-200 bg-slate-50 opacity-60 cursor-not-allowed'
                : 'border-slate-200 bg-white hover:border-slate-300'
            }\`}
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-mono font-medium text-slate-600">{loan.loanNo}</span>
              <StatusBadge label={loan.outstanding > 0 ? 'Not Eligible' : (loan.status === 'closed' ? 'Closed' : 'Closure In Progress')} size="sm" type={loan.outstanding > 0 ? 'slate' : 'default'} />
            </div>
            <div className="font-medium text-slate-900 text-sm">{loan.borrower}</div>
            <div className="text-xs text-slate-500 mt-1">
              {loan.outstanding === 0 ? 'Fully repaid' : \`₹\${loan.outstanding.toLocaleString('en-IN')} outstanding\`}
            </div>
          </button>
        ))}
      </div>

      {/* Tabs */}
      <div className="border-b border-slate-200 mb-6">
        <div className="flex gap-1">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={\`px-4 py-2.5 text-sm font-medium border-b-2 transition-colors \${
                activeTab === tab.id
                  ? 'border-green-600 text-green-700'
                  : 'border-transparent text-slate-500 hover:text-slate-700'
              }\`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      <div className="bg-white border border-slate-200 rounded-xl p-4 mb-6">
        <div className="flex items-center justify-between gap-3 mb-3">
          <div>
            <h3 className="text-sm font-semibold text-slate-900">Closure Status</h3>
            <p className="text-xs text-slate-500 mt-0.5">Current status across NOC, security return, archive and audit.</p>
          </div>
          <StatusBadge label={currentLoanStatus} size="sm" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
          {publicationImpact.map(item => (
            <div key={item.label} className="rounded-lg bg-slate-50 border border-slate-100 p-3">
              <div className="flex items-center justify-between gap-2">
                <p className="text-xs font-semibold text-slate-700">{item.label}</p>
                <StatusBadge label={item.status} size="sm" type={item.status === 'pending' || item.status === 'not_ready' ? 'slate' : 'default'} />
              </div>
              <p className="text-xs text-slate-500 mt-2">{item.note}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Closure Checklist */}
      {activeTab === 'closure' && (
        <div className="max-w-2xl space-y-5">
          <div className="bg-white border border-slate-200 rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="font-semibold text-slate-900">Closure Checklist — {selectedLoan.loanNo}</h3>
                <p className="text-xs text-slate-500 mt-0.5">{selectedLoan.borrower}</p>
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold text-green-600">{completedCount}/{closureChecklist.length}</div>
                <div className="text-xs text-slate-500">items complete</div>
              </div>
            </div>

            <div className="w-full bg-slate-100 rounded-full h-2 mb-5">
              <div
                className="bg-green-500 h-2 rounded-full transition-all"
                style={{ width: \`\${(completedCount / closureChecklist.length) * 100}%\` }}
              />
            </div>

            <div className="space-y-2">
              {closureChecklist.map((item, i) => (
                <div key={i} className={\`flex items-center gap-3 p-3 rounded-lg \${item.done ? 'bg-green-50' : 'bg-slate-50'}\`}>
                  {item.done
                    ? <CheckCircle2 size={16} className="text-green-600 flex-shrink-0" />
                    : <Clock size={16} className="text-slate-300 flex-shrink-0" />
                  }
                  <span className={\`text-sm \${item.done ? 'text-green-800' : 'text-slate-500'}\`}>{item.item}</span>
                </div>
              ))}
            </div>

            {selectedLoan.outstanding === 0 && (
              <div className="mt-5 space-y-3">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1.5">Closure Notes</label>
                  <textarea
                    value={closureNotes}
                    onChange={e => setClosureNotes(e.target.value)}
                    rows={3}
                    placeholder="Record any final observations before closure…"
                    className="w-full px-4 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500 resize-none"
                  />
                </div>
                {canComply && (
                  <button
                    onClick={() => {
                      if (completedCount === closureChecklist.length) {
                        setLoanMarkedClosed(true);
                      } else {
                        setActiveTab('noc');
                      }
                    }}
                    className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-5 py-2.5 rounded-lg text-sm font-semibold transition-colors disabled:opacity-50"
                  >
                    <BadgeCheck size={16} />
                    {completedCount === closureChecklist.length ? 'Mark Loan as Closed' : nocComplete ? 'Continue Closure' : 'Initiate NOC'}
                  </button>
                )}
              </div>
            )}
            {selectedLoan.outstanding > 0 && (
              <div className="mt-4 flex items-center gap-2 text-amber-700 bg-amber-50 rounded-xl p-4 text-sm">
                <AlertTriangle size={16} className="flex-shrink-0" />
                Closure cannot proceed — outstanding balance of ₹{selectedLoan.outstanding.toLocaleString('en-IN')} remains.
              </div>
            )}
          </div>
        </div>
      )}

      {/* NOC Generation */}
      {activeTab === 'noc' && (
        <div className="max-w-2xl space-y-5">
          <div className="bg-white border border-slate-200 rounded-xl p-6">
            <h3 className="font-semibold text-slate-900 mb-4 flex items-center gap-2">
              <BadgeCheck size={16} className="text-green-600" />
              No Objection Certificate (NOC) Generation
            </h3>
            
            {!isEligible ? (
              <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 text-center">
                <Lock size={32} className="mx-auto text-amber-300 mb-3" />
                <div className="font-semibold text-amber-700">NOC Locked</div>
                <div className="text-sm text-amber-600 mt-1">NOC locked until full repayment is validated.</div>
              </div>
            ) : (
              <>
                <div className="grid grid-cols-2 gap-4 text-sm bg-slate-50 rounded-lg p-4 mb-5">
                  <div><div className="text-slate-500">Loan Account</div><div className="font-medium">{selectedLoan.loanNo}</div></div>
                  <div><div className="text-slate-500">Borrower</div><div className="font-medium">{selectedLoan.borrower}</div></div>
                  <div><div className="text-slate-500">Sanctioned Amount</div><div className="font-medium">₹{selectedLoan.sanctioned.toLocaleString('en-IN')}</div></div>
                  <div><div className="text-slate-500">Full Repayment Date</div><div className="font-medium">{selectedLoan.repaidOn || 'Pending'}</div></div>
                </div>

                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    {[
                      { label: 'NOC Date', type: 'date', defaultValue: new Date().toISOString().split('T')[0] },
                      { label: 'Reference Number', type: 'text', defaultValue: 'NOC-2025-042' },
                    ].map(f => (
                      <div key={f.label}>
                        <label className="block text-sm font-medium text-slate-700 mb-1.5">{f.label}</label>
                        <input
                          type={f.type}
                          defaultValue={f.defaultValue}
                          className="w-full px-4 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                        />
                      </div>
                    ))}
                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1.5">Authorised Signatory</label>
                      <select className="w-full px-4 py-2.5 border border-slate-200 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-green-500">
                        <option>Director - Operations</option>
                        <option>CFO</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1.5">Delivery Mode</label>
                      <select className="w-full px-4 py-2.5 border border-slate-200 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-green-500">
                        <option>Email & Portal (MP20)</option>
                        <option>Registered Post</option>
                        <option>In-Person Collection</option>
                      </select>
                    </div>
                  </div>
                  
                  {canComply && (
                    <div className="flex gap-3 flex-wrap mt-4">
                      {!nocGenerated ? (
                        <button
                          onClick={() => setNocGenerated(true)}
                          className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-5 py-2.5 rounded-lg text-sm font-semibold transition-colors"
                        >
                          <BadgeCheck size={16} />
                          Generate NOC
                        </button>
                      ) : (
                        <button disabled className="flex items-center gap-2 bg-slate-100 text-slate-400 px-5 py-2.5 rounded-lg text-sm font-semibold transition-colors">
                          <CheckCircle2 size={16} /> NOC Generated
                        </button>
                      )}
                      
                      <button className="flex items-center gap-2 border border-slate-200 text-slate-700 px-4 py-2.5 rounded-lg text-sm font-medium hover:bg-slate-50 transition-colors">
                        <FileText size={16} />
                        Preview
                      </button>

                      {nocGenerated && !nocSent && (
                        <button onClick={() => setNocSent(true)} className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2.5 rounded-lg text-sm font-medium transition-colors">
                          <Send size={16} /> Send to borrower
                        </button>
                      )}
                      {nocSent && !nocDispatched && (
                        <button onClick={() => setNocDispatched(true)} className="flex items-center gap-2 bg-slate-700 hover:bg-slate-800 text-white px-4 py-2.5 rounded-lg text-sm font-medium transition-colors">
                          <FileCheck size={16} /> Mark hard copy dispatched
                        </button>
                      )}
                      {nocDispatched && !nocAck && (
                        <button onClick={() => setNocAck(true)} className="flex items-center gap-2 border border-green-600 text-green-700 hover:bg-green-50 px-4 py-2.5 rounded-lg text-sm font-medium transition-colors">
                          <Upload size={16} /> Upload acknowledged copy
                        </button>
                      )}
                    </div>
                  )}

                  {nocComplete && (
                    <div className="flex items-center gap-3 bg-green-50 border border-green-200 rounded-xl p-4 mt-4">
                      <CheckCircle2 size={20} className="text-green-600 flex-shrink-0" />
                      <div>
                        <div className="font-medium text-green-800 text-sm">NOC generated, issued, and acknowledged</div>
                        <div className="text-xs text-green-600 mt-0.5">Ref: NOC-2025-042 · Borrower Communication (MP20) updated</div>
                      </div>
                      <button className="ml-auto flex items-center gap-1.5 text-sm text-green-700 font-medium hover:underline flex-shrink-0">
                        <Download size={14} />
                        Download
                      </button>
                    </div>
                  )}
                </div>
              </>
            )}
          </div>
        </div>
      )}

      {/* Security Return */}
      {activeTab === 'security_return' && (
        <div className="max-w-2xl space-y-5">
          <div className="bg-white border border-slate-200 rounded-xl p-6">
            <h3 className="font-semibold text-slate-900 mb-4 flex items-center gap-2">
              <Unlock size={16} className="text-green-600" />
              Security Return & CDSL Unpledge
            </h3>
            
            {!isEligible ? (
              <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 text-center">
                <Lock size={32} className="mx-auto text-amber-300 mb-3" />
                <div className="font-semibold text-amber-700">Security Return Locked</div>
                <div className="text-sm text-amber-600 mt-1">Security return locked until full repayment is validated.</div>
              </div>
            ) : (
              <>
                <div className="space-y-3 mb-5">
                  {[
                    { doc: 'SH-4 Transfer Form',   securityType: 'Physical share transfer',    status: securityComplete || sh4Returned ? 'Returned' : 'Held in Custody', onReturn: () => setSh4Returned(true) },
                    { doc: 'Blank Cheque',         securityType: 'Cheque returned to borrower', status: securityComplete || chequeReturned ? 'Returned' : 'Held in Custody', onReturn: () => setChequeReturned(true) },
                    { doc: 'CDSL Pledge Release',  securityType: 'Demat shares unpledged',      status: securityComplete || cdslUnpledged ? 'Unpledged' : cdslUnpledgeStart ? 'Unpledge Pending' : 'Pledge Active', onReturn: () => cdslUnpledgeStart ? setCdslUnpledged(true) : setCdslUnpledgeStart(true), actionText: cdslUnpledgeStart ? 'Mark Unpledge Complete' : 'Start Unpledge' },
                    { doc: 'Power of Attorney',    securityType: 'PoA cancelled/returned',      status: securityComplete || poaReturned ? 'Returned' : 'Held in Custody', onReturn: () => setPoaReturned(true) },
                  ].map(item => (
                    <div key={item.doc} className="flex flex-col md:flex-row md:items-center justify-between p-4 border border-slate-100 rounded-xl hover:bg-slate-50 gap-4">
                      <div>
                        <div className="text-sm font-medium text-slate-800">{item.doc}</div>
                        <div className="text-xs text-slate-400 mt-0.5">{item.securityType}</div>
                        {(item.status === 'Returned' || item.status === 'Unpledged') && <div className="text-xs text-green-600 mt-0.5">Updated: {new Date().toLocaleDateString('en-IN')}</div>}
                      </div>
                      <div className="flex items-center gap-3">
                        <StatusBadge label={item.status} size="sm" type={item.status.includes('Returned') || item.status.includes('Unpledged') ? 'success' : item.status.includes('Pending') ? 'warning' : 'default'} />
                        {canComply && !item.status.includes('Returned') && !item.status.includes('Unpledged') && (
                          <button onClick={item.onReturn} className="text-xs border border-slate-200 px-3 py-1.5 rounded-lg text-slate-700 hover:bg-slate-100 transition-colors">
                            {item.actionText || 'Mark Returned'}
                          </button>
                        )}
                      </div>
                      {/* Sub-form inline for return details (prototype mock) */}
                      {(item.status === 'Returned' || item.status === 'Unpledged') && (
                        <div className="w-full md:w-auto text-[10px] text-slate-400 mt-1 md:mt-0 text-right space-y-0.5">
                          <div>Custody Loc: HO-Vault-3</div>
                          <div>Ret to: {selectedLoan.borrower}</div>
                          <div>Ack: Uploaded · Ref: SEC-2025</div>
                          <div>By: {currentUser.name}</div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>

                {canComply && (
                  <button
                    onClick={() => setSecurityReturnConfirmed(true)}
                    disabled={!sh4Returned || !chequeReturned || !cdslUnpledged || !poaReturned}
                    className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-5 py-2.5 rounded-lg text-sm font-semibold transition-colors disabled:opacity-50"
                  >
                    <Shield size={16} />
                    {securityReturnConfirmed ? 'Security Return Complete' : 'Confirm Security Return Complete'}
                  </button>
                )}
              </>
            )}
          </div>
        </div>
      )}

      {/* Archive */}
      {activeTab === 'archive' && (
        <div className="max-w-2xl space-y-5">
          {(!nocComplete || !securityComplete) ? (
            <div className="bg-white border border-slate-200 rounded-xl p-8 text-center">
              <Lock size={32} className="mx-auto text-slate-300 mb-3" />
              <div className="font-semibold text-slate-700">Archive Locked</div>
              <div className="text-sm text-slate-500 mt-1">Archive locked until NOC and security return are complete.</div>
            </div>
          ) : (
            <div className="bg-white border border-slate-200 rounded-xl p-6">
              <h3 className="font-semibold text-slate-900 mb-4 flex items-center gap-2">
                <Archive size={16} className="text-slate-600" />
                Loan Record Archival
              </h3>
              <p className="text-xs text-slate-500 mb-5">
                Records must be archived for at least 8 years after closure. Store digital and physical archive references.
              </p>

              <div className="space-y-3 mb-5">
                {[
                  { category: 'Application & Appraisal Documents', count: 7, status: 'ready' },
                  { category: 'Sanction Documents',                  count: 3, status: 'ready' },
                  { category: 'Legal & Security Documents',          count: 5, status: 'ready' },
                  { category: 'Disbursement Records',                count: 2, status: 'ready' },
                  { category: 'Repayment Ledger',                    count: 1, status: 'ready' },
                  { category: 'Compliance Records',                  count: 4, status: 'ready' },
                ].map(cat => (
                  <div key={cat.category} className="flex items-center justify-between p-3 border border-slate-100 rounded-lg">
                    <div>
                      <div className="text-sm font-medium text-slate-800">{cat.category}</div>
                      <div className="text-xs text-slate-400 mt-0.5">{cat.count} document{cat.count !== 1 ? 's' : ''}</div>
                    </div>
                    <StatusBadge label={cat.status} size="sm" />
                  </div>
                ))}
              </div>

              <div className="bg-slate-50 rounded-xl p-4 mb-4 text-sm">
                <div className="grid grid-cols-2 gap-3">
                  <div><div className="text-slate-500 text-xs">Total Documents</div><div className="font-semibold text-slate-900">22</div></div>
                  <div><div className="text-slate-500 text-xs">Archive Retention</div><div className="font-semibold text-slate-900">8 years (until 2033)</div></div>
                  <div><div className="text-slate-500 text-xs">Closure Date</div><div className="font-semibold text-slate-900">{new Date().toLocaleDateString('en-IN')}</div></div>
                  <div><div className="text-slate-500 text-xs">Archive Date</div><div className="font-semibold text-slate-900">{archiveCompleted ? new Date().toLocaleDateString('en-IN') : 'Pending'}</div></div>
                  <div><div className="text-slate-500 text-xs">Archive Status</div><div className="font-semibold text-slate-900">{archiveCompleted ? 'Archived' : 'Ready'}</div></div>
                  <div><div className="text-slate-500 text-xs">Archive ID</div><div className="font-semibold text-slate-900">ARC-2025-042</div></div>
                  <div><div className="text-slate-500 text-xs">Physical File Reference</div><div className="font-semibold text-slate-900">Cabinet 3, Row 2</div></div>
                  <div><div className="text-slate-500 text-xs">Digital Checksum</div><div className="font-mono text-[10px] text-slate-500 truncate">sha256:8f4c2...</div></div>
                </div>
              </div>

              {canComply && (completedCount === closureChecklist.length || loanMarkedClosed) && (
                <div className="flex gap-3">
                  <button
                    onClick={() => setArchiveCompleted(true)}
                    className="flex items-center gap-2 bg-slate-700 hover:bg-slate-800 text-white px-5 py-2.5 rounded-lg text-sm font-semibold transition-colors"
                  >
                    <Archive size={16} />
                    {archiveCompleted ? 'Loan Record Archived' : 'Archive Loan Record'}
                  </button>
                  <button className="flex items-center gap-2 border border-slate-200 text-slate-700 px-4 py-2.5 rounded-lg text-sm font-medium hover:bg-slate-50 transition-colors">
                    <Download size={16} />
                    Download Archive Package
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default LoanClosureHub;
`;

fs.writeFileSync(path.join(__dirname, 'src/pages/closure/LoanClosureHub.tsx'), code);
console.log('Update successful');
