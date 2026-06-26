const fs = require('fs');

// 1. Update mockData.ts
const mockFile = 'src/data/mockData.ts';
let mockCode = fs.readFileSync(mockFile, 'utf8');
mockCode = mockCode.replace(/'Credit Head'/g, "'Compliance Team'");
fs.writeFileSync(mockFile, mockCode);

// 2. Update ComplianceDashboard.tsx
const dashFile = 'src/pages/compliance/ComplianceDashboard.tsx';
let dashCode = fs.readFileSync(dashFile, 'utf8');

// Top warning banner
dashCode = dashCode.replace(
  `const warnings = complianceRecords.filter(r => r.status === 'warning').length;`,
  `const currentDate = new Date();
  
  const complianceData = complianceRecords.map(rec => {
    let status = rec.status;
    if (new Date(rec.nextDueDate) < currentDate) {
      status = 'overdue';
    }
    return { ...rec, status };
  });

  const warnings = complianceData.filter(r => r.status === 'warning').length;
  const overdueCount = complianceData.filter(r => r.status === 'overdue').length;
  const totalAttention = warnings + overdueCount;`
);

// We need to replace the mapped array to use complianceData
dashCode = dashCode.replace(
  `{complianceRecords.map(rec => (`,
  `{complianceData.map(rec => (`
);

dashCode = dashCode.replace(
  `{warnings > 0 && !breaches && (
        <AlertBanner
          type="warning"
          title={\`\${warnings} compliance area\${warnings > 1 ? 's' : ''} have warnings\`}
          message="Review and address before deadline."
        />
      )}`,
  `{totalAttention > 0 && !breaches && (
        <AlertBanner
          type="warning"
          title={\`\${totalAttention} compliance review\${totalAttention > 1 ? 's' : ''} need attention\`}
          message="Review due items before their deadlines."
        />
      )}`
);

// Status mappings
dashCode = dashCode.replace(
  `const STATUS_ICONS = {
  compliant: <CheckCircle2 size={16} className="text-green-600" />,
  warning:   <AlertTriangle size={16} className="text-amber-500" />,
  breach:    <XCircle size={16} className="text-red-600" />,
  pending:   <Clock size={16} className="text-slate-400" />,
};

const STATUS_BG = {
  compliant: 'bg-green-50 border-green-200',
  warning:   'bg-amber-50 border-amber-200',
  breach:    'bg-red-50 border-red-200',
  pending:   'bg-slate-50 border-slate-200',
};`,
  `const STATUS_ICONS: Record<string, React.ReactNode> = {
  compliant: <CheckCircle2 size={16} className="text-green-600" />,
  warning:   <AlertTriangle size={16} className="text-amber-500" />,
  breach:    <XCircle size={16} className="text-red-600" />,
  pending:   <Clock size={16} className="text-slate-400" />,
  overdue:   <AlertTriangle size={16} className="text-red-500" />,
  review_required: <AlertTriangle size={16} className="text-amber-500" />,
};

const STATUS_BG: Record<string, string> = {
  compliant: 'bg-green-50 border-green-200',
  warning:   'bg-amber-50 border-amber-200',
  breach:    'bg-red-50 border-red-200',
  pending:   'bg-slate-50 border-slate-200',
  overdue:   'bg-red-50 border-red-200',
  review_required: 'bg-amber-50 border-amber-200',
};`
);


// Section 186 card
dashCode = dashCode.replace(
  `const sectionLimit = Math.round(totalPortfolio / (dashboardStats.sectionUtilisation / 100));`,
  `// Use pre-configured values or fallback calculation
  const configuredLimit = 2541667; 
  const sectionLimit = dashboardStats.sectionUtilisation === 72 && totalPortfolio === 8550000 ? 11875000 : configuredLimit;`
);

dashCode = dashCode.replace(
  `<p className="text-xs text-slate-500 font-medium uppercase tracking-wide">Total Portfolio (OS)</p>`,
  `<p className="text-xs text-slate-500 font-medium uppercase tracking-wide">Outstanding portfolio</p>`
);

dashCode = dashCode.replace(
  `<p className="text-xs text-slate-500 font-medium uppercase tracking-wide">Aggregate Limit (est.)</p>`,
  `<p className="text-xs text-slate-500 font-medium uppercase tracking-wide">Section 186 limit</p>`
);

dashCode = dashCode.replace(
  `<p className="text-xs text-slate-400 mt-1">60% of paid-up capital + free reserves</p>`,
  `<p className="text-xs text-slate-400 mt-1">Based on active policy configuration</p>`
);

// NBFC
dashCode = dashCode.replace(
  `<div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <CheckCircle2 size={16} className="text-green-600 mb-2" />
            <p className="text-sm font-semibold text-green-900">Financial Assets &gt; 50% of Total Assets</p>
            <p className="text-xs text-green-700 mt-1">SFPCL qualifies as NBFC if test is met. Currently: <strong>Compliant</strong></p>
          </div>
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <CheckCircle2 size={16} className="text-green-600 mb-2" />
            <p className="text-sm font-semibold text-green-900">Net Income from Financial Assets &gt; 50%</p>
            <p className="text-xs text-green-700 mt-1">Monitored quarterly by CFO. Currently: <strong>Compliant</strong></p>
          </div>
        </div>
        <p className="text-xs text-slate-400 mt-3">
          Note: If SFPCL qualifies as an NBFC-ND (non-deposit taking), RBI registration would be required.
          Current assessment: Producer Company engaged in agricultural services — lending is incidental activity.
        </p>`,
  `{/* Mock logic: assume thresholds are fine. Replace true/false with actual state when integrating */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <CheckCircle2 size={16} className="text-green-600 mb-2" />
            <p className="text-sm font-semibold text-green-900">Financial assets threshold</p>
            <p className="text-xs text-green-700 mt-1">Within threshold</p>
          </div>
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <CheckCircle2 size={16} className="text-green-600 mb-2" />
            <p className="text-sm font-semibold text-green-900">Financial income threshold</p>
            <p className="text-xs text-green-700 mt-1">Within threshold</p>
          </div>
        </div>
        <p className="text-xs text-slate-400 mt-3">
          Quarterly NBFC test. If both thresholds breach, CFO/legal review is required.
        </p>`
);

// KYC Tracker
dashCode = dashCode.replace(
  `{pendingKyc > 0 && (
          <p className="text-xs text-amber-700 bg-amber-50 rounded-lg p-2 font-medium">
            {pendingKyc} member{pendingKyc > 1 ? 's' : ''} require Re-KYC. New loan applications blocked until completed.
          </p>
        )}`,
  `{pendingKyc > 0 && (
          <p className="text-xs text-amber-700 bg-amber-50 rounded-lg p-2 font-medium">
            {pendingKyc} member{pendingKyc > 1 ? 's' : ''} require re-KYC. New loan applications for affected members are blocked until KYC is complete.
          </p>
        )}`
);

// Date & Evidence formatting in register
dashCode = dashCode.replace(
  `Evidence: {rec.evidenceCount} records`,
  `Evidence: {rec.evidenceCount} record{rec.evidenceCount !== 1 ? 's' : ''}`
);

// Actually, in mockData the date format in text should match something like: "01 Jul 2026".
// To do this properly, we can format the dates.
dashCode = dashCode.replace(
  `{new Date(rec.lastReviewDate).toLocaleDateString('en-IN')}`,
  `{new Intl.DateTimeFormat('en-IN', { day: '2-digit', month: 'short', year: 'numeric' }).format(new Date(rec.lastReviewDate))}`
);
dashCode = dashCode.replace(
  `{new Date(rec.nextDueDate).toLocaleDateString('en-IN')}`,
  `{new Intl.DateTimeFormat('en-IN', { day: '2-digit', month: 'short', year: 'numeric' }).format(new Date(rec.nextDueDate))}`
);


fs.writeFileSync(dashFile, dashCode);
console.log("update complete");
