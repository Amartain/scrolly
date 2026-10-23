<script lang="ts">
  import type { Snippet } from 'svelte';
  import type { GuideKey } from '../lib/copy-guidance';
  import GuidanceButton from './GuidanceButton.svelte';

  let { title, guide, children }: { title: string; guide?: GuideKey; children: Snippet } = $props();
</script>

<!-- Onboarding sits on the background as one framed scroll, like a sheet laid on a table. Its guidance
     is a `?` beside the heading, a scroll that pops out (owner, 2026-10-23), not a box on the sheet. -->
<div class="table">
  <section class="sheet" aria-label={title}>
    <div class="head">
      <h1 class="display heading">{title}</h1>
      {#if guide}<GuidanceButton topic={guide} />{/if}
    </div>
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

  .head {
    display: flex;
    align-items: center;
    gap: var(--space-3);
  }

  .heading {
    margin: 0;
    font-size: var(--text-display-lg);
  }
</style>
