import { renderToStaticMarkup } from 'react-dom/server';
import { describe, expect, it, vi } from 'vitest';
import { AppraisalWorkbenchView } from './AppraisalWorkbench';
import type { AppraisalNote, EligibilityAssessment, LoanLimitAssessment, SanctionSubmission } from '../../services/creditAssessmentApi';
import type { StaffApplication } from '../../services/applicationIntakeApi';
import workbenchSource from './AppraisalWorkbench.tsx?raw';
import calculatorSource from '../../components/loan/LoanLimitCalculator.tsx?raw';
import intakeSource from '../applications/NewApplication.tsx?raw';

const application = { loan_application_id: 'application-1', application_reference_number: 'LO000001', member: { member_id: 'member-1', display_name: 'API Borrower', member_type: 'individual', folio_number: 'FO-1' }, application_date: '2026-07-10', required_loan_amount: '250000.00', purpose_category: 'crop_production', application_status: 'appraisal_in_progress', current_stage: 'credit_assessment', completeness_status: 'complete' } satisfies StaffApplication;
const eligibility = { eligibility_assessment_id: 'eligibility-1', loan_application_id: 'application-1', member_active_check: 'pass', default_check: 'no_default', document_check: 'complete', terms_acceptance_check: 'accepted', purpose_check: 'agriculture_aligned', nominee_check: 'valid', overall_result: 'eligible', assessment_notes: 'Stored assessment explanation.', assessed_by_user_id: 'user-1', assessed_at: '2026-07-10T10:00:00+05:30' } satisfies EligibilityAssessment;
const loanLimit = { loan_limit_assessment_id: 'limit-1', loan_application_id: 'application-1', member_id: 'member-1', shareholding_id: 'share-1', number_of_shares: 100, valuation_per_share: '2500.00', share_limit_percentage: '10.0000', per_share_cap_amount: '250.00', shareholding_based_limit_amount: '250000.00', land_area_acres: '12.50', scale_of_finance_per_acre_amount: '30000.00', land_based_limit_amount: '375000.00', final_eligible_loan_amount: '250000.00', requested_amount: '250000.00', amount_within_limit_flag: true, exception_required_flag: false, calculation_rule_version: 'board-policy-2026', configuration_source: { type: 'loan_policy_config', loan_policy_config_id: 'policy-1', policy_name: 'Board policy', board_approval_reference: 'BR-01' }, warnings: [], calculated_by_user_id: 'user-1', calculated_at: '2026-07-10T10:05:00+05:30' } satisfies LoanLimitAssessment;
const appraisal = { loan_appraisal_note_id: 'appraisal-1', loan_application_id: 'application-1', eligibility_assessment_id: 'eligibility-1', loan_limit_assessment_id: 'limit-1', eligibility_snapshot: eligibility, loan_limit_snapshot: loanLimit, prerequisite_provenance: 'verified', prepared_by: { user_id: 'user-1', full_name: 'Deputy Manager' }, prepared_at: '2026-07-10T10:10:00+05:30', reviewed_by: null, reviewed_at: null, decision: null, review_comments: null, review_history: [], tat_due_at: '2026-07-12T10:10:00+05:30', tat_status: 'within_tat', borrower_summary: 'Borrower summary', eligibility_summary: 'Eligible', loan_limit_summary: 'Within stored limit', recommended_amount: '250000.00', recommended_tenure_months: 12, recommended_interest_type: 'floating', recommended_security_summary: 'Security', repayment_capacity_notes: 'Capacity', risk_assessment: { risk_assessment_id: 'risk-1', market_risk_rating: 'low', operational_risk_rating: 'low', borrower_risk_rating: 'low', overall_risk_rating: 'low', risk_mitigation_notes: 'Controls', assessed_by_user_id: 'user-1', assessed_at: '2026-07-10T10:10:00+05:30' }, recommendation: 'approve', appraisal_status: 'draft' } satisfies AppraisalNote;
const sanction = { approval_case_id: 'case-006H', loan_application_id: 'application-1', loan_appraisal_note_id: 'appraisal-1', submission_status: 'pending', exception_required_flag: false, submitted_by: { user_id: 'manager-1', full_name: 'Credit Manager' }, submitted_at: '2026-07-10T11:00:00+05:30' } satisfies SanctionSubmission;
const render = (overrides: Partial<React.ComponentProps<typeof AppraisalWorkbenchView>> = {}) => renderToStaticMarkup(<AppraisalWorkbenchView status="success" message="" applications={[application]} selectedApplication={application} eligibility={eligibility} loanLimit={loanLimit} appraisal={appraisal} sanctionSubmission={null} permissions={['credit.appraisal.update', 'credit.appraisal.submit_review', 'credit.risk_assessment.manage']} roleCodes={['deputy_manager_finance']} availableActions={['credit.appraisal.update', 'credit.appraisal.submit_review']} form={appraisal} reviewDecision="reviewed" onSelect={vi.fn()} onField={vi.fn()} onAction={vi.fn()} {...overrides} />);

describe('Appraisal Workbench server-state rendering', () => {
  it.each([['eligible', 'Eligible'], ['ineligible', 'Ineligible'], ['pending_manual_evidence', 'Pending Manual Evidence']])('renders stored %s eligibility', (overall_result, expected) => {
    const html = render({ eligibility: { ...eligibility, overall_result } }); expect(html).toContain(expected); expect(html).toContain('Stored assessment explanation.');
  });
  it.each([['200000.00', true, false, 'within eligible limit'], ['250000.00', true, false, 'within eligible limit'], ['300000.00', false, true, 'exceeds eligible limit']])('renders stored boundary %s', (requested_amount, amount_within_limit_flag, exception_required_flag, expected) => {
    const html = render({ loanLimit: { ...loanLimit, requested_amount, amount_within_limit_flag, exception_required_flag } }); expect(html).toContain(expected); expect(html).toContain('₹2,50,000.00');
  });
  it.each([['draft', 'Save Appraisal Draft'], ['review_pending', 'Record Credit Review'], ['reviewed', 'Submit to Sanction Committee'], ['rejected', 'Appraisal rejected'], ['submitted_to_sanction_committee', 'Submitted to Sanction Committee']])('gates server state %s', (appraisal_status, expected) => {
    const manager = appraisal_status === 'draft' ? {} : { permissions: ['credit.appraisal.review', 'credit.appraisal.submit_sanction'], roleCodes: ['credit_manager'], availableActions: ['credit.appraisal.review', 'credit.appraisal.submit_sanction'] };
    expect(render({ appraisal: { ...appraisal, appraisal_status }, ...manager })).toContain(expected);
  });
  it('preserves ordered review history and returned/rejection facts', () => {
    const review_history = [
      { appraisal_review_decision_id: 'h1', decision: 'returned', review_comments: 'Missing repayment evidence.', reviewer: { user_id: 'm1', full_name: 'Manager' }, decided_at: '2026-07-10T10:00:00+05:30', from_state: 'review_pending', to_state: 'draft', history_provenance: 'native' },
      { appraisal_review_decision_id: 'h2', decision: 'reviewed', review_comments: 'Evidence supplied.', reviewer: { user_id: 'm1', full_name: 'Manager' }, decided_at: '2026-07-10T11:00:00+05:30', from_state: 'review_pending', to_state: 'reviewed', history_provenance: 'native' },
    ];
    const html = render({ appraisal: { ...appraisal, review_history, appraisal_status: 'reviewed' } });
    expect(html.indexOf('Missing repayment evidence.')).toBeLessThan(html.indexOf('Evidence supplied.'));
  });
  it('renders production empty, denied, error, validation and sanction success states', () => {
    expect(render({ status: 'loading' })).toContain('Loading appraisal workbench');
    expect(render({ applications: [], selectedApplication: null, eligibility: null, loanLimit: null, appraisal: null })).toContain('Appraisal queue is clear');
    expect(render({ status: 'denied', message: 'You cannot access this application.' })).toContain('You cannot access this application.');
    expect(render({ status: 'error', message: 'INVALID_STATE_TRANSITION: Refresh.' })).toContain('INVALID_STATE_TRANSITION');
    expect(render({ message: 'recommended_amount: Must be within the frozen limit.' })).toContain('Must be within the frozen limit.');
    expect(render({ sanctionSubmission: sanction })).toContain('case-006H');
  });
  it('separates Deputy Manager, Credit Manager, and no-permission controls', () => {
    expect(render()).toContain('Save Appraisal Draft');
    expect(render({ appraisal: { ...appraisal, appraisal_status: 'review_pending' }, permissions: ['credit.appraisal.review'], roleCodes: ['credit_manager'], availableActions: ['credit.appraisal.review'] })).toContain('Record Credit Review');
    const none = render({ appraisal: { ...appraisal, appraisal_status: 'review_pending' }, permissions: [], roleCodes: [] });
    expect(none).not.toContain('Save Appraisal Draft'); expect(none).not.toContain('Record Credit Review'); expect(none).not.toContain('Submit to Sanction Committee');
  });
  it('requires the dedicated backend legacy revalidation action and update/risk authority', () => {
    const legacy = { ...appraisal, prerequisite_provenance: 'legacy_unverified' };
    expect(render({ appraisal: legacy, form: legacy, availableActions: ['revalidate_appraisal_prerequisites'], permissions: ['credit.appraisal.submit_review'] })).not.toContain('Revalidate Prerequisites');
    expect(render({ appraisal: legacy, form: legacy, availableActions: ['revalidate_appraisal_prerequisites'], permissions: ['credit.appraisal.update', 'credit.risk_assessment.manage'] })).toContain('Revalidate Prerequisites');
  });
  it('hides controls when backend available actions deny them despite usable permissions', () => {
    const html = render({ availableActions: [], permissions: ['credit.eligibility.run', 'credit.loan_limit.calculate', 'credit.appraisal.update', 'credit.risk_assessment.manage', 'credit.appraisal.submit_review'] });
    expect(html).not.toContain('Run Eligibility Assessment');
    expect(html).not.toContain('Calculate Stored Loan Limit');
    expect(html).not.toContain('Save Appraisal Draft');
    expect(html).not.toContain('Submit for Credit Review');
  });
  it('contains no appraisal mock import or frontend loan-limit formula', () => {
    expect(workbenchSource).not.toContain('data/mockData'); expect(`${calculatorSource}${intakeSource}`).not.toMatch(/SHAREHOLDING_PERCENTAGE|SCALE_OF_FINANCE_PER_ACRE|maximumPermissibleLimit/);
  });
});
