<!-- The left of the room: tabs, the trial at hand, the ring, the action bar. -->
<script lang="ts">
  import type { Immediate } from '../../lib/api';
  import { SECLUSION } from '../../lib/copy-seclusion';
  import { seclusion } from '../../lib/seclusion.svelte';
  import type { SeclusionState } from '../../lib/seclusion-api';
  import ActionBar from './ActionBar.svelte';
  import Ring from './Ring.svelte';
  import Tabs from './Tabs.svelte';
  import TrialHeader from './TrialHeader.svelte';
  import WhatNext from './WhatNext.svelte';

  let { room, trial }: { room: SeclusionState; trial: Immediate } = $props();
</script>

<section class="scroll" aria-label="Focus Scroll">
  <Tabs />
  <TrialHeader {trial} note={room.note} />
  <div class="stage">
    {#if seclusion.finished}
      <WhatNext {room} {trial} />
    {:else}
      <Ring {room} {trial} />
    {/if}
  </div>
  <p class="caption">{SECLUSION.caption}</p>
  <div class="timer-row">
    <button class="text display" type="button" onclick={seclusion.newTimer}
      >{SECLUSION.newTimer}</button
    >
    <button class="text display" type="button" onclick={seclusion.zeroOut}
      >{SECLUSION.zeroOut}</button
    >
  </div>
  <ActionBar {trial} ringSeconds={room.ring_elapsed_s} />
</section>

<style>
  .scroll {
    display: flex;
    flex-direction: column;
    min-height: 0;
    background: var(--surface-panel);
    background-image: var(--gloss-faint);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-panel);
  }

  .stage {
    flex: 1;
    min-height: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: var(--space-2) 0;
  }

  .caption {
    margin: 0;
    padding-inline: var(--space-5);
    color: var(--ink-muted);
    font-size: var(--text-body-sm);
    text-align: center;
  }

  .timer-row {
    display: flex;
    justify-content: center;
    gap: var(--space-4);
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
