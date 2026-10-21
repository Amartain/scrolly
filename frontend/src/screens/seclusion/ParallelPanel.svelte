<!-- Parallel Flow: a search bar that, once a trial is picked, turns into that trial's own count-up. -->
<script lang="ts">
  import Panel from '../../components/Panel.svelte';
  import { SECLUSION } from '../../lib/copy-seclusion';
  import { seclusion } from '../../lib/seclusion.svelte';
  import ParallelRow from './ParallelRow.svelte';
  import ParallelSearch from './ParallelSearch.svelte';

  const room = $derived(seclusion.state);
</script>

{#if room?.trial}
  <Panel title={SECLUSION.parallelTitle}>
    {#if room.parallel}
      <ParallelRow trial={room.parallel} />
    {:else}
      <ParallelSearch />
    {/if}
  </Panel>
{:else}
  <Panel title={SECLUSION.parallelTitle} empty={SECLUSION.parallelLine} />
{/if}
