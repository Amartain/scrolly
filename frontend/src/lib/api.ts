import type { components } from './api-types';

export type View = components['schemas']['ViewOut'];
export type Theme = components['schemas']['AppearanceIn']['theme'];
export type DayVariant = NonNullable<components['schemas']['AppearanceIn']['day_variant']>;

async function send<T>(path: string, init?: RequestInit): Promise<T> {
  const reply = await fetch(path, init);
  if (!reply.ok) throw new Error(`${path}: ${reply.status}`);
  return (await reply.json()) as T;
}

export const getView = () => send<View>('/api/view');

export const putAppearance = (theme: Theme, dayVariant: DayVariant | null) =>
  send<View>('/api/appearance', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ theme, day_variant: dayVariant }),
  });
