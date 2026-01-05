import { test as setup, expect } from '@playwright/test';

const AUTH_FILE = 'playwright/.auth/user.json';

setup('authenticate', async ({ page }) => {
  // Go to login page
  await page.goto('/login');

  // Register a new user (first user becomes admin)
  await page.getByText(/Don't have an account/i).click();
  await page.getByRole('button', { name: /Create Account/i }).waitFor();

  await page.locator('#name').fill('Test User');
  await page.locator('#email').fill(`test-${Date.now()}@example.com`);
  await page.locator('#password').fill('testpassword123');

  await page.getByRole('button', { name: /Create Account/i }).click();

  // Wait for redirect to main app
  await expect(page.locator('h1')).toContainText('Songs', { timeout: 10000 });

  // Save authentication state
  await page.context().storageState({ path: AUTH_FILE });
});
