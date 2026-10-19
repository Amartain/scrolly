<script lang="ts">
  import QiField from '../../components/QiField.svelte';
  import TypeMark from '../../components/TypeMark.svelte';
  import { planning, type PlanTrial } from '../../lib/api';
  import { view } from '../../lib/view.svelte';

  let { trial }: { trial: PlanTrial } = $props();

  const restores = $derived(trial.type === 'restorative');
</script>

<span class="title read">{trial.title}</span>
<span class="essence digits">{trial.expected_text}</span>
<TypeMark type={trial.type} />
<QiField
  value={trial.qi_text}
  {restores}
  label={restores ? `Qi restored by ${trial.title}` : `Qi cost of ${trial.title}`}
  onsave={(qi) => view.act(() => planning.update(trial.id, { qi }))}
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
</style>
