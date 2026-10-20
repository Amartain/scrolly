<script lang="ts">
  const PATHS = {
    x: 'M4.5 7.5l3-3 4.5 4.5 4.5-4.5 3 3-4.5 4.5 4.5 4.5-3 3-4.5-4.5-4.5 4.5-3-3 4.5-4.5z',
    arrow: 'M2 9.5h11V4l9 8-9 8v-5.5H2z',
    up: 'M9.5 22V11H4l8-9 8 9h-5.5v11z',
    plus: 'M9.5 3h5v6.5H21v5h-6.5V21h-5v-6.5H3v-5h6.5z',
    minus: 'M3 9.5h18v5H3z',
    play: 'M6 3l14 9-14 9z',
    pause: 'M5 3h5v18H5zM14 3h5v18h-5z',
    reset: 'M13 2L7 6.5l6 4.5V7.6A4.5 4.5 0 1 1 7.6 13H3.6A8.5 8.5 0 1 0 13 3.6z',
    fullscreen: 'M3 3h7v3H6v4H3zM14 3h7v7h-3V6h-4zM3 14h3v4h4v3H3zM18 14h3v7h-7v-3h4z',
  };

  let { name }: { name: keyof typeof PATHS } = $props();
</script>

<svg class="glyph" viewBox="0 0 24 24" aria-hidden="true">
  <path d={PATHS[name]} fill="currentColor" />
</svg>

<style>
  .glyph {
    width: var(--size-glyph);
    height: var(--size-glyph);
  }
</style>
