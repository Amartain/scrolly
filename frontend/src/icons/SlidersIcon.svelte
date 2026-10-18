<script lang="ts">
  let { size = 26 }: { size?: number } = $props();
</script>

<svg width={size} height={size} viewBox="0 0 24 24" aria-hidden="true">
  <path d="M2 5h20v3H2zM2 16h20v3H2zM14 2h4v9h-4zM6 13h4v9H6z" fill="currentColor" />
</svg>
