import { json, send } from './api';
import type { components } from './api-types';

type ScrapText = components['schemas']['ScrapTextOut'];
export type ScrapPage = components['schemas']['ScrapPageOut'];

/** The Bamboo scrap of this visit to Seclusion. Python keeps it; this only reads and writes the text. */
export const scraps = {
  /** Every kept scrap, newest first, for the page that shows them. */
  pages: () => send<ScrapPage[]>('/api/scraps'),
  current: () => send<ScrapText>('/api/scraps/current'),
  write: (text: string) => send<ScrapText>('/api/scraps/current', json('PUT', { text })),
  /** For a page that is closing: `keepalive` lets the request finish after the page is gone. */
  writeOnExit: (text: string) => {
    void fetch('/api/scraps/current', { ...json('PUT', { text }), keepalive: true }).catch(
      () => {},
    );
  },
};
