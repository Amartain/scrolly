<!-- A conquered trial is read-only, but for two things: Revive, and correcting the time it took
     (double-click the time, or Enter on it: a small field with a check mark opens). -->
<script lang="ts">
  import Button from '../../components/Button.svelte';
  import StateMark from '../../components/StateMark.svelte';
  import TypeMark from '../../components/TypeMark.svelte';
  import { putTrialActual } from '../../lib/actual-api';
  import { today, type Conquered } from '../../lib/api';
  import ActualTime from './ActualTime.svelte';
  import { view } from '../../lib/view.svelte';

  let { trial }: { trial: Conquered } = $props();

  const qiOn = $derived(view.planning?.qi.enabled ?? false);
</script>

<StateMark state="done" />
<span class="title read">{trial.title}</span>
<span class="figure digits" data-tour="correct-time" data-tour-on="dblclick">
  <ActualTime
    value={trial.actual_text || '—'}
    title={trial.title}
    onsave={(text) => view.act(() => putTrialActual(trial.id, text))}
  />
</span>
{#if qiOn}
  <span class="figure digits">{trial.qi_text ? `${trial.qi_text} Qi` : '—'}</span>
{/if}
<TypeMark type={trial.type} title={trial.title} />
<Button
  label="Revive"
  tour="revive"
  description="Revive {trial.title}"
  onclick={() => view.act(() => today.revive(trial.id))}
/>

<style>
  .title {
    flex: 1;
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .figure {
    flex: none;
    display: flex;
    justify-content: flex-end;
    color: var(--ink-muted);
    font-size: var(--text-body-md);
    text-align: right;
  }
</style>
