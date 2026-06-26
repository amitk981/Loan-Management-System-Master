const fs = require('fs');

const file = 'src/pages/registers/RegistersHub.tsx';
let code = fs.readFileSync(file, 'utf8');

const oldTab = `{/* Tab 7: Grievance Register */}
        <div className="card p-0 overflow-hidden">
          <div className="p-4 bg-slate-50 border-b border-slate-200">
            <p className="text-sm font-semibold text-slate-900 flex items-center gap-2">
              <AlertOctagon size={14} className="text-amber-500" /> Grievance Register
            </p>
            <p className="text-xs text-slate-500 mt-0.5">All borrower grievances — 7-day resolution SLA</p>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200">
                  <th className="table-header text-left">Ref No.</th>
                  <th className="table-header text-left">Borrower</th>
                  <th className="table-header text-left">Subject</th>
                  <th className="table-header text-left">Raised On</th>
                  <th className="table-header text-left">Status</th>
                  <th className="table-header text-left">CS Response</th>
                  <th className="table-header text-left">Resolved On</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {[
                  { ref: 'GR-001', borrower: 'Ganesh Thorat',   subject: 'Interest calculation query',        date: '2025-01-10', status: 'resolved', response: 'Interest calculated at 12% p.a. on outstanding principal per agreement.', resolved: '2025-01-17' },
                  { ref: 'GR-002', borrower: 'Sunita Kamble',   subject: 'Repayment receipt not received',    date: '2025-03-05', status: 'resolved', response: 'Receipt sent via registered email. Physical copy couriered.', resolved: '2025-03-10' },
                  { ref: 'GR-003', borrower: 'Kiran Pawar',     subject: 'Delay in NOC after repayment',      date: '2025-05-20', status: 'in_progress', response: 'Under CS review — NOC generation in progress.', resolved: null },
                ].map(g => (
                  <tr key={g.ref} className="hover:bg-slate-50">
                    <td className="table-cell font-mono text-slate-600">{g.ref}</td>
                    <td className="table-cell font-medium text-slate-900">{g.borrower}</td>
                    <td className="table-cell text-slate-700">{g.subject}</td>
                    <td className="table-cell">{g.date}</td>
                    <td className="table-cell"><StatusBadge label={g.status} size="sm" /></td>
                    <td className="table-cell text-xs text-slate-500 max-w-xs truncate">{g.response}</td>
                    <td className="table-cell text-slate-500">{g.resolved || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>`;

const newTab = `{/* Tab 7: Grievance Register */}
        <div className="card p-0 overflow-hidden">
          <div className="p-4 bg-slate-50 border-b border-slate-200">
            <p className="text-sm font-semibold text-slate-900 flex items-center gap-2">
              <AlertOctagon size={14} className="text-amber-500" /> Grievance register
            </p>
            <p className="text-xs text-slate-500 mt-0.5">Borrower grievances and resolution status — 7-day TAT</p>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200">
                  <th className="table-header text-left">Grievance Ref</th>
                  <th className="table-header text-left">Borrower</th>
                  <th className="table-header text-left">Subject</th>
                  <th className="table-header text-left">Raised On</th>
                  <th className="table-header text-left">SLA Due</th>
                  <th className="table-header text-left">Status</th>
                  <th className="table-header text-left">Resolution Note</th>
                  <th className="table-header text-left">Resolved On</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {[
                  { ref: 'GR-2025-001', borrower: 'Ganesh Thorat',   subject: 'Interest calculation query',        date: '2025-01-10', status: 'resolved', response: 'Interest calculated at 12% p.a. on outstanding principal as per agreement.', resolved: '2025-01-17', owner: 'Company Secretary' },
                  { ref: 'GR-2025-002', borrower: 'Sunita Kamble',   subject: 'Repayment receipt not received',    date: '2025-03-05', status: 'resolved', response: 'Receipt sent by registered email; physical copy couriered.', resolved: '2025-03-10', owner: 'Company Secretary' },
                  { ref: 'GR-2025-003', borrower: 'Kiran Pawar',     subject: 'Delay in NOC after repayment',      date: '2025-05-20', status: 'in_progress', response: 'NOC generation in progress under Company Secretary review.', resolved: null, owner: 'Company Secretary' },
                ].map(g => {
                  const raisedDate = new Date(g.date);
                  const slaDate = new Date(raisedDate);
                  slaDate.setDate(raisedDate.getDate() + 7);
                  
                  let displayStatus = g.status;
                  if (g.status !== 'resolved' && new Date() > slaDate) {
                    displayStatus = 'overdue';
                  }

                  const statusMap: Record<string, string> = {
                    in_progress: 'In progress',
                    resolved: 'Resolved',
                    overdue: 'Overdue',
                    open: 'Open',
                    escalated: 'Escalated'
                  };

                  let statusText = statusMap[displayStatus] || displayStatus;

                  const dtFormat = new Intl.DateTimeFormat('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
                  let raisedFmt = dtFormat.format(raisedDate);
                  let slaFmt = dtFormat.format(slaDate);
                  let resolvedFmt = g.resolved ? dtFormat.format(new Date(g.resolved)) : '—';
                  
                  const statusColor = statusText === 'Resolved' ? 'bg-green-100 text-green-700' :
                                      statusText === 'Overdue' || statusText === 'Escalated' ? 'bg-red-100 text-red-700' :
                                      statusText === 'In progress' ? 'bg-amber-100 text-amber-700' :
                                      'bg-slate-100 text-slate-700';

                  return (
                  <tr key={g.ref} className={\`hover:bg-slate-50 \${statusText === 'Overdue' ? 'bg-red-50/20' : ''}\`}>
                    <td className="table-cell font-mono text-slate-600">{g.ref}</td>
                    <td className="table-cell font-medium text-slate-900">{g.borrower}</td>
                    <td className="table-cell text-slate-700">{g.subject}</td>
                    <td className="table-cell text-slate-600">{raisedFmt}</td>
                    <td className="table-cell text-slate-500 font-medium">{slaFmt}</td>
                    <td className="table-cell">
                      <span className={\`text-xs font-semibold px-2 py-0.5 rounded-full \${statusColor}\`}>
                        {statusText}
                      </span>
                    </td>
                    <td className="table-cell text-xs text-slate-500 max-w-xs truncate" title={g.response}>{g.response}</td>
                    <td className="table-cell text-slate-500">{resolvedFmt}</td>
                  </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>`;

code = code.replace(oldTab, newTab);

fs.writeFileSync(file, code);
console.log("update complete");
