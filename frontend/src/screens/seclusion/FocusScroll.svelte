<!-- The left of the room: tabs, the trial at hand, the ring, the action bar. -->
<script lang="ts">
  import type { Immediate } from '../../lib/api';
  import { SECLUSION } from '../../lib/copy-seclusion';
  import { seclusion } from '../../lib/seclusion.svelte';
  import type { SeclusionState } from '../../lib/seclusion-api';
  import ActionBar from './ActionBar.svelte';
  import CyclesRing from './CyclesRing.svelte';
  import CyclesSetup from './CyclesSetup.svelte';
  import FlowRing from './FlowRing.svelte';
  import Ring from './Ring.svelte';
  import Tabs from './Tabs.svelte';
  import TimerRow from './TimerRow.svelte';
  import TrialHeader from './TrialHeader.svelte';
  import WhatNext from './WhatNext.svelte';

  let { room, trial }: { room: SeclusionState; trial: Immediate } = $props();

  const caption = $derived(
    room.cycles ? SECLUSION.cycles.caption : room.flow ? SECLUSION.flow.caption : SECLUSION.caption,
  );
</script>

<section class="scroll" aria-label="Focus Scroll">
  <Tabs {room} />
  <TrialHeader {trial} note={room.note} />
  <div class="stage">
    {#if seclusion.finished}
      <WhatNext {room} {trial} />
    {:else if room.cycles}
      {#if room.cycles.phase === 'idle'}
        <CyclesSetup {room} />
      {:else}
        <CyclesRing cycles={room.cycles} />
      {/if}
    {:else if room.flow}
      <FlowRing {room} flow={room.flow} />
    {:else}
      <Ring {room} {trial} />
    {/if}
  </div>
  <p class="caption">{caption}</p>
  <TimerRow {room} />
  <ActionBar {room} {trial} />
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
</style>
