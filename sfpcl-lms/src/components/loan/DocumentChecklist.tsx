import React, { useState } from 'react';
import { CheckCircle2, XCircle, Clock, Upload, Eye, AlertTriangle, Stamp, FileSignature } from 'lucide-react';
import type { DocumentRecord } from '../../types';
import { documents } from '../../data/mockData';

const docLabels: Record<string, string> = {
  pan: 'PAN Card',
  aadhaar: 'Aadhaar Card',
  share_certificate: 'Share Certificates',
  land_712: 'Land Records / 7/12 Extract',
  crop_plan: 'Crop Plan',
  bank_statement: '6-Month Bank Statement',
  poa: 'Power of Attorney (₹500 stamp, notarised)',
  tri_party: 'Tri-party Agreement / Declaration',
  sh4: 'SH-4 Share Transfer Form',
  term_sheet: 'Term Sheet',
  loan_agreement: 'Loan Agreement (₹500 stamp, notarised)',
  cancelled_cheque: 'Cancelled Cheque',
  blank_cheque: 'Blank-Dated Cheque',
  bank_verification_letter: 'Bank Verification Letter',
  checklist: 'Final Checklist',
  appraisal_note: 'Loan Appraisal Note',
};

const groupDocs = (docs: DocumentRecord[]) => ({
  'KYC & Identity': docs.filter(d => ['pan', 'aadhaar', 'share_certificate'].includes(d.documentType)),
  'Agriculture Evidence': docs.filter(d => ['land_712', 'crop_plan', 'bank_statement'].includes(d.documentType)),
  'Legal Documents': docs.filter(d => ['poa', 'tri_party', 'term_sheet', 'loan_agreement', 'sh4'].includes(d.documentType)),
  'Bank & Security': docs.filter(d => ['cancelled_cheque', 'blank_cheque', 'bank_verification_letter'].includes(d.documentType)),
});

const statusConfig = {
  not_started:     { icon: <Clock size={14} className="text-slate-400" />, text: 'Not Started', cls: 'text-slate-500' },
  pending_upload:  { icon: <Upload size={14} className="text-amber-500" />, text: 'Pending Upload', cls: 'text-amber-700' },
  uploaded:        { icon: <Eye size={14} className="text-blue-500" />, text: 'Uploaded', cls: 'text-blue-700' },
  under_review:    { icon: <Clock size={14} className="text-amber-500" />, text: 'Under Review', cls: 'text-amber-700' },
  verified:        { icon: <CheckCircle2 size={14} className="text-green-600" />, text: 'Verified', cls: 'text-green-700' },
  rejected:        { icon: <XCircle size={14} className="text-red-600" />, text: 'Rejected', cls: 'text-red-700' },
  signed:          { icon: <FileSignature size={14} className="text-blue-600" />, text: 'Signed', cls: 'text-blue-700' },
  stamped:         { icon: <Stamp size={14} className="text-amber-600" />, text: 'Stamped', cls: 'text-amber-700' },
  notarised:       { icon: <CheckCircle2 size={14} className="text-green-600" />, text: 'Notarised', cls: 'text-green-700' },
  complete:        { icon: <CheckCircle2 size={14} className="text-green-600" />, text: 'Complete', cls: 'text-green-700' },
  returned:        { icon: <CheckCircle2 size={14} className="text-teal-600" />, text: 'Returned', cls: 'text-teal-700' },
};

interface DocumentChecklistProps {
  applicationId: string;
}

const DocumentChecklist: React.FC<DocumentChecklistProps> = ({ applicationId }) => {
  const [expandedGroups, setExpandedGroups] = useState<Record<string, boolean>>({
    'KYC & Identity': true,
    'Agriculture Evidence': true,
    'Legal Documents': true,
    'Bank & Security': true,
  });

  const docs = documents.filter(d => d.applicationId === applicationId);
  const groups = groupDocs(docs);

  const complete = docs.filter(d => ['verified', 'notarised', 'complete', 'signed'].includes(d.status)).length;
  const blocked = docs.filter(d => d.status === 'rejected').length;
  const pending = docs.filter(d => ['pending_upload', 'not_started', 'uploaded', 'signed'].includes(d.status)).length;

  return (
    <div className="space-y-4">
      {/* Summary */}
      <div className="grid grid-cols-3 gap-3">
        <div className="bg-green-50 border border-green-200 rounded-lg p-3 text-center">
          <div className="text-xl font-bold text-green-700 num">{complete}</div>
          <div className="text-xs text-green-600">Complete</div>
        </div>
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 text-center">
          <div className="text-xl font-bold text-amber-700 num">{pending}</div>
          <div className="text-xs text-amber-600">Pending</div>
        </div>
        <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-center">
          <div className="text-xl font-bold text-red-700 num">{blocked}</div>
          <div className="text-xs text-red-600">Rejected</div>
        </div>
      </div>

      {/* Disbursement gate */}
      {pending > 0 && (
        <div className="flex items-center gap-2 bg-red-50 border border-red-200 rounded-lg px-4 py-3">
          <AlertTriangle size={16} className="text-red-600 flex-shrink-0" />
          <p className="text-sm text-red-800 font-medium">
            Disbursement is blocked — {pending} document{pending > 1 ? 's' : ''} pending completion.
          </p>
        </div>
      )}

      {/* Document groups */}
      {Object.entries(groups).map(([groupName, groupDocs]) => (
        groupDocs.length > 0 && (
          <div key={groupName} className="border border-slate-200 rounded-lg overflow-hidden">
            <button
              onClick={() => setExpandedGroups(prev => ({ ...prev, [groupName]: !prev[groupName] }))}
              className="w-full flex items-center justify-between px-4 py-3 bg-slate-50 hover:bg-slate-100 transition-colors"
            >
              <span className="text-sm font-semibold text-slate-700">{groupName}</span>
              <div className="flex items-center gap-2">
                <span className="text-xs text-slate-500">{groupDocs.filter(d => ['verified', 'notarised', 'complete'].includes(d.status)).length}/{groupDocs.length} complete</span>
                <span className={`transition-transform text-slate-400 ${expandedGroups[groupName] ? 'rotate-180' : ''}`}>▾</span>
              </div>
            </button>

            {expandedGroups[groupName] && (
              <div className="divide-y divide-slate-100">
                {groupDocs.map(doc => {
                  const sc = statusConfig[doc.status] || statusConfig.not_started;
                  const needsStamp = ['poa', 'loan_agreement'].includes(doc.documentType);
                  return (
                    <div key={doc.id} className="flex items-center gap-3 px-4 py-3">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="text-sm text-slate-800">{docLabels[doc.documentType] || doc.documentType}</span>
                          {doc.requiredFlag === 'mandatory' && (
                            <span className="text-xs text-red-500 font-medium">Required</span>
                          )}
                        </div>
                        {needsStamp && (
                          <div className="flex gap-3 mt-1">
                            <span className={`text-xs flex items-center gap-1 ${doc.stampStatus === 'complete' ? 'text-green-600' : doc.stampStatus === 'pending' ? 'text-amber-600' : 'text-slate-400'}`}>
                              <Stamp size={10} /> Stamp: {doc.stampStatus === 'complete' ? 'Done' : doc.stampStatus === 'not_required' ? 'N/A' : 'Pending'}
                            </span>
                            <span className={`text-xs flex items-center gap-1 ${doc.notarisationStatus === 'complete' ? 'text-green-600' : doc.notarisationStatus === 'pending' ? 'text-amber-600' : 'text-slate-400'}`}>
                              ✍ Notarised: {doc.notarisationStatus === 'complete' ? 'Yes' : doc.notarisationStatus === 'not_required' ? 'N/A' : 'Pending'}
                            </span>
                          </div>
                        )}
                      </div>
                      <div className={`flex items-center gap-1 text-xs font-medium flex-shrink-0 ${sc.cls}`}>
                        {sc.icon}
                        {sc.text}
                      </div>
                      <div className="flex gap-1 flex-shrink-0">
                        {doc.status !== 'not_started' && (
                          <button className="text-xs px-2 py-1 border border-slate-200 rounded text-slate-600 hover:bg-slate-50">View</button>
                        )}
                        {['pending_upload', 'not_started', 'rejected'].includes(doc.status) && (
                          <button className="text-xs px-2 py-1 bg-green-50 border border-green-200 rounded text-green-700 hover:bg-green-100">Upload</button>
                        )}
                        {['uploaded', 'under_review', 'signed'].includes(doc.status) && (
                          <button className="text-xs px-2 py-1 bg-blue-50 border border-blue-200 rounded text-blue-700 hover:bg-blue-100">Verify</button>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )
      ))}

      {/* Checklist sign-off sequence */}
      <div className="border border-slate-200 rounded-lg p-4">
        <div className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-3">Checklist Sign-off Sequence</div>
        <div className="space-y-2">
          {[
            { role: 'Company Secretary', meaning: 'All required documents verified', status: 'pending' },
            { role: 'Credit Manager', meaning: 'Loan limit confirmed', status: 'pending' },
            { role: 'Sanction Committee', meaning: 'Final approval given', status: 'pending' },
            { role: 'Senior Manager – Finance', meaning: 'Loan disbursed (signed after disbursement)', status: 'pending' },
          ].map((step, idx) => (
            <div key={idx} className="flex items-center gap-3">
              <div className="w-5 h-5 rounded-full border-2 border-slate-300 flex-shrink-0 flex items-center justify-center">
                <span className="text-xs text-slate-400 font-semibold">{idx + 1}</span>
              </div>
              <div className="flex-1">
                <span className="text-sm font-medium text-slate-700">{step.role}</span>
                <span className="text-xs text-slate-400 ml-2">— {step.meaning}</span>
              </div>
              <span className="text-xs text-amber-600 bg-amber-50 px-2 py-0.5 rounded-full font-medium">Awaiting</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default DocumentChecklist;
