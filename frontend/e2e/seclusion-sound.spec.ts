import type { Page } from '@playwright/test';
import { expect, test } from './fixtures';
import { sealDay, section } from './helpers';

/* eslint-disable @typescript-eslint/no-explicit-any */
const room = (page: Page) => section(page, 'Focus Scroll');
const sounds = (page: Page) => page.evaluate(() => (window as any).__sounds as number[]);
const notices = (page: Page) => page.evaluate(() => (window as any).__notified as string[][]);

// The pitch each sound starts on, so a test can tell which one rang.
const KNOCK = 990;
const BOWL = 196;
const BELL = 1319;
const FINAL = 73;
const TICK = 880;

/** Stand-ins for Web Audio and Notification that only write down what was asked of them. */
async function listen(page: Page) {
  await page.addInitScript(() => {
    const w = window as any;
    w.__sounds = [];
    w.__notified = [];
    class Param {
      value = 0;
      setValueAtTime(value: number) {
        this.value = value;
        return this;
      }
      linearRampToValueAtTime() {
        return this;
      }
      exponentialRampToValueAtTime() {
        return this;
      }
    }
    class Node {
      connect(next: unknown) {
        return next;
      }
    }
    class Audio {
      currentTime = 0;
      destination = new Node();
      private first = true;
      resume() {
        return Promise.resolve();
      }
      close() {
        return Promise.resolve();
      }
      createGain() {
        return Object.assign(new Node(), { gain: new Param() });
      }
      createOscillator() {
        const tone: any = Object.assign(new Node(), { frequency: new Param(), type: 'sine' });
        tone.start = () => {
          if (this.first) w.__sounds.push(Math.round(tone.frequency.value));
          this.first = false;
        };
        tone.stop = () => {};
        return tone;
      }
    }
    w.AudioContext = Audio;
    w.Notification = class {
      static permission = 'granted';
      static requestPermission() {
        return Promise.resolve('granted');
      }
      constructor(title: string, options?: { body?: string }) {
        w.__notified.push([title, options?.body ?? '']);
      }
    };
  });
}

/** Answer every request for the room with this state of the Cycles or Flow, so a phase can end on cue. */
async function serve(page: Page, current: { patch: (state: any) => void }) {
  await page.route('**/api/seclusion**', async (route) => {
    const reply = await route.fetch();
    const state = await reply.json();
    current.patch(state);
    await route.fulfill({ response: reply, json: state });
  });
}

const cycles = (phase: string, remaining: number) => (state: any) => {
  state.discipline = 'cycles';
  state.flow = null;
  state.cycles = {
    phase,
    cycle: 1,
    cycles: 1,
    remaining_s: remaining,
    total_s: 60,
    running: remaining > 0,
  };
};

async function enter(page: Page) {
  await sealDay(page, 'Write report');
  await page.goto('/');
  await page.getByRole('button', { name: /Enter Seclusion/ }).click();
  await expect(room(page)).toBeVisible();
}

test('the volume hides behind the speaker; Esc closes it and the room stays', async ({ page }) => {
  await enter(page);
  const popover = page.getByRole('group', { name: 'Sound' });
  await expect(popover).toHaveCount(0);
  await page.getByRole('button', { name: 'Sound' }).click();
  await expect(popover.getByRole('slider', { name: 'Volume' })).toHaveValue('60');
  await page.keyboard.press('Escape');
  await expect(popover).toHaveCount(0);
  await expect(room(page)).toBeVisible();
});

test('a press elsewhere closes the volume', async ({ page }) => {
  await enter(page);
  await page.getByRole('button', { name: 'Sound' }).click();
  await expect(page.getByRole('group', { name: 'Sound' })).toBeVisible();
  await room(page).click({ position: { x: 5, y: 5 } });
  await expect(page.getByRole('group', { name: 'Sound' })).toHaveCount(0);
});

test('mute and volume are kept across a reload', async ({ page }) => {
  await enter(page);
  await page.getByRole('button', { name: 'Sound' }).click();
  const group = page.getByRole('group', { name: 'Sound' });
  await group.getByRole('slider', { name: 'Volume' }).evaluate((el: HTMLInputElement) => {
    el.value = '20';
    el.dispatchEvent(new Event('change', { bubbles: true }));
  });
  await group.getByLabel('Mute').check({ force: true });
  await page.reload();
  await page.getByRole('button', { name: 'Sound' }).click();
  await expect(group.getByRole('slider', { name: 'Volume' })).toHaveValue('20');
  await expect(group.getByLabel('Mute')).toBeChecked();
});

test('the Scribe tick follows the mute', async ({ page }) => {
  await listen(page);
  await enter(page);
  const input = page.getByLabel('Scribe a sudden trial');
  await input.fill('Water the plants');
  await input.press('Enter');
  await expect.poll(() => sounds(page)).toEqual([TICK]);
  await page.getByRole('button', { name: 'Sound' }).click();
  await page.getByRole('group', { name: 'Sound' }).getByLabel('Mute').check({ force: true });
  await page.keyboard.press('Escape');
  await input.fill('Pay the bill');
  await input.press('Enter');
  await expect(page.getByRole('status').filter({ hasText: 'Inscribed' })).toBeVisible();
  expect(await sounds(page)).toEqual([TICK]);
});

test('Start on the Cycles dial knocks, and a reload rings nothing', async ({ page }) => {
  await listen(page);
  await enter(page);
  await room(page).getByRole('tab', { name: 'Harmonious Cycles' }).click();
  await expect(room(page).getByRole('slider')).toBeFocused();
  await page.keyboard.press('Enter');
  await page.keyboard.press('Enter');
  await page.keyboard.press('Enter');
  await expect(room(page)).toContainText('cycle 1 of 3');
  expect(await sounds(page)).toEqual([KNOCK]);
  await page.reload();
  await expect(room(page)).toContainText('cycle 1 of 3');
  expect(await sounds(page)).toEqual([]);
});

test('each end rings its own sound: bowl, then bell, then the final gong and a notice', async ({
  page,
}) => {
  await listen(page);
  const current = { patch: cycles('focus', 3) };
  await serve(page, current);
  await enter(page);
  await expect(room(page)).toContainText('cycle 1 of 1');
  current.patch = cycles('break', 3);
  await expect.poll(() => sounds(page), { timeout: 8000 }).toEqual([BOWL]);
  await expect(room(page)).toContainText('break');
  current.patch = cycles('waiting', 60);
  await expect.poll(() => sounds(page), { timeout: 8000 }).toEqual([BOWL, BELL]);
  expect(await notices(page)).toEqual([]);

  current.patch = cycles('focus', 3);
  await page.reload();
  await expect(room(page)).toContainText('focus');
  current.patch = cycles('done', 0);
  await expect.poll(() => sounds(page), { timeout: 8000 }).toEqual([FINAL]);
  const [notice] = await notices(page);
  expect(notice[0]).toBe('Harmonious Cycles');
  expect(notice[1]).toContain('Your cycles are complete');
});
