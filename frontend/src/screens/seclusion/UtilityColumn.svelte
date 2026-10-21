<!-- The right of the room: three release valves, so nothing pulls the user out of the trial. -->
<script lang="ts">
  import ParallelPanel from './ParallelPanel.svelte';
  import ScrapsPanel from './ScrapsPanel.svelte';
  import ScribeBox from './ScribeBox.svelte';
</script>

<div class="column">
  <ParallelPanel />
  <ScribeBox />
  <div class="grow">
    <ScrapsPanel />
  </div>
</div>

<style>
  .column {
    display: flex;
    flex-direction: column;
    gap: var(--space-4);
    min-height: 0;
  }

  .grow {
    flex: 1;
    min-height: 0;
    display: flex;
    flex-direction: column;
  }

  .grow :global(.panel) {
    flex: 1;
  }
</style>
