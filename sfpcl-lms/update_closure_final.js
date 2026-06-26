const fs = require('fs');
const file = 'src/pages/closure/LoanClosureHub.tsx';
let code = fs.readFileSync(file, 'utf8');

// 1. Copy changes
code = code.replace("Closure Status", "Closure status");
code = code.replace("Current status across NOC, security return, archive and audit.", "Current readiness for NOC, security return, archive and audit.");
code = code.replace(/Borrower Communication \(MP20\)/g, "Borrower communication");
code = code.replace(/Borrower Communication/g, "Borrower communication");

// Fix publication impact
code = code.replace(
  `    { label: 'Borrower communication', status: nocComplete ? 'published' : nocGenerated ? 'ready_to_publish' : 'not_ready', note: nocGenerated ? 'Closure/NOC status is staged for the borrower portal.' : 'Publish after NOC generation.' },
    { label: 'NOC Register', status: nocComplete ? 'updated' : 'pending', note: nocComplete ? 'NOC reference and issue date are visible in the register preview.' : 'Waiting for NOC issue.' },
    { label: 'Security Register', status: securityComplete ? 'returned' : 'held', note: securityComplete ? 'SH-4, cheque, PoA and CDSL release states are complete.' : 'Security remains in custody.' },
    { label: 'Archive Register', status: archiveComplete ? 'archived' : loanMarkedClosed ? 'ready' : 'pending', note: archiveComplete ? 'Archive ID and retention date are staged.' : 'Archive after closure checklist completion.' },
    { label: 'Audit Trail', status: 'updated', note: 'Local prototype events show closure, NOC, security return and archive actions.' },`,
  `    { label: 'Borrower communication', status: nocSent ? 'sent' : nocComplete ? 'ready' : 'not_ready', note: nocSent ? 'Communication sent to borrower.' : 'Send after NOC is issued.' },
    { label: 'NOC Register', status: nocComplete ? 'issued' : 'pending', note: nocComplete ? 'NOC reference and issue date are visible in the register.' : 'Waiting for NOC issue.' },
    { label: 'Security Register', status: securityComplete ? 'returned' : (cdslUnpledgeStart || sh4Returned || chequeReturned || poaReturned) ? 'return_pending' : 'held_in_custody', note: securityComplete ? 'SH-4, cheque, PoA and CDSL release states are complete.' : 'Security return pending.' },
    { label: 'Archive Register', status: archiveComplete ? 'archived' : 'pending', note: archiveComplete ? 'Archive ID and retention date are staged.' : 'Archive after closure checklist completion.' },
    { label: 'Audit Trail', status: archiveComplete ? 'recorded' : 'in_progress', note: 'Closure events are recorded automatically.' },`
);

// 2. Loan level status consistency
code = code.replace(
  `  const getLoanStatus = (loan: ClosureLoan) => {
    if (loan.outstanding > 0) return 'Not Eligible';
    if (loan.status === 'closed') return 'Closed';
    if (archiveCompleted) return 'Archived';
    if (loanMarkedClosed) return 'Ready to Archive';
    if (!securityComplete) return 'Security Return Pending';
    if (!nocComplete) return 'NOC Pending';
    if (loan.status === 'fully_repaid') return 'Closure In Progress';
    return 'Fully Repaid';
  };`,
  `  const getLoanStatus = (loan: ClosureLoan) => {
    if (loan.outstanding > 0) return 'Blocked';
    if (loan.status === 'closed' && archiveComplete && nocComplete && securityComplete) return 'Closed';
    if (archiveCompleted) return 'Archived';
    if (loanMarkedClosed) return 'Ready to Archive';
    if (!securityComplete) return 'Security Return Pending';
    if (!nocComplete) return 'NOC Pending';
    if (loan.status === 'fully_repaid') return 'Closure in progress';
    return 'Fully repaid';
  };`
);

code = code.replace(
  `<StatusBadge label={loan.outstanding > 0 ? 'Not Eligible' : (loan.status === 'closed' ? 'Closed' : 'Closure In Progress')} size="sm" type={loan.outstanding > 0 ? 'slate' : 'default'} />`,
  `<StatusBadge label={loan.outstanding > 0 ? 'Blocked' : (loan.status === 'closed' ? 'Closed' : 'Closure in progress')} size="sm" type={loan.outstanding > 0 ? 'slate' : 'default'} />`
);

code = code.replace(
  `Closure cannot proceed — outstanding balance of ₹{selectedLoan.outstanding.toLocaleString('en-IN')} remains.`,
  `Closure blocked: ₹{selectedLoan.outstanding.toLocaleString('en-IN')} outstanding.`
);

// 4. NOC Generation Tab
const currentYear = new Date().getFullYear();
code = code.replace(`defaultValue: 'NOC-2025-042'`, `defaultValue: 'NOC-' + new Date().getFullYear() + '-042'`);

code = code.replace(
  `<option>Director - Operations</option>
                        <option>CFO</option>`,
  `<option>Company Secretary</option>
                        <option>Authorised closure signatory</option>`
);

code = code.replace(
  `<option>Email & Portal (MP20)</option>`,
  `<option>Email + portal</option>`
);

// 5. Security Return
code = code.replace(
  `[
                    { doc: 'SH-4 Transfer Form',   securityType: 'Physical share transfer',    status: securityComplete || sh4Returned ? 'Returned' : 'Held in Custody', onReturn: () => setSh4Returned(true) },
                    { doc: 'Blank Cheque',         securityType: 'Cheque returned to borrower', status: securityComplete || chequeReturned ? 'Returned' : 'Held in Custody', onReturn: () => setChequeReturned(true) },
                    { doc: 'CDSL Pledge Release',  securityType: 'Demat shares unpledged',      status: securityComplete || cdslUnpledged ? 'Unpledged' : cdslUnpledgeStart ? 'Unpledge Pending' : 'Pledge Active', onReturn: () => cdslUnpledgeStart ? setCdslUnpledged(true) : setCdslUnpledgeStart(true), actionText: cdslUnpledgeStart ? 'Mark Unpledge Complete' : 'Start Unpledge' },
                    { doc: 'Power of Attorney',    securityType: 'PoA cancelled/returned',      status: securityComplete || poaReturned ? 'Returned' : 'Held in Custody', onReturn: () => setPoaReturned(true) },
                  ]`,
  `[
                    { doc: 'SH-4 Transfer Form',   securityType: 'Original held; return pending',    status: securityComplete || sh4Returned ? 'Returned' : 'Held in custody', onReturn: () => setSh4Returned(true) },
                    { doc: 'Blank Cheque',         securityType: 'Original held; return pending', status: securityComplete || chequeReturned ? 'Returned' : 'Held in custody', onReturn: () => setChequeReturned(true) },
                    { doc: 'CDSL Pledge Release',  securityType: 'Pledge active; unpledge pending',      status: securityComplete || cdslUnpledged ? 'Unpledged' : cdslUnpledgeStart ? 'Unpledge pending' : 'Pledge active', onReturn: () => cdslUnpledgeStart ? setCdslUnpledged(true) : setCdslUnpledgeStart(true), actionText: cdslUnpledgeStart ? 'Mark Unpledge Complete' : 'Start Unpledge' },
                    { doc: 'Power of Attorney',    securityType: 'Cancellation / return pending',      status: securityComplete || poaReturned ? 'Cancelled' : 'Held in custody', onReturn: () => setPoaReturned(true) },
                  ]`
);

// 6. Archive Tab
code = code.replace(
  `Records must be archived for at least 8 years after closure. Store digital and physical archive references.`,
  `Archive loan records for 8 years after closure. Keep digital backup and physical file location.`
);

code = code.replace(`8 years (until 2033)`, `8 years (until {new Date().getFullYear() + 8})`);

code = code.replace(
  `<div><div className="text-slate-500 text-xs">Archive ID</div><div className="font-semibold text-slate-900">ARC-2025-042</div></div>
                  <div><div className="text-slate-500 text-xs">Physical File Reference</div><div className="font-semibold text-slate-900">Cabinet 3, Row 2</div></div>`,
  `<div><div className="text-slate-500 text-xs">Archive ID</div><div className="font-semibold text-slate-900">{archiveCompleted ? 'ARC-2025-042' : 'Not assigned'}</div></div>
                  <div><div className="text-slate-500 text-xs">Physical File Reference</div><div className="font-semibold text-slate-900">{archiveCompleted ? 'Cabinet 3, Row 2' : 'Not assigned'}</div></div>`
);

fs.writeFileSync(file, code);
console.log("update complete");
