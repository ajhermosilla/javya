import { test, expect } from '@playwright/test';

test.describe('Navigation', () => {
  test('can navigate between songs and setlists', async ({ page }) => {
    await page.goto('/');

    // Should start on songs page
    await expect(page.locator('h1')).toContainText('Songs');

    // Navigate to setlists (sidebar uses buttons, not links)
    await page.getByRole('button', { name: /setlists/i }).click();
    await expect(page.locator('h1')).toContainText('Setlists');

    // Navigate back to songs
    await page.getByRole('button', { name: /songs/i }).click();
    await expect(page.locator('h1')).toContainText('Songs');
  });

  test('sidebar is visible and functional', async ({ page }) => {
    await page.goto('/');

    // Sidebar should be visible
    await expect(page.locator('.sidebar')).toBeVisible();

    // App name should be visible
    await expect(page.getByText('Javya')).toBeVisible();
  });

  test('can switch language', async ({ page }) => {
    await page.goto('/');

    // Find language switcher
    const langSwitcher = page.locator('.language-switcher');
    await expect(langSwitcher).toBeVisible();

    // Switch to Spanish
    await langSwitcher.selectOption('es');

    // Page should show Spanish text
    await expect(page.locator('h1')).toContainText('Canciones');

    // Switch back to English
    await langSwitcher.selectOption('en');
    await expect(page.locator('h1')).toContainText('Songs');
  });
});
