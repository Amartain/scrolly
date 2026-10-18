export const SCREEN_TWO_ID = 'screen-two';

/** Smooth between the two dashboard screens; instant under reduced motion. */
export function showScreen(which: 'one' | 'two'): void {
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const behavior: ScrollBehavior = reduced ? 'instant' : 'smooth';
  if (which === 'one') window.scrollTo({ top: 0, behavior });
  else document.getElementById(SCREEN_TWO_ID)?.scrollIntoView({ behavior, block: 'start' });
}

export function onScreenTwo(): boolean {
  return window.scrollY >= window.innerHeight / 2;
}
