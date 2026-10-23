/** The player of the Solo Leveling easter egg (domain/player.py): accepting, and the aura. */

import { json, send, type View } from './api';
import type { components } from './api-types';

export type AuraColour = components['schemas']['AuraColour'];

export const playerApi = {
  accept: () => send<View>('/api/player/accept', json('POST')),
  aura: (robe: AuraColour | null, glow: AuraColour | null, glow_on: boolean) =>
    send<View>('/api/player/aura', json('PUT', { robe, glow, glow_on })),
};

/** The token that paints a colour (styles/tokens/base.css › --aura-*). */
export const auraToken = (colour: AuraColour) => `var(--aura-${colour})`;
