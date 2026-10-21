<!-- The icon row under the ring: ↻ restart, ⏮ zero out, ⏸ pause, ⏭ break, ■ stop, and the sound.
     Incense has one stretch and no setup, so it shows only ↻ ⏸ and the sound. Within a tab a button
     that does not apply right now is dimmed, never removed. Restart and Zero out ask before they scrap
     a minute or more. -->
<script lang="ts">
  import { tick } from 'svelte';
  import GlyphButton from '../../components/GlyphButton.svelte';
  import GlyphIcon from '../../icons/GlyphIcon.svelte';
  import { SECLUSION } from '../../lib/copy-seclusion';
  import { seclusion } from '../../lib/seclusion.svelte';
  import type { SeclusionState } from '../../lib/seclusion-api';
  import { minutesText } from '../../lib/timer.svelte';
  import ScrapConfirm from './ScrapConfirm.svelte';
  import SoundPopover from './SoundPopover.svelte';

  type Kind = 'restart' | 'zero';

  let { room }: { room: SeclusionState } = $props();

  const incense = $derived(room.discipline === 'incense');
  const cycles = $derived(room.cycles);
  const flow = $derived(room.flow);
  const running = $derived(seclusion.running);
  // The Cycles dial and an empty Flow bank have nothing to start over or stop yet.
  const started = $derived(
    incense
      ? running || room.ring_elapsed_s > 0
      : cycles
        ? cycles.phase !== 'idle'
        : flow?.phase !== 'idle' || (flow?.focus_s ?? 0) > 0,
  );
  const inStretch = $derived(
    cycles ? cycles.phase === 'focus' || cycles.phase === 'break' : flow?.phase !== 'idle',
  );
  const canBreak = $derived(cycles?.phase === 'focus' || (flow?.can_break ?? false));
  const onBreak = $derived(cycles?.phase === 'break' || flow?.phase === 'break');
  // The dial has its own Start; a finished run has nothing to start; a Flow break runs out by itself.
  const playable = $derived(
    !seclusion.settingUp && cycles?.phase !== 'done' && flow?.phase !== 'break',
  );

  let asking = $state<{ kind: Kind; seconds: number } | null>(null);

  const act = (kind: Kind) => (kind === 'restart' ? seclusion.restart() : seclusion.zeroOut());

  // What would be scrapped now: the server's figure as of its view, plus the time since, if counting.
  function ask(kind: Kind) {
    const sent = kind === 'restart' ? room.restart_scrap_s : room.zero_scrap_s;
    const since = running ? Math.floor((performance.now() - seclusion.receivedAt) / 1000) : 0;
    const seconds = sent + since;
    if (seconds < 60)
      void act(kind); // under a minute is nothing to ask about
    else asking = { kind, seconds };
  }

  async function answer(scrap: boolean) {
    const kind = asking?.kind;
    asking = null;
    if (scrap && kind) await act(kind);
    await tick(); // the icon row is back in the page before focus returns to its button
    document.getElementById(`control-${kind}`)?.focus();
  }
</script>

<div class="row" role="toolbar" aria-label="Timer">
  {#if asking}
    <ScrapConfirm minutes={minutesText(asking.seconds)} onanswer={answer} />
  {:else}
    <GlyphButton
      id="control-restart"
      label={SECLUSION.restart}
      disabled={!started}
      onclick={() => ask('restart')}><GlyphIcon name="reset" /></GlyphButton
    >
    {#if !incense}
      <GlyphButton
        id="control-zero"
        label={SECLUSION.zeroOut}
        disabled={!inStretch}
        onclick={() => ask('zero')}><GlyphIcon name="back" /></GlyphButton
      >
    {/if}
    <GlyphButton
      label={running
        ? SECLUSION.pauseTimer
        : started
          ? SECLUSION.resumeTimer
          : SECLUSION.startTimer}
      disabled={!playable}
      onclick={running ? seclusion.pause : seclusion.start}
      ><GlyphIcon name={running ? 'pause' : 'play'} /></GlyphButton
    >
    {#if !incense}
      <GlyphButton
        label={onBreak ? SECLUSION.skipBreak : SECLUSION.takeBreak}
        disabled={!canBreak && !onBreak}
        onclick={onBreak ? seclusion.endBreak : seclusion.takeBreak}
        ><GlyphIcon name="skip" /></GlyphButton
      >
      <GlyphButton label={SECLUSION.stop} disabled={!started} onclick={seclusion.stop}
        ><GlyphIcon name="stop" /></GlyphButton
      >
    {/if}
    <SoundPopover up />
  {/if}
</div>

<style>
  .row {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: var(--space-4);
    min-height: calc(var(--size-icon-button) + var(--space-3) * 2);
    padding: var(--space-3) var(--space-5);
  }

  .row :global(.glyph-button) {
    width: var(--size-icon-button);
    height: var(--size-icon-button);
  }

  .row :global(.glyph) {
    width: var(--size-icon);
    height: var(--size-icon);
  }
</style>
