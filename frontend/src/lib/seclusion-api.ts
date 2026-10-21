import { json, send } from './api';
import type { components } from './api-types';

export type SeclusionState = components['schemas']['SeclusionOut'];
export type Discipline = SeclusionState['discipline'];
export type CyclesPlan = components['schemas']['CyclesPlanIn'];
export type EndedHow = components['schemas']['FinishIn']['how'];

const post = (path: string, body?: unknown) =>
  send<SeclusionState>(`/api/seclusion/${path}`, json('POST', body));

/** The focus room. Python decides what the ring says and which rules hold. */
export const seclusion = {
  get: () => send<SeclusionState>('/api/seclusion'),
  enter: () => post('enter'),
  leave: () => post('leave'),
  start: () => post('timer/start'),
  startCycles: (plan: CyclesPlan) => post('timer/start', plan),
  pause: () => post('timer/pause'),
  newTimer: () => post('timer/new'),
  zeroOut: () => post('timer/zero'),
  discipline: (discipline: Discipline) => post('discipline', { discipline }),
  takeBreak: () => post('break/start'),
  endBreak: () => post('break/end'),
  finish: (how: EndedHow, trialId: string) => post('finish', { how, trial_id: trialId }),
  setRatio: (work: number, rest: number) =>
    send<SeclusionState>('/api/seclusion/flow/ratio', json('PUT', { work, rest })),
  /** Fold Bamboo Scraps away, or unfold it. The server keeps the choice. */
  hideScraps: (hidden: boolean) =>
    send<SeclusionState>('/api/seclusion/scraps-hidden', json('PUT', { hidden })),
};
