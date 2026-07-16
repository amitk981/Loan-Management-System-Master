import { expect, test } from '@playwright/test';

test('the centrally selected browser can create a page', async ({ page }) => {
  await page.goto('data:text/html,<title>Ralph browser probe</title>ready');
  await expect(page).toHaveTitle('Ralph browser probe');
});
