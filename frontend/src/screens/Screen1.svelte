<script lang="ts">
  import Panel from '../components/Panel.svelte';
</script>

<div class="grid">
  <div class="column left">
    <Panel title="Essence" empty="No trials on the scroll." />
    <div class="immediate">
      <Panel title="The Immediate Trial" empty="Nothing is underway." />
    </div>
    <Panel title="Conquered Today" empty="Nothing conquered yet." />
  </div>
  <div class="column right">
    <div class="stats">
      <Panel title="Lifetime Conquered" empty="0" />
      <Panel title="Total Days Used" empty="0" />
    </div>
    <Panel title="Cumulative Momentum" empty="Your momentum appears here." />
    <Panel title="7-Day Rhythm" empty="Your rhythm appears here." />
  </div>
</div>
<div class="fold display">One scroll down · the planning peak</div>

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
    margin-top: var(--space-4);
    background: var(--surface-stripe);
    border-top: var(--border-width) solid var(--line);
    color: var(--ink-muted);
    font-size: var(--text-display-sm);
  }
</style>
