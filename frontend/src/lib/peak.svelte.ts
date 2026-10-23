/**
 * The cultivator on the peak, behind Seclusion and in the dashboard header (owner, 2026-10-23). Only how
 * the scene looks: whether they are up there is Python's (`on_peak`, domain/cultivator.py). When that
 * turns true they climb the path while a timer runs (the climb halts with it); when it turns false they
 * walk down. On load they are simply where they belong.
 */

export type Stage = 'foot' | 'climbing' | 'seated' | 'descending';
export type Frame = 'room' | 'header';

/** How long the climb takes while the timer runs (owner: "10-20 s"), and the walk down. */
const CLIMB_MS = 15_000;
const DESCEND_MS = 10_000;

const reduced = () => window.matchMedia('(prefers-reduced-motion: reduce)').matches;

class Peak {
  stage = $state<Stage>('foot');
  /** How far up the path, 0 to 1. */
  progress = $state(0);
  /** A timer runs: the climb goes on (set by the app from the room or the dashboard). */
  running = $state(false);
  /** The scene is being painted in: the room's cards wait for it. Any key or click ends it. */
  painting = $state(false);
  /** The same, painted upward from the header's window: the way up by ↑ (lib/travel.ts). */
  rising = $state(false);
  private placed = false;

  /** Python says whether they are up. The first word places them; later ones send them on the path. */
  sync(up: boolean) {
    if (!this.placed || reduced()) {
      this.placed = true;
      this.place(up);
    } else if (up && (this.stage === 'foot' || this.stage === 'descending')) {
      this.stage = 'climbing';
    } else if (!up && (this.stage === 'seated' || this.stage === 'climbing')) {
      this.stage = 'descending';
    }
  }

  /** The cultivator moved on the path for `ms`. */
  advance(ms: number) {
    if (this.stage === 'climbing') {
      this.progress = Math.min(1, this.progress + ms / CLIMB_MS);
      if (this.progress >= 1) this.place(true);
    } else if (this.stage === 'descending') {
      this.progress = Math.max(0, this.progress - ms / DESCEND_MS);
      if (this.progress <= 0) this.place(false);
    }
  }

  /**
   * A visit to the room begins: painted in (`paint`, as on a reload), painted upward (`rise`), or
   * shown as it is (`open`, a quick way back up). Nothing is painted while the cultivator is on the
   * way or up there.
   */
  arrive(how: 'paint' | 'rise' | 'open') {
    const shown = how === 'open' || this.stage !== 'foot' || reduced();
    this.painting = !shown && how === 'paint';
    this.rising = !shown && how === 'rise';
  }

  /** Another theme: its scene is painted in. */
  repaint() {
    this.painting = !reduced();
    this.rising = false;
  }

  /** The scene is still coming in: the room's cards wait for it. */
  get arriving() {
    return this.painting || this.rising;
  }

  skip = () => {
    this.painting = false;
    this.rising = false;
  };

  private place(up: boolean) {
    this.stage = up ? 'seated' : 'foot';
    this.progress = up ? 1 : 0;
  }
}

export const peak = new Peak();

/**
 * The part of the painting shown. The room shows it all. The header is a window that follows the
 * cultivator: the foot of the path while they wait, the summit while they meditate. It reaches left of
 * the painting's edge (each scene paints on past it) so the cliff sits clear of the title plate.
 */
export function viewBoxFor(frame: Frame, feetY: number | undefined): string {
  if (frame === 'room') return '0 0 1600 900';
  const top = Math.min(660, Math.max(0, (feetY ?? 900) - 170));
  return `-560 ${top} 1920 240`;
}
