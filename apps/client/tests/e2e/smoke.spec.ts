import { expect, test } from '@playwright/test'

/**
 * Smoke test: the app boots and serves the login page.
 *
 * Run with `npm run test:e2e`. The Playwright config starts the Vite dev
 * server automatically unless PLAYWRIGHT_BASE_URL points at a running app.
 */
test('login page loads', async ({ page }) => {
  await page.goto('/login')
  await expect(page).toHaveTitle(/Lumidoc/i)
  await expect(page.locator('#root')).toBeVisible()
})
