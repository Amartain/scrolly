import { today, type Immediate, type View } from './api';
import { playGong } from './chime';
import { SECLUSION } from './copy-seclusion';
import { askNotifyPermission, notify } from './notify';
import { qiAsk } from './qi-ask.svelte';
import { scrapPad } from './scrap-pad.svelte';
import { playSound, soundFor } from './seclusion-sounds';
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
    const working = room.trial?.timer.running ?? false;
    const cycles = room.cycles;
    // The cycle's own clock can run with no trial being worked (after a conquest): then Start is offered.
    if (cycles) return cycles.phase === 'break' ? cycles.running : cycles.running && working;
    if (room.flow) return room.flow.running;
    return working;
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

  /**
   * A countdown has reached zero here: read the room again and ring what the new phase calls for.
   * The end of the last cycle sends the desktop notice; so does the end of a break, but only when the
   * user is on another tab. Reading the room on its own never rings.
   */
  async settle() {
    const before = this.state;
    await this.load();
    const sound = soundFor(before, this.state);
    if (!sound) return;
    playSound(sound);
    if (sound === 'final')
      notify(SECLUSION.tabs.cycles, `${SECLUSION.cycles.done} ${SECLUSION.cycles.doneHint}`);
    if (sound === 'bell' && document.hidden) {
      const tab = this.state?.discipline === 'flow' ? SECLUSION.tabs.flow : SECLUSION.tabs.cycles;
      notify(tab, `${SECLUSION.breakOver} ${SECLUSION.breakOverHint}`);
    }
  }

  /** Run a command of the focus room. A refusal becomes the notice. */
  async act(command: () => Promise<SeclusionState>): Promise<boolean> {
    try {
      const before = this.state;
      const next = await command();
      this.apply(next);
      view.notice = '';
      // Only a focus the user began rings from here; the ends of a phase ring from `settle`.
      if (soundFor(before, next) === 'start') playSound('start');
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
  async finish(how: EndedHow, trial: Immediate): Promise<void> {
    if (!(await this.act(() => api.finish(how, trial.id)))) return;
    await view.refresh();
    this.finished = { how, id: trial.id, title: trial.title };
    // The last trial of a won day has its own sound (Tribulation Weathered), so no gong beside it.
    if (this.state?.trial == null && !view.current?.dashboard.victory?.due) playGong();
    if (how === 'conquered')
      qiAsk.ask({
        id: trial.id,
        title: trial.title,
        estimate: Number(trial.qi_text) || 0,
        undo: () => this.undo(),
      });
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
  leave = async () => {
    this.finished = null;
    await scrapPad.flush(); // what is written on the scrap is saved before the visit ends
    return this.act(api.leave);
  };
  start = async () => {
    this.finished = null;
    askNotifyPermission(); // Flow's break notice needs it too; a click is what lets the browser ask
    await this.ratios; // a ratio still on its way must land before the bank opens
    return this.act(api.start);
  };
  /** Start the first focus of the Cycles with what the dial holds. */
  startCycles = (plan: CyclesPlan) => {
    askNotifyPermission(); // a click is what lets the browser ask
    return this.act(() => api.startCycles(plan));
  };
  pause = () => this.act(api.pause);
  /** Space: pause what runs, start what waits. The Cycles dial has its own Start. */
  toggle = () => {
    const resting = this.state?.discipline === 'flow' && this.state.flow?.phase === 'break';
    if (this.settingUp || resting) return Promise.resolve(false);
    return this.running ? this.pause() : this.start();
  };
  takeBreak = () => {
    this.finished = null; // the break shows on the ring
    return this.act(api.takeBreak);
  };
  endBreak = () => this.act(api.endBreak);
  /** One change at a time, in the order made: the server could otherwise meet two of them reversed. */
  private ratios: Promise<unknown> = Promise.resolve();
  setRatio = (work: number, rest: number) => {
    const done = this.ratios.then(() => this.act(() => api.setRatio(work, rest)));
    this.ratios = done;
    return done;
  };
  /** From zero, at once. The screen has asked before any time is scrapped. */
  restart = () => {
    this.finished = null;
    return this.act(api.restart);
  };
  zeroOut = () => this.act(api.zeroOut);
  stop = () => this.act(api.stop);
  hideSidebar = (hidden: boolean) => this.act(() => api.hideSidebar(hidden));
}

export const seclusion = new SeclusionStore();
