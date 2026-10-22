import { json, send, type View } from './api';
import type { components } from './api-types';

export type PanelStyle = components['schemas']['PanelStyle'];

/** How the panels' header bands are drawn: a lacquer plaque, or a scroll's rod. */
export const putPanelStyle = (style: PanelStyle) =>
  send<View>('/api/panel-style', json('PUT', { style }));
