<!-- A square icon button. Its label is the name a screen reader hears and the tip on hover.
     `disabled` dims it but keeps it in the Tab order, so a row of them never changes shape. -->
<script lang="ts">
  import type { Snippet } from 'svelte';

  let {
    label,
    onclick,
    disabled = false,
    id,
    expanded,
    tour,
    children,
  }: {
    label: string;
    onclick: () => void;
    disabled?: boolean;
    id?: string;
    /** For a button that shows or hides something. */
    expanded?: boolean;
    /** The tour's lesson this button teaches (lib/knowledge.svelte.ts). */
    tour?: string;
    children: Snippet;
  } = $props();
</script>

<button
  class="glyph-button"
  type="button"
  {id}
  data-tour={tour}
  aria-label={label}
  aria-expanded={expanded}
  aria-disabled={disabled || undefined}
  title={label}
  onclick={() => !disabled && onclick()}
>
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

  .glyph-button[aria-disabled='true'] {
    color: var(--ink-faint);
    background-image: none;
    box-shadow: none;
    cursor: default;
    transform: none;
  }
</style>
