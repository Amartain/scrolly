import { today, type Immediate } from './api';
import { parallelApi, type ParallelEnd, type PickSource } from './parallel-api';
import { qiAsk } from './qi-ask.svelte';
import { seclusion } from './seclusion.svelte';
import { view } from './view.svelte';

/** What the user does to the trial run beside the one at hand. Each answer is the room's new state. */
export const parallel = {
  pick: (source: PickSource, ref: string) => seclusion.act(() => parallelApi.pick(source, ref)),
  start: () => seclusion.act(parallelApi.start),
  pause: () => seclusion.act(parallelApi.pause),

  /** Mandate and Mortal switch by the mark, as on the dashboard. */
  toggleMandate: (trial: Immediate) =>
    seclusion.trial(() => today.update(trial.id, { is_mandate: !trial.is_mandate })),

  /** End it on its own; a conquest asks how much qi it took, and taking that back runs it again. */
  async finish(how: ParallelEnd, trial: Immediate): Promise<void> {
    if (!(await seclusion.act(() => parallelApi.finish(how)))) return;
    await view.refresh();
    if (how !== 'conquered') return;
    qiAsk.ask({
      id: trial.id,
      title: trial.title,
      estimate: Number(trial.qi_text) || 0,
      undo: async () => {
        if (await seclusion.trial(() => today.revive(trial.id)))
          await parallel.pick('remaining', trial.id);
      },
    });
  },
};
