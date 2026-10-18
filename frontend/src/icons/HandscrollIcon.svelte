<script lang="ts">
  let { size = 56 }: { size?: number } = $props();
</script>

<svg width={size} height={size} viewBox="0 0 24 24" aria-hidden="true" class="icon">
  <path
    d="M5.6 6.2h12.8v11.6H5.6z"
    fill="var(--icon-paper)"
    stroke="var(--icon-line)"
    stroke-width="1.1"
    stroke-linejoin="round"
  />
  <path
    d="M3 4.6c0-.6.5-1 1.1-1h1.4c.6 0 1.1.4 1.1 1v14.8c0 .6-.5 1-1.1 1H4.1c-.6 0-1.1-.4-1.1-1zM17.4 4.6c0-.6.5-1 1.1-1h1.4c.6 0 1.1.4 1.1 1v14.8c0 .6-.5 1-1.1 1h-1.4c-.6 0-1.1-.4-1.1-1z"
    fill="var(--icon-wood)"
    stroke="var(--icon-line)"
    stroke-width="1.1"
    stroke-linejoin="round"
  />
  <path
    d="M4.8 2.4v1.2M4.8 20.4v1.2M19.2 2.4v1.2M19.2 20.4v1.2M7.6 15.4l2.6-3.6 1.6 2 1.4-1.6 2.6 3.2M13.6 8.6c.6-.3 1.2.1 1 .7M15.9 8v2.2"
    fill="none"
    stroke="var(--icon-line)"
    stroke-width="1.1"
    stroke-linecap="round"
    stroke-linejoin="round"
  />
  <path d="M7 7.2h3.6v1H7z" fill="var(--icon-highlight)" />
</svg>

<style>
  .icon {
    filter: drop-shadow(var(--space-1) var(--space-1) 0 var(--icon-shadow));
  }
</style>
