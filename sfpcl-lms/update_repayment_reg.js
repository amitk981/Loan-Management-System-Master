const fs = require('fs');

const file = 'src/pages/registers/RegistersHub.tsx';
let code = fs.readFileSync(file, 'utf8');

const oldTab = `{/* Tab 14: Repayment Register */}
        <div className="card p-0 overflow-hidden">
          <div className="p-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
            <div>
              <p className="text-sm font-semibold text-slate-900 flex items-center gap-2">
                <RefreshCcw size={14} className="text-blue-600" /> Repayment Register
              </p>
              <p className="text-xs text-slate-500 mt-0.5">Repayment receipts, channels and allocation status</p>
            </div>
            <button disabled={!canExport} className="flex items-center gap-1 text-xs text-green-700 hover:underline disabled:opacity-50 disabled:cursor-not-allowed disabled:no-underline">
              <Download size={12} /> Export
            </button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200">
                  <th className="table-header text-left">Receipt ID</th>
                  <th className="table-header text-left">Loan</th>
                  <th className="table-header text-left">Borrower</th>
                  <th className="table-header text-right">Amount</th>
                  <th className="table-header text-left">Channel</th>
                  <th className="table-header text-left">UTR</th>
                  <th className="table-header text-left">Allocation</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {[
                  { rcp: 'RCP-001', loan: 'LO00000042', borrower: 'Ganesh Thorat', amount: 15000, channel: 'direct_neft', utr: 'SBIN904212', alloc: 'Principal First' },
                  { rcp: 'RCP-002', loan: 'LO00000035', borrower: 'Kisan FPC Ltd', amount: 25000, channel: 'subsidiary_deduction', utr: '—', alloc: 'Interest First' },
                ].map(r => (
                  <tr key={r.rcp} className="hover:bg-slate-50">
                    <td className="table-cell font-mono text-slate-600">{r.rcp}</td>
                    <td className="table-cell font-mono text-slate-600">{r.loan}</td>
                    <td className="table-cell font-medium text-slate-900">{r.borrower}</td>
                    <td className="table-cell num text-right font-semibold text-green-600">₹{r.amount.toLocaleString('en-IN')}</td>
                    <td className="table-cell text-slate-600 capitalize">{r.channel.replace('_', ' ')}</td>
                    <td className="table-cell font-mono text-xs text-slate-500">{r.utr}</td>
                    <td className="table-cell text-xs text-slate-600">{r.alloc}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>`;

const newTab = `{/* Tab 14: Repayment Register */}
        <div className="card p-0 overflow-hidden">
          <div className="p-4 bg-slate-50 border-b border-slate-200">
            <p className="text-sm font-semibold text-slate-900 flex items-center gap-2">
              <RefreshCcw size={14} className="text-blue-600" /> Repayment register
            </p>
            <p className="text-xs text-slate-500 mt-0.5">Repayment receipts, allocation and SAP posting status</p>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200">
                  <th className="table-header text-left">Receipt ID</th>
                  <th className="table-header text-left">Loan Account</th>
                  <th className="table-header text-left">Borrower</th>
                  <th className="table-header text-right">Receipt Amount</th>
                  <th className="table-header text-left">Received On</th>
                  <th className="table-header text-left">Payment Reference</th>
                  <th className="table-header text-left">Channel</th>
                  <th className="table-header text-left">Allocation Status</th>
                  <th className="table-header text-left">SAP Posting</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {[
                  { rcp: 'RCP-001', lnId: 'ln001', amount: 150000, receivedOn: '2026-06-25', utr: 'SBIN904212', channel: 'direct_neft', allocRule: 'Principal first', allocStatus: 'allocated', sapStatus: 'posted_to_sap', sapRef: 'DOC-90021' },
                  { rcp: 'RCP-002', lnId: 'ln002', amount: 250000, receivedOn: '2026-06-26', utr: '—', channel: 'subsidiary_deduction', allocRule: 'Principal first', allocStatus: 'pending_allocation', sapStatus: 'posting_pending', sapRef: null },
                ].map(r => {
                  const matchedLoan = loanAccounts.find(l => l.id === r.lnId);
                  const displayLoan = matchedLoan ? (matchedLoan.accountNumber || matchedLoan.applicationNumber) : r.lnId;
                  const displayBorrower = matchedLoan ? matchedLoan.borrowerName : 'Unknown';

                  const channelMap: Record<string, string> = {
                    direct_neft: 'Direct NEFT',
                    subsidiary_deduction: 'Subsidiary deduction',
                    bank_transfer: 'Bank transfer',
                    adjustment: 'Adjustment',
                    manual_receipt: 'Manual receipt'
                  };
                  const displayChannel = channelMap[r.channel] || r.channel;

                  const allocMap: Record<string, string> = {
                    allocated: 'Allocated',
                    pending_allocation: 'Pending allocation',
                    reconciliation_pending: 'Reconciliation pending',
                    mismatch: 'Mismatch'
                  };
                  const displayAlloc = allocMap[r.allocStatus] || r.allocStatus;

                  const sapMap: Record<string, string> = {
                    posted_to_sap: 'Posted to SAP',
                    posting_pending: 'Posting pending',
                    failed: 'Failed'
                  };
                  const displaySap = sapMap[r.sapStatus] || r.sapStatus;
                  
                  const dtFormat = new Intl.DateTimeFormat('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
                  const displayDate = dtFormat.format(new Date(r.receivedOn));

                  const allocColor = displayAlloc === 'Allocated' ? 'text-green-700 bg-green-100' :
                                     displayAlloc === 'Mismatch' ? 'text-red-700 bg-red-100' :
                                     'text-amber-700 bg-amber-100';

                  const sapColor = displaySap === 'Posted to SAP' ? 'text-green-700 bg-green-100' :
                                   displaySap === 'Failed' ? 'text-red-700 bg-red-100' :
                                   'text-amber-700 bg-amber-100';

                  return (
                    <tr key={r.rcp} className="hover:bg-slate-50">
                      <td className="table-cell font-mono text-slate-600">{r.rcp}</td>
                      <td className="table-cell font-mono text-slate-600">{displayLoan}</td>
                      <td className="table-cell font-medium text-slate-900">{displayBorrower}</td>
                      <td className="table-cell num text-right font-semibold text-green-600">{fmt(r.amount)}</td>
                      <td className="table-cell text-slate-600">{displayDate}</td>
                      <td className="table-cell font-mono text-xs text-slate-500">{r.utr}</td>
                      <td className="table-cell text-slate-600">{displayChannel}</td>
                      <td className="table-cell">
                        <div className="flex flex-col gap-1 items-start">
                          <span className={\`text-xs font-semibold px-2 py-0.5 rounded-full \${allocColor}\`}>{displayAlloc}</span>
                          <span className="text-[10px] text-slate-500 font-medium">({r.allocRule})</span>
                        </div>
                      </td>
                      <td className="table-cell">
                        <div className="flex flex-col gap-1 items-start">
                           <span className={\`text-xs font-semibold px-2 py-0.5 rounded-full \${sapColor}\`}>{displaySap}</span>
                           {r.sapRef && <span className="text-[10px] text-slate-500 font-mono">{r.sapRef}</span>}
                        </div>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>`;

code = code.replace(oldTab, newTab);
fs.writeFileSync(file, code);

console.log("update complete");
