import { test, expect } from '@playwright/test';

test.describe('Setlists', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    // Navigate to setlists page
    await page.getByRole('link', { name: /setlists/i }).click();
    await expect(page.locator('h1')).toContainText('Setlists');
  });

  test('displays setlists page with title', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('Setlists');
    await expect(page.getByRole('button', { name: /add setlist/i })).toBeVisible();
  });

  test('can navigate to add setlist form', async ({ page }) => {
    await page.getByRole('button', { name: /add setlist/i }).click();
    await expect(page.getByRole('heading', { name: /add setlist/i })).toBeVisible();
    await expect(page.getByLabel(/song name/i)).toBeVisible();
  });

  test('can create a new setlist', async ({ page }) => {
    await page.getByRole('button', { name: /add setlist/i }).click();

    // Fill the form
    await page.getByLabel(/song name/i).fill('Sunday Service E2E');
    await page.getByLabel(/description/i).fill('Test description');

    // Submit
    await page.getByRole('button', { name: /save/i }).click();

    // Should return to list and show the new setlist
    await expect(page.locator('h1')).toContainText('Setlists');
    await expect(page.getByText('Sunday Service E2E')).toBeVisible();
  });

  test('can cancel setlist creation', async ({ page }) => {
    await page.getByRole('button', { name: /add setlist/i }).click();
    await page.getByLabel(/song name/i).fill('Should Not Exist');
    await page.getByRole('button', { name: /cancel/i }).click();

    await expect(page.locator('h1')).toContainText('Setlists');
    await expect(page.getByText('Should Not Exist')).not.toBeVisible();
  });

  test('can view setlist editor', async ({ page }) => {
    // First create a setlist
    await page.getByRole('button', { name: /add setlist/i }).click();
    await page.getByLabel(/song name/i).fill('Setlist To View');
    await page.getByRole('button', { name: /save/i }).click();

    // Wait for return to list
    await expect(page.locator('h1')).toContainText('Setlists');

    // Click on the setlist to view editor
    await page.getByText('Setlist To View').click();

    // Should show editor view
    await expect(page.getByRole('heading', { name: 'Setlist To View' })).toBeVisible();
    await expect(page.getByText(/song order/i)).toBeVisible();
    await expect(page.getByRole('button', { name: /back/i })).toBeVisible();
  });

  test('can edit a setlist', async ({ page }) => {
    // First create a setlist
    await page.getByRole('button', { name: /add setlist/i }).click();
    await page.getByLabel(/song name/i).fill('Setlist To Edit');
    await page.getByRole('button', { name: /save/i }).click();

    // Wait for return to list
    await expect(page.locator('h1')).toContainText('Setlists');

    // Find and click edit button
    const setlistCard = page.locator('.setlist-card', { hasText: 'Setlist To Edit' });
    await setlistCard.getByRole('button', { name: /edit/i }).click();

    // Should show edit form
    await expect(page.getByRole('heading', { name: /edit setlist/i })).toBeVisible();

    // Change the name
    await page.getByLabel(/song name/i).fill('Setlist Edited');
    await page.getByRole('button', { name: /save/i }).click();

    // Should return to list with updated name
    await expect(page.locator('h1')).toContainText('Setlists');
    await expect(page.getByText('Setlist Edited')).toBeVisible();
  });

  test('can delete a setlist', async ({ page }) => {
    // First create a setlist
    await page.getByRole('button', { name: /add setlist/i }).click();
    await page.getByLabel(/song name/i).fill('Setlist To Delete');
    await page.getByRole('button', { name: /save/i }).click();

    // Wait for return to list
    await expect(page.locator('h1')).toContainText('Setlists');
    await expect(page.getByText('Setlist To Delete')).toBeVisible();

    // Set up dialog handler before clicking delete
    page.on('dialog', dialog => dialog.accept());

    // Find and click delete button
    const setlistCard = page.locator('.setlist-card', { hasText: 'Setlist To Delete' });
    await setlistCard.getByRole('button', { name: /delete/i }).click();

    // Setlist should be removed
    await expect(page.getByText('Setlist To Delete')).not.toBeVisible();
  });

  test('can add songs to setlist', async ({ page }) => {
    // First create a song
    await page.getByRole('link', { name: /songs/i }).click();
    await page.getByRole('button', { name: /add song/i }).click();
    await page.getByLabel(/song name/i).fill('Song For Setlist');
    await page.getByLabel(/lyrics/i).fill('Some lyrics here');
    await page.getByRole('button', { name: /save/i }).click();
    await expect(page.locator('h1')).toContainText('Songs');

    // Now create a setlist
    await page.getByRole('link', { name: /setlists/i }).click();
    await page.getByRole('button', { name: /add setlist/i }).click();
    await page.getByLabel(/song name/i).fill('Setlist With Songs');
    await page.getByRole('button', { name: /save/i }).click();

    // Open setlist editor
    await page.getByText('Setlist With Songs').click();

    // Should see the song in the picker
    await expect(page.getByText('Song For Setlist')).toBeVisible();

    // Add the song to setlist
    await page.locator('.song-picker-item', { hasText: 'Song For Setlist' })
      .getByRole('button', { name: /\+/i }).click();

    // Song should now appear in the setlist
    await expect(page.locator('.editor-songs').getByText('Song For Setlist')).toBeVisible();

    // Save the setlist
    await page.getByRole('button', { name: /save/i }).click();
  });

  test('shows export buttons in editor', async ({ page }) => {
    // Create a setlist with a song
    await page.getByRole('link', { name: /songs/i }).click();
    await page.getByRole('button', { name: /add song/i }).click();
    await page.getByLabel(/song name/i).fill('Export Test Song');
    await page.getByLabel(/lyrics/i).fill('Lyrics for export');
    await page.getByRole('button', { name: /save/i }).click();

    await page.getByRole('link', { name: /setlists/i }).click();
    await page.getByRole('button', { name: /add setlist/i }).click();
    await page.getByLabel(/song name/i).fill('Export Test Setlist');
    await page.getByRole('button', { name: /save/i }).click();

    await page.getByText('Export Test Setlist').click();

    // Add song
    await page.locator('.song-picker-item', { hasText: 'Export Test Song' })
      .getByRole('button', { name: /\+/i }).click();

    // Save
    await page.getByRole('button', { name: /save/i }).click();

    // Export buttons should be visible
    await expect(page.getByRole('button', { name: /freeshow/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /quelea/i })).toBeVisible();
  });
});
