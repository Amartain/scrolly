/** Which sound a change in the focus room calls for. */
import { playBell, playBowl, playFinalGong } from './chime';
import type { SeclusionState } from './seclusion-api';

export type Sound = 'start' | 'bowl' | 'bell' | 'final';

const PLAYERS: Record<Sound, () => void> = {
  start: playBell,
  bowl: playBowl,
  bell: playBell,
  final: playFinalGong,
};

export const playSound = (sound: Sound) => PLAYERS[sound]();

/**
 * What changed between two states of the room. A focus beginning is the bell; a focus ending is a
 * bowl; a break ending is a bell; the last cycle ending is the final gong. Nothing else rings.
 */
export function soundFor(
  before: SeclusionState | null,
  after: SeclusionState | null,
): Sound | null {
  if (!before || !after) return null;
  if (before.cycles && after.cycles) {
    const [was, now] = [before.cycles.phase, after.cycles.phase];
    if (now === 'done' && was !== 'done') return 'final';
    if (was === 'focus' && now === 'break') return 'bowl';
    if (was === 'break' && now === 'waiting') return 'bell';
    if ((was === 'idle' || was === 'waiting') && now === 'focus') return 'start';
  }
  if (before.flow?.phase === 'break' && after.flow?.phase === 'focus') return 'bell';
  return null;
}
