import { today, type View } from './api';
import { playGong } from './chime';
import {
  seclusion as api,
  type CyclesPlan,
  type Discipline,
  type EndedHow,
  type SeclusionState,
} from './seclusion-api';
import { view } from './view.svelte';

/** How the trial at hand ended, so the "What next?" card can say so and offer Undo. */
export interface Finished {
  how: EndedHow;
  id: string;
  title: string;
}

/** The focus room's latest state from the server, and the way every button reaches it. */
class SeclusionStore {
  state = $state<SeclusionState | null>(null);
  /** `performance.now()` when `state` arrived. The ring adds the time since then. */
  receivedAt = $state(0);
  /** Set when the trial at hand ends; the "What next?" card shows until the user chooses. */
  finished = $state<Finished | null>(null);

  private apply(next: SeclusionState) {
    this.state = next;
    this.receivedAt = performance.now();
  }

  /** Whether the open tab's clock is moving (the Incense timer, the cycle, the flow). */
  get running(): boolean {
    const room = this.state;
    if (!room) return false;
    if (room.discipline === 'cycles') return room.cycles?.running ?? false;
    if (room.discipline === 'flow') return room.flow?.running ?? false;
    return room.trial?.timer.running ?? false;
  }

  /** The Cycles dial is showing: Enter and Space belong to its buttons. */
  get settingUp(): boolean {
    return this.state?.discipline === 'cycles' && this.state.cycles?.phase === 'idle';
  }

  async load() {
    try {
      this.apply(await api.get());
    } catch {
      // Keep showing the last state; the next action tries again.
    }
  }

  /** Run a command of the focus room. A refusal becomes the notice. */
  async act(command: () => Promise<SeclusionState>): Promise<boolean> {
    try {
      this.apply(await command());
      view.notice = '';
      return true;
    } catch (error) {
      view.notice = error instanceof Error ? error.message : 'Something went wrong.';
      return false;
    }
  }

  /** Run a command of the dashboard's own API (conquer, abandon, ...), then read the room again. */
  async trial(command: () => Promise<View>): Promise<boolean> {
    const done = await view.act(command);
    if (done) await this.load();
    return done;
  }

  /** Conquer, abandon or postpone the trial at hand. The next one waits, idle. Nothing left: a gong. */
  async finish(how: EndedHow, trial: { id: string; title: string }): Promise<void> {
    if (!(await this.act(() => api.finish(how, trial.id)))) return;
    await view.refresh();
    this.finished = { how, id: trial.id, title: trial.title };
    if (this.state?.trial == null) playGong();
  }

  /** Take back a conquest. The trial returns as the one at hand. */
  async undo(): Promise<void> {
    const finished = this.finished;
    if (finished?.how !== 'conquered') return;
    if (!(await this.trial(() => today.revive(finished.id)))) return;
    if (this.state?.trial?.id !== finished.id) await this.trial(() => today.promote(finished.id));
    this.finished = null;
  }

  /** Choose the next trial from Remaining. */
  async switchTo(id: string): Promise<void> {
    if (await this.trial(() => today.promote(id))) this.finished = null;
  }

  dismiss = () => (this.finished = null);

  /** Another tab. What was running stops where it is, and its time stays on the trial. */
  chooseDiscipline = (discipline: Discipline) => {
    this.finished = null;
    return this.act(() => api.discipline(discipline));
  };

  enter = () => this.act(api.enter);
  leave = () => {
    this.finished = null;
    return this.act(api.leave);
  };
  start = () => {
    this.finished = null;
    return this.act(api.start);
  };
  /** Start the first focus of the Cycles with what the dial holds. */
  startCycles = (plan: CyclesPlan) => this.act(() => api.startCycles(plan));
  pause = () => this.act(api.pause);
  /** Space: pause what runs, start what waits. The Cycles dial has its own Start. */
  toggle = () => {
    const resting = this.state?.discipline === 'flow' && this.state.flow?.phase === 'break';
    if (this.settingUp || resting) return Promise.resolve(false);
    return this.running ? this.pause() : this.start();
  };
  takeBreak = () => this.act(api.takeBreak);
  endBreak = () => this.act(api.endBreak);
  setRatio = (work: number, rest: number) => this.act(() => api.setRatio(work, rest));
  newTimer = () => {
    this.finished = null;
    return this.act(api.newTimer);
  };
  zeroOut = () => this.act(api.zeroOut);
}

export const seclusion = new SeclusionStore();
