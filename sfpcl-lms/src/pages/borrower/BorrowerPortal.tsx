import React, { useState } from 'react';
import {
  FileText, CheckCircle2, Clock, AlertTriangle, Download,
  Phone, MessageSquare, IndianRupee, Calendar, ChevronRight,
  Leaf, Upload, HelpCircle, Bell, LogOut, BarChart2,
  CreditCard, FileCheck, Shield, ClipboardList, UserRound,
  Landmark, History, Signature, AlertCircle, ChevronLeft, Save
} from 'lucide-react';
import StatusBadge from '../../components/ui/StatusBadge';
import Sidebar from '../../components/layout/Sidebar';
import { useRole } from '../../contexts/RoleContext';

type BorrowerTab = 'overview' | 'newApplication' | 'application' | 'applicationData' | 'repayments' | 'documents' | 'supply' | 'grievance' | 'loanHistory';
type ApplicationStep = 'applicant' | 'shareholding' | 'loan' | 'nominee' | 'documents' | 'declarations' | 'review';

// Mock: check if this borrower is an FPC
const isFPCMember = false; // Set true to demo FPC view

const repaymentSchedule = [
  { due: '2024-12-31', principal: 100000, interest: 6000, total: 106000, status: 'paid', paid: '2024-12-28', utr: 'SFPCL2024120010' },
  { due: '2025-03-31', principal: 100000, interest: 5500, total: 105500, status: 'paid', paid: '2025-03-29', utr: 'SFPCL2025030022' },
  { due: '2025-06-30', principal: 100000, interest: 5000, total: 105000, status: 'overdue', paid: null, utr: null },
  { due: '2025-09-30', principal: 100000, interest: 4500, total: 104500, status: 'upcoming', paid: null, utr: null },
  { due: '2025-12-31', principal: 100000, interest: 4000, total: 104000, status: 'upcoming', paid: null, utr: null },
  { due: '2026-03-31', principal: 0,      interest: 3500, total: 3500,   status: 'upcoming', paid: null, utr: null },
];

const myDocuments = [
  { name: 'PAN Card Copy',              status: 'verified',   date: '2024-08-10', section: 'KYC', note: 'Self-attested borrower copy' },
  { name: 'Aadhaar Card Copy',          status: 'verified',   date: '2024-08-10', section: 'KYC', note: 'Masked display; full value restricted' },
  { name: 'Nominee PAN and Aadhaar',    status: 'verified',   date: '2024-08-12', section: 'Nominee', note: 'Includes signed nominee declaration' },
  { name: 'Share Certificate Copy',     status: 'verified',   date: '2024-08-12', section: 'Shareholding', note: 'Folio M-00042; 5 shares' },
  { name: '7/12 Extract',               status: 'verified',   date: '2024-08-14', section: 'Land', note: '4.5 acres under cultivation' },
  { name: 'Crop Plan',                  status: 'verified',   date: '2024-08-14', section: 'Crop', note: 'Grapes and tomato cultivation plan' },
  { name: 'Six-Month Bank Statement',   status: 'deficient',  date: '2024-08-15', section: 'Bank', note: 'February to April pages requested again' },
  { name: 'Term Sheet',                 status: 'available',  date: '2024-09-15', section: 'Sanction', note: 'Signed by CFO for amount up to ₹5,00,000' },
  { name: 'Loan Agreement',             status: 'available',  date: '2024-09-18', section: 'Legal', note: 'Stamped and notarised' },
  { name: 'Disbursement Advice',        status: 'available',  date: '2024-09-22', section: 'Disbursement', note: 'UTR retained in loan file' },
  { name: 'Repayment Schedule',         status: 'available',  date: '2024-09-22', section: 'Repayment', note: 'Principal-first allocation' },
  { name: 'FY 2025 Interest Invoice',   status: 'available',  date: '2025-04-30', section: 'Interest', note: 'Yearly interest invoice' },
  { name: 'NOC',                        status: 'pending',    date: null,         section: 'Closure', note: 'Available after full repayment and security return' },
];

const applicationFieldSections = [
  {
    title: 'Borrower Details',
    icon: UserRound,
    rows: [
      ['Application Channel', 'Digital Portal'],
      ['Member ID', 'MEM-00042'],
      ['Full Legal Name', 'Ganesh Thorat'],
      ['Father Name', 'Vishnu Thorat'],
      ['Date of Birth', '12 May 1981'],
      ['PAN', 'ABCDE1234F'],
      ['Aadhaar', 'XXXX XXXX 7788'],
      ['Registered Address', 'At Post Mohadi, Tal. Dindori, Nashik, Maharashtra'],
      ['Mobile Number', '+91 98765 43210'],
      ['Email ID', 'ganesh.thorat@sfpcl.in'],
    ],
  },
  {
    title: 'Membership & Eligibility',
    icon: Shield,
    rows: [
      ['Member Type', 'Individual Farmer'],
      ['Folio Number', 'M-00042'],
      ['Shares Held', '5 shares'],
      ['Shareholding Mode', 'Physical'],
      ['Demat BO ID', 'Not applicable'],
      ['Produce Supply History', '5 consecutive years'],
      ['Services Availed', 'Yes'],
      ['Land Area Under Cultivation', '4.5 acres'],
      ['Default Flag', 'No default on record'],
      ['Re-KYC Due Date', '30 September 2026'],
    ],
  },
  {
    title: 'Loan Request',
    icon: ClipboardList,
    rows: [
      ['Required Loan Amount', '₹5,00,000'],
      ['Maximum Permissible Limit', '₹5,00,000'],
      ['Shareholding Limit', '₹5,00,000'],
      ['Land-Based Limit', '₹6,75,000'],
      ['Final Eligible Amount', '₹5,00,000'],
      ['Loan Purpose', 'Crop production / agriculture activity'],
      ['Crop Details', 'Grapes, tomato and seasonal vegetable crop plan'],
      ['Loan Type', 'Short-term'],
      ['Requested Tenure', '12 months'],
      ['Repayment Date', '31 March 2026'],
    ],
  },
  {
    title: 'Nominee & Signatures',
    icon: Signature,
    rows: [
      ['Nominee Name', 'Suman Thorat'],
      ['Nominee Age', '42'],
      ['Nominee Gender', 'Female'],
      ['Relationship', 'Spouse'],
      ['Nominee PAN', 'FGHIJ5678K'],
      ['Nominee Aadhaar', 'XXXX XXXX 4421'],
      ['Borrower Signature', 'Signed on 10 August 2024'],
      ['Nominee Signature', 'Signed on 10 August 2024'],
      ['Witness Validation', 'SFPCL shareholder verified'],
      ['Completeness Status', 'One document deficiency open'],
    ],
  },
];

const validationMessages = [
  { label: 'Member and folio details captured', status: 'passed' },
  { label: 'Loan purpose is agriculture / crop production related', status: 'passed' },
  { label: 'Nominee is not a minor and KYC is attached', status: 'passed' },
  { label: 'Bank statement pages for February to April must be re-uploaded', status: 'attention' },
];

const auditSnapshot = [
  { at: '10 Aug 2024, 10:22 AM', by: 'Ganesh Thorat', role: 'Borrower / Member', action: 'Application submitted', evidence: 'Portal submission v1' },
  { at: '12 Aug 2024, 03:15 PM', by: 'Suresh Patil', role: 'Deputy Manager - Finance', action: 'Completeness check started', evidence: 'Checklist v2' },
  { at: '15 Aug 2024, 11:40 AM', by: 'Suresh Patil', role: 'Deputy Manager - Finance', action: 'Deficiency raised', evidence: 'Bank statement pages missing' },
  { at: '18 Sep 2024, 04:05 PM', by: 'Aarti Desai', role: 'Company Secretary', action: 'Loan agreement notarisation verified', evidence: 'Document version LA-v3' },
];

const applicationSteps: Array<{ id: ApplicationStep; label: string; icon: React.ReactNode }> = [
  { id: 'applicant', label: 'Applicant', icon: <UserRound size={15} /> },
  { id: 'shareholding', label: 'Shares', icon: <Shield size={15} /> },
  { id: 'loan', label: 'Loan', icon: <IndianRupee size={15} /> },
  { id: 'nominee', label: 'Nominee', icon: <Signature size={15} /> },
  { id: 'documents', label: 'Documents', icon: <Upload size={15} /> },
  { id: 'declarations', label: 'Declarations', icon: <FileCheck size={15} /> },
  { id: 'review', label: 'Review', icon: <ClipboardList size={15} /> },
];

const requiredApplicationDocuments = [
  { id: 'borrowerPan', label: 'Borrower PAN', requiredFor: 'All borrowers', note: 'Self-attested PAN card copy' },
  { id: 'borrowerAadhaar', label: 'Borrower Aadhaar', requiredFor: 'Individual borrowers', note: 'Self-attested Aadhaar card copy' },
  { id: 'nomineePan', label: 'Nominee PAN', requiredFor: 'Applications with nominee', note: 'Self-attested nominee PAN copy' },
  { id: 'nomineeAadhaar', label: 'Nominee Aadhaar', requiredFor: 'Applications with nominee', note: 'Self-attested nominee Aadhaar copy' },
  { id: 'shareCertificate', label: 'Share Certificate Copy', requiredFor: 'Physical shares', note: 'Copy of SFPCL share certificate' },
  { id: 'landExtract', label: '7/12 Extract / Land Record', requiredFor: 'Agriculture loans', note: 'Agricultural land evidence' },
  { id: 'cropPlan', label: 'Crop Plan', requiredFor: 'All agriculture loans', note: 'Crop, acreage, season and expected cycle' },
  { id: 'bankStatement', label: 'Six-Month Bank Statement', requiredFor: 'All borrowers', note: 'Latest six months, complete pages' },
];

const panPattern = /^[A-Z]{5}[0-9]{4}[A-Z]$/;

const formatCurrency = (value: number) => `₹${value.toLocaleString('en-IN')}`;

const grievances = [
  { id: 'GR-001', subject: 'Interest calculation query on Dec 2024 instalment', status: 'resolved', date: '2025-01-10', response: 'Interest calculated at 12% p.a. on outstanding principal as per loan agreement.' },
];

// Historical / closed loans — per spec S07 section: Historical loans
const loanHistory = [
  {
    loanNo: 'LO00000021',
    disbursedOn: '15 September 2022',
    closedOn: '20 March 2023',
    sanctionedAmount: 300000,
    purpose: 'Crop Production (Grapes, Kharif 2022)',
    tenure: '6 months',
    interestRate: '12% p.a.',
    totalInterestPaid: 18000,
    totalPrincipalPaid: 300000,
    repaymentMode: 'Direct RTGS',
    nocIssued: true,
    nocDate: '25 March 2023',
    securityReturned: true,
    status: 'closed',
    repayments: [
      { due: '2022-12-31', principal: 150000, interest: 9000, status: 'paid', utr: 'SFPCL2022120009' },
      { due: '2023-03-20', principal: 150000, interest: 9000, status: 'paid', utr: 'SFPCL2023031415' },
    ],
  },
];

const BorrowerPortal: React.FC<{ onLogout?: () => void }> = ({ onLogout }) => {
  const { currentUser } = useRole();
  const [activeTab, setActiveTab] = useState<BorrowerTab>('overview');
  const [grievanceText, setGrievanceText] = useState('');
  const [grievanceSubject, setGrievanceSubject] = useState('');
  const [submittedGrievance, setSubmittedGrievance] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [applicationStep, setApplicationStep] = useState<ApplicationStep>('applicant');
  const [applicationSubmitted, setApplicationSubmitted] = useState(false);
  const [applicationDraftSaved, setApplicationDraftSaved] = useState(false);
  const [borrowerApplication, setBorrowerApplication] = useState({
    applicantType: 'individual_farmer',
    channel: 'Digital Portal',
    memberId: 'MEM-00042',
    borrowerName: currentUser.name,
    folioNumber: 'M-00042',
    contactNumber: '+91 98765 43210',
    email: currentUser.email,
    address: 'At Post Mohadi, Tal. Dindori, Nashik, Maharashtra',
    pan: 'ABCDE1234F',
    aadhaar: '7788',
    sharesHeld: 5,
    shareholdingMode: 'physical',
    dematBoId: '',
    valuationPerShare: 100000,
    requestedAmount: 500000,
    loanPurpose: 'crop_production',
    crop: 'Grapes',
    season: 'Kharif 2026',
    expectedRepaymentDate: '2026-03-31',
    loanType: 'short_term',
    subsidiaryRepayment: 'Sahyadri Farms Post Harvest Care Ltd.',
    nomineeName: 'Suman Thorat',
    nomineeDob: '1983-04-12',
    nomineeAge: 42,
    nomineeGender: 'female',
    nomineeRelationship: 'Spouse',
    nomineeMobile: '+91 99887 76655',
    nomineeAddress: 'Same as borrower',
    nomineePan: 'FGHIJ5678K',
    nomineeAadhaar: '4421',
    borrowerSignature: false,
    nomineeSignature: false,
    declarations: {
      agriculturePurpose: false,
      documentsTrue: false,
      noDefault: false,
      kycConsent: false,
      sanctionTerms: false,
    },
  });
  const [applicationDocs, setApplicationDocs] = useState<Record<string, { uploaded: boolean; selfAttested: boolean }>>(
    Object.fromEntries(requiredApplicationDocuments.map(doc => [doc.id, { uploaded: false, selfAttested: false }]))
  );

  const tabs: { id: BorrowerTab; label: string; icon: React.ReactNode }[] = [
    { id: 'overview',     label: 'Overview',            icon: <BarChart2 size={16} /> },
    { id: 'newApplication', label: 'New Application',    icon: <ClipboardList size={16} /> },
    { id: 'application',  label: 'Application Status',  icon: <FileText size={16} /> },
    { id: 'applicationData', label: 'Application Data',  icon: <ClipboardList size={16} /> },
    { id: 'repayments',   label: 'Repayments',          icon: <IndianRupee size={16} /> },
    { id: 'documents',    label: 'My Documents',        icon: <FileCheck size={16} /> },
    { id: 'loanHistory',  label: 'Loan History',         icon: <History size={16} /> },
    { id: 'supply',       label: 'Produce Supply',      icon: <Leaf size={16} /> },
    { id: 'grievance',    label: 'Raise Grievance',     icon: <MessageSquare size={16} /> },
  ];
  const activeSectionLabel = tabs.find(tab => tab.id === activeTab)?.label || 'My Loan';

  const currentStepIndex = applicationSteps.findIndex(step => step.id === applicationStep);
  const shareholdingLimit = borrowerApplication.sharesHeld * borrowerApplication.valuationPerShare;
  const landBasedLimit = 675000;
  const maximumPermissibleLimit = Math.min(shareholdingLimit, landBasedLimit);
  const uploadedRequiredDocs = requiredApplicationDocuments.filter(doc => applicationDocs[doc.id]?.uploaded && applicationDocs[doc.id]?.selfAttested).length;
  const allDocsComplete = uploadedRequiredDocs === requiredApplicationDocuments.length;
  const allDeclarationsAccepted = Object.values(borrowerApplication.declarations).every(Boolean);

  const updateApplication = (field: string, value: string | number | boolean) => {
    setApplicationDraftSaved(false);
    setBorrowerApplication(prev => ({ ...prev, [field]: value }));
  };

  const updateDeclaration = (field: keyof typeof borrowerApplication.declarations, value: boolean) => {
    setApplicationDraftSaved(false);
    setBorrowerApplication(prev => ({
      ...prev,
      declarations: { ...prev.declarations, [field]: value },
    }));
  };

  const toggleDocument = (docId: string, field: 'uploaded' | 'selfAttested') => {
    setApplicationDraftSaved(false);
    setApplicationDocs(prev => ({
      ...prev,
      [docId]: { ...prev[docId], [field]: !prev[docId]?.[field] },
    }));
  };

  const stepValidations: Record<ApplicationStep, { ok: boolean; message: string }> = {
    applicant: {
      ok: Boolean(borrowerApplication.borrowerName && borrowerApplication.folioNumber && borrowerApplication.memberId && borrowerApplication.contactNumber && borrowerApplication.address && panPattern.test(borrowerApplication.pan) && borrowerApplication.aadhaar.length >= 4),
      message: 'Applicant name, member ID, folio, contact, address, PAN and Aadhaar are mandatory.',
    },
    shareholding: {
      ok: borrowerApplication.sharesHeld > 0 && Boolean(borrowerApplication.shareholdingMode) && (borrowerApplication.shareholdingMode !== 'demat' || borrowerApplication.dematBoId.length > 5),
      message: 'Shares held and shareholding mode are mandatory; Demat BO ID is required for demat shares.',
    },
    loan: {
      ok: borrowerApplication.requestedAmount > 0 && borrowerApplication.requestedAmount <= maximumPermissibleLimit && borrowerApplication.loanPurpose.includes('crop') && Boolean(borrowerApplication.crop && borrowerApplication.expectedRepaymentDate),
      message: 'Loan amount must be within eligible limit and purpose must be crop production or agriculture related.',
    },
    nominee: {
      ok: Boolean(borrowerApplication.nomineeName && borrowerApplication.nomineeGender && borrowerApplication.nomineePan && borrowerApplication.nomineeAadhaar) && borrowerApplication.nomineeAge >= 18 && panPattern.test(borrowerApplication.nomineePan),
      message: 'Nominee name, adult age, gender, PAN and Aadhaar are mandatory.',
    },
    documents: {
      ok: allDocsComplete,
      message: 'All mandatory KYC, shareholding, land, crop and bank statement documents must be uploaded and marked self-attested.',
    },
    declarations: {
      ok: allDeclarationsAccepted && borrowerApplication.borrowerSignature && borrowerApplication.nomineeSignature,
      message: 'All declarations plus borrower and nominee signatures are required before submission.',
    },
    review: {
      ok: true,
      message: 'Review the application before submitting.',
    },
  };

  const completenessItems = [
    ['Applicant details complete', stepValidations.applicant.ok],
    ['Folio number and shares captured', stepValidations.shareholding.ok],
    ['Requested amount and agriculture purpose valid', stepValidations.loan.ok],
    ['Nominee details complete and adult', stepValidations.nominee.ok],
    ['Mandatory documents uploaded and self-attested', stepValidations.documents.ok],
    ['Borrower and nominee signatures captured', borrowerApplication.borrowerSignature && borrowerApplication.nomineeSignature],
    ['Declarations accepted', allDeclarationsAccepted],
  ];

  const goApplicationNext = () => {
    if (currentStepIndex < applicationSteps.length - 1) {
      setApplicationStep(applicationSteps[currentStepIndex + 1].id);
    }
  };

  const goApplicationPrev = () => {
    if (currentStepIndex > 0) {
      setApplicationStep(applicationSteps[currentStepIndex - 1].id);
    }
  };

  const canSubmitApplication = completenessItems.every(([, complete]) => complete);

  const loanStages = [
    { label: 'Application Submitted',   done: true,  date: '10 Aug 2024', owner: 'Borrower' },
    { label: 'Completeness Check',      done: true,  date: '20 Aug 2024', owner: 'Deputy Manager - Finance' },
    { label: 'Appraisal & Eligibility', done: true,  date: '29 Aug 2024', owner: 'Credit Manager' },
    { label: 'Sanction Approval',       done: true,  date: '05 Sep 2024', owner: 'Sanction Committee' },
    { label: 'Documentation',           done: true,  date: '18 Sep 2024', owner: 'Company Secretary' },
    { label: 'SAP Setup',               done: true,  date: '21 Sep 2024', owner: 'Senior Manager - Finance' },
    { label: 'Disbursement',            done: true,  date: '22 Sep 2024', owner: 'CFC' },
    { label: 'Active Loan / Monitoring', done: true, date: 'Ongoing', owner: 'Credit and Accounts' },
    { label: 'Closure / NOC',           done: false, date: null, owner: 'Compliance and CS' },
  ];

  return (
    <div className="flex h-screen overflow-hidden bg-slate-50">
      <Sidebar
        activePage={activeTab}
        onNavigate={page => {
          if (tabs.some(tab => tab.id === page)) setActiveTab(page as BorrowerTab);
        }}
      />
      <div className="flex min-w-0 flex-1 flex-col overflow-hidden">
        <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-6 gap-4 flex-shrink-0 z-10">
          <div className="min-w-0">
            <div className="text-sm font-semibold text-slate-500">Member Portal</div>
            <h1 className="text-lg font-bold text-slate-900 truncate">{activeSectionLabel}</h1>
          </div>
          <div className="flex items-center gap-2 sm:gap-3 flex-shrink-0">
            <button className="p-2 text-slate-500 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition-colors relative" title="Notifications">
              <Bell size={18} />
              <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
            </button>
            <button className="p-2 text-slate-500 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition-colors" title="Help">
              <HelpCircle size={18} />
            </button>
            <div className="flex items-center gap-2 pl-3 pr-2 py-1.5 rounded-lg bg-slate-50 border border-slate-100">
              <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center text-green-700 font-semibold text-sm">
                {currentUser.name.charAt(0)}
              </div>
              <div className="hidden sm:block text-left">
                <div className="text-sm font-medium text-slate-900 leading-tight">{currentUser.name}</div>
                <div className="text-xs text-slate-500 leading-tight">Member · Folio M-00042</div>
              </div>
            </div>
            {onLogout && (
              <button
                onClick={onLogout}
                className="flex items-center gap-1 text-sm text-slate-500 hover:text-red-600 hover:bg-red-50 px-3 py-1.5 rounded-lg transition-colors"
              >
                <LogOut size={15} />
                <span className="hidden sm:inline">Sign out</span>
              </button>
            )}
          </div>
        </header>

        <main className="flex-1 overflow-y-auto">
          <div className="w-full px-4 sm:px-6 py-6">

        {/* Tab content */}
        {activeTab === 'newApplication' && (
          <div className="space-y-4">
            <div className="bg-white rounded-xl border border-slate-100 p-5">
              <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-4">
                <div>
                  <h3 className="font-semibold text-slate-900 flex items-center gap-2">
                    <ClipboardList size={16} className="text-green-600" />
                    New Loan Application
                  </h3>
                  <p className="text-xs text-slate-500 mt-1">
                    Complete each section, upload mandatory documents, sign declarations, then submit for completeness check.
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  {applicationDraftSaved && <span className="text-xs font-medium text-green-700">Draft saved</span>}
                  <button
                    onClick={() => setApplicationDraftSaved(true)}
                    className="flex items-center gap-2 px-3 py-2 rounded-lg border border-slate-200 text-sm font-medium text-slate-700 hover:bg-slate-50"
                  >
                    <Save size={15} />
                    Save Draft
                  </button>
                </div>
              </div>

              <div className="mt-5 overflow-x-auto">
                <div className="flex min-w-max gap-2">
                  {applicationSteps.map((step, index) => {
                    const isActive = step.id === applicationStep;
                    const isComplete = stepValidations[step.id].ok && index < currentStepIndex;
                    return (
                      <button
                        key={step.id}
                        onClick={() => setApplicationStep(step.id)}
                        className={`flex items-center gap-2 rounded-lg px-3 py-2 text-xs font-semibold transition-colors ${
                          isActive ? 'bg-green-600 text-white' :
                          isComplete ? 'bg-green-50 text-green-700' : 'bg-slate-50 text-slate-500'
                        }`}
                      >
                        {isComplete ? <CheckCircle2 size={15} /> : step.icon}
                        {step.label}
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>

            {applicationSubmitted ? (
              <div className="bg-white rounded-xl border border-green-200 p-8 text-center">
                <CheckCircle2 size={44} className="mx-auto text-green-600 mb-4" />
                <h3 className="text-lg font-bold text-slate-900">Application submitted for completeness check</h3>
                <p className="text-sm text-slate-500 mt-2">
                  Draft ID DRAFT-APP-0042 has been submitted. The official LO reference will be generated only after the Deputy Manager - Finance completes the mandatory checklist.
                </p>
                <div className="mt-5 flex flex-col sm:flex-row justify-center gap-3">
                  <button onClick={() => setActiveTab('application')} className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm font-semibold">
                    View Application Status
                  </button>
                  <button onClick={() => setApplicationSubmitted(false)} className="border border-slate-200 text-slate-700 px-4 py-2 rounded-lg text-sm font-semibold hover:bg-slate-50">
                    Edit Draft Copy
                  </button>
                </div>
              </div>
            ) : (
              <div className="bg-white rounded-xl border border-slate-100 p-5">
                {applicationStep === 'applicant' && (
                  <div className="space-y-5">
                    <div>
                      <h3 className="font-semibold text-slate-900">Applicant Identification</h3>
                      <p className="text-xs text-slate-500 mt-1">Member identity must match the SFPCL member master and KYC records.</p>
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1.5">Application Channel</label>
                        <select value={borrowerApplication.channel} onChange={e => updateApplication('channel', e.target.value)} className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm">
                          <option>Digital Portal</option>
                          <option>Assisted Entry</option>
                          <option>Physical Submission</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1.5">Applicant Type</label>
                        <select value={borrowerApplication.applicantType} onChange={e => updateApplication('applicantType', e.target.value)} className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm">
                          <option value="individual_farmer">Individual Farmer</option>
                          <option value="fpc">FPC</option>
                          <option value="producer_institution">Producer Institution</option>
                        </select>
                      </div>
                      {[
                        ['Borrower Name', 'borrowerName'],
                        ['Member ID', 'memberId'],
                        ['Folio Number', 'folioNumber'],
                        ['Contact Number', 'contactNumber'],
                        ['Email', 'email'],
                        ['PAN', 'pan'],
                        ['Aadhaar last 4 digits', 'aadhaar'],
                      ].map(([label, field]) => (
                        <div key={field}>
                          <label className="block text-sm font-medium text-slate-700 mb-1.5">{label}</label>
                          <input
                            value={String(borrowerApplication[field as keyof typeof borrowerApplication])}
                            onChange={e => updateApplication(field, field === 'pan' ? e.target.value.toUpperCase() : e.target.value)}
                            className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                          />
                        </div>
                      ))}
                      <div className="sm:col-span-2">
                        <label className="block text-sm font-medium text-slate-700 mb-1.5">Registered Address</label>
                        <textarea
                          value={borrowerApplication.address}
                          onChange={e => updateApplication('address', e.target.value)}
                          rows={3}
                          className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500 resize-none"
                        />
                      </div>
                    </div>
                  </div>
                )}

                {applicationStep === 'shareholding' && (
                  <div className="space-y-5">
                    <div>
                      <h3 className="font-semibold text-slate-900">Shareholding Details</h3>
                      <p className="text-xs text-slate-500 mt-1">Shares held drive the maximum permissible loan limit and security workflow.</p>
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1.5">Number of Shares Held</label>
                        <input type="number" min={1} value={borrowerApplication.sharesHeld} onChange={e => updateApplication('sharesHeld', Number(e.target.value))} className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm" />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1.5">Shareholding Mode</label>
                        <select value={borrowerApplication.shareholdingMode} onChange={e => updateApplication('shareholdingMode', e.target.value)} className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm">
                          <option value="physical">Physical</option>
                          <option value="demat">Demat</option>
                          <option value="mixed">Mixed</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1.5">Latest Valuation per Share</label>
                        <input type="number" value={borrowerApplication.valuationPerShare} onChange={e => updateApplication('valuationPerShare', Number(e.target.value))} className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm" />
                      </div>
                      {(borrowerApplication.shareholdingMode === 'demat' || borrowerApplication.shareholdingMode === 'mixed') && (
                        <div>
                          <label className="block text-sm font-medium text-slate-700 mb-1.5">Demat BO ID</label>
                          <input value={borrowerApplication.dematBoId} onChange={e => updateApplication('dematBoId', e.target.value)} placeholder="Required for CDSL pledge workflow" className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm" />
                        </div>
                      )}
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                      {[
                        ['Shareholding Limit', shareholdingLimit],
                        ['Land-Based Limit', landBasedLimit],
                        ['Maximum Permissible Limit', maximumPermissibleLimit],
                      ].map(([label, amount]) => (
                        <div key={label} className="rounded-lg border border-green-100 bg-green-50 p-3">
                          <div className="text-xs text-green-700">{label}</div>
                          <div className="mt-1 text-lg font-bold text-green-900">{formatCurrency(Number(amount))}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {applicationStep === 'loan' && (
                  <div className="space-y-5">
                    <div>
                      <h3 className="font-semibold text-slate-900">Requested Loan Details</h3>
                      <p className="text-xs text-slate-500 mt-1">Purpose must be crop production or agriculture related; excess amount is blocked before submission.</p>
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1.5">Required Loan Amount</label>
                        <input type="number" min={1} value={borrowerApplication.requestedAmount} onChange={e => updateApplication('requestedAmount', Number(e.target.value))} className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm" />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1.5">Loan Purpose</label>
                        <select value={borrowerApplication.loanPurpose} onChange={e => updateApplication('loanPurpose', e.target.value)} className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm">
                          <option value="crop_production">Crop Production</option>
                          <option value="agriculture_activity">Agriculture Activity</option>
                        </select>
                      </div>
                      {[
                        ['Crop', 'crop'],
                        ['Season / Cycle', 'season'],
                        ['Expected Repayment Date', 'expectedRepaymentDate'],
                        ['Subsidiary Repayment Linkage', 'subsidiaryRepayment'],
                      ].map(([label, field]) => (
                        <div key={field}>
                          <label className="block text-sm font-medium text-slate-700 mb-1.5">{label}</label>
                          <input
                            type={field === 'expectedRepaymentDate' ? 'date' : 'text'}
                            value={String(borrowerApplication[field as keyof typeof borrowerApplication])}
                            onChange={e => updateApplication(field, e.target.value)}
                            className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm"
                          />
                        </div>
                      ))}
                      <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1.5">Loan Type Requested</label>
                        <select value={borrowerApplication.loanType} onChange={e => updateApplication('loanType', e.target.value)} className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm">
                          <option value="short_term">Short-term</option>
                          <option value="long_term">Long-term</option>
                        </select>
                      </div>
                    </div>
                    {borrowerApplication.requestedAmount > maximumPermissibleLimit && (
                      <div className="flex items-start gap-3 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-800">
                        <AlertTriangle size={16} className="mt-0.5 flex-shrink-0" />
                        Requested amount exceeds maximum permissible limit of {formatCurrency(maximumPermissibleLimit)}.
                      </div>
                    )}
                  </div>
                )}

                {applicationStep === 'nominee' && (
                  <div className="space-y-5">
                    <div>
                      <h3 className="font-semibold text-slate-900">Nominee Details</h3>
                      <p className="text-xs text-slate-500 mt-1">Nominee must not be a minor and PAN/Aadhaar copies are mandatory.</p>
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      {[
                        ['Nominee Full Name', 'nomineeName', 'text'],
                        ['Date of Birth', 'nomineeDob', 'date'],
                        ['Age', 'nomineeAge', 'number'],
                        ['Relationship to Borrower', 'nomineeRelationship', 'text'],
                        ['Mobile Number', 'nomineeMobile', 'text'],
                        ['PAN', 'nomineePan', 'text'],
                        ['Aadhaar last 4 digits', 'nomineeAadhaar', 'text'],
                      ].map(([label, field, type]) => (
                        <div key={field}>
                          <label className="block text-sm font-medium text-slate-700 mb-1.5">{label}</label>
                          <input
                            type={type}
                            value={String(borrowerApplication[field as keyof typeof borrowerApplication])}
                            onChange={e => updateApplication(field, type === 'number' ? Number(e.target.value) : field === 'nomineePan' ? e.target.value.toUpperCase() : e.target.value)}
                            className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm"
                          />
                        </div>
                      ))}
                      <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1.5">Gender</label>
                        <select value={borrowerApplication.nomineeGender} onChange={e => updateApplication('nomineeGender', e.target.value)} className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm">
                          <option value="female">Female</option>
                          <option value="male">Male</option>
                          <option value="other">Other</option>
                        </select>
                      </div>
                      <div className="sm:col-span-2">
                        <label className="block text-sm font-medium text-slate-700 mb-1.5">Nominee Address</label>
                        <textarea value={borrowerApplication.nomineeAddress} onChange={e => updateApplication('nomineeAddress', e.target.value)} rows={3} className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm resize-none" />
                      </div>
                    </div>
                  </div>
                )}

                {applicationStep === 'documents' && (
                  <div className="space-y-5">
                    <div>
                      <h3 className="font-semibold text-slate-900">Mandatory Document Uploads</h3>
                      <p className="text-xs text-slate-500 mt-1">Each required document must be uploaded and marked self-attested before submission.</p>
                    </div>
                    <div className="space-y-3">
                      {requiredApplicationDocuments.map(doc => {
                        const docState = applicationDocs[doc.id];
                        return (
                          <div key={doc.id} className="rounded-lg border border-slate-200 p-4">
                            <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-3">
                              <div>
                                <div className="font-medium text-slate-900">{doc.label}</div>
                                <div className="text-xs text-slate-500 mt-1">{doc.requiredFor} · {doc.note}</div>
                              </div>
                              <div className="flex flex-wrap items-center gap-2">
                                <button onClick={() => toggleDocument(doc.id, 'uploaded')} className={`px-3 py-1.5 rounded-lg border text-xs font-semibold ${docState.uploaded ? 'bg-green-50 border-green-200 text-green-700' : 'border-slate-200 text-slate-600'}`}>
                                  {docState.uploaded ? 'Uploaded' : 'Mark Uploaded'}
                                </button>
                                <button onClick={() => toggleDocument(doc.id, 'selfAttested')} className={`px-3 py-1.5 rounded-lg border text-xs font-semibold ${docState.selfAttested ? 'bg-green-50 border-green-200 text-green-700' : 'border-slate-200 text-slate-600'}`}>
                                  {docState.selfAttested ? 'Self-attested' : 'Self-attested?'}
                                </button>
                              </div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                    <div className="rounded-lg bg-slate-50 border border-slate-100 p-3 text-sm text-slate-600">
                      {uploadedRequiredDocs} of {requiredApplicationDocuments.length} mandatory documents are uploaded and self-attested.
                    </div>
                  </div>
                )}

                {applicationStep === 'declarations' && (
                  <div className="space-y-5">
                    <div>
                      <h3 className="font-semibold text-slate-900">Declarations & Signatures</h3>
                      <p className="text-xs text-slate-500 mt-1">These declarations are required by the application and completeness workflow.</p>
                    </div>
                    <div className="space-y-3">
                      {[
                        ['agriculturePurpose', 'Loan purpose is related to crop production / agriculture activity.'],
                        ['documentsTrue', 'Submitted documents are true, complete and self-attested.'],
                        ['noDefault', 'Borrower is not in default with SFPCL, subsidiaries or associate companies.'],
                        ['kycConsent', 'Borrower consents to KYC / CKYC checks and verification.'],
                        ['sanctionTerms', 'Borrower agrees that final terms will be governed by the sanctioned Term Sheet and Loan Agreement.'],
                      ].map(([field, label]) => (
                        <label key={field} className="flex items-start gap-3 rounded-lg border border-slate-200 p-3 text-sm">
                          <input type="checkbox" checked={borrowerApplication.declarations[field as keyof typeof borrowerApplication.declarations]} onChange={e => updateDeclaration(field as keyof typeof borrowerApplication.declarations, e.target.checked)} className="mt-1" />
                          <span className="text-slate-700">{label}</span>
                        </label>
                      ))}
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      <label className="flex items-start gap-3 rounded-lg border border-slate-200 p-3 text-sm">
                        <input type="checkbox" checked={borrowerApplication.borrowerSignature} onChange={e => updateApplication('borrowerSignature', e.target.checked)} className="mt-1" />
                        <span className="text-slate-700">Borrower signature captured</span>
                      </label>
                      <label className="flex items-start gap-3 rounded-lg border border-slate-200 p-3 text-sm">
                        <input type="checkbox" checked={borrowerApplication.nomineeSignature} onChange={e => updateApplication('nomineeSignature', e.target.checked)} className="mt-1" />
                        <span className="text-slate-700">Nominee signature captured</span>
                      </label>
                    </div>
                  </div>
                )}

                {applicationStep === 'review' && (
                  <div className="space-y-5">
                    <div>
                      <h3 className="font-semibold text-slate-900">Review & Submit</h3>
                      <p className="text-xs text-slate-500 mt-1">The official LO reference is generated only after internal completeness verification.</p>
                    </div>
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                      <div className="rounded-lg border border-slate-200 p-4">
                        <h4 className="font-semibold text-slate-900 mb-3">Application Summary</h4>
                        <div className="space-y-2 text-sm">
                          {[
                            ['Applicant', borrowerApplication.borrowerName],
                            ['Folio / Shares', `${borrowerApplication.folioNumber} / ${borrowerApplication.sharesHeld}`],
                            ['Requested Amount', formatCurrency(borrowerApplication.requestedAmount)],
                            ['Maximum Permissible Limit', formatCurrency(maximumPermissibleLimit)],
                            ['Purpose', borrowerApplication.loanPurpose.replace(/_/g, ' ')],
                            ['Nominee', `${borrowerApplication.nomineeName}, age ${borrowerApplication.nomineeAge}`],
                          ].map(([label, value]) => (
                            <div key={label} className="grid grid-cols-[140px_1fr] gap-3">
                              <span className="text-slate-500">{label}</span>
                              <span className="font-medium text-slate-900">{value}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                      <div className="rounded-lg border border-slate-200 p-4">
                        <h4 className="font-semibold text-slate-900 mb-3">Completeness Checklist</h4>
                        <div className="space-y-2">
                          {completenessItems.map(([label, complete]) => (
                            <div key={String(label)} className="flex items-center gap-2 text-sm">
                              {complete ? <CheckCircle2 size={15} className="text-green-600" /> : <AlertTriangle size={15} className="text-amber-600" />}
                              <span className={complete ? 'text-slate-700' : 'text-amber-700'}>{label}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {applicationStep !== 'review' && !stepValidations[applicationStep].ok && (
                  <div className="mt-5 flex items-start gap-3 rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm text-amber-800">
                    <AlertTriangle size={16} className="mt-0.5 flex-shrink-0" />
                    {stepValidations[applicationStep].message}
                  </div>
                )}

                <div className="mt-6 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-t border-slate-100 pt-4">
                  <button
                    onClick={goApplicationPrev}
                    disabled={currentStepIndex === 0}
                    className="flex items-center justify-center gap-2 rounded-lg border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-50"
                  >
                    <ChevronLeft size={15} />
                    Back
                  </button>
                  {applicationStep === 'review' ? (
                    <button
                      onClick={() => setApplicationSubmitted(true)}
                      disabled={!canSubmitApplication}
                      className="flex items-center justify-center gap-2 rounded-lg bg-green-600 px-4 py-2 text-sm font-semibold text-white disabled:opacity-40 disabled:cursor-not-allowed hover:bg-green-700"
                    >
                      <ChevronRight size={15} />
                      Submit Application
                    </button>
                  ) : (
                    <button
                      onClick={goApplicationNext}
                      disabled={!stepValidations[applicationStep].ok}
                      className="flex items-center justify-center gap-2 rounded-lg bg-green-600 px-4 py-2 text-sm font-semibold text-white disabled:opacity-40 disabled:cursor-not-allowed hover:bg-green-700"
                    >
                      Continue
                      <ChevronRight size={15} />
                    </button>
                  )}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'overview' && (
          <div className="space-y-4">

            {/* Welcome banner — overview only */}
            <div className="bg-gradient-to-r from-green-600 to-green-700 rounded-2xl p-5 sm:p-6 text-white">
              <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
                <div>
                  <p className="text-green-100 text-sm mb-1">Welcome back</p>
                  <h2 className="text-2xl font-bold">{currentUser.name}</h2>
                  <p className="text-green-100 text-sm mt-1">Folio: M-00042 · Shares: 5 · Member since 2019</p>
                  <div className="mt-2 inline-flex items-center gap-1.5 bg-white/20 text-white text-xs font-semibold px-2.5 py-1 rounded-full">
                    <CheckCircle2 size={11} /> Active Member ✓
                  </div>
                </div>
                <div className="sm:text-right">
                  <p className="text-green-100 text-xs mb-1">Outstanding Loan</p>
                  <p className="text-2xl font-bold">₹3,50,000</p>
                  <p className="text-green-100 text-xs mt-1">Loan No. LO00000042</p>
                </div>
              </div>
              {/* Overdue alert — darker background for legibility on green */}
              <div className="mt-4 bg-red-900/50 border border-red-300/40 rounded-xl p-3 flex flex-col sm:flex-row sm:items-center gap-3">
                <AlertTriangle size={18} className="text-red-200 flex-shrink-0" />
                <div className="min-w-0">
                  <p className="text-sm font-semibold text-white">Instalment overdue</p>
                  <p className="text-xs text-red-100">₹1,05,000 due on 30 Jun 2025 — please contact your SFPCL officer</p>
                </div>
                <button onClick={() => setActiveTab('repayments')} className="sm:ml-auto flex-shrink-0 text-xs bg-white/20 hover:bg-white/30 text-white px-3 py-1.5 rounded-lg transition-colors">
                  View Schedule
                </button>
              </div>
            </div>

            {/* Quick stats */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {[
                { label: 'Loan Amount', value: '₹5,00,000', icon: <CreditCard size={16} />, color: 'text-green-600' },
                { label: 'Outstanding', value: '₹3,50,000', icon: <IndianRupee size={16} />, color: 'text-red-500' },
                { label: 'EMIs Paid', value: '2 of 5', icon: <CheckCircle2 size={16} />, color: 'text-green-600' },
                { label: 'Next Due', value: '30 Sep 2025', icon: <Calendar size={16} />, color: 'text-amber-600' },
              ].map(s => (
                <div key={s.label} className="bg-white rounded-xl p-4 border border-slate-100">
                  <div className={`${s.color} mb-2`}>{s.icon}</div>
                  <div className="text-lg font-bold text-slate-900">{s.value}</div>
                  <div className="text-xs text-slate-500">{s.label}</div>
                </div>
              ))}
            </div>

            {/* Pending Actions */}
            <div className="bg-white rounded-xl border border-slate-100 p-6">
              <h3 className="font-semibold text-slate-900 mb-4 flex items-center gap-2">
                <AlertCircle size={16} className="text-amber-500" />
                Pending Actions
              </h3>
              <div className="space-y-3">
                <div className="flex items-start gap-3 rounded-lg border border-red-200 bg-red-50 p-3">
                  <AlertTriangle size={15} className="text-red-600 flex-shrink-0 mt-0.5" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold text-red-800">Overdue instalment — ₹1,05,000</p>
                    <p className="text-xs text-red-600 mt-0.5">Due: 30 June 2025 · Loan No. LO00000042 · Contact your SFPCL officer immediately</p>
                  </div>
                  <button onClick={() => setActiveTab('repayments')} className="flex-shrink-0 text-xs bg-red-600 text-white px-3 py-1.5 rounded-lg hover:bg-red-700 transition-colors">View</button>
                </div>
                <div className="flex items-start gap-3 rounded-lg border border-amber-200 bg-amber-50 p-3">
                  <AlertTriangle size={15} className="text-amber-600 flex-shrink-0 mt-0.5" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold text-amber-800">Bank statement deficiency open</p>
                    <p className="text-xs text-amber-700 mt-0.5">February to April pages requested — upload corrected statement via Application Data</p>
                  </div>
                  <button onClick={() => setActiveTab('applicationData')} className="flex-shrink-0 text-xs bg-amber-600 text-white px-3 py-1.5 rounded-lg hover:bg-amber-700 transition-colors">Respond</button>
                </div>
                <div className="flex items-start gap-3 rounded-lg border border-slate-200 bg-slate-50 p-3">
                  <Clock size={15} className="text-slate-500 flex-shrink-0 mt-0.5" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-slate-700">Re-KYC due: 30 September 2026</p>
                    <p className="text-xs text-slate-500 mt-0.5">Ensure your PAN and Aadhaar copies are updated before the re-KYC deadline</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {/* Member & Eligibility */}
              <div className="bg-white rounded-xl border border-slate-100 p-6">
                <h3 className="font-semibold text-slate-900 mb-4 flex items-center gap-2">
                  <Shield size={16} className="text-green-600" />
                  Member &amp; Eligibility
                </h3>
                <div className="space-y-2.5">
                  {[
                    ['Member Type', 'Individual Farmer'],
                    ['Folio Number', 'M-00042'],
                    ['Shares Held', '5 shares (Physical)'],
                    ['Land Under Cultivation', '4.5 acres'],
                    ['Produce Supply', '5 consecutive years'],
                    ['4-Year Rule', 'Met ✓'],
                    ['KYC Status', 'Verified ✓'],
                    ['Re-KYC Due', '30 September 2026'],
                    ['Default Status', 'No default on record'],
                  ].map(([k, v]) => (
                    <div key={k} className="flex items-center justify-between text-sm border-b border-slate-50 pb-2 last:border-0 last:pb-0">
                      <span className="text-slate-500">{k}</span>
                      <span className="font-medium text-slate-900 text-right">{v}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* My Loan Details */}
              <div className="bg-white rounded-xl border border-slate-100 p-6">
                <h3 className="font-semibold text-slate-900 mb-4 flex items-center gap-2">
                  <Leaf size={16} className="text-green-600" />
                  My Loan Details
                </h3>
                <div className="space-y-2.5">
                  {[
                    ['Loan Account', 'LO00000042'],
                    ['Sanctioned Amount', '₹5,00,000'],
                    ['Outstanding Principal', '₹3,50,000'],
                    ['Interest Rate', '12% p.a.'],
                    ['Loan Type', 'Short-term (1 year)'],
                    ['Purpose', 'Crop Production'],
                    ['Next Instalment', '₹1,04,500 on 30 Sep 2025'],
                    ['Repayment Mode', 'Direct / Subsidiary deduction'],
                    ['Disbursed On', '22 September 2024'],
                  ].map(([k, v]) => (
                    <div key={k} className="flex items-center justify-between text-sm border-b border-slate-50 pb-2 last:border-0 last:pb-0">
                      <span className="text-slate-500">{k}</span>
                      <span className="font-medium text-slate-900 text-right">{v}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Security Instruments */}
            <div className="bg-white rounded-xl border border-slate-100 p-6">
              <h3 className="font-semibold text-slate-900 mb-4 flex items-center gap-2">
                <Shield size={16} className="text-green-600" />
                Security Instruments
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                {[
                  { doc: 'Share Certificate (SH-4)', status: 'held', note: 'Held in custody by Company Secretary', icon: <FileCheck size={15} className="text-slate-400" /> },
                  { doc: 'Power of Attorney', status: 'notarised', note: 'Notarised and executed', icon: <Signature size={15} className="text-slate-400" /> },
                  { doc: 'Blank-Dated Cheque', status: 'held', note: 'Held in custody by SFPCL', icon: <Landmark size={15} className="text-slate-400" /> },
                ].map(item => (
                  <div key={item.doc} className="flex items-start gap-3 p-3 rounded-lg border border-slate-100 bg-slate-50">
                    <div className="mt-0.5 flex-shrink-0">{item.icon}</div>
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium text-slate-800 mb-1">{item.doc}</div>
                      <div className="text-xs text-slate-400 mb-2">{item.note}</div>
                      <StatusBadge label={item.status} size="sm" />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Quick Actions */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {[
                { label: 'New Loan Application', icon: <ClipboardList size={20} />, style: 'bg-green-600 hover:bg-green-700 text-white shadow-sm shadow-green-200', tab: 'newApplication' },
                { label: 'Repayment Schedule', icon: <IndianRupee size={20} />, style: 'bg-white hover:bg-slate-50 text-slate-700 border border-slate-200', tab: 'repayments' },
                { label: 'My Documents', icon: <FileCheck size={20} />, style: 'bg-white hover:bg-slate-50 text-slate-700 border border-slate-200', tab: 'documents' },
                { label: 'Raise Grievance', icon: <MessageSquare size={20} />, style: 'bg-white hover:bg-slate-50 text-slate-700 border border-slate-200', tab: 'grievance' },
              ].map(action => (
                <button
                  key={action.label}
                  onClick={() => setActiveTab(action.tab as BorrowerTab)}
                  className={`flex flex-col items-center justify-center gap-2 rounded-xl p-4 text-sm font-medium transition-colors ${action.style}`}
                >
                  {action.icon}
                  <span className="text-center leading-tight">{action.label}</span>
                </button>
              ))}
            </div>

            {/* Contact Officer */}
            <div className="bg-white rounded-xl border border-slate-100 p-6">
              <h3 className="font-semibold text-slate-900 mb-1">Contact Your Officer</h3>
              <p className="text-xs text-slate-500 mb-4">For queries about your loan, repayment or documents, reach out to your assigned SFPCL credit officer.</p>
              <div className="flex gap-3">
                <button className="flex-1 flex items-center justify-center gap-2 bg-green-50 border border-green-200 text-green-700 px-4 py-2.5 rounded-lg text-sm font-medium hover:bg-green-100 transition-colors">
                  <Phone size={16} />
                  Call Officer
                </button>
                <button className="flex-1 flex items-center justify-center gap-2 bg-blue-50 border border-blue-200 text-blue-700 px-4 py-2.5 rounded-lg text-sm font-medium hover:bg-blue-100 transition-colors">
                  <MessageSquare size={16} />
                  WhatsApp
                </button>
              </div>
            </div>

          </div>
        )}

        {activeTab === 'application' && (
          <div className="bg-white rounded-xl border border-slate-100 p-6">
            <h3 className="font-semibold text-slate-900 mb-6">Application & Loan Progress</h3>
            <div className="space-y-0">
              {loanStages.map((stage, i) => (
                <div key={stage.label} className="flex gap-4">
                  <div className="flex flex-col items-center">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                      stage.done ? 'bg-green-600 text-white' : 'bg-slate-100 text-slate-400'
                    }`}>
                      {stage.done ? <CheckCircle2 size={16} /> : <Clock size={16} />}
                    </div>
                    {i < loanStages.length - 1 && (
                      <div className={`w-0.5 flex-1 my-1 min-h-[24px] ${stage.done ? 'bg-green-300' : 'bg-slate-100'}`} />
                    )}
                  </div>
                  <div className="pb-6 flex-1">
                    <div className={`text-sm font-medium ${stage.done ? 'text-slate-900' : 'text-slate-400'}`}>
                      {stage.label}
                    </div>
                    {stage.date && (
                      <div className="text-xs text-slate-400 mt-0.5">{stage.date}</div>
                    )}
                    <div className="text-xs text-slate-500 mt-1">Owner: {stage.owner}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'applicationData' && (
          <div className="space-y-4">
            <div className="bg-white rounded-xl border border-slate-100 p-5">
              <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3">
                <div>
                  <h3 className="font-semibold text-slate-900 flex items-center gap-2">
                    <ClipboardList size={16} className="text-green-600" />
                    Submitted Application Data
                  </h3>
                  <p className="text-xs text-slate-500 mt-1">
                    Locked after submission. Deficiency responses and requested uploads remain available to the borrower.
                  </p>
                </div>
                <StatusBadge label="submitted" size="sm" />
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {applicationFieldSections.map(section => {
                const Icon = section.icon;
                return (
                  <div key={section.title} className="bg-white rounded-xl border border-slate-100 p-5">
                    <h3 className="font-semibold text-slate-900 mb-4 flex items-center gap-2">
                      <Icon size={16} className="text-green-600" />
                      {section.title}
                    </h3>
                    <div className="space-y-3">
                      {section.rows.map(([label, value]) => (
                        <div key={label} className="grid grid-cols-1 sm:grid-cols-[150px_1fr] gap-1 sm:gap-3 text-sm">
                          <div className="text-slate-500">{label}</div>
                          <div className="font-medium text-slate-900 break-words">{value}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <div className="bg-white rounded-xl border border-slate-100 p-5">
                <h3 className="font-semibold text-slate-900 mb-4 flex items-center gap-2">
                  <AlertCircle size={16} className="text-amber-600" />
                  Validations & Deficiency Response
                </h3>
                <div className="space-y-3">
                  {validationMessages.map(item => (
                    <div
                      key={item.label}
                      className={`flex items-start gap-3 rounded-lg border p-3 text-sm ${
                        item.status === 'passed'
                          ? 'border-green-100 bg-green-50 text-green-800'
                          : 'border-amber-200 bg-amber-50 text-amber-800'
                      }`}
                    >
                      {item.status === 'passed'
                        ? <CheckCircle2 size={16} className="mt-0.5 flex-shrink-0" />
                        : <AlertTriangle size={16} className="mt-0.5 flex-shrink-0" />}
                      <span>{item.label}</span>
                    </div>
                  ))}
                </div>
                <div className="mt-4 rounded-lg border border-slate-200 p-4">
                  <label className="block text-sm font-medium text-slate-700 mb-1.5">Borrower response</label>
                  <textarea
                    rows={3}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500 resize-none"
                    placeholder="Add a note for the officer before uploading the corrected bank statement"
                  />
                  <button className="mt-3 flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
                    <ChevronRight size={15} />
                    Submit Deficiency Response
                  </button>
                </div>
              </div>

              <div className="bg-white rounded-xl border border-slate-100 p-5">
                <h3 className="font-semibold text-slate-900 mb-4 flex items-center gap-2">
                  <History size={16} className="text-green-600" />
                  Borrower-Visible Audit Snapshot
                </h3>
                <div className="space-y-3">
                  {auditSnapshot.map(item => (
                    <div key={`${item.at}-${item.action}`} className="border-l-2 border-green-200 pl-3 py-1">
                      <div className="text-sm font-medium text-slate-900">{item.action}</div>
                      <div className="text-xs text-slate-500 mt-0.5">{item.at} · {item.by} · {item.role}</div>
                      <div className="text-xs text-slate-400 mt-1">Evidence: {item.evidence}</div>
                    </div>
                  ))}
                </div>
                <div className="mt-4 rounded-lg bg-slate-50 border border-slate-100 p-3 text-xs text-slate-500">
                  IP/device metadata and restricted document versions are retained for internal audit and are not editable by borrowers.
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl border border-slate-100 p-5">
              <h3 className="font-semibold text-slate-900 mb-4 flex items-center gap-2">
                <Landmark size={16} className="text-green-600" />
                Verified Bank & Disbursement Evidence
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 text-sm">
                {[
                  ['Bank Account', 'RBL Bank ending 2042'],
                  ['Cancelled Cheque', 'Verified on 18 Sep 2024'],
                  ['SAP Customer Code', 'SAP-CUS-0042'],
                  ['Disbursement UTR', 'RBL2024092200891'],
                ].map(([label, value]) => (
                  <div key={label} className="rounded-lg border border-slate-100 bg-slate-50 p-3">
                    <div className="text-xs text-slate-500">{label}</div>
                    <div className="mt-1 font-semibold text-slate-900 break-words">{value}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'repayments' && (
          <div className="bg-white rounded-xl border border-slate-100 overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
              <h3 className="font-semibold text-slate-900">Repayment Schedule</h3>
              <button className="flex items-center gap-2 text-sm text-green-700 font-medium hover:underline">
                <Download size={14} />
                Download Schedule
              </button>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-slate-50">
                  <tr>
                    <th className="text-left px-6 py-3 text-xs font-semibold text-slate-500 uppercase">Due Date</th>
                    <th className="text-right px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Principal</th>
                    <th className="text-right px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Interest</th>
                    <th className="text-right px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Total</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Status</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Paid On</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-50">
                  {repaymentSchedule.map((row, i) => (
                    <tr key={i} className={`${row.status === 'overdue' ? 'bg-red-50' : ''} hover:bg-slate-50 transition-colors`}>
                      <td className="px-6 py-3 font-medium text-slate-800">{row.due}</td>
                      <td className="px-4 py-3 text-right text-slate-700">
                        {row.principal > 0 ? `₹${row.principal.toLocaleString('en-IN')}` : '—'}
                      </td>
                      <td className="px-4 py-3 text-right text-slate-700">₹{row.interest.toLocaleString('en-IN')}</td>
                      <td className="px-4 py-3 text-right font-semibold text-slate-900">₹{row.total.toLocaleString('en-IN')}</td>
                      <td className="px-4 py-3">
                        <StatusBadge label={row.status} size="sm" />
                      </td>
                      <td className="px-4 py-3 text-slate-500 text-xs">
                        {row.paid || '—'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeTab === 'documents' && (
          <div className="space-y-4">
            <div className="bg-white rounded-xl border border-slate-100 overflow-hidden">
              <div className="px-6 py-4 border-b border-slate-100">
                <h3 className="font-semibold text-slate-900">Available Documents</h3>
                <p className="text-xs text-slate-500 mt-0.5">Documents issued to you as part of your loan</p>
              </div>
              <div className="divide-y divide-slate-50">
                {myDocuments.map(doc => (
                  <div key={doc.name} className="px-6 py-4 flex items-center justify-between hover:bg-slate-50 transition-colors">
                    <div className="flex items-center gap-3 min-w-0">
                      <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${
                        doc.status === 'available' || doc.status === 'verified' ? 'bg-green-50' :
                        doc.status === 'deficient' ? 'bg-red-50' : 'bg-amber-50'
                      }`}>
                        <FileText
                          size={16}
                          className={
                            doc.status === 'available' || doc.status === 'verified' ? 'text-green-600' :
                            doc.status === 'deficient' ? 'text-red-600' : 'text-amber-600'
                          }
                        />
                      </div>
                      <div className="min-w-0">
                        <div className="flex flex-wrap items-center gap-2">
                          <div className="text-sm font-medium text-slate-800">{doc.name}</div>
                          <span className="text-[11px] font-medium text-slate-500 bg-slate-100 rounded px-1.5 py-0.5">{doc.section}</span>
                        </div>
                        <div className="text-xs text-slate-400">
                          {doc.date ? `Updated: ${doc.date}` : 'Not yet available'} · {doc.note}
                        </div>
                      </div>
                    </div>
                    {doc.status === 'available' || doc.status === 'verified' ? (
                      <button className="flex items-center gap-1.5 text-sm text-green-700 font-medium hover:underline flex-shrink-0">
                        <Download size={14} />
                        {doc.status === 'verified' ? 'View' : 'Download'}
                      </button>
                    ) : doc.status === 'deficient' ? (
                      <button
                        onClick={() => setShowUploadModal(true)}
                        className="text-xs text-red-700 bg-red-50 border border-red-100 px-2.5 py-1.5 rounded-lg font-medium flex-shrink-0"
                      >
                        Re-upload
                      </button>
                    ) : (
                      <span className="text-xs text-amber-600 font-medium flex-shrink-0">Pending</span>
                    )}
                  </div>
                ))}
              </div>
            </div>
            <div className="bg-white rounded-xl border border-slate-100 p-6">
              <h3 className="font-semibold text-slate-900 mb-1">Upload Documents</h3>
              <p className="text-xs text-slate-500 mb-4">If your officer has requested additional documents, upload them here.</p>
              <button
                onClick={() => setShowUploadModal(true)}
                className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-4 py-2.5 rounded-lg text-sm font-medium transition-colors"
              >
                <Upload size={16} />
                Upload Document
              </button>
            </div>
          </div>
        )}

        {activeTab === 'grievance' && (
          <div className="space-y-4">
            {grievances.length > 0 && (
              <div className="bg-white rounded-xl border border-slate-100 p-6">
                <h3 className="font-semibold text-slate-900 mb-4">My Grievances</h3>
                {grievances.map(g => (
                  <div key={g.id} className="border border-slate-100 rounded-xl p-4">
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <div className="text-sm font-medium text-slate-800">{g.subject}</div>
                        <div className="text-xs text-slate-400 mt-0.5">Ref: {g.id} · Raised: {g.date}</div>
                      </div>
                      <StatusBadge label={g.status} size="sm" />
                    </div>
                    {g.response && (
                      <div className="mt-3 bg-green-50 border border-green-100 rounded-lg p-3 text-sm text-green-800">
                        <span className="font-medium">SFPCL Response: </span>{g.response}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}

            <div className="bg-white rounded-xl border border-slate-100 p-6">
              <h3 className="font-semibold text-slate-900 mb-1 flex items-center gap-2">
                <HelpCircle size={16} className="text-green-600" />
                Raise a New Grievance
              </h3>
              <p className="text-xs text-slate-500 mb-5">We will respond within 7 working days.</p>

              {submittedGrievance ? (
                <div className="flex flex-col items-center py-8 text-center">
                  <CheckCircle2 size={40} className="text-green-500 mb-3" />
                  <div className="font-semibold text-slate-900 mb-1">Grievance submitted successfully</div>
                  <div className="text-sm text-slate-500">Reference: GR-{Date.now().toString().slice(-4)}</div>
                  <button
                    onClick={() => setSubmittedGrievance(false)}
                    className="mt-4 text-sm text-green-600 font-medium hover:underline"
                  >
                    Raise another grievance
                  </button>
                </div>
              ) : (
                <form onSubmit={e => { e.preventDefault(); if (grievanceSubject && grievanceText) setSubmittedGrievance(true); }} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1.5">Subject</label>
                    <input
                      type="text"
                      value={grievanceSubject}
                      onChange={e => setGrievanceSubject(e.target.value)}
                      placeholder="e.g. Query about interest amount"
                      className="w-full px-4 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1.5">Description</label>
                    <textarea
                      value={grievanceText}
                      onChange={e => setGrievanceText(e.target.value)}
                      rows={4}
                      placeholder="Please describe your issue in detail…"
                      className="w-full px-4 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500 resize-none"
                      required
                    />
                  </div>
                  <button
                    type="submit"
                    className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-5 py-2.5 rounded-lg text-sm font-semibold transition-colors"
                  >
                    <ChevronRight size={16} />
                    Submit Grievance
                  </button>
                </form>
              )}
            </div>
          </div>
        )}

        {/* ── Produce Supply Tab ── */}
        {activeTab === 'supply' && (
          <div className="space-y-4">
            <div className="bg-white rounded-xl border border-slate-100 p-5">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-slate-900 flex items-center gap-2">
                  <Leaf size={16} className="text-green-600" /> My Produce Supply History
                </h3>
                <div className={`inline-flex items-center gap-1.5 text-xs font-semibold px-2.5 py-1 rounded-full ${true ? 'bg-green-100 text-green-700' : 'bg-amber-100 text-amber-700'}`}>
                  <CheckCircle2 size={11} /> Active Member — 5 years supply
                </div>
              </div>
              <p className="text-xs text-slate-500 mb-4">
                Active member status requires 4 consecutive years of produce supply to SFPCL or its subsidiaries. Your current status qualifies you for loan eligibility.
              </p>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-slate-100">
                      {['Financial Year', 'Crop', 'Quantity', 'Supplied To', 'Invoice Ref.', 'Counts Toward Eligibility'].map(h => (
                        <th key={h} className="text-left py-2 px-3 text-xs text-slate-500 font-medium">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-50">
                    {[
                      { fy: 'FY 2024-25', crop: 'Grapes', qty: '12 MT', entity: 'SFPCL', ref: 'INV-2025-042', counts: true },
                      { fy: 'FY 2023-24', crop: 'Tomatoes', qty: '8 MT', entity: 'Sahyadri Farms PHC', ref: 'INV-2024-018', counts: true },
                      { fy: 'FY 2022-23', crop: 'Grapes', qty: '14 MT', entity: 'SFPCL', ref: 'INV-2023-055', counts: true },
                      { fy: 'FY 2021-22', crop: 'Sweetcorn', qty: '5 MT', entity: 'SFPCL', ref: 'INV-2022-031', counts: true },
                      { fy: 'FY 2020-21', crop: 'Grapes', qty: '10 MT', entity: 'SFPCL', ref: 'INV-2021-077', counts: true },
                    ].map((row, i) => (
                      <tr key={i} className="hover:bg-slate-50">
                        <td className="py-3 px-3 font-medium text-slate-800">{row.fy}</td>
                        <td className="py-3 px-3 text-slate-600">{row.crop}</td>
                        <td className="py-3 px-3 text-slate-600">{row.qty}</td>
                        <td className="py-3 px-3 text-slate-600">{row.entity}</td>
                        <td className="py-3 px-3 text-xs text-slate-400">{row.ref}</td>
                        <td className="py-3 px-3">
                          {row.counts
                            ? <span className="flex items-center gap-1 text-green-700 text-xs"><CheckCircle2 size={12} /> Yes</span>
                            : <span className="text-slate-400 text-xs">No</span>}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
            <div className="bg-white rounded-xl border border-slate-100 p-5">
              <h3 className="font-semibold text-slate-900 mb-3">Repayment via Subsidiary Deduction</h3>
              <p className="text-xs text-slate-500 mb-3">Some repayments may be deducted from your produce payment by the subsidiary. Here is the breakdown:</p>
              <div className="space-y-2">
                {[
                  { date: '2024-12-01', amount: '₹10,000', source: 'Sahyadri Farms Post Harvest Care Ltd.', type: 'Subsidiary Deduction', utr: 'UTR20241201005678' },
                ].map((r, i) => (
                  <div key={i} className="flex items-center gap-3 p-3 bg-slate-50 rounded-lg text-sm">
                    <div className="flex-1">
                      <p className="font-semibold text-slate-800">{r.amount} deducted</p>
                      <p className="text-xs text-slate-500">{r.source} · {new Date(r.date).toLocaleDateString('en-IN')}</p>
                      <p className="text-xs text-slate-400">UTR: {r.utr}</p>
                    </div>
                    <span className="text-xs bg-blue-50 text-blue-700 px-2 py-1 rounded">{r.type}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'loanHistory' && (
          <div className="space-y-4">

            {/* Summary header */}
            <div className="bg-white rounded-xl border border-slate-100 p-6">
              <h3 className="font-semibold text-slate-900 mb-1 flex items-center gap-2">
                <History size={16} className="text-green-600" />
                Loan History
              </h3>
              <p className="text-xs text-slate-500 mb-5">All previous SFPCL loans taken by you, including closed loans with NOC and security return status.</p>

              {/* Current active loan summary */}
              <div className="mb-6">
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">Current Active Loan</p>
                <div className="rounded-xl border border-green-200 bg-green-50 p-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-bold text-slate-900">LO00000042</span>
                      <span className="text-xs bg-amber-100 text-amber-700 font-semibold px-2 py-0.5 rounded-full">Overdue</span>
                    </div>
                    <p className="text-xs text-slate-600">Disbursed: 22 Sep 2024 · ₹5,00,000 · Crop Production (Grapes, Kharif 2024)</p>
                    <p className="text-xs text-slate-500">Outstanding: ₹3,50,000 · Next instalment: ₹1,04,500 on 30 Sep 2025</p>
                  </div>
                  <button onClick={() => setActiveTab('repayments')} className="flex-shrink-0 flex items-center gap-1.5 text-xs font-medium text-green-700 bg-white border border-green-200 px-3 py-1.5 rounded-lg hover:bg-green-50 transition-colors">
                    View Repayments <ChevronRight size={13} />
                  </button>
                </div>
              </div>

              {/* Historical loans */}
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">Closed / Historical Loans</p>
              <div className="space-y-4">
                {loanHistory.map(loan => (
                  <div key={loan.loanNo} className="rounded-xl border border-slate-200 overflow-hidden">
                    {/* Loan header */}
                    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 p-4 border-b border-slate-100 bg-slate-50">
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-sm font-bold text-slate-900">{loan.loanNo}</span>
                          <StatusBadge label={loan.status} size="sm" />
                          {loan.nocIssued && (
                            <span className="flex items-center gap-1 text-xs text-green-700 bg-green-100 px-2 py-0.5 rounded-full font-semibold">
                              <CheckCircle2 size={10} /> NOC Issued
                            </span>
                          )}
                        </div>
                        <p className="text-xs text-slate-500">{loan.purpose}</p>
                      </div>
                      <div className="sm:text-right flex-shrink-0">
                        <p className="text-sm font-bold text-slate-900">₹{loan.sanctionedAmount.toLocaleString('en-IN')}</p>
                        <p className="text-xs text-slate-500">Sanctioned Amount</p>
                      </div>
                    </div>

                    {/* Key details grid */}
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 p-4">
                      {[
                        ['Disbursed On', loan.disbursedOn],
                        ['Closed On', loan.closedOn],
                        ['Tenure', loan.tenure],
                        ['Interest Rate', loan.interestRate],
                        ['Total Principal Paid', `₹${loan.totalPrincipalPaid.toLocaleString('en-IN')}`],
                        ['Total Interest Paid', `₹${loan.totalInterestPaid.toLocaleString('en-IN')}`],
                        ['Repayment Mode', loan.repaymentMode],
                        ['Security Returned', loan.securityReturned ? 'Yes ✓' : 'Pending'],
                      ].map(([k, v]) => (
                        <div key={k}>
                          <p className="text-xs text-slate-400 mb-0.5">{k}</p>
                          <p className="text-sm font-medium text-slate-800">{v}</p>
                        </div>
                      ))}
                    </div>

                    {/* NOC row */}
                    {loan.nocIssued && (
                      <div className="flex items-center justify-between px-4 py-3 border-t border-slate-100 bg-green-50">
                        <div className="flex items-center gap-2">
                          <CheckCircle2 size={14} className="text-green-600" />
                          <span className="text-xs font-medium text-green-800">NOC issued on {loan.nocDate} · SH-4 and blank cheque returned</span>
                        </div>
                        <button className="flex items-center gap-1 text-xs text-green-700 font-medium hover:text-green-900">
                          <Download size={13} /> Download NOC
                        </button>
                      </div>
                    )}

                    {/* Repayment records */}
                    <div className="px-4 pb-4 pt-2">
                      <p className="text-xs font-semibold text-slate-500 mb-2">Repayment Record</p>
                      <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                          <thead>
                            <tr className="border-b border-slate-100">
                              {['Due Date', 'Principal', 'Interest', 'Status', 'UTR'].map(h => (
                                <th key={h} className="text-left py-2 px-2 text-xs text-slate-400 font-medium">{h}</th>
                              ))}
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-slate-50">
                            {loan.repayments.map((r, i) => (
                              <tr key={i} className="hover:bg-slate-50">
                                <td className="py-2 px-2 text-slate-600">{r.due}</td>
                                <td className="py-2 px-2 font-medium text-slate-800">₹{r.principal.toLocaleString('en-IN')}</td>
                                <td className="py-2 px-2 text-slate-600">₹{r.interest.toLocaleString('en-IN')}</td>
                                <td className="py-2 px-2"><StatusBadge label={r.status} size="sm" /></td>
                                <td className="py-2 px-2 text-xs text-slate-400 font-mono">{r.utr}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Footer CTA */}
            <div className="bg-white rounded-xl border border-slate-100 p-5 flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-800">Need a statement for an older loan?</p>
                <p className="text-xs text-slate-500 mt-0.5">Contact your SFPCL credit officer to request a full ledger or NOC copy for loans not listed here.</p>
              </div>
              <div className="flex gap-2 flex-shrink-0">
                <button className="flex items-center gap-1.5 text-xs font-medium text-green-700 bg-green-50 border border-green-200 px-3 py-2 rounded-lg hover:bg-green-100 transition-colors">
                  <Phone size={13} /> Call Officer
                </button>
                <button className="flex items-center gap-1.5 text-xs font-medium text-slate-700 bg-slate-50 border border-slate-200 px-3 py-2 rounded-lg hover:bg-slate-100 transition-colors">
                  <Download size={13} /> Request Statement
                </button>
              </div>
            </div>

          </div>
        )}
          </div>
        </main>
      </div>

      {/* Upload modal */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl w-full max-w-md p-6">
            <h3 className="font-semibold text-slate-900 mb-4">Upload Document</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1.5">Document Type</label>
                <select className="w-full px-4 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500 bg-white">
                  <option>PAN Card</option>
                  <option>Aadhaar Card</option>
                  <option>Nominee PAN/Aadhaar</option>
                  <option>Share Certificate Copy</option>
                  <option>7/12 Extract</option>
                  <option>Bank Statement</option>
                  <option>Crop Plan</option>
                  <option>Borrower/Nominee Signature Page</option>
                  <option>Other</option>
                </select>
              </div>
              <div className="border-2 border-dashed border-slate-200 rounded-xl p-8 text-center">
                <Upload size={24} className="mx-auto text-slate-300 mb-2" />
                <p className="text-sm text-slate-500">Click to select file or drag and drop</p>
                <p className="text-xs text-slate-400 mt-1">PDF, JPG, PNG · Max 5 MB</p>
              </div>
            </div>
            <div className="flex gap-3 mt-6">
              <button
                onClick={() => setShowUploadModal(false)}
                className="flex-1 px-4 py-2.5 border border-slate-200 rounded-lg text-sm font-medium text-slate-700 hover:bg-slate-50"
              >
                Cancel
              </button>
              <button
                onClick={() => setShowUploadModal(false)}
                className="flex-1 px-4 py-2.5 bg-green-600 hover:bg-green-700 text-white rounded-lg text-sm font-medium transition-colors"
              >
                Upload
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default BorrowerPortal;
