<script lang="ts">
  const PATHS = {
    x: 'M4.5 7.5l3-3 4.5 4.5 4.5-4.5 3 3-4.5 4.5 4.5 4.5-3 3-4.5-4.5-4.5 4.5-3-3 4.5-4.5z',
    arrow: 'M2 9.5h11V4l9 8-9 8v-5.5H2z',
    plus: 'M9.5 3h5v6.5H21v5h-6.5V21h-5v-6.5H3v-5h6.5z',
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
