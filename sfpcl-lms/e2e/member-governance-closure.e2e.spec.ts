import fs from 'fs';
import path from 'path';
import { expect, test, type Page } from '@playwright/test';
import { E2E_PASSWORD, staffLogin, ZERO_EMAIL } from './helpers';

const evidenceDir = process.env.RALPH_EVIDENCE_DIR;
if (!evidenceDir) throw new Error('RALPH_EVIDENCE_DIR is required for member governance closure');
fs.mkdirSync(evidenceDir, { recursive: true });

const API_ORIGIN = 'http://127.0.0.1:8000';
const FINANCE_EMAIL = 'e2e.credit.finance@sfpcl.example';
const MANAGER_EMAIL = 'e2e.credit.manager@sfpcl.example';
const VERIFIED_MEMBER_ID = '00000000-0000-4000-8000-000000000602';

test('member creation, canonical update, approved identity correction, and denial use real sessions', async ({ page }) => {
  await staffLogin(page, FINANCE_EMAIL, E2E_PASSWORD);
  await openMembers(page);

  await page.getByRole('button', { name: 'Register Member' }).click();
  await page.getByLabel('Legal Name').fill('Governance Closure Farmer');
  await page.getByLabel('Display Name').fill('Governance Closure Farmer');
  await page.getByLabel('Folio Number').fill('FOL-E2E-006Y3');
  await page.getByLabel('Membership Start Date').fill('2024-04-01');
  await page.getByLabel('Mobile Number').fill('+919000000063');
  await page.getByLabel('Email').fill('governance.closure@example.test');
  await page.getByLabel('Address Line 1').fill('Synthetic Governance Road');
  await page.getByLabel('Village / City').fill('Nashik');
  await page.getByLabel('District').fill('Nashik');
  await page.getByLabel('State').fill('Maharashtra');
  await page.getByLabel('Pincode').fill('422001');
  await page.getByLabel('First Name').fill('Governance');
  await page.getByLabel('Last Name').fill('Farmer');
  await page.getByLabel('PAN').fill('LMNOP4321Q');
  await page.getByLabel('Aadhaar').fill('987654321012');

  const created = waitForMutation(page, 'POST', /\/api\/v1\/members\/$/);
  const createdCanonical = waitForCanonicalMember(page);
  await page.getByRole('button', { name: 'Save member' }).click();
  expect((await created).status()).toBe(200);
  expect((await createdCanonical).status()).toBe(200);
  await expect(page.getByRole('heading', { name: 'Governance Closure Farmer' })).toBeVisible();
  await capture(page, 'member-create-submitted.png');

  await page.getByLabel('Display Name').fill('Governance Closure Farmer Updated');
  const updated = waitForMutation(page, 'PATCH', /\/api\/v1\/members\/[0-9a-f-]+\/$/);
  const updatedCanonical = waitForCanonicalMember(page);
  await page.getByRole('button', { name: 'Save member' }).click();
  expect((await updated).status()).toBe(200);
  expect((await updatedCanonical).status()).toBe(200);
  await expect(page.getByRole('heading', { name: 'Governance Closure Farmer Updated' })).toBeVisible();
  await capture(page, 'member-update-refetched.png');

  await openMembers(page);
  await page.getByPlaceholder('Search by name or folio...').fill('Epic 006 Browser Member');
  const verifiedRow = page.getByRole('row').filter({ hasText: 'Epic 006 Browser Member' });
  await verifiedRow.getByRole('button', { name: 'Profile' }).click();
  await expect(page.getByText('Verified identity locked')).toBeVisible();
  await page.getByRole('button', { name: 'Correct verified identity' }).click();
  await page.getByLabel('PAN').fill('PQRST6789U');
  await page.getByLabel('Reverification Reason').fill('Correction backed by synthetic source evidence');
  const requested = waitForMutation(page, 'POST', new RegExp(`/api/v1/members/${VERIFIED_MEMBER_ID}/identity-change-requests/$`));
  const requestedCanonical = waitForCanonicalMember(page, VERIFIED_MEMBER_ID);
  await page.getByRole('button', { name: 'Request identity change' }).click();
  expect((await requested).status()).toBe(200);
  expect((await requestedCanonical).status()).toBe(200);
  await expect(page.getByRole('button', { name: 'Correct verified identity' })).toHaveCount(0);
  await capture(page, 'member-identity-change-requested.png');

  await switchStaffUser(page, MANAGER_EMAIL);
  await openMembers(page);
  await page.getByPlaceholder('Search by name or folio...').fill('Epic 006 Browser Member');
  await page.getByRole('row').filter({ hasText: 'Epic 006 Browser Member' }).getByRole('button', { name: 'Profile' }).click();
  const approveIdentityChange = page.locator('button.btn-primary', { hasText: /^Approve identity change$/ });
  await expect(approveIdentityChange).toBeVisible();
  const approved = waitForMutation(page, 'POST', /\/api\/v1\/member-identity-change-requests\/[0-9a-f-]+\/approve\/$/);
  const approvedCanonical = waitForCanonicalMember(page, VERIFIED_MEMBER_ID);
  await approveIdentityChange.click();
  expect((await approved).status()).toBe(200);
  expect((await approvedCanonical).status()).toBe(200);
  await expect(approveIdentityChange).toHaveCount(0);
  await capture(page, 'member-identity-change-approved.png');

  await switchStaffUser(page, ZERO_EMAIL);
  await expect(page.getByRole('button', { name: 'Members & Borrowers' })).toHaveCount(0);
  const denied = await browserPost(page, `/api/v1/members/${VERIFIED_MEMBER_ID}/identity-change-requests/`, {
    version: 2,
    pan: 'ABCDE1234F',
    reason: 'Synthetic denied mutation',
  });
  expect(denied.status).toBe(403);
  expect(denied.body).toMatchObject({ success: false, error: { code: 'FORBIDDEN' } });
  await capture(page, 'member-governance-denied.png');
});

async function openMembers(page: Page) {
  await page.getByRole('button', { name: 'Members & Borrowers' }).click();
  await expect(page.getByRole('heading', { name: 'Member Directory' })).toBeVisible();
}

async function switchStaffUser(page: Page, email: string) {
  await page.evaluate(() => localStorage.removeItem('sfpcl_staff_auth_session'));
  await page.context().clearCookies();
  await staffLogin(page, email, E2E_PASSWORD);
}

function waitForMutation(page: Page, method: string, pathname: RegExp) {
  return page.waitForResponse(response => response.request().method() === method && pathname.test(new URL(response.url()).pathname));
}

function waitForCanonicalMember(page: Page, memberId?: string) {
  const pathname = memberId
    ? new RegExp(`/api/v1/members/${memberId}/$`)
    : /\/api\/v1\/members\/[0-9a-f-]+\/$/;
  return page.waitForResponse(response => response.request().method() === 'GET' && pathname.test(new URL(response.url()).pathname));
}

async function browserPost(page: Page, pathname: string, body: Record<string, unknown>) {
  return page.evaluate(async ({ origin, target, payload }) => {
    const raw = localStorage.getItem('sfpcl_staff_auth_session');
    const accessToken = raw ? JSON.parse(raw).accessToken : '';
    const response = await fetch(`${origin}${target}`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${accessToken}`, 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return { status: response.status, body: await response.json() };
  }, { origin: API_ORIGIN, target: pathname, payload: body });
}

const capture = (page: Page, name: string) => page.screenshot({
  path: path.join(evidenceDir, name),
  fullPage: true,
  animations: 'disabled',
});
