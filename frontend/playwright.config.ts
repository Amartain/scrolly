import { mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { defineConfig } from '@playwright/test';

const PORT = 4799;
const home = mkdtempSync(join(tmpdir(), 'scrolly-e2e-'));

export default defineConfig({
  testDir: './e2e',
  workers: 1,
  reporter: 'list',
  use: { baseURL: `http://127.0.0.1:${PORT}` },
  webServer: {
    command: `${process.env.SCROLLY_PYTHON ?? 'python'} -m scrolly --no-browser --port ${PORT}`,
    url: `http://127.0.0.1:${PORT}/api/health`,
    env: { SCROLLY_HOME: home },
    reuseExistingServer: false,
    timeout: 30_000,
  },
});
