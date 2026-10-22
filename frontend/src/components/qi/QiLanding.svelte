<!-- Where today's Qi lands with the answer on the card, drawn like the dashboard's Qi bar: the zone's colour,
     ticks where Harmonious and Igniting the Blood end, and the move in words ("60 → 80 · Harmonious"). -->
<script lang="ts">
  import type { QiCard } from '../../lib/qi-api';
  import { QI_CARD, QI_ZONE } from '../../lib/copy-qi';

  let { card, from }: { card: QiCard; from: number } = $props();
</script>

<div class="landing">
  <span class="label display">{QI_CARD.today}</span>
  <span class="track" data-zone={card.zone} aria-hidden="true">
    <span class="fill" style:width="{card.fill_pct}%"></span>
    <span class="tick" style:left="{card.calm_end_pct}%"></span>
    <span class="tick" style:left="{card.surge_end_pct}%"></span>
  </span>
  <span class="move digits" aria-live="polite"
    >{QI_CARD.move(from, card.spent)} · {QI_ZONE[card.zone]}</span
  >
</div>

<style>
  .landing {
    display: grid;
    grid-template-columns: auto minmax(0, 1fr);
    align-items: center;
    gap: var(--space-1) var(--space-3);
    width: 100%;
  }

  .label {
    color: var(--ink-muted);
    font-size: var(--text-display-sm);
  }

  .track {
    position: relative;
    height: var(--space-4);
    background: var(--inset);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-sunken);
  }

  [data-zone='harmonious'] {
    --tone: var(--qi-calm);
  }

  [data-zone='igniting'] {
    --tone: var(--qi-surge);
  }

  [data-zone='strain'] {
    --tone: var(--qi-redline);
  }

  .fill {
    position: absolute;
    inset: 0 auto 0 0;
    background-color: var(--tone);
    background-image: var(--gloss);
    transition: background-color 150ms;
  }

  .tick {
    position: absolute;
    top: 0;
    bottom: 0;
    width: var(--border-width);
    translate: -50% 0;
    background: var(--ink-muted);
  }

  .move {
    grid-column: 2;
    color: var(--num-text);
    font-size: var(--text-body-sm);
  }

  @media (prefers-reduced-motion: reduce) {
    .fill {
      transition: none;
    }
  }
</style>
