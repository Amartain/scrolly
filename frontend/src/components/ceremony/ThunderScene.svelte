<!-- Tribulation Weathered: the storm gathers over the peak, the bolt strikes the kneeling cultivator,
     and the cultivator rises in golden light. A still picture is the last frame: `still` (reduced
     motion, or a key pressed to skip) shows it without moving. The timing is in
     styles/ceremony-thunder.css. -->
<script lang="ts">
  import Cultivator from './Cultivator.svelte';

  let { still }: { still: boolean } = $props();

  const STAGE = 'translate(-320,0)';
  const RAYS = Array.from({ length: 12 }, (_, i) => i * 30);
  const SPARKLES = [
    [690, 470, 0],
    [930, 500, 120],
    [760, 360, 240],
    [880, 330, 80],
    [640, 560, 200],
    [985, 410, 300],
  ];
  const LEFT = [
    'translate(-90,-30) scale(1.5)',
    'translate(150,90) scale(1.05)',
    'translate(-40,180) scale(1.2)',
  ];
  const RIGHT = [
    'translate(1690,-30) scale(-1.5,1.5)',
    'translate(1450,90) scale(-1.05,1.05)',
    'translate(1640,180) scale(-1.2,1.2)',
  ];
</script>

<svg
  class="thunder-scene"
  class:still
  viewBox="0 0 1600 900"
  preserveAspectRatio="xMidYMid slice"
  aria-hidden="true"
>
  <defs>
    <linearGradient id="ceremony-sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" style:stop-color="var(--scene-sky-top)" />
      <stop offset="0.6" style:stop-color="var(--scene-sky-mid)" />
      <stop offset="1" style:stop-color="var(--scene-sky-low)" />
    </linearGradient>
    <radialGradient id="ceremony-halo">
      <stop offset="0" style:stop-color="var(--scene-gold)" stop-opacity="0.9" />
      <stop offset="0.4" style:stop-color="var(--scene-gold)" stop-opacity="0.35" />
      <stop offset="1" style:stop-color="var(--scene-gold)" stop-opacity="0" />
    </radialGradient>
    <radialGradient id="ceremony-aura">
      <stop offset="0" style:stop-color="var(--scene-bolt)" stop-opacity="0.95" />
      <stop offset="0.45" style:stop-color="var(--scene-gold)" stop-opacity="0.6" />
      <stop offset="1" style:stop-color="var(--scene-gold)" stop-opacity="0" />
    </radialGradient>
  </defs>

  {#snippet cloud()}
    <path
      class="cloud"
      d="M20,140 C-10,140 -10,90 30,88 C30,40 90,20 120,55 C140,10 220,5 240,55 C270,30 330,40 330,90 C380,88 390,140 350,140 Z"
    />
    <path class="curl" d="M150,104 a22,22 0 1,1 22,22 a12,12 0 1,1 -12,-12" />
    <path class="curl" d="M262,108 a16,16 0 1,1 16,16 a8,8 0 1,1 -8,-8" />
  {/snippet}

  <!-- The peak stands in the left third (STAGE), so the card can rise on the right without hiding it. -->
  <g class="shake">
    <rect width="1600" height="900" fill="url(#ceremony-sky)" />
    <path
      class="ridge-far"
      d="M0,640 L180,520 L320,600 L470,470 L640,590 L800,520 L960,600 L1120,480 L1290,590 L1440,510 L1600,580 L1600,900 L0,900 Z"
    />
    <g transform={STAGE}>
      <circle class="halo" cx="800" cy="430" r="560" fill="url(#ceremony-halo)" />
      <g class="rays">
        {#each RAYS as angle (angle)}
          <polygon points="800,430 772,-520 828,-520" transform="rotate({angle} 800 430)" />
        {/each}
      </g>
    </g>
    <path
      class="ridge-near"
      d="M0,770 L200,700 L380,750 L540,705 L620,740 L980,740 L1060,700 L1240,760 L1420,690 L1600,750 L1600,900 L0,900 Z"
    />
    <g transform={STAGE}>
      <path
        class="rock"
        d="M600,900 L645,780 L690,700 L702,650 L898,650 L912,700 L955,790 L1000,900 Z"
      />
      <path class="rock-light" d="M708,654 L760,654 L732,716 L700,770 Z" />
      <circle class="ring" cx="800" cy="520" r="44" />
      <g class="smoke">
        <circle cx="755" cy="610" r="42" />
        <circle cx="845" cy="615" r="48" />
        <circle cx="800" cy="575" r="36" />
      </g>
      <g transform="translate(800,652)"><Cultivator /></g>
    </g>
    <g class="bolt" transform={STAGE}>
      <path
        class="bolt-glow"
        pathLength="1"
        d="M820,-10 L782,120 L846,168 L774,300 L832,334 L798,500"
      />
      <path
        class="bolt-core"
        pathLength="1"
        d="M820,-10 L782,120 L846,168 L774,300 L832,334 L798,500"
      />
      <path class="bolt-fork" pathLength="1" d="M846,168 L930,240 L902,262 L986,338" />
      <path class="bolt-fork" pathLength="1" d="M774,300 L702,356 L728,374 L668,440" />
    </g>
    <g class="clouds-left">
      {#each LEFT as place (place)}<g transform={place}>{@render cloud()}</g>{/each}
    </g>
    <g class="clouds-right">
      {#each RIGHT as place (place)}<g transform={place}>{@render cloud()}</g>{/each}
    </g>
    {#each SPARKLES as [x, y, delay] (`${x},${y}`)}
      <g transform="translate({x - 320},{y})">
        <path
          class="sparkle"
          style:--delay="{delay}ms"
          d="M0,-22 L5,-5 L22,0 L5,5 L0,22 L-5,5 L-22,0 L-5,-5 Z"
        />
      </g>
    {/each}
  </g>
  <rect class="flash" width="1600" height="900" />
</svg>
