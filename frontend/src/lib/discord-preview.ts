/**
 * The Dispatch as Discord will show it: headings, emoji for shortcodes, the actual time in bold. Display
 * only: the text itself comes from Python (domain/dispatch.py) and is copied as it is.
 */
import type { components } from './api-types';

type Legend = components['schemas']['LegendOut'];

export interface Part {
  text: string;
  strong?: boolean;
  muted?: boolean;
}

export interface Line {
  kind: 'h1' | 'h2' | 'text' | 'blank';
  parts: Part[];
}

/** Shortcodes the scroll uses besides the legend's own. */
const FIXED: Record<string, string> = {
  scroll: '📜',
  zzz: '💤',
  crescent_moon: '🌙',
  leaves: '🍃',
  droplet: '💧',
  cloud: '☁️',
  lotus: '🪷',
  white_circle: '⚪',
  herb: '🌿',
};

const SHORTCODE = /:(\w+):/g;
const BESIDE = ' ⇄ ';

function emojiMap(legend: Legend | undefined): Record<string, string> {
  const own = Object.values({ ...legend?.states, ...legend?.types }).map((symbol) => [
    symbol.shortcode.replaceAll(':', ''),
    symbol.emoji,
  ]);
  return { ...FIXED, ...Object.fromEntries(own) };
}

function withEmoji(text: string, emoji: Record<string, string>): string {
  return text.replace(SHORTCODE, (whole, name: string) => emoji[name] ?? whole);
}

/** A Done line: the actual time after ">>" in bold, and the ⇄ partner muted. */
function parts(text: string): Part[] {
  const [head, tail] = text.split(' >> ');
  if (tail === undefined) return [{ text }];
  const [actual, partner] = tail.split(BESIDE);
  return [
    { text: `${head} » ` },
    { text: actual, strong: true },
    ...(partner === undefined ? [] : [{ text: ` ⇄ ${partner}`, muted: true }]),
  ];
}

export function preview(text: string, legend: Legend | undefined): Line[] {
  const emoji = emojiMap(legend);
  return text
    .trimEnd()
    .split('\n')
    .map((raw): Line => {
      const line = withEmoji(raw, emoji);
      if (!line.trim()) return { kind: 'blank', parts: [] };
      if (line.startsWith('## ')) return { kind: 'h2', parts: [{ text: line.slice(3) }] };
      if (line.startsWith('# ')) return { kind: 'h1', parts: [{ text: line.slice(2) }] };
      return { kind: 'text', parts: parts(line) };
    });
}
