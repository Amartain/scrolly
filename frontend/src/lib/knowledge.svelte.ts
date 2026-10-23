/**
 * Knowledge of the Dao, in the browser: tells Python a lesson was tried (once), shows a small "+1"
 * beside a find, and lets a hidden bar flash while it moves. What counts and what is next is
 * Python's (domain/knowledge.py); the words are in copy-knowledge.ts.
 *
 * Most lessons are learned by a click (or typing) on an element marked `data-tour="key"`
 * (TourHost listens); a shortcut that does the same calls `knowledge.learn` itself.
 */

import { json, send, type View } from './api';
import type { components } from './api-types';
import { KNOWLEDGE } from './copy-knowledge';
import { view } from './view.svelte';

type Known = components['schemas']['KnowledgeOut'];

export const knowledgeApi = {
  learn: (key: string) => send<Known>('/api/knowledge/learn', json('POST', { key })),
  pass: (key: string) => send<Known>('/api/knowledge/pass', json('POST', { key })),
  choose: (patch: { tour?: boolean; bar_hidden?: boolean }) =>
    send<View>('/api/knowledge', json('PUT', patch)),
  walkAgain: () => send<View>('/api/knowledge/walk-again', json('POST')),
  enlightened: () => send<View>('/api/knowledge/enlightened', json('POST')),
};

/** How long the "+1" of a find, and a hidden bar's flash, stay. */
const FLASH_MS = 2800;

class Knowledge {
  /** The find just learned and where it was (its centre, top and bottom), for its "+1". */
  found = $state<{ key: string; x: number; top: number; bottom: number } | null>(null);
  /** A hidden bar shows while this is true. */
  flashing = $state(false);
  private sent = new Set<string>();
  private timer: ReturnType<typeof setTimeout> | undefined;

  learned(key: string): boolean {
    return view.current?.knowledge.learned.includes(key) ?? false;
  }

  /** `key` was tried. `from` is the element, so a find's "+1" can stand beside it. */
  async learn(key: string, from?: Element | null) {
    if (!view.current || this.learned(key) || this.sent.has(key)) return;
    this.sent.add(key);
    const at = from?.getBoundingClientRect();
    const known = await knowledgeApi.learn(key).catch(() => null);
    if (!known) {
      this.sent.delete(key); // offline for a moment: the next try teaches it
      return;
    }
    this.merge(known);
    // A step has its card; only a find gets a "+1" where it was tried.
    if (key in KNOWLEDGE.finds && at)
      this.found = { key, x: at.left + at.width / 2, top: at.top, bottom: at.bottom };
    this.flash();
  }

  /** "Got it" on a step card. */
  async pass(key: string) {
    this.merge(await knowledgeApi.pass(key).catch(() => null));
  }

  /** Only the knowledge is replaced: the rest of the view is the other answers' to keep. */
  private merge(known: Known | null) {
    if (known && view.current) view.current = { ...view.current, knowledge: known };
  }

  private flash() {
    this.flashing = true;
    clearTimeout(this.timer);
    this.timer = setTimeout(() => {
      this.flashing = false;
      this.found = null;
    }, FLASH_MS);
  }
}

export const knowledge = new Knowledge();
