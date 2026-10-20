<script lang="ts">
  import Button from '../components/Button.svelte';
  import DataPanel from './DataPanel.svelte';
  import GoldenCorePanel from './GoldenCorePanel.svelte';
  import SunsetPanel from './SunsetPanel.svelte';
  import ThemePanel from './ThemePanel.svelte';

  let { onback }: { onback: () => void } = $props();
</script>

<div class="settings">
  <div class="main">
    <div class="bar">
      <h1 class="display title">Settings</h1>
      <Button label="Back" onclick={onback} />
    </div>
    <ThemePanel />
    <SunsetPanel />
    <GoldenCorePanel />
    <DataPanel />
  </div>
</div>

<style>
  .settings {
    flex: 1;
    min-height: 0;
    display: grid;
    grid-template-columns: minmax(0, 3fr) minmax(0, 2fr);
    gap: var(--space-5);
    padding: var(--space-4) var(--size-gutter);
  }

  .main {
    display: flex;
    flex-direction: column;
    gap: var(--space-4);
    min-height: 0;
    padding-right: var(--shadow-room);
  }

  .bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .title {
    margin: 0;
    font-size: var(--text-display-lg);
  }
</style>
