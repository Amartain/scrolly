<!-- Enter Seclusion, as a moon gate: a dark lacquer bar with the round gate drawn in gold at its left and the
     garden's light inside it, the words, then the key that opens it (F). The light brightens on hover. -->
<script lang="ts">
  import { SECLUSION } from '../../lib/copy-seclusion';

  let { title, onclick }: { title: string; onclick: () => void } = $props();
</script>

<button
  class="gate"
  type="button"
  aria-label="{SECLUSION.enterNamed}: {title}"
  aria-keyshortcuts="F"
  title="{SECLUSION.enterNamed}: {title}"
  {onclick}
>
  <span class="moon" aria-hidden="true"></span>
  <span class="word display">{SECLUSION.enter}</span>
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
  .gate:focus-visible .moon {
    background-color: color-mix(in srgb, var(--gold) 35%, transparent);
  }

  .word {
    font-size: var(--text-display-sm);
    letter-spacing: 0.15em;
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
