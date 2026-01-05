import { test as setup, expect } from '@playwright/test';

const AUTH_FILE = 'playwright/.auth/user.json';

setup('authenticate', async ({ page }) => {
  // Go to login page
  await page.goto('/login');

  // Wait for the login form to be fully loaded
  await page.waitForLoadState('domcontentloaded');
  await page.locator('.login-form').waitFor({ state: 'visible' });

  // Switch to registration mode by clicking the "Create Account" link in toggle-mode section
  const toggleButton = page.locator('.toggle-mode button');
  await toggleButton.waitFor({ state: 'visible' });
  await toggleButton.click();

  // Wait for registration form to appear (name field visible)
  await page.locator('#name').waitFor({ state: 'visible' });

  // Fill registration form
  await page.locator('#name').fill('Test User');
  await page.locator('#email').fill(`test-${Date.now()}@example.com`);
  await page.locator('#password').fill('testpassword123');

  // Submit registration form
  await page.locator('.submit-button').click();

  // Wait for redirect to main app - look for the main content area heading
  await expect(page.locator('main h1')).toContainText('Songs', { timeout: 30000 });

  // Save authentication state
  await page.context().storageState({ path: AUTH_FILE });
});
