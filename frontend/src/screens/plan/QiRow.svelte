<script lang="ts">
  import TrialMark from '../../components/TrialMark.svelte';
  import { planning, type PlanTrial } from '../../lib/api';
  import { view } from '../../lib/view.svelte';

  let { trial }: { trial: PlanTrial } = $props();

  const restores = $derived(trial.origin_type === 'restorative_art');

  async function commit(event: Event) {
    const input = event.currentTarget as HTMLInputElement;
    if (input.value.trim() === trial.qi_text) return;
    const accepted = await view.act(() => planning.update(trial.id, { qi: input.value }));
    if (!accepted) input.value = trial.qi_text;
  }
</script>

<TrialMark {trial} />
<span class="title read">{trial.title}</span>
<span class="essence digits">{trial.expected_text}</span>
<span class="sign" aria-hidden="true">{restores ? '+' : ''}</span>
<input
  class="qi digits"
  value={trial.qi_text}
  placeholder="0"
  inputmode="numeric"
  aria-label={restores ? `Qi restored by ${trial.title}` : `Qi cost of ${trial.title}`}
  onchange={commit}
/>

<style>
  .title {
    flex: 1;
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .essence {
    color: var(--ink-muted);
  }

  .sign {
    width: var(--space-3);
    text-align: right;
  }

  .qi {
    flex: none;
    width: var(--size-qi-field);
    height: var(--size-glyph-button);
    padding-inline: var(--space-2);
    background: var(--surface-raised);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-sunken);
    font-size: var(--text-body-md);
    text-align: right;
  }
</style>
