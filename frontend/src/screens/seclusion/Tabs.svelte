<!-- The three disciplines. Each keeps its own colour; choosing one closes the segment that was running
     (its time stays on the trial) and waits, fresh, for Start. -->
<script lang="ts">
  import { SECLUSION } from '../../lib/copy-seclusion';
  import { seclusion } from '../../lib/seclusion.svelte';
  import type { Discipline, SeclusionState } from '../../lib/seclusion-api';

  let { room }: { room: SeclusionState } = $props();

  const TABS: { id: Discipline; label: string }[] = [
    { id: 'incense', label: SECLUSION.tabs.incense },
    { id: 'cycles', label: SECLUSION.tabs.cycles },
    { id: 'flow', label: SECLUSION.tabs.flow },
  ];
</script>

<div class="tabs" role="tablist" aria-label="Discipline">
  {#each TABS as tab (tab.id)}
    <button
      class="tab display"
      role="tab"
      type="button"
      data-tab={tab.id}
      aria-selected={tab.id === room.discipline}
      onclick={() => void (tab.id !== room.discipline && seclusion.chooseDiscipline(tab.id))}
    >
      {tab.label}
    </button>
  {/each}
</div>

<style>
  .tabs {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    height: var(--size-tab);
    border-bottom: var(--border-width) solid var(--line);
  }

  .tab {
    padding-inline: var(--space-3);
    background: var(--btn);
    background-image: var(--gloss-btn);
    color: var(--ink);
    border: 0;
    border-right: var(--border-width) solid var(--line);
    font-size: var(--text-display-md);
    white-space: nowrap;
    cursor: pointer;
  }

  .tab:last-child {
    border-right: 0;
  }

  .tab[aria-selected='true'] {
    --tab-bg: var(--gold);
    --tab-ink: var(--on-gold);
    background: var(--tab-bg);
    background-image: none;
    color: var(--tab-ink);
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
