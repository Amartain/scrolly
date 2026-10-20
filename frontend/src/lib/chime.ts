/**
 * The sunset chime: 216 Hz and 432 Hz sine tones with a six second exponential decay, made with
 * Web Audio (no audio files). It only runs when the user turned the chime on, or pressed Test.
 */
const SECONDS = 6;
const TONES: [hz: number, level: number][] = [
  [216, 0.18],
  [432, 0.09],
];

/** Tones that start together and fade over `seconds`, then the audio context is closed. */
function ring(tones: [hz: number, level: number][], seconds: number): void {
  const Context = window.AudioContext;
  if (!Context) return;
  const audio = new Context();
  void audio.resume();
  const start = audio.currentTime;
  for (const [hz, level] of tones) {
    const tone = audio.createOscillator();
    const gain = audio.createGain();
    tone.frequency.value = hz;
    gain.gain.setValueAtTime(0.0001, start);
    gain.gain.linearRampToValueAtTime(level, start + 0.05);
    gain.gain.exponentialRampToValueAtTime(0.0001, start + seconds);
    tone.connect(gain).connect(audio.destination);
    tone.start(start);
    tone.stop(start + seconds + 0.1);
  }
  setTimeout(() => void audio.close(), (seconds + 1) * 1000);
}

export const playChime = () => ring(TONES, SECONDS);

/** Seclusion's gong: a low bell with inharmonic partials, softer and shorter than the chime. */
const GONG: [hz: number, level: number][] = [
  [110, 0.2],
  [220, 0.1],
  [304, 0.06],
  [594, 0.03],
];
export const playGong = () => ring(GONG, 4);

/** A soft tick that says a sudden trial was written down. */
export const playTick = () => ring([[880, 0.05]], 0.25);
