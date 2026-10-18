<script lang="ts">
  import GlyphButton from '../../components/GlyphButton.svelte';
  import Panel from '../../components/Panel.svelte';
  import RowList from '../../components/RowList.svelte';
  import TrialMark from '../../components/TrialMark.svelte';
  import GlyphIcon from '../../icons/GlyphIcon.svelte';
  import { planning, type PlanTrial } from '../../lib/api';
  import { view } from '../../lib/view.svelte';

  const trials = $derived(view.planning?.trials ?? []);

  const unstage = (trial: PlanTrial) => view.act(() => planning.unstage(trial.id));
</script>

{#snippet row(trial: PlanTrial)}
  <TrialMark {trial} />
  <span class="title">{trial.title}</span>
  <span class="estimate digits">{trial.expected_text}</span>
  <GlyphButton
    label={trial.origin_type === 'horizon'
      ? `Return ${trial.title} to the Horizon`
      : `Remove ${trial.title}`}
    onclick={() => unstage(trial)}
  >
    <GlyphIcon name="x" />
  </GlyphButton>
{/snippet}

<Panel title="On the Scroll" scroll>
  <RowList items={trials} {row} empty="Nothing summoned or scribed yet." />
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
