<script lang="ts">
  import type { Snippet } from 'svelte';

  let {
    label,
    pressed,
    onclick,
    children,
  }: { label: string; pressed?: boolean; onclick: () => void; children: Snippet } = $props();
</script>

<button class="icon-button" aria-label={label} aria-pressed={pressed} {onclick}>
  {@render children()}
</button>

<style>
  .icon-button {
    display: flex;
    align-items: center;
    justify-content: center;
    width: var(--size-icon-button);
    cursor: pointer;
    background: var(--entry-settings-bg);
    color: var(--entry-settings-ink);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-button);
  }

  .icon-button:active,
  .icon-button[aria-pressed='true'] {
    box-shadow: none;
    transform: translate(var(--shadow-offset), var(--shadow-offset));
  }
</style>
