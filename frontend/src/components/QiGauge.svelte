<script lang="ts">
  import type { Qi } from '../lib/api';

  // `value` is the Qi to show: planned in Phase 3, conquered on the dashboard (step 4).
  let { qi, value, caption }: { qi: Qi; value: number; caption: string } = $props();
</script>

<div class="gauge">
  <p class="reading">
    <span class="digits big">{value}</span> Qi {caption}
  </p>
  <div
    class="track"
    role="meter"
    aria-label="Qi {caption}"
    aria-valuemin={0}
    aria-valuemax={qi.redline}
    aria-valuenow={value}
  >
    <span class="fill calm" style:left="0" style:width="{qi.fill_calm_pct}%"></span>
    <span class="fill surge" style:left="{qi.calm_end_pct}%" style:width="{qi.fill_surge_pct}%"
    ></span>
    <span class="fill redline" style:left="{qi.surge_end_pct}%" style:width="{qi.fill_redline_pct}%"
    ></span>
    <span class="tick" style:left="{qi.calm_end_pct}%"></span>
    <span class="tick" style:left="{qi.surge_end_pct}%"></span>
  </div>
  <ul class="legend">
    <li><span class="swatch calm"></span>Harmonious to {qi.start}</li>
    <li><span class="swatch surge"></span>Igniting the Blood to {qi.surge_end}</li>
    <li><span class="swatch redline"></span>Strain to {qi.redline}</li>
  </ul>
</div>

<style>
  .gauge {
    font-size: var(--text-body-md);
  }

  .reading {
    margin: 0;
    margin-bottom: var(--space-2);
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

  .calm {
    background: var(--qi-calm);
  }

  .surge {
    background: var(--qi-surge);
  }

  .redline {
    background: var(--qi-redline);
  }

  .legend {
    display: flex;
    flex-wrap: wrap;
    gap: var(--space-1) var(--space-4);
    margin: var(--space-2) 0 0;
    padding: 0;
    list-style: none;
    color: var(--ink-muted);
  }

  .swatch {
    display: inline-block;
    width: var(--space-3);
    height: var(--space-3);
    margin-right: var(--space-2);
    border: var(--border-width) solid var(--line);
  }
</style>
