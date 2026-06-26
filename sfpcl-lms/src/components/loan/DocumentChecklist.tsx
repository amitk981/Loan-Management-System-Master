import React from 'react';
import { AlertTriangle, Eye, Upload } from 'lucide-react';
import StatusBadge from '../ui/StatusBadge';
import type { DocumentRecord, SecurityInstrument, ShareMode } from '../../types';
import { documents, securities } from '../../data/mockData';

type Requirement = 'mandatory' | 'conditional' | 'not_required';
type CompactState = 'verified' | 'pending' | 'uploaded' | 'signed' | 'not_required' | 'blocked' | 'waived';

interface ChecklistRow {
  id: string;
  name: string;
  required: Requirement;
  owner: string;
  status: CompactState;
  signatureStatus: CompactState;
  stampStatus: CompactState;
  notaryStatus: CompactState;
  verificationStatus: CompactState;
  evidence: string;
  deficiency: string;
  nextAction: string;
  prerequisitesComplete: boolean;
}

interface DocumentChecklistProps {
  applicationId: string;
  shareMode: ShareMode;
  subsidiaryRepayment?: boolean;
  signatureMismatch?: boolean;
  readOnly?: boolean;
  canVerify?: boolean;
  sensitiveVisible?: boolean;
  finalSignoffsComplete?: boolean;
  finalSignoffProgress?: number;
}

const docByType = (docs: DocumentRecord[], type: string) => docs.find(d => d.documentType === type);

const compactStatus = (doc?: DocumentRecord): CompactState => {
  if (!doc) return 'pending';
  if (doc.status === 'rejected') return 'blocked';
  if (['verified', 'complete', 'notarised'].includes(doc.status)) return 'verified';
  if (doc.status === 'signed') return 'signed';
  if (['uploaded', 'under_review'].includes(doc.status)) return 'uploaded';
  return 'pending';
};

const maskGeneric = (val: string) => val.length > 4 ? '•'.repeat(4) + val.slice(-4) : '•'.repeat(val.length);
const mask = (value: string, type: 'pan' | 'aadhaar' | 'acct' | 'ifsc' | 'ref', visible?: boolean) => {
  if (visible) return value;
  if (type === 'ifsc' && value.length > 4) return value.slice(0, 4) + '••••' + value.slice(-3);
  return maskGeneric(value);
};

const isDocVerified = (doc?: DocumentRecord) => !!doc && ['verified', 'complete', 'notarised'].includes(doc.status);
const verifiedTrail = (doc?: DocumentRecord) =>
  doc?.verifiedBy && doc.verifiedAt ? `${doc.verifiedBy} · ${new Date(doc.verifiedAt).toLocaleDateString('en-IN')}` : '';
const securityByType = (items: SecurityInstrument[], type: string) => items.find(item => item.securityType === type);
const shortStatus = (status: CompactState) => status.replace(/_/g, ' ');
const executionSummary = (row: ChecklistRow) => [
  row.signatureStatus !== 'not_required' ? `Sig ${shortStatus(row.signatureStatus)}` : null,
  row.stampStatus !== 'not_required' ? `Stamp ${shortStatus(row.stampStatus)}` : null,
  row.notaryStatus !== 'not_required' ? `Notary ${shortStatus(row.notaryStatus)}` : null,
  row.verificationStatus !== 'not_required' ? `Verify ${shortStatus(row.verificationStatus)}` : null,
].filter(Boolean);

const DocumentChecklist: React.FC<DocumentChecklistProps> = ({
  applicationId,
  shareMode,
  subsidiaryRepayment = true,
  signatureMismatch = true,
  readOnly = false,
  canVerify = false,
  sensitiveVisible = false,
  finalSignoffsComplete = false,
  finalSignoffProgress = 0,
}) => {
  const docs = documents.filter(d => d.applicationId === applicationId);
  const appSecurities = securities.filter(s => s.applicationId === applicationId);
  const pan = docByType(docs, 'pan');
  const aadhaar = docByType(docs, 'aadhaar');
  const nomineePan = docByType(docs, 'nominee_pan');
  const nomineeAadhaar = docByType(docs, 'nominee_aadhaar');
  const witnessPan = docByType(docs, 'witness_pan');
  const witnessAadhaar = docByType(docs, 'witness_aadhaar');
  const poa = docByType(docs, 'poa');
  const triParty = docByType(docs, 'tri_party');
  const sh4 = docByType(docs, 'sh4');
  const termSheet = docByType(docs, 'term_sheet');
  const loanAgreement = docByType(docs, 'loan_agreement');
  const cancelledCheque = docByType(docs, 'cancelled_cheque');
  const blankCheque = docByType(docs, 'blank_cheque');
  const bankVerification = docByType(docs, 'bank_verification_letter');
  const sh4Security = securityByType(appSecurities, 'sh4');
  const cdslSecurity = securityByType(appSecurities, 'cdsl_pledge');
  const sh4Ready = shareMode !== 'physical' || (isDocVerified(sh4) && sh4Security?.status === 'held');
  const cdslReady = shareMode !== 'demat' || cdslSecurity?.status === 'pledged';

  const rows: ChecklistRow[] = [
    {
      id: 'borrower-kyc',
      name: 'Borrower PAN / Aadhaar',
      required: 'mandatory',
      owner: 'Credit / Compliance',
      status: isDocVerified(pan) && isDocVerified(aadhaar) ? 'verified' : 'pending',
      signatureStatus: 'not_required',
      stampStatus: 'not_required',
      notaryStatus: 'not_required',
      verificationStatus: isDocVerified(pan) && isDocVerified(aadhaar) ? 'verified' : 'pending',
      evidence: `${mask('ABCDE1234F', 'pan', sensitiveVisible)} / Aadhaar ${mask('452188884521', 'aadhaar', sensitiveVisible)}`,
      deficiency: pan && aadhaar ? verifiedTrail(pan) || '-' : 'Borrower KYC pending',
      nextAction: isDocVerified(pan) && isDocVerified(aadhaar) ? 'View' : 'Upload',
      prerequisitesComplete: isDocVerified(pan) && isDocVerified(aadhaar),
    },
    {
      id: 'nominee-kyc',
      name: 'Nominee PAN / Aadhaar',
      required: 'mandatory',
      owner: 'Credit / Compliance',
      status: isDocVerified(nomineePan) && isDocVerified(nomineeAadhaar) ? 'verified' : 'pending',
      signatureStatus: 'not_required',
      stampStatus: 'not_required',
      notaryStatus: 'not_required',
      verificationStatus: isDocVerified(nomineePan) && isDocVerified(nomineeAadhaar) ? 'verified' : 'pending',
      evidence: `${mask('FGHIJ5678K', 'pan', sensitiveVisible)} / Aadhaar ${mask('778944447789', 'aadhaar', sensitiveVisible)}`,
      deficiency: nomineePan && nomineeAadhaar ? verifiedTrail(nomineePan) || '-' : 'Nominee KYC pending',
      nextAction: isDocVerified(nomineePan) && isDocVerified(nomineeAadhaar) ? 'View' : 'Upload',
      prerequisitesComplete: isDocVerified(nomineePan) && isDocVerified(nomineeAadhaar),
    },
    {
      id: 'witness-kyc',
      name: 'Witness PAN / Aadhaar',
      required: 'mandatory',
      owner: 'Compliance',
      status: isDocVerified(witnessPan) && isDocVerified(witnessAadhaar) ? 'verified' : 'uploaded',
      signatureStatus: 'not_required',
      stampStatus: 'not_required',
      notaryStatus: 'not_required',
      verificationStatus: isDocVerified(witnessPan) && isDocVerified(witnessAadhaar) ? 'verified' : 'pending',
      evidence: `${mask('WITNS1234Q', 'pan', sensitiveVisible)} / shareholder check`,
      deficiency: isDocVerified(witnessPan) && isDocVerified(witnessAadhaar) ? verifiedTrail(witnessPan) || '-' : 'Witness shareholder validation pending',
      nextAction: isDocVerified(witnessPan) && isDocVerified(witnessAadhaar) ? 'View' : 'Verify',
      prerequisitesComplete: isDocVerified(witnessPan) && isDocVerified(witnessAadhaar),
    },
    {
      id: 'cancelled-cheque',
      name: 'Cancelled cheque',
      required: 'mandatory',
      owner: 'Compliance / Finance',
      status: compactStatus(cancelledCheque),
      signatureStatus: 'not_required',
      stampStatus: 'not_required',
      notaryStatus: 'not_required',
      verificationStatus: compactStatus(cancelledCheque),
      evidence: `Acct ${mask('99990001', 'acct', sensitiveVisible)} / IFSC ${mask('RATN0000001', 'ifsc', sensitiveVisible)}`,
      deficiency: compactStatus(cancelledCheque) === 'verified' ? verifiedTrail(cancelledCheque) || '-' : 'Bank proof pending',
      nextAction: 'View',
      prerequisitesComplete: compactStatus(cancelledCheque) === 'verified',
    },
    {
      id: 'blank-cheque',
      name: 'Blank-dated cheque custody',
      required: 'mandatory',
      owner: 'Company Secretary',
      status: compactStatus(blankCheque),
      signatureStatus: 'not_required',
      stampStatus: 'not_required',
      notaryStatus: 'not_required',
      verificationStatus: compactStatus(blankCheque),
      evidence: `Custody ref ${mask('BCHQ-0042', 'ref', sensitiveVisible)}`,
      deficiency: compactStatus(blankCheque) === 'verified' ? verifiedTrail(blankCheque) || '-' : 'Custody not logged',
      nextAction: 'View',
      prerequisitesComplete: compactStatus(blankCheque) === 'verified',
    },
    {
      id: 'poa',
      name: 'Power of Attorney',
      required: 'mandatory',
      owner: 'Compliance / CS',
      status: compactStatus(poa) === 'verified' ? 'verified' : 'pending',
      signatureStatus: poa?.status === 'signed' || compactStatus(poa) === 'verified' ? 'signed' : 'pending',
      stampStatus: poa?.stampStatus === 'complete' ? 'verified' : 'pending',
      notaryStatus: poa?.notarisationStatus === 'complete' ? 'verified' : 'pending',
      verificationStatus: compactStatus(poa) === 'verified' ? 'verified' : 'pending',
      evidence: poa?.status === 'signed' && (poa?.stampStatus !== 'complete' || poa?.notarisationStatus !== 'complete') ? 'Signature complete · Stamp pending · Notary pending · CS verification pending' : 'PoA draft / custody CS cabinet A',
      deficiency: poa?.stampStatus === 'complete' && poa?.notarisationStatus === 'complete' ? verifiedTrail(poa) || '-' : 'Stamp or notary pending',
      nextAction: compactStatus(poa) === 'verified' ? 'View' : (poa?.status === 'signed' ? 'Mark stamped' : 'Locked (signature pending)'),
      prerequisitesComplete: compactStatus(poa) === 'verified' && poa?.stampStatus === 'complete' && poa?.notarisationStatus === 'complete',
    },
    {
      id: 'tri-party',
      name: 'Tri-party Agreement',
      required: subsidiaryRepayment ? 'conditional' : 'not_required',
      owner: 'Compliance / CS',
      status: subsidiaryRepayment ? compactStatus(triParty) : 'not_required',
      signatureStatus: subsidiaryRepayment ? (compactStatus(triParty) === 'verified' ? 'signed' : 'pending') : 'not_required',
      stampStatus: 'not_required',
      notaryStatus: 'not_required',
      verificationStatus: subsidiaryRepayment ? compactStatus(triParty) : 'not_required',
      evidence: subsidiaryRepayment ? 'Subsidiary deduction agreement' : '-',
      deficiency: subsidiaryRepayment && compactStatus(triParty) !== 'verified' ? 'All party signatures pending' : verifiedTrail(triParty) || '-',
      nextAction: subsidiaryRepayment ? (compactStatus(triParty) === 'verified' ? 'View' : 'Upload') : 'No action',
      prerequisitesComplete: !subsidiaryRepayment || compactStatus(triParty) === 'verified',
    },
    {
      id: 'sh4',
      name: 'SH-4 physical share security',
      required: shareMode === 'physical' ? 'conditional' : 'not_required',
      owner: 'Company Secretary',
      status: shareMode === 'physical' ? (sh4Ready ? 'verified' : compactStatus(sh4)) : 'not_required',
      signatureStatus: shareMode === 'physical' ? (isDocVerified(sh4) ? 'signed' : 'pending') : 'not_required',
      stampStatus: 'not_required',
      notaryStatus: 'not_required',
      verificationStatus: shareMode === 'physical' ? compactStatus(sh4) : 'not_required',
      evidence: shareMode === 'physical' ? `Folio ${mask('FO-0334', 'ref', sensitiveVisible)} / cert ${mask('SC-7781', 'ref', sensitiveVisible)}` : '-',
      deficiency: shareMode === 'physical' && !sh4Ready ? 'Witness signature or custody pending' : verifiedTrail(sh4) || '-',
      nextAction: shareMode === 'physical' ? (sh4Ready ? 'View' : 'Assign custody') : 'No action',
      prerequisitesComplete: sh4Ready,
    },
    {
      id: 'cdsl',
      name: 'CDSL pledge acceptance pending',
      required: shareMode === 'demat' ? 'conditional' : 'not_required',
      owner: 'Company Secretary',
      status: shareMode === 'demat' ? (cdslReady ? 'verified' : 'pending') : 'not_required',
      signatureStatus: 'not_required',
      stampStatus: 'not_required',
      notaryStatus: 'not_required',
      verificationStatus: shareMode === 'demat' ? (cdslReady ? 'verified' : 'pending') : 'not_required',
      evidence: shareMode === 'demat' ? `BO ${mask('120816000042', 'ref', sensitiveVisible)} / PSN ${cdslSecurity?.psnNumber ? mask(cdslSecurity.psnNumber, 'ref', sensitiveVisible) : 'pending'}` : 'Physical shares selected',
      deficiency: shareMode === 'demat' && !cdslReady ? 'DP acceptance pending' : '-',
      nextAction: shareMode === 'demat' ? (cdslReady ? 'View' : 'Verify acceptance') : 'No action',
      prerequisitesComplete: shareMode === 'physical' || cdslReady,
    },
    {
      id: 'term-sheet',
      name: 'Term Sheet',
      required: 'mandatory',
      owner: 'Compliance',
      status: compactStatus(termSheet),
      signatureStatus: compactStatus(termSheet) === 'verified' ? 'signed' : 'pending',
      stampStatus: 'not_required',
      notaryStatus: 'not_required',
      verificationStatus: compactStatus(termSheet),
      evidence: 'Borrower, nominee, CFO/director route',
      deficiency: compactStatus(termSheet) === 'verified' ? verifiedTrail(termSheet) || '-' : 'Signature route pending',
      nextAction: 'Route signatures',
      prerequisitesComplete: compactStatus(termSheet) === 'verified',
    },
    {
      id: 'loan-agreement',
      name: 'Loan Agreement',
      required: 'mandatory',
      owner: 'Compliance / CS',
      status: compactStatus(loanAgreement),
      signatureStatus: compactStatus(loanAgreement) === 'verified' ? 'signed' : 'pending',
      stampStatus: loanAgreement?.stampStatus === 'complete' ? 'verified' : 'pending',
      notaryStatus: loanAgreement?.notarisationStatus === 'complete' ? 'verified' : 'pending',
      verificationStatus: compactStatus(loanAgreement),
      evidence: `Stamp ${mask('ESTAMP-2026-0043', 'ref', sensitiveVisible)}`,
      deficiency: compactStatus(loanAgreement) === 'verified' ? verifiedTrail(loanAgreement) || '-' : 'Borrower/witness signature, stamp and notary required',
      nextAction: compactStatus(loanAgreement) === 'verified' ? 'View' : 'Upload signed copy',
      prerequisitesComplete: compactStatus(loanAgreement) === 'verified' && loanAgreement?.stampStatus === 'complete' && loanAgreement?.notarisationStatus === 'complete',
    },
    {
      id: 'bank-verification',
      name: 'Bank Verification Letter / declaration',
      required: signatureMismatch ? 'conditional' : 'not_required',
      owner: 'Credit / Compliance',
      status: signatureMismatch ? compactStatus(bankVerification) : 'not_required',
      signatureStatus: signatureMismatch ? 'pending' : 'not_required',
      stampStatus: signatureMismatch ? 'pending' : 'not_required',
      notaryStatus: 'not_required',
      verificationStatus: signatureMismatch ? compactStatus(bankVerification) : 'not_required',
      evidence: signatureMismatch ? `Mismatch: cheque vs PAN / acct ${mask('99991234', 'acct', sensitiveVisible)}` : '-',
      deficiency: signatureMismatch && compactStatus(bankVerification) !== 'verified' ? 'Resolution document pending' : verifiedTrail(bankVerification) || '-',
      nextAction: signatureMismatch ? (compactStatus(bankVerification) === 'verified' ? 'View' : 'Upload') : 'View only',
      prerequisitesComplete: !signatureMismatch || compactStatus(bankVerification) === 'verified',
    },
    {
      id: 'final-signatures',
      name: 'Final checklist signatures',
      required: 'mandatory',
      owner: 'CS / Credit / Sanction / Finance',
      status: finalSignoffsComplete ? 'verified' : 'pending',
      signatureStatus: finalSignoffsComplete ? 'signed' : 'pending',
      stampStatus: 'not_required',
      notaryStatus: 'not_required',
      verificationStatus: finalSignoffsComplete ? 'verified' : 'pending',
      evidence: `${finalSignoffProgress}/4 sign-offs`,
      deficiency: finalSignoffsComplete ? '-' : 'Final sign-offs incomplete',
      nextAction: finalSignoffsComplete ? 'View' : 'Submit to CS',
      prerequisitesComplete: finalSignoffsComplete,
    },
  ];

  const blockingRows = rows.filter(row => row.required !== 'not_required' && !row.prerequisitesComplete);

  const markVerifiedDisabled = (row: ChecklistRow) =>
    readOnly || !canVerify || !row.prerequisitesComplete || row.verificationStatus === 'verified';

  return (
    <div className="space-y-3">
      {blockingRows.length > 0 && (
        <div className="flex items-center gap-2 bg-red-50 border border-red-200 rounded-lg px-4 py-3">
          <AlertTriangle size={16} className="text-red-600 flex-shrink-0" />
          <p className="text-sm text-red-800 font-medium">
            Disbursement blocked: {blockingRows.length} documentation items pending. Primary blocker: {blockingRows[0].name.includes('verification') ? blockingRows[0].name : `${blockingRows[0].name} verification`}.
          </p>
        </div>
      )}

      <div className="border border-slate-200 rounded-lg overflow-hidden">
        <table className="w-full text-sm table-fixed">
          <thead className="bg-slate-50">
            <tr>
              <th className="table-header text-left w-[24%]">Document</th>
              <th className="table-header text-left w-[17%]">Requirement</th>
              <th className="table-header text-left w-[19%]">Readiness</th>
              <th className="table-header text-left w-[28%]">Evidence / Deficiency</th>
              <th className="table-header text-left w-[12%]">
                <span title="Immediate allowed action. Later steps stay locked until prerequisites pass." className="border-b border-dotted border-slate-400 cursor-help">
                  Action
                </span>
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {[
              { name: 'Identity & KYC', rowIds: ['borrower-kyc', 'nominee-kyc', 'witness-kyc'] },
              { name: 'Bank & Custody', rowIds: ['cancelled-cheque', 'blank-cheque', 'bank-verification'] },
              { name: 'Legal Documents', rowIds: ['poa', 'tri-party', 'term-sheet', 'loan-agreement'] },
              { name: 'Security Documents', rowIds: ['sh4', 'cdsl'] },
              { name: 'Final Sign-off', rowIds: ['final-signatures'] }
            ].map(group => (
              <React.Fragment key={group.name}>
                <tr className="bg-slate-100/50">
                  <td colSpan={5} className="px-4 py-2 text-xs font-semibold text-slate-700 uppercase tracking-wider">
                    {group.name}
                  </td>
                </tr>
                {group.rowIds.map(rowId => {
                  const row = rows.find(r => r.id === rowId)!;
                  const details = executionSummary(row);
                  const canMarkVerified = !markVerifiedDisabled(row);

                  return (
                    <tr key={row.id} className="hover:bg-slate-50 align-top">
                      <td className="table-cell">
                    <div className="font-medium text-slate-900">{row.name}</div>
                    {row.prerequisitesComplete && row.status !== 'verified' && row.status !== 'signed' && (
                      <div className="text-xs text-green-700 mt-1">Ready for gate</div>
                    )}
                  </td>
                  <td className="table-cell">
                    <StatusBadge label={row.required} size="sm" />
                    <div className="text-xs text-slate-500 mt-1">{row.owner}</div>
                  </td>
                  <td className="table-cell">
                    <StatusBadge label={row.status} size="sm" />
                    <div className="text-xs text-slate-500 mt-1 leading-relaxed">
                      {details.length > 0 ? details.join(' · ') : 'No execution controls'}
                    </div>
                  </td>
                  <td className="table-cell">
                    <div className="text-xs text-slate-600 truncate" title={row.evidence}>{row.evidence}</div>
                    {row.deficiency !== '-' && (
                      <div className={row.prerequisitesComplete ? 'text-xs text-slate-400 mt-1 truncate' : 'text-xs text-amber-700 mt-1 truncate'} title={row.deficiency}>
                        {row.deficiency}
                      </div>
                    )}
                  </td>
                  <td className="table-cell">
                    <div className="flex flex-col items-start gap-1">
                      {row.nextAction !== 'None' && row.status !== 'not_required' && (
                        <button
                          className="text-xs px-2 py-1 border border-slate-200 rounded text-slate-600 hover:bg-slate-50 disabled:opacity-50"
                          disabled={readOnly}
                          title={readOnly ? 'Read-only role' : row.nextAction}
                        >
                          {row.nextAction === 'View' || row.nextAction === 'View only' ? <span className="inline-flex items-center gap-1"><Eye size={12} /> View</span> : row.nextAction.includes('Upload') ? <span className="inline-flex items-center gap-1"><Upload size={12} /> Upload</span> : row.nextAction}
                        </button>
                      )}
                      {canMarkVerified && row.required !== 'not_required' && row.nextAction === 'Verify' && (
                        <button
                          className="text-xs px-2 py-1 bg-blue-50 border border-blue-200 rounded text-blue-700 hover:bg-blue-100"
                          title="Mark verified"
                        >
                          Verify
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              );
            })}
          </React.Fragment>
        ))}
      </tbody>
        </table>
      </div>
    </div>
  );
};

export default DocumentChecklist;
