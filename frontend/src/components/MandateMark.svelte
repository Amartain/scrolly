<!-- Everything that means "Heavenly Mandate" in crimson: its word and its bar segment (the 🪷 itself is a TypeMark).
     The only component that may use --mandate. -->
<script lang="ts">
  import type { Snippet } from 'svelte';

  let {
    kind = 'term',
    share = 0,
    children,
  }: { kind?: 'bar' | 'term'; share?: number; children?: Snippet } = $props();
</script>

{#if kind === 'bar'}
  <span class="segment" style:width="{share}%" aria-hidden="true"></span>
{:else}
  <span class="term">{@render children?.()}</span>
{/if}

<style>
  .term {
    color: var(--lotus-ink, var(--mandate));
    font-weight: 700;
  }

  .segment {
    display: block;
    height: 100%;
    background: var(--lotus-ink, var(--mandate));
  }
</style>
