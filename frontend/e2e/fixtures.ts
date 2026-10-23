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

/**
 * Every test gets its own server, database and clock-day, so no test depends on another.
 * After a conquest the qi card asks how much qi it took: unless a test is about that card
 * (`test.use({ autoQi: false })`), it is answered with Done, which keeps the estimate.
 * The tour's step cards would stand beside the buttons a test clicks: off, unless a test is about
 * the tour (`test.use({ tour: true })`). Learning goes on either way, but a find's "+1" is hidden
 * too: it is a second `status`, and under the fake clock it never goes away.
 */
export const test = base.extend<{ server: string; autoQi: boolean; tour: boolean }>({
  autoQi: [true, { option: true }],
  tour: [false, { option: true }],
  page: async ({ page, autoQi, tour }, use) => {
    if (!tour) {
      const off = await page.request.put('/api/knowledge', { data: { tour: false } });
      expect(off.ok(), 'tour off').toBeTruthy();
      await page.addInitScript(() => {
        document.addEventListener('DOMContentLoaded', () => {
          const style = document.createElement('style');
          style.textContent = ".find[role='status'] { display: none !important; }";
          document.head.append(style);
        });
      });
    }
    if (autoQi) {
      await page.addLocatorHandler(
        page.getByRole('dialog', { name: 'How much qi did this take?' }),
        async (card) => {
          await card.getByRole('button', { name: 'Done' }).click();
        },
      );
    }
    await use(page);
  },
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
      try {
        rmSync(home, { recursive: true, force: true, maxRetries: 10, retryDelay: 100 });
      } catch {
        // Windows may hold a file of the stopped server a while longer: a temp folder left
        // behind is no failure of the test.
      }
    }
  },
  baseURL: async ({ server }, use) => {
    await use(server);
  },
});

export { expect };
