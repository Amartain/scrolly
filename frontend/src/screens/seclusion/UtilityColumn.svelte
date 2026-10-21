<!-- The right of the room: three release valves in one quiet frame, so nothing pulls the user out of the
     trial. Folding Bamboo Scraps shrinks the frame to what is left; nothing else moves. -->
<script lang="ts">
  import { seclusion } from '../../lib/seclusion.svelte';
  import ParallelPanel from './ParallelPanel.svelte';
  import ScrapsPanel from './ScrapsPanel.svelte';
  import ScribeBox from './ScribeBox.svelte';

  const folded = $derived(seclusion.state?.scraps_hidden ?? false);
</script>

<div class="column" class:folded>
  <ParallelPanel />
  <ScribeBox />
  <ScrapsPanel />
</div>

<style>
  .column {
    display: flex;
    flex-direction: column;
    min-height: 0;
    background: var(--surface-panel);
    background-image: var(--gloss-faint);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-panel);
  }

  .column.folded {
    align-self: start;
  }
</style>
