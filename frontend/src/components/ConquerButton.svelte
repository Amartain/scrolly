<!-- Conquered!, the button the day is built around: a gold lacquer stamp, the seal 勝 at its left and the
     word beside it, a gold rule inside its edge. Pressed, it sinks like a stamp (the shadow goes, as on
     every button). The accessible name stays "Conquer {title}", so keys and tests find it. -->
<script lang="ts">
  let { title, label, onclick }: { title: string; label: string; onclick: () => void } = $props();
</script>

<button
  class="stamp lacquer-frame"
  type="button"
  aria-label="Conquer {title}"
  title="Conquer {title}"
  {onclick}
>
  <span class="seal read" lang="zh" aria-hidden="true">勝</span>
  <span class="word display">{label}</span>
</button>

<style>
  .stamp {
    --frame-rule: color-mix(in srgb, var(--on-gold) 45%, transparent);
    display: inline-flex;
    align-items: center;
    gap: var(--space-3);
    padding: var(--space-1) var(--space-5) var(--space-1) var(--space-1);
    cursor: pointer;
    background: var(--gold);
    background-image: var(--gloss-btn);
    color: var(--on-gold);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-button);
    white-space: nowrap;
  }

  .stamp:active {
    box-shadow: none;
    transform: translate(var(--shadow-offset), var(--shadow-offset));
  }

  /* The seal: a square of ink with the character in gold, like a stamp's face. */
  .seal {
    display: grid;
    place-items: center;
    width: var(--size-glyph-button);
    height: var(--size-glyph-button);
    background: var(--on-gold);
    color: var(--gold);
    border: var(--border-width) solid var(--line);
    font-size: var(--text-display-md);
    line-height: 1;
  }

  .word {
    font-size: var(--text-display-sm);
    letter-spacing: 0.08em;
  }
</style>
