import {
  getView,
  importFile,
  putAppearance,
  putReadingFont,
  type DayVariant,
  type ImportResult,
  type Milestone,
  type Planning,
  type ReadingFont,
  type Theme,
  TitleRefused,
  type View,
} from './api';
import { refusalNote, type Segment } from './copy';

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
  /** `performance.now()` when `current` arrived. Only the ticking display reads it. */
  receivedAt = $state(0);

  get planning(): Planning | null {
    return this.current?.planning ?? null;
  }

  private apply(view: View) {
    const root = document.documentElement;
    root.dataset.theme = view.appearance.theme;
    root.dataset.phase = view.appearance.phase;
    root.dataset.readingFont = view.appearance.reading_font;
    if (view.appearance.day_variant) root.dataset.dayVariant = view.appearance.day_variant;
    else delete root.dataset.dayVariant;
    this.current = view;
    this.receivedAt = performance.now();
    // Only the response to the day's first seal carries a milestone; later views never clear it.
    if (view.milestone) this.milestone = view.milestone;
  }

  dismissMilestone() {
    this.milestone = null;
  }

  /** Keep typed planning text in the local view while its save is on the way. */
  rememberText(text: string) {
    if (this.current) this.current.planning.text = text;
  }

  async refresh() {
    try {
      this.apply(await getView());
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

  async chooseReadingFont(font: ReadingFont) {
    this.apply(await putReadingFont(font));
  }

  async restore(file: File): Promise<ImportResult> {
    const result = await importFile(file);
    this.apply(result.view);
    return result;
  }

  start() {
    void this.refresh();
    setInterval(() => void this.refresh(), REFRESH_MS);
    document.addEventListener('visibilitychange', () => {
      if (!document.hidden) void this.refresh();
    });
  }
}

export const view = new ViewStore();
