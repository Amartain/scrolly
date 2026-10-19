<!-- A day-list row: state mark, title, estimate, then the type mark (the Mandate/Mortal switch). -->
<script lang="ts">
  import { today } from '../lib/api';
  import { view } from '../lib/view.svelte';
  import StateMark from './StateMark.svelte';
  import TypeMark from './TypeMark.svelte';

  let {
    trial,
  }: {
    trial: {
      id: string;
      title: string;
      expected_text: string;
      state: string;
      type: string;
      is_mandate: boolean;
    };
  } = $props();

  const toggle = () => view.act(() => today.update(trial.id, { is_mandate: !trial.is_mandate }));
</script>

<StateMark state={trial.state} />
<span class="title read">{trial.title}</span>
<span class="estimate digits">{trial.expected_text}</span>
<TypeMark type={trial.type} title={trial.title} onToggle={toggle} />

<style>
  .title {
    flex: 1;
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .estimate {
    color: var(--ink-muted);
  }
</style>
