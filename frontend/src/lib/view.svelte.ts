import {
  getView,
  importFile,
  putAppearance,
  putReadingFont,
  purgeToday,
  putSunset,
  type DayVariant,
  type ImportResult,
  type Milestone,
  type Planning,
  type ReadingFont,
  type Theme,
  TitleRefused,
  type Victory,
  type View,
} from './api';
import { refusalNote, type Segment } from './copy';
import { putSound } from './sound-api';

const REFRESH_MS = 60_000;

/** The latest server view. Also the only place the theme attributes on <html> are set. */
class ViewStore {
  current = $state<View | null>(null);
  /** The last refusal (for example a bad estimate) as lines of text; empty when there is none. */
  noticeParts = $state<Segment[]>([]);

  /** The same refusal as plain text. Assigning plain text replaces it; '' clears it. */
  get notice(): string {
    return this.noticeParts.map((part) => part.text).join('');
  }

  set notice(text: string) {
    this.noticeParts = text ? [{ text }] : [];
  }
  /** The milestone to show after the first seal of the day, until it is closed. */
  milestone = $state<Milestone | null>(null);
  /** A finished-day ceremony asked for by a secret seal: shown once, it changes nothing. */
  preview = $state<Victory | null>(null);
  /** `performance.now()` when `current` arrived. Only the ticking display reads it. */
  receivedAt = $state(0);

  get planning(): Planning | null {
    return this.current?.planning ?? null;
  }

  /**
   * Show a view. `fade` is true only for the minute-by-minute refresh, so the palette fades when the
   * clock crosses into golden hour or dusk while the page is open. On load, on return to the tab and
   * after the user's own actions the new phase shows at once.
   */
  private apply(view: View, fade = false) {
    const root = document.documentElement;
    root.dataset.theme = view.appearance.theme;
    this.setPhase(view.appearance.phase, fade && this.current !== null);
    root.dataset.readingFont = view.appearance.reading_font;
    if (view.appearance.day_variant) root.dataset.dayVariant = view.appearance.day_variant;
    else delete root.dataset.dayVariant;
    this.current = view;
    this.receivedAt = performance.now();
    // Only the response to the day's first seal carries a milestone; later views never clear it.
    if (view.milestone) this.milestone = view.milestone;
  }

  /**
   * The whole screen crossfades to the new phase (art-direction › Motion), so the canvas, the panels
   * and the text change together. Without the browser's view transitions, or under reduced motion,
   * it switches at once.
   */
  private setPhase(phase: string, fade: boolean) {
    const root = document.documentElement;
    const change = () => {
      root.dataset.phase = phase;
    };
    const still = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (fade && root.dataset.phase !== phase && !still && document.startViewTransition)
      document.startViewTransition(change);
    else change();
  }

  dismissMilestone() {
    this.milestone = null;
  }

  /** Keep typed planning text in the local view while its save is on the way. */
  rememberText(text: string) {
    if (this.current) this.current.planning.text = text;
  }

  async refresh(fade = false) {
    try {
      this.apply(await getView(), fade);
    } catch {
      // Keep showing the last view; the next refresh tries again.
    }
  }

  /** Run a command that returns the new view. A refusal becomes `notice`. */
  async act(command: () => Promise<View>): Promise<boolean> {
    try {
      this.apply(await command());
      this.notice = '';
      return true;
    } catch (error) {
      if (error instanceof TitleRefused) this.noticeParts = refusalNote(error.refusal);
      else this.notice = error instanceof Error ? error.message : 'Something went wrong.';
      return false;
    }
  }

  async choose(theme: Theme, dayVariant: DayVariant | null) {
    this.apply(await putAppearance(theme, dayVariant));
  }

  /** Answer the sunset invitation, or change the hour, the on/off choice or the chime. */
  setSunset(patch: { enabled?: boolean; at?: string; chime?: boolean }): Promise<boolean> {
    return this.act(() => putSunset(patch));
  }

  /** The one volume (0-100) and the one mute of every sound. Only what is given changes. */
  setSound(patch: { volume?: number; muted?: boolean }): Promise<boolean> {
    // One at a time, in the order made: the server merges each change into what it holds.
    const done = this.sounds.then(() => this.act(() => putSound(patch)));
    this.sounds = done;
    return done;
  }

  private sounds: Promise<unknown> = Promise.resolve();

  async chooseReadingFont(font: ReadingFont) {
    this.apply(await putReadingFont(font));
  }

  /** Show a view that arrived some other way (the answer to a secret seal). */
  show(view: View) {
    this.apply(view);
  }

  /** Purge Today's Scroll: today's open trials and the planning in progress. */
  purge(): Promise<boolean> {
    return this.act(purgeToday);
  }

  async restore(file: File): Promise<ImportResult> {
    const result = await importFile(file);
    this.apply(result.view);
    return result;
  }

  start() {
    void this.refresh();
    setInterval(() => void this.refresh(true), REFRESH_MS);
    document.addEventListener('visibilitychange', () => {
      if (!document.hidden) void this.refresh();
    });
  }
}

export const view = new ViewStore();
