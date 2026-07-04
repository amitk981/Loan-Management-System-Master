import React, { useEffect, useMemo, useState } from 'react';
import {
  AlertTriangle, ArrowRight, CheckCircle2, ClipboardList, Eye,
  FileText, Info, MessageSquare, RefreshCw, Send, X, XCircle
} from 'lucide-react';
import StatusBadge from '../../components/ui/StatusBadge';
import { useRole } from '../../contexts/RoleContext';
import { documents, loanApplications, members } from '../../data/mockData';
import { COMPLETENESS_CATEGORIES, COMPLETENESS_ITEMS, getNextLoanReference } from './completenessChecklist';
import { getApplicationReference, getApplicationStatusLabel, hasFormalLoanReference } from '../../utils/applicationDisplay';
import type { DocumentType } from '../../types';

const fmt = (n: number) => '₹' + n.toLocaleString('en-IN');

type CheckState = 'pending' | 'complete' | 'deficient';
type Outcome = null | 'reference_generated' | 'returned' | 'rejected';

interface CompletenessWorkbenchProps {
  initialSelectedId?: string;
  onOpenApplication: (id: string) => void;
  onOpenAppraisal: (id: string) => void;
}

const seededDeficiencies: Record<string, string[]> = {
  app007: ['nominee_signature', 'nominee_fields', 'crop_plan'],
  app016: ['borrower_kyc', 'land_712'],
};

const getQueueStatusLabel = (itemStatus: string, label: string) => {
  if (itemStatus === 'submitted') return 'Pending Completeness';
  if (itemStatus === 'deficiency_raised' || itemStatus === 'returned_for_rectification' || itemStatus === 'incomplete') {
    return 'Returned for Rectification';
  }
  return label;
};

const getInitialChecks = (applicationId: string, shareMode: string): Record<string, CheckState> => {
  const deficient = new Set(seededDeficiencies[applicationId] || []);
  return COMPLETENESS_ITEMS.reduce<Record<string, CheckState>>((acc, item) => {
    if (item.id === 'share_certificate' && shareMode !== 'physical') {
      acc[item.id] = 'complete';
    } else if (deficient.has(item.id)) {
      acc[item.id] = 'deficient';
    } else {
      acc[item.id] = applicationId === 'app015' ? 'pending' : 'complete';
    }
    return acc;
  }, {});
};

const DOC_UPLOADED_STATUSES = new Set(['uploaded', 'verified', 'complete', 'under_review', 'signed']);

type ItemData =
  | { type: 'field'; value: string; ok: boolean }
  | { type: 'manual'; hint: string }
  | { type: 'docs'; docs: { label: string; docType: DocumentType }[] };

const CompletenessWorkbench: React.FC<CompletenessWorkbenchProps> = ({
  initialSelectedId,
  onOpenApplication,
  onOpenAppraisal,
}) => {
  const { currentUser, can } = useRole();
  const queue = loanApplications.filter(app =>
    ['submitted', 'incomplete', 'deficiency_raised', 'returned_for_rectification'].includes(app.status)
  );
  const initialApp = initialSelectedId
    ? queue.find(app =>
      app.id === initialSelectedId ||
      app.applicationNumber === initialSelectedId ||
      app.intakeReference === initialSelectedId ||
      app.officialReference === initialSelectedId
    )
    : queue[0];

  const [selectedId, setSelectedId] = useState<string | null>(initialApp?.id || null);
  const app = queue.find(a => a.id === selectedId) || queue[0];
  const member = app ? members.find(m => m.id === app.memberId) : null;
  const appDocs = app ? documents.filter(d => d.applicationId === app.id) : [];
  const [checks, setChecks] = useState<Record<string, CheckState>>({});
  const [reasons, setReasons] = useState<Record<string, string>>({});
  const [internalComment, setInternalComment] = useState('');
  const [outcome, setOutcome] = useState<Outcome>(null);
  const [viewingDoc, setViewingDoc] = useState<{ label: string; status: string; fileName?: string } | null>(null);

  const generatedReference = useMemo(
    () => getNextLoanReference(
      loanApplications
        .filter(hasFormalLoanReference)
        .map(application => application.officialReference || application.applicationNumber)
    ),
    []
  );

  useEffect(() => {
    if (!app) return;
    const nextChecks = getInitialChecks(app.id, app.shareMode);
    setChecks(nextChecks);
    setReasons(
      COMPLETENESS_ITEMS.reduce<Record<string, string>>((acc, item) => {
        if (nextChecks[item.id] === 'deficient') acc[item.id] = item.deficiencyReason;
        return acc;
      }, {})
    );
    setInternalComment(app.status === 'deficiency_raised' ? 'Borrower may resubmit after rectification.' : '');
    setOutcome(null);
  }, [app]);

  const canAct = can('do_completeness_check') && currentUser.role === 'deputy_manager_finance';
  const reviewableItems = COMPLETENESS_ITEMS.filter(item => !(item.id === 'share_certificate' && app?.shareMode !== 'physical'));
  const deficientItems = reviewableItems.filter(item => checks[item.id] === 'deficient');
  const pendingItems = reviewableItems.filter(item => checks[item.id] === 'pending');
  const completeItems = reviewableItems.filter(item => checks[item.id] === 'complete');
  const allComplete = reviewableItems.length > 0 && pendingItems.length === 0 && deficientItems.length === 0;
  const hasDeficiencies = deficientItems.length > 0;

  const readyAppsCount = useMemo(() => {
    return queue.filter(a => {
      if (a.id === selectedId) return allComplete;
      const c = getInitialChecks(a.id, a.shareMode);
      return COMPLETENESS_ITEMS.every(item => {
        if (item.id === 'share_certificate' && a.shareMode !== 'physical') return true;
        return c[item.id] === 'complete';
      });
    }).length;
  }, [queue, selectedId, allComplete]);

  const markItem = (id: string, state: CheckState) => {
    if (!canAct) return;
    setChecks(prev => ({ ...prev, [id]: state }));
    if (state === 'deficient') {
      const item = COMPLETENESS_ITEMS.find(i => i.id === id);
      setReasons(prev => ({ ...prev, [id]: prev[id] || item?.deficiencyReason || '' }));
    }
  };

  const getItemData = (itemId: string): ItemData | null => {
    if (!app) return null;
    switch (itemId) {
      case 'application_form':
        return {
          type: 'field',
          value: `Submitted ${new Date(app.submittedAt).toLocaleDateString('en-IN')} · Ref: ${app.intakeReference || app.applicationNumber} · ${app.source === 'assisted_entry' ? 'Assisted entry by internal team' : 'Borrower portal submission'}`,
          ok: true,
        };
      case 'applicant_signature':
        return { type: 'manual', hint: "Verify borrower's physical signature is present on the submitted application form." };
      case 'folio_number':
        return {
          type: 'field',
          value: member?.folioNumber ? `Folio ${member.folioNumber}` : 'Folio number not found in member record',
          ok: !!member?.folioNumber,
        };
      case 'shares_present':
        return {
          type: 'field',
          value: `${app.sharesHeld} shares · ${app.shareMode === 'physical' ? 'Physical' : 'Demat'}`,
          ok: app.sharesHeld > 0,
        };
      case 'loan_amount':
        return {
          type: 'field',
          value: `Requested amount captured · ${fmt(app.requestedAmount)}`,
          ok: app.requestedAmount > 0,
        };
      case 'active_member':
        return {
          type: 'field',
          value: member?.activeStatus === 'active' ? 'Active member' : 'Not an active member',
          ok: member?.activeStatus === 'active',
        };
      case 'loan_purpose':
        return {
          type: 'field',
          value: app.purpose === 'crop_production' || app.purpose === 'agriculture_activity' ? 'Agriculture / Crop production' : app.purpose.replace(/_/g, ' '),
          ok: app.purpose === 'crop_production' || app.purpose === 'agriculture_activity',
        };
      case 'existing_default':
        return {
          type: 'field',
          value: member?.defaultStatus === 'no_default' ? 'No existing defaults' : 'Existing default found',
          ok: member?.defaultStatus === 'no_default',
        };
      case 'nominee_signature':
        return { type: 'manual', hint: "Verify nominee's physical signature is present on the submitted application form." };
      case 'nominee_fields':
        return {
          type: 'field',
          value: `Nominee ref: ${app.nomineeId} — verify name, Aadhaar, PAN, and gender on physical form`,
          ok: !!app.nomineeId,
        };
      case 'nominee_age':
        return { type: 'manual', hint: "Verify nominee is not a minor from submitted documents." };
      case 'borrower_kyc':
        return { type: 'docs', docs: [{ label: 'Borrower PAN', docType: 'pan' }, { label: 'Borrower Aadhaar', docType: 'aadhaar' }] };
      case 'nominee_kyc':
        return { type: 'docs', docs: [{ label: 'Nominee PAN', docType: 'nominee_pan' }, { label: 'Nominee Aadhaar', docType: 'nominee_aadhaar' }] };
      case 'share_certificate':
        if (app.shareMode !== 'physical') return null;
        return { type: 'docs', docs: [{ label: 'Share Certificate', docType: 'share_certificate' }] };
      case 'land_712':
        return { type: 'docs', docs: [{ label: '7/12 Extract', docType: 'land_712' }] };
      case 'crop_plan':
        return { type: 'docs', docs: [{ label: 'Crop Plan', docType: 'crop_plan' }] };
      case 'bank_statement':
        return { type: 'docs', docs: [{ label: 'Bank Statement (6 months)', docType: 'bank_statement' }] };
      default:
        return null;
    }
  };

  if (!app) {
    return (
      <div className="p-6">
        <div className="card text-center py-16">
          <CheckCircle2 size={32} className="text-green-500 mx-auto mb-3" />
          <p className="text-slate-600 font-semibold">Completeness queue is clear</p>
          <p className="text-slate-400 text-sm mt-1">No applications are waiting for S12 review.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Application Completeness Check</h1>
          <p className="text-sm text-slate-500 mt-0.5">
            S1–S2 review by Deputy Manager – Finance · {queue.length} application{queue.length !== 1 ? 's' : ''} awaiting completeness decision
          </p>
        </div>
      </div>

      {!canAct && (
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 text-sm text-amber-800 flex items-center gap-2">
          <Info size={16} /> Read-only for {currentUser.role.replace(/_/g, ' ')}. Only Deputy Manager - Finance can complete S12 actions.
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        {[
          { label: 'Applications in Queue', value: queue.length },
          { label: 'Ready for Reference', value: readyAppsCount },
          { label: 'Checklist Items Pending', value: pendingItems.length },
          { label: 'Returned / Deficient', value: deficientItems.length },
        ].map(item => (
          <div key={item.label} className="card">
            <p className="text-xs text-slate-500 font-medium uppercase tracking-wide">{item.label}</p>
            <p className="text-2xl font-bold text-slate-900 mt-1 num">{item.value}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Queue sidebar */}
        <div className="card p-0 overflow-hidden lg:col-span-1">
          <div className="p-4 bg-slate-50 border-b border-slate-200">
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Completeness Queue ({queue.length})</p>
          </div>
          <div className="divide-y divide-slate-100">
            {queue.map(item => (
              <button
                key={item.id}
                onClick={() => setSelectedId(item.id)}
                className={`w-full block p-4 hover:bg-slate-50 transition-colors text-left ${
                  selectedId === item.id ? 'bg-green-50 border-l-4 border-l-green-500' : ''
                }`}
              >
                <div className="min-w-0 space-y-2">
                  <div className="flex items-center gap-2 min-w-0">
                    <div className="font-semibold text-slate-900 num text-sm truncate" title={getApplicationReference(item)}>
                      {getApplicationReference(item)}
                    </div>
                    {item.isException && (
                      <span className="text-[10px] bg-violet-100 text-violet-700 px-1.5 py-0.5 rounded font-bold tracking-wide flex-shrink-0">EX</span>
                    )}
                  </div>
                  <div className="text-xs text-slate-500 truncate">{item.memberName}</div>
                  <div className="text-xs text-slate-400 num">{fmt(item.requestedAmount)} · {item.shareMode}</div>
                  <div className="max-w-full overflow-hidden">
                    <StatusBadge
                      label={getQueueStatusLabel(item.status, getApplicationStatusLabel(item))}
                      family={item.status === 'submitted' ? 'info' : 'blocked'}
                      size="sm"
                    />
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>

        <div className="lg:col-span-2 space-y-4">
          {/* Application header */}
          <div className="card space-y-4">
            <div className="flex items-start justify-between gap-4">
              <div>
                <div className="flex items-center gap-2 flex-wrap">
                  <h2 className="text-lg font-bold text-slate-900 num">
                    {outcome === 'reference_generated' ? generatedReference : getApplicationReference(app)}
                  </h2>
                  <StatusBadge
                    label={
                      outcome === 'reference_generated'
                        ? 'reference_generated'
                        : outcome === 'returned'
                          ? 'returned_for_rectification'
                          : outcome === 'rejected'
                            ? 'rejected_completeness'
                            : getQueueStatusLabel(app.status, getApplicationStatusLabel(app))
                    }
                    family={
                      outcome === 'reference_generated' ? 'info' :
                      outcome === 'returned' ? 'blocked' :
                      app.status === 'submitted' ? 'info' :
                      (app.status === 'deficiency_raised' || app.status === 'returned_for_rectification' || app.status === 'incomplete') ? 'blocked' :
                      undefined
                    }
                  />
                </div>
                <p className="text-sm text-slate-500 mt-0.5">{app.memberName} · Applied {new Date(app.applicationDate).toLocaleDateString('en-IN')}</p>
              </div>
              <button onClick={() => onOpenApplication(app.id)} className="btn-secondary flex items-center gap-2 flex-shrink-0">
                <FileText size={14} /> Full Application
              </button>
            </div>

            {/* Application & member details grid */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {[
                { label: 'Folio', value: member?.folioNumber || 'Pending' },
                { label: 'Member Type', value: app.memberType === 'fpc' ? 'FPC' : app.memberType.charAt(0).toUpperCase() + app.memberType.slice(1).replace('_', ' ') },
                { label: 'Shares', value: `${app.sharesHeld} (${app.shareMode === 'physical' ? 'Physical' : 'Demat'})` },
                { label: 'KYC Status', value: checks['borrower_kyc'] === 'complete' ? (member?.kycStatus || '—') : 'KYC Pending Review', badge: true },
                { label: 'Requested Amount', value: fmt(app.requestedAmount) },
                { label: 'Loan Type', value: app.loanType === 'short_term' ? `Short-term · ${app.tenure} months` : `Long-term · ${app.tenure} months` },
                { label: 'Purpose', value: app.purpose.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) },
                { label: 'Land Area', value: app.landAreaAcres ? `${app.landAreaAcres} acres` : '—' },
                { label: 'Nominee Ref', value: app.nomineeId },
                { label: 'Loan reference', value: hasFormalLoanReference(app) ? app.officialReference || app.applicationNumber : 'Not generated yet' },
                { label: 'Mobile', value: member?.mobile || '—' },
                { label: 'Email', value: member?.email || '—' },
              ].map(item => (
                <div key={item.label} className="bg-slate-50 rounded-lg p-3">
                  <p className="text-xs text-slate-500 font-medium uppercase tracking-wide">{item.label}</p>
                  {item.badge
                    ? <div className="mt-1"><StatusBadge label={item.value} size="sm" /></div>
                    : <p className="text-sm font-semibold text-slate-900 mt-0.5 truncate">{item.value}</p>
                  }
                </div>
              ))}
            </div>
          </div>

          {/* Checklist progress bar */}
          <div className="card">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-semibold text-slate-800 flex items-center gap-2">
                <ClipboardList size={16} className="text-green-600" /> Mandatory Completeness Checklist
              </h3>
              <div className="text-xs text-slate-500">{completeItems.length}/{reviewableItems.length} verified</div>
            </div>
            <div className="w-full bg-slate-100 rounded-full h-2">
              <div
                className={`h-2 rounded-full transition-all ${hasDeficiencies ? 'bg-red-400' : 'bg-green-500'}`}
                style={{ width: `${Math.round((completeItems.length / reviewableItems.length) * 100)}%` }}
              />
            </div>
          </div>

          {/* Checklist categories — each row shows actual submitted data */}
          {COMPLETENESS_CATEGORIES.map(category => (
            <div key={category} className="card p-0 overflow-hidden">
              <div className="px-5 py-3 bg-slate-50 border-b border-slate-100">
                <p className="text-xs font-semibold text-slate-600 uppercase tracking-wide">{category}</p>
              </div>
              <div className="divide-y divide-slate-100">
                {COMPLETENESS_ITEMS.filter(item => item.category === category).map(item => {
                  const isNa = item.id === 'share_certificate' && app.shareMode !== 'physical';
                  const state = isNa ? 'complete' : checks[item.id] || 'pending';
                  const data = getItemData(item.id);

                  return (
                    <div key={item.id} className={`px-5 py-4 ${state === 'deficient' ? 'bg-red-50' : state === 'complete' ? 'bg-green-50/30' : ''}`}>
                      <div className="flex items-start gap-3">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 flex-wrap">
                            <span className="text-sm font-semibold text-slate-800">{item.label}</span>
                            {isNa && <span className="text-xs text-slate-400 bg-slate-100 px-1.5 py-0.5 rounded">N/A (Demat)</span>}
                          </div>

                          {/* Inline submitted data */}
                          {!isNa && data && (
                            <div className="mt-2">
                              {data.type === 'field' && (
                                <div className="flex items-start gap-1.5">
                                  {data.ok
                                    ? <CheckCircle2 size={13} className="text-green-500 flex-shrink-0 mt-0.5" />
                                    : <XCircle size={13} className="text-red-400 flex-shrink-0 mt-0.5" />
                                  }
                                  <span className={`text-xs leading-relaxed ${data.ok ? 'text-slate-600' : 'text-red-700 font-medium'}`}>{data.value}</span>
                                </div>
                              )}
                              {data.type === 'manual' && (
                                <p className="text-xs text-slate-400 italic">{data.hint}</p>
                              )}
                              {data.type === 'docs' && (
                                <div className="flex flex-wrap gap-2 mt-1">
                                  {data.docs.map(d => {
                                    const doc = appDocs.find(r => r.documentType === d.docType);
                                    const uploaded = doc ? DOC_UPLOADED_STATUSES.has(doc.status) : false;
                                    const itemState = checks[item.id] || 'pending';
                                    const isDeficient = itemState === 'deficient';
                                    const colorClass = isDeficient
                                      ? 'bg-red-50 border-red-200 text-red-700'
                                      : uploaded
                                        ? 'bg-green-50 border-green-200 text-green-800'
                                        : 'bg-slate-50 border-slate-200 text-slate-600';
                                    const Icon = isDeficient ? XCircle : (uploaded ? CheckCircle2 : FileText);
                                    
                                    return (
                                      <div
                                        key={d.docType}
                                        className={`inline-flex items-center gap-1.5 text-xs px-2.5 py-1.5 rounded-lg border ${colorClass}`}
                                      >
                                        <Icon size={11} className="flex-shrink-0" />
                                        <span className="font-medium">{d.label}</span>
                                        {doc && (
                                          <span className="text-[10px] uppercase font-semibold px-1 py-0.5 rounded bg-white/70 border border-current opacity-70">
                                            {doc.status.replace(/_/g, ' ')}
                                          </span>
                                        )}
                                        <button
                                          onClick={() => setViewingDoc({
                                            label: d.label,
                                            status: doc?.status || 'not_uploaded',
                                            fileName: doc?.fileName,
                                          })}
                                          className="ml-0.5 p-0.5 rounded text-slate-400 hover:text-blue-600 hover:bg-blue-50 transition-colors"
                                          title={`View ${d.label}`}
                                        >
                                          <Eye size={11} />
                                        </button>
                                      </div>
                                    );
                                  })}
                                </div>
                              )}
                            </div>
                          )}

                          {state === 'deficient' && (
                            <input
                              type="text"
                              disabled={!canAct}
                              value={reasons[item.id] || ''}
                              onChange={e => setReasons(prev => ({ ...prev, [item.id]: e.target.value }))}
                              placeholder="Deficiency reason"
                              className="mt-2 w-full text-xs border border-red-200 rounded px-2.5 py-1.5 bg-white text-red-800 placeholder-red-300 focus:outline-none focus:ring-1 focus:ring-red-300 disabled:bg-red-50"
                            />
                          )}
                          {state === 'pending' && !data && (
                            <p className="text-xs text-slate-400 mt-0.5">Not yet reviewed</p>
                          )}
                        </div>

                        <div className="flex items-center gap-2 flex-shrink-0 pt-0.5">
                          {state === 'complete' ? (
                            <>
                              <StatusBadge label="complete" size="sm" />
                              {!isNa && canAct && (
                                <button onClick={() => markItem(item.id, 'deficient')} className="text-xs text-slate-400 hover:text-red-600 px-1.5 py-1 rounded hover:bg-red-50 transition-colors">Flag</button>
                              )}
                            </>
                          ) : state === 'deficient' ? (
                            <>
                              <StatusBadge label="deficiency_raised" size="sm" />
                              {canAct && (
                                <button onClick={() => markItem(item.id, 'pending')} className="text-xs text-slate-400 hover:text-slate-700 px-1.5 py-1 rounded hover:bg-slate-100 transition-colors">Clear</button>
                              )}
                            </>
                          ) : canAct ? (
                            <div className="flex gap-1">
                              <button
                                onClick={() => markItem(item.id, 'complete')}
                                className="text-xs px-2.5 py-1 rounded border border-green-200 text-green-700 bg-white hover:bg-green-50 font-medium transition-colors flex items-center gap-1"
                              >
                                <CheckCircle2 size={11} /> Complete
                              </button>
                              <button
                                onClick={() => markItem(item.id, 'deficient')}
                                className="text-xs px-2.5 py-1 rounded border border-red-200 text-red-600 bg-white hover:bg-red-50 font-medium transition-colors flex items-center gap-1"
                              >
                                <AlertTriangle size={11} /> Deficient
                              </button>
                            </div>
                          ) : (
                            <span className="text-xs text-amber-600 bg-amber-50 border border-amber-100 px-2 py-0.5 rounded font-medium">Pending</span>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          ))}

          {/* Deficiencies panel + actions */}
          <div className="card space-y-4">
            <div className="flex items-center justify-between gap-3">
              <h3 className="font-semibold text-slate-800">Deficiencies panel</h3>
              <StatusBadge label={hasDeficiencies ? 'deficiency_raised' : allComplete ? 'complete' : 'pending'} size="sm" />
            </div>

            {hasDeficiencies ? (
              <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 space-y-3">
                <p className="text-sm font-semibold text-amber-800 flex items-center gap-2">
                  <AlertTriangle size={15} /> {deficientItems.length} item{deficientItems.length !== 1 ? 's' : ''} require borrower rectification
                </p>
                <ul className="text-xs text-amber-700 space-y-1 list-disc list-inside">
                  {deficientItems.map(item => (
                    <li key={item.id}>{item.label}{reasons[item.id] ? ` — ${reasons[item.id]}` : ''}</li>
                  ))}
                </ul>
              </div>
            ) : (
              <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 text-sm text-slate-700">
                No deficiencies selected for the current application.
              </div>
            )}

            <textarea
              value={internalComment}
              onChange={e => setInternalComment(e.target.value)}
              disabled={!canAct}
              rows={2}
              placeholder="Add internal comment"
              className="w-full text-sm border border-slate-200 rounded-lg px-3 py-2 text-slate-700 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-green-300 resize-none disabled:bg-slate-50"
            />

            <div className="border-t border-slate-100 pt-4 space-y-3">
              <div className="flex items-center justify-between gap-3 flex-wrap">
                <div>
                  <h3 className="font-semibold text-slate-800">Reference number generation</h3>
                  <p className="text-xs text-slate-500 mt-0.5">Next sequential LO reference: <span className="font-semibold text-slate-700 num">{generatedReference}</span></p>
                </div>
                <div className="flex flex-col items-end gap-2">
                  <div className="flex items-center gap-3 flex-wrap">
                    <button
                      disabled={!canAct || !allComplete || outcome !== null || hasDeficiencies}
                      onClick={() => setOutcome('reference_generated')}
                      className="btn-primary flex items-center gap-2"
                    >
                      <ArrowRight size={14} /> Generate reference number
                    </button>
                    <button
                      disabled={!canAct || !hasDeficiencies || outcome !== null || !internalComment.trim()}
                      onClick={() => setOutcome('returned')}
                      className="btn-secondary flex items-center gap-2"
                      title={!internalComment.trim() ? "Internal comment required" : ""}
                    >
                      <Send size={14} /> Return for deficiency
                    </button>
                    <button
                      disabled={!canAct || outcome !== null || !internalComment.trim() || hasDeficiencies}
                      onClick={() => setOutcome('rejected')}
                      className="btn-destructive flex items-center gap-2"
                      title={hasDeficiencies ? "Use Return for Deficiency for missing items" : !internalComment.trim() ? "Internal comment required" : ""}
                    >
                      <XCircle size={14} /> Recommend rejection
                    </button>
                  </div>
                  {!allComplete && <span className="text-[10px] text-slate-400 font-medium">Complete all mandatory checks before generating the loan reference.</span>}
                </div>
              </div>

              {outcome === 'reference_generated' && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <p className="text-sm font-semibold text-green-800 flex items-center gap-2">
                    <CheckCircle2 size={15} /> Reference generated · {generatedReference}
                  </p>
                  <div className="text-xs text-green-700 mt-2 space-y-1">
                    <p>Loan Request Register entry created.</p>
                    <p>Application status changed to Reference Generated.</p>
                    <p>Borrower notified where communication details exist.</p>
                    <p>Application moves to appraisal stage.</p>
                  </div>
                  <button onClick={() => onOpenAppraisal(app.id)} className="btn-secondary mt-3 flex items-center gap-2">
                    <ArrowRight size={14} /> Open appraisal
                  </button>
                </div>
              )}

              {outcome === 'returned' && (
                <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
                  <p className="text-sm font-semibold text-amber-800 flex items-center gap-2">
                    <RefreshCw size={15} /> Deficiency communication generated
                  </p>
                  <p className="text-xs text-amber-700 mt-2">
                    Application status changed to Returned for Rectification. Formal LO reference has not been generated.
                  </p>
                </div>
              )}

              {outcome === 'rejected' && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <p className="text-sm font-semibold text-red-800 flex items-center gap-2">
                    <MessageSquare size={15} /> Rejection recommendation forwarded
                  </p>
                  <p className="text-xs text-red-700 mt-2">
                    Application routed to Credit Manager for final rejection approval. Formal LO reference has not been generated.
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Document viewer modal */}
      {viewingDoc && (
        <div
          className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
          onClick={() => setViewingDoc(null)}
        >
          <div
            className="bg-white rounded-2xl shadow-2xl w-full max-w-md"
            onClick={e => e.stopPropagation()}
          >
            <div className="flex items-center justify-between px-5 py-4 border-b border-slate-100">
              <div className="flex items-center gap-2">
                <FileText size={16} className="text-slate-500" />
                <span className="font-semibold text-slate-900">{viewingDoc.label}</span>
              </div>
              <button
                onClick={() => setViewingDoc(null)}
                className="p-1 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
              >
                <X size={16} />
              </button>
            </div>
            <div className="p-5">
              {DOC_UPLOADED_STATUSES.has(viewingDoc.status) ? (
                <>
                  <div className="bg-slate-50 border-2 border-dashed border-slate-200 rounded-xl p-10 text-center mb-4">
                    <FileText size={40} className="text-slate-300 mx-auto mb-3" />
                    <p className="text-sm font-medium text-slate-600">{viewingDoc.fileName || `${viewingDoc.label}.pdf`}</p>
                    <p className="text-xs text-slate-400 mt-1">Document preview not available in this environment</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <StatusBadge label={viewingDoc.status} size="sm" />
                    <span className="text-xs text-slate-500">{viewingDoc.status.replace(/_/g, ' ')}</span>
                  </div>
                </>
              ) : (
                <div className="bg-red-50 border border-red-200 rounded-xl p-8 text-center">
                  <XCircle size={32} className="text-red-400 mx-auto mb-2" />
                  <p className="text-sm font-semibold text-red-800">Document not uploaded</p>
                  <p className="text-xs text-red-600 mt-1">This document has not been submitted by the borrower.</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CompletenessWorkbench;
