import { test, expect } from '@playwright/test';

// Helper to get the main content page title (not sidebar)
const getPageTitle = (page: import('@playwright/test').Page) =>
  page.locator('main h1');

test.describe('Navigation', () => {
  test('can navigate between songs and setlists', async ({ page }) => {
    await page.goto('/');

    // Should start on songs page
    await expect(getPageTitle(page)).toContainText('Songs');

    // Navigate to setlists (sidebar uses buttons, not links)
    await page.getByRole('button', { name: /setlists/i }).click();
    await expect(getPageTitle(page)).toContainText('Setlists');

    // Navigate back to songs
    await page.getByRole('button', { name: /songs/i }).click();
    await expect(getPageTitle(page)).toContainText('Songs');
  });

  test('sidebar is visible and functional', async ({ page }) => {
    await page.goto('/');

    // Sidebar should be visible
    await expect(page.locator('.sidebar')).toBeVisible();

    // App name should be visible in sidebar
    await expect(page.locator('.sidebar-logo')).toContainText('Javya');
  });

  test('can switch language', async ({ page }) => {
    await page.goto('/');

    // Find language switcher
    const langSwitcher = page.locator('.language-switcher');
    await expect(langSwitcher).toBeVisible();

    // Switch to Spanish (click ES button)
    await langSwitcher.getByRole('button', { name: /es/i }).click();

    // Page should show Spanish text
    await expect(getPageTitle(page)).toContainText('Canciones');

    // Switch back to English (click EN button)
    await langSwitcher.getByRole('button', { name: /en/i }).click();
    await expect(getPageTitle(page)).toContainText('Songs');
  });
});
