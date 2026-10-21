import { today, type Immediate } from './api';
import { qiAsk } from './qi-ask.svelte';
import { view } from './view.svelte';

/** The Immediate Trial's buttons and the Space/Enter keys do the same thing through these. */
export const toggleTimer = (trial: Immediate) =>
  view.act(() => (trial.timer.running ? today.pauseTimer(trial.id) : today.startTimer(trial.id)));

/** Take a conquest back: the trial returns as the Immediate Trial, as it was. */
async function revive(trial: Immediate) {
  if (!(await view.act(() => today.revive(trial.id)))) return;
  if (view.current?.dashboard.immediate?.id !== trial.id) {
    await view.act(() => today.promote(trial.id));
  }
}

/** Conquer it, then ask how much qi it took (the back arrow of that card revives it). */
export async function conquer(trial: Immediate): Promise<boolean> {
  if (!(await view.act(() => today.conquer(trial.id)))) return false;
  qiAsk.ask({
    id: trial.id,
    title: trial.title,
    estimate: Number(trial.qi_text) || 0,
    undo: () => revive(trial),
  });
  return true;
}
