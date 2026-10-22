<!-- One tile of the finished-day tally: a big gold figure over its label. A number rolls up to its value
     when the tile first shows; text (a time) just appears. `settled` jumps to the end. -->
<script lang="ts">
  import { onDestroy } from 'svelte';
  import MandateMark from './MandateMark.svelte';

  let {
    label,
    value,
    shown,
    settled,
    mandate = false,
  }: {
    label: string;
    value: number | string;
    shown: boolean;
    settled: boolean;
    /** The tile counts Heavenly Mandates: its label is the crimson word. */
    mandate?: boolean;
  } = $props();

  const STEPS = 8;
  const STEP_MS = 45;

  let rolled = $state(0);
  let ticker: ReturnType<typeof setInterval> | undefined;

  $effect(() => {
    if (typeof value !== 'number') return;
    if (settled || !shown) {
      rolled = settled ? value : 0;
      return;
    }
    let step = 0;
    ticker = setInterval(() => {
      step += 1;
      rolled = Math.round((value * step) / STEPS);
      if (step >= STEPS) clearInterval(ticker);
    }, STEP_MS);
    return () => clearInterval(ticker);
  });

  onDestroy(() => clearInterval(ticker));

  const figure = $derived(typeof value === 'number' ? rolled : value);
</script>

<div class="tile" class:shown={shown || settled}>
  <span class="figure display digits">{figure}</span>
  <span class="label">
    {#if mandate}<MandateMark>{label}</MandateMark>{:else}{label}{/if}
  </span>
</div>

<style>
  .tile {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: var(--space-2);
    padding: var(--space-3) var(--space-2);
    background: var(--scene-card-raised);
    border: var(--border-width) solid var(--scene-ink);
    box-shadow: var(--shadow-button);
    opacity: 0;
    transition: opacity var(--glitch-fade) linear;
  }

  .shown {
    opacity: 1;
  }

  .figure {
    color: var(--scene-card-num);
    font-size: var(--text-display-xl);
    line-height: 1;
    text-shadow: var(--space-1) var(--space-1) 0 var(--scene-card-num-shadow);
  }

  .label {
    color: var(--scene-card-muted);
    font-size: var(--text-body-sm);
    text-align: center;
  }
</style>
