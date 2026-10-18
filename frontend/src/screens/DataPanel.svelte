<script lang="ts">
  import Button from '../components/Button.svelte';
  import Panel from '../components/Panel.svelte';
  import { view } from '../lib/view.svelte';

  const HINT = 'Reads an old Scrolly backup (.json) or a Discord Quest Board (.md).';

  let picker: HTMLInputElement;
  let message = $state(HINT);

  async function chosen() {
    const file = picker.files?.[0];
    if (!file) return;
    try {
      const result = await view.restore(file);
      message = `Added ${result.added}, skipped ${result.skipped} already there.`;
    } catch (error) {
      message = error instanceof Error ? error.message : 'Restore failed.';
    } finally {
      picker.value = '';
    }
  }
</script>

<Panel title="Data">
  <div class="data">
    <Button label="Restore Scroll" onclick={() => picker.click()} />
    <input
      bind:this={picker}
      type="file"
      accept=".json,.md"
      hidden
      aria-label="Scroll file"
      onchange={chosen}
    />
    <p class="note" role="status">{message}</p>
  </div>
</Panel>

<style>
  .data {
    display: flex;
    align-items: center;
    gap: var(--space-4);
    padding: var(--space-4);
  }

  .note {
    margin: 0;
    color: var(--ink-muted);
  }
</style>
