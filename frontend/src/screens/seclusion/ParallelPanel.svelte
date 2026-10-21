<!-- Parallel Flow: a search bar that, once a trial is picked, turns into that trial's own count-up. -->
<script lang="ts">
  import { SECLUSION } from '../../lib/copy-seclusion';
  import { seclusion } from '../../lib/seclusion.svelte';
  import ParallelRow from './ParallelRow.svelte';
  import ParallelSearch from './ParallelSearch.svelte';
  import Valve from './Valve.svelte';

  const room = $derived(seclusion.state);
</script>

<Valve title={SECLUSION.parallelTitle}>
  {#if !room?.trial}
    <p class="empty">{SECLUSION.parallelLine}</p>
  {:else if room.parallel}
    <ParallelRow trial={room.parallel} />
  {:else}
    <ParallelSearch />
  {/if}
</Valve>

<style>
  .empty {
    margin: 0;
    padding: var(--space-2) var(--space-4) var(--space-3);
    color: var(--ink-muted);
  }
</style>
