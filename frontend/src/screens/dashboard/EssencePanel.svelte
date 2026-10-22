<!-- Essence over Qi, one bar each and no numbers until asked (hover or focus): solid is what is done, a faint
     wash what is planned. Essence carries the sunset as a gold notch; Qi is on the Phase 3 gauge's scale, coloured
     by the zone reached, and shows only with the Golden Core on. Before anything is estimated or spent (Python says
     so), the Essence row is one quiet line. -->
<script lang="ts">
  import GuidanceButton from '../../components/GuidanceButton.svelte';
  import Panel from '../../components/Panel.svelte';
  import type { QiFill } from '../../lib/api';
  import { DASHBOARD } from '../../lib/copy-dashboard';
  import { QI_ZONE } from '../../lib/copy-qi';
  import { view } from '../../lib/view.svelte';
  import BarRow from './essence/BarRow.svelte';

  const essence = $derived(view.current?.dashboard.essence);
  const bar = $derived(view.current?.dashboard.essence_bar);
  const qi = $derived(view.planning?.qi);
  const whole = (fill: QiFill) => fill.calm_pct + fill.surge_pct + fill.redline_pct;
</script>

<Panel title="Essence" bare>
  <div class="rows" class:single={!qi?.enabled}>
    <span class="guide"><GuidanceButton topic="essence" /></span>
    {#if essence?.blank}
      <p class="hint">{DASHBOARD.essenceBlank}</p>
    {:else if essence && bar}
      <BarRow
        label={DASHBOARD.essence}
        done={bar.done_pct}
        plan={bar.plan_pct}
        sunset={bar.sunset_pct}
        tip={DASHBOARD.essenceTip(essence.actual_text, essence.remaining_text, bar.light_text)}
      />
    {/if}
    {#if qi?.enabled}
      <BarRow
        label={DASHBOARD.qi}
        done={whole(qi.spent_fill)}
        plan={whole(qi.planned_fill)}
        tone={qi.spent_zone}
        planTone={qi.planned_zone}
        ticks={[qi.calm_end_pct, qi.surge_end_pct]}
        tip={DASHBOARD.qiTip(qi.spent, qi.start, qi.planned, QI_ZONE[qi.spent_zone])}
      />
    {/if}
  </div>
</Panel>

<style>
  .rows {
    position: relative;
    display: grid;
    align-content: center;
    gap: var(--space-3);
    height: 100%;
    padding: var(--space-2) var(--space-12) var(--space-2) var(--space-4);
  }

  .guide {
    position: absolute;
    top: 50%;
    right: var(--space-4);
    translate: 0 -50%;
  }

  .single {
    --size-tile: var(--size-tile-tall);
  }

  .hint {
    margin: 0;
    color: var(--ink-muted);
  }
</style>
