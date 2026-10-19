<script lang="ts">
  import type { Snippet } from 'svelte';

  let { label, onclick, children }: { label: string; onclick: () => void; children: Snippet } =
    $props();
</script>

<button class="glyph-button" type="button" aria-label={label} title={label} {onclick}>
  {@render children()}
</button>

<style>
  .glyph-button {
    flex: none;
    display: flex;
    align-items: center;
    justify-content: center;
    width: var(--size-glyph-button);
    height: var(--size-glyph-button);
    padding: 0;
    cursor: pointer;
    background: var(--btn);
    background-image: var(--gloss-btn);
    color: var(--glyph-ink, var(--ink));
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-button);
  }

  .glyph-button:active {
    box-shadow: none;
    transform: translate(var(--shadow-offset), var(--shadow-offset));
  }
</style>
