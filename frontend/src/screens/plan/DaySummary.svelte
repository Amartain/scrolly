<script lang="ts">
  import MandateMark from '../../components/MandateMark.svelte';
  import Panel from '../../components/Panel.svelte';
  import { view } from '../../lib/view.svelte';

  const budget = $derived(view.planning?.budget);
  const alt = $derived(
    budget?.light_text
      ? `${budget.planned_text} planned, ${budget.light_text} of light left`
      : `${budget?.planned_text ?? ''} planned, the sun has set`,
  );
</script>

{#if budget}
  <Panel title="Day Summary">
    <div class="summary">
      <p class="line">
        <span class="digits">{budget.trial_count}</span> trials ·
        <span class="digits">{budget.planned_text}</span> planned
      </p>
      {#if budget.light_text !== null}
        <p class="muted">
          <span class="digits">{budget.light_text}</span> of light left until sunset
        </p>
        <div class="bar" role="img" aria-label={alt}>
          <MandateMark kind="bar" share={budget.mandate_pct} />
          <span class="mortal" style:width="{budget.mortal_pct}%"></span>
          {#if budget.light_pct < 100}
            <span class="beyond-zone" style:left="{budget.light_pct}%"></span>
          {/if}
        </div>
        <p class="muted">
          {#if budget.beyond_text}
            <span class="digits">{budget.beyond_text}</span> beyond the light. Leave room to breathe.
          {:else}
            &nbsp;
          {/if}
        </p>
      {:else}
        <p class="muted">The sun has set. Rest is part of the path.</p>
      {/if}
      <!-- One reserved line, so a count appearing never moves the panels below. -->
      <p class="muted last">
        {#if budget.unestimated_count > 0}
          <span class="digits">{budget.unestimated_count}</span> without an estimate
        {:else}
          &nbsp;
        {/if}
      </p>
    </div>
  </Panel>
{/if}

<style>
  .summary {
    padding: var(--space-3) var(--space-4);
    font-size: var(--text-body-md);
  }

  p {
    margin: 0;
    margin-bottom: var(--space-2);
  }

  .line {
    font-size: var(--text-body-lg);
  }

  .muted {
    color: var(--ink-muted);
  }

  .bar {
    position: relative;
    display: flex;
    height: var(--size-gauge);
    margin-bottom: var(--space-2);
    overflow: hidden;
    background: var(--inset);
    border: var(--border-width) solid var(--line);
  }

  .mortal {
    display: block;
    height: 100%;
    background: var(--growth);
  }

  .beyond-zone {
    position: absolute;
    top: 0;
    right: 0;
    bottom: 0;
    border-left: var(--border-width) solid var(--line);
    background: repeating-linear-gradient(
      135deg,
      var(--gold) 0 var(--space-1),
      transparent var(--space-1) var(--space-2)
    );
    opacity: 0.55;
  }

  .last {
    margin-bottom: 0;
  }
</style>
