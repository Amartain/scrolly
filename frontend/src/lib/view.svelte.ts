import { getView, putAppearance, type DayVariant, type Theme, type View } from './api';

const REFRESH_MS = 60_000;

/** The latest server view. Also the only place the theme attributes on <html> are set. */
class ViewStore {
  current = $state<View | null>(null);

  private apply(view: View) {
    const root = document.documentElement;
    root.dataset.theme = view.appearance.theme;
    root.dataset.phase = view.appearance.phase;
    if (view.appearance.day_variant) root.dataset.dayVariant = view.appearance.day_variant;
    else delete root.dataset.dayVariant;
    this.current = view;
  }

  async refresh() {
    try {
      this.apply(await getView());
    } catch {
      // Keep showing the last view; the next refresh tries again.
    }
  }

  async choose(theme: Theme, dayVariant: DayVariant | null) {
    this.apply(await putAppearance(theme, dayVariant));
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
