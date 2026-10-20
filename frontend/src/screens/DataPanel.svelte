<script lang="ts">
  import Button from '../components/Button.svelte';
  import ConfirmModal from '../components/ConfirmModal.svelte';
  import Panel from '../components/Panel.svelte';
  import { DATA } from '../lib/copy';
  import { view } from '../lib/view.svelte';

  let picker: HTMLInputElement;
  let message = $state<string>(DATA.hint);
  /** A backup zip waits here for the user's yes: it replaces everything. */
  let replacing = $state<File | null>(null);
  let purging = $state(false);

  async function restore(file: File) {
    try {
      const result = await view.restore(file);
      message = file.name.toLowerCase().endsWith('.zip')
        ? `Restored ${result.added} rows. The earlier data was copied to the backups folder first.`
        : `Added ${result.added}, skipped ${result.skipped} already there.`;
    } catch (error) {
      message = error instanceof Error ? error.message : 'Restore failed.';
    }
  }

  async function chosen() {
    const file = picker.files?.[0];
    picker.value = '';
    if (!file) return;
    if (file.name.toLowerCase().endsWith('.zip')) replacing = file;
    else await restore(file);
  }

  async function confirmReplace() {
    const file = replacing;
    replacing = null;
    if (file) await restore(file);
  }

  async function confirmPurge() {
    purging = false;
    message = (await view.purge()) ? DATA.purged : view.notice;
  }
</script>

<Panel title="Data">
  <div class="data">
    <Button label="Backup Scroll" onclick={() => (window.location.href = '/api/export')} />
    <Button label="Restore Scroll" onclick={() => picker.click()} />
    <Button label="Purge Today's Scroll" onclick={() => (purging = true)} />
    <input
      bind:this={picker}
      type="file"
      accept=".zip,.csv,.json,.md"
      hidden
      aria-label="Scroll file"
      onchange={chosen}
    />
    <p class="note" role="status">{message}</p>
  </div>
</Panel>

{#if replacing}
  <ConfirmModal
    title={DATA.replaceTitle}
    body={DATA.replaceBody}
    confirm={DATA.replace}
    onconfirm={confirmReplace}
    oncancel={() => (replacing = null)}
  />
{/if}
{#if purging}
  <ConfirmModal
    title={DATA.purgeTitle}
    body={DATA.purgeBody}
    confirm={DATA.purge}
    onconfirm={confirmPurge}
    oncancel={() => (purging = false)}
  />
{/if}

<style>
  .data {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: var(--space-4);
    padding: var(--space-4);
  }

  .note {
    margin: 0;
    color: var(--ink-muted);
  }
</style>
