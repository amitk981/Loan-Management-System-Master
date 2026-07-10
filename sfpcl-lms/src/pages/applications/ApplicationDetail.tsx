import React, { useEffect, useState } from 'react';
import { ChevronLeft, User, Users } from 'lucide-react';
import AlertBanner from '../../components/ui/AlertBanner';
import StageStepper from '../../components/ui/StageStepper';
import StatusBadge from '../../components/ui/StatusBadge';
import Tabs from '../../components/ui/Tabs';
import EligibilityChecklist from '../../components/loan/EligibilityChecklist';
import LoanLimitCalculator from '../../components/loan/LoanLimitCalculator';
import type {
  ApplicationDeficiency,
  ApplicationDocumentChecklistItem,
  StaffApplication,
} from '../../services/applicationIntakeApi';
import { submitStaffApplication } from '../../services/applicationIntakeApi';
import { isActionEnabled } from '../../shared/lib/availableActions';
import { loadApplicationDetail, type ApplicationDetailData } from './applicationDetailLoader';

const fmt = (value: string | null) => (
  value == null ? '—' : `₹${Number(value).toLocaleString('en-IN')}`
);

type LoadStatus = 'loading' | 'success' | 'error';

interface ApplicationDetailProps {
  applicationId: string;
  onBack: () => void;
  onNavigateMember: (memberId: string) => void;
  onNavigateAppraisal?: (applicationId: string) => void;
}

interface ApplicationDetailViewProps extends ApplicationDetailProps {
  status: LoadStatus;
  message: string;
  data: ApplicationDetailData | null;
  activeTab: number;
  onTabChange: (index: number) => void;
  onAction: (actionCode: string) => void;
}

const unavailablePanel = (title: string, message: string) => (
  <div className="card space-y-4">
    <h3 className="text-sm font-semibold text-slate-700">{title}</h3>
    <p className="text-sm text-slate-500">{message}</p>
  </div>
);

const factGrid = (facts: { label: string; value: string }[]) => (
  <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
    {facts.map(({ label, value }) => (
      <div key={label} className="bg-slate-50 rounded-lg p-3">
        <p className="text-xs text-slate-500 font-medium uppercase tracking-wide">{label}</p>
        <p className="text-sm font-semibold text-slate-900 mt-0.5 capitalize">{value}</p>
      </div>
    ))}
  </div>
);

const documentLabel = (value: string) => value.replace(/_/g, ' ');

const ChecklistRows: React.FC<{ items: ApplicationDocumentChecklistItem[] }> = ({ items }) => {
  if (items.length === 0) {
    return unavailablePanel(
      'Document Checklist',
      'No API-backed document checklist rows are available for this application.',
    );
  }
  return (
    <div className="card p-0 overflow-hidden">
      <div className="px-5 py-3 border-b border-slate-100">
        <h3 className="text-sm font-semibold text-slate-700">Document Checklist</h3>
      </div>
      <div className="divide-y divide-slate-100">
        {items.map((item, index) => (
          <div key={item.latest_application_document_id ?? `${item.document_type}-${index}`} className="px-5 py-4 flex items-center justify-between gap-4">
            <div>
              <p className="text-sm font-medium text-slate-800 capitalize">{documentLabel(item.document_type)}</p>
              <p className="text-xs text-slate-500 mt-0.5">
                {item.required_flag === 'optional' || item.required_flag === false ? 'Optional' : 'Required'}
              </p>
            </div>
            <StatusBadge
              label={item.complete ? 'verified' : item.verification_status || item.submission_status || 'not_started'}
              size="sm"
            />
          </div>
        ))}
      </div>
    </div>
  );
};

const DeficiencyRows: React.FC<{ items: ApplicationDeficiency[] }> = ({ items }) => {
  if (items.length === 0) return null;
  return (
    <div className="card p-0 overflow-hidden">
      <div className="px-5 py-3 bg-amber-50 border-b border-amber-200">
        <h3 className="text-sm font-semibold text-amber-800">Deficiency Communication Log</h3>
      </div>
      <div className="divide-y divide-slate-100">
        {items.map(item => (
          <div key={item.deficiency_id} className="px-5 py-4">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-sm font-medium text-slate-800 capitalize">{documentLabel(item.item_code)}</p>
                <p className="text-sm text-slate-600 mt-1">{item.description}</p>
              </div>
              <StatusBadge label={item.resolution_status} size="sm" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

const NomineePanel: React.FC<{ application: StaffApplication }> = ({ application }) => {
  const nominee = application.nominee;
  if (!nominee) {
    return unavailablePanel(
      'Nominee Details',
      'No API-backed nominee details are available for this application.',
    );
  }
  return (
    <div className="card space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-slate-800 flex items-center gap-2">
          <User size={16} className="text-green-600" /> Nominee Details
        </h3>
        <StatusBadge label={nominee.kyc_status} size="sm" />
      </div>
      {factGrid([
        { label: 'Nominee ID', value: nominee.nominee_id },
        { label: 'Full Name', value: nominee.nominee_name },
        { label: 'Age', value: nominee.age_at_application == null ? 'Not available' : String(nominee.age_at_application) },
        { label: 'Minor Status', value: nominee.minor_flag ? 'Minor' : 'Adult' },
        { label: 'Relationship to Borrower', value: nominee.relationship_to_borrower ?? 'Not available' },
        { label: 'KYC Status', value: documentLabel(nominee.kyc_status) },
        { label: 'Signature Required', value: nominee.signature_required_flag ? 'Required' : 'Not required' },
      ])}
    </div>
  );
};

const MemberPanel: React.FC<{
  application: StaffApplication;
  onNavigateMember: (memberId: string) => void;
}> = ({ application, onNavigateMember }) => (
  <div className="card space-y-4">
    <div className="flex items-start justify-between">
      <h3 className="text-sm font-semibold text-slate-700">Member Summary</h3>
      <button
        onClick={() => onNavigateMember(application.member.member_id)}
        className="text-xs text-green-600 hover:underline"
      >
        Full profile
      </button>
    </div>
    {factGrid([
      { label: 'Name', value: application.member.display_name },
      { label: 'Folio', value: application.member.folio_number },
      { label: 'Member Type', value: documentLabel(application.member.member_type) },
      { label: 'Membership Status', value: application.member.membership_status ? documentLabel(application.member.membership_status) : '—' },
      { label: 'KYC Status', value: application.member.kyc_status ? documentLabel(application.member.kyc_status) : '—' },
    ])}
  </div>
);

const RejectionNotePanel: React.FC<{ application: StaffApplication }> = ({ application }) => {
  const note = application.rejection_note;
  if (!note) return null;
  return (
    <div className="card space-y-3">
      <div className="flex items-center justify-between gap-3">
        <h3 className="text-sm font-semibold text-slate-800">Rejection Note</h3>
        <StatusBadge label={note.note_status} size="sm" />
      </div>
      {factGrid([
        { label: 'Stage', value: documentLabel(note.rejection_stage) },
        { label: 'Reason Category', value: documentLabel(note.rejection_reason_category) },
        { label: 'Communication', value: documentLabel(note.communication_mode) },
        { label: 'Reapply Allowed', value: note.reapply_allowed_flag ? 'Yes' : 'No' },
      ])}
    </div>
  );
};

export const ApplicationDetailView: React.FC<ApplicationDetailViewProps> = ({
  onBack,
  onNavigateMember,
  onNavigateAppraisal,
  status,
  message,
  data,
  activeTab,
  onTabChange,
  onAction,
}) => {
  if (status === 'loading') {
    return (
      <div className="p-6">
        <AlertBanner type="info" title="Loading application" message="Loading application details from the staff API." />
      </div>
    );
  }
  if (status === 'error') {
    return (
      <div className="p-6">
        <AlertBanner type="warning" title="Application unavailable" message={message || 'Unable to load application.'} />
      </div>
    );
  }
  if (!data) return null;

  const { application, checklistItems, deficiencies } = data;
  const reference = application.application_reference_number ?? application.loan_application_id.slice(0, 8);
  const steps = [
    { id: 's1', label: 'Submitted', state: 'not_started' as const },
    { id: 's2', label: 'Completeness', state: 'not_started' as const },
    { id: 's3', label: 'Appraisal', state: 'not_started' as const },
    { id: 's4', label: 'Sanction', state: 'not_started' as const },
    { id: 's5', label: 'Documentation', state: 'not_started' as const },
    { id: 's6', label: 'SAP Setup', state: 'not_started' as const },
    { id: 's7', label: 'Disbursement', state: 'not_started' as const },
  ];
  const pendingDocumentCount = checklistItems.filter(item => (
    item.required_flag !== 'optional' && item.required_flag !== false && !item.complete
  )).length;
  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'completeness', label: 'Completeness Check' },
    { id: 'applicant', label: 'Applicant & Member' },
    { id: 'nominee', label: 'Nominee' },
    { id: 'witness', label: 'Witness' },
    { id: 'eligibility', label: 'Eligibility & Limit' },
    { id: 'sanction', label: 'Sanction & Approvals' },
    { id: 'documents', label: 'Documents', badge: pendingDocumentCount || undefined },
    { id: 'security', label: 'Security' },
    { id: 'disbursement', label: 'Disbursement' },
    { id: 'audit', label: 'Audit Trail' },
  ];
  const availableActions = application.available_actions ?? [];

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-start gap-3">
        <button onClick={onBack} className="mt-1 text-slate-500 hover:text-slate-700">
          <ChevronLeft size={20} />
        </button>
        <div className="flex-1 flex items-start justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <h1 className="text-xl font-bold text-slate-900 num">{reference}</h1>
              <StatusBadge label={application.application_status} size="md" />
            </div>
            <div className="flex items-center gap-3 mt-0.5 text-sm text-slate-500 flex-wrap">
              <span>{application.member.display_name}</span>
              <span>·</span>
              <span className="num">{fmt(application.required_loan_amount)} requested</span>
              <span>·</span>
              <span>Applied {new Date(application.application_date).toLocaleDateString('en-IN')}</span>
            </div>
          </div>
          <div className="flex flex-col items-end gap-1 text-sm text-slate-500">
            <span>Owner: <span className="font-medium text-slate-900">{application.assigned_owner?.full_name ?? '—'}</span></span>
            {availableActions.length > 0 && (
              <div className="flex gap-2 mt-2">
                {availableActions.map(action => (
                  <div key={action.action_code} className="flex flex-col items-end gap-1">
                    <button
                      className="btn-secondary text-xs disabled:opacity-50 disabled:cursor-not-allowed"
                      disabled={!isActionEnabled(availableActions, action.action_code)}
                      title={action.disabled_reason ?? undefined}
                      onClick={() => onAction(action.action_code)}
                    >
                      {action.label}
                    </button>
                    {action.disabled_reason && (
                      <span className="text-xs text-slate-500 max-w-xs text-right">{action.disabled_reason}</span>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="card py-5">
        <div className="px-5 pb-4 flex items-center justify-between gap-3">
          <span className="text-xs text-slate-500">Stage history unavailable</span>
          <span className="text-xs text-slate-500">
            Current backend stage: <span className="font-medium text-slate-900">{documentLabel(application.current_stage)}</span>
          </span>
        </div>
        <StageStepper steps={steps} />
      </div>

      <Tabs tabs={tabs} activeIndex={activeTab} onChange={onTabChange}>
        <div className="space-y-4">
          <div className="card space-y-5">
            {factGrid([
              { label: 'Requested Amount', value: fmt(application.required_loan_amount) },
              { label: 'Loan Type', value: application.loan_type_requested ? documentLabel(application.loan_type_requested) : '—' },
              { label: 'Tenure', value: application.requested_tenure_months == null ? '—' : `${application.requested_tenure_months} months` },
              { label: 'Purpose', value: application.purpose_category ? documentLabel(application.purpose_category) : '—' },
            ])}
          </div>
          <DeficiencyRows items={deficiencies} />
          <RejectionNotePanel application={application} />
        </div>
        <div className="space-y-4">
          <ChecklistRows items={checklistItems} />
          <DeficiencyRows items={deficiencies} />
        </div>
        <MemberPanel application={application} onNavigateMember={onNavigateMember} />
        <NomineePanel application={application} />
        <div className="card space-y-4">
          <h3 className="font-semibold text-slate-800 flex items-center gap-2">
            <Users size={16} className="text-blue-600" /> Witness Details
          </h3>
          <p className="text-sm text-slate-500">No API-backed witness details are available for this application yet.</p>
        </div>
        <div className="space-y-4">
          {data.eligibility ? <div className="card"><EligibilityChecklist assessment={data.eligibility} /></div> : unavailablePanel('Eligibility Assessment', 'No stored eligibility assessment is available.')}
          {data.loanLimit ? <div className="card"><LoanLimitCalculator assessment={data.loanLimit} /></div> : unavailablePanel('Loan Limit', 'No stored loan-limit assessment is available.')}
          <div className="card flex items-center justify-between gap-3">
            <div><h3 className="text-sm font-semibold text-slate-700">Appraisal</h3><p className="text-sm text-slate-500 mt-1">{data.appraisal ? `Stored status: ${documentLabel(data.appraisal.appraisal_status)}` : 'No stored appraisal note is available.'}</p></div>
            {onNavigateAppraisal && <button className="btn-secondary text-sm" onClick={() => onNavigateAppraisal(application.loan_application_id)}>Open Appraisal Workbench</button>}
          </div>
        </div>
        {unavailablePanel('Sanction & Approvals', 'No backend sanction or approval facts are available in this detail response.')}
        <ChecklistRows items={checklistItems} />
        {unavailablePanel('Security Instruments', 'No backend security facts are available in this detail response.')}
        {unavailablePanel('Disbursement Authorisation', 'No backend disbursement facts are available for this application.')}
        {unavailablePanel('Application Audit Trail', 'No backend audit events are available in this detail response.')}
      </Tabs>
    </div>
  );
};

const ApplicationDetail: React.FC<ApplicationDetailProps> = props => {
  const [status, setStatus] = useState<LoadStatus>('loading');
  const [message, setMessage] = useState('');
  const [data, setData] = useState<ApplicationDetailData | null>(null);
  const [activeTab, setActiveTab] = useState(0);

  const refresh = async () => {
    const result = await loadApplicationDetail(props.applicationId);
    setData(result);
    setStatus('success');
  };

  const handleAction = async (actionCode: string) => {
    if (actionCode !== 'submit') return;
    setStatus('loading');
    setMessage('');
    try {
      await submitStaffApplication(props.applicationId);
      await refresh();
    } catch (error) {
      setData(null);
      setMessage(error instanceof Error ? error.message : 'Unable to complete application action.');
      setStatus('error');
    }
  };

  useEffect(() => {
    let cancelled = false;
    setStatus('loading');
    setMessage('');
    setData(null);
    setActiveTab(0);
    loadApplicationDetail(props.applicationId)
      .then(result => {
        if (cancelled) return;
        setData(result);
        setStatus('success');
      })
      .catch(error => {
        if (cancelled) return;
        setMessage(error instanceof Error ? error.message : 'Unable to load application.');
        setStatus('error');
      });
    return () => {
      cancelled = true;
    };
  }, [props.applicationId]);

  return (
    <ApplicationDetailView
      {...props}
      status={status}
      message={message}
      data={data}
      activeTab={activeTab}
      onTabChange={setActiveTab}
      onAction={handleAction}
    />
  );
};

export default ApplicationDetail;
