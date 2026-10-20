<!-- The three disciplines. Only the Trial of the Incense is lit so far. -->
<script lang="ts">
  import { SECLUSION } from '../../lib/copy-seclusion';

  const TABS = [
    { id: 'incense', label: SECLUSION.tabs.incense, ready: true },
    { id: 'pulse', label: SECLUSION.tabs.pulse, ready: false },
    { id: 'flow', label: SECLUSION.tabs.flow, ready: false },
  ];
</script>

<div class="tabs" role="tablist" aria-label="Discipline">
  {#each TABS as tab (tab.id)}
    <button
      class="tab display"
      role="tab"
      type="button"
      aria-selected={tab.id === 'incense'}
      disabled={!tab.ready}
      title={tab.ready ? undefined : SECLUSION.tabLater}
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
    background: var(--gold);
    background-image: none;
    color: var(--on-gold);
  }

  .tab:disabled {
    background: var(--surface-stripe);
    background-image: none;
    color: var(--ink-faint);
    cursor: default;
  }
</style>
