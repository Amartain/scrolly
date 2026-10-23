<!-- The three disciplines, as chips at the head of the card. Each keeps its own colour; choosing one closes
     the segment that was running (its time stays on the trial) and waits, fresh, for Start. -->
<script lang="ts">
  import { SECLUSION } from '../../lib/copy-seclusion';
  import { seclusion } from '../../lib/seclusion.svelte';
  import type { SeclusionState } from '../../lib/seclusion-api';

  let { room }: { room: SeclusionState } = $props();

  const TABS = ['incense', 'cycles', 'flow'] as const;
  /** The tour's lesson each chip teaches; Incense is the room itself. */
  const LESSON = { incense: undefined, cycles: 'cycles', flow: 'river-flow' } as const;
</script>

<div class="tabs" role="tablist" aria-label="Discipline">
  {#each TABS as tab (tab)}
    <button
      class="tab display"
      role="tab"
      type="button"
      data-tab={tab}
      data-tour={LESSON[tab]}
      aria-label={SECLUSION.tabs[tab]}
      title={SECLUSION.tabs[tab]}
      aria-selected={tab === room.discipline}
      onclick={() => void (tab !== room.discipline && seclusion.chooseDiscipline(tab))}
    >
      {SECLUSION.chips[tab]}
    </button>
  {/each}
</div>

<style>
  .tabs {
    display: flex;
    justify-content: center;
    gap: var(--space-2);
    padding: var(--space-4) var(--space-4) 0;
  }

  .tab {
    height: var(--size-glyph-button);
    padding-inline: var(--space-3);
    background: transparent;
    color: var(--ink);
    border: var(--border-width) solid var(--line);
    font-size: var(--text-display-sm);
    letter-spacing: 0.08em;
    white-space: nowrap;
    cursor: pointer;
  }

  .tab[aria-selected='true'] {
    --tab-bg: var(--gold);
    --tab-ink: var(--on-gold);
    background: var(--tab-bg);
    color: var(--tab-ink);
    box-shadow: var(--shadow-button);
  }

  .tab[aria-selected='true'][data-tab='cycles'] {
    --tab-bg: var(--cycles);
    --tab-ink: var(--on-cycles);
  }

  .tab[aria-selected='true'][data-tab='flow'] {
    --tab-bg: var(--flow);
    --tab-ink: var(--on-flow);
  }
</style>
