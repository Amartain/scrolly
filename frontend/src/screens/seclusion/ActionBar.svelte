<!-- The bar at the foot of the scroll: Switch (another waiting trial takes this one's place), then the
     big Start or Conquered!, then Postpone (a Mandate) or Abandon. -->
<script lang="ts">
  import Button from '../../components/Button.svelte';
  import ConquerButton from '../../components/ConquerButton.svelte';
  import GlyphButton from '../../components/GlyphButton.svelte';
  import GlyphIcon from '../../icons/GlyphIcon.svelte';
  import type { Immediate } from '../../lib/api';
  import { SECLUSION } from '../../lib/copy-seclusion';
  import { seclusion } from '../../lib/seclusion.svelte';
  import type { SeclusionState } from '../../lib/seclusion-api';
  import RemainingPicker from './RemainingPicker.svelte';

  let { room, trial }: { room: SeclusionState; trial: Immediate } = $props();

  let picking = $state(false);
  let wrap: HTMLDivElement | undefined = $state();

  // Start while nothing has begun (the Cycles dial has its own); Conquered! once it has.
  const showStart = $derived.by(() => {
    if (room.cycles) return room.cycles.phase === 'waiting';
    if (room.flow) return room.flow.phase === 'idle';
    return !seclusion.running && room.ring_elapsed_s === 0;
  });

  const conquer = () => seclusion.finish('conquered', trial);
  const postpone = () => seclusion.finish('postponed', trial);
  const abandon = () => seclusion.finish('abandoned', trial);

  function close() {
    picking = false;
    document.getElementById('control-switch')?.focus();
  }

  function onwindowclick(event: MouseEvent) {
    if (picking && wrap && event.target instanceof Node && !wrap.contains(event.target)) {
      picking = false;
    }
  }

  function onkeydown(event: KeyboardEvent) {
    if (!picking || event.key !== 'Escape') return;
    event.stopPropagation(); // the room stays; only the list closes
    close();
  }
</script>

<svelte:window onclick={onwindowclick} />

<div class="bar">
  <div class="side switch" role="presentation" bind:this={wrap} {onkeydown}>
    <GlyphButton
      id="control-switch"
      label={SECLUSION.switchTrial}
      disabled={room.remaining.length === 0}
      onclick={() => (picking = !picking)}><GlyphIcon name="switch" /></GlyphButton
    >
    {#if picking}
      <div class="picker" role="group" aria-label={SECLUSION.switchTrial}>
        <RemainingPicker remaining={room.remaining} onpicked={() => (picking = false)} />
      </div>
    {/if}
  </div>
  {#if showStart}
    <Button label={SECLUSION.start} tone="primary" onclick={seclusion.start} />
  {:else}
    <ConquerButton label={SECLUSION.conquered} title={trial.title} onclick={conquer} />
  {/if}
  <div class="side end">
    {#if trial.is_mandate}
      <span class="postpone">
        <GlyphButton label="Postpone {trial.title} to the Horizon" onclick={postpone}
          ><GlyphIcon name="arrow" /></GlyphButton
        >
      </span>
    {:else}
      <GlyphButton label="Abandon {trial.title}" onclick={abandon}
        ><GlyphIcon name="x" /></GlyphButton
      >
    {/if}
  </div>
</div>

<style>
  .bar {
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    align-items: center;
    gap: var(--space-4);
    min-height: calc(var(--size-icon-button) + var(--space-6) * 2);
    padding: var(--space-4) var(--space-5);
    background: var(--surface-stripe);
    border-top: var(--border-width) solid var(--line);
  }

  .side {
    position: relative;
    display: flex;
    justify-content: flex-end;
  }

  .side.end {
    justify-content: flex-start;
  }

  .bar :global(.button) {
    padding-block: var(--space-3);
    padding-inline: var(--space-8);
    font-size: var(--text-display-md);
  }

  .bar :global(.glyph-button) {
    width: var(--size-icon-button);
    height: var(--size-icon-button);
  }

  .bar :global(.glyph) {
    width: var(--size-icon);
    height: var(--size-icon);
  }

  .postpone {
    --glyph-ink: var(--postponed);
  }

  /* The waiting trials open above the bar, over the ring, so nothing below them moves. */
  .picker {
    position: absolute;
    bottom: calc(100% + var(--space-2));
    left: 0;
    z-index: 5;
    width: min(26rem, 80vw);
    padding: var(--space-2);
    background: var(--surface-raised);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-panel);
  }
</style>
