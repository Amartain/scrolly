<!-- The small labelled row under the ring caption: start over, zero out, and (Cycles, Flow) the break. -->
<script lang="ts">
  import { SECLUSION } from '../../lib/copy-seclusion';
  import { seclusion } from '../../lib/seclusion.svelte';
  import type { SeclusionState } from '../../lib/seclusion-api';

  let { room }: { room: SeclusionState } = $props();

  const incense = $derived(room.discipline === 'incense');
  // The dial (Cycles) and the empty bank (Flow) have nothing to start over.
  const started = $derived(
    incense ||
      (room.discipline === 'cycles' && room.cycles?.phase !== 'idle') ||
      (room.discipline === 'flow' && (room.flow?.phase !== 'idle' || room.flow.focus_s > 0)),
  );
  const canBreak = $derived(room.cycles?.phase === 'focus' || (room.flow?.can_break ?? false));
  const onBreak = $derived(room.cycles?.phase === 'break' || room.flow?.phase === 'break');
</script>

{#if started}
  <div class="row">
    {#if canBreak}
      <button class="text display" type="button" onclick={seclusion.takeBreak}
        >{SECLUSION.takeBreak}</button
      >
    {/if}
    {#if onBreak}
      <button class="text display" type="button" onclick={seclusion.endBreak}
        >{SECLUSION.skipBreak}</button
      >
    {/if}
    <button class="text display" type="button" onclick={seclusion.newTimer}
      >{incense ? SECLUSION.newTimer : SECLUSION.startNewCycle}</button
    >
    <button class="text display" type="button" onclick={seclusion.zeroOut}
      >{SECLUSION.zeroOut}</button
    >
  </div>
{:else}
  <div class="row"></div>
{/if}

<style>
  .row {
    display: flex;
    justify-content: center;
    gap: var(--space-4);
    min-height: var(--size-timer-row);
    padding: var(--space-3) var(--space-5);
  }

  .text {
    padding: var(--space-1) var(--space-3);
    background: var(--btn);
    background-image: var(--gloss-btn);
    color: var(--ink);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-button);
    font-size: var(--text-display-sm);
    cursor: pointer;
  }

  .text:active {
    box-shadow: none;
    transform: translate(var(--shadow-offset), var(--shadow-offset));
  }
</style>
