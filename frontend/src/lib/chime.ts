/**
 * Every sound of the app, made with Web Audio (no audio files). The volume and the mute are the
 * user's: Seclusion's sounds follow both, the sunset chime follows the volume only (Settings has
 * its own on/off and a Test button, which must be heard).
 */
import { view } from './view.svelte';

type Tones = [hz: number, level: number][];

/** One struck sound: tones that start together `at` seconds in and fade over `seconds`. */
interface Strike {
  at: number;
  tones: Tones;
  seconds: number;
  shape?: OscillatorType;
  attack?: number;
  /** Starts this many times higher and falls to the pitch: the "tok" of a wooden fish. */
  drop?: number;
}

/** Level 60 is the loudness the sounds were first made at, so the default changes nothing. */
const DEFAULT_VOLUME = 60;

function loudness(followsMute: boolean): number {
  const sound = view.current?.sound;
  if (!sound) return 1;
  return followsMute && sound.muted ? 0 : sound.volume / DEFAULT_VOLUME;
}

function play(strikes: Strike[], followsMute = true): void {
  const Context = window.AudioContext;
  const factor = loudness(followsMute);
  if (!Context || factor <= 0) return;
  const audio = new Context();
  void audio.resume();
  const origin = audio.currentTime;
  let end = 0;
  for (const strike of strikes) {
    const start = origin + strike.at;
    for (const [hz, level] of strike.tones) {
      const tone = audio.createOscillator();
      const gain = audio.createGain();
      tone.type = strike.shape ?? 'sine';
      if (strike.drop) {
        tone.frequency.setValueAtTime(hz * strike.drop, start);
        tone.frequency.exponentialRampToValueAtTime(hz, start + 0.06);
      } else {
        tone.frequency.value = hz;
      }
      gain.gain.setValueAtTime(0.0001, start);
      gain.gain.linearRampToValueAtTime(level * factor, start + (strike.attack ?? 0.05));
      gain.gain.exponentialRampToValueAtTime(0.0001, start + strike.seconds);
      tone.connect(gain).connect(audio.destination);
      tone.start(start);
      tone.stop(start + strike.seconds + 0.1);
    }
    end = Math.max(end, strike.at + strike.seconds);
  }
  setTimeout(() => void audio.close(), (end + 1) * 1000);
}

/** The sunset chime: 216 Hz and 432 Hz sine tones with a six second exponential decay. */
export const playChime = () =>
  play(
    [
      {
        at: 0,
        seconds: 6,
        tones: [
          [216, 0.18],
          [432, 0.09],
        ],
      },
    ],
    false,
  );

/** Seclusion's gong: a low bell with inharmonic partials, softer and shorter than the chime. */
export const playGong = () =>
  play([
    {
      at: 0,
      seconds: 4,
      tones: [
        [110, 0.2],
        [220, 0.1],
        [304, 0.06],
        [594, 0.03],
      ],
    },
  ]);

/** A soft tick that says a sudden trial was written down. */
export const playTick = () => play([{ at: 0, seconds: 0.25, tones: [[880, 0.05]] }]);

/** Harmonious Cycles, focus begins: two short, dry knocks of a wooden fish. */
export const playKnock = () => {
  const knock = { seconds: 0.18, attack: 0.005, shape: 'triangle', drop: 1.5 } as const;
  play([
    { ...knock, at: 0, tones: [[660, 0.22]] },
    { ...knock, at: 0.26, tones: [[660, 0.22]] },
  ]);
};

/** Focus ends: a long singing bowl, warm and slowly fading. The two close low tones beat. */
export const playBowl = () =>
  play([
    {
      at: 0,
      seconds: 8,
      attack: 0.08,
      tones: [
        [196, 0.2],
        [197.6, 0.15],
        [528, 0.06],
        [1070, 0.025],
      ],
    },
  ]);

/** The rest is over: a small, high bell, short, calling gently back. */
export const playBell = () =>
  play([
    {
      at: 0,
      seconds: 1.8,
      attack: 0.004,
      tones: [
        [1319, 0.09],
        [3320, 0.04],
        [4180, 0.02],
      ],
    },
  ]);

/** Every cycle is done: a deep gong, struck twice, longer than the Incense gong. */
export const playFinalGong = () => {
  const strike: Tones = [
    [73, 0.28],
    [146, 0.14],
    [219, 0.08],
    [391, 0.05],
  ];
  play([
    { at: 0, seconds: 7, tones: strike },
    { at: 1.7, seconds: 7, tones: strike },
  ]);
};
