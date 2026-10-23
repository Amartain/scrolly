<!-- The first screen of each day: the morning scene of the theme, then the one button. The button appears
     early and works at any moment; the title soaks in like ink as the scene ends. Any key or click shows
     the last frame at once (a key also puts the focus on the button). Under reduced motion it is still. -->
<script lang="ts">
  import Button from '../components/Button.svelte';
  import MorningScene from '../components/morning/MorningScene.svelte';
  import { planning } from '../lib/api';
  import { view } from '../lib/view.svelte';

  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  let still = $state(reduced);
  let message = $state<HTMLElement>();

  // Another theme paints its own morning in (owner, 2026-10-23), even after a skip.
  let shownTheme = '';
  $effect(() => {
    const theme = view.current?.appearance.theme ?? '';
    if (shownTheme && theme !== shownTheme) still = reduced;
    shownTheme = theme;
  });

  function skip(event: KeyboardEvent | PointerEvent) {
    if (still) return;
    still = true;
    if (event instanceof KeyboardEvent && event.key !== 'Tab')
      message?.querySelector('button')?.focus();
  }
</script>

<svelte:window onkeydown={skip} onpointerdown={skip} />

<div class="zero">
  <MorningScene {still} />
  <div class="veil">
    <section class="message" class:still aria-label="The Peak is Serene" bind:this={message}>
      <h1 class="display title">The Peak is Serene</h1>
      <div class="begin">
        <Button
          label="Cultivate Your Focus"
          tone="primary"
          size="large"
          tour="cultivate"
          onclick={() => view.act(planning.start)}
        />
      </div>
    </section>
  </div>
</div>

<style>
  .zero {
    position: relative;
    flex: 1;
    min-height: 0;
    display: flex;
    flex-direction: column;
  }

  .veil {
    position: absolute;
    inset: 0;
    display: grid;
    place-items: center;
  }

  /* No frame: the title and the one button float on the painting, a little above the middle. */
  .message {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--space-8);
    margin-bottom: var(--space-12);
  }

  .title {
    margin: 0;
    font-size: var(--text-display-xl);
    text-shadow: var(--space-1) var(--space-1) 0 var(--surface-canvas);
    animation: morning-soak 1000ms 2300ms ease-out both;
  }

  .begin {
    animation: morning-fade 400ms 1200ms ease-out both;
  }

  .still .title,
  .still .begin {
    animation: none;
  }
</style>
