import type { View } from './api';
import { seclusion as api, type SeclusionState } from './seclusion-api';
import { view } from './view.svelte';

/** The focus room's latest state from the server, and the way every button reaches it. */
class SeclusionStore {
  state = $state<SeclusionState | null>(null);
  /** `performance.now()` when `state` arrived. The ring adds the time since then. */
  receivedAt = $state(0);

  private apply(next: SeclusionState) {
    this.state = next;
    this.receivedAt = performance.now();
  }

  async load() {
    try {
      this.apply(await api.get());
    } catch {
      // Keep showing the last state; the next action tries again.
    }
  }

  /** Run a command of the focus room. A refusal becomes the notice. */
  async act(command: () => Promise<SeclusionState>): Promise<boolean> {
    try {
      this.apply(await command());
      view.notice = '';
      return true;
    } catch (error) {
      view.notice = error instanceof Error ? error.message : 'Something went wrong.';
      return false;
    }
  }

  /** Run a command of the dashboard's own API (conquer, abandon, ...), then read the room again. */
  async trial(command: () => Promise<View>): Promise<boolean> {
    const done = await view.act(command);
    if (done) await this.load();
    return done;
  }

  enter = () => this.act(api.enter);
  leave = () => this.act(api.leave);
  start = () => this.act(api.start);
  pause = () => this.act(api.pause);
  newTimer = () => this.act(api.newTimer);
  zeroOut = () => this.act(api.zeroOut);
}

export const seclusion = new SeclusionStore();
