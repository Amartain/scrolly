<!-- The cultivator, in Han robes: wide sleeves, a long hem, long hair flowing down the back, the bun
     with its crown and pin, two ribbons that sway. `walk` climbs with a staff; `sit` meditates facing
     the peaks. Drawn round the feet (0, 0), facing right. Colours come from the scene's tokens. -->
<script lang="ts">
  let { pose }: { pose: 'walk' | 'sit' } = $props();
</script>

<g class="figure" data-pose={pose}>
  {#if pose === 'sit'}<circle class="aura" cx="0" cy="-32" r="40" />{/if}
  <path
    class="ribbons sway"
    d="M-4,-63 C-12,-66 -19,-61 -27,-64 M-4,-62 C-11,-62 -16,-57 -24,-57"
  />
  {#if pose === 'walk'}
    <path class="staff" d="M14,-60 L18,0" />
    <path
      class="body"
      d="M-6,-46 L7,-46 C9,-30 12,-14 16,0 L-12,0 C-16,-1 -19,-3 -23,-1 C-15,-13 -9,-30 -6,-46 Z"
    />
    <path
      class="body sway"
      d="M-3,-57 C-13,-52 -18,-40 -24,-32 C-27,-28 -31,-27 -35,-28 C-27,-34 -19,-44 -12,-52 C-9,-55 -6,-57 -3,-57 Z"
    />
    <path
      class="body sleeve"
      d="M3,-44 C12,-38 17,-29 16,-20 C11,-18 6,-20 2,-24 C4,-32 4,-38 3,-44 Z"
    />
  {:else}
    <path class="body" d="M-32,0 C-30,-9 -22,-15 -12,-17 L14,-17 C24,-14 31,-7 33,0 Z" />
    <path class="body" d="M-11,-16 C-13,-29 -11,-39 -7,-46 L6,-46 C9,-39 11,-29 12,-16 Z" />
    <path
      class="body sway"
      d="M-3,-57 C-12,-52 -14,-40 -16,-30 C-18,-22 -24,-17 -31,-15 C-23,-22 -17,-31 -13,-41 C-11,-49 -8,-55 -3,-57 Z"
    />
    <path
      class="body sleeve"
      d="M3,-43 C14,-37 21,-27 23,-14 C17,-11 10,-11 3,-16 C6,-25 6,-34 3,-43 Z"
    />
  {/if}
  <circle class="body" cx="1" cy="-53" r="6.5" />
  <ellipse class="body" cx="-1" cy="-61.5" rx="4.5" ry="3.8" />
  <path class="crown" d="M-4,-64 L4,-64 L3,-68 L-3,-68 Z" />
  <path
    class="trim"
    d={pose === 'sit'
      ? 'M-9,-63 L8,-65.5 M-4,-45 L2,-35 L6,-45 M-11,-24 L12,-24'
      : 'M-9,-63 L8,-65.5 M-4,-45 L2,-36 L6,-45 M-7,-30 L9,-30'}
  />
</g>
