<!-- The type symbol of the Legend of the Scrolls (🪷 Mandate, ⚪ Mortal, 📜 and 🌿 Arts).
     With `onToggle` the mark is the control that switches Mandate and Mortal; without, it is only a mark. -->
<script lang="ts">
  import { view } from '../lib/view.svelte';

  let {
    type,
    title = '',
    onToggle,
  }: { type: string; title?: string; onToggle?: () => void } = $props();

  const symbol = $derived(view.current?.legend.types[type]);
  const isMandate = $derived(type === 'mandate');
  // Arts keep their type; only Mandate and Mortal switch.
  const switchable = $derived(onToggle !== undefined && (isMandate || type === 'mortal'));
  const label = $derived(
    isMandate ? `Make ${title} a Mortal Trial` : `Make ${title} a Heavenly Mandate`,
  );
</script>

{#if symbol}
  {#if switchable}
    <button
      class="mark toggle"
      type="button"
      aria-pressed={isMandate}
      aria-label={label}
      title={label}
      onclick={onToggle}
    >
      {symbol.emoji}
    </button>
  {:else}
    <span class="mark" role="img" aria-label={symbol.label} title={symbol.label}
      >{symbol.emoji}</span
    >
  {/if}
{/if}

<style>
  .mark {
    flex: none;
    width: var(--size-icon);
    padding: 0;
    font-size: var(--size-icon);
    line-height: 1;
    text-align: center;
  }

  .toggle {
    cursor: pointer;
    background: none;
    border: 0;
  }

  .toggle:hover {
    background: var(--row-b);
  }
</style>
