import React, { useState } from 'react';
import { useRole } from '../../contexts/RoleContext';
import { BookOpen, FileText, Scale, Gavel, AlertOctagon, RotateCcw, Archive, Stamp, Search, Download, History, Filter } from 'lucide-react';
import Tabs from '../../components/ui/Tabs';
import StatusBadge from '../../components/ui/StatusBadge';
import { loanApplications, loanAccounts, securities, members, complianceRecords, auditEvents } from '../../data/mockData';
import { getApplicationReference, getApplicationStatusLabel } from '../../utils/applicationDisplay';

const fmt = (n?: number) => n !== undefined && n !== null ? '₹' + n.toLocaleString('en-IN') : '—';

const REGISTER_TABS = [
  { id: 'loan_register',           label: 'Loan account register' },
  { id: 'loan_request_register',   label: 'Loan request register' },
  { id: 'sanction_register',       label: 'Credit sanction register' },
  { id: 'security_register',       label: 'Security register' },
  { id: 'exception_register',      label: 'Exception register' },
  { id: 'member_register',         label: 'Member register' },
  { id: 'compliance_register',     label: 'Compliance register' },
  { id: 'stamp_duty',              label: 'Stamp duty register' },
  { id: 'audit_log',               label: 'Audit log' },
  { id: 'grievance_register',      label: 'Grievance register' },
  { id: 'recovery_log',            label: 'Recovery log' },
  { id: 'blank_cheque_register',   label: 'Blank-dated cheque register' },
  { id: 'sh4_register',            label: 'SH-4 register' },
  { id: 'cdsl_register',           label: 'CDSL pledge register' },
  { id: 'sap_register',            label: 'SAP customer code register' },
  { id: 'disbursement_register',   label: 'Disbursement register' },
  { id: 'repayment_register',      label: 'Repayment register' },
  { id: 'interest_invoice_register', label: 'Interest invoice register' },
  { id: 'accrual_register',        label: 'Accrual register' },
  { id: 'dpd_register',            label: 'DPD / monitoring register' },
  { id: 'noc_register',            label: 'NOC / closure register' },
  { id: 'archive_register',        label: 'Archive register' },
  { id: 'sop_change_register',     label: 'SOP change register' },
];

interface RegistersHubProps {
  onOpenLoan?: (id: string) => void;
  onOpenApplication?: (id: string) => void;
}

const RegistersHub: React.FC<RegistersHubProps> = ({ onOpenLoan, onOpenApplication }) => {
  const { can } = useRole();
  const [activeTab, setActiveTab] = useState(0);
  const [auditSearch, setAuditSearch] = useState('');
  const [auditRoleFilter, setAuditRoleFilter] = useState('all');
  const [auditEntityFilter, setAuditEntityFilter] = useState('all');
  const [auditDateFrom, setAuditDateFrom] = useState('');
  const [auditDateTo, setAuditDateTo] = useState('');


  const canExport = can('export_registers');
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
    } else if (l.status === 'recovery_in_progress' || l.status === 'recovery_review') {
      const hasRecovery = auditEvents.some(a => a.entityId === l.id && a.eventType === 'Default Recovery Action Initiated');
      if (!hasRecovery) displayStatus = 'recovery_review';
    } else if (calcDpd !== null && calcDpd > 0 && (l.status === 'active' || l.status === 'active_repayment')) {
      displayStatus = 'overdue';
    }
    
    return { ...l, calcDpd, displayStatus, outstanding };
  });

  const exceptions = loanApplications.filter(a => a.isException);
  const sanctionDecisions = loanApplications.filter(a => a.sanctionDecision === 'approved' || a.sanctionDecision === 'rejected');

  // Stamp duty data
  const stampDutyRecords = [
    { doc: 'Power of Attorney (PoA)', appNo: 'LO00000042', borrower: 'Ganesh Thorat', stampDutyAmt: 500, paidOn: '2024-09-18', status: 'paid', notarised: true, custodian: 'Company Secretary', challanNo: 'MSFM2024082100012' },
    { doc: 'SH-4 transfer form', appNo: 'LO00000042', borrower: 'Ganesh Thorat', stampDutyAmt: 'Not required', paidOn: '2024-09-15', status: 'paid', notarised: 'not_required', custodian: 'Company Secretary', challanNo: 'MSFM2024082100013' },
    { doc: 'Power of Attorney (PoA)', appNo: 'LO00000035', borrower: 'Kisan FPC Ltd', stampDutyAmt: 500, paidOn: '2026-04-22', status: 'paid', notarised: true, custodian: 'Company Secretary', challanNo: 'MSFM2026042200001' },
    { doc: 'Loan Agreement', appNo: 'LO00000047', borrower: 'Vijay Deshmukh', stampDutyAmt: 500, paidOn: 'pending', status: 'pending', notarised: 'pending', custodian: 'not_assigned', challanNo: 'pending' },
  ];

  // Filtered audit events
  const filteredAudit = auditEvents.filter(ev => {
    const matchSearch = !auditSearch ||
      ev.actorName.toLowerCase().includes(auditSearch.toLowerCase()) ||
      ev.entityId.toLowerCase().includes(auditSearch.toLowerCase()) ||
      ev.eventType.toLowerCase().includes(auditSearch.toLowerCase());
    const matchRole = auditRoleFilter === 'all' || ev.actorRole === auditRoleFilter;
    const matchEntity = auditEntityFilter === 'all' || ev.entityType === auditEntityFilter;
    const matchFrom = !auditDateFrom || ev.timestamp >= auditDateFrom;
    const matchTo = !auditDateTo || ev.timestamp <= auditDateTo + 'T23:59:59Z';
    return matchSearch && matchRole && matchEntity && matchFrom && matchTo;
  });

  const supplementalRegisters = [
    {
      title: 'Blank-Dated Cheque Register',
      subtitle: 'Cheque custody, return and invocation records',
      headers: ['Cheque ID', 'Application', 'Borrower', 'Bank', 'Custody', 'Status', 'Return / Invocation'],
      rows: [
        ['CHQ-2024-042', 'LO00000042', 'Ganesh Thorat', 'HDFC Bank', 'Company Secretary', 'held', 'Pending closure'],
        ['CHQ-2025-035', 'LO00000035', 'Kisan FPC Ltd', 'Bank of Maharashtra', 'Company Secretary', 'invocation_pending', 'Recovery approved'],
      ],
    },
    {
      title: 'SH-4 Register',
      subtitle: 'Physical share transfer forms held for security',
      headers: ['SH-4 ID', 'Application', 'Borrower', 'Shares', 'Execution Date', 'Custodian', 'Status'],
      rows: [
        ['SH4-2024-042', 'LO00000042', 'Ganesh Thorat', '5', '2024-09-15', 'Company Secretary', 'held'],
        ['SH4-2023-021', 'LO00000021', 'Ganesh Thorat', '3', '2022-09-14', 'Company Secretary', 'returned'],
      ],
    },
    {
      title: 'CDSL Pledge Register',
      subtitle: 'Demat pledge creation, invocation and unpledge tracking',
      headers: ['Pledge ID', 'Application', 'Borrower', 'PSN', 'BO ID', 'Status', 'Unpledge Date'],
      rows: [
        ['CDSL-2026-00234', 'LO00000035', 'Kisan FPC Ltd', 'PSN-00234', '12081600XXXX2234', 'pledged', '—'],
        ['CDSL-2025-00112', 'LO00000028', 'Vijay Patil', 'PSN-00112', '12081600XXXX1188', 'unpledged', '2025-05-14'],
      ],
    },
    {
      title: 'SAP Customer Code Register',
      subtitle: 'SAP customer profile request and confirmation records',
      headers: ['Request ID', 'Application', 'Borrower', 'Requested On', 'SAP Code', 'Status', 'Confirmed By'],
      rows: [
        ['SAPR-2024-042', 'LO00000042', 'Ganesh Thorat', '2024-09-20', 'SAP-240042', 'created', 'Senior Manager Finance'],
        ['SAPR-2026-047', 'LO00000047', 'Vijay Deshmukh', '2026-06-18', '—', 'pending', '—'],
      ],
    },
    {
      title: 'Disbursement Register',
      subtitle: 'Payment initiation, bank authorisation and UTR evidence',
      headers: ['Advice ID', 'Loan', 'Borrower', 'Amount', 'Initiated', 'UTR', 'Status'],
      rows: [
        ['DA-2024-042', 'LO00000042', 'Ganesh Thorat', fmt(500000), '2024-09-22', 'UTR2409220042', 'completed'],
        ['DA-2026-047', 'LO00000047', 'Vijay Deshmukh', fmt(450000), '—', '—', 'readiness_pending'],
      ],
    },
    {
      title: 'Repayment Register',
      subtitle: 'Repayment receipts, channels and allocation status',
      headers: ['Receipt ID', 'Loan', 'Borrower', 'Amount', 'Channel', 'UTR', 'Allocation'],
      rows: [
        ['RCP-2025-042-03', 'LO00000042', 'Ganesh Thorat', fmt(105000), 'Direct NEFT', 'UTR2506290042', 'principal_first'],
        ['RCP-2025-044-02', 'LO00000044', 'Sunita Kamble', fmt(52000), 'Subsidiary Deduction', 'SUB-APR-044', 'principal_first'],
      ],
    },
    {
      title: 'Interest Invoice Register',
      subtitle: 'Annual borrower interest invoices and payment status',
      headers: ['Invoice', 'Loan', 'Borrower', 'Period', 'Amount', 'Due By', 'Status'],
      rows: [
        ['INV-2025-001', 'LO00000042', 'Ganesh Thorat', 'FY 2024-25', fmt(36000), '2025-04-30', 'sent'],
        ['INV-2025-003', 'LO00000038', 'Malti Shinde', 'FY 2024-25', fmt(25200), '2025-04-30', 'overdue'],
      ],
    },
    {
      title: 'Accrual Register',
      subtitle: 'Monthly and quarterly interest accrual postings',
      headers: ['Accrual ID', 'Loan', 'Borrower', 'Period', 'Principal', 'Accrued', 'SAP Status'],
      rows: [
        ['ACR-2025-Q2-042', 'LO00000042', 'Ganesh Thorat', 'Q2 FY 2025-26', fmt(350000), fmt(10543), 'pending'],
        ['ACR-2025-Q2-038', 'LO00000038', 'Malti Shinde', 'Q2 FY 2025-26', fmt(180000), fmt(6273), 'pending'],
      ],
    },
    {
      title: 'DPD / Monitoring Register',
      subtitle: 'Delinquency bucket and reminder tracking',
      headers: ['Loan', 'Borrower', 'DPD', 'Bucket', 'Last Reminder', 'Next Action', 'Owner'],
      rows: [
        ['LO00000042', 'Ganesh Thorat', '45', '31-60', '2025-06-10', 'Grace review', 'Credit Manager'],
        ['LO00000038', 'Malti Shinde', '95', '91-365', '2025-06-15', 'Non-payment note', 'Credit Manager'],
      ],
    },
    {
      title: 'NOC / Closure Register',
      subtitle: 'Closure readiness, NOC issue and security return tracking',
      headers: ['NOC ID', 'Loan', 'Borrower', 'Balance', 'NOC Status', 'Security Return', 'Archive'],
      rows: [
        ['NOC-2025-042', 'LO00000031', 'Asha Bhosale', fmt(0), 'ready', 'pending', 'pending'],
        ['NOC-2025-025', 'LO00000025', 'Radha Kisan Org', fmt(0), 'issued', 'complete', 'archived'],
      ],
    },
    {
      title: 'Archive Register',
      subtitle: 'Closed loan file archive and retention records',
      headers: ['Archive ID', 'Loan', 'Borrower', 'Closed On', 'Location', 'Retention Until', 'Status'],
      rows: [
        ['ARC-2025-025', 'LO00000025', 'Radha Kisan Org', '2025-03-28', 'Cabinet 3, Row 2', '2033-03-28', 'archived'],
        ['ARC-2023-021', 'LO00000021', 'Ganesh Thorat', '2023-03-20', 'Cabinet 1, Row 4', '2031-03-20', 'archived'],
      ],
    },
    {
      title: 'SOP Change Register',
      subtitle: 'Policy/SOP revisions and Board approval tracking',
      headers: ['Change ID', 'Area', 'Requested By', 'Requested On', 'Approval', 'Effective Date', 'Status'],
      rows: [
        ['SOP-CHG-001', 'Loan threshold matrix', 'CFO', '2026-05-12', 'Board pending', '—', 'under_review'],
        ['SOP-CHG-002', 'KYC refresh cycle', 'Company Secretary', '2026-04-08', 'Approved', '2026-06-01', 'active'],
      ],
    },
  ];

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900 flex items-center gap-2">
            <BookOpen size={20} className="text-green-600" />
            Registers
          </h1>
          <p className="text-sm text-slate-500 mt-0.5">Statutory and internal registers · 8-year retention</p>
        </div>
        <button disabled={!canExport} className="btn-secondary flex items-center gap-2 text-sm disabled:opacity-50 disabled:cursor-not-allowed">
          <Archive size={14} />
          Export Register
        </button>
      </div>

      <Tabs tabs={REGISTER_TABS} activeIndex={activeTab} onChange={setActiveTab}>
        {/* Tab 0: Loan Register */}
        <div className="card p-0 overflow-hidden">
          <div className="p-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
            <div>
              <p className="text-sm font-semibold text-slate-900 flex items-center gap-2">
                <FileText size={14} className="text-green-600" /> Loan account register
              </p>
              <p className="text-xs text-slate-500 mt-0.5">Showing {loanAccounts.length} of 23 loan accounts</p>
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200">
                  <th className="table-header text-left">Account No.</th>
                  <th className="table-header text-left">Member</th>
                  <th className="table-header text-right">Disbursed</th>
                  <th className="table-header text-right">Outstanding</th>
                  <th className="table-header text-right">Current rate</th>
                  <th className="table-header text-left">Status</th>
                  <th className="table-header text-left">SAP code</th>
                  <th className="table-header text-right">DPD</th>
                  <th className="table-header text-left">Repayment due date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {processedLoans.map(l => (
                  <tr key={l.id} className="hover:bg-slate-50">
                    <td className="table-cell num font-semibold text-green-700">
                      {onOpenLoan ? (
                        <button onClick={() => onOpenLoan(l.id)} className="hover:underline text-left">{l.accountNumber}</button>
                      ) : l.accountNumber}
                    </td>
                    <td className="table-cell font-medium">{l.memberName}</td>
                    <td className="table-cell text-right num">{fmt(l.disbursedAmount)}</td>
                    <td className="table-cell text-right num font-semibold">{fmt(l.outstanding)}</td>
                    <td className="table-cell text-right">{l.interestRate}%</td>
                    <td className="table-cell"><StatusBadge label={l.displayStatus} size="sm" /></td>
                    <td className="table-cell num text-slate-600">{l.sapCustomerCode}</td>
                    <td className="table-cell text-right">
                      {l.calcDpd !== null ? (
                        <span className={`font-bold num ${l.calcDpd > 90 ? 'text-red-600' : l.calcDpd > 0 ? 'text-amber-600' : 'text-green-600'}`}>{l.calcDpd}</span>
                      ) : (
                        <span className="text-slate-400">—</span>
                      )}
                    </td>
                    <td className="table-cell">{new Date(l.repaymentDueDate).toLocaleDateString('en-IN')}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Tab 1: Loan Request Register */}
        <div className="card p-0 overflow-hidden">
          <div className="p-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
            <div>
              <p className="text-sm font-semibold text-slate-900 flex items-center gap-2">
                <FileText size={14} className="text-green-600" /> Loan request register
              </p>
              <p className="text-xs text-slate-500 mt-0.5">All loan requests and application references — {loanApplications.length} records</p>
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200">
                  <th className="table-header text-left">Application No.</th>
                  <th className="table-header text-left">Member</th>
                  <th className="table-header text-left">Type</th>
                  <th className="table-header text-right">Requested amount</th>
                  <th className="table-header text-right">Eligible limit</th>
                  <th className="table-header text-left">Purpose</th>
                  <th className="table-header text-left">Status</th>
                  <th className="table-header text-left">Owner</th>
                  <th className="table-header text-left">Exception</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {loanApplications.map(app => {
                  const typeMap: Record<string, string> = { individual: 'Individual', fpc: 'FPC', producer_institution: 'Producer Institution' };
                  const purposeMap: Record<string, string> = { crop_production: 'Crop production', agriculture_activity: 'Agriculture activity', allied_activity: 'Allied activity' };
                  
                  let displayType = typeMap[app.memberType] || app.memberType;
                  let displayPurpose = purposeMap[app.purpose] || app.purpose;
                  
                  let displayStatus = getApplicationStatusLabel(app);
                  if (['sanctioned', 'documentation_in_progress', 'documentation_deficiency_raised'].includes(app.status) && app.currentOwnerRole === 'compliance_team') {
                    displayStatus = 'documentation_pending';
                  }
                  
                  let displayOwner = app.currentOwner;
                  if ((app.status === 'pending_credit_manager_review' || app.status === 'credit_review') && app.currentOwner === 'Deputy Manager – Finance') {
                    displayOwner = 'Credit Manager';
                  }

                  let displayEligible: string = fmt(app.eligibleAmount);
                  let exceptionDisplay = 'None';
                  let isExceptionActive = false;
                  
                  if (app.status === 'incomplete' || app.status === 'returned_for_rectification' || app.status === 'deficiency_raised') {
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
                    <tr key={app.id} className={`hover:bg-slate-50 ${isExceptionActive ? 'bg-violet-50/30' : ''}`}>
                      <td className="table-cell num font-semibold text-green-700">
                        {onOpenApplication ? (
                          <button onClick={() => onOpenApplication(app.id)} className="hover:underline text-left">{getApplicationReference(app)}</button>
                        ) : getApplicationReference(app)}
                      </td>
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
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Tab 2: Credit Sanction Register */}
        <div className="card p-0 overflow-hidden">
          <div className="p-4 bg-slate-50 border-b border-slate-200">
            <p className="text-sm font-semibold text-slate-900 flex items-center gap-2">
              <Gavel size={14} className="text-green-600" /> Credit sanction register
            </p>
            <p className="text-xs text-slate-500 mt-0.5">All sanction decisions — {sanctionDecisions.length} records</p>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200">
                  <th className="table-header text-left">Application No.</th>
                  <th className="table-header text-left">Member</th>
                  <th className="table-header text-right">Sanctioned Amount</th>
                  <th className="table-header text-left">Decision</th>
                  <th className="table-header text-left">Decision date</th>
                  <th className="table-header text-left">Approval authority</th>
                  <th className="table-header text-left">Exception</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {sanctionDecisions.map(app => {
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
                    <td className="table-cell num font-semibold text-green-700">{getApplicationReference(app)}</td>
                    <td className="table-cell font-medium">{app.memberName}</td>
                    <td className="table-cell text-right num">{fmt(app.requestedAmount)}</td>
                    <td className="table-cell">
                      <span className={`text-xs font-semibold px-2 py-0.5 rounded-full capitalize ${decisionBadgeColor}`}>
                        {app.sanctionDecision}
                      </span>
                    </td>
                    <td className="table-cell text-slate-600">{formattedDate}</td>
                    <td className="table-cell text-slate-600">{authority}</td>
                    <td className="table-cell">
                      {app.isException ? (
                        <span className={`flex items-center gap-1 text-xs font-semibold ${exceptionDisplay === 'Rejected' ? 'text-red-700' : 'text-violet-700'}`}>
                          <AlertOctagon size={12} /> {exceptionDisplay}
                        </span>
                      ) : (
                        <span className="text-xs text-green-600 font-medium">None</span>
                      )}
                    </td>
                  </tr>
                )
     })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Tab 2: Security Register */}
        <div className="card p-0 overflow-hidden">
          <div className="p-4 bg-slate-50 border-b border-slate-200">
            <p className="text-sm font-semibold text-slate-900 flex items-center gap-2">
              <Scale size={14} className="text-green-600" /> Security register
            </p>
            <p className="text-xs text-slate-500 mt-0.5">All security instruments — {securities.length} records</p>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200">
                  <th className="table-header text-left">Instrument</th>
                  <th className="table-header text-left">Application</th>
                  <th className="table-header text-left">Status</th>
                  <th className="table-header text-left">Execution Date</th>
                  <th className="table-header text-left">Custodian</th>
                  <th className="table-header text-left">Stamp Duty</th>
                  <th className="table-header text-left">Notarised</th>
                  <th className="table-header text-left">PSN</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {securities.map(sec => {
                  const typeMap: Record<string, string> = { sh4: 'SH-4', poa: 'PoA', cdsl_pledge: 'CDSL pledge', blank_cheque: 'Blank cheque', loan_agreement: 'Loan agreement' };
                  let displayType = typeMap[sec.securityType] || sec.securityType.replace('_', ' ');

                  const appObj = loanApplications.find(a => a.id === sec.applicationId);
                  let displayApp = appObj ? appObj.applicationNumber : sec.applicationId;

                  let stampDisplay = sec.stampDutyStatus === 'complete' ? 'Complete' : sec.stampDutyStatus === 'pending' ? 'Pending' : '—';
                  let notarisedDisplay = sec.notarisationStatus === 'complete' ? 'Complete' : sec.notarisationStatus === 'pending' ? 'Pending' : '—';
                  
                  let psnDisplay = sec.psnNumber || '—';

                  if (sec.securityType === 'blank_cheque') {
                    stampDisplay = 'Not required';
                    notarisedDisplay = 'Not required';
                    psnDisplay = 'Not required';
                  } else if (sec.securityType === 'cdsl_pledge') {
                    stampDisplay = 'Not required';
                    notarisedDisplay = 'Not required';
                    psnDisplay = sec.status === 'pledged' ? (sec.psnNumber || 'CDSL-PENDING') : sec.status === 'pending' ? 'Pending' : 'Not required';
                  } else if (sec.securityType === 'sh4') {
                    psnDisplay = 'Not required';
                  }

                  let displayStatus: string = sec.status;
                  const statusMap: Record<string, string> = {
                    held: 'Held in custody',
                    executed: 'Executed',
                    pledged: 'Pledged',
                    pending: 'Pending',
                    invoked: 'Invoked',
                    returned: 'Returned',
                    not_required: 'Not required'
                  };
                  
                  if (sec.securityType === 'poa' && sec.status === 'executed' && (sec.stampDutyStatus === 'pending' || sec.notarisationStatus === 'pending')) {
                    displayStatus = 'Execution pending';
                  } else {
                    displayStatus = statusMap[sec.status] || sec.status;
                  }

                  let formattedDate = '—';
                  if (sec.executionDate) {
                    formattedDate = new Intl.DateTimeFormat('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }).format(new Date(sec.executionDate));
                  }
                  
                  const statusColor = displayStatus === 'Held in custody' || displayStatus === 'Executed' || displayStatus === 'Pledged' ? 'bg-green-100 text-green-700' : 
                                      displayStatus === 'Execution pending' || displayStatus === 'Pending' ? 'bg-amber-100 text-amber-700' :
                                      displayStatus === 'Invoked' ? 'bg-red-100 text-red-700' : 'bg-slate-100 text-slate-700';

                  return (
                    <tr key={sec.id} className="hover:bg-slate-50">
                      <td className="table-cell font-semibold">{displayType}</td>
                      <td className="table-cell num font-medium text-slate-800">{displayApp}</td>
                      <td className="table-cell">
                        <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${statusColor}`}>
                          {displayStatus}
                        </span>
                      </td>
                      <td className="table-cell text-slate-600">{formattedDate}</td>
                      <td className="table-cell text-slate-600">{sec.custodian || '—'}</td>
                      <td className="table-cell">
                        <span className={`text-xs font-medium ${stampDisplay === 'Complete' ? 'text-green-600' : stampDisplay === 'Pending' ? 'text-amber-600' : 'text-slate-500'}`}>
                          {stampDisplay}
                        </span>
                      </td>
                      <td className="table-cell">
                        <span className={`text-xs font-medium ${notarisedDisplay === 'Complete' ? 'text-green-600' : notarisedDisplay === 'Pending' ? 'text-amber-600' : 'text-slate-500'}`}>
                          {notarisedDisplay}
                        </span>
                      </td>
                      <td className="table-cell num text-xs text-slate-500">{psnDisplay}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Tab 3: Exception Register */}
        <div className="card p-0 overflow-hidden">
          <div className="p-4 bg-slate-50 border-b border-slate-200">
            <p className="text-sm font-semibold text-slate-900 flex items-center gap-2">
              <AlertOctagon size={14} className="text-violet-600" /> Exception register
            </p>
            <p className="text-xs text-slate-500 mt-0.5">Open and approved exception records — {exceptions.length} records</p>
          </div>
          {exceptions.length === 0 ? (
            <div className="p-8 text-center text-slate-400 text-sm">No exception cases on record.</div>
          ) : (
            <div className="divide-y divide-slate-100">
              {exceptions.map(app => {
                let excType = 'Limit breach';
                let excDesc = ``;
                let authority = 'CFO + 2 Directors required';
                
                if (app.requestedAmount === app.eligibleAmount && app.requestedAmount > 500000) {
                  excType = 'High-value approval';
                  excDesc = `${excType}: ${authority}.`;
                } else {
                  let diff = app.requestedAmount - (app.eligibleAmount ?? 0);
                  if (diff > 0) {
                    excDesc = `Limit breach: requested ${fmt(app.requestedAmount)} vs eligible ${fmt(app.eligibleAmount)}; excess ${fmt(diff)}.`;
                  } else {
                    excDesc = `Limit breach: requested ${fmt(app.requestedAmount)} vs eligible ${fmt(app.eligibleAmount)}.`;
                  }
                }

                let excStatus = app.sanctionDecision === 'approved' ? 'Approved' : 'Open';
                let formattedDate = new Intl.DateTimeFormat('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }).format(new Date(app.applicationDate));

                return (
                  <div key={app.id} className="p-4 bg-violet-50/50 hover:bg-violet-50/80 transition-colors">
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-semibold text-slate-900 num">{getApplicationReference(app)}</span>
                          <StatusBadge label={app.status} size="sm" />
                          <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${excStatus === 'Approved' ? 'bg-green-100 text-green-700' : 'bg-amber-100 text-amber-700'}`}>
                            Exception: {excStatus}
                          </span>
                        </div>
                        <p className="text-sm font-medium text-slate-800 mt-1.5">{app.memberName}</p>
                        <p className="text-sm text-slate-600 mt-0.5">{excDesc}</p>
                        <p className="text-xs text-violet-700 mt-1.5 font-medium flex items-center gap-1.5 bg-violet-100/50 w-max px-2 py-1 rounded">
                          <AlertOctagon size={12} /> {excType} ({authority})
                        </p>
                      </div>
                      <div className="text-xs font-medium text-slate-500 flex-shrink-0">{formattedDate}</div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Tab 4: Member Register */}
        <div className="card p-0 overflow-hidden">
          <div className="p-4 bg-slate-50 border-b border-slate-200">
            <p className="text-sm font-semibold text-slate-900 flex items-center gap-2">
              <BookOpen size={14} className="text-green-600" /> Member register
            </p>
            <p className="text-xs text-slate-500 mt-0.5">All SFPCL members — {members.length} records</p>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200">
                  <th className="table-header text-left">Name</th>
                  <th className="table-header text-left">Folio</th>
                  <th className="table-header text-left">Member type</th>
                  <th className="table-header text-right">Shares</th>
                  <th className="table-header text-left">KYC</th>
                  <th className="table-header text-left">Member status</th>
                  <th className="table-header text-right">Exposure</th>
                  <th className="table-header text-left">Member since</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {members.map(m => {
                  let displayName = m.name;
                  if (displayName === 'Green Valley F P C') displayName = 'Green Valley FPC';

                  const typeMap: Record<string, string> = { individual: 'Individual', fpc: 'FPC', producer_institution: 'Producer Institution' };
                  let displayType = typeMap[m.memberType] || m.memberType;

                  const kycMap: Record<string, string> = {
                    verified: 'Verified',
                    re_kyc_due: 'Re-KYC due',
                    kyc_expired: 'KYC expired',
                    pending: 'Pending'
                  };
                  let displayKyc = kycMap[m.kycStatus] || m.kycStatus;

                  const statusMap: Record<string, string> = {
                    active: 'Active',
                    inactive: 'Inactive',
                    under_review: 'Under review'
                  };
                  let displayStatus = statusMap[m.activeStatus] || m.activeStatus;
                  
                  let formattedDate = new Intl.DateTimeFormat('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }).format(new Date(m.registeredOn));

                  return (
                    <tr key={m.id} className="hover:bg-slate-50">
                      <td className="table-cell font-semibold text-slate-900">{displayName}</td>
                      <td className="table-cell num text-slate-600">{m.folioNumber}</td>
                      <td className="table-cell text-xs font-medium text-slate-700">{displayType}</td>
                      <td className="table-cell text-right num">{m.sharesHeld.toLocaleString('en-IN')}</td>
                      <td className="table-cell">
                        <StatusBadge label={displayKyc} size="sm" />
                      </td>
                      <td className="table-cell">
                        <StatusBadge label={displayStatus} size="sm" />
                      </td>
                      <td className="table-cell text-right num font-medium">{fmt(m.currentExposure)}</td>
                      <td className="table-cell text-slate-600">{formattedDate}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Tab 6: Compliance Register */}
        <div className="card p-0 overflow-hidden">
          <div className="p-4 bg-slate-50 border-b border-slate-200">
            <p className="text-sm font-semibold text-slate-900 flex items-center gap-2">
              <BookOpen size={14} className="text-green-600" /> Compliance register
            </p>
            <p className="text-xs text-slate-500 mt-0.5">Compliance controls and evidence records</p>
          </div>
          <div className="divide-y divide-slate-100">
            {complianceRecords.map(rec => {
              const areaMap: Record<string, string> = {
                'Producer Company lending': 'Producer Company lending — members only',
                'Section 186 limit check': 'Section 186 loan limits',
                'NBFC principal business test': 'NBFC principal business test',
                'KYC & AML verification': 'KYC / AML verification',
                'Re-KYC cycle': 'Re-KYC cycle',
                'Stamp duty & notarisation': 'Stamp duty & notarisation',
                'Money-lending exemption': 'Money-lending law exemption review'
              };
              let displayArea = areaMap[rec.area] || rec.area;

              const ownerMap: Record<string, string> = {
                'Producer Company lending — members only': 'Company Secretary',
                'Section 186 loan limits': 'CFO',
                'NBFC principal business test': 'CFO',
                'KYC / AML verification': 'Compliance Team',
                'Re-KYC cycle': 'Compliance Team',
                'Stamp duty & notarisation': 'Company Secretary',
                'Money-lending law exemption review': 'Company Secretary'
              };
              let displayOwner = ownerMap[displayArea] || rec.owner;
              
              let isOverdue = new Date(rec.nextDueDate) < new Date();
              let displayStatus: string = rec.status;
              
              if (rec.status === 'compliant') displayStatus = 'Compliant';
              else if (rec.status === 'warning') displayStatus = 'Warning';
              else if (rec.status === 'pending') {
                if (isOverdue) displayStatus = 'Overdue';
                else displayStatus = 'Pending';
              } else {
                 displayStatus = rec.status;
              }
              
              let statusColor = displayStatus === 'Compliant' ? 'bg-green-100 text-green-700' :
                                displayStatus === 'Warning' ? 'bg-amber-100 text-amber-700' :
                                displayStatus === 'Overdue' ? 'bg-red-100 text-red-700' :
                                'bg-slate-100 text-slate-700';
                                
              let formattedDate = new Intl.DateTimeFormat('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }).format(new Date(rec.nextDueDate));
              
              let evidenceText = rec.evidenceCount === 1 ? '1 evidence record' : `${rec.evidenceCount} evidence records`;
              
              return (
              <div key={rec.id} className="flex items-center gap-4 p-4 hover:bg-slate-50 transition-colors">
                <div className="flex-1">
                  <p className="text-sm font-medium text-slate-900">{displayArea}</p>
                  <p className="text-xs text-slate-500 mt-1">
                    {displayOwner} · {rec.frequency} · {evidenceText}
                  </p>
                </div>
                <div className="text-right">
                  <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${statusColor}`}>
                    {displayStatus}
                  </span>
                  <p className="text-xs text-slate-500 font-medium mt-1.5">Due: {formattedDate}</p>
                </div>
              </div>
            )})}
          </div>
        </div>

        {/* Tab 7: Stamp Duty Register */}
        <div className="card p-0 overflow-hidden">
          <div className="p-4 bg-slate-50 border-b border-slate-200">
            <p className="text-sm font-semibold text-slate-900 flex items-center gap-2">
              <FileText size={14} className="text-green-600" /> Stamp duty register
            </p>
            <p className="text-xs text-slate-500 mt-0.5">Stamp duty and notarisation records for security documents</p>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200">
                  <th className="table-header text-left">Document Type</th>
                  <th className="table-header text-left">Application No.</th>
                  <th className="table-header text-left">Borrower</th>
                  <th className="table-header text-left">Stamp Duty Amount</th>
                  <th className="table-header text-left">Paid On</th>
                  <th className="table-header text-left">Challan No.</th>
                  <th className="table-header text-left">Notarised</th>
                  <th className="table-header text-left">Custodian</th>
                  <th className="table-header text-left">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {stampDutyRecords.map((row, i) => {
                  
                  let amtDisplay = typeof row.stampDutyAmt === 'number' ? fmt(row.stampDutyAmt) : row.stampDutyAmt;
                  
                  let dateDisplay = '—';
                  if (row.paidOn === 'pending') {
                    dateDisplay = 'Pending';
                  } else if (row.paidOn) {
                    dateDisplay = new Intl.DateTimeFormat('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }).format(new Date(row.paidOn));
                  }
                  
                  let challanDisplay = row.challanNo === 'pending' ? 'Pending' : (row.challanNo || '—');
                  let custodianDisplay = row.custodian === 'not_assigned' ? 'Not assigned' : (row.custodian || '—');
                  
                  let notDisplay = null;
                  if (row.notarised === 'not_required') {
                    notDisplay = <span className="text-xs text-slate-500 font-medium">Not required</span>;
                  } else if (row.notarised === 'pending') {
                    notDisplay = <span className="text-xs text-amber-600 font-medium">Pending notarisation</span>;
                  } else if (row.notarised === true) {
                    notDisplay = <span className="text-xs text-green-700 font-semibold">Yes ✓</span>;
                  } else {
                    notDisplay = <span className="text-xs text-amber-600 font-medium">Pending notarisation</span>;
                  }

                  let statusDisplay = row.status === 'paid' && row.notarised === false ? 'pending_notarisation' : row.status;

                  return (
                    <tr key={i} className={`hover:bg-slate-50 ${row.status === 'pending' ? 'bg-amber-50/30' : ''}`}>
                      <td className="table-cell font-medium text-slate-800">{row.doc}</td>
                      <td className="table-cell num text-slate-600">{row.appNo}</td>
                      <td className="table-cell text-slate-700">{row.borrower}</td>
                      <td className="table-cell num text-slate-900 font-semibold">{amtDisplay}</td>
                      <td className="table-cell text-slate-600">{dateDisplay}</td>
                      <td className="table-cell font-mono text-xs text-slate-500">{challanDisplay}</td>
                      <td className="table-cell">{notDisplay}</td>
                      <td className="table-cell text-slate-600">{custodianDisplay}</td>
                      <td className="table-cell"><StatusBadge label={statusDisplay} size="sm" /></td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Tab 6: Audit Log Explorer (S74) */}
        <div className="space-y-3">
          {/* Filters */}
          <div className="card">
            <div className="flex items-center gap-2 mb-3">
              <Filter size={14} className="text-slate-500" />
              <p className="text-sm font-semibold text-slate-700">Audit log explorer</p>
              <span className="text-xs text-slate-400 ml-auto">{filteredAudit.length} events</span>
            </div>
            <div className="flex flex-wrap gap-3">
              <div className="relative flex-1 min-w-48">
                <Search size={13} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                <input
                  type="text"
                  placeholder="Search actor, entity ID, event type…"
                  value={auditSearch}
                  onChange={e => setAuditSearch(e.target.value)}
                  className="field-input pl-8 text-sm py-2 w-full"
                />
              </div>
              <select value={auditRoleFilter} onChange={e => setAuditRoleFilter(e.target.value)} className="field-select text-sm py-2">
                <option value="all">All roles</option>
                <option value="deputy_manager_finance">Deputy Manager – Finance</option>
                <option value="credit_manager">Credit Manager</option>
                <option value="cfo">CFO</option>
                <option value="company_secretary">Company Secretary</option>
                <option value="director">Director</option>
                <option value="accounts">Accounts</option>
              </select>
              <select value={auditEntityFilter} onChange={e => setAuditEntityFilter(e.target.value)} className="field-select text-sm py-2">
                <option value="all">All entity types</option>
                <option value="application">Application</option>
                <option value="loan_account">Loan Account</option>
                <option value="member">Member</option>
                <option value="security">Security</option>
              </select>
              <input
                type="date"
                value={auditDateFrom}
                onChange={e => setAuditDateFrom(e.target.value)}
                className="field-input text-sm py-2"
                placeholder="From date"
              />
              <input
                type="date"
                value={auditDateTo}
                onChange={e => setAuditDateTo(e.target.value)}
                className="field-input text-sm py-2"
                placeholder="To date"
              />
              <button disabled={!canExport} className="flex items-center gap-1 text-xs text-green-700 hover:underline disabled:opacity-50 disabled:cursor-not-allowed disabled:no-underline">
                <Download size={12} /> Export
              </button>
            </div>
          </div>

          <div className="card p-0 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-slate-50 border-b border-slate-200">
                    {['Timestamp', 'Actor', 'Role', 'Entity Type', 'Entity ID', 'Event', 'Before State', 'After State', 'Comment'].map(h => (
                      <th key={h} className="table-header text-left whitespace-nowrap">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {filteredAudit.length === 0 ? (
                    <tr>
                      <td colSpan={9} className="table-cell text-center text-slate-400 py-8">No events match the current filters.</td>
                    </tr>
                  ) : filteredAudit.map(ev => {
                    const formattedDate = new Intl.DateTimeFormat('en-GB', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit', hour12: true }).format(new Date(ev.timestamp));
                    
                    let displayActor = ev.actorName;
                    if (displayActor === 'Credit Assessment Team') displayActor = 'System';
                    if (displayActor === 'System Admin' && (ev.eventType.includes('Sanction') || ev.eventType.includes('Document'))) {
                        displayActor = 'System';
                    }

                    const roleMap: Record<string, string> = {
                      deputy_manager_finance: 'Deputy Manager – Finance',
                      credit_manager: 'Credit Manager',
                      cfo: 'CFO',
                      company_secretary: 'Company Secretary',
                      director: 'Director',
                      system: 'System'
                    };
                    let displayRole = roleMap[ev.actorRole] || ev.actorRole.replace(/_/g, ' ');

                    let displayEntityId = ev.entityId;
                    const matchedApp = loanApplications.find(a => a.id === ev.entityId);
                    if (matchedApp) displayEntityId = getApplicationReference(matchedApp);
                    const matchedLoan = loanAccounts.find(l => l.id === ev.entityId);
                    if (matchedLoan) displayEntityId = matchedLoan.accountNumber;

                    const eventMap: Record<string, string> = {
                      'Application Submitted': 'Application submitted',
                      'Reference Number Generated': 'Reference number generated',
                      'Appraisal Note Prepared': 'Appraisal note prepared',
                      'Submitted to Sanction Committee': 'Submitted to Sanction Committee',
                      'Sanction Approved': 'Sanction approved',
                      'Document Pack Generated': 'Document pack generated',
                      'Default Recovery Action Initiated': 'Default recovery action initiated',
                      'Repayment Posted': 'Repayment posted'
                    };
                    let displayEvent = eventMap[ev.eventType] || ev.eventType;
                    if (displayEvent.toLowerCase() === displayEvent) {
                       displayEvent = displayEvent.charAt(0).toUpperCase() + displayEvent.slice(1);
                    }

                    const stateMap: Record<string, string> = {
                      submitted: 'Submitted',
                      reference_generated: 'Application complete / appraisal in progress',
                      appraisal_in_progress: 'Application complete / appraisal in progress',
                      appraisal_pending: 'Appraisal pending',
                      returned_for_rectification: 'Returned for rectification',
                      credit_review: 'Pending credit manager review',
                      pending_credit_manager_review: 'Pending credit manager review',
                      pending_sanction: 'Pending sanction committee approval',
                      pending_sanction_committee_approval: 'Pending sanction committee approval',
                      under_sanction_review: 'Under sanction review',
                      clarification_requested: 'Clarification requested',
                      sanctioned: 'Sanctioned',
                      documentation_in_progress: 'Documentation in progress',
                      pending_final_checklist_approvals: 'Pending final checklist approvals',
                      sap_customer_code_pending: 'SAP customer code pending',
                      sap_customer_code_confirmed: 'SAP customer code confirmed',
                      payment_initiated: 'Payment initiated',
                      payment_authorized: 'Payment authorized',
                      transfer_executed: 'Transfer executed',
                      active: 'Active repayment',
                      active_repayment: 'Active repayment',
                      default_review: 'Recovery review',
                      recovery_review: 'Recovery review',
                      recovery_in_progress: 'Recovery in progress',
                      recovery_action_approved: 'Recovery action approved',
                      closure_review: 'Closure review'
                    };
                    let displayPrev = ev.previousState ? (stateMap[ev.previousState] || ev.previousState) : null;
                    let displayNew = ev.newState ? (stateMap[ev.newState] || ev.newState) : null;

                    return (
                      <tr key={ev.id} className="hover:bg-slate-50">
                        <td className="table-cell text-xs text-slate-500 whitespace-nowrap">{formattedDate}</td>
                        <td className="table-cell font-medium text-slate-900">{displayActor}</td>
                        <td className="table-cell text-xs text-slate-500 capitalize">{displayRole}</td>
                        <td className="table-cell text-xs text-slate-500 capitalize">{ev.entityType.replace(/_/g, ' ')}</td>
                        <td className="table-cell font-mono text-xs text-slate-600">{displayEntityId}</td>
                        <td className="table-cell font-medium text-slate-800">{displayEvent}</td>
                        <td className="table-cell">
                          {displayPrev
                            ? <span className="text-xs bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded">{displayPrev}</span>
                            : <span className="text-slate-300">—</span>}
                        </td>
                        <td className="table-cell">
                          {displayNew
                            ? <span className="text-xs bg-green-100 text-green-700 px-1.5 py-0.5 rounded">{displayNew}</span>
                            : <span className="text-slate-300">—</span>}
                        </td>
                        <td className="table-cell text-xs text-slate-500 max-w-xs truncate" title={ev.comment}>{ev.comment || '—'}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Tab 7: Grievance Register */}
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
                  <tr key={g.ref} className={`hover:bg-slate-50 ${statusText === 'Overdue' ? 'bg-red-50/20' : ''}`}>
                    <td className="table-cell font-mono text-slate-600">{g.ref}</td>
                    <td className="table-cell font-medium text-slate-900">{g.borrower}</td>
                    <td className="table-cell text-slate-700">{g.subject}</td>
                    <td className="table-cell text-slate-600">{raisedFmt}</td>
                    <td className="table-cell text-slate-500 font-medium">{slaFmt}</td>
                    <td className="table-cell">
                      <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${statusColor}`}>
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
        </div>

        {/* Tab 7: Recovery Log */}
        <div className="card p-0 overflow-hidden">
          <div className="p-4 bg-slate-50 border-b border-slate-200">
            <p className="text-sm font-semibold text-slate-900 flex items-center gap-2">
              <Scale size={14} className="text-red-600" /> Recovery Log
            </p>
            <p className="text-xs text-slate-500 mt-0.5">All default management and recovery action records</p>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200">
                  <th className="table-header text-left">Loan No.</th>
                  <th className="table-header text-left">Borrower</th>
                  <th className="table-header text-right">Outstanding</th>
                  <th className="table-header text-right">DPD</th>
                  <th className="table-header text-left">Stage</th>
                  <th className="table-header text-left">Action Taken</th>
                  <th className="table-header text-left">Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {[
                  { loan: 'LO00000042', borrower: 'Ganesh Thorat',   outstanding: 350000, dpd: 45,  stage: 'grace_period',    action: 'Reminder calls + SMS issued',      date: '2025-06-10' },
                  { loan: 'LO00000038', borrower: 'Malti Shinde',    outstanding: 180000, dpd: 95,  stage: 'recovery_review',  action: 'Non-payment note submitted to SC', date: '2025-06-15' },
                  { loan: 'LO00000035', borrower: 'Kisan FPC Ltd',   outstanding: 890000, dpd: 187, stage: 'recovery_action_approved', action: 'CFO approved security invocation', date: '2025-04-28' },
                ].map(r => (
                  <tr key={r.loan} className={`hover:bg-slate-50 ${r.dpd > 90 ? 'bg-red-50/20' : ''}`}>
                    <td className="table-cell font-mono text-slate-700">{r.loan}</td>
                    <td className="table-cell font-medium text-slate-900">{r.borrower}</td>
                    <td className="table-cell text-right num">{fmt(r.outstanding)}</td>
                    <td className="table-cell text-right font-semibold text-red-600">{r.dpd}</td>
                    <td className="table-cell"><StatusBadge label={r.stage} size="sm" /></td>
                    <td className="table-cell text-slate-600">{r.action}</td>
                    <td className="table-cell text-slate-500">{r.date}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {supplementalRegisters.map(register => (
          <div key={register.title} className="card p-0 overflow-hidden">
            <div className="p-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
              <div>
                <p className="text-sm font-semibold text-slate-900 flex items-center gap-2">
                  <BookOpen size={14} className="text-green-600" /> {register.title}
                </p>
                <p className="text-xs text-slate-500 mt-0.5">{register.subtitle}</p>
              </div>
              <button disabled={!canExport} className="flex items-center gap-1 text-xs text-green-700 hover:underline disabled:opacity-50 disabled:cursor-not-allowed disabled:no-underline">
                <Download size={12} /> Export
              </button>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-slate-50 border-b border-slate-200">
                    {register.headers.map(header => (
                      <th key={header} className="table-header text-left whitespace-nowrap">{header}</th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {register.rows.map((row, rowIndex) => (
                    <tr key={`${register.title}-${rowIndex}`} className="hover:bg-slate-50">
                      {row.map((cell, cellIndex) => (
                        <td
                          key={`${register.title}-${rowIndex}-${cellIndex}`}
                          className={`table-cell ${cellIndex === 0 ? 'font-mono text-slate-700' : 'text-slate-600'}`}
                        >
                          {cellIndex === row.length - 1 ? <StatusBadge label={cell} size="sm" /> : cell}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ))}
      </Tabs>
    </div>
  );
};

export default RegistersHub;
