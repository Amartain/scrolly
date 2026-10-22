import { json, send, type View } from './api';
import type { components } from './api-types';

export type QiCard = components['schemas']['QiCardOut'];

/** Tell the server how much Qi a conquered trial took. Python checks the range. */
export const putTrialQi = (id: string, qi: number) =>
  send<View>(`/api/trials/${id}/qi`, json('PUT', { qi }));

/** The card's three choices, and where the day's Qi would land with `qi`. Saves nothing. */
export const getQiCard = (id: string, qi: number) =>
  send<QiCard>(`/api/trials/${id}/qi-card?qi=${qi}`);
