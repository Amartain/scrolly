<script lang="ts">
  let { label, onclick }: { label: string; onclick: () => void } = $props();
</script>

<button class="button display" {onclick}>{label}</button>

<style>
  .button {
    padding: var(--space-2) var(--space-4);
    cursor: pointer;
    background: var(--btn);
    background-image: var(--gloss-btn);
    color: var(--ink);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-button);
    font-size: var(--text-display-sm);
  }

  .button:active {
    box-shadow: none;
    transform: translate(var(--shadow-offset), var(--shadow-offset));
  }
</style>
