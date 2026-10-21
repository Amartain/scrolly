<!-- The trial run beside the one at hand, once picked: its name and a plain count-up in neutral ink,
     with its own Conquered, start and pause, and ✖ or ➔ by type. Nothing here touches the main trial. -->
<script lang="ts">
  import Button from '../../components/Button.svelte';
  import GlyphButton from '../../components/GlyphButton.svelte';
  import TypeMark from '../../components/TypeMark.svelte';
  import type { Immediate } from '../../lib/api';
  import { SECLUSION } from '../../lib/copy-seclusion';
  import { parallel } from '../../lib/parallel.svelte';
  import { seclusion } from '../../lib/seclusion.svelte';
  import { clockText, useTimerDisplay } from '../../lib/timer.svelte';
  import GlyphIcon from '../../icons/GlyphIcon.svelte';

  let { trial }: { trial: Immediate } = $props();

  const copy = SECLUSION.parallel;
  const display = useTimerDisplay(
    () => trial.timer,
    () => seclusion.receivedAt,
  );
  const running = $derived(trial.timer.running);
</script>

<div class="beside" role="group" aria-label={SECLUSION.parallelTitle}>
  <div class="head">
    <TypeMark
      type={trial.type}
      title={trial.title}
      onToggle={() => parallel.toggleMandate(trial)}
    />
    <span class="name">{trial.title}</span>
    <span class="clock display digits">{clockText(display.seconds)}</span>
  </div>
  <div class="actions">
    <Button
      label={SECLUSION.conquered}
      tone="gold"
      description="Conquer {trial.title}"
      onclick={() => parallel.finish('conquered', trial)}
    />
    <GlyphButton
      label={running ? copy.pause : copy.start}
      onclick={running ? parallel.pause : parallel.start}
    >
      <GlyphIcon name={running ? 'pause' : 'play'} />
    </GlyphButton>
    {#if trial.is_mandate}
      <GlyphButton
        label="Postpone {trial.title} to the Horizon"
        onclick={() => parallel.finish('postponed', trial)}
      >
        <GlyphIcon name="arrow" />
      </GlyphButton>
    {:else}
      <GlyphButton
        label="Abandon {trial.title}"
        onclick={() => parallel.finish('abandoned', trial)}
      >
        <GlyphIcon name="x" />
      </GlyphButton>
    {/if}
  </div>
</div>

<style>
  .beside {
    display: flex;
    flex-direction: column;
    gap: var(--space-3);
    padding: var(--space-3) var(--space-4);
  }

  .head {
    display: flex;
    align-items: center;
    gap: var(--space-3);
  }

  .name {
    flex: 1;
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    font-size: var(--text-read-lg);
  }

  .clock {
    color: var(--ink);
    font-size: var(--text-display-md);
  }

  .actions {
    display: flex;
    align-items: center;
    gap: var(--space-3);
  }

  .actions :global(.glyph) {
    width: var(--size-icon);
    height: var(--size-icon);
  }
</style>
