import React, { useCallback, useEffect, useState } from 'react';
import { AlertTriangle, CheckCircle2, Clock, Scale, Shield, XCircle } from 'lucide-react';
import AlertBanner from '../../components/ui/AlertBanner';
import StatusBadge from '../../components/ui/StatusBadge';
import { AuthSessionError } from '../../services/authSession';
import {
  fetchComplianceDashboard,
  reviewComplianceEvidence,
  reviewNbfcPrincipalTest,
  reviewSection186Tracker,
  type ComplianceDashboardProjection,
  type ComplianceTaskProjection,
} from '../../services/recoveryApi';

const money = new Intl.NumberFormat('en-IN', {
  style: 'currency',
  currency: 'INR',
  minimumFractionDigits: 2,
});
const date = new Intl.DateTimeFormat('en-IN', {
  day: '2-digit',
  month: 'short',
  year: 'numeric',
});

const statusIcon = (status: string) => {
  if (['active', 'accepted', 'adequate', 'completed'].includes(status)) {
    return <CheckCircle2 size={16} className="text-green-600" />;
  }
  if (['overdue', 'rejected', 'insufficient'].includes(status)) {
    return <XCircle size={16} className="text-red-600" />;
  }
  if (['warning', 'evidence_submitted'].includes(status)) {
    return <AlertTriangle size={16} className="text-amber-500" />;
  }
  return <Clock size={16} className="text-slate-400" />;
};

const statusBackground = (status: string) => {
  if (['active', 'accepted', 'adequate', 'completed'].includes(status)) {
    return 'bg-green-50 border-green-200';
  }
  if (['overdue', 'rejected', 'insufficient'].includes(status)) {
    return 'bg-red-50 border-red-200';
  }
  if (['warning', 'evidence_submitted'].includes(status)) {
    return 'bg-amber-50 border-amber-200';
  }
  return 'bg-slate-50 border-slate-200';
};

const tasksForControl = (
  tasks: ComplianceTaskProjection[],
  controlId: string,
) => tasks.filter(task => task.compliance_control_id === controlId);

type ReviewTarget = {
  kind: 'evidence' | 'section186' | 'nbfc';
  id: string;
  label: string;
};

const ComplianceDashboard: React.FC = () => {
  const [projection, setProjection] = useState<ComplianceDashboardProjection | null>(null);
  const [loadError, setLoadError] = useState<Error | null>(null);
  const [reviewTarget, setReviewTarget] = useState<ReviewTarget | null>(null);
  const [reviewDecision, setReviewDecision] = useState<'accepted' | 'rejected'>('accepted');
  const [reviewComments, setReviewComments] = useState('');
  const [presentedToBoard, setPresentedToBoard] = useState(false);
  const [boardDocumentId, setBoardDocumentId] = useState('');
  const [reviewBusy, setReviewBusy] = useState(false);
  const [reviewError, setReviewError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  const loadDashboard = useCallback(async () => {
    try {
      setProjection(await fetchComplianceDashboard());
      setLoadError(null);
    } catch (error) {
      setLoadError(error instanceof Error ? error : new Error('Compliance trackers could not be loaded.'));
    }
  }, []);

  useEffect(() => {
    void loadDashboard();
  }, [loadDashboard]);

  const openReview = (target: ReviewTarget) => {
    setReviewTarget(target);
    setReviewDecision('accepted');
    setReviewComments('');
    setPresentedToBoard(false);
    setBoardDocumentId('');
    setReviewError('');
    setSuccessMessage('');
  };

  const submitReview = async () => {
    if (!reviewTarget) return;
    const comments = reviewComments.trim();
    if (!comments) {
      setReviewError('Review comments are required.');
      return;
    }
    if (presentedToBoard && !boardDocumentId.trim()) {
      setReviewError('Governed Board document ID is required when Board presentation is selected.');
      return;
    }
    setReviewBusy(true);
    setReviewError('');
    setSuccessMessage('');
    try {
      if (reviewTarget.kind === 'evidence') {
        await reviewComplianceEvidence(reviewTarget.id, {
          review_status: reviewDecision,
          review_comments: comments,
        });
      } else {
        const input = {
          decision: reviewDecision,
          comments,
          presented_to_board_flag: presentedToBoard,
          board_document_id: boardDocumentId.trim() || null,
        };
        if (reviewTarget.kind === 'section186') {
          await reviewSection186Tracker(reviewTarget.id, input);
        } else {
          await reviewNbfcPrincipalTest(reviewTarget.id, input);
        }
      }
      await loadDashboard();
      setReviewTarget(null);
      setSuccessMessage('Compliance review saved from canonical backend state.');
    } catch (error) {
      const fieldMessage = error instanceof AuthSessionError
        ? Object.values(error.fieldErrors ?? {})[0]
        : undefined;
      setReviewError(
        fieldMessage
        || (error instanceof Error ? error.message : 'Compliance review could not be saved.'),
      );
    } finally {
      setReviewBusy(false);
    }
  };

  if (loadError) {
    const denied = loadError instanceof AuthSessionError
      && [401, 403].includes(loadError.status ?? 0);
    return (
      <div className="card p-8 text-center">
        <h2 className="font-semibold text-slate-900">
          {denied ? 'Access Denied' : 'Compliance Dashboard Unavailable'}
        </h2>
        <p className="text-sm text-slate-500 mt-1">{loadError.message}</p>
      </div>
    );
  }

  if (!projection) {
    return <div className="card p-8 text-center text-slate-500">Loading compliance trackers…</div>;
  }

  const overdueCount = projection.tasks.filter(task => task.task_status === 'overdue').length
    + projection.kycReviews.filter(review => review.status === 'overdue').length;
  const breachCount = projection.section186.filter(row => !row.within_limit_flag).length
    + projection.nbfcTests.filter(row => row.registration_triggered_flag).length;
  const kycCounts = {
    completed: projection.kycReviews.filter(row => row.status === 'completed').length,
    due: projection.kycReviews.filter(row => row.status === 'due').length,
    warning: projection.kycReviews.filter(row => row.status === 'warning').length,
    overdue: projection.kycReviews.filter(row => row.status === 'overdue').length,
  };

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-xl font-bold text-slate-900">Compliance Dashboard</h1>
        <p className="text-sm text-slate-500 mt-0.5">
          Regulatory compliance, Section 186, NBFC test, and KYC tracker
        </p>
      </div>

      {breachCount > 0 && (
        <AlertBanner
          type="error"
          title={`${breachCount} compliance breach${breachCount > 1 ? 'es' : ''} require immediate attention`}
          message="Review the backend-owned statutory tracker evidence."
        />
      )}
      {breachCount === 0 && overdueCount > 0 && (
        <AlertBanner
          type="warning"
          title={`${overdueCount} compliance review${overdueCount > 1 ? 's' : ''} need attention`}
          message="Review due items before their deadlines."
        />
      )}
      {successMessage && (
        <AlertBanner type="success" title={successMessage} />
      )}
      {reviewTarget && (
        <div className="card">
          <div className="flex items-center justify-between gap-4 mb-4">
            <div>
              <h2 className="section-title">{reviewTarget.label}</h2>
              <p className="text-xs text-slate-500 mt-1">
                Record the projected maker-checker review; canonical state is reloaded after save.
              </p>
            </div>
            <button type="button" className="btn-secondary" onClick={() => setReviewTarget(null)}>
              Cancel
            </button>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label htmlFor="compliance-review-decision" className="field-label">Decision</label>
              <select
                id="compliance-review-decision"
                className="field-input"
                value={reviewDecision}
                onChange={event => setReviewDecision(event.target.value as 'accepted' | 'rejected')}
              >
                <option value="accepted">Accepted</option>
                <option value="rejected">Rejected</option>
              </select>
            </div>
            <div>
              <label htmlFor="compliance-review-comments" className="field-label">
                Review comments
              </label>
              <textarea
                id="compliance-review-comments"
                className="field-input resize-none"
                value={reviewComments}
                onChange={event => setReviewComments(event.target.value)}
              />
            </div>
            {reviewTarget.kind !== 'evidence' && (
              <>
                <label className="flex items-center gap-2 text-sm text-slate-700">
                  <input
                    type="checkbox"
                    checked={presentedToBoard}
                    onChange={event => setPresentedToBoard(event.target.checked)}
                  />
                  Presented to Board
                </label>
                <div>
                  <label htmlFor="compliance-board-document" className="field-label">
                    Board document ID
                  </label>
                  <input
                    id="compliance-board-document"
                    className="field-input"
                    value={boardDocumentId}
                    onChange={event => setBoardDocumentId(event.target.value)}
                  />
                </div>
              </>
            )}
          </div>
          {reviewError && <p className="text-xs text-red-600 font-medium mt-3">{reviewError}</p>}
          <button
            type="button"
            className="btn-primary mt-4"
            disabled={reviewBusy}
            onClick={() => void submitReview()}
          >
            {reviewBusy ? 'Saving…' : 'Submit Review'}
          </button>
        </div>
      )}

      <div className="card">
        <h2 className="section-title mb-4 flex items-center gap-2">
          <Shield size={16} className="text-green-600" />
          Section 186 — Aggregate Lending Limit
        </h2>
        {projection.section186.length > 0 ? (
          <div className="space-y-4">
            {projection.section186.map(row => (
              <div key={row.section_186_tracker_id} className="border-t border-slate-100 pt-4 first:border-0 first:pt-0">
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-3">
                  {row.financial_year} · {row.quarter}
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  <div className="bg-slate-50 rounded-lg border border-slate-200 p-4">
                    <p className="text-xs text-slate-500 font-medium uppercase tracking-wide">Capital base</p>
                    <p className="text-lg font-bold text-slate-900 num mt-1">
                      {money.format(Number(row.paid_up_capital_amount))}
                    </p>
                    <p className="text-xs text-slate-500 mt-1">
                      Reserves {money.format(Number(row.free_reserves_amount))}
                    </p>
                    <p className="text-xs text-slate-500">
                      Premium {money.format(Number(row.securities_premium_amount))}
                    </p>
                  </div>
                  <div className="bg-slate-50 rounded-lg border border-slate-200 p-4">
                    <p className="text-xs text-slate-500 font-medium uppercase tracking-wide">Section 186 limit</p>
                    <p className="text-lg font-bold text-slate-900 num mt-1">
                      {money.format(Number(row.applicable_limit_amount))}
                    </p>
                    <p className="text-xs text-slate-500 mt-1">
                      60% basis {money.format(Number(row.limit_60_percent_basis_amount))}
                    </p>
                    <p className="text-xs text-slate-500">
                      100% basis {money.format(Number(row.limit_100_percent_basis_amount))}
                    </p>
                  </div>
                  <div className={`rounded-lg border p-4 ${
                    row.within_limit_flag
                      ? 'bg-green-50 border-green-200'
                      : 'bg-red-50 border-red-200'
                  }`}>
                    <p className="text-xs text-slate-600 font-medium uppercase tracking-wide">Exposure</p>
                    <p className="text-lg font-bold text-slate-900 num mt-1">
                      {money.format(Number(row.total_loans_exposure_amount))}
                    </p>
                    <p className="text-xs text-slate-600 mt-1">
                      Headroom {money.format(Number(row.headroom_amount))}
                    </p>
                    <div className="mt-2">
                      <StatusBadge
                        label={row.within_limit_flag ? row.review_status : 'resolution required'}
                        size="sm"
                        type={row.within_limit_flag ? undefined : 'error'}
                      />
                    </div>
                  </div>
                </div>
                {row.available_actions.includes('review') && (
                  <button
                    type="button"
                    className="btn-secondary mt-3"
                    onClick={() => openReview({
                      kind: 'section186',
                      id: row.section_186_tracker_id,
                      label: `Section 186 Review · ${row.financial_year} ${row.quarter}`,
                    })}
                  >
                    Review Section 186
                  </button>
                )}
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-slate-500">No Section 186 tracker is available.</p>
        )}
      </div>

      <div className="card">
        <h2 className="section-title mb-4">NBFC Principal Business Test</h2>
        {projection.nbfcTests.length > 0 ? (
          <div className="space-y-4">
            {projection.nbfcTests.map(row => (
              <div key={row.nbfc_principal_test_id} className="border-t border-slate-100 pt-4 first:border-0 first:pt-0">
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-3">
                  {row.financial_year} · {row.quarter}
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {[
                    {
                      label: 'Financial assets threshold',
                      amount: row.financial_assets_amount,
                      total: row.total_assets_amount,
                      ratio: row.financial_asset_ratio,
                    },
                    {
                      label: 'Financial income threshold',
                      amount: row.financial_income_amount,
                      total: row.gross_income_amount,
                      ratio: row.financial_income_ratio,
                    },
                  ].map(metric => (
                    <div
                      key={metric.label}
                      className={`border rounded-lg p-4 ${
                        row.registration_triggered_flag
                          ? 'bg-red-50 border-red-200'
                          : row.early_warning_flag
                            ? 'bg-amber-50 border-amber-200'
                            : 'bg-green-50 border-green-200'
                      }`}
                    >
                      {statusIcon(row.registration_triggered_flag ? 'overdue' : row.early_warning_flag ? 'warning' : 'accepted')}
                      <p className="text-sm font-semibold text-slate-900 mt-2">{metric.label}</p>
                      <p className="text-xl font-bold num text-slate-900 mt-1">{metric.ratio}%</p>
                      <p className="text-xs text-slate-600 mt-1">
                        {money.format(Number(metric.amount))} of {money.format(Number(metric.total))}
                      </p>
                      <p className="text-xs text-slate-500 mt-1">
                        Early warning {row.early_warning_threshold_ratio}%
                      </p>
                    </div>
                  ))}
                </div>
                <p className="text-xs text-slate-500 mt-3">
                  Board: {row.presented_to_board_flag ? 'Presented' : 'Pending'} · Review: {row.review_status}
                  {row.review_comments ? ` · ${row.review_comments}` : ''}
                </p>
                {row.available_actions.includes('review') && (
                  <button
                    type="button"
                    className="btn-secondary mt-3"
                    onClick={() => openReview({
                      kind: 'nbfc',
                      id: row.nbfc_principal_test_id,
                      label: `NBFC Test Review · ${row.financial_year} ${row.quarter}`,
                    })}
                  >
                    Review NBFC Test
                  </button>
                )}
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-slate-500">No NBFC test is available.</p>
        )}
      </div>

      <div className="card">
        <h2 className="section-title mb-4">KYC & Re-KYC Tracker</h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-4">
          {[
            ['Completed', kycCounts.completed, 'bg-green-50 border-green-200 text-green-900'],
            ['Due', kycCounts.due, 'bg-slate-50 border-slate-200 text-slate-900'],
            ['30-day warning', kycCounts.warning, 'bg-amber-50 border-amber-200 text-amber-900'],
            ['Overdue', kycCounts.overdue, 'bg-red-50 border-red-200 text-red-900'],
          ].map(([label, count, classes]) => (
            <div key={String(label)} className={`rounded-lg border p-3 text-center ${classes}`}>
              <div className="text-xl font-bold num">{count}</div>
              <div className="text-xs font-medium mt-0.5">{label}</div>
            </div>
          ))}
        </div>
        {projection.kycReviews.length > 0 ? (
          <div className="border border-slate-200 rounded-lg overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-100">
                  <th className="table-header text-left">Member</th>
                  <th className="table-header text-left">KYC status</th>
                  <th className="table-header text-left">PAN</th>
                  <th className="table-header text-left">CKYC consent</th>
                  <th className="table-header text-left">Re-KYC due</th>
                  <th className="table-header text-left">Days overdue</th>
                  <th className="table-header text-left">Risk</th>
                  <th className="table-header text-left">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {projection.kycReviews.map(review => (
                  <tr key={review.kyc_review_id}>
                    <td className="table-cell">
                      <p className="font-medium text-slate-900">{review.member_name}</p>
                      <p className="text-xs text-slate-500">{review.member_type}</p>
                    </td>
                    <td className="table-cell text-slate-600">{review.kyc_status}</td>
                    <td className="table-cell text-slate-600">
                      {String(review.completeness.pan_status || '—')}
                    </td>
                    <td className="table-cell text-slate-600">
                      {String(review.completeness.ckyc_consent_status || '—')}
                    </td>
                    <td className="table-cell text-slate-600">{date.format(new Date(review.due_date))}</td>
                    <td className="table-cell text-slate-600 num">{review.days_overdue}</td>
                    <td className="table-cell text-slate-600">{review.risk_rating || '—'}</td>
                    <td className="table-cell"><StatusBadge label={review.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-sm text-slate-500">No KYC or re-KYC reviews are available.</p>
        )}
      </div>

      <div className="card">
        <h2 className="section-title mb-4 flex items-center gap-2">
          <Scale size={16} className="text-indigo-600" />
          Money-Lending Act — Annual Review
        </h2>
        {projection.moneyLendingReviews.length > 0 ? (
          <div className="space-y-2">
            {projection.moneyLendingReviews.map(review => (
              <div
                key={review.money_lending_law_review_id}
                className="bg-green-50 border border-green-200 rounded-lg p-4"
              >
                <div className="flex items-start gap-2">
                  <CheckCircle2 size={16} className="text-green-600 mt-0.5" />
                  <div>
                    <p className="text-sm font-semibold text-green-900">
                      {review.financial_year} · {review.state}
                    </p>
                    <p className="text-xs text-green-700 mt-1">
                      Applicability: {review.applicability} · reviewed{' '}
                      {date.format(new Date(review.reviewed_at))}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-slate-500">No annual money-lending review is available.</p>
        )}
      </div>

      <div className="card">
        <h2 className="section-title mb-4">Stamp Duty Register</h2>
        {projection.stampDuty.length > 0 ? (
          <div className="border border-slate-200 rounded-lg overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-100">
                  <th className="table-header text-left">Application</th>
                  <th className="table-header text-left">Borrower</th>
                  <th className="table-header text-left">Document</th>
                  <th className="table-header text-left">Stamp value</th>
                  <th className="table-header text-left">Stamp number</th>
                  <th className="table-header text-left">Purchase date</th>
                  <th className="table-header text-left">Stamp</th>
                  <th className="table-header text-left">Notarisation</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {projection.stampDuty.map(record => (
                  <tr key={record.stamp_duty_record_id}>
                    <td className="table-cell font-medium text-slate-900">
                      {record.application_reference_number}
                    </td>
                    <td className="table-cell text-slate-600">{record.borrower_name}</td>
                    <td className="table-cell text-slate-600">
                      {record.document_type.replace(/_/g, ' ')}
                    </td>
                    <td className="table-cell text-slate-600 num">
                      {money.format(Number(record.stamp_paper_amount))}
                    </td>
                    <td className="table-cell text-slate-600">{record.stamp_number || '—'}</td>
                    <td className="table-cell text-slate-600">
                      {record.stamp_purchase_date
                        ? date.format(new Date(record.stamp_purchase_date))
                        : '—'}
                    </td>
                    <td className="table-cell">
                      <StatusBadge label={record.status} size="sm" />
                    </td>
                    <td className="table-cell text-slate-600">
                      {record.notarisation_status || 'Not required'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-sm text-slate-500">No stamp-duty records are available.</p>
        )}
      </div>

      <div>
        <h2 className="section-title mb-3">Compliance Register</h2>
        {projection.controls.length === 0 ? (
          <p className="text-sm text-slate-500">
            No compliance controls are available in your scope.
          </p>
        ) : (
          <div className="space-y-2">
            {projection.controls.map(control => {
              const tasks = tasksForControl(projection.tasks, control.compliance_control_id);
              return (
                <div
                  key={control.compliance_control_id}
                  className={`rounded-lg border p-4 ${statusBackground(control.status)}`}
                >
                  <div className="flex items-start gap-3">
                    <div className="mt-0.5 flex-shrink-0">{statusIcon(control.status)}</div>
                    <div className="flex-1">
                      <p className="text-sm font-semibold text-slate-900">{control.control_name}</p>
                      <p className="text-xs text-slate-500 mt-0.5">
                        Owner: {control.owner_role_code.replace(/_/g, ' ')} · Frequency:{' '}
                        {control.frequency} · Evidence: {control.evidence_required}
                      </p>
                      {tasks.map(task => (
                        <div
                          key={task.compliance_task_id}
                          className="mt-3 border-t border-slate-200 pt-3 flex items-start justify-between gap-4"
                        >
                          <div>
                            <p className="text-xs font-medium text-slate-700">
                              {task.task_period} · Due {date.format(new Date(task.due_date))}
                            </p>
                            {task.remarks && (
                              <p className="text-xs text-slate-500 mt-1">{task.remarks}</p>
                            )}
                            {task.compliance_evidence_id
                              && task.available_actions.includes('review_evidence') && (
                                <button
                                  type="button"
                                  className="btn-secondary mt-3"
                                  onClick={() => openReview({
                                    kind: 'evidence',
                                    id: task.compliance_evidence_id!,
                                    label: `${control.control_name} Evidence Review · ${task.task_period}`,
                                  })}
                                >
                                  Review Evidence
                                </button>
                              )}
                          </div>
                          <StatusBadge label={task.task_status} size="sm" />
                        </div>
                      ))}
                      {tasks.length === 0 && (
                        <p className="text-xs text-slate-500 mt-2">No generated tasks.</p>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default ComplianceDashboard;
