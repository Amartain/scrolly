<!-- The waiting trials, to choose the one at hand from. Picking one makes it Immediate; the trial it
     replaces steps back, paused, to the top of Remaining (Python's Promote). -->
<script lang="ts">
  import TypeMark from '../../components/TypeMark.svelte';
  import { SECLUSION } from '../../lib/copy-seclusion';
  import { seclusion } from '../../lib/seclusion.svelte';
  import type { SeclusionState } from '../../lib/seclusion-api';

  let { remaining, onpicked }: { remaining: SeclusionState['remaining']; onpicked?: () => void } =
    $props();

  async function pick(id: string) {
    await seclusion.switchTo(id);
    onpicked?.();
  }
</script>

<ul class="list">
  {#each remaining as waiting (waiting.id)}
    <li>
      <button
        class="row"
        type="button"
        aria-label="{SECLUSION.switchTo} {waiting.title}"
        onclick={() => pick(waiting.id)}
      >
        <span class="mark"><TypeMark type={waiting.type} title={waiting.title} /></span>
        <span class="read">{waiting.title}</span>
      </button>
    </li>
  {/each}
</ul>

<style>
  .list {
    align-self: stretch;
    max-height: 14rem;
    margin: 0;
    padding: 0;
    overflow-y: auto;
    list-style: none;
    scrollbar-width: thin;
    scrollbar-color: var(--scrollbar-thumb) var(--scrollbar-track);
  }

  .row {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    width: 100%;
    padding: var(--space-2) var(--space-3);
    background: none;
    border: 0;
    color: var(--ink);
    font-size: var(--text-read-md);
    text-align: left;
    cursor: pointer;
  }

  .row:hover,
  .row:focus-visible {
    background: var(--surface-stripe);
  }

  .mark {
    display: flex;
  }
</style>
