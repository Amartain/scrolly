<!-- The cultivator on the peak, seen from behind: topknot, wide-sleeved robe, sash and a sword over the
     shoulder. Two poses, drawn at the feet (0, 0): kneeling as the bolt falls, then standing tall in
     the golden aura. The scene's stylesheet (styles/ceremony-thunder.css) moves them. -->
<svelte:options namespace="svg" />

<script lang="ts">
  // A drawing only: no props. The parent places it with a transform.
</script>

<g class="aura" aria-hidden="true">
  <ellipse cx="0" cy="-130" rx="150" ry="210" fill="url(#ceremony-aura)" />
</g>

<g class="kneel">
  <path class="robe" d="M-72,0 C-68,-30 -52,-62 -40,-82 L40,-82 C52,-62 68,-30 72,0 Z" />
  <path class="robe" d="M-40,-82 C-46,-106 -42,-126 -34,-136 L34,-136 C42,-126 46,-106 40,-82 Z" />
  <path
    class="robe"
    d="M-34,-132 C-58,-120 -68,-78 -66,-28 L-46,-26 C-46,-70 -42,-100 -28,-114 Z"
  />
  <path class="robe" d="M34,-132 C58,-120 68,-78 66,-28 L46,-26 C46,-70 42,-100 28,-114 Z" />
  <rect class="sash" x="-38" y="-90" width="76" height="10" />
  <path class="blade" d="M14,-136 L44,-196" />
  <circle class="robe" cx="0" cy="-150" r="19" />
  <circle class="robe" cx="0" cy="-171" r="8" />
</g>

<g class="stand">
  <path class="ribbon" d="M6,-252 C28,-262 44,-246 66,-258 C80,-266 92,-258 104,-266" />
  <path class="robe" d="M-62,0 C-52,-42 -42,-92 -36,-132 L36,-132 C42,-92 52,-42 62,0 Z" />
  <path
    class="robe"
    d="M-36,-132 C-42,-160 -46,-182 -42,-198 L42,-198 C46,-182 42,-160 36,-132 Z"
  />
  <path
    class="robe"
    d="M-42,-196 C-66,-186 -76,-150 -74,-100 L-50,-96 C-52,-138 -48,-164 -38,-176 Z"
  />
  <path class="robe" d="M42,-196 C66,-186 76,-150 74,-100 L50,-96 C52,-138 48,-164 38,-176 Z" />
  <rect class="sash" x="-38" y="-142" width="76" height="12" />
  <path class="sash-tail" d="M10,-130 C14,-100 8,-70 18,-44" />
  <path class="blade" d="M16,-200 L52,-270" />
  <path class="guard" d="M24,-226 L44,-216" />
  <rect class="robe" x="-9" y="-216" width="18" height="18" />
  <circle class="robe" cx="0" cy="-232" r="21" />
  <circle class="robe" cx="0" cy="-256" r="9" />
</g>

<style>
  .robe {
    fill: var(--scene-figure);
    stroke: var(--scene-ink);
    stroke-width: 5;
    stroke-linejoin: round;
  }

  .sash {
    fill: var(--scene-gold-deep);
    stroke: var(--scene-ink);
    stroke-width: 4;
  }

  .blade,
  .guard {
    fill: none;
    stroke: var(--scene-ink);
    stroke-width: 9;
    stroke-linecap: round;
  }

  .sash-tail,
  .ribbon {
    fill: none;
    stroke: var(--scene-gold-deep);
    stroke-width: 5;
    stroke-linecap: round;
  }
</style>
