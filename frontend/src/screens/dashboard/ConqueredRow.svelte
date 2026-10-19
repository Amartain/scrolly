<!-- A conquered trial is read-only. The one thing to do with it is Revive. -->
<script lang="ts">
  import Button from '../../components/Button.svelte';
  import StateMark from '../../components/StateMark.svelte';
  import TypeMark from '../../components/TypeMark.svelte';
  import { today, type Conquered } from '../../lib/api';
  import { view } from '../../lib/view.svelte';

  let { trial }: { trial: Conquered } = $props();

  const qiOn = $derived(view.planning?.qi.enabled ?? false);
</script>

<StateMark state="done" />
<span class="title read">{trial.title}</span>
<span class="figure digits">{trial.actual_text || '—'}</span>
{#if qiOn}
  <span class="figure digits">{trial.qi_text ? `${trial.qi_text} Qi` : '—'}</span>
{/if}
<TypeMark type={trial.type} title={trial.title} />
<Button
  label="Revive"
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
    color: var(--ink-muted);
    font-size: var(--text-body-md);
    text-align: right;
  }
</style>
