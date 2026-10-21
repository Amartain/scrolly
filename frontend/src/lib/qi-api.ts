import { json, send, type View } from './api';

/** Tell the server how much Qi a conquered trial took. Python checks the range. */
export const putTrialQi = (id: string, qi: number) =>
  send<View>(`/api/trials/${id}/qi`, json('PUT', { qi }));
