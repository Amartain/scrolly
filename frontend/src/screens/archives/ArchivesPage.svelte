<!-- The Grand Archives: past days, newest first, fourteen at a time. Read-only. -->
<script lang="ts">
  import Button from '../../components/Button.svelte';
  import GuidanceButton from '../../components/GuidanceButton.svelte';
  import SprigIcon from '../../icons/SprigIcon.svelte';
  import { archives, type ArchiveCard } from '../../lib/archives-api';
  import { ARCHIVES } from '../../lib/copy-archives';
  import ArchiveDay from './ArchiveDay.svelte';

  let { onback }: { onback: () => void } = $props();

  let cards = $state<ArchiveCard[] | null>(null);
  let older = $state<string | null>(null);

  async function load(before: string | null) {
    const page = await archives.page(before);
    cards = [...(cards ?? []), ...page.cards];
    older = page.older ?? null;
  }

  $effect(() => {
    void load(null);
  });
</script>

<div class="page">
  <div class="bar">
    <div class="heading">
      <h1 class="display title">{ARCHIVES.title}</h1>
      <GuidanceButton topic="archives" />
    </div>
    <Button label={ARCHIVES.back} onclick={onback} />
  </div>
  <div class="list">
    {#if cards && cards.length === 0}
      <p class="empty">{ARCHIVES.empty}</p>
    {/if}
    {#each cards ?? [] as card (card.day)}
      {#if card.rest_days > 0}
        <p class="rest">
          <SprigIcon />
          <span>{ARCHIVES.rest(card.rest_days)}</span>
        </p>
      {/if}
      <ArchiveDay {card} />
    {/each}
    {#if older}
      <div class="more"><Button label={ARCHIVES.older} onclick={() => load(older)} /></div>
    {/if}
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

  .heading {
    display: flex;
    align-items: center;
    gap: var(--space-3);
  }

  .title {
    margin: 0;
    font-size: var(--text-display-lg);
  }

  .list {
    flex: 1;
    min-height: 0;
    display: flex;
    flex-direction: column;
    gap: var(--space-4);
    padding-right: var(--shadow-room);
    padding-bottom: var(--shadow-room);
    overflow-y: auto;
    scrollbar-width: thin;
    scrollbar-color: var(--scrollbar-thumb) var(--scrollbar-track);
  }

  .rest {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    margin: 0;
    color: var(--ink-muted);
  }

  .more {
    display: flex;
    justify-content: center;
  }

  .empty {
    margin: 0;
    color: var(--ink-muted);
  }
</style>
