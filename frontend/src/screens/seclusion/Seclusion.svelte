<!-- The focus room, 閉關: the theme's peak fills it, and one frosted card holds the Immediate Trial and its
     timer. The three release valves float at the right, folded by default. Nothing else is shown. -->
<script lang="ts">
  import { onMount, tick } from 'svelte';
  import PeakScene from '../../components/peak/PeakScene.svelte';
  import { playGong } from '../../lib/chime';
  import { onControl, typing } from '../../lib/keys';
  import { peak } from '../../lib/peak.svelte';
  import { seclusion } from '../../lib/seclusion.svelte';
  import { view } from '../../lib/view.svelte';
  import FocusScroll from './FocusScroll.svelte';
  import RestScroll from './RestScroll.svelte';
  import TopBar from './TopBar.svelte';
  import UtilityColumn from './UtilityColumn.svelte';

  let { onleave }: { onleave: () => void } = $props();

  const room = $derived(seclusion.state);
  const trial = $derived(room?.trial ?? null);
  const folded = $derived(room?.sidebar_hidden ?? false);

  // Coming back while the cultivator is up there (or on the way): nothing is painted again.
  onMount(() => peak.arrive());

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
    if (event.key === ' ') void seclusion.toggle();
    else if (event.key === 'Enter' && !seclusion.settingUp)
      void seclusion.finish('conquered', trial);
    else return;
    event.preventDefault();
  }

  // Any key or click shows the painting's last frame at once. N jumps to the Scribe box, as on the
  // dashboard (opening the Parallel sidebar if it is folded).
  async function onkeycapture(event: KeyboardEvent) {
    peak.skip();
    const modified = event.altKey || event.ctrlKey || event.metaKey;
    if (modified || typing(event.target) || (event.key !== 'n' && event.key !== 'N')) return;
    event.preventDefault();
    if (folded) {
      await seclusion.hideSidebar(false);
      await tick();
    }
    document.getElementById('seclusion-scribe')?.focus();
  }
</script>

<svelte:window {onkeydown} onkeydowncapture={onkeycapture} onpointerdown={peak.skip} />

<div class="room" class:painting={peak.painting}>
  <PeakScene />
  <div class="ui">
    <TopBar {onleave} />
    <div class="stage">
      {#if room && trial}
        <FocusScroll {room} {trial} />
      {:else}
        <RestScroll />
      {/if}
    </div>
    <UtilityColumn />
  </div>
  <p class="notice" role="status">{view.notice}</p>
</div>

<style>
  .room {
    position: relative;
    isolation: isolate;
    flex: 1;
    min-height: 0;
    display: flex;
    flex-direction: column;
    background: var(--seclusion-canvas);
  }

  .ui {
    position: relative;
    flex: 1;
    min-height: 0;
    display: flex;
    flex-direction: column;
  }

  /* The room's cards come in once the peak is painted; a key or click brings them at once. */
  .painting .ui {
    animation: peak-fade 700ms 3200ms ease-out both;
  }

  .stage {
    flex: 1;
    min-height: 0;
    display: flex;
    justify-content: center;
    align-items: flex-start;
    padding: var(--space-4) var(--size-gutter) 0;
  }

  .notice {
    position: absolute;
    bottom: 0;
    left: 0;
    margin: 0;
    padding: var(--space-1) var(--size-gutter);
    color: var(--ink-muted);
  }

  /* Words never lie bare on the painting. */
  .notice:not(:empty) {
    background: var(--seclusion-frost);
    backdrop-filter: var(--seclusion-blur);
  }

  @media (max-width: 60rem) {
    .room {
      overflow-y: auto;
    }

    .stage {
      flex: none;
      flex-direction: column;
      align-items: center;
      gap: var(--space-4);
    }
  }

  @media (prefers-reduced-motion: reduce) {
    .painting .ui {
      animation: none;
    }
  }
</style>
