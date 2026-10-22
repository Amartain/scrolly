<script lang="ts">
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

<!-- No title or Back: the pressed ⚙ in the header (or Esc) goes back. The heading stays for screen readers. -->
<div class="settings">
  <h1 class="sr-only">Settings</h1>
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
    grid-template-rows: minmax(0, 1fr);
    gap: var(--space-4) var(--space-5);
    padding: var(--space-4) var(--size-gutter);
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
  }

  /* Panels keep their full height; the column scrolls instead of squeezing them. */
  .column > :global(*) {
    flex: none;
  }
</style>
