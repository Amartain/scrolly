import { defineConfig } from '@playwright/test';

// Each test starts its own server (see e2e/fixtures.ts), so there is no shared webServer here.
export default defineConfig({
  testDir: './e2e',
  // Every test has its own server, database and port, so tests can run side by side.
  workers: 4,
  reporter: 'list',
});
