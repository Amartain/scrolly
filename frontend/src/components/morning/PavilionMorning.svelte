<!-- The Hidden Pavilion at dawn, in the header art's bold language: the skyline rises, windows light up in a
     cascade, lanterns ignite one by one along their wire and sway once, the gate's great lantern glows,
     the sky warms. Lanterns only, no neon (owner, 2026-10-22). Colours are mixed from the theme's own
     canvas, so teal, crimson and purple each have their own dawn. Timing: styles/morning-pavilion.css. -->
<script lang="ts">
  import PavilionGate from './PavilionGate.svelte';

  type Tower = { x: number; y: number; width: number; cols: number; rows: number; delay: number };

  const TOWERS: Tower[] = [
    { x: 110, y: 330, width: 230, cols: 4, rows: 9, delay: 200 },
    { x: 380, y: 480, width: 150, cols: 3, rows: 6, delay: 350 },
    { x: 1070, y: 440, width: 160, cols: 3, rows: 7, delay: 300 },
    { x: 1250, y: 280, width: 240, cols: 4, rows: 10, delay: 150 },
  ];
  const WINDOW = { width: 24, height: 30, gapX: 28, gapY: 24, inset: 30 };

  // Each window gets its own moment in a cascade, spread pseudo-randomly so the city wakes unevenly.
  const windows = TOWERS.flatMap((tower, t) =>
    Array.from({ length: tower.cols * tower.rows }, (_, i) => {
      const col = i % tower.cols;
      const row = Math.floor(i / tower.cols);
      return {
        key: `${t}-${i}`,
        x: tower.x + WINDOW.inset + col * (WINDOW.width + WINDOW.gapX),
        y: tower.y + WINDOW.inset + row * (WINDOW.height + WINDOW.gapY),
        delay: 800 + ((i * 37 + t * 211) % 1400),
        // One window in five stays dark: a city where everyone is awake looks painted, not lived in.
        off: (i * 7 + t * 3) % 5 === 0,
      };
    }),
  );

  // Lanterns hang along one wire (a quadratic curve) high across the sky; the gate's roof hides its
  // middle, so none hang there.
  const WIRE = [
    [80, 150],
    [800, 300],
    [1520, 150],
  ];
  const lanterns = [0.1, 0.22, 0.34, 0.66, 0.78, 0.9].map((t, i) => {
    const [[x0, y0], [x1, y1], [x2, y2]] = WIRE;
    const at = (a: number, b: number, c: number) =>
      (1 - t) ** 2 * a + 2 * (1 - t) * t * b + t ** 2 * c;
    return { x: at(x0, x1, x2), y: at(y0, y1, y2), delay: 900 + i * 170 };
  });
  const STARS = [
    [140, 120],
    [420, 70],
    [700, 150],
    [980, 60],
    [1210, 140],
    [1480, 90],
  ];
</script>

<svg
  class="pavilion-morning"
  viewBox="0 0 1600 900"
  preserveAspectRatio="xMidYMid slice"
  aria-hidden="true"
>
  <defs>
    <linearGradient id="morning-night" x1="0" y1="0" x2="0" y2="1">
      <stop
        offset="0"
        style:stop-color="color-mix(in srgb, var(--surface-canvas) 22%, var(--scene-ink))"
      />
      <stop
        offset="1"
        style:stop-color="color-mix(in srgb, var(--surface-canvas) 70%, var(--scene-ink))"
      />
    </linearGradient>
    <linearGradient id="morning-dawn" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0.35" style:stop-color="var(--gold)" stop-opacity="0" />
      <stop offset="1" style:stop-color="var(--morning-lantern)" stop-opacity="0.85" />
    </linearGradient>
    <radialGradient id="morning-glow">
      <stop offset="0" style:stop-color="var(--gold)" stop-opacity="0.8" />
      <stop offset="1" style:stop-color="var(--gold)" stop-opacity="0" />
    </radialGradient>
  </defs>

  <rect width="1600" height="900" fill="url(#morning-night)" />
  <rect class="dawn" width="1600" height="900" fill="url(#morning-dawn)" />
  {#each STARS as [cx, cy] (`${cx},${cy}`)}
    <circle class="star" {cx} {cy} r="3" />
  {/each}
  <path
    class="skyline"
    d="M0,900 L0,560 L80,560 L80,500 L150,500 L150,540 L230,540 L230,430 L300,430 L300,520 L380,520 L380,470 L470,470 L470,560 L1130,560 L1130,480 L1200,480 L1200,410 L1280,410 L1280,500 L1350,500 L1350,450 L1440,450 L1440,530 L1520,530 L1520,480 L1600,480 L1600,900 Z"
  />
  {#each TOWERS as tower (tower.x)}
    <g class="tower" style:--delay="{tower.delay}ms">
      <rect x={tower.x} y={tower.y} width={tower.width} height={900 - tower.y} />
      <path class="antenna" d="M{tower.x + tower.width / 2},{tower.y} v-40" />
    </g>
  {/each}
  <g class="windows">
    {#each windows as w (w.key)}
      <rect
        x={w.x}
        y={w.y}
        width={WINDOW.width}
        height={WINDOW.height}
        class:off={w.off}
        style:--delay="{w.delay}ms"
      />
    {/each}
  </g>
  <path class="wire" d="M80,150 Q800,300 1520,150" />
  {#each lanterns as lantern (lantern.x)}
    <g transform="translate({lantern.x},{lantern.y})">
      <g class="lantern" style:--delay="{lantern.delay}ms">
        <path class="cord" d="M0,0 v14" />
        <circle class="halo" cy="38" r="40" fill="url(#morning-glow)" />
        <ellipse class="body" cy="38" rx="16" ry="20" />
        <rect class="cap" x="-9" y="14" width="18" height="6" />
        <rect class="cap" x="-9" y="56" width="18" height="6" />
      </g>
    </g>
  {/each}
  <!-- Lifted so its lintel clears the title, which sits in the gate's opening. -->
  <g transform="translate(0,-45)"><PavilionGate /></g>
</svg>
