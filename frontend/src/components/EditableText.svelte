<!-- Saved text that is renamed in place: double-click it, or press Enter while it has focus. -->
<script lang="ts">
  import { tick } from 'svelte';

  let {
    value,
    label,
    onsave,
  }: { value: string; label: string; onsave: (text: string) => void | Promise<unknown> } = $props();

  let editing = $state(false);
  let draft = $state('');
  let field = $state<HTMLInputElement>();

  /** Begin renaming, for example from a pencil button. */
  export async function start() {
    draft = value;
    editing = true;
    await tick();
    field?.select();
  }

  async function finish(save: boolean) {
    if (!editing) return;
    editing = false;
    if (save && draft.trim() && draft.trim() !== value) await onsave(draft);
  }

  function onkey(event: KeyboardEvent) {
    if (event.key === 'Enter') void finish(true);
    if (event.key === 'Escape') void finish(false);
  }
</script>

{#if editing}
  <input
    class="text input"
    aria-label={label}
    bind:value={draft}
    bind:this={field}
    onkeydown={onkey}
    onblur={() => finish(true)}
  />
{:else}
  <button
    class="text read"
    type="button"
    title="Double-click to rename"
    ondblclick={start}
    onclick={(event) => event.detail === 0 && start()}
  >
    {value}
  </button>
{/if}

<style>
  .text {
    flex: 1;
    min-width: 0;
    margin: 0;
    padding: 0;
    background: none;
    border: 0;
    color: inherit;
    font-size: var(--editable-size, var(--text-read-md));
    line-height: inherit;
    text-align: left;
  }

  button.text {
    cursor: text;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .input {
    font-family: var(--font-body);
    font-size: var(--editable-size, var(--text-read-md));
    background: var(--surface-raised);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-sunken);
    padding-inline: var(--space-2);
  }
</style>
