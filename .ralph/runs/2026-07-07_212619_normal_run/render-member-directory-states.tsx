import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { mkdirSync, readdirSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { MemberDirectoryView } from '../../../sfpcl-lms/src/pages/members/MemberDirectory';
import type { MemberDirectoryItem } from '../../../sfpcl-lms/src/services/memberDirectoryApi';

const outDir = resolve('../.ralph/runs/2026-07-07_212619_normal_run/evidence/screenshots/member-directory-html');
mkdirSync(outDir, { recursive: true });

const cssFile = readdirSync(resolve('dist/assets')).find(file => file.endsWith('.css'));
if (!cssFile) throw new Error('Built CSS asset was not found.');
const cssHref = resolve(`dist/assets/${cssFile}`);

const member: MemberDirectoryItem = {
  member_id: 'member-screen-1',
  member_number: 'MEM-SCREEN-001',
  member_type: 'individual_farmer',
  legal_name: 'Ramesh Screenshot Patil',
  display_name: 'Ramesh Screenshot Patil',
  folio_number: 'FOL-SCREEN-001',
  membership_status: 'active',
  kyc_status: 'verified',
  rekyc_due_date: '2027-06-22',
  default_status: 'no_default',
  mobile_number: '******7890',
  email: 'ramesh.screen@example.com',
  share_summary: {
    number_of_shares: 100,
    holding_mode: 'physical',
    available_share_count: 100,
  },
  active_member_status: {
    status: 'active',
    verified_at: '2026-06-22T10:30:00Z',
  },
};

const states = [
  { name: 'populated', status: 'success' as const, members: [member], message: '' },
  { name: 'empty', status: 'success' as const, members: [], message: '' },
  {
    name: 'forbidden',
    status: 'forbidden' as const,
    members: [],
    message: 'You do not have permission to read members.',
  },
  {
    name: 'unauthorized',
    status: 'unauthorized' as const,
    members: [],
    message: 'Please sign in to continue.',
  },
  {
    name: 'api-error',
    status: 'error' as const,
    members: [],
    message: 'Network unavailable',
  },
];

for (const state of states) {
  const body = renderToStaticMarkup(
    <MemberDirectoryView
      status={state.status}
      message={state.message}
      members={state.members}
      search=""
      kycFilter="all"
      typeFilter="all"
      onSearchChange={() => undefined}
      onKycFilterChange={() => undefined}
      onTypeFilterChange={() => undefined}
      onSelect={() => undefined}
      canViewMembers
    />,
  );
  writeFileSync(
    resolve(outDir, `${state.name}.html`),
    `<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="file://${cssHref}"><title>${state.name}</title></head><body class="bg-slate-50"><main class="max-w-7xl mx-auto">${body}</main></body></html>`,
  );
}

console.log(`Rendered ${states.length} member directory evidence pages to ${outDir}`);
