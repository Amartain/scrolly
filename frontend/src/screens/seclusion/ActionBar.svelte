<!-- Split bar: what you do with the time (left) and what you do with the trial (right). -->
<script lang="ts">
  import Button from '../../components/Button.svelte';
  import GlyphIcon from '../../icons/GlyphIcon.svelte';
  import type { Immediate } from '../../lib/api';
  import { SECLUSION } from '../../lib/copy-seclusion';
  import { seclusion } from '../../lib/seclusion.svelte';
  import type { SeclusionState } from '../../lib/seclusion-api';

  let { room, trial }: { room: SeclusionState; trial: Immediate } = $props();

  const running = $derived(seclusion.running);

  // Which of the time controls the open tab offers right now.
  const controls = $derived.by(() => {
    if (room.cycles) {
      const phase = room.cycles.phase;
      return {
        start: phase === 'waiting',
        toggle: phase === 'focus' || phase === 'break',
        conquer: phase !== 'idle',
      };
    }
    if (room.flow) {
      const phase = room.flow.phase;
      return { start: phase === 'idle', toggle: phase === 'focus', conquer: phase !== 'idle' };
    }
    const idle = !running && room.ring_elapsed_s === 0;
    return { start: idle, toggle: !idle, conquer: !idle };
  });

  const conquer = () => seclusion.finish('conquered', trial);
  const postpone = () => seclusion.finish('postponed', trial);
  const abandon = () => seclusion.finish('abandoned', trial);
</script>

<div class="bar">
  <div class="time">
    {#if controls.start}
      <Button label={SECLUSION.start} tone="primary" onclick={seclusion.start} />
    {/if}
    {#if controls.toggle}
      <button
        class="icon play"
        type="button"
        aria-label={running ? 'Pause timer' : 'Resume timer'}
        onclick={running ? seclusion.pause : seclusion.start}
      >
        <GlyphIcon name={running ? 'pause' : 'play'} />
      </button>
    {/if}
    {#if controls.conquer}
      <Button
        label={SECLUSION.conquered}
        tone="gold"
        description="Conquer {trial.title}"
        onclick={conquer}
      />
    {/if}
  </div>
  <div class="trial">
    {#if trial.is_mandate}
      <button
        class="icon postpone"
        type="button"
        aria-label="Postpone {trial.title} to the Horizon"
        onclick={postpone}
      >
        <GlyphIcon name="arrow" />
      </button>
    {:else}
      <button class="icon" type="button" aria-label="Abandon {trial.title}" onclick={abandon}>
        <GlyphIcon name="x" />
      </button>
    {/if}
  </div>
</div>

<style>
  .bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--space-4);
    min-height: calc(var(--size-icon-button) + var(--space-6) * 2);
    padding: var(--space-4) var(--space-5);
    background: var(--surface-stripe);
    border-top: var(--border-width) solid var(--line);
  }

  .time,
  .trial {
    display: flex;
    align-items: center;
    gap: var(--space-3);
  }

  .bar :global(.button) {
    padding-block: var(--space-3);
    padding-inline: var(--space-8);
    font-size: var(--text-display-md);
  }

  .icon {
    flex: none;
    display: flex;
    align-items: center;
    justify-content: center;
    width: var(--size-icon-button);
    height: var(--size-icon-button);
    padding: 0;
    cursor: pointer;
    background: var(--btn);
    background-image: var(--gloss-btn);
    color: var(--ink);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-button);
  }

  .play {
    background: var(--growth);
    background-image: none;
    color: var(--on-growth);
  }

  .postpone {
    color: var(--postponed);
  }

  .icon :global(.glyph) {
    width: var(--size-icon);
    height: var(--size-icon);
  }

  .icon:active {
    box-shadow: none;
    transform: translate(var(--shadow-offset), var(--shadow-offset));
  }
</style>
