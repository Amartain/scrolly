<!-- Split bar: what you do with the time (left) and what you do with the trial (right). -->
<script lang="ts">
  import Button from '../../components/Button.svelte';
  import GlyphIcon from '../../icons/GlyphIcon.svelte';
  import type { Immediate } from '../../lib/api';
  import { SECLUSION } from '../../lib/copy-seclusion';
  import { seclusion } from '../../lib/seclusion.svelte';

  let { trial, ringSeconds }: { trial: Immediate; ringSeconds: number } = $props();

  const running = $derived(trial.timer.running);
  const idle = $derived(!running && ringSeconds === 0);

  const conquer = () => seclusion.finish('conquered', trial);
  const postpone = () => seclusion.finish('postponed', trial);
  const abandon = () => seclusion.finish('abandoned', trial);
</script>

<div class="bar">
  <div class="time">
    {#if idle}
      <Button label={SECLUSION.begin} tone="primary" onclick={seclusion.start} />
    {:else}
      <button
        class="icon play"
        type="button"
        aria-label={running ? 'Pause timer' : 'Resume timer'}
        onclick={running ? seclusion.pause : seclusion.start}
      >
        <GlyphIcon name={running ? 'pause' : 'play'} />
      </button>
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
