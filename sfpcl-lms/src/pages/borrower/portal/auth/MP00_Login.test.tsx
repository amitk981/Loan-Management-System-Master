import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { describe, expect, it, vi } from 'vitest';
import MP00_Login from './MP00_Login';
import loginSource from './MP00_Login.tsx?raw';
import appSource from '../../../../App.tsx?raw';

describe('MP00 portal login authority (005FA2 regression)', () => {
  it('renders the real credential form', () => {
    const html = renderToStaticMarkup(
      <MP00_Login
        onSubmitLogin={vi.fn(async () => undefined)}
        onNavigateToActivation={vi.fn()}
        onNavigateToForgot={vi.fn()}
      />,
    );

    expect(html).toContain('Member Portal');
    expect(html).toContain('Sign in securely');
  });

  it('has no demo-login fallback path in the component', () => {
    // The pre-fix component accepted an `onLogin` prop and fell back to it when
    // onSubmitLogin was absent, yielding an unauthenticated demo borrower session.
    expect(loginSource).not.toContain('onLogin');
    expect(loginSource).toContain('await onSubmitLogin({ identifier, password: secret });');
  });

  it('App wires the portal login only to the real session handler', () => {
    // The pre-fix App passed onLogin={() => handleDemoLogin('borrower')} unconditionally,
    // ungated by DEMO_AUTH_ENABLED.
    expect(appSource).not.toContain("handleDemoLogin('borrower')");
    expect(appSource).toContain('onSubmitLogin={handleMemberLogin}');
  });
});
