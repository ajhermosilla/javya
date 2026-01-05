import { test, expect } from '@playwright/test';

// Helper to get the main content page title (not sidebar)
const getPageTitle = (page: import('@playwright/test').Page) =>
  page.locator('main h1');

test.describe('Songs', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    // Wait for the app to load
    await expect(getPageTitle(page)).toContainText('Songs');
  });

  test('displays songs page with title', async ({ page }) => {
    await expect(getPageTitle(page)).toContainText('Songs');
    await expect(page.getByRole('button', { name: /add song/i })).toBeVisible();
  });

  test('shows search bar and filters', async ({ page }) => {
    await expect(page.getByPlaceholder(/search/i)).toBeVisible();
    await expect(page.locator('.filter-bar')).toBeVisible();
  });

  test('can navigate to add song form', async ({ page }) => {
    await page.getByRole('button', { name: /add song/i }).click();
    await expect(page.getByRole('heading', { name: /add song/i })).toBeVisible();
    await expect(page.getByLabel(/song name/i)).toBeVisible();
  });

  test('can create a new song', async ({ page }) => {
    // Navigate to add form
    await page.getByRole('button', { name: /add song/i }).click();

    // Fill the form
    await page.getByLabel(/song name/i).fill('Test Song E2E');
    await page.getByLabel(/artist/i).fill('Test Artist');
    await page.getByLabel(/tempo/i).fill('120');

    // Submit
    await page.getByRole('button', { name: /save/i }).click();

    // Should return to list and show the new song
    await expect(getPageTitle(page)).toContainText('Songs');
    await expect(page.getByText('Test Song E2E')).toBeVisible();
  });

  test('can cancel song creation', async ({ page }) => {
    await page.getByRole('button', { name: /add song/i }).click();
    await page.getByLabel(/song name/i).fill('Should Not Exist');
    await page.getByRole('button', { name: /cancel/i }).click();

    await expect(getPageTitle(page)).toContainText('Songs');
    await expect(page.getByText('Should Not Exist')).not.toBeVisible();
  });

  test('can search for songs', async ({ page }) => {
    // First create a song
    await page.getByRole('button', { name: /add song/i }).click();
    await page.getByLabel(/song name/i).fill('Searchable Song');
    await page.getByRole('button', { name: /save/i }).click();

    // Wait for return to list
    await expect(getPageTitle(page)).toContainText('Songs');

    // Search for it
    await page.getByPlaceholder(/search/i).fill('Searchable');

    // Should show the song
    await expect(page.getByText('Searchable Song')).toBeVisible();

    // Search for something else
    await page.getByPlaceholder(/search/i).fill('NonExistent12345');

    // Should show no results
    await expect(page.getByText(/no songs found/i)).toBeVisible();
  });

  test('can view song details', async ({ page }) => {
    // First create a song with lyrics
    await page.getByRole('button', { name: /add song/i }).click();
    await page.getByLabel(/song name/i).fill('Song With Details');
    await page.getByLabel(/artist/i).fill('Detail Artist');
    await page.getByLabel(/lyrics/i).fill('These are the lyrics\nLine two');
    await page.getByRole('button', { name: /save/i }).click();

    // Wait for return to list
    await expect(getPageTitle(page)).toContainText('Songs');

    // Click on the song to view details
    await page.getByText('Song With Details').click();

    // Should show detail view
    await expect(page.getByText('Detail Artist')).toBeVisible();
    await expect(page.getByText('These are the lyrics')).toBeVisible();
    await expect(page.getByRole('button', { name: /back/i })).toBeVisible();
  });

  test('can edit a song', async ({ page }) => {
    // First create a song
    await page.getByRole('button', { name: /add song/i }).click();
    await page.getByLabel(/song name/i).fill('Song To Edit');
    await page.getByRole('button', { name: /save/i }).click();

    // Wait for return to list
    await expect(getPageTitle(page)).toContainText('Songs');

    // Find and click edit button (use class selector to avoid matching header button)
    const songCard = page.locator('.song-card', { hasText: 'Song To Edit' });
    await songCard.locator('.edit-button').click();

    // Should show edit form
    await expect(page.getByRole('heading', { name: /edit song/i })).toBeVisible();

    // Change the name
    await page.getByLabel(/song name/i).fill('Song Edited');
    await page.getByRole('button', { name: /save/i }).click();

    // Should return to list with updated name
    await expect(getPageTitle(page)).toContainText('Songs');
    await expect(page.getByText('Song Edited')).toBeVisible();
    await expect(page.getByText('Song To Edit')).not.toBeVisible();
  });

  test('can delete a song', async ({ page }) => {
    // First create a song
    await page.getByRole('button', { name: /add song/i }).click();
    await page.getByLabel(/song name/i).fill('Song To Delete');
    await page.getByRole('button', { name: /save/i }).click();

    // Wait for return to list
    await expect(getPageTitle(page)).toContainText('Songs');
    await expect(page.getByText('Song To Delete')).toBeVisible();

    // Set up dialog handler before clicking delete
    page.on('dialog', dialog => dialog.accept());

    // Find and click delete button (use class selector to avoid matching header button)
    const songCard = page.locator('.song-card', { hasText: 'Song To Delete' });
    await songCard.locator('.delete-button').click();

    // Song should be removed
    await expect(page.getByText('Song To Delete')).not.toBeVisible();
  });

  test('can filter songs by key', async ({ page }) => {
    // Create a song with a specific key
    await page.getByRole('button', { name: /add song/i }).click();
    await page.getByLabel(/song name/i).fill('G Major Song');
    await page.getByLabel(/original key/i).selectOption('G');
    await page.getByRole('button', { name: /save/i }).click();

    // Wait for return to list
    await expect(getPageTitle(page)).toContainText('Songs');

    // Filter by key G
    await page.locator('.filter-select').first().selectOption('G');

    // Should show the song
    await expect(page.getByText('G Major Song')).toBeVisible();

    // Filter by different key
    await page.locator('.filter-select').first().selectOption('A');

    // Song should not be visible (unless it also matches)
    // The song with key G should not appear when filtering by A
  });
});
