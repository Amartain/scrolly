import { json, send, type View } from './api';

/** The time away counts: every timer carries on as if it had never stopped. */
export const keepGhost = () => send<View>('/api/ghost/keep', json('POST'));

/** Count only until the user left. */
export const cutGhost = () => send<View>('/api/ghost/cut', json('POST'));
