import React from 'react';
import { AlertTriangle, Check, Download, Upload } from 'lucide-react';
import type { DocumentationAction, DocumentationItem } from '../../services/documentationWorkspaceApi';
import StatusBadge from '../ui/StatusBadge';

interface DocumentChecklistProps {
  items: DocumentationItem[];
  busy?: boolean;
  onDownload?: (item: DocumentationItem) => void;
  onAction?: (action: DocumentationAction) => void;
}

const label = (value: string | null) => (value || 'not recorded').replace(/_/g, ' ');

const DocumentChecklist: React.FC<DocumentChecklistProps> = ({
  items,
  busy = false,
  onDownload,
  onAction,
}) => {
  return (
    <div className="space-y-3">
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
            {items.map(item => (
              <tr key={item.item_code} className="hover:bg-slate-50 align-top">
                <td className="table-cell">
                  <div className="font-medium text-slate-900">{item.item_label}</div>
                  {item.document && <div className="text-xs text-slate-500 mt-1">Template version {item.document.version}</div>}
                </td>
                <td className="table-cell">
                  <StatusBadge label={!item.applicable ? 'not_required' : item.required ? 'mandatory' : 'conditional'} size="sm" />
                </td>
                <td className="table-cell">
                  <StatusBadge label={!item.applicable ? 'not_required' : item.status} size="sm" />
                  {item.blocker && (
                    <div className="text-xs text-amber-700 mt-1 truncate" title={label(item.blocker)}>
                      <AlertTriangle size={12} className="inline mr-1" />{label(item.blocker)}
                    </div>
                  )}
                </td>
                <td className="table-cell">
                  <div className="text-xs text-slate-600 truncate">Stamp {label(item.stamp_status)} · Notary {label(item.notarisation_status)}</div>
                  <div className="text-xs text-slate-400 mt-1 truncate">Verification {label(item.document?.verification_status ?? null)}</div>
                </td>
                <td className="table-cell">
                  <div className="flex flex-col items-start gap-1">
                    {item.document?.download && onDownload && (
                      <button className="text-xs px-2 py-1 border border-slate-200 rounded text-slate-600 hover:bg-slate-50 disabled:opacity-50" onClick={() => onDownload(item)} disabled={busy}>
                        <Download size={12} className="inline mr-1" /> Download
                      </button>
                    )}
                    {onAction && item.available_actions.map(action => (
                      <button key={action.action} className="text-xs px-2 py-1 border border-slate-200 rounded text-slate-600 hover:bg-slate-50 disabled:opacity-50" onClick={() => onAction(action)} disabled={busy}>
                        {action.action === 'generate_document' ? <Upload size={12} className="inline mr-1" /> : <Check size={12} className="inline mr-1" />}
                        {action.action === 'generate_document' ? 'Generate document' : action.action === 'complete_item' ? 'Mark complete' : 'Verify document'}
                      </button>
                    ))}
                    {!item.document?.download && item.available_actions.length === 0 && item.applicable && <span className="text-xs text-slate-400">Restricted or no action available</span>}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default DocumentChecklist;
