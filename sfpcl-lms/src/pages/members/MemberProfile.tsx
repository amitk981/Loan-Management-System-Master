import React, { useEffect, useState } from 'react';
import {
  AlertTriangle,
  Building2,
  ChevronLeft,
  Clock,
  FileText,
  History,
  Eye,
  EyeOff,
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
  createMemberCropPlan,
  createMemberKycProfile,
  createMemberLandHolding,
  createMemberShareholding,
  createMemberNominee,
  fetchMemberCropPlans,
  fetchMemberKycProfile,
  fetchMemberLandHoldings,
  fetchMemberNominees,
  fetchMemberProfile,
  fetchMemberShareholdings,
  revealMemberSensitiveField,
  updateMemberKycProfile,
  uploadMemberKycDocument,
  verifyMemberKycDocument,
  type CreateMemberKycProfilePayload,
  type CreateMemberCropPlanPayload,
  type CreateMemberLandHoldingPayload,
  type CreateMemberNomineePayload,
  type CreateMemberShareholdingPayload,
  type KycDocumentDetail,
  type KycProfileDetail,
  type UpdateMemberKycProfilePayload,
  type UploadMemberKycDocumentPayload,
  type VerifyMemberKycDocumentPayload,
  type MemberCropPlanDetail,
  type MemberLandHoldingDetail,
  type MemberNomineeDetail,
  type MemberProfileDetail,
  type MemberShareholdingDetail,
} from '../../services/memberProfileApi';

type ProfileStatus = 'loading' | 'success' | 'empty' | 'unauthorized' | 'forbidden' | 'error';
type NomineeStatus = 'idle' | 'loading' | 'success' | 'empty' | 'unauthorized' | 'forbidden' | 'error';
type ShareholdingStatus = 'idle' | 'loading' | 'success' | 'empty' | 'unauthorized' | 'forbidden' | 'error';
type LandCropStatus = 'idle' | 'loading' | 'success' | 'empty' | 'unauthorized' | 'forbidden' | 'error';
type KycStatus = 'idle' | 'loading' | 'success' | 'empty' | 'unauthorized' | 'forbidden' | 'error';

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
  const [landCropStatus, setLandCropStatus] = useState<LandCropStatus>('idle');
  const [landCropMessage, setLandCropMessage] = useState('');
  const [landHoldings, setLandHoldings] = useState<MemberLandHoldingDetail[]>([]);
  const [cropPlans, setCropPlans] = useState<MemberCropPlanDetail[]>([]);
  const [landCreateFieldErrors, setLandCreateFieldErrors] = useState<Record<string, string>>({});
  const [landCreateMessage, setLandCreateMessage] = useState('');
  const [landCreateSubmitting, setLandCreateSubmitting] = useState(false);
  const [cropCreateFieldErrors, setCropCreateFieldErrors] = useState<Record<string, string>>({});
  const [cropCreateMessage, setCropCreateMessage] = useState('');
  const [cropCreateSubmitting, setCropCreateSubmitting] = useState(false);
  const [kycStatus, setKycStatus] = useState<KycStatus>('idle');
  const [kycMessage, setKycMessage] = useState('');
  const [kycProfile, setKycProfile] = useState<KycProfileDetail | null>(null);
  const [kycCreateFieldErrors, setKycCreateFieldErrors] = useState<Record<string, string>>({});
  const [kycCreateMessage, setKycCreateMessage] = useState('');
  const [kycCreateSubmitting, setKycCreateSubmitting] = useState(false);
  const [kycDocumentFieldErrors, setKycDocumentFieldErrors] = useState<Record<string, string>>({});
  const [kycDocumentMessage, setKycDocumentMessage] = useState('');
  const [kycDocumentSubmitting, setKycDocumentSubmitting] = useState(false);
  const [kycVerifyFieldErrors, setKycVerifyFieldErrors] = useState<Record<string, string>>({});
  const [kycVerifyMessage, setKycVerifyMessage] = useState('');
  const [kycVerifySubmitting, setKycVerifySubmitting] = useState(false);

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
    setLandCropStatus('idle');
    setLandCropMessage('');
    setLandHoldings([]);
    setCropPlans([]);
    setLandCreateFieldErrors({});
    setLandCreateMessage('');
    setCropCreateFieldErrors({});
    setCropCreateMessage('');
    setKycStatus('idle');
    setKycMessage('');
    setKycProfile(null);
    setKycCreateFieldErrors({});
    setKycCreateMessage('');
    setKycDocumentFieldErrors({});
    setKycDocumentMessage('');
    setKycVerifyFieldErrors({});
    setKycVerifyMessage('');
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
    if (status !== 'success' || activeTab !== 4 || landCropStatus !== 'idle') return;
    let cancelled = false;
    setLandCropStatus('loading');
    setLandCropMessage('');
    Promise.all([fetchMemberLandHoldings(memberId), fetchMemberCropPlans(memberId)])
      .then(([landResult, cropResult]) => {
        if (!cancelled) {
          setLandHoldings(landResult.items);
          setCropPlans(cropResult.items);
          setLandCropStatus(landResult.items.length > 0 || cropResult.items.length > 0 ? 'success' : 'empty');
        }
      })
      .catch(error => {
        if (!cancelled) {
          const next = errorState(error);
          setLandCropStatus(next.status);
          setLandCropMessage(next.message);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [activeTab, landCropStatus, memberId, status]);

  useEffect(() => {
    if (status !== 'success' || activeTab !== 5 || kycStatus !== 'idle') return;
    let cancelled = false;
    setKycStatus('loading');
    setKycMessage('');
    fetchMemberKycProfile(memberId)
      .then(result => {
        if (!cancelled) {
          setKycProfile(result);
          setKycStatus('success');
        }
      })
      .catch(error => {
        if (!cancelled) {
          const next = errorState(error);
          setKycStatus(next.status === 'empty' ? 'empty' : next.status);
          setKycMessage(next.message);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [activeTab, kycStatus, memberId, status]);

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

  const handleCreateLandHolding = async (payload: CreateMemberLandHoldingPayload) => {
    setLandCreateSubmitting(true);
    setLandCreateFieldErrors({});
    setLandCreateMessage('');
    try {
      const created = await createMemberLandHolding(memberId, payload);
      setLandHoldings(current => [created, ...current.filter(item => item.land_holding_id !== created.land_holding_id)]);
      setLandCropStatus('success');
      setLandCreateMessage('Land holding saved.');
    } catch (error) {
      if (error instanceof AuthSessionError) {
        setLandCreateFieldErrors(error.fieldErrors ?? {});
        setLandCreateMessage(error.message);
      } else {
        setLandCreateMessage(error instanceof Error ? error.message : 'Land holding could not be saved.');
      }
    } finally {
      setLandCreateSubmitting(false);
    }
  };

  const handleCreateCropPlan = async (payload: CreateMemberCropPlanPayload) => {
    setCropCreateSubmitting(true);
    setCropCreateFieldErrors({});
    setCropCreateMessage('');
    try {
      const created = await createMemberCropPlan(memberId, payload);
      setCropPlans(current => [created, ...current.filter(item => item.crop_plan_id !== created.crop_plan_id)]);
      setLandCropStatus('success');
      setCropCreateMessage('Crop plan saved.');
    } catch (error) {
      if (error instanceof AuthSessionError) {
        setCropCreateFieldErrors(error.fieldErrors ?? {});
        setCropCreateMessage(error.message);
      } else {
        setCropCreateMessage(error instanceof Error ? error.message : 'Crop plan could not be saved.');
      }
    } finally {
      setCropCreateSubmitting(false);
    }
  };

  const handleCreateKycProfile = async (payload: CreateMemberKycProfilePayload) => {
    setKycCreateSubmitting(true);
    setKycCreateFieldErrors({});
    setKycCreateMessage('');
    try {
      const created = await createMemberKycProfile(memberId, payload);
      setKycProfile(created);
      setKycStatus('success');
      setKycCreateMessage('KYC profile saved.');
    } catch (error) {
      if (error instanceof AuthSessionError) {
        setKycCreateFieldErrors(error.fieldErrors ?? {});
        setKycCreateMessage(error.message);
      } else {
        setKycCreateMessage(error instanceof Error ? error.message : 'KYC profile could not be saved.');
      }
    } finally {
      setKycCreateSubmitting(false);
    }
  };

  const handleUpdateKycProfile = async (payload: UpdateMemberKycProfilePayload) => {
    if (!kycProfile) return;
    setKycCreateSubmitting(true);
    setKycCreateFieldErrors({});
    setKycCreateMessage('');
    try {
      const updated = await updateMemberKycProfile(kycProfile.kyc_profile_id, payload);
      setKycProfile(updated);
      setKycStatus('success');
      setKycCreateMessage('KYC profile saved.');
    } catch (error) {
      if (error instanceof AuthSessionError) {
        setKycCreateFieldErrors(error.fieldErrors ?? {});
        setKycCreateMessage(error.message);
      } else {
        setKycCreateMessage(error instanceof Error ? error.message : 'KYC profile could not be saved.');
      }
    } finally {
      setKycCreateSubmitting(false);
    }
  };

  const handleUploadKycDocument = async (payload: UploadMemberKycDocumentPayload) => {
    if (!kycProfile) return;
    setKycDocumentSubmitting(true);
    setKycDocumentFieldErrors({});
    setKycDocumentMessage('');
    try {
      const uploaded = await uploadMemberKycDocument(kycProfile.kyc_profile_id, payload);
      setKycProfile(current => current ? {
        ...current,
        documents: [uploaded, ...current.documents.filter(item => item.kyc_document_id !== uploaded.kyc_document_id)],
      } : current);
      setKycDocumentMessage('KYC document uploaded.');
    } catch (error) {
      if (error instanceof AuthSessionError) {
        setKycDocumentFieldErrors(error.fieldErrors ?? {});
        setKycDocumentMessage(error.message);
      } else {
        setKycDocumentMessage(error instanceof Error ? error.message : 'KYC document could not be uploaded.');
      }
    } finally {
      setKycDocumentSubmitting(false);
    }
  };

  const handleVerifyKycDocument = async (kycDocumentId: string, payload: VerifyMemberKycDocumentPayload) => {
    setKycVerifySubmitting(true);
    setKycVerifyFieldErrors({});
    setKycVerifyMessage('');
    try {
      const verified = await verifyMemberKycDocument(kycDocumentId, payload);
      setKycProfile(current => current ? {
        ...current,
        documents: current.documents.map(item => item.kyc_document_id === verified.kyc_document_id ? verified : item),
      } : current);
      setKycVerifyMessage('KYC document verified.');
    } catch (error) {
      if (error instanceof AuthSessionError) {
        setKycVerifyFieldErrors(error.fieldErrors ?? {});
        setKycVerifyMessage(error.message);
      } else {
        setKycVerifyMessage(error instanceof Error ? error.message : 'KYC document could not be verified.');
      }
    } finally {
      setKycVerifySubmitting(false);
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
      landCropStatus={landCropStatus}
      landCropMessage={landCropMessage}
      landHoldings={landHoldings}
      cropPlans={cropPlans}
      landCreateFieldErrors={landCreateFieldErrors}
      landCreateMessage={landCreateMessage}
      landCreateSubmitting={landCreateSubmitting}
      cropCreateFieldErrors={cropCreateFieldErrors}
      cropCreateMessage={cropCreateMessage}
      cropCreateSubmitting={cropCreateSubmitting}
      onCreateLandHolding={handleCreateLandHolding}
      onCreateCropPlan={handleCreateCropPlan}
      kycStatus={kycStatus}
      kycMessage={kycMessage}
      kycProfile={kycProfile}
      kycCreateFieldErrors={kycCreateFieldErrors}
      kycCreateMessage={kycCreateMessage}
      kycCreateSubmitting={kycCreateSubmitting}
      kycDocumentFieldErrors={kycDocumentFieldErrors}
      kycDocumentMessage={kycDocumentMessage}
      kycDocumentSubmitting={kycDocumentSubmitting}
      kycVerifyFieldErrors={kycVerifyFieldErrors}
      kycVerifyMessage={kycVerifyMessage}
      kycVerifySubmitting={kycVerifySubmitting}
      onCreateKycProfile={handleCreateKycProfile}
      onUpdateKycProfile={handleUpdateKycProfile}
      onUploadKycDocument={handleUploadKycDocument}
      onVerifyKycDocument={handleVerifyKycDocument}
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
  landCropStatus?: LandCropStatus;
  landCropMessage?: string;
  landHoldings?: MemberLandHoldingDetail[];
  cropPlans?: MemberCropPlanDetail[];
  landCreateFieldErrors?: Record<string, string>;
  landCreateMessage?: string;
  landCreateSubmitting?: boolean;
  cropCreateFieldErrors?: Record<string, string>;
  cropCreateMessage?: string;
  cropCreateSubmitting?: boolean;
  onCreateLandHolding?: (payload: CreateMemberLandHoldingPayload) => void | Promise<void>;
  onCreateCropPlan?: (payload: CreateMemberCropPlanPayload) => void | Promise<void>;
  kycStatus?: KycStatus;
  kycMessage?: string;
  kycProfile?: KycProfileDetail | null;
  kycCreateFieldErrors?: Record<string, string>;
  kycCreateMessage?: string;
  kycCreateSubmitting?: boolean;
  kycDocumentFieldErrors?: Record<string, string>;
  kycDocumentMessage?: string;
  kycDocumentSubmitting?: boolean;
  kycVerifyFieldErrors?: Record<string, string>;
  kycVerifyMessage?: string;
  kycVerifySubmitting?: boolean;
  onCreateKycProfile?: (payload: CreateMemberKycProfilePayload) => void | Promise<void>;
  onUpdateKycProfile?: (payload: UpdateMemberKycProfilePayload) => void | Promise<void>;
  onUploadKycDocument?: (payload: UploadMemberKycDocumentPayload) => void | Promise<void>;
  onVerifyKycDocument?: (kycDocumentId: string, payload: VerifyMemberKycDocumentPayload) => void | Promise<void>;
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
  landCropStatus = 'idle',
  landCropMessage = '',
  landHoldings = [],
  cropPlans = [],
  landCreateFieldErrors = {},
  landCreateMessage = '',
  landCreateSubmitting = false,
  cropCreateFieldErrors = {},
  cropCreateMessage = '',
  cropCreateSubmitting = false,
  onCreateLandHolding,
  onCreateCropPlan,
  kycStatus = 'idle',
  kycMessage = '',
  kycProfile = null,
  kycCreateFieldErrors = {},
  kycCreateMessage = '',
  kycCreateSubmitting = false,
  kycDocumentFieldErrors = {},
  kycDocumentMessage = '',
  kycDocumentSubmitting = false,
  kycVerifyFieldErrors = {},
  kycVerifyMessage = '',
  kycVerifySubmitting = false,
  onCreateKycProfile,
  onUpdateKycProfile,
  onUploadKycDocument,
  onVerifyKycDocument,
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
        <LandTab
          status={landCropStatus}
          message={landCropMessage}
          landHoldings={landHoldings}
          cropPlans={cropPlans}
          landCreateFieldErrors={landCreateFieldErrors}
          landCreateMessage={landCreateMessage}
          landCreateSubmitting={landCreateSubmitting}
          cropCreateFieldErrors={cropCreateFieldErrors}
          cropCreateMessage={cropCreateMessage}
          cropCreateSubmitting={cropCreateSubmitting}
          onCreateLandHolding={onCreateLandHolding}
          onCreateCropPlan={onCreateCropPlan}
        />
        <KycTab
          profile={profile}
          status={kycStatus}
          message={kycMessage}
          kycProfile={kycProfile}
          createFieldErrors={kycCreateFieldErrors}
          createMessage={kycCreateMessage}
          createSubmitting={kycCreateSubmitting}
          documentFieldErrors={kycDocumentFieldErrors}
          documentMessage={kycDocumentMessage}
          documentSubmitting={kycDocumentSubmitting}
          verifyFieldErrors={kycVerifyFieldErrors}
          verifyMessage={kycVerifyMessage}
          verifySubmitting={kycVerifySubmitting}
          onCreateKycProfile={onCreateKycProfile}
          onUpdateKycProfile={onUpdateKycProfile}
          onUploadKycDocument={onUploadKycDocument}
          onVerifyKycDocument={onVerifyKycDocument}
        />
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
  <OverviewPanel profile={profile} />
);

const OverviewPanel: React.FC<{ profile: MemberProfileDetail }> = ({ profile }) => {
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
      setMessages(current => ({
        ...current,
        [fieldName]: error instanceof Error ? error.message : 'Sensitive value could not be revealed.',
      }));
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
    </div>
  );
};

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

const LandTab: React.FC<{
  status: LandCropStatus;
  message: string;
  landHoldings: MemberLandHoldingDetail[];
  cropPlans: MemberCropPlanDetail[];
  landCreateFieldErrors: Record<string, string>;
  landCreateMessage: string;
  landCreateSubmitting: boolean;
  cropCreateFieldErrors: Record<string, string>;
  cropCreateMessage: string;
  cropCreateSubmitting: boolean;
  onCreateLandHolding?: (payload: CreateMemberLandHoldingPayload) => void | Promise<void>;
  onCreateCropPlan?: (payload: CreateMemberCropPlanPayload) => void | Promise<void>;
}> = ({
  status,
  message,
  landHoldings,
  cropPlans,
  landCreateFieldErrors,
  landCreateMessage,
  landCreateSubmitting,
  cropCreateFieldErrors,
  cropCreateMessage,
  cropCreateSubmitting,
  onCreateLandHolding,
  onCreateCropPlan,
}) => (
  <div className="card space-y-5">
    <div className="flex items-center justify-between gap-3">
      <h3 className="font-semibold text-slate-800">Land & Crop Evidence</h3>
      <StatusBadge label={landHoldings.length + cropPlans.length > 0 ? `${landHoldings.length + cropPlans.length} recorded` : 'pending'} size="sm" />
    </div>
    {landCreateMessage && (
      <AlertBanner
        type={Object.keys(landCreateFieldErrors).length > 0 ? 'error' : 'success'}
        title={Object.keys(landCreateFieldErrors).length > 0 ? 'Land holding validation failed' : 'Land holding update'}
        message={landCreateMessage}
      />
    )}
    {cropCreateMessage && (
      <AlertBanner
        type={Object.keys(cropCreateFieldErrors).length > 0 ? 'error' : 'success'}
        title={Object.keys(cropCreateFieldErrors).length > 0 ? 'Crop plan validation failed' : 'Crop plan update'}
        message={cropCreateMessage}
      />
    )}
    <LandCropState status={status} message={message} landHoldings={landHoldings} cropPlans={cropPlans} />
    <div className="grid grid-cols-1 xl:grid-cols-2 gap-5 border-t border-slate-100 pt-4">
      <LandHoldingCreateForm
        fieldErrors={landCreateFieldErrors}
        submitting={landCreateSubmitting}
        onCreateLandHolding={onCreateLandHolding}
      />
      <CropPlanCreateForm
        fieldErrors={cropCreateFieldErrors}
        submitting={cropCreateSubmitting}
        onCreateCropPlan={onCreateCropPlan}
      />
    </div>
  </div>
);

const LandCropState: React.FC<{
  status: LandCropStatus;
  message: string;
  landHoldings: MemberLandHoldingDetail[];
  cropPlans: MemberCropPlanDetail[];
}> = ({ status, message, landHoldings, cropPlans }) => {
  if (status === 'idle' || status === 'loading') {
    return <EmptyPanel icon={<Clock size={18} className="text-slate-500 flex-shrink-0" />} title="Loading land and crop records" />;
  }
  if (status === 'unauthorized' || status === 'forbidden' || status === 'error') {
    return <EmptyPanel icon={<AlertTriangle size={18} className="text-slate-500 flex-shrink-0" />} title={message || 'Land and crop records could not be loaded.'} />;
  }
  if (status === 'empty' || (landHoldings.length === 0 && cropPlans.length === 0)) {
    return <EmptyPanel icon={<FileText size={18} className="text-slate-500 flex-shrink-0" />} title={message || 'No land or crop records are available from the backend yet.'} />;
  }
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <div className="space-y-3">
        <p className="text-xs text-slate-500 font-semibold uppercase tracking-wide">Land Holdings</p>
        {landHoldings.length === 0 && <EmptyPanel icon={<FileText size={18} className="text-slate-500 flex-shrink-0" />} title="No land holding records are available from the backend yet." />}
        {landHoldings.map(land => (
          <div key={land.land_holding_id} className="bg-slate-50 border border-slate-200 rounded-lg p-4 space-y-3">
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="text-sm font-semibold text-slate-900">{land.survey_number || 'Survey number not recorded'}</p>
                <p className="text-xs text-slate-500 mt-0.5">{land.village || '-'} · {land.taluka || '-'} · {land.district || '-'}</p>
              </div>
              <StatusBadge label={land.verification_status || 'pending'} size="sm" />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <InfoTile label="Document Type" value={land.document_type || '-'} />
              <InfoTile label="Area" value={`${land.area_acres} acres`} />
              <InfoTile label="State" value={land.state || '-'} />
              <InfoTile label="Document ID" value={land.document_id} />
            </div>
          </div>
        ))}
      </div>
      <div className="space-y-3">
        <p className="text-xs text-slate-500 font-semibold uppercase tracking-wide">Crop Plans</p>
        {cropPlans.length === 0 && <EmptyPanel icon={<FileText size={18} className="text-slate-500 flex-shrink-0" />} title="No crop plan records are available from the backend yet." />}
        {cropPlans.map(crop => (
          <div key={crop.crop_plan_id} className="bg-slate-50 border border-slate-200 rounded-lg p-4 space-y-3">
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="text-sm font-semibold text-slate-900">{crop.crop_type}</p>
                <p className="text-xs text-slate-500 mt-0.5">{crop.season || 'Season not recorded'} · {crop.loan_purpose_alignment}</p>
              </div>
              <StatusBadge label={crop.verification_status || 'pending'} size="sm" />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <InfoTile label="Planned Area" value={`${crop.planned_area_acres} acres`} />
              <InfoTile label="Estimated Cost" value={crop.estimated_cost_amount || '-'} />
              <InfoTile label="Document ID" value={crop.document_id || '-'} />
              <InfoTile label="Application ID" value={crop.loan_application_id || '-'} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

const LandHoldingCreateForm: React.FC<{
  fieldErrors: Record<string, string>;
  submitting: boolean;
  onCreateLandHolding?: (payload: CreateMemberLandHoldingPayload) => void | Promise<void>;
}> = ({ fieldErrors, submitting, onCreateLandHolding }) => {
  const [form, setForm] = useState<CreateMemberLandHoldingPayload>({
    document_type: '7_12_extract',
    survey_number: '',
    village: '',
    taluka: '',
    district: '',
    state: '',
    area_acres: '',
    document_id: '',
  });
  const setField = (field: keyof CreateMemberLandHoldingPayload, value: string) => {
    setForm(current => ({ ...current, [field]: value }));
  };
  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    await onCreateLandHolding?.(form);
  };
  return (
    <form className="space-y-4" onSubmit={submit}>
      <h4 className="text-sm font-semibold text-slate-800">Add Land Holding</h4>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <Field label="Document type" error={fieldErrors.document_type}>
          <input className="field-input" value={form.document_type} onChange={event => setField('document_type', event.target.value)} />
        </Field>
        <Field label="Survey number" error={fieldErrors.survey_number}>
          <input className="field-input" value={form.survey_number} onChange={event => setField('survey_number', event.target.value)} />
        </Field>
        <Field label="Village" error={fieldErrors.village}>
          <input className="field-input" value={form.village} onChange={event => setField('village', event.target.value)} />
        </Field>
        <Field label="Taluka" error={fieldErrors.taluka}>
          <input className="field-input" value={form.taluka} onChange={event => setField('taluka', event.target.value)} />
        </Field>
        <Field label="District" error={fieldErrors.district}>
          <input className="field-input" value={form.district} onChange={event => setField('district', event.target.value)} />
        </Field>
        <Field label="State" error={fieldErrors.state}>
          <input className="field-input" value={form.state} onChange={event => setField('state', event.target.value)} />
        </Field>
        <Field label="Area acres" error={fieldErrors.area_acres}>
          <input className="field-input" value={form.area_acres} onChange={event => setField('area_acres', event.target.value)} />
        </Field>
        <Field label="Document ID" error={fieldErrors.document_id}>
          <input className="field-input" value={form.document_id} onChange={event => setField('document_id', event.target.value)} />
        </Field>
      </div>
      <button className="btn-primary" disabled={submitting || !onCreateLandHolding} type="submit">
        {submitting ? 'Saving land holding' : 'Save land holding'}
      </button>
    </form>
  );
};

const CropPlanCreateForm: React.FC<{
  fieldErrors: Record<string, string>;
  submitting: boolean;
  onCreateCropPlan?: (payload: CreateMemberCropPlanPayload) => void | Promise<void>;
}> = ({ fieldErrors, submitting, onCreateCropPlan }) => {
  const [form, setForm] = useState<CreateMemberCropPlanPayload>({
    loan_application_id: '',
    crop_type: '',
    season: '',
    planned_area_acres: '',
    estimated_cost_amount: '',
    loan_purpose_alignment: 'agriculture_aligned',
    document_id: '',
  });
  const setField = (field: keyof CreateMemberCropPlanPayload, value: string) => {
    setForm(current => ({ ...current, [field]: value }));
  };
  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    await onCreateCropPlan?.(form);
  };
  return (
    <form className="space-y-4" onSubmit={submit}>
      <h4 className="text-sm font-semibold text-slate-800">Add Crop Plan</h4>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <Field label="Loan application ID" error={fieldErrors.loan_application_id}>
          <input className="field-input" value={form.loan_application_id} onChange={event => setField('loan_application_id', event.target.value)} />
        </Field>
        <Field label="Crop type" error={fieldErrors.crop_type}>
          <input className="field-input" value={form.crop_type} onChange={event => setField('crop_type', event.target.value)} />
        </Field>
        <Field label="Season" error={fieldErrors.season}>
          <input className="field-input" value={form.season} onChange={event => setField('season', event.target.value)} />
        </Field>
        <Field label="Planned area acres" error={fieldErrors.planned_area_acres}>
          <input className="field-input" value={form.planned_area_acres} onChange={event => setField('planned_area_acres', event.target.value)} />
        </Field>
        <Field label="Estimated cost amount" error={fieldErrors.estimated_cost_amount}>
          <input className="field-input" value={form.estimated_cost_amount} onChange={event => setField('estimated_cost_amount', event.target.value)} />
        </Field>
        <Field label="Purpose alignment" error={fieldErrors.loan_purpose_alignment}>
          <input className="field-input" value={form.loan_purpose_alignment} onChange={event => setField('loan_purpose_alignment', event.target.value)} />
        </Field>
        <Field label="Document ID" error={fieldErrors.document_id}>
          <input className="field-input" value={form.document_id} onChange={event => setField('document_id', event.target.value)} />
        </Field>
      </div>
      <button className="btn-primary" disabled={submitting || !onCreateCropPlan} type="submit">
        {submitting ? 'Saving crop plan' : 'Save crop plan'}
      </button>
    </form>
  );
};

const KycTab: React.FC<{
  profile: MemberProfileDetail;
  status: KycStatus;
  message: string;
  kycProfile: KycProfileDetail | null;
  createFieldErrors: Record<string, string>;
  createMessage: string;
  createSubmitting: boolean;
  documentFieldErrors: Record<string, string>;
  documentMessage: string;
  documentSubmitting: boolean;
  verifyFieldErrors: Record<string, string>;
  verifyMessage: string;
  verifySubmitting: boolean;
  onCreateKycProfile?: (payload: CreateMemberKycProfilePayload) => void | Promise<void>;
  onUpdateKycProfile?: (payload: UpdateMemberKycProfilePayload) => void | Promise<void>;
  onUploadKycDocument?: (payload: UploadMemberKycDocumentPayload) => void | Promise<void>;
  onVerifyKycDocument?: (kycDocumentId: string, payload: VerifyMemberKycDocumentPayload) => void | Promise<void>;
}> = ({
  profile,
  status,
  message,
  kycProfile,
  createFieldErrors,
  createMessage,
  createSubmitting,
  documentFieldErrors,
  documentMessage,
  documentSubmitting,
  verifyFieldErrors,
  verifyMessage,
  verifySubmitting,
  onCreateKycProfile,
  onUpdateKycProfile,
  onUploadKycDocument,
  onVerifyKycDocument,
}) => (
  <div className="card space-y-5">
    <div className="flex items-center justify-between gap-3">
      <h3 className="font-semibold text-slate-800">KYC Profile</h3>
      <StatusBadge label={kycProfile?.kyc_status || profile.kyc_status || 'pending'} family={(kycProfile?.kyc_status || profile.kyc_status) === 'verified' ? 'approved' : undefined} />
    </div>
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <SensitiveTile label="PAN" value={profile.pan.masked} />
      <SensitiveTile label="Aadhaar" value={profile.aadhaar.masked} />
    </div>
    {createMessage && (
      <AlertBanner
        type={Object.keys(createFieldErrors).length > 0 ? 'error' : 'success'}
        title={Object.keys(createFieldErrors).length > 0 ? 'KYC profile validation failed' : 'KYC profile update'}
        message={createMessage}
      />
    )}
    {documentMessage && (
      <AlertBanner
        type={Object.keys(documentFieldErrors).length > 0 ? 'error' : 'success'}
        title={Object.keys(documentFieldErrors).length > 0 ? 'KYC document validation failed' : 'KYC document update'}
        message={documentMessage}
      />
    )}
    {verifyMessage && (
      <AlertBanner
        type={Object.keys(verifyFieldErrors).length > 0 ? 'error' : 'success'}
        title={Object.keys(verifyFieldErrors).length > 0 ? 'KYC verification failed' : 'KYC verification update'}
        message={verifyMessage}
      />
    )}
    <KycProfileState status={status} message={message} kycProfile={kycProfile} />
    <KycProfileForm
      kycProfile={kycProfile}
      fieldErrors={createFieldErrors}
      submitting={createSubmitting}
      onCreateKycProfile={onCreateKycProfile}
      onUpdateKycProfile={onUpdateKycProfile}
    />
    {kycProfile && (
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-5 border-t border-slate-100 pt-4">
        <KycDocumentUploadForm
          fieldErrors={documentFieldErrors}
          submitting={documentSubmitting}
          onUploadKycDocument={onUploadKycDocument}
        />
        <KycDocumentVerifyForm
          documents={kycProfile.documents}
          fieldErrors={verifyFieldErrors}
          submitting={verifySubmitting}
          onVerifyKycDocument={onVerifyKycDocument}
        />
      </div>
    )}
  </div>
);

const KycProfileState: React.FC<{
  status: KycStatus;
  message: string;
  kycProfile: KycProfileDetail | null;
}> = ({ status, message, kycProfile }) => {
  if (status === 'idle' || status === 'loading') {
    return <EmptyPanel icon={<Clock size={18} className="text-slate-500 flex-shrink-0" />} title="Loading KYC records" />;
  }
  if (status === 'unauthorized' || status === 'forbidden' || status === 'error') {
    return <EmptyPanel icon={<AlertTriangle size={18} className="text-slate-500 flex-shrink-0" />} title={message || 'KYC records could not be loaded.'} />;
  }
  if (status === 'empty' || !kycProfile) {
    return <EmptyPanel icon={<Shield size={18} className="text-slate-500 flex-shrink-0" />} title={message || 'No KYC profile is available from the backend yet.'} />;
  }
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <InfoTile label="CKYC Consent" value={kycProfile.ckyc_consent_flag ? 'Yes' : 'No'} />
        <InfoTile label="Beneficial Ownership" value={kycProfile.beneficial_ownership_verified_flag === null ? '-' : kycProfile.beneficial_ownership_verified_flag ? 'Yes' : 'No'} />
        <InfoTile label="Risk Rating" value={titleCase(kycProfile.risk_rating || '-')} />
        <InfoTile label="Re-KYC Due" value={formatDate(kycProfile.rekyc_due_date)} />
      </div>
      <div className="space-y-3">
        <p className="text-xs text-slate-500 font-semibold uppercase tracking-wide">KYC Documents</p>
        {kycProfile.documents.length === 0 && <EmptyPanel icon={<FileText size={18} className="text-slate-500 flex-shrink-0" />} title="No KYC document records are available from the backend yet." />}
        {kycProfile.documents.map(document => (
          <div key={document.kyc_document_id} className="bg-slate-50 border border-slate-200 rounded-lg p-4 space-y-3">
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="text-sm font-semibold text-slate-900">{document.file_name || document.document_type}</p>
                <p className="text-xs text-slate-500 mt-0.5">
                  {titleCase(document.document_type)} · {document.self_attested_flag ? 'Self Attested' : 'Not self attested'}
                </p>
              </div>
              <StatusBadge label={document.verification_status || 'pending'} size="sm" family={document.verification_status === 'verified' ? 'approved' : undefined} />
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <InfoTile label="Document ID" value={document.document_id} />
              <InfoTile label="Sensitivity" value={titleCase(document.sensitivity_level)} />
              <InfoTile label="File Size" value={document.file_size_bytes === null ? '-' : `${document.file_size_bytes} bytes`} />
              <InfoTile label="Remarks" value={document.remarks || '-'} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

const KycProfileForm: React.FC<{
  kycProfile: KycProfileDetail | null;
  fieldErrors: Record<string, string>;
  submitting: boolean;
  onCreateKycProfile?: (payload: CreateMemberKycProfilePayload) => void | Promise<void>;
  onUpdateKycProfile?: (payload: UpdateMemberKycProfilePayload) => void | Promise<void>;
}> = ({ kycProfile, fieldErrors, submitting, onCreateKycProfile, onUpdateKycProfile }) => {
  const [form, setForm] = useState<CreateMemberKycProfilePayload>({
    ckyc_consent_flag: kycProfile?.ckyc_consent_flag ?? true,
    beneficial_ownership_verified_flag: kycProfile?.beneficial_ownership_verified_flag ?? false,
    risk_rating: kycProfile?.risk_rating ?? 'low',
  });
  const setField = (field: keyof CreateMemberKycProfilePayload, value: string | boolean) => {
    setForm(current => ({ ...current, [field]: value }));
  };
  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (kycProfile) {
      await onUpdateKycProfile?.(form);
    } else {
      await onCreateKycProfile?.(form);
    }
  };
  return (
    <form className="border-t border-slate-100 pt-4 space-y-4" onSubmit={submit}>
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Field label="Risk rating" error={fieldErrors.risk_rating}>
          <select className="field-select" value={form.risk_rating} onChange={event => setField('risk_rating', event.target.value)}>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
        </Field>
        <label className="flex items-center gap-2 text-sm text-slate-700 pt-6">
          <input
            type="checkbox"
            className="accent-green-600"
            checked={form.ckyc_consent_flag}
            onChange={event => setField('ckyc_consent_flag', event.target.checked)}
          />
          CKYC consent
        </label>
        <label className="flex items-center gap-2 text-sm text-slate-700 pt-6">
          <input
            type="checkbox"
            className="accent-green-600"
            checked={form.beneficial_ownership_verified_flag}
            onChange={event => setField('beneficial_ownership_verified_flag', event.target.checked)}
          />
          Beneficial ownership verified
        </label>
      </div>
      {fieldErrors.ckyc_consent_flag && <span className="text-xs text-red-600 block">{fieldErrors.ckyc_consent_flag}</span>}
      <button className="btn-primary" disabled={submitting || (!kycProfile && !onCreateKycProfile) || (Boolean(kycProfile) && !onUpdateKycProfile)} type="submit">
        {submitting ? 'Saving KYC profile' : 'Save KYC profile'}
      </button>
    </form>
  );
};

const KycDocumentUploadForm: React.FC<{
  fieldErrors: Record<string, string>;
  submitting: boolean;
  onUploadKycDocument?: (payload: UploadMemberKycDocumentPayload) => void | Promise<void>;
}> = ({ fieldErrors, submitting, onUploadKycDocument }) => {
  const [documentType, setDocumentType] = useState('pan');
  const [selfAttested, setSelfAttested] = useState(true);
  const [file, setFile] = useState<Blob | null>(null);
  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!file) return;
    await onUploadKycDocument?.({ document_type: documentType, self_attested_flag: selfAttested, file });
  };
  return (
    <form className="space-y-4" onSubmit={submit}>
      <h4 className="text-sm font-semibold text-slate-800">Upload KYC Document</h4>
      <Field label="Document type" error={fieldErrors.document_type}><select className="field-select" value={documentType} onChange={event => setDocumentType(event.target.value)}><option value="pan">PAN</option><option value="aadhaar">Aadhaar</option><option value="photo">Photo</option><option value="ckyc_consent">CKYC Consent</option></select></Field>
      <Field label="File" error={fieldErrors.file}><input className="field-input" type="file" onChange={event => setFile(event.target.files?.[0] ?? null)} /></Field>
      <label className="flex items-center gap-2 text-sm text-slate-700">
        <input type="checkbox" className="accent-green-600" checked={selfAttested} onChange={event => setSelfAttested(event.target.checked)} />
        Self attested
      </label>
      {fieldErrors.self_attested_flag && <span className="text-xs text-red-600 block">{fieldErrors.self_attested_flag}</span>}
      <button className="btn-primary" disabled={submitting || !onUploadKycDocument} type="submit">
        {submitting ? 'Uploading KYC document' : 'Upload KYC document'}
      </button>
    </form>
  );
};

const KycDocumentVerifyForm: React.FC<{
  documents: KycDocumentDetail[];
  fieldErrors: Record<string, string>;
  submitting: boolean;
  onVerifyKycDocument?: (kycDocumentId: string, payload: VerifyMemberKycDocumentPayload) => void | Promise<void>;
}> = ({ documents, fieldErrors, submitting, onVerifyKycDocument }) => {
  const [documentId, setDocumentId] = useState(documents[0]?.kyc_document_id ?? '');
  const [verificationStatus, setVerificationStatus] = useState<'verified' | 'rejected'>('verified');
  const [remarks, setRemarks] = useState('');
  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!documentId) return;
    await onVerifyKycDocument?.(documentId, { verification_status: verificationStatus, remarks });
  };
  return (
    <form className="space-y-4" onSubmit={submit}>
      <h4 className="text-sm font-semibold text-slate-800">Verify KYC Document</h4>
      <Field label="Document" error={fieldErrors.kyc_document_id}><select className="field-select" value={documentId} onChange={event => setDocumentId(event.target.value)}>{documents.map(document => <option key={document.kyc_document_id} value={document.kyc_document_id}>{document.file_name || document.document_type}</option>)}</select></Field>
      <Field label="Verification status" error={fieldErrors.verification_status}><select className="field-select" value={verificationStatus} onChange={event => setVerificationStatus(event.target.value as 'verified' | 'rejected')}><option value="verified">Verified</option><option value="rejected">Rejected</option></select></Field>
      <Field label="Remarks" error={fieldErrors.remarks}><input className="field-input" value={remarks} onChange={event => setRemarks(event.target.value)} /></Field>
      <button className="btn-primary" disabled={submitting || !onVerifyKycDocument || documents.length === 0} type="submit">
        {submitting ? 'Saving verification' : 'Save verification'}
      </button>
    </form>
  );
};

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
          <button
            className="btn-secondary text-xs inline-flex items-center gap-1"
            disabled={submitting}
            onClick={revealed ? onHide : onReveal}
            type="button"
          >
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
const formatDateTime = (value: string | null) => (value ? new Date(value).toLocaleString('en-IN') : '-');
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
