<script lang="ts">
  import NoticeText from '../../components/NoticeText.svelte';
  import Panel from '../../components/Panel.svelte';
  import RowList from '../../components/RowList.svelte';
  import type { Conquered } from '../../lib/api';
  import { EMPTY } from '../../lib/copy';
  import { view } from '../../lib/view.svelte';
  import ConqueredRow from './ConqueredRow.svelte';

  const conquered = $derived(view.current?.dashboard.conquered ?? []);
</script>

{#snippet row(trial: Conquered)}
  <ConqueredRow {trial} />
{/snippet}

<Panel
  title="Conquered Today"
  tone="conquered"
  guide="conquered"
  count={conquered.length}
  scroll
  striped
>
  {#if view.notice}<p class="notice" role="status"><NoticeText /></p>{/if}
  <RowList items={conquered} {row} empty={EMPTY.conquered} />
</Panel>

<style>
  .notice {
    margin: 0;
    padding: var(--space-2) var(--space-4);
    color: var(--ink-muted);
  }
</style>
