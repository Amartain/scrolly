<!-- One release valve of the Parallel sidebar: an inset card with its own header band (capitals, as
     every header), a small mark, and an accent edge so each is told apart at a glance. -->
<script lang="ts">
  import type { Snippet } from 'svelte';
  import GlyphIcon from '../../icons/GlyphIcon.svelte';

  type Icon = 'parallel' | 'brush' | 'bamboo';

  let {
    id,
    title,
    icon,
    accent = 'neutral',
    grow = false,
    children,
  }: {
    id: string;
    title: string;
    icon: Icon;
    /** The edge colour: Parallel Flow is neutral ink (as its timer), Scribe gold, Bamboo green. */
    accent?: 'neutral' | 'gold' | 'growth';
    /** Takes the height the other valves leave. */
    grow?: boolean;
    children: Snippet;
  } = $props();
</script>

<section class="valve {accent}" class:grow {id} aria-label={title}>
  <h2 class="head display gold-foot">
    <span class="icon"><GlyphIcon name={icon} /></span>
    <span class="plaque">{title}</span>
  </h2>
  {@render children()}
</section>

<style>
  .valve {
    --valve-accent: var(--ink);
    flex: none;
    display: flex;
    flex-direction: column;
    min-height: 0;
    background: var(--surface-raised);
    border: var(--border-width) solid var(--line);
    border-left: var(--space-1) solid var(--valve-accent);
    box-shadow: var(--shadow-button);
  }

  .gold {
    --valve-accent: var(--gold);
  }

  .growth {
    --valve-accent: var(--growth);
  }

  .grow {
    flex: 1;
  }

  .head {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    margin: 0;
    padding: var(--space-2) var(--space-3);
    background: var(--head-bg);
    color: var(--head-ink);
    border-bottom: var(--border-width) solid var(--line);
    font-size: var(--text-display-sm);
    font-weight: normal;
  }

  .icon {
    display: flex;
  }
</style>
