import { today, type Immediate } from './api';
import { view } from './view.svelte';

/** The Immediate Trial's buttons and the Space/Enter keys do the same thing through these. */
export const toggleTimer = (trial: Immediate) =>
  view.act(() => (trial.timer.running ? today.pauseTimer(trial.id) : today.startTimer(trial.id)));

export const conquer = (trial: Immediate) => view.act(() => today.conquer(trial.id));
