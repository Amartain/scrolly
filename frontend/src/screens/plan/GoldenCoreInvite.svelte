<script lang="ts">
  import Button from '../../components/Button.svelte';
  import Panel from '../../components/Panel.svelte';
  import { goldenCore } from '../../lib/api';
  import { view } from '../../lib/view.svelte';

  const answer = (enabled: boolean) => view.act(() => goldenCore.set(enabled));
</script>

<!-- Shown once. Either answer retires it; after that only Settings switches the Golden Core. -->
<Panel title="The Golden Core">
  <div class="invite">
    <p>
      An hour of one trial can cost less than ten minutes of another. Would you like to weigh your
      Qi, your inner energy, as well as your time?
    </p>
    <div class="actions">
      <Button label="Perhaps later" tour="golden-core" onclick={() => answer(false)} />
      <Button
        label="Awaken the Golden Core"
        tone="primary"
        tour="golden-core"
        onclick={() => answer(true)}
      />
    </div>
  </div>
</Panel>

<style>
  .invite {
    padding: var(--space-3) var(--space-4);
    font-size: var(--text-body-md);
  }

  p {
    margin: 0;
    margin-bottom: var(--space-3);
  }

  .actions {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    gap: var(--space-3);
    padding-right: var(--shadow-room);
    padding-bottom: var(--shadow-room);
  }
</style>
