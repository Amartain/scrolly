<script lang="ts">
  import { tick } from 'svelte';
  import Button from '../../components/Button.svelte';
  import QiField from '../../components/QiField.svelte';
  import StateMark from '../../components/StateMark.svelte';
  import TypeMark from '../../components/TypeMark.svelte';
  import { today, type Conquered } from '../../lib/api';
  import { view } from '../../lib/view.svelte';

  let { trial }: { trial: Conquered } = $props();

  const qiOn = $derived(view.planning?.qi.enabled ?? false);

  let editing = $state(false);
  let draft = $state('');
  let field = $state<HTMLInputElement>();

  async function edit() {
    draft = trial.actual_text;
    editing = true;
    await tick();
    field?.select();
  }

  async function finish(save: boolean) {
    if (!editing) return;
    editing = false;
    if (save && draft.trim() !== trial.actual_text) {
      await view.act(() => today.update(trial.id, { actual: draft }));
    }
  }

  function onkey(event: KeyboardEvent) {
    if (event.key === 'Enter') void finish(true);
    if (event.key === 'Escape') void finish(false);
  }
</script>

<StateMark state="done" />
<span class="title read">{trial.title}</span>
{#if editing}
  <input
    class="minutes digits"
    aria-label="Minutes for {trial.title}"
    placeholder="45m"
    bind:value={draft}
    bind:this={field}
    onkeydown={onkey}
    onblur={() => finish(true)}
  />
{:else}
  <button
    class="minutes digits"
    type="button"
    aria-label="Edit recorded minutes for {trial.title}"
    onclick={edit}
  >
    {trial.actual_text || '—'}
  </button>
{/if}
{#if qiOn}
  <QiField
    value={trial.qi_text}
    restores={trial.type === 'restorative'}
    label="Qi spent on {trial.title}"
    onsave={(actual_qi) => view.act(() => today.update(trial.id, { actual_qi }))}
  />
{/if}
<TypeMark
  type={trial.type}
  title={trial.title}
  onToggle={() => view.act(() => today.update(trial.id, { is_mandate: !trial.is_mandate }))}
/>
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

  .minutes {
    flex: none;
    width: var(--size-estimate);
    padding-inline: var(--space-2);
    background: none;
    border: 0;
    color: var(--ink);
    font-size: var(--text-body-md);
    text-align: right;
    text-decoration: underline dotted;
    cursor: pointer;
  }

  input.minutes {
    height: var(--size-glyph-button);
    background: var(--surface-raised);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-sunken);
    color: var(--ink);
    text-decoration: none;
    cursor: text;
  }
</style>
