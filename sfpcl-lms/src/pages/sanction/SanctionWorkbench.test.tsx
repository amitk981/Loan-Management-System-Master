import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { describe, expect, it, vi } from 'vitest';
import appSource from '../../App.tsx?raw';
import { RoleProvider } from '../../contexts/RoleContext';
import SanctionWorkbench from './SanctionWorkbench';

describe('app shell application authority', () => {
  it('does not seed or mutate application workflow state in App.tsx', () => {
    expect(appSource).not.toMatch(/from ['"].*data\/mockData['"]/);
    expect(appSource).not.toContain('initialApplications');
    expect(appSource).not.toContain('setApplications');
    expect(appSource).not.toContain('updateApplicationStatus');
  });

  it('renders an explicit not-wired state for the shell consumer without mock records', () => {
    const html = renderToStaticMarkup(
      <RoleProvider>
        <SanctionWorkbench
          applications={[]}
          onOpenApplication={vi.fn()}
        />
      </RoleProvider>,
    );

    expect(html).toContain('Sanction queue data is not connected yet');
    expect(html).toContain('No application records are shown until sanction API wiring is complete.');
    expect(html).not.toContain('Sanction queue is clear');
    expect(html).not.toContain('LOAN-');
  });
});
