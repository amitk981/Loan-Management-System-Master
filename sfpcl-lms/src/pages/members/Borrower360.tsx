import React, { useEffect, useState } from 'react';
import {
  AlertTriangle,
  Banknote,
  Building2,
  ChevronLeft,
  Clock,
  CreditCard,
  Eye,
  EyeOff,
  FileText,
  History,
  Lock,
  MapPin,
  MessageSquare,
  Shield,
  User,
} from 'lucide-react';
import AlertBanner from '../../components/ui/AlertBanner';
import StatusBadge from '../../components/ui/StatusBadge';
import Tabs from '../../components/ui/Tabs';
import { AuthSessionError } from '../../services/authSession';
import {
  fetchMemberBankAccounts,
  fetchMemberCancelledCheques,
  fetchMemberCropPlans,
  fetchMemberKycProfile,
  fetchMemberLandHoldings,
  fetchMemberNominees,
  fetchMemberProfile,
  fetchMemberShareholdings,
  revealMemberSensitiveField,
  type KycProfileDetail,
  type MemberBankAccountDetail,
  type MemberCancelledChequeDetail,
  type MemberCropPlanDetail,
  type MemberLandHoldingDetail,
  type MemberNomineeDetail,
  type MemberProfileDetail,
  type MemberShareholdingDetail,
} from '../../services/memberProfileApi';

type Borrower360Status = 'loading' | 'success' | 'empty' | 'unauthorized' | 'forbidden' | 'error';

interface Borrower360Props {
  memberId: string;
  onBack: () => void;
  onOpenApplication?: (id: string) => void;
  onOpenLoanAccount?: (id: string) => void;
}

const Borrower360: React.FC<Borrower360Props> = ({ memberId, onBack, onOpenApplication, onOpenLoanAccount }) => {
  const [status, setStatus] = useState<Borrower360Status>('loading');
  const [message, setMessage] = useState('');
  const [profile, setProfile] = useState<MemberProfileDetail | null>(null);
  const [shareholdings, setShareholdings] = useState<MemberShareholdingDetail[]>([]);
  const [landHoldings, setLandHoldings] = useState<MemberLandHoldingDetail[]>([]);
  const [cropPlans, setCropPlans] = useState<MemberCropPlanDetail[]>([]);
  const [nominees, setNominees] = useState<MemberNomineeDetail[]>([]);
  const [kycProfile, setKycProfile] = useState<KycProfileDetail | null>(null);
  const [bankAccounts, setBankAccounts] = useState<MemberBankAccountDetail[]>([]);
  const [cancelledCheques, setCancelledCheques] = useState<MemberCancelledChequeDetail[]>([]);
  const [dataWarnings, setDataWarnings] = useState<string[]>([]);

  useEffect(() => {
    let cancelled = false;
    setStatus('loading');
    setMessage('');
    setProfile(null);
    setShareholdings([]);
    setLandHoldings([]);
    setCropPlans([]);
    setNominees([]);
    setKycProfile(null);
    setBankAccounts([]);
    setCancelledCheques([]);
    setDataWarnings([]);

    fetchMemberProfile(memberId)
      .then(async profileResult => {
        const [
          shareholdingResult,
          landResult,
          cropResult,
          nomineeResult,
          kycResult,
          bankResult,
          chequeResult,
        ] = await Promise.allSettled([
          fetchMemberShareholdings(memberId),
          fetchMemberLandHoldings(memberId),
          fetchMemberCropPlans(memberId),
          fetchMemberNominees(memberId),
          fetchMemberKycProfile(memberId),
          fetchMemberBankAccounts(memberId),
          fetchMemberCancelledCheques(memberId),
        ]);
        if (cancelled) return;
        setProfile(profileResult);
        setShareholdings(itemsFrom(shareholdingResult));
        setLandHoldings(itemsFrom(landResult));
        setCropPlans(itemsFrom(cropResult));
        setNominees(itemsFrom(nomineeResult));
        setKycProfile(valueFrom(kycResult));
        setBankAccounts(itemsFrom(bankResult));
        setCancelledCheques(itemsFrom(chequeResult));
        setDataWarnings([
          warningFrom(shareholdingResult, 'Shareholding records could not be loaded.'),
          warningFrom(landResult, 'Land records could not be loaded.'),
          warningFrom(cropResult, 'Crop records could not be loaded.'),
          warningFrom(nomineeResult, 'Nominee records could not be loaded.'),
          warningFrom(kycResult, 'KYC records could not be loaded.'),
          warningFrom(bankResult, 'Bank account records could not be loaded.'),
          warningFrom(chequeResult, 'Cancelled cheque records could not be loaded.'),
        ].filter(Boolean) as string[]);
        setStatus('success');
      })
      .catch(error => {
        if (cancelled) return;
        const next = errorState(error);
        setStatus(next.status);
        setMessage(next.message);
      });

    return () => {
      cancelled = true;
    };
  }, [memberId]);

  return (
    <Borrower360View
      status={status}
      message={message}
      profile={profile}
      shareholdings={shareholdings}
      landHoldings={landHoldings}
      cropPlans={cropPlans}
      nominees={nominees}
      kycProfile={kycProfile}
      bankAccounts={bankAccounts}
      cancelledCheques={cancelledCheques}
      dataWarnings={dataWarnings}
      onBack={onBack}
      onOpenApplication={onOpenApplication}
      onOpenLoanAccount={onOpenLoanAccount}
    />
  );
};

interface Borrower360ViewProps {
  status: Borrower360Status;
  message?: string;
  profile: MemberProfileDetail | null;
  shareholdings?: MemberShareholdingDetail[];
  landHoldings?: MemberLandHoldingDetail[];
  cropPlans?: MemberCropPlanDetail[];
  nominees?: MemberNomineeDetail[];
  kycProfile?: KycProfileDetail | null;
  bankAccounts?: MemberBankAccountDetail[];
  cancelledCheques?: MemberCancelledChequeDetail[];
  dataWarnings?: string[];
  activeTabIndex?: number;
  onBack: () => void;
  onOpenApplication?: (id: string) => void;
  onOpenLoanAccount?: (id: string) => void;
}

export const Borrower360View: React.FC<Borrower360ViewProps> = ({
  status,
  message = '',
  profile,
  shareholdings = [],
  landHoldings = [],
  cropPlans = [],
  nominees = [],
  kycProfile = null,
  bankAccounts = [],
  cancelledCheques = [],
  dataWarnings = [],
  activeTabIndex = 0,
  onBack,
}) => {
  const [activeTab, setActiveTab] = useState(activeTabIndex);

  if (status !== 'success' || !profile) {
    return <BorrowerState status={status} message={message} onBack={onBack} />;
  }

  const isInstitution = profile.member_type === 'fpc' || profile.member_type === 'producer_institution';
  const tabs = [
    { id: 'summary', label: 'Member Summary' },
    { id: 'kyc', label: 'KYC & Documents', badge: kycProfile?.documents.length || undefined },
    { id: 'security', label: 'Bank & Security', badge: bankAccounts.length || undefined },
    { id: 'nominee', label: 'Nominee', badge: nominees.length || undefined },
    { id: 'supply', label: 'Produce Supply', badge: profile.produce_supply_records?.length || undefined },
    { id: 'applications', label: 'Applications' },
    { id: 'loans', label: 'Loan Accounts' },
    { id: 'repayments', label: 'Repayment History' },
    { id: 'comms', label: 'Communications' },
    { id: 'risk', label: 'Risk & Exceptions' },
    { id: 'audit', label: 'Audit Trail' },
  ];

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-start gap-3">
        <button onClick={onBack} className="mt-1 text-slate-500 hover:text-slate-700 flex-shrink-0">
          <ChevronLeft size={20} />
        </button>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-3 flex-wrap">
            <div className={`w-12 h-12 rounded-full flex items-center justify-center flex-shrink-0 ${isInstitution ? 'bg-blue-100' : 'bg-green-100'}`}>
              {isInstitution ? <Building2 size={22} className="text-blue-700" /> : <User size={22} className="text-green-700" />}
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <h1 className="text-xl font-bold text-slate-900">{profile.display_name || profile.legal_name}</h1>
                <span className="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded font-medium">Member 360</span>
                {isInstitution && <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full font-semibold">{memberTypeLabel(profile.member_type)}</span>}
                <StatusBadge label={activeStatusLabel(profile)} size="sm" />
                <StatusBadge label={profile.kyc_status === 'verified' ? 'KYC verified' : profile.kyc_status} family={profile.kyc_status === 'verified' ? 'approved' : undefined} size="sm" />
                {profile.default_status !== 'no_default' && <StatusBadge label={profile.default_status} size="sm" />}
              </div>
              <p className="text-sm text-slate-500 mt-0.5">
                Folio: <span className="font-semibold text-slate-900 num">{profile.folio_number}</span>
                {' · '}{memberTypeLabel(profile.member_type)}
                {profile.member_number && <> · Member: <span className="font-semibold text-slate-900">{profile.member_number}</span></>}
                {' · '}Shares: {formatCount(profile.share_summary.number_of_shares)} ({profile.share_summary.holding_mode || 'unknown'})
              </p>
            </div>
          </div>
        </div>
        <div className="hidden lg:flex items-center gap-4 flex-shrink-0">
          <HeaderMetric label="KYC / Re-KYC" value={profile.kyc_status === 'rekyc_due' ? 'Re-KYC Due' : titleCase(profile.kyc_status)} />
          <HeaderMetric label="Available Shares" value={formatCount(profile.share_summary.available_share_count)} />
          <HeaderMetric label="Bank Records" value={String(bankAccounts.length)} />
        </div>
      </div>

      {profile.kyc_status === 'rekyc_due' && (
        <AlertBanner type="warning" title="Re-KYC Required" message="KYC renewal is due. Later lending slices own application, sanction, and disbursement blockers." />
      )}
      {profile.default_status !== 'no_default' && (
        <AlertBanner type="error" title="Default Status Requires Review" message="Default and recovery decisions are shown only when backend loan-account APIs exist." />
      )}
      {dataWarnings.map(warning => (
        <AlertBanner key={warning} type="warning" title="Partial borrower data" message={warning} />
      ))}

      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-3">
        <Chip label="Active Status" value={activeStatusLabel(profile).replace(/_/g, ' ')} />
        <Chip label="KYC / Re-KYC" value={profile.kyc_status === 'rekyc_due' ? 'Re-KYC Due' : titleCase(profile.kyc_status)} />
        <Chip label="Shareholding" value={`${formatCount(profile.share_summary.number_of_shares)} ${profile.share_summary.holding_mode || ''}`} />
        <Chip label="Land Records" value={String(landHoldings.length)} />
        <Chip label="Crop Plans" value={String(cropPlans.length)} />
        <Chip label="Bank Metadata" value={String(bankAccounts.length + cancelledCheques.length)} />
      </div>

      <Tabs tabs={tabs} activeIndex={activeTab} onChange={setActiveTab}>
        <SummaryTab profile={profile} shareholdings={shareholdings} landHoldings={landHoldings} cropPlans={cropPlans} />
        <KycPanel profile={profile} kycProfile={kycProfile} />
        <BankSecurityTab bankAccounts={bankAccounts} cancelledCheques={cancelledCheques} shareholdings={shareholdings} />
        <NomineePanel nominees={nominees} />
        <BorrowerSupplyPanel records={profile.produce_supply_records ?? []} />
        <DeferredTab title="Applications" message="No loan application records are available from the backend yet." />
        <DeferredTab title="Loan Accounts" message="No loan records are available from the backend yet." />
        <DeferredTab title="Repayment History" message="No repayment records are available from the backend yet." />
        <DeferredTab title="Communications" message="No communication records are available from the backend yet." />
        <DeferredTab title="Risk & Exceptions" message="No source-backed risk or exception records are available from the backend yet." />
        <DeferredTab title="Audit Trail" message="No audit trail records are available from the backend yet." />
      </Tabs>
    </div>
  );
};

const SummaryTab: React.FC<{
  profile: MemberProfileDetail;
  shareholdings: MemberShareholdingDetail[];
  landHoldings: MemberLandHoldingDetail[];
  cropPlans: MemberCropPlanDetail[];
}> = ({ profile, shareholdings, landHoldings, cropPlans }) => (
  <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
    <div className="card space-y-4">
      <h3 className="font-semibold text-slate-800">Member Profile</h3>
      <div className="grid grid-cols-2 gap-3">
        <InfoTile label="Member ID" value={profile.member_id.toUpperCase()} />
        <InfoTile label="Member Number" value={profile.member_number || '-'} />
        <InfoTile label="Folio Number" value={profile.folio_number} />
        <InfoTile label="Member Type" value={memberTypeLabel(profile.member_type)} />
        <InfoTile label="Registered On" value={formatDate(profile.membership_start_date)} />
        <InfoTile label="Default Status" value={profile.default_status.replace(/_/g, ' ')} />
        <InfoTile label="Mobile" value={profile.mobile_number || '-'} />
        <InfoTile label="Email" value={profile.email || '-'} />
      </div>
      <div>
        <p className="text-xs text-slate-500 font-medium uppercase tracking-wide mb-1 flex items-center gap-1"><MapPin size={12} /> Address</p>
        <p className="text-sm text-slate-800">{addressText(profile)}</p>
      </div>
      <IdentityPanel profile={profile} />
    </div>
    <div className="card space-y-4">
      <h3 className="font-semibold text-slate-800">Membership Evidence</h3>
      <div className="grid grid-cols-2 gap-3">
        <InfoTile label="Total Shares" value={formatCount(profile.share_summary.number_of_shares)} />
        <InfoTile label="Available Shares" value={formatCount(profile.share_summary.available_share_count)} />
        <InfoTile label="Holding Mode" value={profile.share_summary.holding_mode || '-'} />
        <InfoTile label="Land Records" value={String(landHoldings.length)} />
      </div>
      <RecordList
        title="Shareholding Records"
        empty="No shareholding records are available from the backend yet."
        items={shareholdings.map(item => ({
          id: item.shareholding_id,
          title: item.folio_number,
          subtitle: `${titleCase(item.holding_mode)} · ${formatCount(item.available_share_count)} available`,
          status: item.status,
        }))}
      />
      <RecordList
        title="Land & Crop Evidence"
        empty="No land or crop records are available from the backend yet."
        items={[
          ...landHoldings.map(item => ({
            id: item.land_holding_id,
            title: item.survey_number || 'Survey number not recorded',
            subtitle: `${item.area_acres} acres · ${item.village || '-'} · ${item.document_type}`,
            status: item.verification_status,
          })),
          ...cropPlans.map(item => ({
            id: item.crop_plan_id,
            title: item.crop_type,
            subtitle: `${item.planned_area_acres} acres · ${item.season || 'Season not recorded'} · ${item.estimated_cost_amount || '-'}`,
            status: item.verification_status,
          })),
        ]}
      />
    </div>
  </div>
);

const BorrowerSupplyPanel: React.FC<{ records: NonNullable<MemberProfileDetail['produce_supply_records']> }> = ({ records }) => (
  <div className="bg-white rounded-xl border border-slate-100 p-5">
    <h3 className="font-semibold text-slate-900 mb-3">Produce Supply History</h3>
    {records.length ? <div className="space-y-2">{records.map(record => <div key={record.produce_supply_record_id} className="flex items-center justify-between border-b border-slate-50 pb-2"><span className="text-sm font-medium">{record.financial_year} · {record.crop_type || 'Crop not recorded'}</span><StatusBadge label={record.verified_flag ? 'verified' : 'pending'} size="sm" /></div>)}</div> : <p className="text-sm text-slate-500">No produce supply records are available.</p>}
  </div>
);

const IdentityPanel: React.FC<{ profile: MemberProfileDetail }> = ({ profile }) => {
  const [revealed, setRevealed] = useState<Record<string, { value: string; expiresAt: string }>>({});
  const [reasons, setReasons] = useState<Record<string, string>>({});
  const [messages, setMessages] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState<Record<string, boolean>>({});

  const handleReveal = async (fieldName: 'pan' | 'aadhaar') => {
    const reason = (reasons[fieldName] || '').trim();
    if (!reason) {
      setMessages(current => ({ ...current, [fieldName]: 'Reason is required before reveal.' }));
      return;
    }
    setSubmitting(current => ({ ...current, [fieldName]: true }));
    setMessages(current => ({ ...current, [fieldName]: '' }));
    try {
      const result = await revealMemberSensitiveField(profile.member_id, { field_name: fieldName, reason });
      setRevealed(current => ({ ...current, [fieldName]: { value: result.value, expiresAt: result.expires_at } }));
      setReasons(current => ({ ...current, [fieldName]: '' }));
      setMessages(current => ({ ...current, [fieldName]: `Temporary access expires at ${formatDateTime(result.expires_at)}.` }));
    } catch (error) {
      setMessages(current => ({ ...current, [fieldName]: error instanceof Error ? error.message : 'Sensitive value could not be revealed.' }));
    } finally {
      setSubmitting(current => ({ ...current, [fieldName]: false }));
    }
  };

  const hideReveal = (fieldName: 'pan' | 'aadhaar') => {
    setRevealed(current => {
      const next = { ...current };
      delete next[fieldName];
      return next;
    });
  };

  return (
    <div className="border-t border-slate-100 pt-4">
      <p className="text-xs text-slate-500 font-semibold uppercase tracking-wide mb-3 flex items-center gap-1"><Lock size={12} /> Sensitive Identifiers - Masked</p>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <SensitiveTile
          label="PAN"
          value={revealed.pan?.value || profile.pan.masked}
          canReveal={profile.pan.can_view_full}
          revealed={Boolean(revealed.pan)}
          reason={reasons.pan || ''}
          message={messages.pan || ''}
          submitting={Boolean(submitting.pan)}
          onReasonChange={value => setReasons(current => ({ ...current, pan: value }))}
          onReveal={() => handleReveal('pan')}
          onHide={() => hideReveal('pan')}
        />
        <SensitiveTile
          label="Aadhaar"
          value={revealed.aadhaar?.value || profile.aadhaar.masked}
          canReveal={profile.aadhaar.can_view_full}
          revealed={Boolean(revealed.aadhaar)}
          reason={reasons.aadhaar || ''}
          message={messages.aadhaar || ''}
          submitting={Boolean(submitting.aadhaar)}
          onReasonChange={value => setReasons(current => ({ ...current, aadhaar: value }))}
          onReveal={() => handleReveal('aadhaar')}
          onHide={() => hideReveal('aadhaar')}
        />
      </div>
    </div>
  );
};

const KycPanel: React.FC<{ profile: MemberProfileDetail; kycProfile: KycProfileDetail | null }> = ({ profile, kycProfile }) => (
  <div className="card space-y-5">
    <div className="flex items-center justify-between gap-3">
      <h3 className="font-semibold text-slate-800">KYC Verification</h3>
      <StatusBadge label={kycProfile?.kyc_status || profile.kyc_status || 'pending'} family={(kycProfile?.kyc_status || profile.kyc_status) === 'verified' ? 'approved' : undefined} />
    </div>
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <SensitiveTile label="PAN" value={profile.pan.masked} />
      <SensitiveTile label="Aadhaar" value={profile.aadhaar.masked} />
    </div>
    {!kycProfile ? (
      <EmptyPanel icon={<Shield size={18} className="text-slate-500 flex-shrink-0" />} title="No KYC profile is available from the backend yet." />
    ) : (
      <div className="space-y-4">
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <InfoTile label="CKYC Consent" value={kycProfile.ckyc_consent_flag ? 'Yes' : 'No'} />
          <InfoTile label="Beneficial Ownership" value={kycProfile.beneficial_ownership_verified_flag === null ? '-' : kycProfile.beneficial_ownership_verified_flag ? 'Yes' : 'No'} />
          <InfoTile label="Risk Rating" value={titleCase(kycProfile.risk_rating || '-')} />
          <InfoTile label="Re-KYC Due" value={formatDate(kycProfile.rekyc_due_date)} />
        </div>
        <RecordList
          title="KYC Documents"
          empty="No KYC document records are available from the backend yet."
          items={kycProfile.documents.map(document => ({
            id: document.kyc_document_id,
            title: document.file_name || document.document_type,
            subtitle: `${titleCase(document.document_type)} · ${document.self_attested_flag ? 'Self Attested' : 'Not self attested'} · ${titleCase(document.sensitivity_level)}`,
            status: document.verification_status,
          }))}
        />
      </div>
    )}
  </div>
);

const BankSecurityTab: React.FC<{
  bankAccounts: MemberBankAccountDetail[];
  cancelledCheques: MemberCancelledChequeDetail[];
  shareholdings: MemberShareholdingDetail[];
}> = ({ bankAccounts, cancelledCheques, shareholdings }) => (
  <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
    <div className="card space-y-4">
      <h3 className="font-semibold text-slate-800 flex items-center gap-2"><CreditCard size={16} className="text-green-600" /> Bank Account Metadata</h3>
      {bankAccounts.length === 0 ? (
        <EmptyPanel icon={<Banknote size={18} className="text-slate-500 flex-shrink-0" />} title="No bank account metadata is available from the backend yet." />
      ) : bankAccounts.map(account => (
        <div key={account.bank_account_id} className="bg-slate-50 border border-slate-200 rounded-lg p-4 space-y-3">
          <div className="flex items-start justify-between gap-3">
            <div>
              <p className="text-sm font-semibold text-slate-900">{account.account_holder_name}</p>
              <p className="text-xs text-slate-500 mt-0.5">{account.bank_name || '-'} · {account.branch_name || '-'}</p>
            </div>
            <StatusBadge label={account.verification_status || account.status || 'pending'} size="sm" family={account.verification_status === 'verified' ? 'approved' : undefined} />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <SensitiveTile label="Bank Account" value={account.account_number.masked} />
            <InfoTile label="IFSC" value={account.ifsc || '-'} />
            <InfoTile label="Last Four" value={account.account_number.last4 || '-'} />
            <InfoTile label="Signature Verified" value={account.signature_verified_flag === null ? '-' : account.signature_verified_flag ? 'Yes' : 'No'} />
          </div>
        </div>
      ))}
    </div>
    <div className="card space-y-4">
      <h3 className="font-semibold text-slate-800 flex items-center gap-2"><Shield size={16} className="text-green-600" /> Security References</h3>
      <RecordList
        title="Cancelled Cheques"
        empty="No cancelled-cheque metadata is available from the backend yet."
        items={cancelledCheques.map(cheque => ({
          id: cheque.cancelled_cheque_id,
          title: cheque.account_number.masked || 'Masked account',
          subtitle: `${cheque.ifsc || '-'} · ${cheque.branch_name || '-'} · Document ${cheque.document_id}`,
          status: cheque.signature_mismatch_flag ? 'signature_mismatch' : cheque.verification_status,
        }))}
      />
      <RecordList
        title="Share Security"
        empty="No shareholding security records are available from the backend yet."
        items={shareholdings.map(shareholding => ({
          id: shareholding.shareholding_id,
          title: shareholding.folio_number,
          subtitle: `${formatCount(shareholding.pledged_share_count)} pledged · ${formatCount(shareholding.available_share_count)} available`,
          status: shareholding.future_shares_pledge_flag ? 'future pledge' : shareholding.status,
        }))}
      />
    </div>
  </div>
);

const NomineePanel: React.FC<{ nominees: MemberNomineeDetail[] }> = ({ nominees }) => (
  <div className="card space-y-4">
    <div className="flex items-center justify-between gap-3">
      <h3 className="font-semibold text-slate-800">Nominee Details</h3>
      <StatusBadge label={nominees.length > 0 ? `${nominees.length} recorded` : 'pending'} size="sm" />
    </div>
    {nominees.length === 0 ? (
      <EmptyPanel icon={<FileText size={18} className="text-slate-500 flex-shrink-0" />} title="No nominee records are available from the backend yet." />
    ) : nominees.map(nominee => (
      <div key={nominee.nominee_id} className="bg-slate-50 border border-slate-200 rounded-lg p-4 space-y-3">
        <div className="flex items-start justify-between gap-3">
          <div>
            <p className="text-sm font-semibold text-slate-900">{nominee.nominee_name}</p>
            <p className="text-xs text-slate-500 mt-0.5">{nominee.relationship_to_borrower || 'Relationship not recorded'} · {nominee.gender || '-'} · Age {nominee.age_at_application ?? '-'}</p>
          </div>
          <StatusBadge label={nominee.kyc_status || 'pending'} size="sm" />
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <SensitiveTile label="Nominee PAN" value={nominee.pan.masked} />
          <SensitiveTile label="Nominee Aadhaar" value={nominee.aadhaar.masked} />
          <InfoTile label="Signature Required" value={nominee.signature_required_flag ? 'Yes' : 'No'} />
        </div>
      </div>
    ))}
  </div>
);

const RecordList: React.FC<{
  title: string;
  empty: string;
  items: { id: string; title: string; subtitle: string; status: string }[];
}> = ({ title, empty, items }) => (
  <div className="space-y-3">
    <p className="text-xs text-slate-500 font-semibold uppercase tracking-wide">{title}</p>
    {items.length === 0 ? (
      <EmptyPanel icon={<FileText size={18} className="text-slate-500 flex-shrink-0" />} title={empty} />
    ) : items.map(item => (
      <div key={item.id} className="flex items-center gap-3 p-3 bg-slate-50 rounded-lg border border-slate-100">
        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold text-slate-900">{item.title}</p>
          <p className="text-xs text-slate-500 mt-0.5">{item.subtitle}</p>
        </div>
        <StatusBadge label={item.status || 'pending'} size="sm" family={item.status === 'verified' || item.status === 'active' ? 'approved' : undefined} />
      </div>
    ))}
  </div>
);

const DeferredTab: React.FC<{ title: string; message: string }> = ({ title, message }) => (
  <div className="card p-0 overflow-hidden">
    <div className="px-6 py-4 border-b border-slate-100">
      <h3 className="font-semibold text-slate-800">{title}</h3>
    </div>
    <div className="px-6 py-8">
      <EmptyPanel icon={deferredIcon(title)} title={message} />
    </div>
  </div>
);

const BorrowerState: React.FC<{ status: Borrower360Status; message?: string; onBack: () => void }> = ({ status, message, onBack }) => {
  const title = status === 'loading' ? 'Loading borrower 360' : 'Borrower 360 unavailable';
  const detail = status === 'loading' ? 'Please wait while borrower data is loaded.' : message || 'Borrower could not be loaded.';
  return (
    <div className="p-6 space-y-4">
      <div className="flex items-start gap-3">
        <button onClick={onBack} className="mt-1 text-slate-500 hover:text-slate-700 flex-shrink-0">
          <ChevronLeft size={20} />
        </button>
        <div>
          <h1 className="text-xl font-bold text-slate-900">{title}</h1>
          <p className="text-sm text-slate-500 mt-0.5">{detail}</p>
        </div>
      </div>
      <div className="card text-center py-12">
        <div className="mx-auto text-slate-300 mb-3 flex justify-center">
          {status === 'loading' ? <Clock size={24} /> : <AlertTriangle size={24} />}
        </div>
        <p className="text-sm font-semibold text-slate-700">{title}</p>
        <p className="text-xs text-slate-500 mt-1">{detail}</p>
      </div>
    </div>
  );
};

const HeaderMetric: React.FC<{ label: string; value: string }> = ({ label, value }) => (
  <div className="text-right">
    <p className="text-xs text-slate-400">{label}</p>
    <p className="text-lg font-bold text-slate-900 num">{value}</p>
  </div>
);

const Chip: React.FC<{ label: string; value: string }> = ({ label, value }) => (
  <div className="rounded-xl p-3 border border-slate-100 bg-slate-50 text-slate-900">
    <p className="text-lg font-bold">{value}</p>
    <p className="text-xs opacity-70 mt-0.5">{label}</p>
  </div>
);

const InfoTile: React.FC<{ label: string; value: string | number }> = ({ label, value }) => (
  <div className="bg-slate-50 rounded-lg p-3">
    <p className="text-xs text-slate-500 font-medium uppercase tracking-wide">{label}</p>
    <p className="text-sm font-semibold text-slate-900 mt-0.5">{value}</p>
  </div>
);

const SensitiveTile: React.FC<{
  label: string;
  value: string | null;
  canReveal?: boolean;
  revealed?: boolean;
  reason?: string;
  message?: string;
  submitting?: boolean;
  onReasonChange?: (value: string) => void;
  onReveal?: () => void;
  onHide?: () => void;
}> = ({
  label,
  value,
  canReveal = false,
  revealed = false,
  reason = '',
  message = '',
  submitting = false,
  onReasonChange,
  onReveal,
  onHide,
}) => (
  <div className="flex items-center gap-3 bg-amber-50 border border-amber-100 rounded-lg p-3">
    <div className="flex-1">
      <p className="text-xs text-slate-500">{label}</p>
      <p className="text-sm font-mono font-semibold text-slate-900">{value || '-'}</p>
      {canReveal && (
        <div className="mt-3 space-y-2">
          {!revealed && (
            <input
              className="field-input"
              value={reason}
              onChange={event => onReasonChange?.(event.target.value)}
              placeholder={`Reason to reveal ${label}`}
            />
          )}
          {message && <p className="text-xs text-slate-600">{message}</p>}
          <button className="btn-secondary text-xs inline-flex items-center gap-1" disabled={submitting} onClick={revealed ? onHide : onReveal} type="button">
            {revealed ? <EyeOff size={12} /> : <Eye size={12} />}
            {revealed ? 'Hide' : submitting ? 'Revealing' : 'Reveal'}
          </button>
        </div>
      )}
    </div>
    {revealed ? <Eye size={14} className="text-amber-700" /> : <Lock size={14} className="text-amber-700" />}
  </div>
);

const EmptyPanel: React.FC<{ icon: React.ReactNode; title: string }> = ({ icon, title }) => (
  <div className="flex items-center gap-3 bg-slate-50 border border-slate-200 rounded-lg p-4">
    {icon}
    <p className="text-sm font-semibold text-slate-700">{title}</p>
  </div>
);

const itemsFrom = <T,>(result: PromiseSettledResult<{ items: T[] }>): T[] => (
  result.status === 'fulfilled' ? result.value.items : []
);

const valueFrom = <T,>(result: PromiseSettledResult<T>): T | null => (
  result.status === 'fulfilled' ? result.value : null
);

const warningFrom = (result: PromiseSettledResult<unknown>, fallback: string) => (
  result.status === 'rejected' && !isNotFound(result.reason)
    ? result.reason instanceof Error ? result.reason.message : fallback
    : ''
);

const isNotFound = (error: unknown) => error instanceof AuthSessionError && error.status === 404;

const errorState = (error: unknown): { status: Borrower360Status; message: string } => {
  if (error instanceof AuthSessionError) {
    if (error.status === 401) return { status: 'unauthorized', message: error.message };
    if (error.status === 403) return { status: 'forbidden', message: error.message };
    if (error.status === 404) return { status: 'empty', message: error.message };
  }
  return { status: 'error', message: error instanceof Error ? error.message : 'Borrower could not be loaded.' };
};

const deferredIcon = (title: string) => {
  if (title === 'Communications') return <MessageSquare size={18} className="text-slate-500 flex-shrink-0" />;
  if (title === 'Audit Trail') return <History size={18} className="text-slate-500 flex-shrink-0" />;
  if (title === 'Loan Accounts') return <Banknote size={18} className="text-slate-500 flex-shrink-0" />;
  return <FileText size={18} className="text-slate-500 flex-shrink-0" />;
};

const memberTypeLabel = (value: string) => (value === 'fpc' ? 'FPC' : value.replace(/_/g, ' '));
const titleCase = (value: string) => value ? `${value.charAt(0).toUpperCase()}${value.slice(1).replace(/_/g, ' ')}` : '-';
const activeStatusLabel = (profile: MemberProfileDetail) => (
  (profile.active_member_status.status || profile.membership_status) === 'active'
    ? 'active_member'
    : profile.active_member_status.status || profile.membership_status
);
const formatCount = (value: number | null) => (value === null ? '-' : value.toLocaleString('en-IN'));
const formatDate = (value: string | null) => (value ? new Date(value).toLocaleDateString('en-IN') : '-');
const formatDateTime = (value: string | null) => (value ? new Date(value).toLocaleString('en-IN') : '-');
const addressText = (profile: MemberProfileDetail) => (
  [
    profile.registered_address.line1,
    profile.registered_address.line2,
    profile.registered_address.village_city,
    profile.registered_address.district,
    profile.registered_address.state,
    profile.registered_address.pincode,
  ].filter(Boolean).join(', ') || '-'
);

export default Borrower360;
