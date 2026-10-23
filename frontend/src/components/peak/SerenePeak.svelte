<!-- The Serene Peak behind Seclusion, as a shan shui ink painting: far ranges washed in back to front,
     mist between them, two cranes, and the near cliff where a pine leans over a ledge. The path climbs
     the cliff to that ledge, where the cultivator sits facing the peaks. 閉關, closed-door seclusion,
     and a seal on the right. Colours are the scene's tokens (styles/peak-tokens.css), by phase. -->
<script lang="ts">
  import Climber from './Climber.svelte';
  import PeakSky from './PeakSky.svelte';

  const CLIFF =
    'M0,470 C67,450 122,430 189,445 C244,458 267,500 322,506 C378,512 422,500 455,530 C500,570 489,650 522,720 C555,790 600,850 622,900';
  const PATH =
    'M200,866 C222,830 178,800 233,776 C300,742 244,700 311,662 C378,626 322,590 367,556 C389,538 396,520 408,507';
  const PADS = [
    [251, 366, 60, 16],
    [376, 418, 44, 13],
    [207, 404, 40, 12],
  ] as const;
</script>

<svg
  class="peak-art"
  viewBox="0 0 1600 900"
  preserveAspectRatio="xMidYMid slice"
  aria-hidden="true"
>
  <defs>
    <filter id="peak-brush">
      <feTurbulence type="fractalNoise" baseFrequency="0.035" numOctaves="2" seed="5" />
      <feDisplacementMap in="SourceGraphic" scale="8" />
    </filter>
    <linearGradient id="peak-mist" x1="0" y1="0" x2="0" y2="1">
      <stop class="mist-edge" offset="0" />
      <stop class="mist-core" offset="0.5" />
      <stop class="mist-edge" offset="1" />
    </linearGradient>
  </defs>
  <PeakSky />
  <path
    class="far-1 paint-far-1"
    filter="url(#peak-brush)"
    d="M0,520 C130,470 220,380 330,300 C400,250 440,300 500,340 C580,400 620,330 710,262 C780,212 845,252 910,320 C1000,400 1065,330 1155,272 C1220,232 1280,282 1345,330 C1430,392 1510,352 1600,312 L1600,900 L0,900 Z"
  />
  <g class="mist paint-mist"><rect class="drift" x="-120" y="470" width="1840" height="130" /></g>
  <path
    class="far-2 paint-far-2"
    filter="url(#peak-brush)"
    d="M0,600 C155,560 290,500 420,520 C530,536 620,470 755,432 C865,402 955,460 1065,470 C1200,482 1290,420 1420,440 C1510,452 1555,480 1600,470 L1600,900 L0,900 Z"
  />
  <path
    class="far-3 paint-far-3"
    filter="url(#peak-brush)"
    d="M0,720 C220,660 400,640 580,680 C735,714 865,640 1045,622 C1200,606 1330,660 1465,650 C1530,645 1575,660 1600,660 L1600,900 L0,900 Z"
  />
  <g class="mist paint-mist"
    ><rect class="drift slow" x="-120" y="690" width="1840" height="120" /></g
  >
  <g class="birds paint-birds">
    <path d="M1000,150 Q1018,134 1033,150 Q1049,134 1066,150" />
    <path d="M1075,190 Q1088,179 1100,190 Q1111,179 1124,190" />
  </g>
  <path class="cliff paint-cliff" filter="url(#peak-brush)" d="{CLIFF} L0,900 Z" />
  <path class="contour paint-contour" d={CLIFF} />
  <path class="trail paint-trail" d={PATH} />
  <g class="pine paint-pine" filter="url(#peak-brush)">
    <path class="trunk" d="M333,506 C329,470 302,450 291,420 C284,396 267,380 251,372" />
    <path class="branch" d="M296,432 C322,422 344,420 371,424" />
    {#each PADS as [cx, cy, rx, ry] (`${cx},${cy}`)}<ellipse {cx} {cy} {rx} {ry} />{/each}
  </g>
  <g class="paint-figure"><Climber path={PATH} scale={1.1} sitScale={1.4} /></g>
  <text class="verse paint-verse" x="1440" y="110">閉關</text>
  <g class="seal paint-seal" transform="translate(1416,250)">
    <rect width="50" height="50" rx="4" />
    <text x="25" y="36">靜</text>
  </g>
</svg>
