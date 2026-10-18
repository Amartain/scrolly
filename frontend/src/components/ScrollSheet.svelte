<script lang="ts">
  import type { Snippet } from 'svelte';

  let { title, children }: { title: string; children: Snippet } = $props();
</script>

<!-- Onboarding sits on the background as one framed scroll, like a sheet laid on a table. -->
<div class="table">
  <section class="sheet" aria-label={title}>
    <h1 class="display heading">{title}</h1>
    {@render children()}
  </section>
</div>

<style>
  .table {
    flex: 1;
    min-height: 0;
    display: grid;
    place-items: center;
    padding: var(--space-6) var(--size-gutter);
  }

  .sheet {
    display: flex;
    flex-direction: column;
    gap: var(--space-3);
    width: min(100%, var(--size-sheet-width));
    height: min(100%, var(--size-sheet-height));
    min-height: 0;
    padding: var(--space-5) var(--space-6) var(--space-6);
    background: var(--surface-panel);
    background-image: var(--gloss-faint);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-panel);
  }

  .heading {
    margin: 0;
    font-size: var(--text-display-lg);
  }
</style>
