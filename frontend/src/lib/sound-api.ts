import { json, send, type View } from './api';

/** The one volume (0-100) and the one mute of every sound. Only what is given changes. */
export const putSound = (patch: { volume?: number; muted?: boolean }) =>
  send<View>('/api/sound', json('PUT', patch));
