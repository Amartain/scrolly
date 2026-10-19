<script lang="ts">
  import Button from '../../components/Button.svelte';
  import EditableText from '../../components/EditableText.svelte';
  import GlyphButton from '../../components/GlyphButton.svelte';
  import QiField from '../../components/QiField.svelte';
  import StateMark from '../../components/StateMark.svelte';
  import TypeMark from '../../components/TypeMark.svelte';
  import GlyphIcon from '../../icons/GlyphIcon.svelte';
  import { today, type PlanTrial } from '../../lib/api';
  import { view } from '../../lib/view.svelte';

  let { trial }: { trial: PlanTrial } = $props();

  const qiOn = $derived(view.planning?.qi.enabled ?? false);
  const update = (patch: Parameters<typeof today.update>[1]) =>
    view.act(() => today.update(trial.id, patch));

  async function commitEstimate(event: Event) {
    const input = event.currentTarget as HTMLInputElement;
    if (input.value.trim() === trial.expected_text) return;
    if (!(await update({ estimate: input.value }))) input.value = trial.expected_text;
  }
</script>

<StateMark state="remaining" />
<EditableText
  value={trial.title}
  label="Rename {trial.title}"
  onsave={(title) => update({ title })}
/>
<input
  class="estimate digits"
  value={trial.expected_text}
  placeholder="—"
  aria-label="Estimate for {trial.title}"
  onchange={commitEstimate}
/>
{#if qiOn}
  <QiField
    value={trial.qi_text}
    restores={trial.type === 'restorative'}
    label="Qi expected of {trial.title}"
    onsave={(qi) => update({ qi })}
  />
{/if}
<TypeMark
  type={trial.type}
  title={trial.title}
  onToggle={() => update({ is_mandate: !trial.is_mandate })}
/>
<Button
  label="Promote"
  description="Promote {trial.title}"
  onclick={() => view.act(() => today.promote(trial.id))}
/>
{#if trial.is_mandate}
  <span class="postpone">
    <GlyphButton
      label="Postpone {trial.title} to the Horizon"
      onclick={() => view.act(() => today.postpone(trial.id))}
    >
      <GlyphIcon name="arrow" />
    </GlyphButton>
  </span>
{:else}
  <GlyphButton
    label="Abandon {trial.title}"
    onclick={() => view.act(() => today.abandon(trial.id))}
  >
    <GlyphIcon name="x" />
  </GlyphButton>
{/if}

<style>
  .estimate {
    flex: none;
    width: var(--size-estimate);
    height: var(--size-glyph-button);
    padding-inline: var(--space-2);
    background: var(--surface-raised);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-sunken);
    font-size: var(--text-body-md);
    text-align: right;
  }

  .postpone {
    --glyph-ink: var(--postponed);
    display: flex;
  }
</style>
