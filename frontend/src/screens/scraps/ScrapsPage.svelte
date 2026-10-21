<!-- Bamboo Scraps, kept: every finished visit to Seclusion, newest first. Read-only; there is nothing to
     open. The Markdown export is one file with all of them. -->
<script lang="ts">
  import Button from '../../components/Button.svelte';
  import { SECLUSION } from '../../lib/copy-seclusion';
  import { scraps, type ScrapPage } from '../../lib/scraps-api';
  import ScrapCard from './ScrapCard.svelte';

  let { onback }: { onback: () => void } = $props();

  let pages = $state<ScrapPage[] | null>(null);

  $effect(() => {
    void scraps.pages().then((found) => (pages = found));
  });
</script>

<div class="page">
  <div class="bar">
    <h1 class="display title">{SECLUSION.scrapsTitle}</h1>
    <div class="actions">
      <a class="export display" href="/api/scraps/export.md" download>
        {SECLUSION.scrapsPage.export}
      </a>
      <Button label={SECLUSION.scrapsPage.back} onclick={onback} />
    </div>
  </div>
  <div class="list">
    {#if pages && pages.length === 0}
      <p class="empty">{SECLUSION.scrapsPage.empty}</p>
    {/if}
    {#each pages ?? [] as scrap (scrap.id)}
      <ScrapCard {scrap} />
    {/each}
  </div>
</div>

<style>
  .page {
    flex: 1;
    min-height: 0;
    display: flex;
    flex-direction: column;
    gap: var(--space-4);
    padding: var(--space-4) var(--size-gutter) var(--shadow-room);
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

  .actions {
    display: flex;
    align-items: center;
    gap: var(--space-4);
  }

  .export {
    color: var(--ink-muted);
    font-size: var(--text-display-sm);
  }

  .list {
    flex: 1;
    min-height: 0;
    display: flex;
    flex-direction: column;
    gap: var(--space-4);
    padding-right: var(--shadow-room);
    overflow-y: auto;
    scrollbar-width: thin;
    scrollbar-color: var(--scrollbar-thumb) var(--scrollbar-track);
  }

  .empty {
    margin: 0;
    color: var(--ink-muted);
  }
</style>
