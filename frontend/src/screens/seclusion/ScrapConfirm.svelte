<!-- Asked before Restart or Zero out takes time off the trial. Keep has focus first, so Enter or Esc
     loses nothing. It stands where the icon row was, at the same height. -->
<script lang="ts">
  import { onMount } from 'svelte';
  import { SECLUSION } from '../../lib/copy-seclusion';

  let { minutes, onanswer }: { minutes: string; onanswer: (scrap: boolean) => void } = $props();

  let keep: HTMLButtonElement | undefined = $state();
  onMount(() => keep?.focus());

  function onkeydown(event: KeyboardEvent) {
    if (event.key !== 'Escape') return;
    event.stopPropagation(); // the room stays; only the question closes
    onanswer(false);
  }
</script>

<div class="ask" role="group" aria-label={SECLUSION.scrapAsk(minutes)}>
  <span class="question display">{SECLUSION.scrapAsk(minutes)}</span>
  <button
    bind:this={keep}
    class="choice display"
    type="button"
    {onkeydown}
    onclick={() => onanswer(false)}>{SECLUSION.keep}</button
  >
  <button class="choice display" type="button" {onkeydown} onclick={() => onanswer(true)}
    >{SECLUSION.scrap}</button
  >
</div>

<style>
  .ask {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: center;
    gap: var(--space-3);
  }

  .question {
    font-size: var(--text-display-sm);
  }

  .choice {
    padding: var(--space-1) var(--space-4);
    background: var(--btn);
    background-image: var(--gloss-btn);
    color: var(--ink);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-button);
    font-size: var(--text-display-sm);
    cursor: pointer;
  }

  .choice:active {
    box-shadow: none;
    transform: translate(var(--shadow-offset), var(--shadow-offset));
  }
</style>
