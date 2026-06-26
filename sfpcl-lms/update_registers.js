const fs = require('fs');

const file = 'src/pages/registers/RegistersHub.tsx';
let code = fs.readFileSync(file, 'utf8');

// Title & Subtitle
code = code.replace(
  `SOP Registers`,
  `Registers`
);
code = code.replace(
  `All statutory and internal registers · 8-year retention policy`,
  `Statutory and internal registers · 8-year retention`
);

// Tab labels
code = code.replace(
  `const REGISTER_TABS = [
  { id: 'loan_register',      label: 'Loan Account Register' },
  { id: 'loan_request_register', label: 'Loan Request Register' },
  { id: 'sanction_register',  label: 'Credit Sanction Register' },
  { id: 'security_register',  label: 'Security Register' },
  { id: 'exception_register', label: 'Exception Register' },
  { id: 'member_register',    label: 'Member Register' },
  { id: 'compliance_register', label: 'Compliance Register' },
  { id: 'stamp_duty',         label: 'Stamp Duty Register' },
  { id: 'audit_log',          label: 'Audit Log Explorer' },
  { id: 'grievance_register', label: 'Grievance Register' },
  { id: 'recovery_log',       label: 'Recovery Log' },
  { id: 'blank_cheque_register', label: 'Blank-Dated Cheque Register' },
  { id: 'sh4_register',       label: 'SH-4 Register' },
  { id: 'cdsl_register',      label: 'CDSL Pledge Register' },
  { id: 'sap_register',       label: 'SAP Customer Code Register' },
  { id: 'disbursement_register', label: 'Disbursement Register' },
  { id: 'repayment_register', label: 'Repayment Register' },
  { id: 'interest_invoice_register', label: 'Interest Invoice Register' },
  { id: 'accrual_register',   label: 'Accrual Register' },
  { id: 'dpd_register',       label: 'DPD / Monitoring Register' },
  { id: 'noc_register',       label: 'NOC / Closure Register' },
  { id: 'archive_register',   label: 'Archive Register' },
  { id: 'sop_change_register', label: 'SOP Change Register' },
];`,
  `const REGISTER_TABS = [
  { id: 'loan_register',      label: 'Loan account register' },
  { id: 'loan_request_register', label: 'Loan request register' },
  { id: 'sanction_register',  label: 'Credit sanction register' },
  { id: 'security_register',  label: 'Security register' },
  { id: 'exception_register', label: 'Exception register' },
  { id: 'member_register',    label: 'Member register' },
  { id: 'compliance_register', label: 'Compliance register' },
  { id: 'stamp_duty',         label: 'Stamp duty register' },
  { id: 'audit_log',          label: 'Audit log explorer' },
  { id: 'grievance_register', label: 'Grievance register' },
  { id: 'recovery_log',       label: 'Recovery log' },
  { id: 'blank_cheque_register', label: 'Blank-dated cheque register' },
  { id: 'sh4_register',       label: 'SH-4 register' },
  { id: 'cdsl_register',      label: 'CDSL pledge register' },
  { id: 'sap_register',       label: 'SAP customer code register' },
  { id: 'disbursement_register', label: 'Disbursement register' },
  { id: 'repayment_register', label: 'Repayment register' },
  { id: 'interest_invoice_register', label: 'Interest invoice register' },
  { id: 'accrual_register',   label: 'Accrual register' },
  { id: 'dpd_register',       label: 'DPD / monitoring register' },
  { id: 'noc_register',       label: 'NOC / closure register' },
  { id: 'archive_register',   label: 'Archive register' },
  { id: 'sop_change_register', label: 'SOP change register' },
];`
);

// Add dynamic DPD and Status calculations
const dpdCalcStr = `
  const canExport = can('export_reports');
  const processedLoans = loanAccounts.map(l => {
    const due = new Date(l.repaymentDueDate);
    const diffDays = Math.floor((new Date().getTime() - due.getTime()) / (1000 * 3600 * 24));
    let calcDpd = l.status === 'closed' ? null : Math.max(0, diffDays);
    let displayStatus = l.status;
    let outstanding = l.status === 'closed' ? 0 : l.outstandingPrincipal;
    
    if (l.status === 'closed') {
      displayStatus = 'closed';
    } else if (calcDpd !== null && calcDpd > 90 && l.status === 'grace_period') {
      displayStatus = 'default_review';
    } else if (l.status === 'recovery_in_progress') {
      const hasRecovery = auditEvents.some(a => a.entityId === l.id && a.eventType === 'Default Recovery Action Initiated');
      if (!hasRecovery) displayStatus = 'default_review';
    } else if (calcDpd !== null && calcDpd > 0 && l.status === 'active') {
      displayStatus = 'overdue';
    }
    
    return { ...l, calcDpd, displayStatus, outstanding };
  });
`;

code = code.replace(
  `  const exceptions = loanApplications.filter(a => a.isException);`,
  dpdCalcStr + `\n  const exceptions = loanApplications.filter(a => a.isException);`
);

// Tab 0 Title & Headers
code = code.replace(
  `<p className="text-sm font-semibold text-slate-900 flex items-center gap-2">
                <FileText size={14} className="text-green-600" /> Loan Register
              </p>
              <p className="text-xs text-slate-500 mt-0.5">All loan accounts — {loanAccounts.length} records</p>`,
  `<p className="text-sm font-semibold text-slate-900 flex items-center gap-2">
                <FileText size={14} className="text-green-600" /> Loan account register
              </p>
              <p className="text-xs text-slate-500 mt-0.5">Showing {loanAccounts.length} of 23 loan accounts</p>`
);

code = code.replace(
  `<th className="table-header text-right">Rate</th>
                  <th className="table-header text-left">Status</th>
                  <th className="table-header text-left">SAP Code</th>
                  <th className="table-header text-right">DPD</th>
                  <th className="table-header text-left">Due Date</th>`,
  `<th className="table-header text-right">Current rate</th>
                  <th className="table-header text-left">Status</th>
                  <th className="table-header text-left">SAP code</th>
                  <th className="table-header text-right">DPD</th>
                  <th className="table-header text-left">Repayment due date</th>`
);

// Table row for Loan account register
code = code.replace(
  `{loanAccounts.map(l => (
                  <tr key={l.id} className="hover:bg-slate-50">
                    <td className="table-cell num font-semibold text-green-700">{l.accountNumber}</td>
                    <td className="table-cell font-medium">{l.memberName}</td>
                    <td className="table-cell text-right num">{fmt(l.disbursedAmount)}</td>
                    <td className="table-cell text-right num font-semibold">{fmt(l.outstandingPrincipal)}</td>
                    <td className="table-cell text-right">{l.interestRate}%</td>
                    <td className="table-cell"><StatusBadge label={l.status} size="sm" /></td>
                    <td className="table-cell num text-slate-600">{l.sapCustomerCode}</td>
                    <td className="table-cell text-right">
                      <span className={\`font-bold num \${l.dpd > 90 ? 'text-red-600' : l.dpd > 0 ? 'text-amber-600' : 'text-green-600'}\`}>{l.dpd}</span>
                    </td>
                    <td className="table-cell">{new Date(l.repaymentDueDate).toLocaleDateString('en-IN')}</td>
                  </tr>
                ))}`,
  `{processedLoans.map(l => (
                  <tr key={l.id} className="hover:bg-slate-50">
                    <td className="table-cell num font-semibold text-green-700">{l.accountNumber}</td>
                    <td className="table-cell font-medium">{l.memberName}</td>
                    <td className="table-cell text-right num">{fmt(l.disbursedAmount)}</td>
                    <td className="table-cell text-right num font-semibold">{fmt(l.outstanding)}</td>
                    <td className="table-cell text-right">{l.interestRate}%</td>
                    <td className="table-cell"><StatusBadge label={l.displayStatus} size="sm" /></td>
                    <td className="table-cell num text-slate-600">{l.sapCustomerCode}</td>
                    <td className="table-cell text-right">
                      {l.calcDpd !== null ? (
                        <span className={\`font-bold num \${l.calcDpd > 90 ? 'text-red-600' : l.calcDpd > 0 ? 'text-amber-600' : 'text-green-600'}\`}>{l.calcDpd}</span>
                      ) : (
                        <span className="text-slate-400">—</span>
                      )}
                    </td>
                    <td className="table-cell">{new Date(l.repaymentDueDate).toLocaleDateString('en-IN')}</td>
                  </tr>
                ))}`
);

// Export Permissions
code = code.replace(
  `<button className="btn-secondary flex items-center gap-2 text-sm">
          <Archive size={14} />
          Export Register
        </button>`,
  `<button disabled={!canExport} className="btn-secondary flex items-center gap-2 text-sm disabled:opacity-50 disabled:cursor-not-allowed">
          <Archive size={14} />
          Export Register
        </button>`
);

// Fix Stamp Duty Register title case
code = code.replace(
  `<p className="text-sm font-semibold text-slate-900 flex items-center gap-2">
                <FileText size={14} className="text-green-600" /> Stamp Duty Register
              </p>`,
  `<p className="text-sm font-semibold text-slate-900 flex items-center gap-2">
                <FileText size={14} className="text-green-600" /> Stamp duty register
              </p>`
);

// All supplemental export buttons
code = code.replace(
  /<button className="flex items-center gap-1 text-xs text-green-700 hover:underline">/g,
  `<button disabled={!canExport} className="flex items-center gap-1 text-xs text-green-700 hover:underline disabled:opacity-50 disabled:cursor-not-allowed disabled:no-underline">`
);

fs.writeFileSync(file, code);
console.log("update complete");
