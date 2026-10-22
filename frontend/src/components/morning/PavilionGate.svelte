<!-- The pavilion gate at the heart of the city, wide enough to frame the zero state's title and button in
     its opening: lacquered pillars, two upturned roofs, the plaque 曉 (dawn) on the lintel, a great
     lantern at each eave, and sparks that twinkle over the roof once the city is awake. -->
<svelte:options namespace="svg" />

<script lang="ts">
  const SPARKS = [
    [600, 180, 0],
    [1000, 180, 140],
    [800, 150, 260],
    [470, 250, 380],
    [1130, 250, 200],
  ];
  const EAVES = [450, 1150];
</script>

<g class="gate">
  <rect class="pillar" x="520" y="330" width="40" height="615" />
  <rect class="pillar" x="1040" y="330" width="40" height="615" />
  <rect class="lintel" x="470" y="330" width="660" height="30" />
  <path
    class="roof"
    d="M420,330 Q470,318 495,285 L1105,285 Q1130,318 1180,330 Q1130,310 1120,270 L480,270 Q470,310 420,330 Z"
  />
  <path
    class="roof"
    d="M560,250 Q600,240 612,212 L988,212 Q1000,240 1040,250 Q1000,232 994,200 L606,200 Q600,232 560,250 Z"
  />
  <rect class="plaque" x="765" y="322" width="70" height="44" />
  <text class="plaque-word" x="800" y="355">曉</text>
  {#each EAVES as x (x)}
    <path class="cord" d="M{x},326 v22" />
    <g class="great-lantern">
      <circle class="halo" cx={x} cy="388" r="80" fill="url(#morning-glow)" />
      <ellipse class="body" cx={x} cy="388" rx="30" ry="38" />
      <rect class="cap" x={x - 15} y="346" width="30" height="7" />
      <rect class="cap" x={x - 15} y="423" width="30" height="7" />
    </g>
  {/each}
</g>
{#each SPARKS as [x, y, delay] (`${x},${y}`)}
  <g transform="translate({x},{y})">
    <path
      class="spark"
      style:--delay="{delay}ms"
      d="M0,-18 L4,-4 L18,0 L4,4 L0,18 L-4,4 L-18,0 L-4,-4 Z"
    />
  </g>
{/each}
