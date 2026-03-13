import { test as setup, expect } from '@playwright/test';

const AUTH_FILE = 'playwright/.auth/user.json';
const ADMIN_EMAIL = 'e2e-admin@test.com';
const ADMIN_PASSWORD = 'testpassword123';
const ADMIN_NAME = 'E2E Admin';

setup('authenticate', async ({ page }) => {
  await page.goto('/login');
  await page.waitForLoadState('domcontentloaded');
  await page.locator('.login-form').waitFor({ state: 'visible' });

  // Try logging in with the known E2E admin account
  await page.locator('#email').fill(ADMIN_EMAIL);
  await page.locator('#password').fill(ADMIN_PASSWORD);
  await page.locator('.submit-button').click();

  // Check if login succeeded (redirect to main app) or failed (error message)
  const result = await Promise.race([
    page.locator('main h1').waitFor({ timeout: 5000 }).then(() => 'logged-in' as const),
    page.locator('.error-message').waitFor({ timeout: 5000 }).then(() => 'login-failed' as const),
  ]);

  if (result === 'login-failed') {
    // Account doesn't exist — register (first user becomes admin)
    const toggleButton = page.locator('.toggle-mode button');
    await toggleButton.click();
    await page.locator('#name').waitFor({ state: 'visible' });

    await page.locator('#name').fill(ADMIN_NAME);
    await page.locator('#email').fill(ADMIN_EMAIL);
    await page.locator('#password').fill(ADMIN_PASSWORD);
    await page.locator('.submit-button').click();

    await expect(page.locator('main h1')).toContainText('Songs', { timeout: 30000 });
  }

  // Save authentication state
  await page.context().storageState({ path: AUTH_FILE });
});
