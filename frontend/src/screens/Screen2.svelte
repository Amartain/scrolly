<script lang="ts">
  import Button from '../components/Button.svelte';
  import { ARCHIVES } from '../lib/copy-archives';
  import { DISPATCH } from '../lib/copy';
  import { SECLUSION } from '../lib/copy-seclusion';
  import { SCREEN_TWO_ID } from '../lib/screens';
  import ArtsPanels from './screen2/ArtsPanels.svelte';
  import HorizonPanel from './screen2/HorizonPanel.svelte';
  import LetGoPanels from './screen2/LetGoPanels.svelte';
  import RemainingPanel from './screen2/RemainingPanel.svelte';
  import ScribePanel from './screen2/ScribePanel.svelte';

  let {
    ondispatch,
    onscraps,
    onarchives,
  }: { ondispatch: () => void; onscraps: () => void; onarchives: () => void } = $props();
</script>

<div class="screen" id={SCREEN_TWO_ID}>
  <div class="column left">
    <ScribePanel />
    <RemainingPanel />
    <LetGoPanels />
    <ArtsPanels />
  </div>
  <div class="column right">
    <HorizonPanel />
    <div class="tools">
      <Button label={ARCHIVES.open} tone="archives" onclick={onarchives} />
      <Button label={SECLUSION.scrapsTitle} onclick={onscraps} />
      <Button label={DISPATCH.open} onclick={ondispatch} />
    </div>
  </div>
</div>

<style>
  .screen {
    height: 100dvh;
    display: grid;
    grid-template-columns: minmax(0, 3fr) minmax(0, 2fr);
    gap: var(--space-5);
    padding: var(--space-4) var(--size-gutter);
  }

  .column {
    display: grid;
    grid-template-columns: minmax(0, 1fr);
    gap: var(--space-4);
    min-height: 0;
    padding-right: var(--shadow-room);
    padding-bottom: var(--shadow-room);
  }

  .left {
    grid-template-rows: var(--size-short-panel) minmax(0, 3fr) var(--size-short-panel) minmax(
        0,
        2fr
      );
  }

  .right {
    grid-template-rows: minmax(0, 1fr) var(--size-glyph-button);
  }

  .tools {
    /* A fixed row, so a theme with thicker borders moves nothing. */
    display: flex;
    align-items: stretch;
    justify-content: flex-end;
    gap: var(--space-3);
  }

  .tools :global(.button) {
    padding-block: 0;
  }
</style>
