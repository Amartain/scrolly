/**
 * The cultivator on the peak behind Seclusion (owner, 2026-10-23). Only how the scene looks, no rule:
 * the cultivator waits at the foot of the path until the first Start of a visit, climbs while the timer
 * runs (the climb halts with it), then sits and meditates for the rest of the visit. Coming back while a
 * run goes on finds them seated, with no painting.
 */

export type Stage = 'foot' | 'climbing' | 'seated';

/** How long the climb takes while the timer runs (owner: "10-20 s"). */
const CLIMB_MS = 15_000;

const reduced = () => window.matchMedia('(prefers-reduced-motion: reduce)').matches;

class Peak {
  stage = $state<Stage>('foot');
  /** How far up the path, 0 to 1. */
  progress = $state(0);
  /** The scene is being painted in: the room's cards wait for it. Any key or click ends it. */
  painting = $state(false);

  /** A visit begins. With a run already going the cultivator is seated and nothing is painted. */
  arrive(live: boolean) {
    this.stage = live ? 'seated' : 'foot';
    this.progress = live ? 1 : 0;
    this.painting = !live && !reduced();
  }

  /** The timer started: the climb begins (at once seated when motion is reduced). */
  begin() {
    if (this.stage !== 'foot') return;
    if (reduced()) this.sit();
    else this.stage = 'climbing';
  }

  /** The timer ran on for `ms` while climbing. */
  advance(ms: number) {
    if (this.stage !== 'climbing') return;
    this.progress = Math.min(1, this.progress + ms / CLIMB_MS);
    if (this.progress >= 1) this.sit();
  }

  /** Another theme: its scene is painted in. */
  repaint() {
    this.painting = !reduced();
  }

  skip = () => {
    this.painting = false;
  };

  private sit() {
    this.stage = 'seated';
    this.progress = 1;
  }
}

export const peak = new Peak();
