<!-- The finished-day ceremony, full screen: the scene plays (thunder for a day that conquered a
     Heavenly Mandate), the card rises out of the light and its tally counts up tile by tile. Any key
     or a click before the end skips to it; Esc closes. Under reduced motion the last frame shows at
     once. The sounds follow the volume and the mute (chime-ceremony.ts). -->
<script lang="ts">
  import { onMount, tick } from 'svelte';
  import type { Victory } from '../../lib/api';
  import { playTallyTick, playThunder, playTribulation } from '../../lib/chime-ceremony';
  import { SCENES } from '../../lib/copy-victory';
  import { view } from '../../lib/view.svelte';
  import CeremonyCard from './CeremonyCard.svelte';
  import ThunderScene from './ThunderScene.svelte';

  let { victory, onclose }: { victory: Victory; onclose: () => void } = $props();

  const ROWS = 4;
  const BOLT_MS = 550;
  const ROW_MS = 400;
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const thunder = $derived(victory.scene === 'thunder');
  // The Wind scene comes in a later build; until then a wind day goes straight to the card.
  const cardMs = $derived(thunder ? 1600 : 300);

  let still = $state(reduced);
  let card = $state(reduced);
  let rows = $state(reduced ? ROWS : 0);
  let settled = $state(reduced);
  let dialog = $state<HTMLDialogElement>();
  const timers: ReturnType<typeof setTimeout>[] = [];
  const lifetime = $derived(view.current?.dashboard.lifetime_conquered ?? 0);

  const at = (ms: number, then: () => void) => timers.push(setTimeout(then, ms));

  async function settle() {
    timers.forEach(clearTimeout);
    still = true;
    card = true;
    rows = ROWS;
    settled = true;
    await tick();
    dialog?.querySelector<HTMLButtonElement>('.close button')?.focus();
  }

  onMount(() => {
    const opener = document.activeElement;
    dialog?.showModal();
    if (reduced) {
      playTribulation();
      void settle();
    } else {
      if (thunder) at(BOLT_MS, playThunder);
      else playTribulation();
      at(cardMs, () => (card = true));
      for (let n = 1; n <= ROWS; n++)
        at(cardMs + 300 + (n - 1) * ROW_MS, () => {
          rows = n;
          playTallyTick(n);
        });
      at(cardMs + 300 + ROWS * ROW_MS, () => void settle());
    }
    return () => {
      timers.forEach(clearTimeout);
      dialog?.close();
      if (opener instanceof HTMLElement) opener.focus();
    };
  });

  // A key (other than Esc, which closes) or a click before the end only skips to it.
  function skip(event: Event) {
    if (settled || (event instanceof KeyboardEvent && event.key === 'Escape')) return;
    event.preventDefault();
    event.stopPropagation();
    void settle();
  }
</script>

<svelte:window onkeydowncapture={skip} />

<!-- svelte-ignore a11y_click_events_have_key_events, a11y_no_noninteractive_element_interactions -->
<dialog
  bind:this={dialog}
  class={victory.scene}
  aria-label={SCENES[victory.scene].title}
  onclick={skip}
  oncancel={(event) => {
    event.preventDefault();
    onclose();
  }}
>
  {#if thunder}<ThunderScene {still} />{/if}
  {#if card}
    <CeremonyCard {victory} {lifetime} {rows} {settled} {still} {onclose} />
  {/if}
</dialog>

<style>
  dialog {
    width: 100vw;
    height: 100dvh;
    max-width: none;
    max-height: none;
    margin: 0;
    padding: 0;
    border: 0;
    display: grid;
    place-items: center;
    overflow: hidden;
    background: linear-gradient(
      var(--scene-sky-top),
      var(--scene-sky-mid) 60%,
      var(--scene-sky-low)
    );
    color: var(--scene-card-ink);
  }

  dialog.thunder {
    justify-items: end;
    padding-inline-end: var(--size-ceremony-inset);
  }

  dialog::backdrop {
    background: var(--scene-backdrop);
  }
</style>
