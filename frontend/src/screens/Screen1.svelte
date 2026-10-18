<script lang="ts">
  import Panel from '../components/Panel.svelte';
  import { showScreen } from '../lib/screens';
</script>

<div class="grid">
  <div class="column left">
    <Panel title="Essence" empty="No trials on the scroll." />
    <div class="immediate">
      <Panel title="The Immediate Trial" empty="Nothing is underway." scroll />
    </div>
    <Panel title="Conquered Today" empty="Nothing conquered yet." scroll />
  </div>
  <div class="column right">
    <div class="stats">
      <Panel title="Lifetime Conquered" empty="0" />
      <Panel title="Heavenly Cycles" empty="0" />
    </div>
    <Panel title="Cumulative Momentum" empty="Your momentum appears here." />
    <Panel title="Rhythm" empty="Your rhythm appears here." />
  </div>
</div>
<button class="fold display" type="button" onclick={() => showScreen('two')}>
  The planning peak <kbd>↓</kbd>
</button>

<style>
  .grid {
    flex: 1;
    min-height: 0;
    display: grid;
    grid-template-columns: minmax(0, 3fr) minmax(0, 2fr);
    gap: var(--space-5);
    padding: var(--space-4) var(--size-gutter) 0;
  }

  .column {
    display: grid;
    gap: var(--space-4);
    min-height: 0;
  }

  .left {
    grid-template-rows: var(--size-short-panel) var(--size-immediate) minmax(0, 1fr);
  }

  .right {
    grid-template-rows: var(--size-short-panel) minmax(0, 1fr) minmax(0, 1fr);
  }

  .immediate {
    display: grid;
    min-height: 0;
  }

  .stats {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--space-5);
  }

  .fold {
    flex: none;
    height: var(--size-fold);
    display: flex;
    align-items: center;
    justify-content: center;
    gap: var(--space-3);
    margin: var(--space-4) 0 0;
    padding: 0;
    border: 0;
    border-top: var(--border-width) solid var(--line);
    background: var(--surface-stripe);
    color: var(--ink-muted);
    font-size: var(--text-display-sm);
    cursor: pointer;
  }

  .fold:hover {
    color: var(--ink);
  }

  kbd {
    padding-inline: var(--space-2);
    background: var(--surface-raised);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-button);
    color: var(--ink);
    font: inherit;
  }
</style>
