<script lang="ts">
  import Panel from '../../components/Panel.svelte';
  import QiGauge from '../../components/QiGauge.svelte';
  import { view } from '../../lib/view.svelte';

  const essence = $derived(view.current?.dashboard.essence);
  const qi = $derived(view.planning?.qi);
</script>

<Panel title="Essence">
  {#if essence}
    <div class="essence">
      <span class="figure digits">{essence.actual_text} / {essence.expected_text}</span>
      <div
        class="meter"
        role="meter"
        aria-label="Essence conquered"
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={essence.meter_pct}
      >
        <span class="fill" style:width="{essence.meter_pct}%"></span>
      </div>
      <span class="label display">Remaining</span>
      <span class="figure digits">{essence.remaining_text}</span>
      {#if qi?.enabled}
        <div class="qi">
          <QiGauge {qi} value={qi.spent} fill={qi.spent_fill} caption="conquered today" compact />
        </div>
      {/if}
    </div>
  {/if}
</Panel>

<style>
  .essence {
    display: flex;
    align-items: center;
    gap: var(--space-4);
    padding: var(--space-1) var(--space-4);
  }

  .figure {
    color: var(--num-text);
    font-size: var(--text-body-md);
    white-space: nowrap;
  }

  .label {
    font-size: var(--text-display-sm);
    white-space: nowrap;
  }

  .meter {
    flex: 1;
    min-width: var(--space-8);
    height: var(--size-gauge);
    position: relative;
    overflow: hidden;
    background: var(--surface-raised);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-sunken);
  }

  .fill {
    position: absolute;
    inset: 0 auto 0 0;
    background: var(--gold);
    background-image: var(--gloss);
  }

  .qi {
    flex: none;
    width: var(--size-qi-gauge);
  }
</style>
