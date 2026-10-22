<script lang="ts">
  import type { Qi, QiFill } from '../lib/api';
  import { QI_ZONE } from '../lib/copy-qi';

  // `value` and `fill` are the Qi to show (planned, in Phase 3); `zone` is the stretch it reaches, as
  // Python names it. No legend: the reading names only the zone reached, with its colour beside it.
  let {
    qi,
    value,
    fill,
    zone,
    caption,
  }: { qi: Qi; value: number; fill: QiFill; zone: Qi['planned_zone']; caption: string } = $props();
</script>

<div class="gauge">
  <p class="reading">
    <span class="digits big">{value}</span> Qi {caption}
    <span class="zone"><span class="swatch {zone}"></span>{QI_ZONE[zone]}</span>
  </p>
  <div
    class="track"
    role="meter"
    aria-label="Qi {caption}"
    aria-valuetext="{value} of {qi.redline}. Harmonious to {qi.start}, igniting the blood to {qi.surge_end}, strain to {qi.redline}."
    aria-valuemin={0}
    aria-valuemax={qi.redline}
    aria-valuenow={value}
  >
    <span class="fill calm" style:left="0" style:width="{fill.calm_pct}%"></span>
    <span class="fill surge" style:left="{qi.calm_end_pct}%" style:width="{fill.surge_pct}%"></span>
    <span class="fill redline" style:left="{qi.surge_end_pct}%" style:width="{fill.redline_pct}%"
    ></span>
    <span class="tick" style:left="{qi.calm_end_pct}%"></span>
    <span class="tick" style:left="{qi.surge_end_pct}%"></span>
  </div>
</div>

<style>
  .gauge {
    font-size: var(--text-body-md);
  }

  .reading {
    display: flex;
    align-items: baseline;
    gap: var(--space-2);
    margin: 0;
    margin-bottom: var(--space-2);
  }

  .zone {
    display: inline-flex;
    align-items: center;
    margin-left: auto;
    font-weight: 700;
  }

  .big {
    font-size: var(--text-body-xl);
  }

  .track {
    position: relative;
    height: var(--size-gauge);
    overflow: hidden;
    background: var(--inset);
    border: var(--border-width) solid var(--line);
  }

  .fill {
    position: absolute;
    top: 0;
    bottom: 0;
  }

  .tick {
    position: absolute;
    top: 0;
    bottom: 0;
    border-left: var(--border-width) solid var(--line);
  }

  .calm,
  .harmonious {
    background: var(--qi-calm);
  }

  .surge,
  .igniting {
    background: var(--qi-surge);
  }

  .redline,
  .strain {
    background: var(--qi-redline);
  }

  .swatch {
    display: inline-block;
    width: var(--space-3);
    height: var(--space-3);
    margin-right: var(--space-2);
    border: var(--border-width) solid var(--line);
  }
</style>
