<!-- A find learned: "+1" and one line, just above where it was tried (below it near the top of the
     window), for a moment (the store clears it). It moves nothing and catches no click. -->
<script lang="ts">
  import { KNOWLEDGE } from '../../lib/copy-knowledge';

  let { key, x, top, bottom }: { key: string; x: number; top: number; bottom: number } = $props();

  /** Room above for the note; nearer the top than this, it goes below. */
  const ROOM = 110;
  const below = $derived(top < ROOM);
  const left = $derived(Math.min(Math.max(x, ROOM * 1.5), window.innerWidth - ROOM * 1.5));
</script>

<p
  class="find"
  class:below
  role="status"
  style:left="{left}px"
  style:top="{below ? bottom : top}px"
>
  <span class="plus display">{KNOWLEDGE.plus}</span>
  <span class="name">{KNOWLEDGE.title}</span>
  <span class="line">{KNOWLEDGE.finds[key]}</span>
</p>

<style>
  .find {
    position: fixed;
    z-index: 45;
    display: flex;
    flex-wrap: wrap;
    align-items: baseline;
    column-gap: var(--space-2);
    max-width: var(--size-tour-card);
    margin: 0;
    padding: var(--space-2) var(--space-3);
    background: var(--surface-panel);
    color: var(--ink);
    border: var(--border-width) solid var(--line);
    border-left: var(--space-1) solid var(--gold);
    box-shadow: var(--shadow-card);
    transform: translate(-50%, calc(-100% - var(--space-2)));
    pointer-events: none;
    animation: find-in var(--motion-fast) ease-out both;
  }

  .find.below {
    transform: translate(-50%, var(--space-2));
  }

  .plus {
    color: var(--gold);
    font-size: var(--text-display-md);
  }

  .name {
    color: var(--ink-muted);
    font-size: var(--text-body-sm);
  }

  .line {
    flex-basis: 100%;
    font-size: var(--text-body-md);
  }

  @keyframes find-in {
    from {
      opacity: 0;
    }
  }

  @media (prefers-reduced-motion: reduce) {
    .find {
      animation: none;
    }
  }
</style>
