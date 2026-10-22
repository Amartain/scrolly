import { today, type Immediate } from './api';
import { flourish } from './flourish.svelte';
import { qiAsk } from './qi-ask.svelte';
import { seclusion } from './seclusion.svelte';
import { view } from './view.svelte';

const CARD = 'section[aria-label="The Immediate Trial"]';
/** The Qi card waits this long after a conquest, so the flourish is seen first. */
const QI_WAIT_MS = 800;

/** The Immediate Trial's buttons and the Space/Enter keys do the same thing through these. */
export async function toggleTimer(trial: Immediate): Promise<boolean> {
  // A run of the room goes on after stepping out: pause and resume reach that run, not the trial alone.
  if (seclusion.state?.run_under_way) {
    const done = await seclusion.toggle();
    if (done) await view.refresh();
    return done;
  }
  if (trial.timer.running) return view.act(() => today.pauseTimer(trial.id));
  const button = document.querySelector(`${CARD} [aria-label="Start timer"]`);
  const done = await view.act(() => today.startTimer(trial.id));
  if (done)
    flourish.begin(button, document.querySelector(`${CARD} .clock`), trial.timer.elapsed_s === 0);
  return done;
}

/** Take a conquest back: the trial returns as the Immediate Trial, as it was. */
async function revive(trial: Immediate) {
  if (!(await view.act(() => today.revive(trial.id)))) return;
  if (view.current?.dashboard.immediate?.id !== trial.id) {
    await view.act(() => today.promote(trial.id));
  }
}

/** Conquer it, then ask how much qi it took (the back arrow of that card revives it). */
export async function conquer(trial: Immediate): Promise<boolean> {
  const card = document.querySelector(CARD)?.getBoundingClientRect() ?? null;
  if (!(await view.act(() => today.conquer(trial.id)))) return false;
  const dashboard = view.current?.dashboard;
  // The day's last conquest has the ceremony instead, which waits for the Qi card itself.
  const won = !!dashboard?.victory?.due;
  if (!won) void flourish.conquer(card, dashboard?.conquered.length ?? 1);
  const ask = () =>
    qiAsk.ask({
      id: trial.id,
      title: trial.title,
      estimate: Number(trial.qi_text) || 0,
      restores: trial.type === 'restorative',
      undo: () => revive(trial),
    });
  if (won || flourish.reduced()) ask();
  else setTimeout(ask, QI_WAIT_MS);
  return true;
}
