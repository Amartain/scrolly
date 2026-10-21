import { json, send } from './api';
import type { components } from './api-types';
import type { SeclusionState } from './seclusion-api';

export type Candidate = components['schemas']['CandidateOut'];
export type PickSource = components['schemas']['ParallelPickIn']['source'];
export type ParallelEnd = components['schemas']['ParallelFinishIn']['how'];

const post = (path: string, body?: unknown) =>
  send<SeclusionState>(`/api/seclusion/parallel${path}`, json('POST', body));

/** The trial run beside the one at hand. Python decides what can and cannot run beside. */
export const parallelApi = {
  search: (q: string) =>
    send<Candidate[]>(`/api/seclusion/parallel/search?q=${encodeURIComponent(q)}`),
  pick: (source: PickSource, ref: string) => post('', { source, ref }),
  start: () => post('/start'),
  pause: () => post('/pause'),
  finish: (how: ParallelEnd) => post('/finish', { how }),
};
