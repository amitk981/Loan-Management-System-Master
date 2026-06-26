const fs = require('fs');

// Fix Tabs focus-visible
const tabsFile = 'src/components/ui/Tabs.tsx';
let tabsCode = fs.readFileSync(tabsFile, 'utf8');
tabsCode = tabsCode.replace(
  `className={\`flex items-center gap-1.5 px-4 py-3 text-sm font-medium border-b-2 transition-colors whitespace-nowrap \${`,
  `className={\`flex items-center gap-1.5 px-4 py-3 text-sm font-medium border-b-2 transition-colors whitespace-nowrap focus:outline-none focus-visible:ring-2 focus-visible:ring-green-500/50 \${`
);
fs.writeFileSync(tabsFile, tabsCode);


// Fix RegistersHub Credit Sanction Tab
const registersFile = 'src/pages/registers/RegistersHub.tsx';
let code = fs.readFileSync(registersFile, 'utf8');

code = code.replace(
  `const sanctionedApps = loanApplications.filter(a => a.sanctionDecision === 'approved');`,
  `const sanctionDecisions = loanApplications.filter(a => a.sanctionDecision === 'approved' || a.sanctionDecision === 'rejected');`
);

code = code.replace(
  `<p className="text-sm font-semibold text-slate-900 flex items-center gap-2">
              <Gavel size={14} className="text-green-600" /> Credit Sanction Register
            </p>
            <p className="text-xs text-slate-500 mt-0.5">All sanctioned loan applications — {sanctionedApps.length} records</p>`,
  `<p className="text-sm font-semibold text-slate-900 flex items-center gap-2">
              <Gavel size={14} className="text-green-600" /> Credit sanction register
            </p>
            <p className="text-xs text-slate-500 mt-0.5">All sanction decisions — {sanctionDecisions.length} records</p>`
);

code = code.replace(
  `<th className="table-header text-left">Sanctioned On</th>
                  <th className="table-header text-left">Sanctioned By</th>`,
  `<th className="table-header text-left">Decision date</th>
                  <th className="table-header text-left">Approval authority</th>`
);

const oldRowLoop = `{sanctionedApps.map(app => (
                  <tr key={app.id} className="hover:bg-slate-50">
                    <td className="table-cell num font-semibold text-green-700">{app.applicationNumber}</td>
                    <td className="table-cell font-medium">{app.memberName}</td>
                    <td className="table-cell text-right num">{fmt(app.requestedAmount)}</td>
                    <td className="table-cell">
                      <span className="text-xs font-semibold bg-green-100 text-green-700 px-2 py-0.5 rounded-full capitalize">
                        {app.sanctionDecision}
                      </span>
                    </td>
                    <td className="table-cell">{app.sanctionedAt ? new Date(app.sanctionedAt).toLocaleDateString('en-IN') : '—'}</td>
                    <td className="table-cell text-slate-600">CFO + {app.requestedAmount > 500000 ? '2 Directors' : '1 Director'}</td>
                    <td className="table-cell">
                      {app.isException ? (
                        <span className="flex items-center gap-1 text-xs text-violet-700">
                          <AlertOctagon size={12} /> Yes
                        </span>
                      ) : (
                        <span className="text-xs text-green-600">No</span>
                      )}
                    </td>
                  </tr>
                ))}`;

const newRowLoop = `{sanctionDecisions.map(app => {
                  let authority = app.requestedAmount > 500000 ? 'CFO + 2 Directors' : 'CFO + 1 Director';
                  
                  let exceptionDisplay = 'None';
                  if (app.isException) {
                     if (app.sanctionDecision === 'approved') {
                       exceptionDisplay = 'Approved';
                     } else if (app.sanctionDecision === 'rejected') {
                       exceptionDisplay = 'Rejected';
                     } else {
                       exceptionDisplay = 'Open';
                     }
                  }
                  
                  let formattedDate = '—';
                  if (app.sanctionedAt) {
                    formattedDate = new Intl.DateTimeFormat('en-GB', { day: 'numeric', month: 'short', year: 'numeric' }).format(new Date(app.sanctionedAt));
                  }

                  let decisionBadgeColor = app.sanctionDecision === 'approved' ? 'bg-green-100 text-green-700' : app.sanctionDecision === 'rejected' ? 'bg-red-100 text-red-700' : 'bg-slate-100 text-slate-700';

                  return (
                  <tr key={app.id} className="hover:bg-slate-50">
                    <td className="table-cell num font-semibold text-green-700">{app.applicationNumber}</td>
                    <td className="table-cell font-medium">{app.memberName}</td>
                    <td className="table-cell text-right num">{fmt(app.requestedAmount)}</td>
                    <td className="table-cell">
                      <span className={\`text-xs font-semibold px-2 py-0.5 rounded-full capitalize \${decisionBadgeColor}\`}>
                        {app.sanctionDecision}
                      </span>
                    </td>
                    <td className="table-cell text-slate-600">{formattedDate}</td>
                    <td className="table-cell text-slate-600">{authority}</td>
                    <td className="table-cell">
                      {app.isException ? (
                        <span className={\`flex items-center gap-1 text-xs font-semibold \${exceptionDisplay === 'Rejected' ? 'text-red-700' : 'text-violet-700'}\`}>
                          <AlertOctagon size={12} /> {exceptionDisplay}
                        </span>
                      ) : (
                        <span className="text-xs text-green-600 font-medium">None</span>
                      )}
                    </td>
                  </tr>
                )
     })}`;

code = code.replace(oldRowLoop, newRowLoop);
fs.writeFileSync(registersFile, code);

console.log("updates complete");
