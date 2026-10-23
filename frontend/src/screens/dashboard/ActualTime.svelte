<!-- A conquered trial's time. Double-click it (or Enter on it): a small field with a check mark takes
     its place, as for a late estimate. Enter or ✓ saves, Esc keeps the old time. -->
<script lang="ts">
  import { tick } from 'svelte';
  import { knowledge } from '../../lib/knowledge.svelte';

  let {
    value,
    title,
    onsave,
  }: { value: string; title: string; onsave: (text: string) => Promise<boolean> } = $props();

  let editing = $state(false);
  let draft = $state('');
  let field = $state<HTMLInputElement>();

  /** Opened by a double-click or by Enter: either teaches the tour's lesson. */
  async function open(event: Event) {
    knowledge.learn('correct-time', event.currentTarget as Element);
    draft = value === '—' ? '' : value;
    editing = true;
    await tick();
    field?.focus();
    field?.select();
  }

  async function commit() {
    if (!draft.trim()) return;
    if (await onsave(draft)) editing = false;
  }

  function onkeydown(event: KeyboardEvent) {
    if (event.key === 'Enter') void commit();
    if (event.key === 'Escape') editing = false;
  }
</script>

{#if editing}
  <span class="set">
    <input
      bind:this={field}
      bind:value={draft}
      class="field digits"
      placeholder="45m"
      aria-label="Actual time of {title}"
      {onkeydown}
    />
    <button
      class="check"
      type="button"
      aria-label="Save the time of {title}"
      title="Save"
      onclick={commit}>✓</button
    >
  </span>
{:else}
  <button
    class="time digits"
    type="button"
    aria-label="Actual time of {title}"
    title="Double-click to correct"
    ondblclick={open}
    onclick={(event) => event.detail === 0 && open(event)}>{value}</button
  >
{/if}

<style>
  .time {
    padding: 0;
    background: none;
    border: 0;
    color: inherit;
    font: inherit;
    cursor: text;
  }

  .set {
    display: flex;
    align-items: center;
    gap: var(--space-1);
  }

  .field {
    width: var(--size-estimate);
    height: var(--size-glyph-button);
    padding-inline: var(--space-2);
    background: var(--surface-raised);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-sunken);
    color: var(--ink);
    font-size: var(--text-body-sm);
    text-align: right;
  }

  .check {
    padding-block: 0;
    padding-inline: var(--space-1);
    background: none;
    border: 0;
    color: var(--ink);
    cursor: pointer;
    font-size: var(--text-body-md);
  }
</style>
