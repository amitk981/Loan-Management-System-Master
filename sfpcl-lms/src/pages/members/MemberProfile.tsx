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
import { fetchMemberProfile, type MemberProfileDetail } from '../../services/memberProfileApi';

type ProfileStatus = 'loading' | 'success' | 'empty' | 'unauthorized' | 'forbidden' | 'error';

interface MemberProfileProps {
  memberId: string;
  onBack: () => void;
}

const MemberProfile: React.FC<MemberProfileProps> = ({ memberId, onBack }) => {
  const [status, setStatus] = useState<ProfileStatus>('loading');
  const [message, setMessage] = useState('');
  const [profile, setProfile] = useState<MemberProfileDetail | null>(null);
  const [activeTab, setActiveTab] = useState(0);

  useEffect(() => {
    let cancelled = false;
    setStatus('loading');
    setMessage('');
    setProfile(null);
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

  return (
    <MemberProfileView
      status={status}
      message={message}
      profile={profile}
      activeTab={activeTab}
      onTabChange={setActiveTab}
      onBack={onBack}
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
}

export const MemberProfileView: React.FC<MemberProfileViewProps> = ({
  status,
  message,
  profile,
  activeTab,
  onTabChange,
  onBack,
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
        <ShareholdingTab profile={profile} />
        <DeferredTab title="Produce Supply History" message="No produce supply records are available from the backend yet." />
        <ServicesTab profile={profile} />
        <LandTab profile={profile} />
        <KycTab profile={profile} />
        <DeferredTab title="Loans" message="No loan records are available from the backend yet." />
        <DeferredTab title="Nominee" message="No nominee records are available from the backend yet." />
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
    <div className="border-t border-slate-100 pt-4">
      <p className="text-xs text-slate-500 font-semibold uppercase tracking-wide mb-3 flex items-center gap-1"><Lock size={12} /> Sensitive Identifiers - Masked</p>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <SensitiveTile label="PAN" value={profile.pan.masked} />
        <SensitiveTile label="Aadhaar" value={profile.aadhaar.masked} />
      </div>
    </div>
  </div>
);

const ShareholdingTab: React.FC<{ profile: MemberProfileDetail }> = ({ profile }) => (
  <div className="card space-y-4">
    <h3 className="font-semibold text-slate-800">Shareholding Details</h3>
    <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
      <InfoTile label="Total Shares Held" value={formatCount(profile.share_summary.number_of_shares)} />
      <InfoTile label="Available Shares" value={formatCount(profile.share_summary.available_share_count)} />
      <InfoTile label="Folio Number" value={profile.folio_number} />
      <InfoTile label="Shareholding Mode" value={profile.share_summary.holding_mode || '-'} />
    </div>
    <EmptyPanel icon={<FileText size={18} className="text-slate-500 flex-shrink-0" />} title="Share certificate details are not available from the backend yet." />
  </div>
);

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
const activeStatusLabel = (profile: MemberProfileDetail) => (
  (profile.active_member_status.status || profile.membership_status) === 'active'
    ? 'active_member'
    : profile.active_member_status.status || profile.membership_status
);
const formatCount = (value: number | null) => (value === null ? '-' : value.toLocaleString('en-IN'));
const formatDate = (value: string | null) => (value ? new Date(value).toLocaleDateString('en-IN') : '-');
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
