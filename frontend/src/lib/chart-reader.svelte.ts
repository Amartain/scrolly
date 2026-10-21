/**
 * Which day of a chart is being read: set by the pointer, or moved with the arrow keys (Home and End
 * jump to the ends, Esc puts the tip away). Both dashboard charts read their days the same way.
 * `count` is how many days there are; `live` is false while the chart is only a shape under fog.
 */
export function useReader(count: () => number, live: () => boolean) {
  let shown = $state<number | null>(null);

  return {
    get shown() {
      return shown;
    },
    set shown(index: number | null) {
      shown = index;
    },
    clear: () => (shown = null),
    onkeydown(event: KeyboardEvent) {
      if (!live()) return;
      const last = count() - 1;
      const at = shown ?? last;
      const moves: Record<string, number> = {
        ArrowLeft: at - 1,
        ArrowRight: at + 1,
        Home: 0,
        End: last,
      };
      if (event.key === 'Escape') shown = null;
      else if (event.key in moves) shown = Math.min(last, Math.max(0, moves[event.key]));
      else return;
      event.preventDefault();
    },
    /** Tabbing in shows the latest day. A mouse click that focuses the chart does not. */
    onfocus(event: FocusEvent) {
      const keyboard = (event.currentTarget as HTMLElement).matches(':focus-visible');
      if (live() && shown === null && keyboard) shown = count() - 1;
    },
  };
}
