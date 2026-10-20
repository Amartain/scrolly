/**
 * The sunset chime: 216 Hz and 432 Hz sine tones with a six second exponential decay, made with
 * Web Audio (no audio files). It only runs when the user turned the chime on, or pressed Test.
 */
const SECONDS = 6;
const TONES: [hz: number, level: number][] = [
  [216, 0.18],
  [432, 0.09],
];

export function playChime(): void {
  const Context = window.AudioContext;
  if (!Context) return;
  const audio = new Context();
  void audio.resume();
  const start = audio.currentTime;
  for (const [hz, level] of TONES) {
    const tone = audio.createOscillator();
    const gain = audio.createGain();
    tone.frequency.value = hz;
    gain.gain.setValueAtTime(0.0001, start);
    gain.gain.linearRampToValueAtTime(level, start + 0.05);
    gain.gain.exponentialRampToValueAtTime(0.0001, start + SECONDS);
    tone.connect(gain).connect(audio.destination);
    tone.start(start);
    tone.stop(start + SECONDS + 0.1);
  }
  setTimeout(() => void audio.close(), (SECONDS + 1) * 1000);
}
