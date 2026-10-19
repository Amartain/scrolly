<script lang="ts">
  import MandateMark from '../../components/MandateMark.svelte';
  import Panel from '../../components/Panel.svelte';
  import TypeMark from '../../components/TypeMark.svelte';
</script>

<Panel title="Guidance">
  <div class="copy">
    <p>
      Time blindness is conquered through practice. Divine the essence each trial needs (45m, 2h,
      1h30m). A forgotten estimate can be set later.
    </p>
    <p>
      Watch the light: a plan that fills every minute leaves no room for the unexpected. Drag a row,
      or press Alt with the arrow keys, to set the order.
    </p>
    <p class="term">
      <TypeMark type="mortal" />
      <span><strong>Mortal Trials:</strong> let them go freely, they fade at 4 AM.</span>
    </p>
    <p class="term">
      <TypeMark type="mandate" />
      <span>
        <MandateMark kind="term">Heavenly Mandates:</MandateMark> postponing sends a copy back to the
        Horizon.
      </span>
    </p>
    <p>Click a trial's mark to switch it between the two.</p>
  </div>
</Panel>

<style>
  .copy {
    --size-icon: var(--size-icon-guidance);
    padding: var(--space-3) var(--space-4);
    font-size: var(--text-body-md);
  }

  p {
    margin: 0;
    margin-bottom: var(--space-3);
  }

  p:last-child {
    margin-bottom: 0;
  }

  .term {
    display: flex;
    align-items: flex-start;
    gap: var(--space-3);
  }
</style>
