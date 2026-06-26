const fs = require('fs');

const file = 'src/pages/registers/RegistersHub.tsx';
let code = fs.readFileSync(file, 'utf8');

// Title & Subtitle for Tab 1
code = code.replace(
  `<p className="text-sm font-semibold text-slate-900 flex items-center gap-2">
                <FileText size={14} className="text-green-600" /> Loan Request Register
              </p>
              <p className="text-xs text-slate-500 mt-0.5">All submitted and draft loan requests before account creation — {loanApplications.length} records</p>`,
  `<p className="text-sm font-semibold text-slate-900 flex items-center gap-2">
                <FileText size={14} className="text-green-600" /> Loan request register
              </p>
              <p className="text-xs text-slate-500 mt-0.5">All loan requests and application references — {loanApplications.length} records</p>`
);

// Table column labels
code = code.replace(
  `<th className="table-header text-right">Requested</th>
                  <th className="table-header text-right">Eligible</th>`,
  `<th className="table-header text-right">Requested amount</th>
                  <th className="table-header text-right">Eligible limit</th>`
);

// Add mapping block inside the loan request map
code = code.replace(
  `{loanApplications.map(app => (
                  <tr key={app.id} className={\`hover:bg-slate-50 \${app.isException ? 'bg-violet-50/30' : ''}\`}>
                    <td className="table-cell num font-semibold text-green-700">{app.applicationNumber}</td>
                    <td className="table-cell font-medium">{app.memberName}</td>
                    <td className="table-cell capitalize">{app.memberType.replace('_', ' ')}</td>
                    <td className="table-cell text-right num">{fmt(app.requestedAmount)}</td>
                    <td className="table-cell text-right num">{fmt(app.eligibleAmount)}</td>
                    <td className="table-cell capitalize">{app.purpose.replace(/_/g, ' ')}</td>
                    <td className="table-cell"><StatusBadge label={app.status} size="sm" /></td>
                    <td className="table-cell text-slate-600">{app.currentOwner}</td>
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
                ))}`,
  `{loanApplications.map(app => {
                  const typeMap: Record<string, string> = { individual: 'Individual', fpc: 'FPC', producer_institution: 'Producer Institution' };
                  const purposeMap: Record<string, string> = { crop_production: 'Crop production', agriculture_activity: 'Agriculture activity', allied_activity: 'Allied activity' };
                  
                  let displayType = typeMap[app.memberType] || app.memberType;
                  let displayPurpose = purposeMap[app.purpose] || app.purpose;
                  
                  let displayStatus = app.status;
                  if (app.status === 'sanctioned' && app.currentOwnerRole === 'compliance_team') {
                    displayStatus = 'documentation_pending';
                  }
                  
                  let displayOwner = app.currentOwner;
                  if (app.status === 'credit_review' && app.currentOwner === 'Deputy Manager – Finance') {
                    displayOwner = 'Credit Manager';
                  }

                  let displayEligible: string = fmt(app.eligibleAmount);
                  let exceptionDisplay = 'None';
                  let isExceptionActive = false;
                  
                  if (app.status === 'incomplete') {
                    displayEligible = 'Not calculated';
                    exceptionDisplay = 'Pending review';
                  } else if (app.isException) {
                    isExceptionActive = true;
                    if (app.sanctionDecision === 'approved') {
                      exceptionDisplay = 'Approved';
                    } else {
                      exceptionDisplay = 'Open';
                    }
                  }

                  return (
                    <tr key={app.id} className={\`hover:bg-slate-50 \${isExceptionActive ? 'bg-violet-50/30' : ''}\`}>
                      <td className="table-cell num font-semibold text-green-700">{app.applicationNumber}</td>
                      <td className="table-cell font-medium">{app.memberName}</td>
                      <td className="table-cell">{displayType}</td>
                      <td className="table-cell text-right num">{fmt(app.requestedAmount)}</td>
                      <td className="table-cell text-right num font-medium text-slate-600">{displayEligible}</td>
                      <td className="table-cell">{displayPurpose}</td>
                      <td className="table-cell"><StatusBadge label={displayStatus} size="sm" /></td>
                      <td className="table-cell text-slate-600">{displayOwner}</td>
                      <td className="table-cell">
                        {isExceptionActive ? (
                          <span className="flex items-center gap-1 text-xs font-semibold text-violet-700">
                            <AlertOctagon size={12} /> {exceptionDisplay}
                          </span>
                        ) : exceptionDisplay === 'Pending review' ? (
                          <span className="text-xs text-slate-500 font-medium">{exceptionDisplay}</span>
                        ) : (
                          <span className="text-xs text-green-600 font-medium">None</span>
                        )}
                      </td>
                    </tr>
                  );
                })}`
);

fs.writeFileSync(file, code);
console.log("update complete");
