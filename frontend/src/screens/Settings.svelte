<script lang="ts">
  import Button from '../components/Button.svelte';
  import DataPanel from './DataPanel.svelte';
  import FeedbackPanel from './FeedbackPanel.svelte';
  import GoldenCorePanel from './GoldenCorePanel.svelte';
  import HeaderPanel from './HeaderPanel.svelte';
  import SealPanel from './SealPanel.svelte';
  import SunsetPanel from './SunsetPanel.svelte';
  import SymbolsPanel from './SymbolsPanel.svelte';
  import ThemePanel from './ThemePanel.svelte';

  let { onback }: { onback: () => void } = $props();
</script>

<div class="settings">
  <div class="bar">
    <h1 class="display title">Settings</h1>
    <Button label="Back" onclick={onback} />
  </div>
  <div class="column">
    <ThemePanel />
    <HeaderPanel />
    <SymbolsPanel />
  </div>
  <div class="column">
    <SunsetPanel />
    <GoldenCorePanel />
    <DataPanel />
    <SealPanel ondone={onback} />
    <FeedbackPanel />
  </div>
</div>

<style>
  .settings {
    flex: 1;
    min-height: 0;
    display: grid;
    grid-template-columns: minmax(0, 3fr) minmax(0, 2fr);
    grid-template-rows: auto minmax(0, 1fr);
    gap: var(--space-4) var(--space-5);
    padding: var(--space-4) var(--size-gutter);
  }

  .bar {
    grid-column: 1 / -1;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .title {
    margin: 0;
    font-size: var(--text-display-lg);
  }

  .column {
    display: flex;
    flex-direction: column;
    gap: var(--space-4);
    min-height: 0;
    padding-right: var(--shadow-room);
    padding-bottom: var(--shadow-room);
    overflow-y: auto;
    scrollbar-gutter: stable;
    scrollbar-width: thin;
    scrollbar-color: var(--scrollbar-thumb) var(--scrollbar-track);
  }
</style>
