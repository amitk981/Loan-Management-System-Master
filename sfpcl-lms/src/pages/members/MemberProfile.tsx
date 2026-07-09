import React, { useEffect, useState } from 'react';
import {
  AlertTriangle,
  Building2,
  ChevronLeft,
  Clock,
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
  createMemberShareholding,
  createMemberNominee,
  fetchMemberNominees,
  fetchMemberProfile,
  fetchMemberShareholdings,
  type CreateMemberNomineePayload,
  type CreateMemberShareholdingPayload,
  type MemberNomineeDetail,
  type MemberProfileDetail,
  type MemberShareholdingDetail,
} from '../../services/memberProfileApi';

type ProfileStatus = 'loading' | 'success' | 'empty' | 'unauthorized' | 'forbidden' | 'error';
type NomineeStatus = 'idle' | 'loading' | 'success' | 'empty' | 'unauthorized' | 'forbidden' | 'error';
type ShareholdingStatus = 'idle' | 'loading' | 'success' | 'empty' | 'unauthorized' | 'forbidden' | 'error';

interface MemberProfileProps {
  memberId: string;
  onBack: () => void;
}

const MemberProfile: React.FC<MemberProfileProps> = ({ memberId, onBack }) => {
  const [status, setStatus] = useState<ProfileStatus>('loading');
  const [message, setMessage] = useState('');
  const [profile, setProfile] = useState<MemberProfileDetail | null>(null);
  const [activeTab, setActiveTab] = useState(0);
  const [nomineeStatus, setNomineeStatus] = useState<NomineeStatus>('idle');
  const [nomineeMessage, setNomineeMessage] = useState('');
  const [nominees, setNominees] = useState<MemberNomineeDetail[]>([]);
  const [nomineeCreateFieldErrors, setNomineeCreateFieldErrors] = useState<Record<string, string>>({});
  const [nomineeCreateMessage, setNomineeCreateMessage] = useState('');
  const [nomineeCreateSubmitting, setNomineeCreateSubmitting] = useState(false);
  const [shareholdingStatus, setShareholdingStatus] = useState<ShareholdingStatus>('idle');
  const [shareholdingMessage, setShareholdingMessage] = useState('');
  const [shareholdings, setShareholdings] = useState<MemberShareholdingDetail[]>([]);
  const [shareholdingCreateFieldErrors, setShareholdingCreateFieldErrors] = useState<Record<string, string>>({});
  const [shareholdingCreateMessage, setShareholdingCreateMessage] = useState('');
  const [shareholdingCreateSubmitting, setShareholdingCreateSubmitting] = useState(false);

  useEffect(() => {
    let cancelled = false;
    setStatus('loading');
    setMessage('');
    setProfile(null);
    setNomineeStatus('idle');
    setNomineeMessage('');
    setNominees([]);
    setNomineeCreateFieldErrors({});
    setNomineeCreateMessage('');
    setShareholdingStatus('idle');
    setShareholdingMessage('');
    setShareholdings([]);
    setShareholdingCreateFieldErrors({});
    setShareholdingCreateMessage('');
    fetchMemberProfile(memberId)
      .then(result => {
        if (!cancelled) {
          setProfile(result);
          setStatus('success');
        }
      })
      .catch(error => {
        if (!cancelled) {
          const next = errorState(error);
          setStatus(next.status);
          setMessage(next.message);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [memberId]);

  useEffect(() => {
    if (status !== 'success' || activeTab !== 1 || shareholdingStatus !== 'idle') return;
    let cancelled = false;
    setShareholdingStatus('loading');
    setShareholdingMessage('');
    fetchMemberShareholdings(memberId)
      .then(result => {
        if (!cancelled) {
          setShareholdings(result.items);
          setShareholdingStatus(result.items.length > 0 ? 'success' : 'empty');
        }
      })
      .catch(error => {
        if (!cancelled) {
          const next = errorState(error);
          setShareholdingStatus(next.status);
          setShareholdingMessage(next.message);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [activeTab, memberId, shareholdingStatus, status]);

  useEffect(() => {
    if (status !== 'success' || activeTab !== 7 || nomineeStatus !== 'idle') return;
    let cancelled = false;
    setNomineeStatus('loading');
    setNomineeMessage('');
    fetchMemberNominees(memberId)
      .then(result => {
        if (!cancelled) {
          setNominees(result.items);
          setNomineeStatus(result.items.length > 0 ? 'success' : 'empty');
        }
      })
      .catch(error => {
        if (!cancelled) {
          const next = errorState(error);
          setNomineeStatus(next.status);
          setNomineeMessage(next.message);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [activeTab, memberId, nomineeStatus, status]);

  const handleCreateNominee = async (payload: CreateMemberNomineePayload) => {
    setNomineeCreateSubmitting(true);
    setNomineeCreateFieldErrors({});
    setNomineeCreateMessage('');
    try {
      const created = await createMemberNominee(memberId, payload);
      setNominees(current => [created, ...current.filter(item => item.nominee_id !== created.nominee_id)]);
      setNomineeStatus('success');
      setNomineeCreateMessage('Nominee saved.');
    } catch (error) {
      if (error instanceof AuthSessionError) {
        setNomineeCreateFieldErrors(error.fieldErrors ?? {});
        setNomineeCreateMessage(error.message);
      } else {
        setNomineeCreateMessage(error instanceof Error ? error.message : 'Nominee could not be saved.');
      }
    } finally {
      setNomineeCreateSubmitting(false);
    }
  };

  const handleCreateShareholding = async (payload: CreateMemberShareholdingPayload) => {
    setShareholdingCreateSubmitting(true);
    setShareholdingCreateFieldErrors({});
    setShareholdingCreateMessage('');
    try {
      const created = await createMemberShareholding(memberId, payload);
      setShareholdings(current => [created, ...current.filter(item => item.shareholding_id !== created.shareholding_id)]);
      setShareholdingStatus('success');
      setShareholdingCreateMessage('Shareholding saved.');
    } catch (error) {
      if (error instanceof AuthSessionError) {
        setShareholdingCreateFieldErrors(error.fieldErrors ?? {});
        setShareholdingCreateMessage(error.message);
      } else {
        setShareholdingCreateMessage(error instanceof Error ? error.message : 'Shareholding could not be saved.');
      }
    } finally {
      setShareholdingCreateSubmitting(false);
    }
  };

  return (
    <MemberProfileView
      status={status}
      message={message}
      profile={profile}
      activeTab={activeTab}
      onTabChange={setActiveTab}
      onBack={onBack}
      nomineeStatus={nomineeStatus}
      nomineeMessage={nomineeMessage}
      nominees={nominees}
      nomineeCreateFieldErrors={nomineeCreateFieldErrors}
      nomineeCreateMessage={nomineeCreateMessage}
      nomineeCreateSubmitting={nomineeCreateSubmitting}
      onCreateNominee={handleCreateNominee}
      shareholdingStatus={shareholdingStatus}
      shareholdingMessage={shareholdingMessage}
      shareholdings={shareholdings}
      shareholdingCreateFieldErrors={shareholdingCreateFieldErrors}
      shareholdingCreateMessage={shareholdingCreateMessage}
      shareholdingCreateSubmitting={shareholdingCreateSubmitting}
      onCreateShareholding={handleCreateShareholding}
    />
  );
};

interface MemberProfileViewProps {
  status: ProfileStatus;
  message?: string;
  profile: MemberProfileDetail | null;
  activeTab: number;
  onTabChange: (index: number) => void;
  onBack: () => void;
  nomineeStatus?: NomineeStatus;
  nomineeMessage?: string;
  nominees?: MemberNomineeDetail[];
  nomineeCreateFieldErrors?: Record<string, string>;
  nomineeCreateMessage?: string;
  nomineeCreateSubmitting?: boolean;
  onCreateNominee?: (payload: CreateMemberNomineePayload) => void | Promise<void>;
  shareholdingStatus?: ShareholdingStatus;
  shareholdingMessage?: string;
  shareholdings?: MemberShareholdingDetail[];
  shareholdingCreateFieldErrors?: Record<string, string>;
  shareholdingCreateMessage?: string;
  shareholdingCreateSubmitting?: boolean;
  onCreateShareholding?: (payload: CreateMemberShareholdingPayload) => void | Promise<void>;
}

export const MemberProfileView: React.FC<MemberProfileViewProps> = ({
  status,
  message,
  profile,
  activeTab,
  onTabChange,
  onBack,
  nomineeStatus = 'idle',
  nomineeMessage = '',
  nominees = [],
  nomineeCreateFieldErrors = {},
  nomineeCreateMessage = '',
  nomineeCreateSubmitting = false,
  onCreateNominee,
  shareholdingStatus = 'idle',
  shareholdingMessage = '',
  shareholdings = [],
  shareholdingCreateFieldErrors = {},
  shareholdingCreateMessage = '',
  shareholdingCreateSubmitting = false,
  onCreateShareholding,
}) => {
  if (status !== 'success' || !profile) {
    return <ProfileState status={status} message={message} onBack={onBack} />;
  }

  const isInstitution = profile.member_type === 'fpc' || profile.member_type === 'producer_institution';
  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'shareholding', label: 'Shareholding' },
    { id: 'supply', label: 'Produce Supply' },
    { id: 'services', label: 'Services Availed' },
    { id: 'land', label: 'Land & Crop' },
    { id: 'kyc', label: 'KYC' },
    { id: 'loans', label: 'Loans' },
    { id: 'nominee', label: 'Nominee' },
    { id: 'communications', label: 'Communications' },
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
                {isInstitution && <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full font-semibold">{memberTypeLabel(profile.member_type)}</span>}
                <StatusBadge label={activeStatusLabel(profile)} size="sm" />
                <StatusBadge
                  label={profile.kyc_status === 'verified' ? 'KYC verified' : profile.kyc_status}
                  family={profile.kyc_status === 'verified' ? 'approved' : undefined}
                  size="sm"
                />
                {profile.default_status !== 'no_default' && <StatusBadge label={profile.default_status} size="sm" />}
              </div>
              <p className="text-sm text-slate-500 mt-0.5">
                Folio: <span className="font-semibold text-slate-900 num">{profile.folio_number}</span>
                {' · '}{memberTypeLabel(profile.member_type)}
                {profile.membership_start_date && ` · Member since ${new Date(profile.membership_start_date).getFullYear()}`}
                {' · '}Shares: {formatCount(profile.share_summary.number_of_shares)} ({profile.share_summary.holding_mode || 'unknown'})
              </p>
            </div>
            <div className="flex gap-2 flex-shrink-0">
              {profile.available_actions.map(action => (
                <button
                  key={action.action_code}
                  className="btn-secondary text-xs disabled:opacity-50 disabled:cursor-not-allowed"
                  disabled={!action.enabled}
                  title={action.disabled_reason || undefined}
                >
                  {action.label}
                </button>
              ))}
              <button className="btn-secondary text-xs">View KYC</button>
            </div>
          </div>
        </div>
      </div>

      {profile.kyc_status === 'rekyc_due' && (
        <AlertBanner type="warning" title="Re-KYC Required" message="KYC renewal is due before this member can proceed through later lending workflows." />
      )}
      {profile.default_status !== 'no_default' && (
        <AlertBanner type="error" title="Default Status Requires Review" message="Member has a default status on record. Eligibility decisions belong to later lending slices." />
      )}

      <Tabs tabs={tabs} activeIndex={activeTab} onChange={onTabChange}>
        <OverviewTab profile={profile} />
        <ShareholdingTab
          status={shareholdingStatus}
          message={shareholdingMessage}
          shareholdings={shareholdings}
          createFieldErrors={shareholdingCreateFieldErrors}
          createMessage={shareholdingCreateMessage}
          createSubmitting={shareholdingCreateSubmitting}
          onCreateShareholding={onCreateShareholding}
        />
        <DeferredTab title="Produce Supply History" message="No produce supply records are available from the backend yet." />
        <ServicesTab profile={profile} />
        <LandTab profile={profile} />
        <KycTab profile={profile} />
        <DeferredTab title="Loans" message="No loan records are available from the backend yet." />
        <NomineeTab
          status={nomineeStatus}
          message={nomineeMessage}
          nominees={nominees}
          createFieldErrors={nomineeCreateFieldErrors}
          createMessage={nomineeCreateMessage}
          createSubmitting={nomineeCreateSubmitting}
          onCreateNominee={onCreateNominee}
        />
        <DeferredTab title="Communications" message="No communication records are available from the backend yet." />
        <DeferredTab title="Audit Trail" message="No audit trail records are available from the backend yet." />
      </Tabs>
    </div>
  );
};

const ProfileState: React.FC<{ status: ProfileStatus; message?: string; onBack: () => void }> = ({ status, message, onBack }) => {
  const title = status === 'loading' ? 'Loading member profile' : 'Member profile unavailable';
  const detail = status === 'loading' ? 'Please wait while the member profile is loaded.' : message || 'Member could not be loaded.';
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

const OverviewTab: React.FC<{ profile: MemberProfileDetail }> = ({ profile }) => (
  <div className="card space-y-5">
    <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
      {[
        ['Member ID', profile.member_id.toUpperCase()],
        ['Member Number', profile.member_number || '-'],
        ['Folio Number', profile.folio_number],
        ['Member Type', memberTypeLabel(profile.member_type)],
        ['Membership Status', profile.membership_status.replace(/_/g, ' ')],
        ['Active Status', activeStatusLabel(profile).replace(/_/g, ' ')],
        ['Registered On', formatDate(profile.membership_start_date)],
        ['Mobile', profile.mobile_number || '-'],
        ['Email', profile.email || '-'],
      ].map(([label, value]) => <InfoTile key={label} label={label} value={value} />)}
    </div>
    <div>
      <p className="text-xs text-slate-500 font-medium uppercase tracking-wide mb-1 flex items-center gap-1"><MapPin size={12} /> Address</p>
      <p className="text-sm text-slate-800">{addressText(profile)}</p>
    </div>
    <TypeSpecificDetails profile={profile} />
    <div className="border-t border-slate-100 pt-4">
      <p className="text-xs text-slate-500 font-semibold uppercase tracking-wide mb-3 flex items-center gap-1"><Lock size={12} /> Sensitive Identifiers - Masked</p>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <SensitiveTile label="PAN" value={profile.pan.masked} />
        <SensitiveTile label="Aadhaar" value={profile.aadhaar.masked} />
      </div>
    </div>
  </div>
);

const TypeSpecificDetails: React.FC<{ profile: MemberProfileDetail }> = ({ profile }) => {
  const isInstitution = profile.member_type === 'fpc' || profile.member_type === 'producer_institution';
  const individual = profile.individual_profile;
  const producer = profile.producer_institution_profile;
  return (
    <div className="border-t border-slate-100 pt-4 space-y-3">
      <p className="text-xs text-slate-500 font-semibold uppercase tracking-wide">
        {isInstitution ? 'Producer Institution Details' : 'Individual Farmer Details'}
      </p>
      {isInstitution && producer && (
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
          <InfoTile label="Institution Type" value={producer.institution_type.replace(/_/g, ' ')} />
          <InfoTile label="Registration Number" value={producer.registration_number || '-'} />
          <InfoTile label="Authorised Signatory" value={producer.authorised_signatory_name} />
          <InfoTile label="Board Resolution Required" value={producer.board_resolution_required_flag ? 'Yes' : 'No'} />
          <InfoTile label="Produce Supply" value={formatYears(producer.produce_supply_years)} />
        </div>
      )}
      {!isInstitution && individual && (
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
          <InfoTile label="First Name" value={individual.first_name} />
          <InfoTile label="Middle Name" value={individual.middle_name || '-'} />
          <InfoTile label="Last Name" value={individual.last_name} />
          <InfoTile label="Gender" value={individual.gender?.replace(/_/g, ' ') || '-'} />
          <InfoTile label="Date of Birth" value={formatDate(individual.date_of_birth)} />
          <InfoTile label="Occupation" value={individual.occupation || '-'} />
          <InfoTile label="Employment / Service" value={formatYears(individual.employment_or_service_years)} />
        </div>
      )}
      {!producer && !individual && (
        <EmptyPanel
          icon={isInstitution
            ? <Building2 size={18} className="text-slate-500 flex-shrink-0" />
            : <User size={18} className="text-slate-500 flex-shrink-0" />}
          title="Profile details are not available from the backend yet."
        />
      )}
    </div>
  );
};

const ShareholdingTab: React.FC<{
  status: ShareholdingStatus;
  message: string;
  shareholdings: MemberShareholdingDetail[];
  createFieldErrors: Record<string, string>;
  createMessage: string;
  createSubmitting: boolean;
  onCreateShareholding?: (payload: CreateMemberShareholdingPayload) => void | Promise<void>;
}> = ({
  status,
  message,
  shareholdings,
  createFieldErrors,
  createMessage,
  createSubmitting,
  onCreateShareholding,
}) => (
  <div className="card space-y-5">
    <div className="flex items-center justify-between gap-3">
      <h3 className="font-semibold text-slate-800">Shareholding Details</h3>
      <StatusBadge label={shareholdings.length > 0 ? `${shareholdings.length} recorded` : 'pending'} size="sm" />
    </div>
    {createMessage && (
      <AlertBanner
        type={Object.keys(createFieldErrors).length > 0 || status === 'forbidden' || status === 'error' ? 'error' : 'success'}
        title={Object.keys(createFieldErrors).length > 0 ? 'Shareholding validation failed' : 'Shareholding update'}
        message={createMessage}
      />
    )}
    <ShareholdingState status={status} message={message} shareholdings={shareholdings} />
    <ShareholdingCreateForm
      fieldErrors={createFieldErrors}
      submitting={createSubmitting}
      onCreateShareholding={onCreateShareholding}
    />
  </div>
);

const ShareholdingState: React.FC<{
  status: ShareholdingStatus;
  message: string;
  shareholdings: MemberShareholdingDetail[];
}> = ({ status, message, shareholdings }) => {
  if (status === 'idle' || status === 'loading') {
    return <EmptyPanel icon={<Clock size={18} className="text-slate-500 flex-shrink-0" />} title="Loading shareholding records" />;
  }
  if (status === 'empty' || shareholdings.length === 0) {
    return <EmptyPanel icon={<FileText size={18} className="text-slate-500 flex-shrink-0" />} title={message || 'No shareholding records are available from the backend yet.'} />;
  }
  if (status === 'unauthorized' || status === 'forbidden' || status === 'error') {
    return <EmptyPanel icon={<AlertTriangle size={18} className="text-slate-500 flex-shrink-0" />} title={message || 'Shareholdings could not be loaded.'} />;
  }
  return (
    <div className="space-y-3">
      {shareholdings.map(shareholding => (
        <div key={shareholding.shareholding_id} className="bg-slate-50 border border-slate-200 rounded-lg p-4 space-y-3">
          <div className="flex items-start justify-between gap-3">
            <div>
              <p className="text-sm font-semibold text-slate-900">{shareholding.folio_number}</p>
              <p className="text-xs text-slate-500 mt-0.5">
                {titleCase(shareholding.holding_mode)} · {shareholding.status || 'active'}
              </p>
            </div>
            <StatusBadge label={shareholding.future_shares_pledge_flag ? 'future pledge' : shareholding.status || 'active'} size="sm" />
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <InfoTile label="Total Shares" value={formatCount(shareholding.number_of_shares)} />
            <InfoTile label="Pledged Shares" value={formatCount(shareholding.pledged_share_count)} />
            <InfoTile label="Available Shares" value={formatCount(shareholding.available_share_count)} />
            <InfoTile label="Valuation / Share" value={shareholding.valuation_per_share || '-'} />
          </div>
        </div>
      ))}
    </div>
  );
};

const ShareholdingCreateForm: React.FC<{
  fieldErrors: Record<string, string>;
  submitting: boolean;
  onCreateShareholding?: (payload: CreateMemberShareholdingPayload) => void | Promise<void>;
}> = ({ fieldErrors, submitting, onCreateShareholding }) => {
  const [form, setForm] = useState<CreateMemberShareholdingPayload>({
    folio_number: '',
    number_of_shares: 0,
    holding_mode: 'physical',
    valuation_per_share: '',
    valuation_effective_date: '',
    pledged_share_count: 0,
    future_shares_pledge_flag: false,
  });
  const setField = (field: keyof CreateMemberShareholdingPayload, value: string | number | boolean) => {
    setForm(current => ({ ...current, [field]: value }));
  };
  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    await onCreateShareholding?.(form);
  };
  return (
    <form className="border-t border-slate-100 pt-4 space-y-4" onSubmit={submit}>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <Field label="Folio number" error={fieldErrors.folio_number}>
          <input className="field-input" value={form.folio_number} onChange={event => setField('folio_number', event.target.value)} />
        </Field>
        <Field label="Holding mode" error={fieldErrors.holding_mode}>
          <select className="field-select" value={form.holding_mode} onChange={event => setField('holding_mode', event.target.value)}>
            <option value="physical">Physical</option>
            <option value="demat">Demat</option>
            <option value="mixed">Mixed</option>
          </select>
        </Field>
        <Field label="Number of shares" error={fieldErrors.number_of_shares}>
          <input type="number" min="0" className="field-input" value={form.number_of_shares} onChange={event => setField('number_of_shares', Number(event.target.value))} />
        </Field>
        <Field label="Pledged shares" error={fieldErrors.pledged_share_count}>
          <input type="number" min="0" className="field-input" value={form.pledged_share_count} onChange={event => setField('pledged_share_count', Number(event.target.value))} />
        </Field>
        <Field label="Valuation per share" error={fieldErrors.valuation_per_share}>
          <input className="field-input" value={form.valuation_per_share} onChange={event => setField('valuation_per_share', event.target.value)} />
        </Field>
        <Field label="Valuation effective date" error={fieldErrors.valuation_effective_date}>
          <input type="date" className="field-input" value={form.valuation_effective_date} onChange={event => setField('valuation_effective_date', event.target.value)} />
        </Field>
      </div>
      <label className="flex items-center gap-2 text-sm text-slate-700">
        <input
          type="checkbox"
          className="accent-green-600"
          checked={form.future_shares_pledge_flag}
          onChange={event => setField('future_shares_pledge_flag', event.target.checked)}
        />
        Future shares pledged
      </label>
      <button className="btn-primary" disabled={submitting || !onCreateShareholding} type="submit">
        {submitting ? 'Saving shareholding' : 'Save shareholding'}
      </button>
    </form>
  );
};

const ServicesTab: React.FC<{ profile: MemberProfileDetail }> = ({ profile }) => {
  const serviceFlag = profile.individual_profile?.services_availed_flag ?? profile.producer_institution_profile?.services_availed_flag ?? null;
  return (
    <div className="card space-y-4">
      <h3 className="font-semibold text-slate-800">Services Availed</h3>
      <InfoTile label="Services Availed Flag" value={serviceFlag === null ? '-' : serviceFlag ? 'Yes' : 'No'} />
      <EmptyPanel icon={<Shield size={18} className="text-slate-500 flex-shrink-0" />} title="Detailed service records are not available from the backend yet." />
    </div>
  );
};

const LandTab: React.FC<{ profile: MemberProfileDetail }> = ({ profile }) => (
  <div className="card space-y-4">
    <h3 className="font-semibold text-slate-800">Land & Crop Evidence</h3>
    <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
      <InfoTile label="Land Area Under Cultivation" value={profile.individual_profile?.land_area_under_cultivation_acres ? `${profile.individual_profile.land_area_under_cultivation_acres} acres` : '-'} />
      <InfoTile label="Primary Crop" value={profile.individual_profile?.primary_crop || '-'} />
    </div>
    <EmptyPanel icon={<FileText size={18} className="text-slate-500 flex-shrink-0" />} title="Land document and crop evidence records are not available from the backend yet." />
  </div>
);

const KycTab: React.FC<{ profile: MemberProfileDetail }> = ({ profile }) => (
  <div className="card space-y-4">
    <div className="flex items-center justify-between">
      <h3 className="font-semibold text-slate-800">KYC Status</h3>
      <StatusBadge label={profile.kyc_status === 'verified' ? 'KYC verified' : profile.kyc_status} family={profile.kyc_status === 'verified' ? 'approved' : undefined} />
    </div>
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <SensitiveTile label="PAN" value={profile.pan.masked} />
      <SensitiveTile label="Aadhaar" value={profile.aadhaar.masked} />
    </div>
    <EmptyPanel icon={<Shield size={18} className="text-slate-500 flex-shrink-0" />} title="KYC document records are not available from the backend yet." />
  </div>
);

const NomineeTab: React.FC<{
  status: NomineeStatus;
  message: string;
  nominees: MemberNomineeDetail[];
  createFieldErrors: Record<string, string>;
  createMessage: string;
  createSubmitting: boolean;
  onCreateNominee?: (payload: CreateMemberNomineePayload) => void | Promise<void>;
}> = ({
  status,
  message,
  nominees,
  createFieldErrors,
  createMessage,
  createSubmitting,
  onCreateNominee,
}) => (
  <div className="card space-y-5">
    <div className="flex items-center justify-between gap-3">
      <h3 className="font-semibold text-slate-800">Nominee Details</h3>
      <StatusBadge label={nominees.length > 0 ? `${nominees.length} recorded` : 'pending'} size="sm" />
    </div>
    {createMessage && (
      <AlertBanner
        type={Object.keys(createFieldErrors).length > 0 || status === 'forbidden' || status === 'error' ? 'error' : 'success'}
        title={Object.keys(createFieldErrors).length > 0 ? 'Nominee validation failed' : 'Nominee update'}
        message={createMessage}
      />
    )}
    <NomineeState status={status} message={message} nominees={nominees} />
    <NomineeCreateForm
      fieldErrors={createFieldErrors}
      submitting={createSubmitting}
      onCreateNominee={onCreateNominee}
    />
  </div>
);

const NomineeState: React.FC<{
  status: NomineeStatus;
  message: string;
  nominees: MemberNomineeDetail[];
}> = ({ status, message, nominees }) => {
  if (status === 'idle' || status === 'loading') {
    return <EmptyPanel icon={<Clock size={18} className="text-slate-500 flex-shrink-0" />} title="Loading nominee records" />;
  }
  if (status === 'empty' || nominees.length === 0) {
    return <EmptyPanel icon={<FileText size={18} className="text-slate-500 flex-shrink-0" />} title={message || 'No nominee records are available from the backend yet.'} />;
  }
  if (status === 'unauthorized' || status === 'forbidden' || status === 'error') {
    return <EmptyPanel icon={<AlertTriangle size={18} className="text-slate-500 flex-shrink-0" />} title={message || 'Nominees could not be loaded.'} />;
  }
  return (
    <div className="space-y-3">
      {nominees.map(nominee => (
        <div key={nominee.nominee_id} className="bg-slate-50 border border-slate-200 rounded-lg p-4 space-y-3">
          <div className="flex items-start justify-between gap-3">
            <div>
              <p className="text-sm font-semibold text-slate-900">{nominee.nominee_name}</p>
              <p className="text-xs text-slate-500 mt-0.5">
                {nominee.relationship_to_borrower || 'Relationship not recorded'} · {nominee.gender || '-'} · Age {nominee.age_at_application ?? '-'}
              </p>
            </div>
            <StatusBadge label={nominee.kyc_status || 'pending'} size="sm" />
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <SensitiveTile label="PAN" value={nominee.pan.masked} />
            <SensitiveTile label="Aadhaar" value={nominee.aadhaar.masked} />
            <InfoTile label="Signature Required" value={nominee.signature_required_flag ? 'Yes' : 'No'} />
          </div>
        </div>
      ))}
    </div>
  );
};

const NomineeCreateForm: React.FC<{
  fieldErrors: Record<string, string>;
  submitting: boolean;
  onCreateNominee?: (payload: CreateMemberNomineePayload) => void | Promise<void>;
}> = ({ fieldErrors, submitting, onCreateNominee }) => {
  const [form, setForm] = useState<CreateMemberNomineePayload>({
    nominee_name: '',
    date_of_birth: '',
    gender: '',
    relationship_to_borrower: '',
    pan: '',
    aadhaar: '',
    signature_required_flag: true,
  });
  const setField = (field: keyof CreateMemberNomineePayload, value: string | boolean) => {
    setForm(current => ({ ...current, [field]: value }));
  };
  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    await onCreateNominee?.(form);
  };
  return (
    <form className="border-t border-slate-100 pt-4 space-y-4" onSubmit={submit}>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <Field label="Nominee full name" error={fieldErrors.nominee_name}>
          <input className="field-input" value={form.nominee_name} onChange={event => setField('nominee_name', event.target.value)} />
        </Field>
        <Field label="Date of birth" error={fieldErrors.date_of_birth}>
          <input type="date" className="field-input" value={form.date_of_birth} onChange={event => setField('date_of_birth', event.target.value)} />
        </Field>
        <Field label="Gender" error={fieldErrors.gender}>
          <select className="field-select" value={form.gender} onChange={event => setField('gender', event.target.value)}>
            <option value="">Select gender</option>
            <option value="female">Female</option>
            <option value="male">Male</option>
            <option value="other">Other</option>
          </select>
        </Field>
        <Field label="Relationship to borrower" error={fieldErrors.relationship_to_borrower}>
          <input className="field-input" value={form.relationship_to_borrower} onChange={event => setField('relationship_to_borrower', event.target.value)} />
        </Field>
        <Field label="PAN" error={fieldErrors.pan}>
          <input className="field-input" value={form.pan} onChange={event => setField('pan', event.target.value)} />
        </Field>
        <Field label="Aadhaar" error={fieldErrors.aadhaar}>
          <input className="field-input" value={form.aadhaar} onChange={event => setField('aadhaar', event.target.value)} />
        </Field>
      </div>
      <label className="flex items-center gap-2 text-sm text-slate-700">
        <input
          type="checkbox"
          className="accent-green-600"
          checked={form.signature_required_flag}
          onChange={event => setField('signature_required_flag', event.target.checked)}
        />
        Signature required
      </label>
      <button className="btn-primary" disabled={submitting || !onCreateNominee} type="submit">
        {submitting ? 'Saving nominee' : 'Save nominee'}
      </button>
    </form>
  );
};

const Field: React.FC<{ label: string; error?: string; children: React.ReactNode }> = ({ label, error, children }) => (
  <label className="block">
    <span className="field-label">{label}</span>
    {children}
    {error && <span className="text-xs text-red-600 mt-1 block">{error}</span>}
  </label>
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

const InfoTile: React.FC<{ label: string; value: string | number }> = ({ label, value }) => (
  <div className="bg-slate-50 rounded-lg p-3">
    <p className="text-xs text-slate-500 font-medium uppercase tracking-wide">{label}</p>
    <p className="text-sm font-semibold text-slate-900 mt-0.5">{value}</p>
  </div>
);

const SensitiveTile: React.FC<{ label: string; value: string | null }> = ({ label, value }) => (
  <div className="flex items-center gap-3 bg-amber-50 border border-amber-100 rounded-lg p-3">
    <div className="flex-1">
      <p className="text-xs text-slate-500">{label}</p>
      <p className="text-sm font-mono font-semibold text-slate-900">{value || '-'}</p>
    </div>
    <Lock size={14} className="text-amber-700" />
  </div>
);

const EmptyPanel: React.FC<{ icon: React.ReactNode; title: string }> = ({ icon, title }) => (
  <div className="flex items-center gap-3 bg-slate-50 border border-slate-200 rounded-lg p-4">
    {icon}
    <p className="text-sm font-semibold text-slate-700">{title}</p>
  </div>
);

const errorState = (error: unknown): { status: ProfileStatus; message: string } => {
  if (error instanceof AuthSessionError) {
    if (error.status === 401) return { status: 'unauthorized', message: error.message };
    if (error.status === 403) return { status: 'forbidden', message: error.message };
    if (error.status === 404) return { status: 'empty', message: error.message };
  }
  return { status: 'error', message: error instanceof Error ? error.message : 'Member could not be loaded.' };
};

const deferredIcon = (title: string) => {
  if (title === 'Communications') return <MessageSquare size={18} className="text-slate-500 flex-shrink-0" />;
  if (title === 'Audit Trail') return <History size={18} className="text-slate-500 flex-shrink-0" />;
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
const formatYears = (value: string | null) => (value ? `${value} years` : '-');
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

export default MemberProfile;
