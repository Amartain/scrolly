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
