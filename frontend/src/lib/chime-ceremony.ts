/**
 * The sounds of the finished-day ceremony, made like every other sound of the app (chime.ts): no
 * files. Thunder is shaped noise. All of them follow the volume and the mute.
 */
import { loudness, play } from './chime';

/** White noise through a low-pass filter: bright for the crack, dark for the rumble. */
function noise(audio: AudioContext, at: number, seconds: number, level: number, cutoff: number) {
  const length = Math.ceil(audio.sampleRate * seconds);
  const buffer = audio.createBuffer(1, length, audio.sampleRate);
  const samples = buffer.getChannelData(0);
  for (let i = 0; i < length; i++) samples[i] = Math.random() * 2 - 1;
  const source = audio.createBufferSource();
  source.buffer = buffer;
  const filter = audio.createBiquadFilter();
  filter.type = 'lowpass';
  filter.frequency.value = cutoff;
  const gain = audio.createGain();
  gain.gain.setValueAtTime(0.0001, at);
  gain.gain.linearRampToValueAtTime(level, at + 0.01);
  gain.gain.exponentialRampToValueAtTime(0.0001, at + seconds);
  source.connect(filter).connect(gain).connect(audio.destination);
  source.start(at);
  source.stop(at + seconds);
}

/** The bolt lands: a sharp crack, a long low rumble, then a rising golden chime as the cultivator stands. */
export function playThunder(): void {
  const factor = loudness(true);
  const Context = window.AudioContext;
  if (!Context || factor <= 0) return;
  const audio = new Context();
  void audio.resume();
  const now = audio.currentTime;
  noise(audio, now, 0.45, 0.55 * factor, 3500);
  noise(audio, now + 0.04, 3, 0.5 * factor, 180);
  setTimeout(() => void audio.close(), 4000);
  play([
    { at: 0, seconds: 2.4, attack: 0.01, drop: 2, tones: [[50, 0.3]] },
    { at: 0.4, seconds: 1.6, tones: [[523, 0.035]] },
    { at: 0.55, seconds: 1.6, tones: [[659, 0.035]] },
    {
      at: 0.7,
      seconds: 2.2,
      tones: [
        [784, 0.04],
        [1568, 0.015],
      ],
    },
  ]);
}

/** The card arrives without a storm: a deep drum under a short rising shimmer. */
export const playTribulation = () =>
  play([
    {
      at: 0,
      seconds: 2.5,
      attack: 0.01,
      drop: 2,
      tones: [
        [55, 0.3],
        [110, 0.12],
      ],
    },
    { at: 0.15, seconds: 1.4, tones: [[660, 0.04]] },
    { at: 0.3, seconds: 1.4, tones: [[880, 0.04]] },
    { at: 0.45, seconds: 2, tones: [[1320, 0.05]] },
  ]);

/** One tile of the tally lands: a soft tick, each a little higher than the last. */
export const playTallyTick = (step: number) =>
  play([{ at: 0, seconds: 0.25, tones: [[523 * 1.1225 ** step, 0.06]] }]);

/** A trial begins from nothing: a match strikes, then a warm bowl swells as the incense catches. */
export function playIgnite(): void {
  const factor = loudness(true);
  const Context = window.AudioContext;
  if (!Context || factor <= 0) return;
  const audio = new Context();
  void audio.resume();
  noise(audio, audio.currentTime, 0.14, 0.18 * factor, 6000);
  setTimeout(() => void audio.close(), 1000);
  play([
    {
      at: 0.08,
      seconds: 2.2,
      attack: 0.25,
      tones: [
        [196, 0.12],
        [392, 0.05],
        [588, 0.02],
      ],
    },
  ]);
}

/** A paused trial goes on: one soft, short tick. */
export const playResumeTick = () => play([{ at: 0, seconds: 0.18, tones: [[1047, 0.04]] }]);

// A major pentatonic scale from C5: every phrase in it sounds bright, whatever step it starts on.
const PENTATONIC = [
  523.25, 587.33, 659.25, 783.99, 880, 1046.5, 1174.66, 1318.51, 1567.98, 1760, 2093,
];
const TOP_STEP = 7;

/**
 * A trial conquered: a rising three-note phrase. `count` is how many trials are conquered today;
 * each conquest starts a step higher than the last, so the day builds like a melody (from the 8th
 * the top phrase repeats). It begins again each morning and never steps down.
 */
export function playConquest(count: number): void {
  const step = Math.min(Math.max(count, 1) - 1, TOP_STEP);
  const notes = [PENTATONIC[step], PENTATONIC[step + 2], PENTATONIC[step + 3]];
  play([
    { at: 0, seconds: 1.2, tones: [[PENTATONIC[step] / 2, 0.05]] },
    ...notes.map((hz, i) => ({
      at: i * 0.09,
      seconds: i === 2 ? 1.6 : 0.9,
      attack: 0.01,
      tones: [[hz, 0.055] as [number, number]],
    })),
  ]);
}
