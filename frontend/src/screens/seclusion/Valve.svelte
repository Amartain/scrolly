<!-- One release valve of the focus room's side column: a quiet label, then what it holds. The column is
     one frame, so a valve has no box of its own, only a thin line above it. With `onfold` the label
     carries a hide / show toggle; folded, only the label is left. -->
<script lang="ts">
  import type { Snippet } from 'svelte';
  import { SECLUSION } from '../../lib/copy-seclusion';

  let {
    title,
    grow = false,
    folded = false,
    onfold,
    children,
  }: {
    title: string;
    /** Takes the height the other valves leave (and none when folded). */
    grow?: boolean;
    folded?: boolean;
    onfold?: () => void;
    children: Snippet;
  } = $props();
</script>

<section class="valve" class:grow={grow && !folded} aria-label={title}>
  <div class="head">
    <h2 class="label">{title}</h2>
    {#if onfold}
      <button
        class="fold"
        type="button"
        aria-expanded={!folded}
        aria-label={folded ? SECLUSION.fold.showName(title) : SECLUSION.fold.hideName(title)}
        onclick={onfold}>{folded ? SECLUSION.fold.show : SECLUSION.fold.hide}</button
      >
    {/if}
  </div>
  {#if !folded}{@render children()}{/if}
</section>

<style>
  .valve {
    display: flex;
    flex-direction: column;
    min-height: 0;
  }

  .valve:not(:first-child) {
    border-top: var(--border-width) solid var(--grid);
  }

  .grow {
    flex: 1;
  }

  .head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--space-3);
    padding: var(--space-2) var(--space-4) 0;
  }

  .label {
    margin: 0;
    color: var(--ink-muted);
    font-size: var(--text-body-sm);
    font-weight: normal;
  }

  .fold {
    padding-inline: var(--space-1);
    background: none;
    border: 0;
    color: var(--ink-muted);
    font-size: var(--text-body-sm);
    cursor: pointer;
  }

  .fold:hover {
    color: var(--ink);
    text-decoration: underline;
  }
</style>
