<script lang="ts">
  import type { Snippet } from 'svelte';
  import type { GuideKey } from '../lib/copy-guidance';
  import GuidanceButton from './GuidanceButton.svelte';

  type Tone = 'neutral' | 'horizon' | 'foundational' | 'restorative' | 'conquered';

  let {
    title,
    tone = 'neutral',
    empty = 'Nothing here yet.',
    scroll = false,
    striped = false,
    count,
    hint,
    guide,
    actions,
    children,
  }: {
    title: string;
    tone?: Tone;
    empty?: string;
    scroll?: boolean;
    /** Alternate row bands that fill the whole body, even below the last row. */
    striped?: boolean;
    count?: number;
    /** A short line in the header, for example how to reorder. */
    hint?: string;
    /** The `?` after the title: which guidance scroll it opens. */
    guide?: GuideKey;
    /** Small controls at the right of the header, for example the expand button. */
    actions?: Snippet;
    children?: Snippet;
  } = $props();
</script>

<section class="panel {tone}" aria-label={title}>
  <div class="head">
    <div class="heading">
      <h2 class="display">{title}{count === undefined ? '' : ` · ${count}`}</h2>
      {#if guide}<GuidanceButton topic={guide} />{/if}
    </div>
    {#if hint}<span class="hint">{hint}</span>{/if}
    {#if actions}<span class="actions">{@render actions()}</span>{/if}
  </div>
  <div class="body" class:scroll class:striped>
    {#if children}
      {@render children()}
    {:else}
      <p class="empty">{empty}</p>
    {/if}
  </div>
</section>

<style>
  .panel {
    --row-a: transparent;
    --row-b: var(--surface-stripe);
    display: flex;
    flex-direction: column;
    min-height: 0;
    background: var(--surface-panel);
    background-image: var(--gloss-faint);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-panel);
  }

  .head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--space-4);
    min-height: calc(var(--size-glyph-button) + var(--space-2) * 2);
    padding: var(--space-2) var(--space-4);
    background: var(--head-bg);
    color: var(--head-ink);
    border-bottom: var(--border-width) solid var(--line);
  }

  .heading {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    min-width: 0;
  }

  .head h2 {
    margin: 0;
    font-size: var(--text-display-md);
  }

  .actions {
    display: flex;
    gap: var(--space-2);
    margin-left: auto;
  }

  .hint {
    font-size: var(--text-body-sm);
    opacity: 0.8;
  }

  .body {
    flex: 1;
    min-height: 0;
    overflow: hidden;
  }

  .body.striped {
    background-image: repeating-linear-gradient(
      to bottom,
      var(--row-a) 0,
      var(--row-a) var(--size-row),
      var(--row-b) var(--size-row),
      var(--row-b) calc(var(--size-row) * 2)
    );
    background-attachment: local;
  }

  .body.scroll {
    overflow-y: auto;
    scrollbar-gutter: stable;
    scrollbar-width: thin;
    scrollbar-color: var(--scrollbar-thumb) var(--scrollbar-track);
  }

  .empty {
    margin: 0;
    padding: var(--space-2) var(--space-4);
    color: var(--ink-muted);
  }

  .conquered {
    --row-a: var(--conquered-row-a);
    --row-b: var(--conquered-row-b);
  }

  .horizon,
  .foundational,
  .restorative {
    --row-a: var(--card-ink-row-a);
    --row-b: var(--card-ink-row-b);
    color: var(--card-ink);
    box-shadow: var(--shadow-card);
  }

  .horizon {
    --card-ink: var(--card-horizon-ink);
    --card-ink-head: var(--card-horizon-head);
    --card-ink-row-a: var(--card-horizon-row-a);
    --card-ink-row-b: var(--card-horizon-row-b);
    --lotus-ink: var(--card-horizon-mandate);
    background: linear-gradient(160deg, var(--card-horizon-a), var(--card-horizon-b));
  }

  .foundational {
    --card-ink: var(--card-foundational-ink);
    --card-ink-head: var(--card-foundational-head);
    --card-ink-row-a: var(--card-foundational-row-a);
    --card-ink-row-b: var(--card-foundational-row-b);
    background: linear-gradient(160deg, var(--card-foundational-a), var(--card-foundational-b));
  }

  .restorative {
    --card-ink: var(--card-restorative-ink);
    --card-ink-head: var(--card-restorative-head);
    --card-ink-row-a: var(--card-restorative-row-a);
    --card-ink-row-b: var(--card-restorative-row-b);
    background: linear-gradient(160deg, var(--card-restorative-a), var(--card-restorative-b));
  }

  /* Empty text sits on the first row band, never on the bare gradient. */
  .horizon .empty,
  .foundational .empty,
  .restorative .empty {
    background: var(--card-ink-row-a);
    color: var(--card-ink);
  }
</style>
