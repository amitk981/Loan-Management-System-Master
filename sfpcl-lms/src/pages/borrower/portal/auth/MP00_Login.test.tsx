import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { describe, expect, expectTypeOf, it, vi } from 'vitest';
import MP00_Login from './MP00_Login';

describe('MP00 portal login authority (005FA3)', () => {
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

  it('requires the real-session callback and exposes no alternate success callback', () => {
    type Props = React.ComponentProps<typeof MP00_Login>;
    expectTypeOf<Props['onSubmitLogin']>().toBeFunction();
    expectTypeOf<Props>().not.toHaveProperty('onLogin');
  });
});
