<!-- The focus room: the Immediate Trial, its timer and three release valves. Nothing else is shown. -->
<script lang="ts">
  import { playGong } from '../../lib/chime';
  import { onControl, typing } from '../../lib/keys';
  import { seclusion } from '../../lib/seclusion.svelte';
  import { view } from '../../lib/view.svelte';
  import FocusScroll from './FocusScroll.svelte';
  import RestScroll from './RestScroll.svelte';
  import TopBar from './TopBar.svelte';
  import UtilityColumn from './UtilityColumn.svelte';

  let { onleave }: { onleave: () => void } = $props();

  const room = $derived(seclusion.state);
  const trial = $derived(room?.trial ?? null);

  // The server says when the next gong is due; the browser only rings it, then asks again.
  $effect(() => {
    const due = room?.gong_in_s;
    if (due == null || !trial?.timer.running) return;
    const wait = due * 1000 - (performance.now() - seclusion.receivedAt);
    const id = setTimeout(
      () => {
        playGong();
        void seclusion.load();
      },
      Math.max(0, wait),
    );
    return () => clearTimeout(id);
  });

  // Space starts or pauses the timer, Enter conquers. A focused button already does both itself.
  function onkeydown(event: KeyboardEvent) {
    const modified = event.altKey || event.ctrlKey || event.metaKey || event.shiftKey;
    if (!trial || modified || typing(event.target) || onControl(event.target)) return;
    if (event.key === ' ') void (trial.timer.running ? seclusion.pause() : seclusion.start());
    else if (event.key === 'Enter') void seclusion.finish('conquered', trial);
    else return;
    event.preventDefault();
  }

  // N: jump to the Scribe box, as on the dashboard.
  function onnote(event: KeyboardEvent) {
    const modified = event.altKey || event.ctrlKey || event.metaKey;
    if (modified || typing(event.target) || (event.key !== 'n' && event.key !== 'N')) return;
    event.preventDefault();
    document.getElementById('seclusion-scribe')?.focus();
  }
</script>

<svelte:window {onkeydown} onkeydowncapture={onnote} />

<div class="room">
  <TopBar {onleave} />
  <div class="grid">
    {#if room && trial}
      <FocusScroll {room} {trial} />
    {:else}
      <RestScroll />
    {/if}
    <UtilityColumn />
  </div>
  <p class="notice" role="status">{view.notice}</p>
</div>

<style>
  .room {
    flex: 1;
    min-height: 0;
    display: flex;
    flex-direction: column;
    background: var(--seclusion-canvas);
  }

  .grid {
    flex: 1;
    min-height: 0;
    display: grid;
    grid-template-columns: minmax(0, 2fr) minmax(var(--size-utility-min), 1fr);
    gap: var(--space-5);
    padding: var(--space-4) var(--size-gutter) 0;
  }

  .notice {
    flex: none;
    min-height: var(--space-8);
    margin: 0;
    padding: var(--space-1) var(--size-gutter);
    color: var(--ink-muted);
  }

  @media (max-width: 60rem) {
    .room {
      overflow-y: auto;
    }

    .grid {
      flex: none;
      grid-template-columns: minmax(0, 1fr);
    }
  }
</style>
