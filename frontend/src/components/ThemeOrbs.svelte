<!-- The three theme orbs: Serene Peak, Pavilion teal, Pavilion crimson. In onboarding they sit fixed in the
     corner, so choosing a theme never moves anything; in the header, bare, beside the clock. The Serene orb
     shows the look a click gives: in Serene it switches between the scroll colours and green (the bright
     green while the scroll look shows, the cream one while green shows); from Pavilion it brings back the
     Serene look last chosen. -->
<script lang="ts">
  import { view } from '../lib/view.svelte';
  import type { DayVariant, Theme } from '../lib/api';

  let { placement = 'corner' }: { placement?: 'corner' | 'header' } = $props();

  type Orb = { label: string; swatch: string; theme: Theme; variant: DayVariant };

  const current = $derived(view.current?.appearance);

  const sereneTarget = $derived.by((): DayVariant => {
    const saved = current?.serene_variant ?? 'scroll';
    if (current?.theme !== 'serene') return saved;
    return saved === 'green' ? 'scroll' : 'green';
  });

  const orbs = $derived<Orb[]>([
    {
      label: 'Serene Peak theme',
      swatch: sereneTarget === 'green' ? 'var(--swatch-serene-green)' : 'var(--swatch-serene)',
      theme: 'serene',
      variant: sereneTarget,
    },
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
  ]);

  function active(orb: Orb): boolean {
    if (current?.theme !== orb.theme) return false;
    return orb.theme === 'serene' || current.day_variant === orb.variant;
  }

  const hint = (orb: Orb) =>
    orb.theme === 'serene' ? `Serene Peak, ${orb.variant === 'green' ? 'green' : 'scroll'}` : '';
</script>

<div class="orbs" data-placement={placement} data-tour="orbs">
  {#each orbs as orb (orb.label)}
    <button
      class="orb"
      style:background={orb.swatch}
      aria-label={orb.label}
      aria-pressed={active(orb)}
      title={hint(orb) || undefined}
      onclick={() => view.choose(orb.theme, orb.variant)}
    ></button>
  {/each}
</div>

<style>
  .orbs {
    display: flex;
    gap: var(--space-3);
  }

  .orbs[data-placement='corner'] {
    position: fixed;
    right: var(--size-gutter);
    bottom: var(--size-gutter);
    z-index: 10;
  }

  .orbs[data-placement='header'] {
    align-self: center;
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
