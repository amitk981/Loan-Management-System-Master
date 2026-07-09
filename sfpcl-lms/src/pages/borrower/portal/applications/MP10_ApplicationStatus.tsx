import React, { useEffect, useState } from 'react';
import { ArrowLeft, CheckCircle2, Clock, AlertTriangle, History, ClipboardList, Shield, UserRound, Signature, AlertCircle } from 'lucide-react';
import StatusBadge from '../../../../components/ui/StatusBadge';
import { AuthSessionError } from '../../../../services/authSession';
import { fetchPortalApplication, type PortalApplication } from '../../../../services/portalApi';

interface MP10_ApplicationStatusProps {
  applicationId: string | null;
  onBack: () => void;
}

const MP10_ApplicationStatus: React.FC<MP10_ApplicationStatusProps> = ({ applicationId, onBack }) => {
  const [activeTab, setActiveTab] = useState<'progress' | 'data'>('progress');
  const [application, setApplication] = useState<PortalApplication | null>(null);
  const [loading, setLoading] = useState(Boolean(applicationId));
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!applicationId) {
      setApplication(null);
      setLoading(false);
      return;
    }
    let mounted = true;
    setLoading(true);
    fetchPortalApplication(applicationId)
      .then(result => {
        if (!mounted) return;
        setApplication(result);
        setError(null);
      })
      .catch(err => {
        if (!mounted) return;
        setError(err instanceof AuthSessionError ? err.message : 'Application status could not be loaded.');
      })
      .finally(() => {
        if (mounted) setLoading(false);
      });
    return () => {
      mounted = false;
    };
  }, [applicationId]);

  const loanStages = buildStages(application);

  const applicationFieldSections = [
    {
      title: 'Borrower Details',
      icon: UserRound,
      rows: [
        ['Application Channel', 'Digital Portal'],
        ['Member ID', application?.member?.member_number ?? 'Not available'],
        ['Full Legal Name', application?.member?.display_name ?? 'Not available'],
        ['Folio Number', application?.member?.folio_number ?? 'Not available'],
        ['Member Type', application?.member?.member_type?.replace(/_/g, ' ') ?? 'Not available'],
      ],
    },
    {
      title: 'Membership & Eligibility',
      icon: Shield,
      rows: [
        ['Shares Held', String(application?.member?.share_summary?.number_of_shares ?? 'Not available')],
        ['Holding Mode', application?.member?.share_summary?.holding_mode ?? 'Not available'],
        ['KYC Status', application?.member?.kyc_status?.replace(/_/g, ' ') ?? 'Not available'],
        ['Default Flag', application?.member?.default_status?.replace(/_/g, ' ') ?? 'Not available'],
        ['Active Member Status', application?.member?.active_member_status?.status ?? 'Not available'],
      ],
    },
    {
      title: 'Loan Request',
      icon: ClipboardList,
      rows: [
        ['Required Loan Amount', formatCurrency(application?.required_loan_amount ?? null)],
        ['Application Reference', application?.application_reference_number ?? 'Pending completeness check'],
        ['Loan Purpose', application?.declared_purpose || application?.purpose_category?.replace(/_/g, ' ') || 'Not entered'],
        ['Loan Type', application?.loan_type_requested?.replace(/_/g, ' ') ?? 'Not entered'],
        ['Requested Tenure', application?.requested_tenure_months ? `${application.requested_tenure_months} months` : 'Not entered'],
      ],
    },
    {
      title: 'Nominee & Signatures',
      icon: Signature,
      rows: [
        ['Application Status', application?.application_status?.replace(/_/g, ' ') ?? 'Not available'],
        ['Current Stage', application?.current_stage?.replace(/_/g, ' ') ?? 'Not available'],
        ['Completeness Status', application?.completeness_status?.replace(/_/g, ' ') ?? 'Not available'],
        ['Open Deficiencies', String(application?.open_deficiency_count ?? 0)],
      ],
    },
  ];

  const validationMessages = buildValidationMessages(application);

  const auditSnapshot = application?.timeline ?? [];

  if (!applicationId) {
    return (
      <div className="bg-white rounded-xl border border-slate-100 p-6 text-sm text-slate-500">
        Select an application from My Applications to view status.
      </div>
    );
  }

  if (loading) {
    return (
      <div className="bg-white rounded-xl border border-slate-100 p-6 text-sm text-slate-500">
        Loading application status...
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-4">
        <button onClick={onBack} className="flex items-center gap-2 text-sm font-medium text-slate-600 hover:text-slate-900">
          <ArrowLeft size={16} />
          Back to applications
        </button>
        <div className="flex items-start gap-3 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-800">
          <AlertTriangle size={16} className="mt-0.5 flex-shrink-0" />
          {error}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <button onClick={onBack} className="p-2 hover:bg-slate-200 rounded-lg text-slate-500 transition-colors">
          <ArrowLeft size={18} />
        </button>
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-bold text-slate-900">Application {application?.display_reference ?? applicationId}</h2>
            <StatusBadge label={application?.application_status?.replace(/_/g, ' ') ?? 'pending'} size="sm" />
          </div>
          <p className="text-sm text-slate-500 mt-1">
            {application?.purpose_category?.replace(/_/g, ' ') || 'Loan Application'} • {formatCurrency(application?.required_loan_amount ?? null)} • {application?.submitted_at ? `Submitted ${formatDate(application.submitted_at)}` : 'Draft'}
          </p>
        </div>
      </div>

      <div className="flex border-b border-slate-200">
        <button
          onClick={() => setActiveTab('progress')}
          className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
            activeTab === 'progress' ? 'border-green-600 text-green-700' : 'border-transparent text-slate-500 hover:text-slate-700'
          }`}
        >
          Track Progress
        </button>
        <button
          onClick={() => setActiveTab('data')}
          className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
            activeTab === 'data' ? 'border-green-600 text-green-700' : 'border-transparent text-slate-500 hover:text-slate-700'
          }`}
        >
          Submitted Data & Deficiencies
        </button>
      </div>

      {activeTab === 'progress' && (
        <div className="bg-white rounded-xl border border-slate-100 p-6">
          <h3 className="font-semibold text-slate-900 mb-6">Application Journey</h3>
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
                  {stage.at && (
                    <div className="text-xs text-slate-400 mt-0.5">{formatDate(stage.at)}</div>
                  )}
                  <div className="text-xs text-slate-500 mt-1">Owner: {stage.owner}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'data' && (
        <div className="space-y-4">
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
                <div className="text-sm font-medium text-slate-700">Borrower action</div>
                <p className="mt-1 text-sm text-slate-500">
                  {application?.application_status === 'incomplete_returned'
                    ? 'Review the returned deficiencies. Upload and resubmission workflow will be available in the deficiency response slice.'
                    : 'No action is required from you right now.'}
                </p>
              </div>
            </div>

            <div className="bg-white rounded-xl border border-slate-100 p-5">
              <h3 className="font-semibold text-slate-900 mb-4 flex items-center gap-2">
                <History size={16} className="text-green-600" />
                Borrower-Visible Audit Snapshot
              </h3>
              <div className="space-y-3">
                {auditSnapshot.map(item => (
                  <div key={`${item.at}-${item.event}`} className="border-l-2 border-green-200 pl-3 py-1">
                    <div className="text-sm font-medium text-slate-900">{item.event}</div>
                    <div className="text-xs text-slate-500 mt-0.5">{item.at ? formatDate(item.at) : 'Date pending'} · {item.owner}</div>
                  </div>
                ))}
              </div>
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

        </div>
      )}

    </div>
  );
};

const buildStages = (application: PortalApplication | null) => {
  const status = application?.application_status;
  return [
    { label: 'Draft created', done: Boolean(application), at: application?.created_at ?? null, owner: 'Borrower' },
    { label: 'Application submitted', done: Boolean(application?.submitted_at), at: application?.submitted_at ?? null, owner: 'Borrower' },
    { label: 'Completeness Check', done: status === 'reference_generated', at: null, owner: 'SFPCL' },
    { label: 'Deficiency Raised', done: status === 'incomplete_returned', at: application?.updated_at ?? null, owner: 'SFPCL' },
    { label: 'Appraisal & Eligibility', done: application?.current_stage === 'credit_assessment', at: null, owner: 'Credit Manager' },
    { label: 'Sanction Approval', done: false, at: null, owner: 'Sanction Committee' },
    { label: 'Documentation', done: false, at: null, owner: 'Company Secretary' },
    { label: 'SAP Setup', done: false, at: null, owner: 'Senior Manager - Finance' },
    { label: 'Disbursement', done: false, at: null, owner: 'CFC' },
  ];
};

const buildValidationMessages = (application: PortalApplication | null) => {
  const messages = [
    { label: 'Member and folio details captured', status: application?.member ? 'passed' : 'attention' },
    { label: 'Loan purpose is agriculture / crop production related', status: application?.purpose_category ? 'passed' : 'attention' },
  ];
  if (application?.application_status === 'incomplete_returned') {
    return [
      ...messages,
      ...((application.deficiencies ?? []).map(item => ({
        label: item.description,
        status: 'attention',
      }))),
    ];
  }
  return [
    ...messages,
    { label: application?.borrower_action ?? 'No action required', status: 'passed' },
  ];
};

const formatCurrency = (value: string | null) => {
  if (!value) return 'Not entered';
  return `₹${Number(value).toLocaleString('en-IN')}`;
};

const formatDate = (value: string) => new Intl.DateTimeFormat('en-IN', {
  day: '2-digit',
  month: 'short',
  year: 'numeric',
}).format(new Date(value));

export default MP10_ApplicationStatus;
