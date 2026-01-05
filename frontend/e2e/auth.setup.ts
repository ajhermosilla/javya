import { test as setup, expect } from '@playwright/test';

const AUTH_FILE = 'playwright/.auth/user.json';

setup('authenticate', async ({ page }) => {
  // Go to login page
  await page.goto('/login');

  // Wait for the login form to load
  await page.waitForLoadState('networkidle');

  // Switch to registration mode by clicking the "Create Account" link in toggle-mode section
  await page.locator('.toggle-mode button').click();

  // Wait for registration form to appear (name field visible)
  await page.locator('#name').waitFor();

  await page.locator('#name').fill('Test User');
  await page.locator('#email').fill(`test-${Date.now()}@example.com`);
  await page.locator('#password').fill('testpassword123');

  // Submit registration form
  await page.locator('.submit-button').click();

  // Wait for redirect to main app
  await expect(page.locator('h1')).toContainText('Songs', { timeout: 10000 });

  // Save authentication state
  await page.context().storageState({ path: AUTH_FILE });
});
