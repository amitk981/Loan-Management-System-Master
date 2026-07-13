import React, { useEffect, useState } from 'react';
import { Search, Users, AlertTriangle, RefreshCw, Eye, Clock } from 'lucide-react';
import StatusBadge from '../../components/ui/StatusBadge';
import { useRole } from '../../contexts/RoleContext';
import { AuthSessionError } from '../../services/authSession';
import {
  fetchMemberDirectory,
  type MemberDirectoryItem,
} from '../../services/memberDirectoryApi';
import MemberGovernanceForm from './MemberGovernanceForm';

type DirectoryStatus = 'loading' | 'success' | 'forbidden' | 'unauthorized' | 'error';
type KycFilter = 'all' | 'verified' | 'rekyc_due' | 'missing' | 'pending';
type TypeFilter = 'all' | 'individual_farmer' | 'fpc' | 'producer_institution';

interface MemberDirectoryProps {
  onSelect: (memberId: string) => void;
  onBorrower360?: (memberId: string) => void;
}

const MemberDirectory: React.FC<MemberDirectoryProps> = ({ onSelect }) => {
  const { can, currentUser } = useRole();
  const [showCreate, setShowCreate] = useState(false);
  const [search, setSearch] = useState('');
  const [kycFilter, setKycFilter] = useState<KycFilter>('all');
  const [typeFilter, setTypeFilter] = useState<TypeFilter>('all');
  const [status, setStatus] = useState<DirectoryStatus>('loading');
  const [message, setMessage] = useState('');
  const [members, setMembers] = useState<MemberDirectoryItem[]>([]);

  useEffect(() => {
    let cancelled = false;
    setStatus('loading');
    setMessage('');

    fetchMemberDirectory({
      search,
      kycStatus: kycFilter,
      memberType: typeFilter,
    })
      .then(result => {
        if (cancelled) return;
        setMembers(result.items);
        setStatus('success');
      })
      .catch(error => {
        if (cancelled) return;
        const next = memberDirectoryErrorState(error);
        setStatus(next.status);
        setMessage(next.message);
        setMembers([]);
      });

    return () => {
      cancelled = true;
    };
  }, [search, kycFilter, typeFilter]);

  return <>
    {showCreate && <div className="p-6 pb-0"><MemberGovernanceForm onSaved={member => onSelect(member.member_id)} onCancel={() => setShowCreate(false)} /></div>}
    <MemberDirectoryView
      status={status}
      message={message}
      members={members}
      search={search}
      kycFilter={kycFilter}
      typeFilter={typeFilter}
      onSearchChange={setSearch}
      onKycFilterChange={setKycFilter}
      onTypeFilterChange={setTypeFilter}
      onSelect={onSelect}
      canViewMembers={can('view_members')}
      canCreateMember={currentUser.permissions.includes('members.member.create')}
      onCreate={() => setShowCreate(true)}
    />
  </>;
};

interface MemberDirectoryViewProps {
  status: DirectoryStatus;
  message?: string;
  members: MemberDirectoryItem[];
  search: string;
  kycFilter: KycFilter;
  typeFilter: TypeFilter;
  onSearchChange: (value: string) => void;
  onKycFilterChange: (value: KycFilter) => void;
  onTypeFilterChange: (value: TypeFilter) => void;
  onSelect: (memberId: string) => void;
  canViewMembers: boolean;
  canCreateMember?: boolean;
  onCreate?: () => void;
}

export const MemberDirectoryView: React.FC<MemberDirectoryViewProps> = ({
  status,
  message,
  members,
  search,
  kycFilter,
  typeFilter,
  onSearchChange,
  onKycFilterChange,
  onTypeFilterChange,
  onSelect,
  canViewMembers,
  canCreateMember,
  onCreate,
}) => {
  const reKycCount = members.filter(m => m.kyc_status === 'rekyc_due').length;

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Member Directory</h1>
          <p className="text-sm text-slate-500 mt-0.5">{members.length} members</p>
        </div>
        <div className="flex items-center gap-2">
        {canCreateMember && <button className="btn-primary text-sm" onClick={onCreate}>Register Member</button>}
        {reKycCount > 0 && (
          <div className="flex items-center gap-2 text-sm text-amber-700 bg-amber-50 border border-amber-200 rounded-lg px-3 py-2">
            <RefreshCw size={14} />
            {reKycCount} member{reKycCount > 1 ? 's' : ''} have Re-KYC blockers
          </div>
        )}
        </div>
      </div>

      <div className="flex flex-wrap gap-3">
        <div className="relative flex-1 min-w-48 max-w-sm">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search by name or folio..."
            value={search}
            onChange={e => onSearchChange(e.target.value)}
            className="field-input pl-8 py-2 text-sm"
          />
        </div>
        <select
          value={kycFilter}
          onChange={e => onKycFilterChange(e.target.value as KycFilter)}
          className="field-select py-2 text-sm"
        >
          <option value="all">All KYC statuses</option>
          <option value="verified">Verified</option>
          <option value="rekyc_due">Re-KYC Due</option>
          <option value="missing">Missing</option>
          <option value="pending">Pending</option>
        </select>
        <select
          value={typeFilter}
          onChange={e => onTypeFilterChange(e.target.value as TypeFilter)}
          className="field-select py-2 text-sm"
        >
          <option value="all">All types</option>
          <option value="individual_farmer">Individual</option>
          <option value="fpc">FPC</option>
          <option value="producer_institution">Producer Institution</option>
        </select>
      </div>

      <div className="card p-0 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50">
                <th className="table-header text-left">Member</th>
                <th className="table-header text-left">Folio / Type</th>
                <th className="table-header text-right">Shares</th>
                <th className="table-header text-left">KYC Status</th>
                <th className="table-header text-left">Active Status</th>
                <th className="table-header text-left">Default</th>
                <th className="table-header text-left">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {status === 'loading' ? (
                <DirectoryMessage colSpan={7} icon={<Clock size={24} />} title="Loading members" />
              ) : status !== 'success' ? (
                <DirectoryMessage
                  colSpan={7}
                  icon={<Users size={24} />}
                  title="Member directory unavailable"
                  message={message || 'Members could not be loaded.'}
                />
              ) : members.length === 0 ? (
                <DirectoryMessage colSpan={7} icon={<Users size={24} />} title="No members found." />
              ) : (
                members.map(member => (
                  <tr
                    key={member.member_id}
                    onClick={() => onSelect(member.member_id)}
                    className="hover:bg-slate-50 cursor-pointer transition-colors"
                  >
                    <td className="table-cell">
                      <div className="flex items-center gap-2">
                        <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center flex-shrink-0">
                          <Users size={14} className="text-green-700" />
                        </div>
                        <div>
                          <div className="font-semibold text-slate-900">{member.display_name}</div>
                          <div className="text-xs text-slate-400">{member.member_number || member.member_id}</div>
                          <div className="text-xs text-slate-400">{contactLabel(member)}</div>
                        </div>
                      </div>
                    </td>
                    <td className="table-cell">
                      <div className="font-medium text-slate-700 num">{member.folio_number}</div>
                      <div className="text-xs text-slate-400 capitalize">{memberTypeLabel(member.member_type)}</div>
                    </td>
                    <td className="table-cell text-right num">
                      <div>{formatCount(member.share_summary.number_of_shares)}</div>
                      <div className="text-xs text-slate-400 capitalize">{member.share_summary.holding_mode || 'Unknown'}</div>
                    </td>
                    <td className="table-cell">
                      <StatusBadge label={member.kyc_status} size="sm" />
                    </td>
                    <td className="table-cell">
                      <StatusBadge label={activeStatusBadgeLabel(member)} size="sm" />
                    </td>
                    <td className="table-cell">
                      {member.default_status !== 'no_default' ? (
                        <span className={`flex items-center gap-1 text-xs ${member.default_status === 'existing_default' ? 'text-red-600' : 'text-amber-600'}`}>
                          <AlertTriangle size={12} />
                          {member.default_status === 'existing_default' ? 'Existing default' : 'Past default'}
                        </span>
                      ) : (
                        <span className="text-xs text-green-600">None</span>
                      )}
                    </td>
                    <td className="table-cell">
                      <div className="flex items-center gap-1" onClick={e => e.stopPropagation()}>
                        {canViewMembers && (
                          <button
                            onClick={() => onSelect(member.member_id)}
                            className="flex items-center gap-1 text-xs text-green-700 hover:text-green-900 px-2 py-1 rounded hover:bg-green-50 transition-colors"
                            title="Member Profile"
                          >
                            <Eye size={12} /> Profile
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

const DirectoryMessage: React.FC<{
  colSpan: number;
  icon: React.ReactNode;
  title: string;
  message?: string;
}> = ({ colSpan, icon, title, message }) => (
  <tr>
    <td colSpan={colSpan} className="table-cell text-center text-slate-400 py-12">
      <div className="mx-auto text-slate-300 mb-3 flex justify-center">{icon}</div>
      <p className="text-sm font-semibold text-slate-700">{title}</p>
      {message && <p className="text-xs text-slate-500 mt-1">{message}</p>}
    </td>
  </tr>
);

const memberDirectoryErrorState = (error: unknown): { status: DirectoryStatus; message: string } => {
  if (error instanceof AuthSessionError) {
    if (error.status === 401) return { status: 'unauthorized', message: error.message };
    if (error.status === 403) return { status: 'forbidden', message: error.message };
  }
  return {
    status: 'error',
    message: error instanceof Error ? error.message : 'Members could not be loaded.',
  };
};

const formatCount = (value: number | null) => (
  value === null ? '-' : value.toLocaleString('en-IN')
);

const memberTypeLabel = (value: string) => {
  if (value === 'fpc') return 'FPC';
  return value.replace(/_/g, ' ');
};

const contactLabel = (member: MemberDirectoryItem) => (
  [member.email, member.mobile_number].filter(Boolean).join(' / ') || 'Contact not available'
);

const activeStatusBadgeLabel = (member: MemberDirectoryItem) => {
  const status = member.active_member_status.status || member.membership_status;
  if (status === 'active') return 'active_member';
  if (status === 'inactive') return 'inactive_member';
  return status;
};

export default MemberDirectory;
