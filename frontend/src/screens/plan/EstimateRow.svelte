<script lang="ts">
  import GlyphButton from '../../components/GlyphButton.svelte';
  import TrialMark from '../../components/TrialMark.svelte';
  import GlyphIcon from '../../icons/GlyphIcon.svelte';
  import { planning, type PlanTrial } from '../../lib/api';
  import { view } from '../../lib/view.svelte';

  let { trial }: { trial: PlanTrial } = $props();

  const isArt = $derived(
    trial.origin_type === 'foundational_art' || trial.origin_type === 'restorative_art',
  );

  async function commit(event: Event) {
    const input = event.currentTarget as HTMLInputElement;
    if (input.value.trim() === trial.expected_text) return;
    const accepted = await view.act(() => planning.update(trial.id, { estimate: input.value }));
    if (!accepted) input.value = trial.expected_text;
  }

  // The icon is the control: the cloud becomes a lotus and back. Python decides what is allowed.
  const toggleMandate = () =>
    view.act(() => planning.update(trial.id, { is_mandate: !trial.is_mandate }));
  const dismiss = () => view.act(() => planning.dismiss(trial.id));
</script>

{#if isArt}
  <TrialMark {trial} />
{:else}
  <button
    class="mark-toggle"
    type="button"
    aria-pressed={trial.is_mandate}
    aria-label={trial.is_mandate
      ? `Make ${trial.title} a Mortal Trial`
      : `Make ${trial.title} a Heavenly Mandate`}
    onclick={toggleMandate}
  >
    <TrialMark {trial} />
  </button>
{/if}
<span class="title read">{trial.title}</span>
<input
  class="estimate digits"
  value={trial.expected_text}
  placeholder="45m"
  aria-label="Estimate for {trial.title}"
  onchange={commit}
/>
<GlyphButton
  label={trial.is_mandate ? `Postpone ${trial.title} to the Horizon` : `Let go of ${trial.title}`}
  onclick={dismiss}
>
  <GlyphIcon name={trial.is_mandate ? 'arrow' : 'x'} />
</GlyphButton>

<style>
  .title {
    flex: 1;
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .mark-toggle {
    flex: none;
    display: flex;
    padding: 0;
    cursor: pointer;
    background: none;
    border: 0;
  }

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
</style>
