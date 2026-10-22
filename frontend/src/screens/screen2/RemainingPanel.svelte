<script lang="ts">
  import NoticeText from '../../components/NoticeText.svelte';
  import Panel from '../../components/Panel.svelte';
  import ReorderList from '../../components/ReorderList.svelte';
  import { EMPTY } from '../../lib/copy';
  import { VICTORY } from '../../lib/copy-victory';
  import { today, type PlanTrial } from '../../lib/api';
  import { useOrder } from '../../lib/order.svelte';
  import { view } from '../../lib/view.svelte';
  import RemainingRow from './RemainingRow.svelte';

  const remaining = $derived(
    (view.planning?.trials ?? []).filter((trial) => trial.state === 'remaining'),
  );
  const order = useOrder(
    () => remaining,
    (ids) => today.reorder(ids),
  );
</script>

{#snippet row(trial: PlanTrial)}
  <RemainingRow {trial} />
{/snippet}

<Panel
  title="Remaining Trials"
  guide="remaining"
  count={remaining.length}
  hint="drag a row or Alt+↑↓ to reorder"
  scroll
  striped
>
  {#if view.notice}<p class="notice" role="status"><NoticeText /></p>{/if}
  {#if remaining.length === 0}
    <p class="empty">{view.current?.dashboard.victory ? VICTORY.arenaEmpty : EMPTY.remaining}</p>
  {:else}
    <ReorderList items={order.shown} label="Remaining trials" onreorder={order.reorder} {row} />
  {/if}
</Panel>

<style>
  .empty,
  .notice {
    margin: 0;
    padding: var(--space-2) var(--space-4);
    color: var(--ink-muted);
  }
</style>
