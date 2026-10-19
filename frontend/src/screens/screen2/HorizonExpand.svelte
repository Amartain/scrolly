<!-- The Horizon at full size: rename, switch Mandate, delete. Durations are read-only here. -->
<script lang="ts">
  import Modal from '../../components/Modal.svelte';
  import RowList from '../../components/RowList.svelte';
  import type { HorizonItem } from '../../lib/api';
  import { EMPTY } from '../../lib/copy';
  import { view } from '../../lib/view.svelte';
  import HorizonRow from '../plan/HorizonRow.svelte';

  let { onclose }: { onclose: () => void } = $props();
</script>

{#snippet row(item: HorizonItem)}
  <HorizonRow {item} editable />
{/snippet}

<Modal title="The Horizon, expanded" tone="horizon" {onclose}>
  <RowList items={view.planning?.horizon ?? []} {row} empty={EMPTY.horizon} />
</Modal>
