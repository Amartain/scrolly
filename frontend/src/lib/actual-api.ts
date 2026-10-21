import { json, send, type View } from './api';

/** Correct the time a conquered trial took ("45m"). Python reads and checks it. */
export const putTrialActual = (id: string, text: string) =>
  send<View>(`/api/trials/${id}/actual`, json('PUT', { text }));
