<!-- The state symbol of the Legend of the Scrolls (💧 next, ☁️ remaining, 🍃 conquered).
     Emoji for now; custom drawings come later. Which symbol is chosen by Python: view.legend. -->
<script lang="ts">
  import { view } from '../lib/view.svelte';

  let { state }: { state: string } = $props();

  const symbol = $derived(view.current?.legend.states[state]);
</script>

{#if symbol}
  <span class="mark" role="img" aria-label={symbol.label}>{symbol.emoji}</span>
{/if}

<style>
  .mark {
    flex: none;
    width: var(--size-icon);
    font-size: var(--size-icon);
    line-height: 1;
    text-align: center;
  }
</style>
