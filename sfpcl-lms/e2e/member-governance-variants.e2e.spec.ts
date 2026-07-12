import fs from 'fs';
import path from 'path';
import { expect, test, type Page, type Request } from '@playwright/test';
import { E2E_PASSWORD, staffLogin } from './helpers';

const evidenceDir = process.env.RALPH_EVIDENCE_DIR;
if (!evidenceDir) throw new Error('RALPH_EVIDENCE_DIR is required for member governance variants');
fs.mkdirSync(evidenceDir, { recursive: true });

const FINANCE_EMAIL = 'e2e.credit.finance@sfpcl.example';
const FINANCE_NAME = 'E2E Deputy Manager Finance';
const MANAGER_EMAIL = 'e2e.credit.manager@sfpcl.example';
const VERIFIED_MEMBER_ID = '00000000-0000-4000-8000-000000000602';

test('complete member variants and protected identity approval cross real staff sessions', async ({ page }) => {
  const suffix = String(Date.now()).slice(-4);
  const individual = identities('IND', suffix, 'A');
  const institution = identities('INS', suffix, 'B');
  const mutations: Request[] = [];
  const canonicalReads: Request[] = [];
  page.on('request', request => {
    const pathname = new URL(request.url()).pathname;
    if (request.method() === 'POST' && pathname === '/api/v1/members/') mutations.push(request);
    if (request.method() === 'GET' && /^\/api\/v1\/members\/[0-9a-f-]+\/$/.test(pathname)) canonicalReads.push(request);
  });

  await staffLogin(page, FINANCE_EMAIL, E2E_PASSWORD);
  await openMembers(page);
  await registerIndividual(page, individual);
  expect(mutations).toHaveLength(1);
  expect(canonicalReads).toHaveLength(1);
  expect(mutations[0].postDataJSON()).toEqual(individual.body);
  await expect(page.getByText(maskPan(individual.pan))).toBeVisible();
  await expect(page.getByText(maskAadhaar(individual.aadhaar), { exact: true })).toBeVisible();
  const ordinaryUpdate = page.waitForResponse(response => response.request().method() === 'PATCH'
    && /^\/api\/v1\/members\/[0-9a-f-]+\/$/.test(new URL(response.url()).pathname));
  await page.getByLabel('Display Name').fill('Complete Synthetic Farmer Corrected');
  await page.getByRole('button', { name: 'Save member' }).click();
  expect((await ordinaryUpdate).status()).toBe(200);
  await expect(page.getByRole('heading', { name: 'Complete Synthetic Farmer Corrected' })).toBeVisible();
  expect(canonicalReads).toHaveLength(2);
  await capture(page, 'member-individual-complete-reloaded.png');

  await openMembers(page);
  await registerInstitution(page, institution);
  expect(mutations).toHaveLength(2);
  expect(canonicalReads).toHaveLength(3);
  expect(mutations[1].postDataJSON()).toEqual(institution.body);
  await expect(page.getByText(maskPan(institution.pan))).toBeVisible();
  await capture(page, 'member-institution-complete-reloaded.png');

  await openSeededVerifiedMember(page);
  await expect(page.getByText('Verified identity locked')).toBeVisible();
  await page.getByRole('button', { name: 'Correct verified identity' }).click();
  await page.getByLabel('PAN').fill(`CDEFG${suffix}H`);
  await page.getByLabel('Reverification Reason').fill('Synthetic source-backed protected identity correction');
  const requested = page.waitForResponse(response => response.request().method() === 'POST'
    && response.url().endsWith(`/api/v1/members/${VERIFIED_MEMBER_ID}/identity-change-requests/`));
  await page.getByRole('button', { name: 'Request identity change' }).click();
  expect((await requested).status()).toBe(200);
  const requesterApproval = projectedApproval(page);
  await expect(requesterApproval).toBeDisabled();
  await expect(requesterApproval).toHaveAttribute('title', 'Missing identity change approval permission.');
  await capture(page, 'member-identity-requester-denied.png');

  await signOut(page);
  await staffLogin(page, MANAGER_EMAIL, E2E_PASSWORD);
  await openSeededVerifiedMember(page);
  await expect(projectedApproval(page)).toBeEnabled();
  const approve = page.locator('button.btn-primary', { hasText: /^Approve identity change$/ });
  await expect(approve).toBeVisible();
  const approved = page.waitForResponse(response => response.request().method() === 'POST'
    && /\/api\/v1\/member-identity-change-requests\/[0-9a-f-]+\/approve\/$/.test(new URL(response.url()).pathname));
  await approve.click();
  expect((await approved).status()).toBe(200);
  await expect(approve).toHaveCount(0);
  await expect(page.getByText(maskPan(`CDEFG${suffix}H`))).toBeVisible();
  await capture(page, 'member-identity-checker-approved.png');
});

function identities(prefix: string, suffix: string, panPrefix: string) {
  const pan = `${panPrefix}BCDE${suffix}F`;
  const aadhaar = `12345678${suffix}`;
  const legalName = prefix === 'IND' ? 'Complete Synthetic Farmer' : 'Complete Synthetic Producer';
  const common = {
    member_type: prefix === 'IND' ? 'individual_farmer' : 'fpc', legal_name: legalName,
    display_name: legalName, folio_number: `${prefix}-${Date.now()}-${suffix}`,
    membership_start_date: '2024-04-01', pan, registered_address: {
      line1: 'Synthetic Registry Road', line2: 'Evidence Block', village_city: 'Nashik',
      district: 'Nashik', state: 'Maharashtra', pincode: '422001',
    }, mobile_number: `+91910000${suffix}`, email: `${prefix.toLowerCase()}.${Date.now()}@example.test`,
  };
  const body = prefix === 'IND' ? { ...common, aadhaar, individual_profile: {
    first_name: 'Complete', middle_name: 'Synthetic', last_name: 'Farmer', gender: 'female',
    date_of_birth: '1980-01-15', occupation: 'Farmer', land_area_under_cultivation_acres: '5.25',
    primary_crop: 'grapes', services_availed_flag: true, employment_or_service_years: '7',
  } } : { ...common, producer_institution_profile: {
    institution_type: 'farmer_producer_company', registration_number: `REG-${suffix}`,
    authorised_signatory_name: 'Synthetic Signatory', authorised_signatory_pan: `ZBCDE${suffix}Y`,
    authorised_signatory_aadhaar: `87654321${suffix}`, board_resolution_required_flag: true,
    services_availed_flag: true, produce_supply_years: '6',
  } };
  return { pan, aadhaar, body };
}

async function registerIndividual(page: Page, fixture: ReturnType<typeof identities>) {
  await startRegistration(page);
  await fillCommon(page, fixture.body as Record<string, unknown>);
  const profile = fixture.body.individual_profile as Record<string, string | boolean>;
  for (const [label, key] of [['First Name', 'first_name'], ['Middle Name', 'middle_name'], ['Last Name', 'last_name'], ['Gender', 'gender'], ['Occupation', 'occupation'], ['Cultivation Area (acres)', 'land_area_under_cultivation_acres'], ['Primary Crop', 'primary_crop'], ['Employment / Service Years', 'employment_or_service_years']] as const) await page.getByLabel(label).fill(String(profile[key]));
  await page.getByLabel('Date of Birth').fill(String(profile.date_of_birth));
  await page.getByLabel('Services Availed').fill('true');
  await page.getByLabel('Aadhaar').fill(fixture.aadhaar);
  await saveMember(page, String(fixture.body.legal_name));
}

async function registerInstitution(page: Page, fixture: ReturnType<typeof identities>) {
  await startRegistration(page);
  await page.getByLabel('Member Type').selectOption('fpc');
  await fillCommon(page, fixture.body as Record<string, unknown>);
  const profile = fixture.body.producer_institution_profile as Record<string, string | boolean>;
  for (const [label, key] of [['Institution Type', 'institution_type'], ['Registration Number', 'registration_number'], ['Authorised Signatory', 'authorised_signatory_name'], ['Signatory PAN', 'authorised_signatory_pan'], ['Signatory Aadhaar', 'authorised_signatory_aadhaar'], ['Produce Supply Years', 'produce_supply_years']] as const) await page.getByLabel(label).fill(String(profile[key]));
  await page.getByLabel('Board Resolution Required').fill('true');
  await page.getByLabel('Services Availed').fill('true');
  await saveMember(page, String(fixture.body.legal_name));
}

async function startRegistration(page: Page) { await page.getByRole('button', { name: 'Register Member' }).click(); }
async function fillCommon(page: Page, body: Record<string, unknown>) {
  const address = body.registered_address as Record<string, string>;
  for (const [label, key] of [['Legal Name', 'legal_name'], ['Display Name', 'display_name'], ['Folio Number', 'folio_number'], ['Membership Start Date', 'membership_start_date'], ['Mobile Number', 'mobile_number'], ['Email', 'email'], ['PAN', 'pan']] as const) await page.getByLabel(label, { exact: true }).fill(String(body[key]));
  for (const [label, key] of [['Address Line 1', 'line1'], ['Address Line 2', 'line2'], ['Village / City', 'village_city'], ['District', 'district'], ['State', 'state'], ['Pincode', 'pincode']] as const) await page.getByLabel(label).fill(address[key]);
}
async function saveMember(page: Page, legalName: string) {
  const saved = page.waitForResponse(response => response.request().method() === 'POST' && new URL(response.url()).pathname === '/api/v1/members/');
  await page.getByRole('button', { name: 'Save member' }).click();
  expect((await saved).status()).toBe(200);
  await expect(page.getByRole('heading', { name: legalName })).toBeVisible();
}
async function openMembers(page: Page) {
  await page.getByRole('button', { name: 'Members & Borrowers' }).click();
  await expect(page.getByRole('heading', { name: 'Member Directory' })).toBeVisible();
}
async function openSeededVerifiedMember(page: Page) {
  await openMembers(page);
  await page.getByPlaceholder('Search by name or folio...').fill('Epic 006 Browser Member');
  await page.getByRole('row').filter({ hasText: 'Epic 006 Browser Member' }).getByRole('button', { name: 'Profile' }).click();
  await expect(page.getByRole('heading', { name: 'Epic 006 Browser Member' })).toBeVisible();
}
async function signOut(page: Page) {
  await page.getByRole('button', { name: new RegExp(`^${FINANCE_NAME}`) }).click();
  await page.getByRole('button', { name: 'Sign out' }).click();
  await expect(page.getByRole('heading', { name: 'Sign in to your account' })).toBeVisible();
}
const projectedApproval = (page: Page) => page.locator('button.btn-secondary', { hasText: /^Approve identity change$/ });
const maskPan = (pan: string) => `******${pan.slice(-4)}`;
const maskAadhaar = (aadhaar: string) => `********${aadhaar.slice(-4)}`;
const capture = (page: Page, name: string) => page.screenshot({ path: path.join(evidenceDir, name), fullPage: true, animations: 'disabled' });
