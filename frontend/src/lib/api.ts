import type { components } from './api-types';

export type View = components['schemas']['ViewOut'];
export type Planning = components['schemas']['PlanningOut'];
export type PlanTrial = components['schemas']['PlanTrialOut'];
export type Budget = components['schemas']['BudgetOut'];
export type Qi = components['schemas']['QiOut'];
export type QiFill = components['schemas']['QiFillOut'];
export type Dashboard = components['schemas']['DashboardOut'];
export type Immediate = components['schemas']['ImmediateOut'];
export type Timer = components['schemas']['TimerOut'];
export type Conquered = components['schemas']['ConqueredOut'];
export type HorizonItem = components['schemas']['HorizonItemOut'];
export type Art = components['schemas']['ArtOut'];
export type LetGo = components['schemas']['LetGoOut'];
export type ArtKind = components['schemas']['ArtOrderIn']['kind'];
export type Theme = components['schemas']['AppearanceIn']['theme'];
export type DayVariant = NonNullable<components['schemas']['AppearanceIn']['day_variant']>;
export type ReadingFont = components['schemas']['ReadingFontIn']['font'];
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

export const putReadingFont = (font: ReadingFont) =>
  send<View>('/api/reading-font', json('PUT', { font }));

export async function importFile(file: File): Promise<ImportResult> {
  const body = new FormData();
  body.append('file', file);
  return send<ImportResult>('/api/import', { method: 'POST', body });
}

export const goldenCore = {
  set: (enabled: boolean) => send<View>('/api/golden-core', json('PUT', { enabled })),
};

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
  update: (id: string, patch: { estimate?: string; is_mandate?: boolean; qi?: string }) =>
    plan(`trials/${id}`, json('PATCH', patch)),
  qiStart: (value: number) => plan('qi-start', json('PUT', { value })),
  unstage: (id: string) => plan(`trials/${id}/unstage`, json('POST')),
  dismiss: (id: string) => plan(`trials/${id}/dismiss`, json('POST')),
  reorder: (ids: string[]) => plan('order', json('PUT', { ids })),
};

const trial = (id: string, action: string) =>
  send<View>(`/api/trials/${id}/${action}`, json('POST'));

/** What the user does to the trials of a sealed day. Python decides what is allowed. */
export const today = {
  startTimer: (id: string) => trial(id, 'timer/start'),
  pauseTimer: (id: string) => trial(id, 'timer/pause'),
  resetTimer: (id: string) => trial(id, 'timer/reset'),
  conquer: (id: string) => trial(id, 'conquer'),
  postpone: (id: string) => trial(id, 'postpone'),
  abandon: (id: string) => trial(id, 'abandon'),
  revive: (id: string) => trial(id, 'revive'),
  promote: (id: string) => trial(id, 'promote'),
  update: (
    id: string,
    patch: {
      title?: string;
      is_mandate?: boolean;
      estimate?: string;
      qi?: string;
    },
  ) => send<View>(`/api/trials/${id}`, json('PATCH', patch)),
  scribe: (title: string, estimate: string, qi: string) =>
    send<View>('/api/trials', json('POST', { title, estimate, qi })),
  summon: (source: 'horizon' | 'art', id: string) =>
    send<View>('/api/trials/summon', json('POST', { source, id })),
  reorder: (ids: string[]) => send<View>('/api/trials/order', json('PUT', { ids })),
};

/** The user's backlog and the order of their Arts. */
export const horizon = {
  add: (title: string, estimate = '') =>
    send<View>('/api/horizon', json('POST', { title, estimate })),
  edit: (id: string, patch: { title?: string; estimate?: string; is_mandate?: boolean }) =>
    send<View>(`/api/horizon/${id}`, json('PATCH', patch)),
  discard: (id: string) => send<View>(`/api/horizon/${id}`, json('DELETE')),
  reorder: (ids: string[]) => send<View>('/api/horizon/order', json('PUT', { ids })),
  reorderArts: (kind: ArtKind, ids: string[]) =>
    send<View>('/api/arts/order', json('PUT', { kind, ids })),
};

/** Add, edit and delete Arts (their order is `horizon.reorderArts`). */
export const arts = {
  add: (kind: ArtKind, title: string, estimate: string) =>
    send<View>('/api/arts', json('POST', { kind, title, estimate })),
  edit: (id: string, patch: { title?: string; estimate?: string }) =>
    send<View>(`/api/arts/${id}`, json('PATCH', patch)),
  remove: (id: string) => send<View>(`/api/arts/${id}`, json('DELETE')),
};
