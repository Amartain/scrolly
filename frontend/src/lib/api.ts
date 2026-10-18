import type { components } from './api-types';

export type View = components['schemas']['ViewOut'];
export type Planning = components['schemas']['PlanningOut'];
export type PlanTrial = components['schemas']['PlanTrialOut'];
export type HorizonItem = components['schemas']['HorizonItemOut'];
export type Art = components['schemas']['ArtOut'];
export type Theme = components['schemas']['AppearanceIn']['theme'];
export type DayVariant = NonNullable<components['schemas']['AppearanceIn']['day_variant']>;
export type ImportResult = components['schemas']['ImportOut'];

/** The server's own plain-language reason, ready to show. */
async function failure(reply: Response, path: string): Promise<Error> {
  const problem = (await reply.json().catch(() => null)) as { detail?: unknown } | null;
  const detail = typeof problem?.detail === 'string' ? problem.detail : null;
  return new Error(detail ?? `${path}: ${reply.status}`);
}

async function send<T>(path: string, init?: RequestInit): Promise<T> {
  const reply = await fetch(path, init);
  if (!reply.ok) throw await failure(reply, path);
  return (await reply.json()) as T;
}

const json = (method: string, body?: unknown): RequestInit => ({
  method,
  headers: { 'Content-Type': 'application/json' },
  body: body === undefined ? undefined : JSON.stringify(body),
});

export const getView = () => send<View>('/api/view');

export const putAppearance = (theme: Theme, dayVariant: DayVariant | null) =>
  send<View>('/api/appearance', json('PUT', { theme, day_variant: dayVariant }));

export async function importFile(file: File): Promise<ImportResult> {
  const body = new FormData();
  body.append('file', file);
  return send<ImportResult>('/api/import', { method: 'POST', body });
}

const plan = (path: string, init: RequestInit) => send<View>(`/api/planning/${path}`, init);

export const planning = {
  start: () => plan('start', json('POST')),
  saveText: (text: string) => plan('text', json('PUT', { text })),
  proceed: () => plan('proceed', json('POST')),
  back: () => plan('back', json('POST')),
  abandon: () => plan('abandon', json('POST')),
  seal: () => plan('seal', json('POST')),
  summon: (source: 'horizon' | 'art', id: string) => plan('summon', json('POST', { source, id })),
  add: (title: string) => plan('trials', json('POST', { title })),
  update: (id: string, patch: { estimate?: string; is_mandate?: boolean }) =>
    plan(`trials/${id}`, json('PATCH', patch)),
  unstage: (id: string) => plan(`trials/${id}/unstage`, json('POST')),
  dismiss: (id: string) => plan(`trials/${id}/dismiss`, json('POST')),
  reorder: (ids: string[]) => plan('order', json('PUT', { ids })),
};
