import { json, send } from './api';
import type { components } from './api-types';

export type SeclusionState = components['schemas']['SeclusionOut'];

const post = (path: string) => send<SeclusionState>(`/api/seclusion/${path}`, json('POST'));

/** The focus room. Python decides what the ring says; conquer, postpone and abandon are `today`'s. */
export const seclusion = {
  get: () => send<SeclusionState>('/api/seclusion'),
  enter: () => post('enter'),
  leave: () => post('leave'),
  start: () => post('timer/start'),
  pause: () => post('timer/pause'),
  newTimer: () => post('timer/new'),
  zeroOut: () => post('timer/zero'),
};
