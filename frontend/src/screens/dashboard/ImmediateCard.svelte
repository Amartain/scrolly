<script lang="ts">
  import EditableText from '../../components/EditableText.svelte';
  import Panel from '../../components/Panel.svelte';
  import QiField from '../../components/QiField.svelte';
  import StateMark from '../../components/StateMark.svelte';
  import TypeMark from '../../components/TypeMark.svelte';
  import { today, type Immediate } from '../../lib/api';
  import { view } from '../../lib/view.svelte';
  import TimerControls from './TimerControls.svelte';

  let { trial }: { trial: Immediate } = $props();

  const qiOn = $derived(view.planning?.qi.enabled ?? false);
  const meta = $derived(
    [
      trial.expected_text ? `Expected ${trial.expected_text}` : 'No estimate',
      view.current?.legend.types[trial.type]?.label,
      trial.has_note ? '1 note' : '',
    ]
      .filter(Boolean)
      .join(' · '),
  );

  const rename = (title: string) => view.act(() => today.update(trial.id, { title }));
  const setQi = (qi: string) => view.act(() => today.update(trial.id, { qi }));
  const toggleMandate = () =>
    view.act(() => today.update(trial.id, { is_mandate: !trial.is_mandate }));
</script>

<Panel title="The Immediate Trial" scroll>
  <div class="card">
    <div class="top">
      <span class="mark"><StateMark state="immediate" /></span>
      <div class="text">
        <span class="title"
          ><EditableText value={trial.title} label="Trial title" onsave={rename} /></span
        >
        <span class="meta">{meta}</span>
      </div>
      {#if qiOn}
        <QiField
          value={trial.qi_text}
          label="Qi expected of {trial.title}"
          restores={trial.type === 'restorative'}
          onsave={setQi}
        />
      {/if}
      <span class="mark"
        ><TypeMark type={trial.type} title={trial.title} onToggle={toggleMandate} /></span
      >
    </div>
    <TimerControls {trial} />
  </div>
</Panel>

<style>
  .card {
    display: flex;
    flex-direction: column;
    gap: var(--space-3);
    padding: var(--space-3) var(--space-4);
  }

  .top {
    display: flex;
    align-items: center;
    gap: var(--space-4);
  }

  .mark {
    --size-icon: var(--size-icon-large);
    display: flex;
  }

  .text {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
    gap: var(--space-1);
  }

  .title {
    --editable-size: var(--text-read-lg);
    display: flex;
    color: var(--ink);
    line-height: 1.1;
  }

  .meta {
    color: var(--ink-muted);
    font-size: var(--text-body-sm);
  }
</style>
