import { scraps } from './scraps-api';

const PAUSE_MS = 800;

/** The Bamboo scrap of this visit: what is typed saves itself after a pause, and before leaving. */
class ScrapPad {
  text = $state('');
  /** Whether the server holds what is on the page. */
  saved = $state(true);
  private held = '';
  private timer: ReturnType<typeof setTimeout> | undefined;
  /** One save at a time, in order, so a slow one cannot land after a newer one. */
  private saving: Promise<unknown> = Promise.resolve();

  async load() {
    try {
      this.held = (await scraps.current()).text;
    } catch {
      // Keep what is on the page; the next save tries again.
    }
    this.text = this.held;
    this.saved = true;
  }

  type = (text: string) => {
    this.text = text;
    this.saved = false;
    clearTimeout(this.timer);
    this.timer = setTimeout(() => void this.flush(), PAUSE_MS);
  };

  /** Save now: on a pause in typing, on blur, and before Seclusion is left. */
  flush = () => {
    clearTimeout(this.timer);
    this.saving = this.saving.then(() => this.send());
    return this.saving;
  };

  private async send() {
    const sending = this.text;
    if (sending === this.held) {
      this.saved = true;
      return;
    }
    try {
      await scraps.write(sending);
      this.held = sending;
      this.saved = this.text === sending;
    } catch {
      this.saved = false;
    }
  }

  /** The page is closing: send what is left in a request that outlives it. */
  unload = () => {
    if (this.text !== this.held) scraps.writeOnExit(this.text);
  };
}

export const scrapPad = new ScrapPad();
