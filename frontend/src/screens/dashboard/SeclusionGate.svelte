<!-- Enter Seclusion, as a moon gate: a dark lacquer bar with the round gate drawn in gold at its left and the
     garden's light inside it, the words, then the key that opens it (F). The light brightens on hover. -->
<script lang="ts">
  import GlyphIcon from '../../icons/GlyphIcon.svelte';
  import type { Immediate } from '../../lib/api';
  import { SECLUSION } from '../../lib/copy-seclusion';
  import { seclusion } from '../../lib/seclusion.svelte';
  import { clockText, useTimerDisplay } from '../../lib/timer.svelte';

  let {
    title,
    onclick,
    live = false,
    beside = null,
  }: {
    title: string;
    onclick: () => void;
    /** The room's run or the trial beside goes on: the gate is lit and says Return. */
    live?: boolean;
    beside?: Immediate | null;
  } = $props();

  // The trial beside comes with the room's state, so it counts from when that arrived.
  const besideTime = useTimerDisplay(
    () => beside?.timer ?? null,
    () => seclusion.receivedAt,
  );
  const word = $derived(live ? SECLUSION.returnTo : SECLUSION.enter);
</script>

<button
  class="gate"
  class:live
  type="button"
  aria-label="{live ? SECLUSION.returnTo : SECLUSION.enterNamed}: {title}"
  aria-keyshortcuts="F ArrowUp"
  data-tour="seclusion"
  data-tour-on="commit"
  title="{live ? SECLUSION.returnTo : SECLUSION.enterNamed}: {title}"
  {onclick}
>
  <span class="moon" aria-hidden="true"></span>
  <span class="word display"
    >{word}{#if beside}<span class="beside"
        ><GlyphIcon name="switch" />{beside.title} · {clockText(besideTime.seconds)}</span
      >{/if}</span
  >
  <kbd class="key display" aria-hidden="true">F</kbd>
</button>

<style>
  .gate {
    display: grid;
    grid-template-columns: auto minmax(0, 1fr) auto;
    align-items: center;
    gap: var(--space-4);
    padding: var(--space-1) var(--space-3);
    cursor: pointer;
    background: var(--strong);
    background-image: var(--gloss-btn);
    color: var(--on-strong);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-button);
  }

  .gate:active {
    box-shadow: none;
    transform: translate(var(--shadow-offset), var(--shadow-offset));
  }

  /* The gate: a round opening in the dark wall, ringed in gold, with the garden's light inside. */
  .moon {
    width: var(--size-glyph-button);
    aspect-ratio: 1;
    border: var(--border-width) solid var(--gold);
    border-radius: 50%;
    background-image: radial-gradient(
      circle,
      color-mix(in srgb, var(--gold) 75%, transparent),
      color-mix(in srgb, var(--gold) 20%, transparent) 60%,
      transparent 75%
    );
    transition: background-color 150ms;
  }

  .gate:hover .moon,
  .gate:focus-visible .moon,
  .gate.live .moon {
    background-color: color-mix(in srgb, var(--gold) 35%, transparent);
  }

  .word {
    display: flex;
    align-items: baseline;
    gap: var(--space-4);
    min-width: 0;
    font-size: var(--text-display-sm);
    letter-spacing: 0.15em;
  }

  /* The trial run beside: one quiet line, its own time still counting. */
  .beside {
    display: flex;
    align-items: center;
    gap: var(--space-1);
    min-width: 0;
    overflow: hidden;
    color: var(--gold);
    font-size: var(--text-body-sm);
    letter-spacing: normal;
    white-space: nowrap;
    text-overflow: ellipsis;
  }

  .beside :global(.glyph) {
    flex: none;
    width: 1em;
    height: 1em;
  }

  .key {
    padding-inline: var(--space-2);
    color: var(--gold);
    border: var(--border-width) solid var(--gold);
    box-shadow: var(--shadow-sunken);
    font-size: var(--text-body-sm);
  }

  @media (prefers-reduced-motion: reduce) {
    .moon {
      transition: none;
    }
  }
</style>
