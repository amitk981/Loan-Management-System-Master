import React, { useEffect, useState } from 'react';
import {
  AlertTriangle, Calculator, Check, CheckCircle2, ChevronLeft, ChevronRight,
  FileCheck, FileText, IndianRupee, Save, Shield, Signature, Upload, User
} from 'lucide-react';
import { useRole } from '../../contexts/RoleContext';
import LoanLimitCalculator from '../../components/loan/LoanLimitCalculator';
import { fetchMemberDirectory, type MemberDirectoryItem } from '../../services/memberDirectoryApi';
import {
  createStaffApplicationDraft,
  submitStaffApplication,
  updateStaffApplicationDraft,
  type StaffApplication,
} from '../../services/applicationIntakeApi';
import type { LoanPurpose, LoanType } from '../../types';

interface NewApplicationProps {
  onBack: () => void;
  onNavigateTasks?: () => void;
}

type Step = 'member' | 'applicant' | 'shareholding' | 'loan' | 'nominee' | 'documents' | 'declarations' | 'review';

const STEPS: Array<{ id: Step; label: string; icon: React.ReactNode }> = [
  { id: 'member', label: 'Member', icon: <User size={15} /> },
  { id: 'applicant', label: 'Applicant', icon: <FileText size={15} /> },
  { id: 'shareholding', label: 'Shares', icon: <Shield size={15} /> },
  { id: 'loan', label: 'Loan', icon: <IndianRupee size={15} /> },
  { id: 'nominee', label: 'Nominee', icon: <Signature size={15} /> },
  { id: 'documents', label: 'Documents', icon: <Upload size={15} /> },
  { id: 'declarations', label: 'Declarations', icon: <FileCheck size={15} /> },
  { id: 'review', label: 'Review', icon: <Calculator size={15} /> },
];

const STEP_ORDER: Step[] = STEPS.map(step => step.id);

const REQUIRED_DOCUMENTS = [
  { id: 'borrowerPan', label: 'Borrower PAN', requiredFor: 'All borrowers', note: 'Self-attested PAN card copy' },
  { id: 'borrowerAadhaar', label: 'Borrower Aadhaar', requiredFor: 'Individual borrowers', note: 'Self-attested Aadhaar copy' },
  { id: 'nomineePan', label: 'Nominee PAN', requiredFor: 'All nominee applications', note: 'Self-attested nominee PAN copy' },
  { id: 'nomineeAadhaar', label: 'Nominee Aadhaar', requiredFor: 'All nominee applications', note: 'Self-attested nominee Aadhaar copy' },
  { id: 'shareCertificate', label: 'Share Certificate Copy', requiredFor: 'Physical shares', note: 'Copy required for security workflow' },
  { id: 'land712', label: '7/12 Extract / Land Record', requiredFor: 'Agriculture loans', note: 'Land evidence' },
  { id: 'cropPlan', label: 'Crop Plan', requiredFor: 'All agriculture loans', note: 'Crop, acreage, season and cycle' },
  { id: 'bankStatement', label: 'Six-Month Bank Statement', requiredFor: 'All borrowers', note: 'Latest six months, all pages' },
];

const fmt = (n: number) => '₹' + n.toLocaleString('en-IN');
const panPattern = /^[A-Z]{5}[0-9]{4}[A-Z]$/;

const formatKyc = (status: string) => {
  if (status === 'rekyc_due') return 'Re-KYC Due';
  if (status === 'verified') return 'Verified';
  if (status === 'pending') return 'Pending';
  return status;
};

const formatMemberType = (type: string) => {
  if (type === 'individual') return 'Individual';
  if (type === 'fpc') return 'FPC';
  if (type === 'producer_institution') return 'Producer Institution';
  return type;
};

const blankDocs = Object.fromEntries(REQUIRED_DOCUMENTS.map(doc => [doc.id, { uploaded: false, selfAttested: false }]));

interface MemberOption {
  id: string;
  name: string;
  folioNumber: string;
  memberType: string;
  mobile: string;
  email: string;
  address: string;
  pan: string;
  aadhaar: string;
  sharesHeld: number;
  shareMode: string;
  activeStatus: string;
  kycStatus: string;
  defaultStatus: string;
}

const toMemberOption = (member: MemberDirectoryItem): MemberOption => ({
  id: member.member_id,
  name: member.display_name || member.legal_name,
  folioNumber: member.folio_number,
  memberType: member.member_type,
  mobile: member.mobile_number ?? '',
  email: member.email ?? '',
  address: 'Member master address on file',
  pan: '',
  aadhaar: '',
  sharesHeld: member.share_summary.number_of_shares ?? 0,
  shareMode: member.share_summary.holding_mode ?? 'physical',
  activeStatus: member.membership_status,
  kycStatus: member.kyc_status,
  defaultStatus: member.default_status,
});

const NewApplication: React.FC<NewApplicationProps> = ({ onBack, onNavigateTasks }) => {
  const { can } = useRole();

  const [step, setStep] = useState<Step>('member');
  const [selectedMemberId, setSelectedMemberId] = useState('');
  const [memberSearch, setMemberSearch] = useState('');
  const [submittedApplication, setSubmittedApplication] = useState<StaffApplication | null>(null);
  const [draftSaved, setDraftSaved] = useState(false);
  const [draftApplicationId, setDraftApplicationId] = useState('');
  const [membersStatus, setMembersStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [membersMessage, setMembersMessage] = useState('');
  const [memberOptions, setMemberOptions] = useState<MemberOption[]>([]);
  const [submitMessage, setSubmitMessage] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [applicationForm, setApplicationForm] = useState({
    channel: 'Assisted Entry',
    applicantType: 'individual',
    borrowerName: '',
    memberId: '',
    folioNumber: '',
    contactNumber: '',
    email: '',
    address: '',
    pan: '',
    aadhaar: '',
    sharesHeld: 0,
    shareholdingMode: 'physical',
    dematBoId: '',
    valuationPerShare: 1200,
    landAreaAcres: 4.5,
    requestedAmount: 0,
    purpose: 'crop_production' as LoanPurpose,
    crop: '',
    season: '',
    expectedRepaymentDate: '',
    loanType: 'short_term' as LoanType,
    tenure: 12,
    subsidiaryRepayment: '',
    nomineeName: '',
    nomineeDob: '',
    nomineeAge: 0,
    nomineeGender: '',
    nomineeRelationship: '',
    nomineeMobile: '',
    nomineeAddress: '',
    nomineePan: '',
    nomineeAadhaar: '',
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
  const [documentState, setDocumentState] = useState<Record<string, { uploaded: boolean; selfAttested: boolean }>>(blankDocs);

  const selectedMember = memberOptions.find(m => m.id === selectedMemberId);

  useEffect(() => {
    let cancelled = false;
    setMembersStatus('loading');
    fetchMemberDirectory({ search: memberSearch, pageSize: 20 })
      .then(result => {
        if (cancelled) return;
        setMemberOptions(result.items.map(toMemberOption));
        setMembersStatus('success');
        setMembersMessage('');
      })
      .catch(error => {
        if (cancelled) return;
        setMemberOptions([]);
        setMembersStatus('error');
        setMembersMessage(error instanceof Error ? error.message : 'Unable to load members.');
      });
    return () => {
      cancelled = true;
    };
  }, [memberSearch]);

  const stepIndex = STEP_ORDER.indexOf(step);
  const shareholdingLimit = applicationForm.sharesHeld * applicationForm.valuationPerShare;
  const landBasedLimit = applicationForm.landAreaAcres * 20000;
  const maximumPermissibleLimit = Math.min(shareholdingLimit, landBasedLimit || shareholdingLimit);
  
  const applicableDocuments = REQUIRED_DOCUMENTS.filter(doc => {
    if (doc.id === 'borrowerAadhaar' && applicationForm.applicantType !== 'individual') return false;
    if (doc.id.startsWith('nominee') && applicationForm.applicantType !== 'individual') return false;
    if (doc.id === 'shareCertificate' && applicationForm.shareholdingMode !== 'physical') return false;
    return true;
  });
  
  const allDocsComplete = applicableDocuments.every(doc => documentState[doc.id]?.uploaded && documentState[doc.id]?.selfAttested);
  const allDeclarationsAccepted = Object.values(applicationForm.declarations).every(Boolean);

  const updateField = (field: string, value: string | number | boolean) => {
    setDraftSaved(false);
    setApplicationForm(prev => {
      const next = { ...prev, [field]: value };
      if (field === 'nomineeDob' && typeof value === 'string') {
        const birthDate = new Date(value);
        if (!isNaN(birthDate.getTime())) {
          const today = new Date();
          let age = today.getFullYear() - birthDate.getFullYear();
          const m = today.getMonth() - birthDate.getMonth();
          if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
            age--;
          }
          next.nomineeAge = age > 0 ? age : 0;
        }
      }
      return next;
    });
  };

  const updateDeclaration = (field: keyof typeof applicationForm.declarations, value: boolean) => {
    setDraftSaved(false);
    setApplicationForm(prev => ({
      ...prev,
      declarations: { ...prev.declarations, [field]: value },
    }));
  };

  const toggleDocument = (docId: string, field: 'uploaded' | 'selfAttested') => {
    setDraftSaved(false);
    setDocumentState(prev => ({
      ...prev,
      [docId]: { ...prev[docId], [field]: !prev[docId]?.[field] },
    }));
  };

  const hydrateFromMember = (member: MemberOption) => {
    setSelectedMemberId(member.id);
    setDraftSaved(false);
    setApplicationForm(prev => ({
      ...prev,
      applicantType: member.memberType,
      borrowerName: member.name,
      memberId: member.id,
      folioNumber: member.folioNumber,
      contactNumber: member.mobile,
      email: member.email,
      address: member.address,
      pan: member.pan,
      aadhaar: member.aadhaar.replace(/[^0-9]/g, '').slice(-4),
      sharesHeld: member.sharesHeld,
      shareholdingMode: member.shareMode,
      subsidiaryRepayment: '',
    }));
  };

  const persistDraft = async () => {
    if (!selectedMember) return null;
    setIsSaving(true);
    setSubmitMessage('');
    try {
      const payload = {
        member_id: selectedMember.id,
        required_loan_amount: applicationForm.requestedAmount || null,
        requested_tenure_months: applicationForm.tenure || null,
        declared_purpose: applicationForm.crop ? `${applicationForm.purpose}: ${applicationForm.crop}` : applicationForm.purpose,
        purpose_category: applicationForm.purpose,
        loan_type_requested: applicationForm.loanType,
        borrower_request_notes: applicationForm.season || '',
        terms_acceptance_flag: allDeclarationsAccepted,
      };
      const saved = draftApplicationId
        ? await updateStaffApplicationDraft(draftApplicationId, payload)
        : await createStaffApplicationDraft(payload);
      setDraftApplicationId(saved.loan_application_id);
      setDraftSaved(true);
      return saved;
    } catch (error) {
      setSubmitMessage(error instanceof Error ? error.message : 'Unable to save draft.');
      return null;
    } finally {
      setIsSaving(false);
    }
  };

  const handleSubmit = async () => {
    const saved = await persistDraft();
    if (!saved) return;
    setIsSaving(true);
    try {
      const submitted = await submitStaffApplication(saved.loan_application_id);
      setSubmittedApplication(submitted);
    } catch (error) {
      setSubmitMessage(error instanceof Error ? error.message : 'Unable to submit application.');
    } finally {
      setIsSaving(false);
    }
  };

  const validations: Record<Step, { ok: boolean; message: string }> = {
    member: {
      ok: Boolean(selectedMember && selectedMember.activeStatus === 'active' && selectedMember.defaultStatus === 'no_default' && selectedMember.kycStatus === 'verified'),
      message: 'Select an active, KYC-verified member with no current default.',
    },
    applicant: {
      ok: Boolean(applicationForm.borrowerName && applicationForm.memberId && applicationForm.folioNumber && applicationForm.address),
      message: 'Borrower name, member ID, folio and address are mandatory.',
    },
    shareholding: {
      ok: applicationForm.sharesHeld > 0 && Boolean(applicationForm.shareholdingMode) && (applicationForm.shareholdingMode !== 'demat' || applicationForm.dematBoId.length > 5),
      message: 'Shares held and shareholding mode are mandatory; Demat BO ID is required for demat shares.',
    },
    loan: {
      ok: applicationForm.requestedAmount > 0 && applicationForm.requestedAmount <= maximumPermissibleLimit && ['crop_production', 'agriculture_activity'].includes(applicationForm.purpose) && Boolean(applicationForm.crop && applicationForm.expectedRepaymentDate),
      message: 'Requested amount must be within the permissible limit and purpose must be crop/agriculture related.',
    },
    nominee: {
      ok: applicationForm.applicantType !== 'individual' || (Boolean(applicationForm.nomineeName && applicationForm.nomineeGender && applicationForm.nomineePan && applicationForm.nomineeAadhaar) && applicationForm.nomineeAge >= 18 && panPattern.test(applicationForm.nomineePan)),
      message: applicationForm.applicantType !== 'individual' ? '' : 'Nominee name, adult age, gender, PAN and Aadhaar last four digits are mandatory.',
    },
    documents: {
      ok: allDocsComplete,
      message: 'All mandatory documents must be uploaded and marked self-attested.',
    },
    declarations: {
      ok: allDeclarationsAccepted && applicationForm.borrowerSignature && applicationForm.nomineeSignature,
      message: 'All declarations plus borrower and nominee signatures are required.',
    },
    review: {
      ok: true,
      message: 'Review the application before submission.',
    },
  };

  const completenessItems = [
    ['Applicant is an eligible active member', validations.member.ok],
    ['Applicant identity and KYC fields complete', validations.applicant.ok],
    ['Shareholding and security inputs complete', validations.shareholding.ok],
    ['Requested amount and crop/agriculture purpose valid', validations.loan.ok],
    ['Nominee complete and not a minor', validations.nominee.ok],
    ['Mandatory documents uploaded and self-attested', validations.documents.ok],
    ['Borrower and nominee signatures captured', applicationForm.borrowerSignature && applicationForm.nomineeSignature],
    ['Declarations accepted', allDeclarationsAccepted],
  ];
  const canSubmit = completenessItems.every(([, ok]) => ok);

  const goNext = () => {
    if (stepIndex < STEP_ORDER.length - 1) setStep(STEP_ORDER[stepIndex + 1]);
  };

  const goPrev = () => {
    if (stepIndex > 0) setStep(STEP_ORDER[stepIndex - 1]);
    else onBack();
  };

  if (!can('create_application')) {
    return (
      <div className="p-6 max-w-2xl mx-auto">
        <div className="card text-center py-12">
          <div className="w-16 h-16 bg-amber-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <AlertTriangle size={32} className="text-amber-600" />
          </div>
          <h2 className="text-xl font-bold text-slate-900 mb-2">Access Denied</h2>
          <p className="text-slate-500 mb-6">You do not have permission to create loan applications.</p>
          <button onClick={onBack} className="btn-secondary">Back to Applications</button>
        </div>
      </div>
    );
  }

  if (submittedApplication) {
    return (
      <div className="p-6 max-w-2xl mx-auto">
        <div className="card text-center py-12">
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Check size={32} className="text-green-600" />
          </div>
          <h2 className="text-xl font-bold text-slate-900 mb-2">Application Submitted for Completeness Check</h2>
          <p className="text-slate-500 mb-1">Application ID {submittedApplication.loan_application_id.slice(0, 8)} created. Official LO reference will be generated after mandatory checklist verification.</p>
          <p className="text-xs text-slate-400 mb-6">Member: {applicationForm.borrowerName} · Amount: {fmt(applicationForm.requestedAmount)}</p>
          <div className="flex items-center justify-center gap-3 flex-wrap">
            <button onClick={onBack} className="btn-secondary">Back to Applications</button>
            {onNavigateTasks && (
              <button onClick={onNavigateTasks} className="btn-primary">View in Task Inbox</button>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-5xl mx-auto space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div className="flex items-start gap-3">
          <button onClick={goPrev} className="text-slate-500 hover:text-slate-700 mt-1">
            <ChevronLeft size={20} />
          </button>
          <div>
            <h1 className="text-xl font-bold text-slate-900">New Loan Application</h1>
            <p className="text-sm text-slate-500">Assisted entry workflow aligned to borrower portal intake.</p>
          </div>
        </div>
        <button onClick={persistDraft} disabled={isSaving || !selectedMember} className="btn-secondary flex items-center gap-2 self-start disabled:opacity-50 disabled:cursor-not-allowed">
          <Save size={16} />
          {draftSaved ? 'Draft Saved' : isSaving ? 'Saving…' : 'Save Draft'}
        </button>
      </div>

      <div className="card overflow-x-auto">
        <div className="flex min-w-max gap-2">
          {STEPS.map((s, idx) => {
            const isActive = s.id === step;
            const isDone = validations[s.id].ok && idx < stepIndex;
            return (
              <button
                key={s.id}
                onClick={() => setStep(s.id)}
                className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-semibold transition-colors ${
                  isActive ? 'bg-green-600 text-white' :
                  isDone ? 'bg-green-50 text-green-700' : 'bg-slate-50 text-slate-500'
                }`}
              >
                {isDone ? <CheckCircle2 size={15} /> : s.icon}
                {s.label}
              </button>
            );
          })}
        </div>
      </div>

      <div className="card space-y-5">
        {step === 'member' && (
          <>
            <div>
              <h2 className="text-lg font-semibold text-slate-900">Validate Member</h2>
              <p className="text-sm text-slate-500">Only active members with no unresolved default can proceed.</p>
            </div>
            <input
              type="text"
              placeholder="Search by member name, folio number or PAN"
              value={memberSearch}
              onChange={e => setMemberSearch(e.target.value)}
              className="field-input"
            />
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {membersStatus === 'loading' && (
                <div className="table-cell text-center text-slate-400 py-8">Loading members…</div>
              )}
              {membersStatus === 'error' && (
                <div className="table-cell text-center text-red-600 py-8">{membersMessage}</div>
              )}
              {membersStatus === 'success' && memberOptions.length === 0 && (
                <div className="table-cell text-center text-slate-400 py-8">No members found.</div>
              )}
              {memberOptions.map(member => {
                const blocked = member.activeStatus !== 'active' || member.defaultStatus !== 'no_default';
                return (
                  <label
                    key={member.id}
                    className={`flex items-start gap-3 p-3 rounded-lg border transition-colors ${
                      selectedMemberId === member.id ? 'border-green-500 bg-green-50' : 'border-slate-200 hover:border-slate-300'
                    } ${blocked ? 'opacity-60 cursor-not-allowed' : 'cursor-pointer'}`}
                  >
                    <input
                      type="radio"
                      name="member"
                      checked={selectedMemberId === member.id}
                      disabled={blocked}
                      onChange={() => !blocked && hydrateFromMember(member)}
                      className="mt-1"
                    />
                    <div className="flex-1 min-w-0">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="font-semibold text-slate-900">{member.name}</span>
                        <span className="text-xs text-slate-400">{member.folioNumber}</span>
                        <span className="text-xs bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded">{formatMemberType(member.memberType)}</span>
                        {member.activeStatus !== 'active' && <span className="text-xs bg-red-100 text-red-600 px-1.5 py-0.5 rounded">Inactive / Review</span>}
                        {member.defaultStatus !== 'no_default' && <span className="text-xs bg-red-100 text-red-600 px-1.5 py-0.5 rounded">Default on record</span>}
                      </div>
                      <div className="text-xs text-slate-500 mt-1">{member.address}</div>
                      <div className="flex flex-wrap gap-3 mt-1 text-xs text-slate-400">
                        <span>{member.sharesHeld} shares</span>
                        <span>KYC: {formatKyc(member.kycStatus)}</span>
                        <span>Exposure: —</span>
                      </div>
                    </div>
                  </label>
                );
              })}
            </div>
          </>
        )}

        {step === 'applicant' && (
          <>
            <div>
              <h2 className="text-lg font-semibold text-slate-900">Applicant Identification</h2>
              <p className="text-sm text-slate-500">Prefilled from member master; verify against KYC documents before continuing.</p>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Field label="Application Channel">
                <select value={applicationForm.channel} onChange={e => updateField('channel', e.target.value)} className="field-select">
                  <option>Assisted Entry</option>
                  <option>Digital Portal</option>
                  <option>Physical Submission</option>
                </select>
              </Field>
              <Field label="Applicant Type">
                <select value={applicationForm.applicantType} onChange={e => updateField('applicantType', e.target.value)} className="field-select">
                  <option value="individual">Individual Farmer</option>
                  <option value="fpc">FPC</option>
                  <option value="producer_institution">Producer Institution</option>
                </select>
              </Field>
              <TextField label="Borrower Name" value={applicationForm.borrowerName} onChange={v => updateField('borrowerName', v)} readOnly />
              <TextField label="Member ID" value={applicationForm.memberId} onChange={v => updateField('memberId', v)} readOnly />
              <TextField label="Folio Number" value={applicationForm.folioNumber} onChange={v => updateField('folioNumber', v)} readOnly />
              <TextField label="Contact Number" value={applicationForm.contactNumber} onChange={v => updateField('contactNumber', v)} readOnly />
              <TextField label="Email" value={applicationForm.email} onChange={v => updateField('email', v)} readOnly />
              <TextField label="PAN" value={applicationForm.pan} onChange={v => updateField('pan', v.toUpperCase())} readOnly />
              <TextField label="Aadhaar last four digits" value={applicationForm.aadhaar} onChange={v => updateField('aadhaar', v)} readOnly />
              <Field label="Registered Address" className="sm:col-span-2">
                <textarea value={applicationForm.address} onChange={e => updateField('address', e.target.value)} rows={3} className="field-input bg-slate-50 cursor-not-allowed text-slate-500 border-slate-200 resize-none" readOnly />
              </Field>
            </div>
          </>
        )}

        {step === 'shareholding' && (
          <>
            <div>
              <h2 className="text-lg font-semibold text-slate-900">Shareholding & Security Inputs</h2>
              <p className="text-sm text-slate-500">Capture shareholding mode and valuation before calculating permissible loan limits.</p>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <NumberField label="Number of Shares Held" value={applicationForm.sharesHeld} readOnly />
              <Field label="Shareholding Mode">
                <select value={applicationForm.shareholdingMode} onChange={e => updateField('shareholdingMode', e.target.value)} className="field-select">
                  <option value="physical">Physical</option>
                  <option value="demat">Demat</option>
                  <option value="mixed">Mixed</option>
                </select>
              </Field>
              <NumberField label="Latest Valuation per Share" value={applicationForm.valuationPerShare} readOnly />
              <NumberField label="Land Area Under Cultivation (acres)" value={applicationForm.landAreaAcres} onChange={v => updateField('landAreaAcres', v)} />
              {applicationForm.shareholdingMode === 'demat' && (
                <TextField label="Demat BO ID" value={applicationForm.dematBoId} onChange={v => updateField('dematBoId', v)} />
              )}
            </div>
            {applicationForm.sharesHeld === 0 && (
              <Warning>Enter shares held to calculate the shareholding limit.</Warning>
            )}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <LimitCard label="Shareholding Limit" value={applicationForm.sharesHeld === 0 ? 0 : shareholdingLimit} />
              <LimitCard label="Land-Based Limit" value={landBasedLimit} />
              <LimitCard label="Maximum Permissible Limit" value={applicationForm.sharesHeld === 0 ? 0 : maximumPermissibleLimit} />
            </div>
          </>
        )}

        {step === 'loan' && (
          <>
            <div>
              <h2 className="text-lg font-semibold text-slate-900">Requested Loan Details</h2>
              <p className="text-sm text-slate-500">Loan purpose must be crop production or agriculture activity.</p>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <NumberField label="Requested Loan Amount" value={applicationForm.requestedAmount} onChange={v => updateField('requestedAmount', v)} />
              <Field label="Loan Purpose">
                <select value={applicationForm.purpose} onChange={e => updateField('purpose', e.target.value)} className="field-select">
                  <option value="crop_production">Crop Production</option>
                  <option value="agriculture_activity">Agriculture Activity</option>
                </select>
              </Field>
              <TextField label="Crop" value={applicationForm.crop} onChange={v => updateField('crop', v)} />
              <TextField label="Season / Cycle" value={applicationForm.season} onChange={v => updateField('season', v)} />
              <Field label="Expected Repayment Date">
                <input type="date" value={applicationForm.expectedRepaymentDate} onChange={e => updateField('expectedRepaymentDate', e.target.value)} className="field-input" />
              </Field>
              <Field label="Loan Type Requested">
                <select value={applicationForm.loanType} onChange={e => updateField('loanType', e.target.value)} className="field-select">
                  <option value="short_term">Short-term</option>
                  <option value="long_term">Long-term</option>
                </select>
              </Field>
              <NumberField label="Tenure (months)" value={applicationForm.tenure} onChange={v => updateField('tenure', v)} />
              <Field label="Subsidiary Repayment Linkage">
                <select value={applicationForm.subsidiaryRepayment} onChange={e => updateField('subsidiaryRepayment', e.target.value)} className="field-select">
                  <option value="">None</option>
                  <option value="Sahyadri Farms Post Harvest Care Ltd.">Sahyadri Farms Post Harvest Care Ltd.</option>
                  <option value="Sahyadri Agro Retails">Sahyadri Agro Retails</option>
                </select>
              </Field>
            </div>
            {selectedMember && applicationForm.requestedAmount > 0 && (
              <LoanLimitCalculator
                sharesHeld={applicationForm.sharesHeld || selectedMember.sharesHeld}
                shareMode={selectedMember.shareMode as 'physical' | 'demat'}
                landAreaAcres={applicationForm.landAreaAcres}
                requestedAmount={applicationForm.requestedAmount}
              />
            )}
            {applicationForm.requestedAmount > maximumPermissibleLimit && (
              <Warning>{`Requested amount exceeds maximum permissible limit of ${fmt(maximumPermissibleLimit)}.`}</Warning>
            )}
          </>
        )}

        {step === 'nominee' && (
          <>
            <div>
              <h2 className="text-lg font-semibold text-slate-900">Nominee Details</h2>
              <p className="text-sm text-slate-500">Nominee name, adult age, gender, PAN and Aadhaar last four digits are mandatory.</p>
            </div>
            {applicationForm.applicantType !== 'individual' ? (
              <Warning>Authorised signatory flow gap: Nominee details are not applicable for institutional borrowers. Please proceed to the next step.</Warning>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <TextField label="Nominee Full Name" value={applicationForm.nomineeName} onChange={v => updateField('nomineeName', v)} />
                <Field label="Date of Birth">
                  <input type="date" value={applicationForm.nomineeDob} onChange={e => updateField('nomineeDob', e.target.value)} className="field-input" />
                </Field>
                <NumberField label="Age" value={applicationForm.nomineeAge} readOnly />
                <Field label="Gender">
                  <select value={applicationForm.nomineeGender} onChange={e => updateField('nomineeGender', e.target.value)} className="field-select">
                    <option value="">Select gender</option>
                    <option value="female">Female</option>
                    <option value="male">Male</option>
                    <option value="other">Other</option>
                  </select>
                </Field>
                <TextField label="Relationship to Borrower" value={applicationForm.nomineeRelationship} onChange={v => updateField('nomineeRelationship', v)} />
                <TextField label="Mobile Number" value={applicationForm.nomineeMobile} onChange={v => updateField('nomineeMobile', v)} />
                <TextField label="PAN" value={applicationForm.nomineePan} onChange={v => updateField('nomineePan', v.toUpperCase())} />
                <TextField label="Aadhaar last four digits" value={applicationForm.nomineeAadhaar} onChange={v => updateField('nomineeAadhaar', v)} />
                <Field label="Nominee Address" className="sm:col-span-2">
                  <textarea value={applicationForm.nomineeAddress} onChange={e => updateField('nomineeAddress', e.target.value)} rows={3} className="field-input resize-none" />
                </Field>
              </div>
            )}
          </>
        )}

        {step === 'documents' && (
          <>
            <div>
              <h2 className="text-lg font-semibold text-slate-900">Mandatory Documents</h2>
              <p className="text-sm text-slate-500">Upload and self-attestation checks mirror the borrower portal and completeness checklist.</p>
            </div>
            <div className="space-y-3">
              {applicableDocuments.map(doc => {
                const state = documentState[doc.id];
                return (
                  <div key={doc.id} className="border border-slate-200 rounded-lg p-4">
                    <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-3">
                      <div>
                        <div className="font-medium text-slate-900">{doc.label}</div>
                        <div className="text-xs text-slate-500 mt-1">{doc.requiredFor} · {doc.note}</div>
                      </div>
                      <div className="flex flex-wrap items-center gap-2">
                        <button onClick={() => toggleDocument(doc.id, 'uploaded')} className={`px-3 py-1.5 rounded-lg border text-xs font-semibold ${state.uploaded ? 'bg-green-50 border-green-200 text-green-700' : 'border-slate-200 text-slate-600'}`}>
                          {state.uploaded ? 'Uploaded' : 'Upload'}
                        </button>
                        <button onClick={() => toggleDocument(doc.id, 'selfAttested')} className={`px-3 py-1.5 rounded-lg border text-xs font-semibold ${state.selfAttested ? 'bg-green-50 border-green-200 text-green-700' : 'border-slate-200 text-slate-600'}`}>
                          {state.selfAttested ? 'Self-attested' : 'Mark self-attested'}
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </>
        )}

        {step === 'declarations' && (
          <>
            <div>
              <h2 className="text-lg font-semibold text-slate-900">Declarations & Signatures</h2>
              <p className="text-sm text-slate-500">Required before submission to Credit Assessment Team.</p>
            </div>
            <div className="space-y-3">
              {[
                ['agriculturePurpose', 'Loan purpose is related to crop production / agriculture activity.'],
                ['documentsTrue', 'Submitted documents are true, complete and self-attested.'],
                ['noDefault', 'Borrower is not in default with SFPCL, subsidiary or associate company.'],
                ['kycConsent', 'Borrower consents to KYC / CKYC checks and verification.'],
                ['sanctionTerms', 'Borrower agrees final terms will be governed by sanctioned Term Sheet and Loan Agreement.'],
              ].map(([field, label]) => (
                <label key={field} className="flex items-start gap-3 border border-slate-200 rounded-lg p-3 text-sm">
                  <input type="checkbox" checked={applicationForm.declarations[field as keyof typeof applicationForm.declarations]} onChange={e => updateDeclaration(field as keyof typeof applicationForm.declarations, e.target.checked)} className="mt-1" />
                  <span className="text-slate-700">{label}</span>
                </label>
              ))}
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <label className="flex items-start gap-3 border border-slate-200 rounded-lg p-3 text-sm">
                <input type="checkbox" checked={applicationForm.borrowerSignature} onChange={e => updateField('borrowerSignature', e.target.checked)} className="mt-1" />
                <span className="text-slate-700">Borrower signature captured</span>
              </label>
              <label className="flex items-start gap-3 border border-slate-200 rounded-lg p-3 text-sm">
                <input type="checkbox" checked={applicationForm.nomineeSignature} onChange={e => updateField('nomineeSignature', e.target.checked)} className="mt-1" />
                <span className="text-slate-700">Nominee signature captured</span>
              </label>
            </div>
          </>
        )}

        {step === 'review' && (
          <>
            <div>
              <h2 className="text-lg font-semibold text-slate-900">Review & Submit</h2>
              <p className="text-sm text-slate-500">Submission creates a draft application pending completeness check. It does not generate the official LO reference yet.</p>
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <div className="border border-slate-200 rounded-lg p-4">
                <h3 className="font-semibold text-slate-900 mb-3">Application Summary</h3>
                <SummaryRow label="Applicant" value={applicationForm.borrowerName || '—'} />
                <SummaryRow label="Folio / Shares" value={`${applicationForm.folioNumber || '—'} / ${applicationForm.sharesHeld || '—'}`} />
                <SummaryRow label="Requested Amount" value={applicationForm.requestedAmount ? fmt(applicationForm.requestedAmount) : '—'} />
                <SummaryRow label="Eligible Limit" value={maximumPermissibleLimit ? fmt(maximumPermissibleLimit) : '—'} />
                <SummaryRow label="Purpose" value={applicationForm.purpose.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')} />
                <SummaryRow label="Nominee" value={applicationForm.applicantType !== 'individual' ? 'Not Applicable' : `${applicationForm.nomineeName || '—'} · Age ${applicationForm.nomineeAge || '—'}`} />
              </div>
              <div className="border border-slate-200 rounded-lg p-4">
                <h3 className="font-semibold text-slate-900 mb-3">Completeness Checklist</h3>
                <div className="space-y-2">
                  {completenessItems.map(([label, ok]) => (
                    <div key={String(label)} className="flex items-center gap-2 text-sm">
                      {ok ? <CheckCircle2 size={15} className="text-green-600" /> : <AlertTriangle size={15} className="text-amber-600" />}
                      <span className={ok ? 'text-slate-700' : 'text-amber-700'}>{label}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </>
        )}

        {step !== 'review' && !validations[step].ok && (
          <Warning>{validations[step].message}</Warning>
        )}
      </div>

      {submitMessage && <Warning>{submitMessage}</Warning>}

      <div className="flex items-center justify-between">
        <button onClick={goPrev} className="btn-secondary flex items-center gap-2">
          <ChevronLeft size={16} />
          {stepIndex === 0 ? 'Cancel' : 'Back'}
        </button>
        {step === 'review' ? (
          <button onClick={handleSubmit} disabled={!canSubmit || isSaving} className="btn-primary flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed">
            <Save size={16} />
            {isSaving ? 'Submitting…' : 'Submit Application'}
          </button>
        ) : (
          <button onClick={goNext} disabled={!validations[step].ok} className="btn-primary flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed">
            Continue
            <ChevronRight size={16} />
          </button>
        )}
      </div>
    </div>
  );
};

const Field: React.FC<{ label: string; children: React.ReactNode; className?: string }> = ({ label, children, className = '' }) => (
  <div className={className}>
    <label className="field-label">{label}</label>
    {children}
  </div>
);

const TextField: React.FC<{ label: string; value: string; onChange?: (value: string) => void; readOnly?: boolean }> = ({ label, value, onChange, readOnly }) => (
  <Field label={label}>
    <input 
      value={value} 
      onChange={e => onChange?.(e.target.value)} 
      className={`field-input ${readOnly ? 'bg-slate-50 cursor-not-allowed text-slate-500 border-slate-200' : ''}`} 
      readOnly={readOnly}
    />
  </Field>
);

const NumberField: React.FC<{ label: string; value: number; onChange?: (value: number) => void; readOnly?: boolean }> = ({ label, value, onChange, readOnly }) => (
  <Field label={label}>
    <input 
      type="number" 
      value={value || ''} 
      onChange={e => onChange?.(Number(e.target.value))} 
      className={`field-input ${readOnly ? 'bg-slate-50 cursor-not-allowed text-slate-500 border-slate-200' : ''}`} 
      min={0}
      readOnly={readOnly}
    />
  </Field>
);

const LimitCard: React.FC<{ label: string; value: number }> = ({ label, value }) => (
  <div className="rounded-lg border border-green-100 bg-green-50 p-3">
    <div className="text-xs text-green-700">{label}</div>
    <div className="mt-1 text-lg font-bold text-green-900">{fmt(value)}</div>
  </div>
);

const SummaryRow: React.FC<{ label: string; value: string }> = ({ label, value }) => (
  <div className="grid grid-cols-[140px_1fr] gap-3 py-1 text-sm">
    <span className="text-slate-500">{label}</span>
    <span className="font-medium text-slate-900 break-words">{value}</span>
  </div>
);

const Warning: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div className="flex items-start gap-3 rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm text-amber-800">
    <AlertTriangle size={16} className="mt-0.5 flex-shrink-0" />
    <span>{children}</span>
  </div>
);

export default NewApplication;
