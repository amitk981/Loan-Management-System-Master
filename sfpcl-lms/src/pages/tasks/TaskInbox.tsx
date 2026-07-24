import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import {
  AlertTriangle,
  ArrowRight,
  Ban,
  CheckCircle2,
  Clock,
  Filter,
  Inbox,
  MessageSquare,
  MoreVertical,
  RefreshCw,
  UserPlus,
} from 'lucide-react';
import type { Page } from '../../services/navigationPermissions';
import { AuthSessionError, type Pagination } from '../../services/authSession';
import {
  fetchTaskInbox,
  submitTaskAction,
  type TaskInboxQuery,
  type TaskPriority,
  type TaskType,
  type WorkflowTaskRow,
} from '../../services/taskInboxApi';
import AlertBanner from '../../components/ui/AlertBanner';
import Modal from '../../components/ui/Modal';
import StatusBadge from '../../components/ui/StatusBadge';
import { useRole } from '../../contexts/RoleContext';

type LoadState = 'loading' | 'success' | 'empty' | 'unauthorized' | 'error';
type TimeFilter = 'all' | 'due_today' | 'overdue';
type AssignmentFilter = 'all' | 'me' | 'team';
type TaskActionKind = 'reassign' | 'comments' | 'block';

interface TaskInboxProps {
  onNavigate?: (page: Page, id?: string) => void;
}

interface Filters {
  taskType: TaskType | 'all';
  time: TimeFilter;
  borrowerType: 'all' | 'individual_farmer' | 'fpc' | 'producer_institution';
  minimumAmount: string;
  specialCase: boolean;
  exceptionRequired: boolean;
  assignment: AssignmentFilter;
}

const EMPTY_FILTERS: Filters = {
  taskType: 'all',
  time: 'all',
  borrowerType: 'all',
  minimumAmount: '',
  specialCase: false,
  exceptionRequired: false,
  assignment: 'all',
};

const TASK_TYPE_LABELS: Record<TaskType, string> = {
  completeness_check: 'Completeness Check',
  appraisal: 'Prepare Appraisal',
  sanction: 'Sanction Decision',
  document_verification: 'Document Verification',
  sap_setup: 'SAP Setup',
  disbursement: 'Disbursement',
  repayment_posting: 'Repayment Posting',
  default_review: 'Default Review',
};

const TASK_TYPE_COLORS: Record<TaskType, string> = {
  completeness_check: 'bg-blue-50 text-blue-700',
  appraisal: 'bg-amber-50 text-amber-700',
  sanction: 'bg-violet-50 text-violet-700',
  document_verification: 'bg-teal-50 text-teal-700',
  sap_setup: 'bg-slate-50 text-slate-600',
  disbursement: 'bg-green-50 text-green-700',
  repayment_posting: 'bg-indigo-50 text-indigo-700',
  default_review: 'bg-red-50 text-red-700',
};

const PRIORITY: Record<TaskPriority, { label: string; color: string }> = {
  normal: { label: 'Normal', color: 'bg-slate-100 text-slate-600' },
  high: { label: 'High', color: 'bg-amber-100 text-amber-700' },
  critical: { label: 'Critical', color: 'bg-red-100 text-red-700' },
};

const TaskInbox: React.FC<TaskInboxProps> = ({ onNavigate }) => {
  const { currentUser } = useRole();
  const [rows, setRows] = useState<WorkflowTaskRow[]>([]);
  const [pagination, setPagination] = useState<Pagination | null>(null);
  const [filters, setFilters] = useState<Filters>(EMPTY_FILTERS);
  const [page, setPage] = useState(1);
  const [loadState, setLoadState] = useState<LoadState>('loading');
  const [message, setMessage] = useState('');
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);
  const [activeMenu, setActiveMenu] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);
  const [action, setAction] = useState<{ kind: TaskActionKind; task: WorkflowTaskRow } | null>(null);
  const [actionValue, setActionValue] = useState('');
  const [actionBusy, setActionBusy] = useState(false);
  const [actionMessage, setActionMessage] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const requestSequence = useRef(0);

  const query = useMemo<TaskInboxQuery>(() => ({
    page,
    pageSize: 20,
    ...(filters.taskType !== 'all' ? { taskType: filters.taskType } : {}),
    ...(filters.time === 'due_today' ? { dueToday: true } : {}),
    ...(filters.time === 'overdue' ? { overdue: true } : {}),
    ...(filters.borrowerType !== 'all' ? { borrowerType: filters.borrowerType } : {}),
    ...(filters.minimumAmount.trim() ? { minimumAmount: filters.minimumAmount.trim() } : {}),
    ...(filters.specialCase ? { specialCase: true } : {}),
    ...(filters.exceptionRequired ? { exceptionRequired: true } : {}),
    ...(filters.assignment === 'me' ? { assignedToUserId: currentUser.id } : {}),
    ...(filters.assignment === 'team' ? { assignedToMyTeam: true } : {}),
  }), [currentUser.id, filters, page]);

  const load = useCallback(async () => {
    const requestId = ++requestSequence.current;
    setLoadState('loading');
    setMessage('');
    try {
      const result = await fetchTaskInbox(query);
      if (requestId !== requestSequence.current) return;
      setRows(result.items);
      setPagination(result.pagination);
      setLoadState(result.items.length ? 'success' : 'empty');
    } catch (error) {
      if (requestId !== requestSequence.current) return;
      setRows([]);
      setPagination(null);
      const denied = error instanceof AuthSessionError && [401, 403].includes(error.status ?? 0);
      setLoadState(denied ? 'unauthorized' : 'error');
      setMessage(error instanceof Error ? error.message : 'Task Inbox could not be loaded.');
    }
  }, [query]);

  useEffect(() => {
    void load();
  }, [load, refreshKey]);

  const changeFilter = <K extends keyof Filters>(key: K, value: Filters[K]) => {
    setPage(1);
    setFilters(current => ({ ...current, [key]: value }));
  };

  const openTask = (task: WorkflowTaskRow) => {
    if (!onNavigate) return;
    onNavigate(
      task.linked_entity_type === 'loan_account' ? 'loan-accounts/detail' : 'applications/detail',
      task.application_or_loan_id,
    );
  };

  const openAction = (task: WorkflowTaskRow, kind: TaskActionKind) => {
    setActiveMenu(null);
    setAction({ task, kind });
    setActionValue('');
    setActionMessage('');
  };

  const runAction = async () => {
    if (!action || !actionValue.trim()) return;
    setActionBusy(true);
    setActionMessage('');
    try {
      const payload: Record<string, string> = action.kind === 'reassign'
        ? { assigned_to_user_id: actionValue.trim() }
        : action.kind === 'comments'
          ? { comment: actionValue.trim() }
          : { reason: actionValue.trim() };
      const updated = await submitTaskAction(action.task.task_id, action.kind, payload);
      setRows(current => current.map(row => row.task_id === updated.task_id ? updated : row));
      setSuccessMessage(`${actionLabel(action.kind)} completed for ${action.task.task_reference}.`);
      setAction(null);
      setActionValue('');
    } catch (error) {
      setActionMessage(error instanceof Error ? error.message : 'Task action could not be completed.');
    } finally {
      setActionBusy(false);
    }
  };

  const canReassign = currentUser.permissions.includes('users.team.manage');

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Task Inbox</h1>
          <p className="text-sm text-slate-500 mt-1">
            Real pending work assigned to you, your active roles, or your teams.
          </p>
        </div>
        {loadState === 'success' && rows.some(row => row.priority === 'critical') && (
          <span className="flex items-center gap-1.5 text-xs font-semibold text-red-700 bg-red-100 px-3 py-1.5 rounded-full">
            <AlertTriangle size={12} />
            Critical work visible
          </span>
        )}
      </div>

      {successMessage && (
        <div className="mb-4">
          <AlertBanner type="success" title="Task updated" message={successMessage} />
        </div>
      )}

      <div className="flex items-center gap-3 mb-5 flex-wrap">
        <select
          aria-label="Task type"
          value={filters.taskType}
          onChange={event => changeFilter('taskType', event.target.value as Filters['taskType'])}
          className="text-sm border border-slate-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500 bg-white"
        >
          <option value="all">All task types</option>
          {Object.entries(TASK_TYPE_LABELS).map(([value, label]) => (
            <option key={value} value={value}>{label}</option>
          ))}
        </select>
        <button
          type="button"
          onClick={() => setShowAdvancedFilters(current => !current)}
          className={`flex items-center gap-2 text-sm px-3 py-2 border rounded-lg transition-colors ${
            showAdvancedFilters
              ? 'bg-slate-100 border-slate-300 text-slate-800'
              : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50'
          }`}
        >
          <Filter size={16} /> Advanced Filters
        </button>
        {filtersActive(filters) && (
          <button type="button" onClick={() => { setFilters(EMPTY_FILTERS); setPage(1); }} className="btn-secondary">
            Clear filters
          </button>
        )}
      </div>

      {showAdvancedFilters && (
        <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 mb-6 grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
          <FilterSelect
            label="Assignment"
            value={filters.assignment}
            onChange={value => changeFilter('assignment', value as AssignmentFilter)}
            options={[
              ['all', 'All assigned work'],
              ['me', 'Assigned to Me'],
              ['team', 'Assigned to My Team'],
            ]}
          />
          <FilterSelect
            label="Time"
            value={filters.time}
            onChange={value => changeFilter('time', value as TimeFilter)}
            options={[
              ['all', 'Any time'],
              ['due_today', 'Due Today'],
              ['overdue', 'Overdue'],
            ]}
          />
          <FilterSelect
            label="Borrower Type"
            value={filters.borrowerType}
            onChange={value => changeFilter('borrowerType', value as Filters['borrowerType'])}
            options={[
              ['all', 'Any type'],
              ['individual_farmer', 'Individual'],
              ['fpc', 'FPC'],
              ['producer_institution', 'Producer Institution'],
            ]}
          />
          <div>
            <label htmlFor="task-minimum-amount" className="block text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1.5">
              Minimum Amount
            </label>
            <input
              id="task-minimum-amount"
              inputMode="decimal"
              value={filters.minimumAmount}
              onChange={event => changeFilter('minimumAmount', event.target.value)}
              placeholder="₹ amount"
              className="field-input text-sm py-1.5 w-full"
            />
          </div>
          <div>
            <span className="block text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1.5">Flags</span>
            <label className="flex items-center gap-2 text-sm text-slate-700 mb-2">
              <input
                type="checkbox"
                checked={filters.specialCase}
                onChange={event => changeFilter('specialCase', event.target.checked)}
              />
              Special case
            </label>
            <label className="flex items-center gap-2 text-sm text-slate-700">
              <input
                type="checkbox"
                checked={filters.exceptionRequired}
                onChange={event => changeFilter('exceptionRequired', event.target.checked)}
              />
              Exception required
            </label>
          </div>
        </div>
      )}

      {loadState === 'loading' && (
        <div className="card bg-white flex items-center justify-center py-16 text-slate-400 text-sm">
          <Clock size={16} className="mr-2 text-green-500" /> Loading task inbox...
        </div>
      )}
      {loadState === 'unauthorized' && (
        <AlertBanner
          type="error"
          title="Task Inbox unavailable"
          message={message || 'You are not authorised to view staff tasks.'}
        />
      )}
      {loadState === 'error' && (
        <div>
          <AlertBanner type="error" title="Task Inbox could not be loaded" message={message} />
          <button type="button" onClick={() => setRefreshKey(value => value + 1)} className="btn-secondary mt-3 flex items-center gap-2">
            <RefreshCw size={14} /> Retry
          </button>
        </div>
      )}
      {loadState === 'empty' && (
        <div className="flex flex-col items-center py-20 text-center">
          <CheckCircle2 size={40} className="text-green-400 mb-4" />
          <h2 className="text-lg font-semibold text-slate-700 mb-2">All clear!</h2>
          <p className="text-sm text-slate-400">No pending tasks match this server-scoped view.</p>
        </div>
      )}
      {loadState === 'success' && pagination && (
        <TaskTable
          rows={rows}
          pagination={pagination}
          canReassign={canReassign}
          activeMenu={activeMenu}
          onMenu={setActiveMenu}
          onOpen={openTask}
          onAction={openAction}
          onPage={setPage}
        />
      )}

      <Modal
        isOpen={Boolean(action)}
        onClose={() => !actionBusy && setAction(null)}
        title={action ? actionLabel(action.kind) : 'Task action'}
        subtitle={action?.task.task_reference}
        destructive={action?.kind === 'block'}
        footer={(
          <>
            <button type="button" onClick={() => setAction(null)} disabled={actionBusy} className="btn-secondary">Cancel</button>
            <button type="button" onClick={() => void runAction()} disabled={actionBusy || !actionValue.trim()} className="btn-primary">
              {actionBusy ? 'Saving...' : action ? actionLabel(action.kind) : 'Save'}
            </button>
          </>
        )}
      >
        {actionMessage && <AlertBanner type="error" title="Task action rejected" message={actionMessage} />}
        <label htmlFor="task-action-value" className="field-label mt-3">
          {action?.kind === 'reassign' ? 'Target user ID' : action?.kind === 'comments' ? 'Comment' : 'Blocking reason'}
        </label>
        <textarea
          id="task-action-value"
          value={actionValue}
          onChange={event => setActionValue(event.target.value)}
          className="field-input min-h-24"
        />
      </Modal>
    </div>
  );
};

const TaskTable: React.FC<{
  rows: WorkflowTaskRow[];
  pagination: Pagination;
  canReassign: boolean;
  activeMenu: string | null;
  onMenu: (taskId: string | null) => void;
  onOpen: (task: WorkflowTaskRow) => void;
  onAction: (task: WorkflowTaskRow, kind: TaskActionKind) => void;
  onPage: (page: number) => void;
}> = ({ rows, pagination, canReassign, activeMenu, onMenu, onOpen, onAction, onPage }) => (
  <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
    <div className="px-6 py-3 border-b border-slate-100 bg-slate-50 flex items-center justify-between text-xs font-semibold text-slate-500">
      <span className="flex items-center gap-2">
        <Inbox size={14} /> {pagination.total_count} pending task{pagination.total_count === 1 ? '' : 's'}
      </span>
      <span className="flex items-center gap-2">
        Page {pagination.page} of {pagination.total_pages}
        <button type="button" aria-label="Previous page" disabled={!pagination.has_previous} onClick={() => onPage(pagination.page - 1)} className="btn-secondary">Previous</button>
        <button type="button" aria-label="Next page" disabled={!pagination.has_next} onClick={() => onPage(pagination.page + 1)} className="btn-secondary">Next</button>
      </span>
    </div>
    <div className="divide-y divide-slate-50 overflow-x-auto">
      {rows.map(task => (
        <div
          key={task.task_id}
          className={`px-6 py-4 grid grid-cols-[4px_160px_1fr_220px_100px_96px_118px] items-center gap-4 hover:bg-slate-50 transition-colors ${
            task.priority === 'critical' ? 'bg-red-50/30' : ''
          }`}
        >
          <div className={`w-1 h-12 rounded-full ${
            task.priority === 'critical' ? 'bg-red-500' : task.priority === 'high' ? 'bg-amber-400' : 'bg-slate-200'
          }`} />
          <div className="min-w-0">
            <span className="block text-xs text-slate-400 mb-1">Task type</span>
            <span className={`text-xs font-medium px-2 py-1 rounded-lg ${TASK_TYPE_COLORS[task.task_type]}`}>
              {TASK_TYPE_LABELS[task.task_type]}
            </span>
          </div>
          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <span className="text-xs text-slate-400">Task ID</span>
              <span className="font-mono text-sm text-slate-600 whitespace-nowrap">{task.task_reference}</span>
              <span className="text-slate-400">·</span>
              <span className="text-xs text-slate-400">Borrower</span>
              <span className="text-sm font-medium text-slate-900 truncate">{task.borrower || '—'}</span>
            </div>
            <div className="flex items-center gap-3 mt-1 text-xs text-slate-500 min-w-0">
              <span className="whitespace-nowrap"><strong className="font-medium">Application / Loan ID</strong> {task.application_or_loan_id}</span>
              <span className="whitespace-nowrap"><strong className="font-medium">Amount</strong> {formatAmount(task.amount)}</span>
              <span className="whitespace-nowrap"><strong className="font-medium">Created date</strong> {formatDate(task.created_date)}</span>
            </div>
          </div>
          <div className="min-w-0">
            <span className="block text-xs text-slate-400 mb-1">Current status</span>
            <StatusBadge label={statusLabel(task)} family={task.blocked ? 'rejected' : 'pending'} size="sm" />
            <span className="block mt-1 text-xs text-slate-500 truncate"><strong className="font-medium">Assigned to</strong> {assignmentLabel(task)}</span>
          </div>
          <div className="text-right">
            <span className="block text-xs text-slate-400">SLA / TAT</span>
            <span className={`text-sm font-semibold ${task.sla_tat.overdue_days ? 'text-red-600' : 'text-slate-700'}`}>{slaLabel(task)}</span>
            <span className="block text-xs text-slate-400"><strong className="font-medium">Due date</strong> {formatDate(task.due_date)}</span>
          </div>
          <div>
            <span className="block text-xs text-slate-400 mb-1">Priority</span>
            <span className={`text-xs px-2 py-1 rounded-full font-semibold ${PRIORITY[task.priority].color}`}>{PRIORITY[task.priority].label}</span>
          </div>
          <div>
            <span className="block text-xs text-slate-400 mb-1">Action</span>
            <div className="flex items-center justify-end gap-2">
              <button type="button" onClick={() => onOpen(task)} className="flex items-center gap-1 bg-green-600 hover:bg-green-700 text-white text-xs font-medium px-3 py-2 rounded-lg transition-colors">
                Open <ArrowRight size={12} />
              </button>
              <div className="relative">
                <button type="button" aria-label={`Actions for ${task.task_reference}`} onClick={() => onMenu(activeMenu === task.task_id ? null : task.task_id)} className="p-1.5 text-slate-400 hover:bg-slate-100 rounded-lg">
                  <MoreVertical size={16} />
                </button>
                {activeMenu === task.task_id && (
                  <div className="absolute right-0 top-full mt-1 w-48 bg-white border border-slate-200 rounded-xl shadow-lg z-10 py-1">
                    {canUseAction(task, 'comments') && <ActionButton icon={<MessageSquare size={14} />} label="Add Comment" onClick={() => onAction(task, 'comments')} />}
                    {canReassign && canUseAction(task, 'reassign') && <ActionButton icon={<UserPlus size={14} />} label="Reassign Task" onClick={() => onAction(task, 'reassign')} />}
                    {canUseAction(task, 'block') && <ActionButton icon={<Ban size={14} />} label="Mark Blocked" onClick={() => onAction(task, 'block')} destructive />}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  </div>
);

const FilterSelect: React.FC<{
  label: string;
  value: string;
  options: Array<[string, string]>;
  onChange: (value: string) => void;
}> = ({ label, value, options, onChange }) => (
  <div>
    <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1.5">
      {label}
      <select aria-label={label} value={value} onChange={event => onChange(event.target.value)} className="field-select text-sm py-1.5 w-full mt-1.5 normal-case font-normal">
        {options.map(([optionValue, optionLabel]) => <option key={optionValue} value={optionValue}>{optionLabel}</option>)}
      </select>
    </label>
  </div>
);

const ActionButton: React.FC<{ icon: React.ReactNode; label: string; onClick: () => void; destructive?: boolean }> = ({ icon, label, onClick, destructive }) => (
  <button type="button" onClick={onClick} className={`w-full flex items-center gap-2 px-3 py-2 text-xs hover:bg-slate-50 ${destructive ? 'text-red-600' : 'text-slate-600'}`}>
    {icon} {label}
  </button>
);

const canUseAction = (task: WorkflowTaskRow, actionCode: string) => {
  if (!task.available_actions) return true;
  return task.available_actions.some(action => action.action_code === actionCode && action.enabled);
};

const filtersActive = (filters: Filters) => JSON.stringify(filters) !== JSON.stringify(EMPTY_FILTERS);
const actionLabel = (kind: TaskActionKind) => kind === 'reassign' ? 'Reassign Task' : kind === 'comments' ? 'Add Comment' : 'Mark Blocked';
const assignmentLabel = (task: WorkflowTaskRow) => task.assigned_to.user?.full_name || task.assigned_to.team_code || task.assigned_to.role_code.replace(/_/g, ' ');
const formatAmount = (amount: string | null) => amount === null ? '—' : new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(Number(amount));
const formatDate = (value: string | null) => value ? new Intl.DateTimeFormat('en-IN', { dateStyle: 'medium' }).format(new Date(value)) : 'Not set';
const statusLabel = (task: WorkflowTaskRow) => task.blocked ? 'Blocked' : task.current_status.replace(/_/g, ' ');
const slaLabel = (task: WorkflowTaskRow) => task.sla_tat.overdue_days > 0
  ? `${task.sla_tat.overdue_days} day${task.sla_tat.overdue_days === 1 ? '' : 's'} overdue`
  : task.sla_tat.due_at ? `Due ${formatDate(task.sla_tat.due_at)}` : 'No governed TAT';

export default TaskInbox;
