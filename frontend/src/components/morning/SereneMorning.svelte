<!-- The Serene Peak at morning, as a shan shui ink painting: far peaks wash in palest first, the near
     cliff's contour is painted with one stroke, a pine grows from it, mist drifts between the ranges, the
     sun rises behind, two cranes cross, the seal is stamped. Ink, paper and sun come from the theme (at
     dusk the painting is moonlit). The look and timing are in styles/morning-serene*.css. -->
<script lang="ts">
  const MIST = [
    [-200, 515, 900, 60],
    [700, 600, 1100, 70],
    [250, 470, 700, 40],
  ];
  const PADS = [
    [240, 176, 72, 18],
    [302, 272, 60, 16],
    [80, 232, 56, 15],
    [196, 216, 50, 14],
  ];
  const CRANES = ['translate(980,170)', 'translate(1060,205) scale(0.8)'];
  const CLIFF_TOP =
    'M0,420 C40,400 70,380 110,390 C150,400 160,440 200,450 C250,460 270,430 300,450 C340,480 330,560 360,620 C390,680 450,720 470,800';
</script>

<svg
  class="serene-morning"
  viewBox="0 0 1600 900"
  preserveAspectRatio="xMidYMid slice"
  aria-hidden="true"
>
  <defs>
    <filter id="morning-brush">
      <feTurbulence type="fractalNoise" baseFrequency="0.035" numOctaves="2" seed="3" />
      <feDisplacementMap in="SourceGraphic" scale="10" />
    </filter>
    <filter id="morning-grain">
      <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" stitchTiles="stitch" />
      <feColorMatrix values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 0.07 0" />
    </filter>
    <!-- A chop's imprint: rough edges and a speckle where the ink did not take. -->
    <filter id="morning-chop" x="-5%" y="-5%" width="110%" height="110%">
      <feTurbulence
        type="fractalNoise"
        baseFrequency="0.9"
        numOctaves="2"
        seed="7"
        result="noise"
      />
      <feDisplacementMap in="SourceGraphic" in2="noise" scale="3" result="edge" />
      <feColorMatrix
        in="noise"
        values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -2.2 1.95"
        result="speckle"
      />
      <feComposite in="edge" in2="speckle" operator="in" />
    </filter>
    <filter id="morning-mist" x="-20%" y="-100%" width="140%" height="300%">
      <feGaussianBlur stdDeviation="18" />
    </filter>
  </defs>

  <rect class="paper" width="1600" height="900" />
  <circle class="sun" cx="1150" cy="260" r="64" />
  <path
    class="far"
    filter="url(#morning-brush)"
    d="M0,620 C60,600 90,520 120,470 C140,430 170,430 185,470 C200,520 230,560 270,540 C300,520 310,430 340,380 C360,350 395,350 410,395 C430,450 450,520 500,530 C540,540 560,470 590,440 C620,410 650,420 665,470 C690,540 740,560 800,545 C860,530 880,470 910,430 C935,400 965,405 985,450 C1010,510 1040,540 1090,530 C1130,520 1150,450 1180,410 C1205,380 1240,385 1255,430 C1275,490 1300,520 1350,515 C1400,510 1420,470 1450,450 C1490,425 1530,440 1560,480 L1600,500 L1600,900 L0,900 Z"
  />
  <g class="mist">
    {#each MIST as [x, y, width, height] (`${x},${y}`)}
      <rect {x} {y} {width} {height} rx="30" filter="url(#morning-mist)" />
    {/each}
  </g>
  <path
    class="mid"
    filter="url(#morning-brush)"
    d="M0,700 C120,640 200,600 300,620 C380,640 420,560 520,560 C620,560 660,640 760,650 C860,660 900,600 1000,590 C1100,580 1160,650 1260,660 C1360,670 1420,610 1500,600 C1550,595 1580,610 1600,620 L1600,900 L0,900 Z"
  />
  <path
    class="bank"
    filter="url(#morning-brush)"
    d="M900,900 C980,800 1100,760 1250,770 C1380,780 1480,740 1600,720 L1600,900 Z"
  />
  <path class="cliff" filter="url(#morning-brush)" d="{CLIFF_TOP} L480,900 L0,900 Z" />
  <path class="contour" pathLength="1" d={CLIFF_TOP} />
  <g class="pine" filter="url(#morning-brush)">
    <path class="trunk" d="M160,400 C150,340 190,300 170,250 C160,220 190,190 230,180" />
    <path class="branch" d="M172,300 C210,290 250,300 290,280" />
    <path class="branch" d="M175,250 C140,240 110,250 80,240" />
    {#each PADS as [cx, cy, rx, ry] (`${cx},${cy}`)}
      <ellipse {cx} {cy} {rx} {ry} />
    {/each}
  </g>
  <g class="cranes">
    {#each CRANES as place (place)}
      <g transform={place}>
        <g class="crane">
          <path
            class="wings"
            d="M0,0 C-20,-25 -45,-30 -70,-22 C-45,-15 -20,-5 0,0 C20,-5 45,-15 70,-22 C45,-30 20,-25 0,0 Z"
          />
          <path class="neck" d="M0,0 L-34,6" />
          <circle class="head" cx="-36" cy="6" r="4" />
        </g>
      </g>
    {/each}
  </g>
  <!-- Kept inside x 240–1360: on a 4:3 screen the sliced painting shows only that much. -->
  <text class="verse" x="1320" y="110">峰靜心明</text>
  <!-- The seal is stamped: the hand brings it down, it presses, ink spreads a little and it settles. -->
  <g class="seal-stamp" transform="translate(1250,700)">
    <rect class="seal-bloom" width="92" height="92" rx="6" />
    <g class="seal-hand">
      <g class="seal" filter="url(#morning-chop)">
        <rect width="92" height="92" rx="6" />
        <text x="46" y="40">靜</text>
        <text x="46" y="80">峰</text>
      </g>
    </g>
  </g>
  <rect class="grain" width="1600" height="900" filter="url(#morning-grain)" />
</svg>
