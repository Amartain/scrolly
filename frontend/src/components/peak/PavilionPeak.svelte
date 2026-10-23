<!-- The Hidden Pavilion behind Seclusion, in the header art's bold language: jagged ranges with thick
     ink outlines, swirl clouds, and a pavilion on the near cliff with two paper lanterns (lit at golden
     hour and dusk). Stone steps zigzag up the cliff to it; the cultivator sits under its roof. Colours
     are the scene's tokens (styles/peak-tokens.css), by variant and phase. The ranges and the cliff go
     on left of the painting's edge, for the header's window. -->
<script lang="ts">
  import { viewBoxFor, type Frame } from '../../lib/peak.svelte';
  import Climber from './Climber.svelte';
  import PavilionCity from './PavilionCity.svelte';
  import PeakSky from './PeakSky.svelte';

  let { frame }: { frame: Frame } = $props();

  // The cliff left of the painting's edge is its own stroke, so the painted one draws as before.
  const LEFT = 'M-700,640 L-520,590 L-380,610 L-220,520 L-90,470 L0,440';
  const CLIFF =
    'M0,440 L78,410 L167,440 L189,455 L383,455 L411,470 L466,540 L505,640 L533,760 L578,900';
  const PATH = 'M200,866 L255,830 L189,770 L278,700 L211,640 L294,575 L250,525 L289,447';
  // The steps drawn end under the pavilion's floor; the cultivator's way ends on top of it.
  const STEPS = 'M200,900 L200,866 L255,830 L189,770 L278,700 L211,640 L294,575 L250,525 L289,460';
  const LANTERNS = [229, 349];

  let at: DOMPoint | undefined = $state();
</script>

<svg
  class="peak-art"
  viewBox={viewBoxFor(frame, at?.y)}
  preserveAspectRatio="xMidYMid slice"
  aria-hidden="true"
>
  <defs>
    <linearGradient id="peak-mist" x1="0" y1="0" x2="0" y2="1">
      <stop class="mist-edge" offset="0" />
      <stop class="mist-core" offset="0.5" />
      <stop class="mist-edge" offset="1" />
    </linearGradient>
  </defs>
  <PeakSky />
  <g class="clouds paint-birds">
    <path
      class="drift"
      d="M900,210 h130 a20,20 0 0 0 0,-40 a26,26 0 0 0 -48,-12 a32,32 0 0 0 -60,14 a19,19 0 0 0 -22,38 z"
    />
    <path
      class="drift slow"
      d="M1250,300 h110 a18,18 0 0 0 0,-36 a24,24 0 0 0 -44,-10 a28,28 0 0 0 -52,12 a17,17 0 0 0 -14,34 z"
    />
  </g>
  <path
    class="far-1 outlined paint-far-1"
    d="M-700,420 L-560,520 L-420,360 L-280,470 L-130,400 L0,560 L133,430 L222,500 L355,330 L466,460 L577,380 L711,520 L844,360 L977,470 L1088,300 L1222,450 L1355,380 L1488,470 L1600,410 L1600,900 L-700,900 Z"
  />
  <g class="mist paint-mist"><rect class="drift" x="-820" y="500" width="2540" height="110" /></g>
  <path
    class="far-2 outlined paint-far-2"
    d="M-700,620 L-520,570 L-360,640 L-180,580 L0,680 L178,560 L311,620 L466,540 L622,640 L777,580 L955,660 L1111,590 L1288,650 L1444,600 L1600,640 L1600,900 L-700,900 Z"
  />
  <path
    class="far-3 outlined paint-far-3"
    d="M-700,760 L-460,720 L-220,770 L0,790 L244,720 L466,760 L711,700 L955,770 L1200,710 L1422,760 L1600,730 L1600,900 L-700,900 Z"
  />
  <PavilionCity part="city" />
  <path class="cliff paint-cliff" d="{LEFT} L{CLIFF.slice(1)} L-700,900 Z" />
  <path class="contour paint-cliff" d={LEFT} />
  <path class="contour paint-contour" d={CLIFF} />
  <path class="trail steps paint-trail" d={STEPS} />
  <PavilionCity part="gate" />
  <g class="pavilion paint-pine">
    <rect class="wood" x="178" y="447" width="222" height="10" />
    <rect class="wood" x="198" y="386" width="10" height="61" />
    <rect class="wood" x="368" y="386" width="10" height="61" />
    <path
      class="wood"
      d="M142,394 C189,392 244,372 289,340 C333,372 389,392 436,394 L413,380 L164,380 Z"
    />
    <path class="wood" d="M258,348 L289,324 L320,348 Z" />
    {#each LANTERNS as x (x)}
      <circle class="lantern-glow" cx={x} cy="410" r="17" />
      <path class="string" d="M{x},392 L{x},400" />
      <rect class="lantern" x={x - 7} y="400" width="14" height="19" rx="5" />
    {/each}
  </g>
  <g class="paint-figure"><Climber path={PATH} scale={1} sitScale={0.95} bind:at /></g>
  <g class="plaque paint-verse" transform="translate(1410,96)">
    <rect width="66" height="132" />
    <text x="33" y="22">閉關</text>
  </g>
</svg>
