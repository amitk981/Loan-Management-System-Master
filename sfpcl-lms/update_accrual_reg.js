const fs = require('fs');

const file = 'src/pages/registers/RegistersHub.tsx';
let code = fs.readFileSync(file, 'utf8');

const oldTab = `{/* Tab 16: Accrual Register */}
        <div className="card p-0 overflow-hidden">
          <div className="p-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
            <div>
              <p className="text-sm font-semibold text-slate-900 flex items-center gap-2">
                <Calculator size={14} className="text-purple-600" /> Accrual Register
              </p>
              <p className="text-xs text-slate-500 mt-0.5">Monthly and quarterly interest accrual postings</p>
            </div>
            <button disabled={!canExport} className="flex items-center gap-1 text-xs text-green-700 hover:underline disabled:opacity-50 disabled:cursor-not-allowed disabled:no-underline">
              <Download size={12} /> Export
            </button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200">
                  <th className="table-header text-left">Accrual ID</th>
                  <th className="table-header text-left">Loan</th>
                  <th className="table-header text-left">Borrower</th>
                  <th className="table-header text-left">Period</th>
                  <th className="table-header text-right">Principal</th>
                  <th className="table-header text-right">Accrued</th>
                  <th className="table-header text-left">SAP Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {[
                  { acc: 'ACR-25-001', loan: 'LO00000042', borrower: 'Ganesh Thorat', period: 'Q2 FY 2025-26', principal: 1000000, accrued: 25000, status: 'pending' },
                  { acc: 'ACR-25-002', loan: 'LO00000035', borrower: 'Kisan FPC Ltd', period: 'Q2 FY 2025-26', principal: 2500000, accrued: 62500, status: 'posted' },
                ].map(a => (
                  <tr key={a.acc} className="hover:bg-slate-50">
                    <td className="table-cell font-mono text-slate-600">{a.acc}</td>
                    <td className="table-cell font-mono text-slate-600">{a.loan}</td>
                    <td className="table-cell font-medium text-slate-900">{a.borrower}</td>
                    <td className="table-cell text-slate-600">{a.period}</td>
                    <td className="table-cell num text-right">₹{a.principal.toLocaleString('en-IN')}</td>
                    <td className="table-cell num text-right font-semibold text-purple-700">₹{a.accrued.toLocaleString('en-IN')}</td>
                    <td className="table-cell"><StatusBadge label={a.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>`;

const newTab = `{/* Tab 16: Accrual Register */}
        <div className="card p-0 overflow-hidden">
          <div className="p-4 bg-slate-50 border-b border-slate-200">
            <p className="text-sm font-semibold text-slate-900 flex items-center gap-2">
              <Calculator size={14} className="text-purple-600" /> Accrual register
            </p>
            <p className="text-xs text-slate-500 mt-0.5">Interest accrual postings and SAP status</p>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200">
                  <th className="table-header text-left">Accrual ID</th>
                  <th className="table-header text-left">Loan Account</th>
                  <th className="table-header text-left">Borrower</th>
                  <th className="table-header text-left">Period</th>
                  <th className="table-header text-right">Principal Basis</th>
                  <th className="table-header text-right">Accrued Interest</th>
                  <th className="table-header text-left">Accrual Date</th>
                  <th className="table-header text-left">SAP Ref</th>
                  <th className="table-header text-left">SAP Posting</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {[
                  { acc: 'ACR-25-001', lnId: 'ln001', period: 'Q2 FY 2025–26', principal: 1000000, accrued: 25000, accrualDate: '2025-09-30', status: 'posting_pending', sapRef: null, generatedBy: 'Accounts' },
                  { acc: 'ACR-25-002', lnId: 'ln002', period: 'Q2 FY 2025–26', principal: 2500000, accrued: 62500, accrualDate: '2025-09-30', status: 'posted', sapRef: 'DOC-90111', generatedBy: 'Accounts' },
                ].map(a => {
                  const matchedLoan = loanAccounts.find(l => l.id === a.lnId);
                  const displayLoan = matchedLoan ? (matchedLoan.accountNumber || matchedLoan.applicationNumber) : a.lnId;
                  const displayBorrower = matchedLoan ? matchedLoan.borrowerName : 'Unknown';

                  const statusMap: Record<string, string> = {
                    posting_pending: 'Posting pending',
                    posted: 'Posted',
                    failed: 'Failed',
                    rework_required: 'Rework required',
                    not_required: 'Not required'
                  };
                  let displayStatus = statusMap[a.status] || a.status;
                  
                  // Enforcement: Do not show "Posted" without SAP ref
                  if (displayStatus === 'Posted' && !a.sapRef) {
                    displayStatus = 'Posting pending';
                  }

                  const dtFormat = new Intl.DateTimeFormat('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
                  const dateText = dtFormat.format(new Date(a.accrualDate));

                  const statusColor = displayStatus === 'Posted' ? 'bg-green-100 text-green-700' :
                                      displayStatus === 'Posting pending' ? 'bg-amber-100 text-amber-700' :
                                      displayStatus === 'Failed' || displayStatus === 'Rework required' ? 'bg-red-100 text-red-700' :
                                      'bg-slate-100 text-slate-700';

                  return (
                    <tr key={a.acc} className="hover:bg-slate-50">
                      <td className="table-cell font-mono text-slate-600">{a.acc}</td>
                      <td className="table-cell font-mono text-slate-600">{displayLoan}</td>
                      <td className="table-cell font-medium text-slate-900">{displayBorrower}</td>
                      <td className="table-cell text-slate-600">{a.period}</td>
                      <td className="table-cell num text-right text-slate-600">{fmt(a.principal)}</td>
                      <td className="table-cell num text-right font-semibold text-purple-700">{fmt(a.accrued)}</td>
                      <td className="table-cell text-slate-600">{dateText}</td>
                      <td className="table-cell text-xs font-mono text-slate-500">{a.sapRef || '—'}</td>
                      <td className="table-cell">
                        <span className={\`text-xs font-semibold px-2 py-0.5 rounded-full \${statusColor}\`}>
                          {displayStatus}
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
