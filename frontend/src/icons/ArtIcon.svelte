<script lang="ts">
  let { kind }: { kind: 'foundational' | 'restorative' } = $props();
</script>

<svg class="icon" viewBox="0 0 24 24" aria-hidden="true">
  {#if kind === 'foundational'}
    <path d="M5.6 6.2h12.8v11.6H5.6z" fill="var(--icon-paper)" />
    <path
      d="M3 4.6c0-.6.5-1 1.1-1h1.4c.6 0 1.1.4 1.1 1v14.8c0 .6-.5 1-1.1 1H4.1c-.6 0-1.1-.4-1.1-1zM17.4 4.6c0-.6.5-1 1.1-1h1.4c.6 0 1.1.4 1.1 1v14.8c0 .6-.5 1-1.1 1h-1.4c-.6 0-1.1-.4-1.1-1z"
      fill="var(--icon-wood)"
    />
    <path
      d="M4.8 2.4v1.2M4.8 20.4v1.2M19.2 2.4v1.2M19.2 20.4v1.2M7.6 15.4l2.6-3.6 1.6 2 1.4-1.6 2.6 3.2M13.6 8.6c.6-.3 1.2.1 1 .7M15.9 8v2.2"
      fill="none"
      stroke="var(--icon-line)"
      stroke-width="1.2"
      stroke-linecap="round"
    />
    <path d="M7 7.2h3.6v1H7z" fill="var(--icon-highlight)" />
  {:else}
    <path
      d="M11.4 15.3C6.6 15.8 3.3 13 3.3 7.6c5.2-.4 8.2 2.7 8.1 7.7zM12.9 12.8c-.2-5 2.6-8.3 7.9-8.4.1 5.2-2.7 8.5-7.9 8.4zM12.1 17.6c3.1-.4 5.4.9 6.5 3.1-3.1.6-5.4-.5-6.5-3.1z"
      fill="var(--icon-sprig)"
    />
    <path
      d="M12.2 21.4c-.4-4.4-.6-8.6.1-12.6M5.6 9.8c1.8 1.4 3.6 3 5.4 5.2M18.4 6.6c-1.6 1.6-3.4 3.6-5.2 5.8"
      fill="none"
      stroke="var(--icon-line)"
      stroke-width="1.2"
      stroke-linecap="round"
    />
    <path
      d="M5 9c1.3.2 2.5.8 3.4 1.7-1.2-.4-2.2-.8-3.4-1.7zM15.5 6.2c1-.6 2.1-.9 3.2-.9-1 .5-2 .9-3.2.9z"
      fill="var(--icon-highlight)"
    />
  {/if}
</svg>

<style>
  .icon {
    flex: none;
    width: var(--size-icon);
    height: var(--size-icon);
    filter: var(--icon-drop);
  }
</style>
