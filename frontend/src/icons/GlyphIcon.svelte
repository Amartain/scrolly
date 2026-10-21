<script lang="ts">
  const PATHS = {
    x: 'M4.5 7.5l3-3 4.5 4.5 4.5-4.5 3 3-4.5 4.5 4.5 4.5-3 3-4.5-4.5-4.5 4.5-3-3 4.5-4.5z',
    arrow: 'M2 9.5h11V4l9 8-9 8v-5.5H2z',
    up: 'M9.5 22V11H4l8-9 8 9h-5.5v11z',
    plus: 'M9.5 3h5v6.5H21v5h-6.5V21h-5v-6.5H3v-5h6.5z',
    minus: 'M3 9.5h18v5H3z',
    speaker: 'M3 9h4l5-4v14l-5-4H3zM15 9h2v6h-2zM19 6h2v12h-2z',
    muted:
      'M3 9h4l5-4v14l-5-4H3zM15.5 9.5l1.5-1.5 2 2 2-2 1.5 1.5-2 2 2 2-1.5 1.5-2-2-2 2-1.5-1.5 2-2z',
    play: 'M6 3l14 9-14 9z',
    pause: 'M5 3h5v18H5zM14 3h5v18h-5z',
    reset: 'M13 2L7 6.5l6 4.5V7.6A4.5 4.5 0 1 1 7.6 13H3.6A8.5 8.5 0 1 0 13 3.6z',
    fullscreen: 'M3 3h7v3H6v4H3zM14 3h7v7h-3V6h-4zM3 14h3v4h4v3H3zM18 14h3v7h-7v-3h4z',
    switch: 'M2 5h13V2l7 4.5-7 4.5V8H2zM22 16H9v-3l-7 4.5L9 22v-3h13z',
    back: 'M3 3h4v18H3zM21 3v18L8 12z',
    skip: 'M3 3l13 9-13 9zM17 3h4v18h-4z',
    stop: 'M4 4h16v16H4z',
    sidebar: 'M2 3h20v18H2zM4 5v14h10V5z',
    parallel: 'M2 4h13V1l7 5-7 5V8H2zM2 16h13v-3l7 5-7 5v-3H2z',
    brush:
      'M20.5 2L22 3.5 11 14.5 9.5 13zM8.5 14l1.5 1.5c0 3-2.5 6.5-8 6.5 2-1.5 2-3.5 2.5-5S6.5 14 8.5 14z',
    bamboo:
      'M9 2h4v5H9zM9 8h4v6H9zM9 15h4v7H9zM13 9c3-3 6-4 9-4-1 3-4 5-9 6zM9 17c-3 0-6-2-7-5 3 0 6 1 7 3z',
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
