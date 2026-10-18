import { defineConfig } from '@playwright/test';

// Each test starts its own server (see e2e/fixtures.ts), so there is no shared webServer here.
export default defineConfig({
  testDir: './e2e',
  workers: 1,
  reporter: 'list',
});
