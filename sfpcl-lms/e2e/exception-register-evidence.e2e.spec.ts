import fs from 'fs';
import path from 'path';
import { expect, test, type Page, type Route } from '@playwright/test';

const evidenceDir = process.env.RALPH_EVIDENCE_DIR;
if (!evidenceDir) throw new Error('RALPH_EVIDENCE_DIR is required for Exception Register visual acceptance');
fs.mkdirSync(evidenceDir, { recursive: true });

test('S25 renders frozen comments and supporting metadata without granting download authority', async ({ page }) => {
  await page.setViewportSize({ width: 1280, height: 720 });
  let canDownload = true;
  const observedPaths: string[] = [];
  page.on('request', request => {
    const url = new URL(request.url());
    if (url.pathname.startsWith('/api/v1/')) observedPaths.push(url.pathname);
  });

  await page.addInitScript(() => localStorage.setItem('sfpcl_staff_auth_session', JSON.stringify({ accessToken: 'register-access', refreshToken: 'register-refresh' })));
  await page.route('**/api/v1/auth/me/', route => json(route, user(canDownload)));
  await page.route('**/api/v1/dashboard/', route => json(route, { role_context: 'cfo', cards: [], tasks: [] }));
  await page.route('**/api/v1/exception-register/**', route => {
    const url = new URL(route.request().url());
    expect(url.searchParams.get('page')).toBe('1');
    expect(url.searchParams.get('page_size')).toBe('20');
    return paginated(route, [exceptionRow]);
  });

  await page.goto('/');
  await page.getByRole('button', { name: /^Registers$/ }).click();
  await expect(page.getByText('Frozen exception description')).toBeVisible();
  await expect(page.getByText('Frozen Visual Borrower')).toBeVisible();
  await expect(page.getByText(/Visual Requester/)).toBeVisible();
  await expect(page.getByText('Seasonal exception is commercially justified.')).toBeVisible();
  await expect(page.getByText('CFO approved with monitoring.')).toBeVisible();
  await expect(page.getByText('cash-flow-evidence.pdf')).toBeVisible();
  await expect(page.getByRole('button', { name: /download/i })).toHaveCount(0);
  await expect(page.getByRole('link', { name: /download/i })).toHaveCount(0);
  await captureReviewable(page, 'exception-register-source-evidence.png');

  canDownload = false;
  await page.reload();
  await page.getByRole('button', { name: /^Registers$/ }).click();
  await expect(page.getByText('cash-flow-evidence.pdf')).toBeVisible();
  await expect(page.getByText('CFO approved with monitoring.')).toBeVisible();
  await expect(page.getByRole('button', { name: /download/i })).toHaveCount(0);
  await expect(page.getByRole('link', { name: /download/i })).toHaveCount(0);
  await captureReviewable(page, 'exception-register-document-denied.png');

  expect(observedPaths.some(value => value.includes('/document-files/'))).toBe(false);
});

const exceptionRow = {
  exception_register_entry_id: 'exception-visual-007', loan_application_id: 'application-visual-007', loan_account_id: null,
  approval_case_id: 'case-visual-007', cycle_number: 2, exception_type: 'exceeds_loan_limit',
  description: 'Frozen exception description', business_reason: 'Seasonal exception is commercially justified.',
  borrower_name: 'Frozen Visual Borrower', financial_impact: '575000.00', requested_by: { user_id: 'requester-visual', full_name: 'Visual Requester' }, decision_date: '2026-07-13',
  risk_assessment: 'Medium', status: 'approved', case_status: 'approved', conflict_block_reason: null,
  authority_applied_summary: 'CFO: Visual CFO (approved); Director: Visual Director One (approved); Director: Visual Director Two (approved)',
  route_approvers: [], required_approvers: [],
  approval_actions: [
    { approval_action_id: 'action-cfo', role_code: 'cfo', user_id: 'cfo-visual', full_name: 'Visual CFO', decision: 'approved', comments: 'CFO approved with monitoring.', acted_at: '2026-07-13T10:00:00Z' },
    { approval_action_id: 'action-director', role_code: 'director', user_id: 'director-visual', full_name: 'Visual Director', decision: 'approved', comments: 'Director confirms the documented controls.', acted_at: '2026-07-13T11:00:00Z' },
  ],
  supporting_documents: [
    { document_id: 'document-visual-007', file_name: 'cash-flow-evidence.pdf', mime_type: 'application/pdf', file_size_bytes: 2456, sensitivity_level: 'restricted', uploaded_at: '2026-07-13T09:00:00Z' },
  ],
  created_at: '2026-07-13T09:30:00Z', closed_at: '2026-07-13T11:00:00Z',
};

const user = (canDownload: boolean) => ({
  user_id: 'cfo-visual', full_name: 'Visual CFO', email: 'visual.cfo@sfpcl.example', status: 'active',
  roles: [{ role_code: 'cfo', role_name: 'CFO' }], teams: [], role_codes: ['cfo'], team_codes: [],
  permissions: ['approvals.exception_register.read', ...(canDownload ? ['documents.file.download'] : [])], available_actions: [],
});

const json = (route: Route, data: unknown) => route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ success: true, data }) });
const paginated = (route: Route, data: unknown[]) => route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ success: true, data, pagination: { page: 1, page_size: 20, total_count: data.length, total_pages: 1, has_next: false, has_previous: false } }) });
const captureReviewable = async (page: Page, fileName: string) => {
  const evidence = page.getByTestId('exception-source-evidence');
  await evidence.scrollIntoViewIfNeeded();
  const box = await evidence.boundingBox();
  expect(box).not.toBeNull();
  expect(box!.y).toBeGreaterThanOrEqual(0);
  expect(box!.y + box!.height).toBeLessThanOrEqual(720);
  const screenshot = await page.screenshot({ path: path.join(evidenceDir, fileName), animations: 'disabled' });
  const stats = await page.evaluate(async dataUrl => {
    const image = new Image();
    image.src = dataUrl;
    await image.decode();
    const canvas = document.createElement('canvas');
    canvas.width = image.width; canvas.height = image.height;
    const context = canvas.getContext('2d')!;
    context.drawImage(image, 0, 0);
    const pixels = context.getImageData(0, 0, image.width, image.height).data;
    let opaqueDark = 0;
    const buckets = new Set<number>();
    for (let index = 0; index < pixels.length; index += 16) {
      const red = pixels[index]; const green = pixels[index + 1]; const blue = pixels[index + 2];
      if (red < 12 && green < 12 && blue < 12) opaqueDark += 1;
      buckets.add((red >> 5) * 64 + (green >> 5) * 8 + (blue >> 5));
    }
    const tileSize = 64;
    const columns = Math.ceil(image.width / tileSize);
    const rows = Math.ceil(image.height / tileSize);
    const uniform = Array<boolean>(columns * rows).fill(false);
    for (let tileY = 0; tileY < rows; tileY += 1) {
      for (let tileX = 0; tileX < columns; tileX += 1) {
        let min = 255; let max = 0;
        for (let y = tileY * tileSize; y < Math.min((tileY + 1) * tileSize, image.height); y += 4) {
          for (let x = tileX * tileSize; x < Math.min((tileX + 1) * tileSize, image.width); x += 4) {
            const offset = (y * image.width + x) * 4;
            for (let channel = 0; channel < 3; channel += 1) {
              min = Math.min(min, pixels[offset + channel]); max = Math.max(max, pixels[offset + channel]);
            }
          }
        }
        uniform[tileY * columns + tileX] = max - min <= 4;
      }
    }
    const visited = Array<boolean>(uniform.length).fill(false);
    let largestUniformRegion = 0;
    for (let start = 0; start < uniform.length; start += 1) {
      if (!uniform[start] || visited[start]) continue;
      const queue = [start]; visited[start] = true; let size = 0;
      while (queue.length) {
        const current = queue.pop()!; size += 1;
        const x = current % columns; const y = Math.floor(current / columns);
        for (const next of [x > 0 ? current - 1 : -1, x + 1 < columns ? current + 1 : -1, y > 0 ? current - columns : -1, y + 1 < rows ? current + columns : -1]) {
          if (next >= 0 && uniform[next] && !visited[next]) { visited[next] = true; queue.push(next); }
        }
      }
      largestUniformRegion = Math.max(largestUniformRegion, size);
    }
    return { width: image.width, height: image.height, darkRatio: opaqueDark / (pixels.length / 16), colorBuckets: buckets.size, largestUniformRegionRatio: largestUniformRegion / uniform.length };
  }, `data:image/png;base64,${screenshot.toString('base64')}`);
  expect(stats).toMatchObject({ width: 1280, height: 720 });
  expect(stats.darkRatio).toBeLessThan(0.2);
  expect(stats.colorBuckets).toBeGreaterThan(16);
  expect(stats.largestUniformRegionRatio).toBeLessThan(0.3);
};
