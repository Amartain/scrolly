<script lang="ts" generics="T extends { id: string }">
  import type { Snippet } from 'svelte';

  let { items, row, empty = '' }: { items: T[]; row: Snippet<[T]>; empty?: string } = $props();
</script>

{#if items.length === 0}
  {#if empty}<p class="empty">{empty}</p>{/if}
{:else}
  <ul class="rows">
    {#each items as item (item.id)}
      <li class="row">{@render row(item)}</li>
    {/each}
  </ul>
{/if}

<style>
  .rows {
    margin: 0;
    padding: 0;
    list-style: none;
  }

  .row {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    min-height: var(--size-row);
    padding-inline: var(--space-4);
    font-size: var(--text-body-md);
  }

  .empty {
    margin: 0;
    padding: var(--space-2) var(--space-4);
    color: var(--ink-muted);
  }
</style>
