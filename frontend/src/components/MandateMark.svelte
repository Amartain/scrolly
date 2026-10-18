<!-- Everything that means "Heavenly Mandate" in crimson: the lotus, its word and its bar segment.
     The only component that may use --mandate. -->
<script lang="ts">
  import type { Snippet } from 'svelte';

  let {
    kind = 'icon',
    share = 0,
    children,
  }: { kind?: 'icon' | 'bar' | 'term'; share?: number; children?: Snippet } = $props();
</script>

{#if kind === 'bar'}
  <span class="segment" style:width="{share}%" aria-hidden="true"></span>
{:else if kind === 'term'}
  <span class="term">{@render children?.()}</span>
{:else}
  <!-- A pointed brush-painted lotus. Original drawing. -->
  <svg class="mark" viewBox="0 0 24 24" role="img" aria-label="Heavenly Mandate">
    <g
      fill="var(--lotus-ink, var(--mandate))"
      stroke="var(--icon-line)"
      stroke-width="1.5"
      stroke-linejoin="round"
    >
      <path d="M10.4 17.6C6.6 19 3 17.6 1.6 13.8c3.4-.6 6.8.6 8.8 3.8z" />
      <path d="M13.6 17.6c3.8 1.4 7.4 0 8.8-3.8-3.4-.6-6.8.6-8.8 3.8z" />
      <path d="M10.8 16.8C6.8 15.6 4.4 12 4.2 8c3.4.6 6.2 3.6 6.6 8.8z" />
      <path d="M13.2 16.8c4-1.2 6.4-4.8 6.6-8.8-3.4.6-6.2 3.6-6.6 8.8z" />
      <path d="M12 2.8C9.2 6 8.8 10.8 12 17c3.2-6.2 2.8-11 0-14.2z" />
    </g>
    <path
      d="M3 21c3.2 1.2 14.8 1.2 18 0"
      fill="none"
      stroke="var(--icon-line)"
      stroke-width="1.5"
      stroke-linecap="round"
    />
    <path
      d="M11.2 7.2c.2-1 .5-1.8.8-2.4.3.7.5 1.6.5 2.6-.5-.1-.9-.2-1.3-.2z"
      fill="var(--icon-highlight)"
    />
  </svg>
{/if}

<style>
  .mark {
    flex: none;
    width: var(--size-icon);
    height: var(--size-icon);
    filter: var(--icon-drop);
  }

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
