import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { Eye, RefreshCw, Search, ShieldCheck, X } from 'lucide-react';

import StatusBadge from '../../components/ui/StatusBadge';
import { AuthSessionError } from '../../services/authSession';
import {
  fetchAuditorEpic011,
  type AuditorEpic011Projection,
} from '../../services/auditorApi';

type Family = 'all' | 'defaults' | 'closures' | 'compliance' | 'grievances';

interface AuditRow {
  family: Exclude<Family, 'all'>;
  id: string;
  reference: string;
  subject: string;
  status: string;
  details: Record<string, unknown>;
  auditReferences: string[];
  workflowReferences: string[];
}

const text = (value: unknown) => typeof value === 'string' ? value : '';

const rowsFor = (data: AuditorEpic011Projection): AuditRow[] => [
  ...data.default_cases.map(row => ({
    family: 'defaults' as const,
    id: row.default_case_id,
    reference: row.loan_account_number,
    subject: row.borrower_name,
    status: row.default_case_status,
    details: row,
    auditReferences: row.audit_references,
    workflowReferences: row.workflow_references,
  })),
  ...data.closures.map(row => ({
    family: 'closures' as const,
    id: row.loan_closure_id,
    reference: row.loan_account_number,
    subject: row.borrower_name,
    status: row.closure_stage,
    details: row,
    auditReferences: row.audit_references,
    workflowReferences: row.workflow_references,
  })),
  ...data.compliance_items.map(row => ({
    family: 'compliance' as const,
    id: row.record_id,
    reference: text(row.details.control_code) || text(row.details.task_period) || row.record_type,
    subject: row.record_type.replace(/_/g, ' '),
    status: text(row.details.status) || text(row.details.task_status) || text(row.details.review_status) || 'recorded',
    details: row.details,
    auditReferences: row.audit_references,
    workflowReferences: row.workflow_references,
  })),
  ...data.grievances.map(row => ({
    family: 'grievances' as const,
    id: row.grievance_id,
    reference: row.grievance_reference,
    subject: row.grievance_category.replace(/_/g, ' '),
    status: row.status,
    details: row,
    auditReferences: row.audit_references,
    workflowReferences: row.workflow_references,
  })),
];

const errorStatus = (error: unknown) => {
  if (error instanceof AuthSessionError) return error.status;
  if (error && typeof error === 'object' && 'status' in error) {
    return (error as { status?: number }).status;
  }
  return undefined;
};

const AuditorEpic011View: React.FC = () => {
  const [data, setData] = useState<AuditorEpic011Projection | null>(null);
  const [family, setFamily] = useState<Family>('all');
  const [query, setQuery] = useState('');
  const [selected, setSelected] = useState<AuditRow | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<'unauthorised' | 'failed' | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setData(await fetchAuditorEpic011());
    } catch (caught) {
      setData(null);
      setError(errorStatus(caught) === 403 ? 'unauthorised' : 'failed');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const rows = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    return data ? rowsFor(data).filter(row => (
      (family === 'all' || row.family === family)
      && (!normalized || `${row.reference} ${row.subject} ${row.status}`.toLowerCase().includes(normalized))
    )) : [];
  }, [data, family, query]);

  if (loading) {
    return <div className="card p-8 text-center text-slate-500">Loading Epic 011 audit records…</div>;
  }

  if (error === 'unauthorised') {
    return (
      <div className="card p-8 text-center">
        <ShieldCheck className="mx-auto text-amber-500 mb-3" size={32} />
        <h2 className="font-semibold text-slate-900">Auditor access is not authorised.</h2>
        <p className="text-sm text-slate-500 mt-1">An active audit-readonly scope and compliance-report permission are required.</p>
      </div>
    );
  }

  if (error === 'failed' || !data) {
    return (
      <div className="card p-8 text-center">
        <h2 className="font-semibold text-slate-900">Epic 011 audit records could not be loaded.</h2>
        <button type="button" onClick={() => void load()} className="btn-secondary mt-4">
          <RefreshCw size={16} /> Retry
        </button>
      </div>
    );
  }

  const evidence = selected?.details.evidence_metadata;
  const evidenceRows = Array.isArray(evidence) ? evidence : (
    selected?.details.compliance_evidence_id
      ? [{ evidence_id: selected.details.compliance_evidence_id }]
      : []
  );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Epic 011 Audit View</h1>
        <p className="text-sm text-slate-500 mt-1">Read-only default, recovery, closure, compliance, KYC and grievance evidence.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          ['Default & Recovery', data.summary.default_cases],
          ['Closure & Archive', data.summary.closures],
          ['Compliance & KYC', data.summary.compliance_items],
          ['Grievances', data.summary.grievances],
        ].map(([label, value]) => (
          <div className="card p-4" key={String(label)}>
            <div className="text-sm font-medium text-slate-500">{label}</div>
            <div className="text-2xl font-bold text-slate-900 mt-1">{value}</div>
          </div>
        ))}
      </div>

      <div className="card">
        <div className="p-4 border-b border-slate-100 flex flex-col md:flex-row gap-3">
          <label className="text-sm text-slate-600">
            <span className="block mb-1">Record family</span>
            <select className="field-select text-sm" value={family} onChange={event => setFamily(event.target.value as Family)}>
              <option value="all">All records</option>
              <option value="defaults">Default & recovery</option>
              <option value="closures">Closure & archive</option>
              <option value="compliance">Compliance & KYC</option>
              <option value="grievances">Grievances</option>
            </select>
          </label>
          <label className="text-sm text-slate-600 flex-1">
            <span className="block mb-1">Search records</span>
            <span className="relative block">
              <Search size={16} className="absolute left-3 top-2.5 text-slate-400" />
              <input className="field-input text-sm pl-9" value={query} onChange={event => setQuery(event.target.value)} placeholder="Reference, member, status" />
            </span>
          </label>
        </div>

        {rows.length === 0 ? (
          <div className="p-10 text-center text-sm text-slate-500">No Epic 011 records match this view.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr>
                  <th className="table-header text-left">Family</th>
                  <th className="table-header text-left">Reference</th>
                  <th className="table-header text-left">Subject</th>
                  <th className="table-header text-left">Status</th>
                  <th className="table-header text-right">Read-only detail</th>
                </tr>
              </thead>
              <tbody>
                {rows.map(row => (
                  <tr key={`${row.family}-${row.id}`} className="border-b border-slate-100">
                    <td className="table-cell capitalize">{row.family}</td>
                    <td className="table-cell font-medium text-slate-900">{row.reference}</td>
                    <td className="table-cell capitalize">{row.subject}</td>
                    <td className="table-cell"><StatusBadge label={row.status} size="sm" /></td>
                    <td className="table-cell text-right">
                      <button type="button" className="btn-secondary text-xs" onClick={() => setSelected(row)} aria-label={`View ${row.id}`}>
                        <Eye size={14} /> View
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {selected && (
        <div className="card">
          <div className="p-4 border-b border-slate-100 flex items-center justify-between">
            <div>
              <h2 className="font-semibold text-slate-900">Read-only record detail</h2>
              <p className="text-xs text-slate-500 font-mono mt-1">{selected.id}</p>
            </div>
            <button type="button" className="btn-secondary" onClick={() => setSelected(null)} aria-label="Close details"><X size={16} /></button>
          </div>
          <div className="p-4 grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <h3 className="text-sm font-semibold text-slate-700 mb-2">Immutable references</h3>
              {[...selected.auditReferences, ...selected.workflowReferences].length === 0 ? (
                <p className="text-sm text-slate-500">No immutable references recorded.</p>
              ) : [...selected.auditReferences, ...selected.workflowReferences].map(reference => (
                <div key={reference} className="text-xs font-mono text-slate-600 py-1">{reference}</div>
              ))}
            </div>
            <div>
              <h3 className="text-sm font-semibold text-slate-700 mb-2">Evidence metadata</h3>
              {evidenceRows.length === 0 ? (
                <p className="text-sm text-slate-500">No evidence metadata linked.</p>
              ) : evidenceRows.map((item, index) => {
                const metadata = item as Record<string, unknown>;
                const evidenceId = text(metadata.evidence_id) || text(metadata.compliance_evidence_id) || `evidence-${index + 1}`;
                const href = text(metadata.download_path) || `#evidence-${evidenceId}`;
                return <a key={evidenceId} href={href} className="block text-sm text-green-700 py-1">Evidence metadata {evidenceId}</a>;
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AuditorEpic011View;
