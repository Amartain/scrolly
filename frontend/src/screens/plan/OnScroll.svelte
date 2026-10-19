<script lang="ts">
  import GlyphButton from '../../components/GlyphButton.svelte';
  import Panel from '../../components/Panel.svelte';
  import RowList from '../../components/RowList.svelte';
  import TypeMark from '../../components/TypeMark.svelte';
  import GlyphIcon from '../../icons/GlyphIcon.svelte';
  import { planning, type PlanTrial } from '../../lib/api';
  import { EMPTY } from '../../lib/copy';
  import { view } from '../../lib/view.svelte';

  const trials = $derived(view.planning?.trials ?? []);

  const unstage = (trial: PlanTrial) => view.act(() => planning.unstage(trial.id));
</script>

{#snippet row(trial: PlanTrial)}
  <span class="title read">{trial.title}</span>
  <span class="estimate digits">{trial.expected_text}</span>
  <TypeMark type={trial.type} />
  <GlyphButton
    label={trial.origin_type === 'horizon'
      ? `Return ${trial.title} to the Horizon`
      : `Remove ${trial.title}`}
    onclick={() => unstage(trial)}
  >
    <GlyphIcon name="x" />
  </GlyphButton>
{/snippet}

<Panel title="On the Scroll" scroll striped>
  <RowList items={trials} {row} empty={EMPTY.onScroll} />
</Panel>

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
