<!-- Shows a chart as it is, or, for a fresh scroll, a fixed shape under fog with an invitation. -->
<script lang="ts">
  import type { Snippet } from 'svelte';

  let { foggy, invite, children }: { foggy: boolean; invite: string; children: Snippet } = $props();
</script>

<div class="stage">
  <div class="chart" class:foggy aria-hidden={foggy}>{@render children()}</div>
  {#if foggy}<p class="invite display" role="status">{invite}</p>{/if}
</div>

<style>
  .stage {
    position: relative;
    height: 100%;
    min-height: 0;
  }

  .chart {
    height: 100%;
    min-height: 0;
    display: flex;
    flex-direction: column;
  }

  .chart.foggy {
    filter: blur(var(--space-1));
    opacity: 0.55;
  }

  .invite {
    position: absolute;
    inset: 0;
    margin: 0;
    display: grid;
    place-items: center;
    padding: var(--space-4);
    text-align: center;
    color: var(--ink);
    font-size: var(--text-display-sm);
  }
</style>
