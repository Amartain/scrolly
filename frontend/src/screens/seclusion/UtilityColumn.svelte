<!-- The right of the room: three release valves, so nothing pulls the user out of the trial. -->
<script lang="ts">
  import Panel from '../../components/Panel.svelte';
  import { SECLUSION } from '../../lib/copy-seclusion';
</script>

<div class="column">
  <Panel title={SECLUSION.parallelTitle} empty={SECLUSION.parallelLine} />
  <div class="grow">
    <Panel title={SECLUSION.scrapsTitle} empty={SECLUSION.scrapsLine} />
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
