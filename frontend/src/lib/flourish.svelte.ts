/**
 * The short flourishes of a trial begun and a trial conquered: what plays, and where on the screen.
 * They are drawn by components/Flourish.svelte in a layer over the layout that moves nothing and
 * blocks nothing (art-direction › Motion). Under reduced motion only the colour flash and the sound
 * remain. Which moment it is comes from the view; nothing here decides a rule.
 */
import { tick } from 'svelte';
import { playConquest, playIgnite, playResumeTick } from './chime-ceremony';

export type Effect =
  | { kind: 'ignite' | 'seal'; id: number; x: string; y: string }
  | { kind: 'comet'; id: number; x: string; y: string; dx: string; dy: string };

const LIFE_MS = 1200;
const GLOW_MS = 800;

const px = (n: number) => `${Math.round(n)}px`;
const still = () => window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const token = (name: string) => getComputedStyle(document.documentElement).getPropertyValue(name);

function centre(box: DOMRect): [number, number] {
  return [box.left + box.width / 2, box.top + box.height / 2];
}

/** A one-off colour flash on an element, back to its own colour. Nothing moves. */
function flash(
  element: Element | null | undefined,
  property: 'color' | 'backgroundColor',
  colour = '--scene-gold',
) {
  element?.animate([{ [property]: token(colour) }, {}], { duration: GLOW_MS, easing: 'ease-out' });
}

class Flourish {
  effects = $state<Effect[]>([]);
  private next = 0;

  /** Under reduced motion nothing waits for a flourish. */
  reduced = still;

  private add(effect: Effect) {
    this.effects.push(effect);
    setTimeout(() => (this.effects = this.effects.filter((e) => e.id !== effect.id)), LIFE_MS);
  }

  /**
   * A trial begins. From a clock at zero the incense is lit: a gold ring and sparks at the button,
   * the clock flashes gold, a match and a bowl sound. Going on after a pause is only a soft tick.
   */
  begin(button: Element | null, clock: Element | null, fresh: boolean) {
    if (!fresh) {
      playResumeTick();
      return;
    }
    playIgnite();
    flash(clock, 'color', '--scene-bolt'); // the clock is gold already: it flares pale
    if (still() || !button) return;
    const [x, y] = centre(button.getBoundingClientRect());
    this.add({ kind: 'ignite', id: this.next++, x: px(x), y: px(y) });
  }

  /**
   * A trial conquered, not the day's last (that one has the ceremony). `from` is where the trial
   * was (the Immediate card, or Seclusion's ring), measured before it changed; `count` is how many
   * trials are conquered today, which sets the chime's step. A seal stamps where the trial was, a
   * spark flies to its new row in Conquered Today, the row and Lifetime Conquered glow.
   */
  async conquer(from: DOMRect | null, count: number) {
    playConquest(count);
    await tick();
    const row = document.querySelector('section[aria-label^="Conquered Today"] li:last-of-type');
    flash(row, 'backgroundColor');
    flash(document.querySelector('section[aria-label="Lifetime Conquered"] .figure'), 'color');
    if (still() || !from) return;
    const [x, y] = centre(from);
    this.add({ kind: 'seal', id: this.next++, x: px(x), y: px(y) });
    if (!row) return;
    const [tx, ty] = centre(row.getBoundingClientRect());
    this.add({
      kind: 'comet',
      id: this.next++,
      x: px(x),
      y: px(y),
      dx: px(tx - x),
      dy: px(ty - y),
    });
  }
}

export const flourish = new Flourish();
