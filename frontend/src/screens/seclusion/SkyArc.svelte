<!-- A thin arc in Seclusion's top bar, with the sun on it by day and the moon after the sunset. Python says
     which and how far along (view.sky); it moves a step with each minute's view, without animating. -->
<script lang="ts">
  import { view } from '../../lib/view.svelte';

  const sky = $derived(view.current?.sky);
  // The arc is a quadratic curve from (8, 30) over (60, -6) to (112, 30).
  const at = (t: number, a: number, b: number, c: number) =>
    (1 - t) ** 2 * a + 2 * (1 - t) * t * b + t ** 2 * c;
  const x = $derived(sky ? at(sky.progress, 8, 60, 112) : 8);
  const y = $derived(sky ? at(sky.progress, 30, -6, 30) : 30);
</script>

{#if sky}
  <svg
    class="sky"
    viewBox="0 0 120 34"
    role="img"
    aria-label="The {sky.body} on its way across the sky"
  >
    <path class="arc" d="M8,30 Q60,-6 112,30" />
    {#if sky.body === 'sun'}
      <circle class="sun" cx={x} cy={y} r="5" />
    {:else}
      <circle class="moon" cx={x} cy={y} r="5" />
      <circle class="moon-shade" cx={x + 2.5} cy={y - 1.5} r="4.2" />
    {/if}
  </svg>
{/if}

<style>
  .sky {
    width: var(--size-sky-arc);
    height: var(--size-glyph-button);
    overflow: visible;
  }

  .arc {
    fill: none;
    stroke: var(--plaque-rule);
    stroke-width: 1.5;
    stroke-dasharray: 3 3;
  }

  .sun {
    fill: var(--gold);
    stroke: var(--line);
    stroke-width: 1.5;
  }

  .moon {
    fill: var(--ink);
  }

  .moon-shade {
    fill: var(--surface-panel);
  }
</style>
