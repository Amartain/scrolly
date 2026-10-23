<!-- The sky over the peak: a wash from the top down, stars at dusk, and the sun or the moon where Python
     says it stands (view.sky, the same as the old arc in the top bar): it rises from behind the left
     ranges, crosses high over the room and sets on the right. It moves a step with each minute's view. -->
<script lang="ts">
  import { view } from '../../lib/view.svelte';

  const STARS = [
    [140, 90, 2],
    [470, 60, 1.6],
    [690, 150, 2.2],
    [950, 70, 1.6],
    [1090, 230, 2],
    [1400, 110, 1.8],
    [1530, 270, 2.2],
    [330, 240, 1.5],
    [820, 260, 1.4],
    [-420, 120, 1.8],
    [-200, 60, 1.6],
    [-60, 210, 2],
  ] as const;

  const sky = $derived(view.current?.sky);
  // A quadratic curve from (260, 520) over (800, -280) to (1340, 520): high at midday, low at the ends.
  const along = (t: number, a: number, b: number, c: number) =>
    (1 - t) ** 2 * a + 2 * (1 - t) * t * b + t ** 2 * c;
  const t = $derived(sky?.progress ?? 0.3);
  const x = $derived(along(t, 260, 800, 1340));
  const y = $derived(along(t, 520, -280, 520));
</script>

<defs>
  <linearGradient id="peak-sky" x1="0" y1="0" x2="0" y2="1">
    <stop class="sky-top" offset="0" />
    <stop class="sky-low" offset="1" />
  </linearGradient>
</defs>
<rect class="sky paint-sky" x="-700" width="2300" height="900" fill="url(#peak-sky)" />
<g class="stars paint-sky">
  {#each STARS as [cx, cy, r] (`${cx},${cy}`)}<circle {cx} {cy} {r} />{/each}
</g>
<g class="paint-sun" data-body={sky?.body ?? 'sun'}>
  <circle class="halo" cx={x} cy={y} r="100" />
  <circle class="sun" cx={x} cy={y} r="62" />
</g>
