<script lang="ts">
  import { view } from '../lib/view.svelte';
  import type { DayVariant, Theme } from '../lib/api';

  type Orb = { label: string; swatch: string; theme: Theme; variant: DayVariant | null };

  const orbs: Orb[] = [
    { label: 'Serene Peak theme', swatch: 'var(--swatch-serene)', theme: 'serene', variant: null },
    {
      label: 'Hidden Pavilion teal theme',
      swatch: 'var(--swatch-teal)',
      theme: 'pavilion',
      variant: 'teal',
    },
    {
      label: 'Hidden Pavilion crimson theme',
      swatch: 'var(--swatch-crimson)',
      theme: 'pavilion',
      variant: 'crimson',
    },
  ];

  const current = $derived(view.current?.appearance);

  function active(orb: Orb): boolean {
    if (current?.theme !== orb.theme) return false;
    return orb.theme === 'serene' || current.day_variant === orb.variant;
  }
</script>

<!-- Onboarding only. Fixed in the corner so choosing a theme never moves anything. -->
<div class="orbs">
  {#each orbs as orb (orb.label)}
    <button
      class="orb"
      style:background={orb.swatch}
      aria-label={orb.label}
      aria-pressed={active(orb)}
      onclick={() => view.choose(orb.theme, orb.variant)}
    ></button>
  {/each}
</div>

<style>
  .orbs {
    position: fixed;
    right: var(--size-gutter);
    bottom: var(--size-gutter);
    z-index: 10;
    display: flex;
    gap: var(--space-3);
  }

  .orb {
    width: var(--size-orb);
    height: var(--size-orb);
    padding: 0;
    border: var(--border-width) solid var(--line);
    border-radius: 50%;
    box-shadow: var(--shadow-button);
    cursor: pointer;
  }

  .orb[aria-pressed='true'] {
    outline: var(--border-width) solid var(--gold);
    outline-offset: var(--space-1);
  }

  .orb:active {
    transform: translate(var(--shadow-offset), var(--shadow-offset));
    box-shadow: none;
  }
</style>
