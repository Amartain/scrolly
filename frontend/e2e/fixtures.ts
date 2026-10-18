import { spawn } from 'node:child_process';
import { mkdtempSync, rmSync } from 'node:fs';
import { createServer } from 'node:net';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { test as base, expect } from '@playwright/test';

async function freePort(): Promise<number> {
  return new Promise((resolve, reject) => {
    const probe = createServer();
    probe.once('error', reject);
    probe.listen(0, '127.0.0.1', () => {
      const { port } = probe.address() as { port: number };
      probe.close(() => resolve(port));
    });
  });
}

async function waitUntilHealthy(url: string, timeoutMs = 30_000): Promise<void> {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    try {
      if ((await fetch(url)).ok) return;
    } catch {
      // The server is still starting.
    }
    await new Promise((resolve) => setTimeout(resolve, 100));
  }
  throw new Error(`The server did not start: ${url}`);
}

/** Every test gets its own server, database and clock-day, so no test depends on another. */
export const test = base.extend<{ server: string }>({
  // eslint-disable-next-line no-empty-pattern
  server: async ({}, use) => {
    const home = mkdtempSync(join(tmpdir(), 'scrolly-e2e-'));
    const port = await freePort();
    const python = process.env.SCROLLY_PYTHON ?? 'python';
    const child = spawn(python, ['-m', 'scrolly', '--no-browser', '--port', String(port)], {
      env: { ...process.env, SCROLLY_HOME: home },
      stdio: 'ignore',
    });
    const url = `http://127.0.0.1:${port}`;
    try {
      await waitUntilHealthy(`${url}/api/health`);
      await use(url);
    } finally {
      child.kill();
      rmSync(home, { recursive: true, force: true, maxRetries: 10, retryDelay: 100 });
    }
  },
  baseURL: async ({ server }, use) => {
    await use(server);
  },
});

export { expect };
