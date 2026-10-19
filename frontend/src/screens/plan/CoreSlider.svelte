<script lang="ts">
  import { planning, type Qi } from '../../lib/api';
  import { view } from '../../lib/view.svelte';

  let { qi }: { qi: Qi } = $props();

  // The thumb follows the hand at once; the server's answer then confirms the value.
  let shown = $state(0);
  $effect(() => {
    shown = qi.start;
  });

  const resting = $derived(qi.low === qi.high);
  // One save at a time, in order, so a quick key repeat cannot leave an older value last.
  let saving: Promise<unknown> = Promise.resolve();
  function commit() {
    const value = shown;
    saving = saving.then(() => view.act(() => planning.qiStart(value)));
  }
</script>

<div class="slider">
  <label for="core-start">
    Your core begins at <span class="digits">{shown}</span> Qi
  </label>
  <input
    id="core-start"
    type="range"
    min={qi.low}
    max={qi.high}
    step={1}
    bind:value={shown}
    disabled={resting}
    onchange={commit}
  />
  <p class="hint">
    {#if resting}
      Your core must rest today. Mending begins tomorrow.
    {:else}
      Slide it lower if you feel tired.
    {/if}
  </p>
</div>

<style>
  .slider {
    margin-top: var(--space-4);
    font-size: var(--text-body-md);
  }

  label {
    display: block;
    margin-bottom: var(--space-2);
  }

  input {
    width: 100%;
    height: var(--size-slider-thumb);
    margin: 0;
    accent-color: var(--growth);
    cursor: pointer;
  }

  input:disabled {
    cursor: default;
  }

  .hint {
    margin: var(--space-2) 0 0;
    color: var(--ink-muted);
  }
</style>
