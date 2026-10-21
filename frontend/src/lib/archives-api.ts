import { send } from './api';
import type { components } from './api-types';

export type ArchivePage = components['schemas']['ArchivePageOut'];
export type ArchiveCard = components['schemas']['ArchiveCardOut'];
export type ArchiveRow = components['schemas']['ArchiveRowOut'];

/** The Grand Archives: fourteen past days at a time. Python groups and words them; this only asks. */
export const archives = {
  page: (before?: string | null) =>
    send<ArchivePage>(before ? `/api/archives?before=${before}` : '/api/archives'),
};
