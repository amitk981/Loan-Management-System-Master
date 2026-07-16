import React from 'react';
import { FileText, CheckCircle2, XCircle, Upload, Banknote, User, AlertOctagon } from 'lucide-react';
import type { AuditEvent } from '../../types';

const eventIcons: Record<string, React.ReactNode> = {
  'Application Submitted':           <FileText size={14} />,
  'Reference Number Generated':      <CheckCircle2 size={14} />,
  'Appraisal Note Prepared':         <FileText size={14} />,
  'Submitted to Sanction Committee': <User size={14} />,
  'Loan Approved':                   <CheckCircle2 size={14} />,
  'Loan Rejected':                   <XCircle size={14} />,
  'Document Uploaded':               <Upload size={14} />,
  'Disbursement Initiated':          <Banknote size={14} />,
  'Exception Created':               <AlertOctagon size={14} />,
};

const eventColors: Record<string, string> = {
  'Application Submitted':           'bg-blue-100 text-blue-700',
  'Reference Number Generated':      'bg-green-100 text-green-700',
  'Appraisal Note Prepared':         'bg-amber-100 text-amber-700',
  'Submitted to Sanction Committee': 'bg-violet-100 text-violet-700',
  'Loan Approved':                   'bg-green-100 text-green-700',
  'Loan Rejected':                   'bg-red-100 text-red-700',
  'Exception Created':               'bg-violet-100 text-violet-700',
};

interface AuditTimelineProps {
  events: AuditEvent[];
  limit?: number;
  sensitiveVisible?: boolean;
}

const formatTime = (ts: string) => {
  const d = new Date(ts);
  return d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' }) +
    ' at ' + d.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });
};

const formatState = (s: string) => s.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');

const roleLabels: Record<string, string> = {
  field_officer: 'Field Officer',
  deputy_manager_finance: 'Deputy Manager – Finance',
  credit_manager: 'Credit Manager',
  compliance_team: 'Compliance Team',
  company_secretary: 'Company Secretary',
  sanction_committee: 'Sanction Committee',
  cfo: 'CFO',
  director: 'Director',
  senior_manager_finance: 'Senior Manager – Finance',
  cfc: 'Chief Financial Controller',
  accounts: 'Accounts',
  sales_team_user: 'Sales Team User',
  auditor: 'Auditor',
  admin: 'Administrator',
  borrower: 'Borrower / Member',
};

const maskText = (text: string, visible?: boolean) => {
  if (visible) return text;
  return text
    .replace(/(ref |SN-|DP-|SR-)([A-Z0-9-]*?)([0-9]{4})\b/ig, '$1••••$3')
    .replace(/(PAN|Aadhaar|Account)[ \w-]*?([0-9]{4})\b/ig, '$1 ••••$2');
};

const AuditTimeline: React.FC<AuditTimelineProps> = ({ events, limit = 20, sensitiveVisible }) => {
  const visibleEvents = events.slice(0, limit);

  if (visibleEvents.length === 0) {
    return (
      <div className="text-center py-8 text-slate-400 text-sm">No audit events recorded yet.</div>
    );
  }

  return (
    <div className="space-y-0">
      {visibleEvents.map((event, idx) => {
        const isLast = idx === visibleEvents.length - 1;
        const iconStyle = eventColors[event.eventType] || 'bg-slate-100 text-slate-600';
        const icon = eventIcons[event.eventType] || <FileText size={14} />;

        return (
          <div key={event.id} className="flex gap-3">
            {/* Timeline */}
            <div className="flex flex-col items-center">
              <div className={`w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 ${iconStyle}`}>
                {icon}
              </div>
              {!isLast && <div className="w-0.5 flex-1 bg-slate-200 my-1" />}
            </div>

            {/* Content */}
            <div className={`flex-1 ${isLast ? '' : 'pb-4'}`}>
              <div className="flex items-start justify-between gap-2">
                <div>
                  <span className="text-sm font-semibold text-slate-900">{event.eventType}</span>
                </div>
                <span className="text-xs text-slate-400 flex-shrink-0">{formatTime(event.timestamp)}</span>
              </div>
              {event.previousState && event.newState && (
                <div className="mt-1 text-xs text-slate-500 font-medium">
                  Status changed from {formatState(event.previousState)} to {formatState(event.newState)}.
                </div>
              )}
              <div className="text-xs text-slate-500 mt-0.5">
                {event.actorName} · {roleLabels[event.actorRole] || event.actorRole}
              </div>
              {event.comment && (
                <div className="mt-1.5 text-xs text-slate-600 bg-slate-50 rounded-lg px-3 py-2 border border-slate-100">
                  {maskText(event.comment, sensitiveVisible)}
                </div>
              )}
              {event.reason && (
                <div className="mt-1 text-xs text-amber-700 bg-amber-50 rounded px-2 py-1">
                  Reason: {maskText(event.reason, sensitiveVisible)}
                </div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default AuditTimeline;
