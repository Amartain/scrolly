<script lang="ts">
  import EditableText from '../../components/EditableText.svelte';
  import Panel from '../../components/Panel.svelte';
  import SetOnce from '../../components/SetOnce.svelte';
  import StateMark from '../../components/StateMark.svelte';
  import TypeMark from '../../components/TypeMark.svelte';
  import Button from '../../components/Button.svelte';
  import { today, type Immediate } from '../../lib/api';
  import { SECLUSION } from '../../lib/copy-seclusion';
  import { view } from '../../lib/view.svelte';
  import TimerControls from './TimerControls.svelte';

  let { trial, onseclusion }: { trial: Immediate; onseclusion?: () => void } = $props();

  const qiOn = $derived(view.planning?.qi.enabled ?? false);
  const meta = $derived(
    [view.current?.legend.types[trial.type]?.label].filter(Boolean).join(' · '),
  );

  const rename = (title: string) => view.act(() => today.update(trial.id, { title }));
  const setQi = (qi: string) => view.act(() => today.update(trial.id, { qi }));
  const setEstimate = (estimate: string) => view.act(() => today.update(trial.id, { estimate }));
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
      <SetOnce
        kind="time"
        confirm="Set the time for {trial.title}"
        value={trial.expected_text}
        label="Estimate for {trial.title}"
        onsave={setEstimate}
      />
      {#if qiOn}
        <SetOnce
          kind="qi"
          confirm="Set the Qi for {trial.title}"
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
    {#if onseclusion}
      <div class="enter">
        <Button
          label={SECLUSION.enter}
          tone="strong"
          description="{SECLUSION.enterNamed}: {trial.title}"
          onclick={onseclusion}
        />
      </div>
    {/if}
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

  .enter {
    display: grid;
  }

  .enter :global(.button) {
    padding-block: var(--space-3);
    letter-spacing: 0.15em;
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
