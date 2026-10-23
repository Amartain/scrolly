<!-- Everything let go or postponed today, one per line. A double-click summons one back. -->
<script lang="ts">
  import Modal from '../../components/Modal.svelte';
  import RowList from '../../components/RowList.svelte';
  import StateMark from '../../components/StateMark.svelte';
  import type { LetGo } from '../../lib/api';
  import LetGoName from './LetGoName.svelte';

  let {
    title,
    items,
    state,
    empty,
    onclose,
  }: { title: string; items: LetGo[]; state: string; empty: string; onclose: () => void } =
    $props();
</script>

{#snippet row(item: LetGo)}
  <StateMark {state} />
  <span class="read"><LetGoName {item} /></span>
{/snippet}

<Modal title="{title}, expanded" {onclose}>
  <RowList {items} {row} {empty} />
</Modal>
