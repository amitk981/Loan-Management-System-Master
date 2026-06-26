const fs = require('fs');

const file = 'src/pages/registers/RegistersHub.tsx';
let code = fs.readFileSync(file, 'utf8');

const oldTab = `{/* Tab 13: Disbursement Register */}
        <div className="card p-0 overflow-hidden">
          <div className="p-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
            <div>
              <p className="text-sm font-semibold text-slate-900 flex items-center gap-2">
                <Send size={14} className="text-green-600" /> Disbursement Register
              </p>
              <p className="text-xs text-slate-500 mt-0.5">Payment initiation, bank authorisation and UTR evidence</p>
            </div>
            <button disabled={!canExport} className="flex items-center gap-1 text-xs text-green-700 hover:underline disabled:opacity-50 disabled:cursor-not-allowed disabled:no-underline">
              <Download size={12} /> Export
            </button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200">
                  <th className="table-header text-left">Advice ID</th>
                  <th className="table-header text-left">Loan</th>
                  <th className="table-header text-left">Borrower</th>
                  <th className="table-header text-right">Amount</th>
                  <th className="table-header text-left">Initiated</th>
                  <th className="table-header text-left">UTR</th>
                  <th className="table-header text-left">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {[
                  { adv: 'ADV-001', loan: 'LO00000042', borrower: 'Ganesh Thorat', amount: 50000, initiated: '2024-09-22', utr: 'HDFCR52390124', status: 'disbursed' },
                  { adv: 'ADV-002', loan: 'LO00000047', borrower: 'Vijay Deshmukh', amount: 45000, initiated: null, utr: null, status: 'readiness_pending' },
                ].map(d => (
                  <tr key={d.adv} className="hover:bg-slate-50">
                    <td className="table-cell font-mono text-slate-600">{d.adv}</td>
                    <td className="table-cell font-mono text-slate-600">{d.loan}</td>
                    <td className="table-cell font-medium text-slate-900">{d.borrower}</td>
                    <td className="table-cell num text-right font-semibold">₹{d.amount.toLocaleString('en-IN')}</td>
                    <td className="table-cell text-slate-600">{d.initiated || '—'}</td>
                    <td className="table-cell font-mono text-xs text-slate-500">{d.utr || '—'}</td>
                    <td className="table-cell"><StatusBadge label={d.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>`;

const newTab = `{/* Tab 13: Disbursement Register */}
        <div className="card p-0 overflow-hidden">
          <div className="p-4 bg-slate-50 border-b border-slate-200">
            <p className="text-sm font-semibold text-slate-900 flex items-center gap-2">
              <Send size={14} className="text-green-600" /> Disbursement register
            </p>
            <p className="text-xs text-slate-500 mt-0.5">Payment initiation, bank authorisation and UTR records</p>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200">
                  <th className="table-header text-left">Advice ID</th>
                  <th className="table-header text-left">Loan Account</th>
                  <th className="table-header text-left">Borrower</th>
                  <th className="table-header text-right">Disbursed Amount</th>
                  <th className="table-header text-left">Initiated On</th>
                  <th className="table-header text-left">Authorised By</th>
                  <th className="table-header text-left">Authorised On</th>
                  <th className="table-header text-left">UTR / Bank Ref</th>
                  <th className="table-header text-left">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {[
                  { adv: 'ADV-001', lnId: 'ln001', amount: 500000, initiated: '2026-06-22', initiatedBy: 'Senior Manager – Finance', authBy: 'CFC', authOn: '2026-06-22', utr: 'HDFCR52390124', status: 'disbursed' },
                  { adv: 'ADV-002', lnId: 'ln002', amount: 450000, initiated: null, initiatedBy: null, authBy: null, authOn: null, utr: null, status: 'readiness_pending' },
                ].map(d => {
                  const matchedLoan = loanAccounts.find(l => l.id === d.lnId);
                  const displayLoan = matchedLoan ? (matchedLoan.accountNumber || matchedLoan.applicationNumber) : d.lnId;
                  const displayBorrower = matchedLoan ? matchedLoan.borrowerName : 'Unknown';

                  const statusMap: Record<string, string> = {
                    readiness_pending: 'Payment readiness pending',
                    payment_initiated: 'Payment initiated',
                    authorisation_pending: 'Authorisation pending',
                    returned: 'Returned',
                    failed: 'Failed',
                    disbursed: 'Disbursed'
                  };
                  let statusText = statusMap[d.status] || d.status;
                  
                  const dtFormat = new Intl.DateTimeFormat('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
                  
                  let displayInitiated = d.initiated ? dtFormat.format(new Date(d.initiated)) : 'Pending';
                  let displayAuthOn = d.authOn ? dtFormat.format(new Date(d.authOn)) : 'Pending';
                  let displayAuthBy = d.authBy || 'Pending';
                  let displayUtr = d.utr || 'Pending';
                  
                  if (statusText !== 'Disbursed' && statusText !== 'Payment initiated' && statusText !== 'Authorisation pending' && statusText !== 'Returned' && statusText !== 'Failed') {
                    displayAuthOn = 'Pending';
                    displayAuthBy = 'Pending';
                  }

                  const statusColor = statusText === 'Disbursed' ? 'bg-green-100 text-green-700' :
                                      statusText === 'Payment readiness pending' ? 'bg-amber-50 text-amber-600' :
                                      statusText === 'Payment initiated' || statusText === 'Authorisation pending' ? 'bg-amber-100 text-amber-700' :
                                      statusText === 'Failed' || statusText === 'Returned' ? 'bg-red-100 text-red-700' :
                                      'bg-slate-100 text-slate-700';

                  return (
                    <tr key={d.adv} className="hover:bg-slate-50">
                      <td className="table-cell font-mono text-slate-600">{d.adv}</td>
                      <td className="table-cell font-mono text-slate-600">{displayLoan}</td>
                      <td className="table-cell font-medium text-slate-900">{displayBorrower}</td>
                      <td className="table-cell num text-right font-semibold text-slate-900">{fmt(d.amount)}</td>
                      <td className="table-cell text-slate-600">{displayInitiated}</td>
                      <td className="table-cell text-slate-600">{displayAuthBy}</td>
                      <td className="table-cell text-slate-600">{displayAuthOn}</td>
                      <td className="table-cell font-mono text-xs text-slate-500">{displayUtr}</td>
                      <td className="table-cell">
                        <span className={\`text-xs font-semibold px-2 py-0.5 rounded-full \${statusColor}\`}>
                          {statusText}
                        </span>
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
