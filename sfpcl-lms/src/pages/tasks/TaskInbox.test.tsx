// @vitest-environment jsdom
import React, { useEffect } from 'react';
import { cleanup, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { clearStoredAuthSession, storedAuthSession } from '../../services/authSession';
import { RoleProvider, useRole } from '../../contexts/RoleContext';
import { fetchTaskInbox, submitTaskAction } from '../../services/taskInboxApi';
import { fetchDashboardSummary } from '../../services/dashboardApi';
import TaskInbox from './TaskInbox';
import taskInboxSource from './TaskInbox.tsx?raw';

const storage = new Map<string, string>();

beforeEach(() => {
  vi.stubGlobal('localStorage', {
    getItem: vi.fn((key: string) => storage.get(key) ?? null),
    setItem: vi.fn((key: string, value: string) => storage.set(key, value)),
    removeItem: vi.fn((key: string) => storage.delete(key)),
  });
  storage.clear();
  storedAuthSession({ accessToken: 'task-access-token', refreshToken: 'task-refresh-token' });
});

afterEach(() => {
  cleanup();
  clearStoredAuthSession();
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe('Task Inbox API', () => {
  it('loads a strict page and sends S03 filters to the backend', async () => {
    const fetchMock = vi.fn().mockResolvedValueOnce(ok([taskRow], {
      page: 2,
      page_size: 20,
      total_count: 21,
      total_pages: 2,
      has_next: false,
      has_previous: true,
    }));
    vi.stubGlobal('fetch', fetchMock);

    const result = await fetchTaskInbox({
      page: 2,
      pageSize: 20,
      taskType: 'appraisal',
      assignedToUserId: '11111111-1111-4111-8111-111111111111',
      dueToday: true,
      borrowerType: 'individual_farmer',
    });

    expect(fetchMock).toHaveBeenCalledWith(
      'http://127.0.0.1:8000/api/v1/tasks/?page=2&page_size=20&task_type=appraisal&due_today=true&borrower_type=individual_farmer&assigned_to_user_id=11111111-1111-4111-8111-111111111111',
      expect.objectContaining({
        method: 'GET',
        headers: expect.objectContaining({
          Authorization: 'Bearer task-access-token',
        }),
      }),
    );
    expect(result.items).toEqual([taskRow]);
    expect(result.pagination).toMatchObject({ page: 2, total_count: 21, has_previous: true });
  });

  it('rejects malformed task rows instead of displaying invented defaults', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValueOnce(ok([{}], {
      page: 1,
      page_size: 20,
      total_count: 1,
      total_pages: 1,
      has_next: false,
      has_previous: false,
    })));

    await expect(fetchTaskInbox()).rejects.toMatchObject({ code: 'MALFORMED_RESPONSE' });
  });

  it('reads the same seeded task identity through Task Inbox and Dashboard APIs', async () => {
    const dashboardTask = {
      task_type: taskRow.task_type,
      entity_id: taskRow.application_or_loan_id,
      title: taskRow.title,
      due_at: taskRow.due_date,
    };
    vi.stubGlobal('fetch', vi.fn()
      .mockResolvedValueOnce(ok([taskRow], singlePage()))
      .mockResolvedValueOnce(success({
        role_context: 'credit_manager',
        cards: [],
        tasks: [dashboardTask],
      })));

    const inbox = await fetchTaskInbox();
    const dashboard = await fetchDashboardSummary();

    expect(dashboard.tasks[0]).toMatchObject({
      entity_id: inbox.items[0].application_or_loan_id,
      task_type: inbox.items[0].task_type,
      title: inbox.items[0].title,
    });
  });

  it.each([
    ['reassign', { assigned_to_user_id: '44444444-4444-4444-8444-444444444444' }],
    ['comments', { comment: 'Public interface comment' }],
    ['block', { reason: 'Governed evidence is pending' }],
  ] as const)('posts the %s action to the 012EA endpoint', async (action, payload) => {
    const fetchMock = vi.fn().mockResolvedValueOnce(success(taskRow));
    vi.stubGlobal('fetch', fetchMock);

    await submitTaskAction(taskRow.task_id, action, payload);

    expect(fetchMock).toHaveBeenCalledWith(
      `http://127.0.0.1:8000/api/v1/tasks/${taskRow.task_id}/${action}/`,
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify(payload),
      }),
    );
  });

  it.each(['reassign', 'comments', 'block'] as const)(
    'preserves a backend denial from the %s action endpoint',
    async action => {
      vi.stubGlobal('fetch', vi.fn().mockResolvedValueOnce(
        failed(403, 'FORBIDDEN', 'Task authority was removed.'),
      ));

      await expect(submitTaskAction(taskRow.task_id, action, {})).rejects.toMatchObject({
        code: 'FORBIDDEN',
        status: 403,
        message: 'Task authority was removed.',
      });
    },
  );
});

describe('Task Inbox screen', () => {
  it('has no prototype task data or client-side export fallback', () => {
    expect(taskInboxSource).not.toContain('mockData');
    expect(taskInboxSource).not.toContain('allTasks');
    expect(taskInboxSource).not.toContain('Export CSV');
  });

  it('renders the S03 API columns and replaces the page through backend pagination', async () => {
    const firstPageRows = Array.from({ length: 20 }, (_, index) => ({
      ...taskRow,
      task_id: `22222222-2222-4222-8222-${String(index).padStart(12, '0')}`,
      task_reference: `TASK-${String(index + 1).padStart(6, '0')}`,
      borrower: index === 0 ? 'Seeded Borrower' : `Seeded Borrower ${index + 1}`,
    }));
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(ok(firstPageRows, page(1, 21, true)))
      .mockResolvedValueOnce(ok([{ ...taskRow, task_id: 'task-page-2', task_reference: 'TASK-000021' }], page(2, 21, false)));
    vi.stubGlobal('fetch', fetchMock);

    renderTaskInbox();

    expect(await screen.findByText('Seeded Borrower')).toBeTruthy();
    [
      'Task ID', 'Task type', 'Application / Loan ID', 'Borrower', 'Amount',
      'Priority', 'SLA / TAT', 'Current status', 'Assigned to', 'Created date',
      'Due date', 'Action',
    ].forEach(column => expect(screen.getAllByText(column).length).toBeGreaterThan(0));
    expect(screen.getByText('21 pending tasks')).toBeTruthy();

    await userEvent.click(screen.getByRole('button', { name: 'Next page' }));

    await waitFor(() => expect(fetchMock).toHaveBeenLastCalledWith(
      expect.stringContaining('/api/v1/tasks/?page=2&page_size=20'),
      expect.any(Object),
    ));
    expect(await screen.findByText('TASK-000021')).toBeTruthy();
  });

  it('round-trips assigned-to-me, due-today, and overdue filters through the API', async () => {
    const fetchMock = vi.fn().mockResolvedValue(ok([taskRow], {
      page: 1,
      page_size: 20,
      total_count: 1,
      total_pages: 1,
      has_next: false,
      has_previous: false,
    }));
    vi.stubGlobal('fetch', fetchMock);
    renderTaskInbox();
    await screen.findByText('Seeded Borrower');

    await userEvent.click(screen.getByRole('button', { name: 'Advanced Filters' }));
    await userEvent.selectOptions(screen.getByLabelText('Assignment'), 'me');
    await waitFor(() => expect(lastRequestUrl(fetchMock)).toContain(
      'assigned_to_user_id=11111111-1111-4111-8111-111111111111',
    ));

    await userEvent.selectOptions(screen.getByLabelText('Time'), 'due_today');
    await waitFor(() => expect(lastRequestUrl(fetchMock)).toContain('due_today=true'));

    await userEvent.selectOptions(screen.getByLabelText('Time'), 'overdue');
    await waitFor(() => {
      expect(lastRequestUrl(fetchMock)).toContain('overdue=true');
      expect(lastRequestUrl(fetchMock)).not.toContain('due_today=true');
    });
  });

  it('opens the linked application and completes a permitted comment action', async () => {
    const onNavigate = vi.fn();
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(ok([taskRow], singlePage()))
      .mockResolvedValueOnce(success(taskRow));
    vi.stubGlobal('fetch', fetchMock);
    renderTaskInbox(onNavigate);
    await screen.findByText('Seeded Borrower');

    await userEvent.click(screen.getByRole('button', { name: 'Open' }));
    expect(onNavigate).toHaveBeenCalledWith(
      'applications/detail',
      '33333333-3333-4333-8333-333333333333',
    );

    await userEvent.click(screen.getByRole('button', { name: 'Actions for TASK-000021' }));
    await userEvent.click(screen.getByRole('button', { name: 'Add Comment' }));
    await userEvent.type(screen.getByLabelText('Comment'), 'Seeded follow-up note');
    await userEvent.click(screen.getByRole('button', { name: 'Add Comment' }));

    expect(await screen.findByText('Task updated')).toBeTruthy();
    expect(fetchMock).toHaveBeenLastCalledWith(
      'http://127.0.0.1:8000/api/v1/tasks/22222222-2222-4222-8222-222222222222/comments/',
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ comment: 'Seeded follow-up note' }),
      }),
    );
  });

  it('surfaces the backend rejection when task authority changes before an action', async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(ok([taskRow], singlePage()))
      .mockResolvedValueOnce(failed(403, 'FORBIDDEN', 'You do not have permission to change this task.'));
    vi.stubGlobal('fetch', fetchMock);
    renderTaskInbox();
    await screen.findByText('Seeded Borrower');

    await userEvent.click(screen.getByRole('button', { name: 'Actions for TASK-000021' }));
    await userEvent.click(screen.getByRole('button', { name: 'Mark Blocked' }));
    await userEvent.type(screen.getByLabelText('Blocking reason'), 'Waiting for governed evidence');
    await userEvent.click(screen.getByRole('button', { name: 'Mark Blocked' }));

    expect(await screen.findByText('Task action rejected')).toBeTruthy();
    expect(screen.getByText('You do not have permission to change this task.')).toBeTruthy();
  });

  it('hides reassignment without users.team.manage while retaining scoped comment/block actions', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValueOnce(ok([taskRow], singlePage())));
    renderTaskInbox(vi.fn(), ['applications.loan_application.read']);
    await screen.findByText('Seeded Borrower');

    await userEvent.click(screen.getByRole('button', { name: 'Actions for TASK-000021' }));

    expect(screen.queryByRole('button', { name: 'Reassign Task' })).toBeNull();
    expect(screen.getByRole('button', { name: 'Add Comment' })).toBeTruthy();
    expect(screen.getByRole('button', { name: 'Mark Blocked' })).toBeTruthy();
  });

  it('uses a returned available_actions projection to narrow task actions', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValueOnce(ok([{
      ...taskRow,
      available_actions: [{
        action_code: 'comments',
        label: 'Add Comment',
        enabled: true,
        disabled_reason: null,
      }],
    }], singlePage())));
    renderTaskInbox();
    await screen.findByText('Seeded Borrower');

    await userEvent.click(screen.getByRole('button', { name: 'Actions for TASK-000021' }));

    expect(screen.getByRole('button', { name: 'Add Comment' })).toBeTruthy();
    expect(screen.queryByRole('button', { name: 'Reassign Task' })).toBeNull();
    expect(screen.queryByRole('button', { name: 'Mark Blocked' })).toBeNull();
  });

  it.each([
    [failed(403, 'FORBIDDEN', 'Task scope denied.'), 'Task Inbox unavailable'],
    [failed(500, 'SERVER_ERROR', 'Task service unavailable.'), 'Task Inbox could not be loaded'],
    [ok([], { ...singlePage(), total_count: 0 }), 'All clear!'],
  ])('renders the declared non-success state', async (response, expected) => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValueOnce(response));
    renderTaskInbox();
    expect(await screen.findByText(expected)).toBeTruthy();
  });
});

function renderTaskInbox(
  onNavigate = vi.fn(),
  permissions = ['applications.loan_application.read', 'users.team.manage'],
) {
  return render(
    <RoleProvider>
      <AuthenticatedHarness permissions={permissions}>
        <TaskInbox onNavigate={onNavigate} />
      </AuthenticatedHarness>
    </RoleProvider>,
  );
}

const AuthenticatedHarness: React.FC<{ children: React.ReactNode; permissions: string[] }> = ({ children, permissions }) => {
  const { currentUser, setBackendUser } = useRole();
  useEffect(() => {
    setBackendUser({
      id: '11111111-1111-4111-8111-111111111111',
      name: 'Task Owner',
      email: 'owner@example.test',
      role: 'deputy_manager_finance',
      roleName: 'Deputy Manager – Finance',
      team: 'credit_assessment',
      teamName: 'Credit Assessment',
      roleCodes: ['deputy_manager_finance'],
      teamCodes: ['credit_assessment'],
      permissions,
      availableActions: [],
    });
  }, [permissions, setBackendUser]);
  return currentUser.isBackendSession ? children : null;
};

const taskRow = {
  task_id: '22222222-2222-4222-8222-222222222222',
  task_reference: 'TASK-000021',
  task_type: 'appraisal',
  title: 'Prepare appraisal',
  application_or_loan_id: '33333333-3333-4333-8333-333333333333',
  linked_entity_type: 'loan_application',
  borrower: 'Seeded Borrower',
  borrower_type: 'individual_farmer',
  amount: '250000.00',
  priority: 'high',
  sla_tat: { due_at: '2026-07-25T10:00:00Z', overdue_days: 0 },
  current_status: 'draft',
  assigned_to: {
    role_code: 'deputy_manager_finance',
    team_code: 'credit_assessment',
    user: {
      user_id: '11111111-1111-4111-8111-111111111111',
      full_name: 'Task Owner',
    },
  },
  blocked: false,
  blocked_reason: null,
  special_case: false,
  exception_required: false,
  created_date: '2026-07-24T10:00:00Z',
  due_date: '2026-07-25T10:00:00Z',
  closed_at: null,
  action: { code: 'open', url: '/tasks/22222222-2222-4222-8222-222222222222' },
};

function page(pageNumber: number, totalCount: number, hasNext: boolean) {
  return {
    page: pageNumber,
    page_size: 20,
    total_count: totalCount,
    total_pages: 2,
    has_next: hasNext,
    has_previous: pageNumber > 1,
  };
}

function singlePage() {
  return {
    page: 1,
    page_size: 20,
    total_count: 1,
    total_pages: 1,
    has_next: false,
    has_previous: false,
  };
}

function lastRequestUrl(fetchMock: ReturnType<typeof vi.fn>): string {
  return String(fetchMock.mock.calls[fetchMock.mock.calls.length - 1]?.[0] ?? '');
}

function ok(data: unknown, pagination: Record<string, unknown>): Response {
  return {
    ok: true,
    status: 200,
    json: async () => ({
      success: true,
      data,
      pagination,
      meta: { api_version: 'v1' },
    }),
  } as Response;
}

function success(data: unknown): Response {
  return {
    ok: true,
    status: 200,
    json: async () => ({ success: true, data, meta: { api_version: 'v1' } }),
  } as Response;
}

function failed(status: number, code: string, message: string): Response {
  return {
    ok: false,
    status,
    json: async () => ({
      success: false,
      error: { code, message },
      meta: { api_version: 'v1' },
    }),
  } as Response;
}
