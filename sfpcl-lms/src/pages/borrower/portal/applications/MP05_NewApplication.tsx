import React, { useState } from 'react';
import { ClipboardList, Save, CheckCircle2, AlertTriangle, ChevronLeft, ChevronRight, UserRound, Shield, IndianRupee, Signature, Upload, FileCheck } from 'lucide-react';
import { useRole } from '../../../../contexts/RoleContext';
import { AuthSessionError } from '../../../../services/authSession';
import {
  createPortalApplicationDraft,
  submitPortalApplication,
  updatePortalApplicationDraft,
  type PortalApplication,
} from '../../../../services/portalApi';

type ApplicationStep = 'applicant' | 'shareholding' | 'loan' | 'nominee' | 'documents' | 'declarations' | 'review';

interface MP05_NewApplicationProps {
  onNavigateToApplication: (id: string) => void;
}

const MP05_NewApplication: React.FC<MP05_NewApplicationProps> = ({ onNavigateToApplication }) => {
  const { currentUser } = useRole();
  const [applicationStep, setApplicationStep] = useState<ApplicationStep>('applicant');
  const [applicationSubmitted, setApplicationSubmitted] = useState(false);
  const [applicationDraftSaved, setApplicationDraftSaved] = useState(false);
  const [savedApplication, setSavedApplication] = useState<PortalApplication | null>(null);
  const [saving, setSaving] = useState(false);
  const [apiMessage, setApiMessage] = useState<string | null>(null);
  
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

  const [applicationDocs, setApplicationDocs] = useState<Record<string, { uploaded: boolean; selfAttested: boolean }>>(
    Object.fromEntries(requiredApplicationDocuments.map(doc => [doc.id, { uploaded: false, selfAttested: false }]))
  );

  const applicationSteps: Array<{ id: ApplicationStep; label: string; icon: React.ReactNode }> = [
    { id: 'applicant', label: 'Applicant', icon: <UserRound size={15} /> },
    { id: 'shareholding', label: 'Shares', icon: <Shield size={15} /> },
    { id: 'loan', label: 'Loan', icon: <IndianRupee size={15} /> },
    { id: 'nominee', label: 'Nominee', icon: <Signature size={15} /> },
    { id: 'documents', label: 'Documents', icon: <Upload size={15} /> },
    { id: 'declarations', label: 'Declarations', icon: <FileCheck size={15} /> },
    { id: 'review', label: 'Review', icon: <ClipboardList size={15} /> },
  ];

  const currentStepIndex = applicationSteps.findIndex(step => step.id === applicationStep);
  const shareholdingLimit = borrowerApplication.sharesHeld * borrowerApplication.valuationPerShare;
  const landBasedLimit = 675000;
  const maximumPermissibleLimit = Math.min(shareholdingLimit, landBasedLimit);
  const uploadedRequiredDocs = requiredApplicationDocuments.filter(doc => applicationDocs[doc.id]?.uploaded && applicationDocs[doc.id]?.selfAttested).length;
  const allDocsComplete = uploadedRequiredDocs === requiredApplicationDocuments.length;
  const allDeclarationsAccepted = Object.values(borrowerApplication.declarations).every(Boolean);

  const panPattern = /^[A-Z]{5}[0-9]{4}[A-Z]$/;
  const formatCurrency = (value: number) => `₹${value.toLocaleString('en-IN')}`;

  const updateApplication = (field: string, value: string | number | boolean) => {
    setApplicationDraftSaved(false);
    setApiMessage(null);
    setBorrowerApplication(prev => ({ ...prev, [field]: value }));
  };

  const updateDeclaration = (field: keyof typeof borrowerApplication.declarations, value: boolean) => {
    setApplicationDraftSaved(false);
    setApiMessage(null);
    setBorrowerApplication(prev => ({
      ...prev,
      declarations: { ...prev.declarations, [field]: value },
    }));
  };

  const toggleDocument = (docId: string, field: 'uploaded' | 'selfAttested') => {
    setApplicationDraftSaved(false);
    setApiMessage(null);
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

  const portalDraftPayload = () => ({
    required_loan_amount: String(borrowerApplication.requestedAmount),
    declared_purpose: borrowerApplication.loanPurpose.replace(/_/g, ' '),
    purpose_category: borrowerApplication.loanPurpose,
    loan_type_requested: borrowerApplication.loanType,
    borrower_request_notes: `${borrowerApplication.crop} ${borrowerApplication.season}`.trim(),
    terms_acceptance_flag: allDeclarationsAccepted,
  });

  const saveDraft = async () => {
    setSaving(true);
    setApiMessage(null);
    try {
      const draft = savedApplication
        ? await updatePortalApplicationDraft(savedApplication.loan_application_id, portalDraftPayload())
        : await createPortalApplicationDraft(portalDraftPayload());
      setSavedApplication(draft);
      setApplicationDraftSaved(true);
    } catch (error) {
      setApiMessage(error instanceof AuthSessionError ? error.message : 'Draft could not be saved.');
    } finally {
      setSaving(false);
    }
  };

  const submitApplication = async () => {
    setSaving(true);
    setApiMessage(null);
    try {
      const draft = savedApplication
        ? await updatePortalApplicationDraft(savedApplication.loan_application_id, portalDraftPayload())
        : await createPortalApplicationDraft(portalDraftPayload());
      const submitted = await submitPortalApplication(draft.loan_application_id);
      setSavedApplication(submitted);
      setApplicationSubmitted(true);
    } catch (error) {
      setApiMessage(error instanceof AuthSessionError ? error.message : 'Application could not be submitted.');
    } finally {
      setSaving(false);
    }
  };

  return (
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
              onClick={saveDraft}
              disabled={saving}
              className="flex items-center gap-2 px-3 py-2 rounded-lg border border-slate-200 text-sm font-medium text-slate-700 hover:bg-slate-50 transition-colors"
            >
              <Save size={15} />
              {saving ? 'Saving...' : 'Save Draft'}
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
                    isComplete ? 'bg-green-50 text-green-700' : 'bg-slate-50 text-slate-500 hover:bg-slate-100'
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
            Application ID APP-2026-000001 has been submitted. The official LO reference will be generated only after the Deputy Manager - Finance completes the mandatory checklist.
          </p>
          <div className="mt-5 flex flex-col sm:flex-row justify-center gap-3">
            <button
              onClick={() => savedApplication && onNavigateToApplication(savedApplication.loan_application_id)}
              disabled={!savedApplication}
              className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm font-semibold transition-colors shadow-sm disabled:opacity-40 disabled:cursor-not-allowed"
            >
              View Application Status
            </button>
            <button onClick={() => setApplicationSubmitted(false)} className="border border-slate-200 text-slate-700 px-4 py-2 rounded-lg text-sm font-semibold hover:bg-slate-50 transition-colors">
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
                  <select value={borrowerApplication.channel} onChange={e => updateApplication('channel', e.target.value)} className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm bg-white">
                    <option>Digital Portal</option>
                    <option>Assisted Entry</option>
                    <option>Physical Submission</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1.5">Applicant Type</label>
                  <select value={borrowerApplication.applicantType} onChange={e => updateApplication('applicantType', e.target.value)} className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm bg-white">
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
                  <select value={borrowerApplication.shareholdingMode} onChange={e => updateApplication('shareholdingMode', e.target.value)} className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm bg-white">
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
                  <select value={borrowerApplication.loanPurpose} onChange={e => updateApplication('loanPurpose', e.target.value)} className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm bg-white">
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
                  <select value={borrowerApplication.loanType} onChange={e => updateApplication('loanType', e.target.value)} className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm bg-white">
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
                  <select value={borrowerApplication.nomineeGender} onChange={e => updateApplication('nomineeGender', e.target.value)} className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm bg-white">
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
                    <div key={doc.id} className="rounded-lg border border-slate-200 p-4 hover:bg-slate-50 transition-colors">
                      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-3">
                        <div>
                          <div className="font-medium text-slate-900">{doc.label}</div>
                          <div className="text-xs text-slate-500 mt-1">{doc.requiredFor} · {doc.note}</div>
                        </div>
                        <div className="flex flex-wrap items-center gap-2">
                          <button onClick={() => toggleDocument(doc.id, 'uploaded')} className={`px-3 py-1.5 rounded-lg border text-xs font-semibold transition-colors ${docState.uploaded ? 'bg-green-50 border-green-200 text-green-700' : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-100'}`}>
                            {docState.uploaded ? 'Uploaded' : 'Mark Uploaded'}
                          </button>
                          <button onClick={() => toggleDocument(doc.id, 'selfAttested')} className={`px-3 py-1.5 rounded-lg border text-xs font-semibold transition-colors ${docState.selfAttested ? 'bg-green-50 border-green-200 text-green-700' : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-100'}`}>
                            {docState.selfAttested ? 'Self-attested' : 'Self-attested?'}
                          </button>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
              <div className="rounded-lg bg-slate-50 border border-slate-100 p-3 text-sm text-slate-600 font-medium">
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
                  <label key={field} className="flex items-start gap-3 rounded-lg border border-slate-200 p-3 text-sm cursor-pointer hover:bg-slate-50 transition-colors">
                    <input type="checkbox" checked={borrowerApplication.declarations[field as keyof typeof borrowerApplication.declarations]} onChange={e => updateDeclaration(field as keyof typeof borrowerApplication.declarations, e.target.checked)} className="mt-1" />
                    <span className="text-slate-700">{label}</span>
                  </label>
                ))}
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <label className="flex items-start gap-3 rounded-lg border border-slate-200 p-3 text-sm cursor-pointer hover:bg-slate-50 transition-colors">
                  <input type="checkbox" checked={borrowerApplication.borrowerSignature} onChange={e => updateApplication('borrowerSignature', e.target.checked)} className="mt-1" />
                  <span className="text-slate-700">Borrower signature captured</span>
                </label>
                <label className="flex items-start gap-3 rounded-lg border border-slate-200 p-3 text-sm cursor-pointer hover:bg-slate-50 transition-colors">
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
                      ['Maximum Limit', formatCurrency(maximumPermissibleLimit)],
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
                        <span className={complete ? 'text-slate-700 font-medium' : 'text-amber-700'}>{label}</span>
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

          {apiMessage && (
            <div className="mt-5 flex items-start gap-3 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-800">
              <AlertTriangle size={16} className="mt-0.5 flex-shrink-0" />
              {apiMessage}
            </div>
          )}

          <div className="mt-6 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-t border-slate-100 pt-4">
            <button
              onClick={goApplicationPrev}
              disabled={currentStepIndex === 0}
              className="flex items-center justify-center gap-2 rounded-lg bg-white border border-slate-200 px-4 py-2.5 text-sm font-semibold text-slate-700 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-50 transition-colors"
            >
              <ChevronLeft size={15} />
              Back
            </button>
            {applicationStep === 'review' ? (
              <button
                onClick={submitApplication}
                disabled={!canSubmitApplication || saving}
                className="flex items-center justify-center gap-2 rounded-lg bg-green-600 px-6 py-2.5 text-sm font-semibold text-white disabled:opacity-40 disabled:cursor-not-allowed hover:bg-green-700 transition-colors shadow-sm"
              >
                <ChevronRight size={15} />
                {saving ? 'Submitting...' : 'Submit Application'}
              </button>
            ) : (
              <button
                onClick={goApplicationNext}
                disabled={!stepValidations[applicationStep].ok}
                className="flex items-center justify-center gap-2 rounded-lg bg-green-600 px-6 py-2.5 text-sm font-semibold text-white disabled:opacity-40 disabled:cursor-not-allowed hover:bg-green-700 transition-colors shadow-sm"
              >
                Continue
                <ChevronRight size={15} />
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default MP05_NewApplication;
