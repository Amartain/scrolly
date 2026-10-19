import {
  getView,
  importFile,
  putAppearance,
  putReadingFont,
  type DayVariant,
  type ImportResult,
  type Planning,
  type ReadingFont,
  type Theme,
  type View,
} from './api';

const REFRESH_MS = 60_000;

/** The latest server view. Also the only place the theme attributes on <html> are set. */
class ViewStore {
  current = $state<View | null>(null);
  /** The server's last plain-language refusal (for example a bad estimate), or ''. */
  notice = $state('');
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
      this.notice = error instanceof Error ? error.message : 'Something went wrong.';
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
