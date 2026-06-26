const fs = require('fs');

const file = 'src/pages/registers/RegistersHub.tsx';
let code = fs.readFileSync(file, 'utf8');

const oldTab = `{/* Tab 15: Interest Invoice Register */}
        <div className="card p-0 overflow-hidden">
          <div className="p-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
            <div>
              <p className="text-sm font-semibold text-slate-900 flex items-center gap-2">
                <ReceiptText size={14} className="text-indigo-600" /> Interest Invoice Register
              </p>
              <p className="text-xs text-slate-500 mt-0.5">Annual borrower interest invoices and payment status</p>
            </div>
            <button disabled={!canExport} className="flex items-center gap-1 text-xs text-green-700 hover:underline disabled:opacity-50 disabled:cursor-not-allowed disabled:no-underline">
              <Download size={12} /> Export
            </button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200">
                  <th className="table-header text-left">Invoice</th>
                  <th className="table-header text-left">Loan</th>
                  <th className="table-header text-left">Borrower</th>
                  <th className="table-header text-left">Period</th>
                  <th className="table-header text-right">Amount</th>
                  <th className="table-header text-left">Due By</th>
                  <th className="table-header text-left">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {[
                  { inv: 'INV-2025-001', loan: 'LO00000042', borrower: 'Ganesh Thorat', period: 'FY 2024-25', amount: 45000, due: '2025-04-30', status: 'sent' },
                  { inv: 'INV-2025-002', loan: 'LO00000035', borrower: 'Kisan FPC Ltd', period: 'FY 2024-25', amount: 80000, due: '2025-04-30', status: 'draft' },
                ].map(i => (
                  <tr key={i.inv} className="hover:bg-slate-50">
                    <td className="table-cell font-mono text-slate-600">{i.inv}</td>
                    <td className="table-cell font-mono text-slate-600">{i.loan}</td>
                    <td className="table-cell font-medium text-slate-900">{i.borrower}</td>
                    <td className="table-cell text-slate-600">{i.period}</td>
                    <td className="table-cell num text-right font-semibold">₹{i.amount.toLocaleString('en-IN')}</td>
                    <td className="table-cell text-slate-600">{i.due}</td>
                    <td className="table-cell"><StatusBadge label={i.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>`;

const newTab = `{/* Tab 15: Interest Invoice Register */}
        <div className="card p-0 overflow-hidden">
          <div className="p-4 bg-slate-50 border-b border-slate-200">
            <p className="text-sm font-semibold text-slate-900 flex items-center gap-2">
              <ReceiptText size={14} className="text-indigo-600" /> Interest invoice register
            </p>
            <p className="text-xs text-slate-500 mt-0.5">Annual interest invoices and payment status</p>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200">
                  <th className="table-header text-left">Invoice No.</th>
                  <th className="table-header text-left">Loan Account</th>
                  <th className="table-header text-left">Borrower</th>
                  <th className="table-header text-left">Period</th>
                  <th className="table-header text-right">Invoice Amount</th>
                  <th className="table-header text-left">Due Date</th>
                  <th className="table-header text-left">Payment Status</th>
                  <th className="table-header text-left">SAP Posting</th>
                  <th className="table-header text-left">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {[
                  { inv: 'INV-2025-001', lnId: 'ln001', period: 'FY 2024–25', amount: 450000, due: '2025-04-30', rawStatus: 'sent', sentDate: '2025-04-01', paymentStatus: 'unpaid', paidAmount: 0, paidDate: null, sapStatus: 'posted_to_sap' },
                  { inv: 'INV-2025-002', lnId: 'ln002', period: 'FY 2024–25', amount: 800000, due: '2025-04-30', rawStatus: 'draft', sentDate: null, paymentStatus: 'unpaid', paidAmount: 0, paidDate: null, sapStatus: 'posting_pending' },
                ].map(i => {
                  const matchedLoan = loanAccounts.find(l => l.id === i.lnId);
                  const displayLoan = matchedLoan ? (matchedLoan.accountNumber || matchedLoan.applicationNumber) : i.lnId;
                  const displayBorrower = matchedLoan ? matchedLoan.borrowerName : 'Unknown';

                  const dueDate = new Date(i.due);
                  const now = new Date();
                  
                  let derivedStatus = i.rawStatus;
                  if (i.rawStatus === 'sent' && i.paymentStatus === 'unpaid' && now > dueDate) {
                    derivedStatus = 'overdue';
                  } else if (i.paymentStatus === 'paid') {
                    derivedStatus = 'paid';
                  } else if (i.paymentStatus === 'part_paid') {
                    derivedStatus = 'part_paid';
                  }

                  const statusMap: Record<string, string> = {
                    draft: 'Draft',
                    sent: 'Sent',
                    paid: 'Paid',
                    part_paid: 'Part-paid',
                    overdue: 'Overdue',
                    cancelled: 'Cancelled'
                  };
                  const displayStatus = statusMap[derivedStatus] || derivedStatus;
                  
                  const paymentMap: Record<string, string> = {
                    unpaid: 'Unpaid',
                    paid: 'Paid',
                    part_paid: 'Part-paid'
                  };
                  const displayPayment = paymentMap[i.paymentStatus] || i.paymentStatus;
                  
                  const sapMap: Record<string, string> = {
                    posted_to_sap: 'Posted to SAP',
                    posting_pending: 'Posting pending',
                    failed: 'Failed'
                  };
                  const displaySap = sapMap[i.sapStatus] || i.sapStatus;
                  
                  const dtFormat = new Intl.DateTimeFormat('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
                  const displayDueDate = dtFormat.format(dueDate);
                  
                  const statusColor = displayStatus === 'Paid' ? 'bg-green-100 text-green-700' :
                                      displayStatus === 'Overdue' || displayStatus === 'Cancelled' ? 'bg-red-100 text-red-700' :
                                      displayStatus === 'Sent' || displayStatus === 'Part-paid' ? 'bg-amber-100 text-amber-700' :
                                      'bg-slate-100 text-slate-700';
                                      
                  const paymentColor = displayPayment === 'Paid' ? 'text-green-700' :
                                       displayPayment === 'Unpaid' && displayStatus === 'Overdue' ? 'text-red-700 font-medium' :
                                       'text-slate-600';

                  return (
                    <tr key={i.inv} className="hover:bg-slate-50">
                      <td className="table-cell font-mono text-slate-600">{i.inv}</td>
                      <td className="table-cell font-mono text-slate-600">{displayLoan}</td>
                      <td className="table-cell font-medium text-slate-900">{displayBorrower}</td>
                      <td className="table-cell font-medium text-slate-700">{i.period}</td>
                      <td className="table-cell num text-right font-semibold text-slate-900">{fmt(i.amount)}</td>
                      <td className="table-cell text-slate-600">{displayDueDate}</td>
                      <td className={\`table-cell text-xs \${paymentColor}\`}>{displayPayment}</td>
                      <td className="table-cell text-xs text-slate-500">{displaySap}</td>
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
