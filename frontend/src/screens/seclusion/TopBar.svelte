<script lang="ts">
  import Button from '../../components/Button.svelte';
  import GlyphButton from '../../components/GlyphButton.svelte';
  import GuidanceButton from '../../components/GuidanceButton.svelte';
  import GlyphIcon from '../../icons/GlyphIcon.svelte';
  import { SECLUSION } from '../../lib/copy-seclusion';

  let { onleave }: { onleave: () => void } = $props();

  let now = $state(new Date());
  $effect(() => {
    const timer = setInterval(() => (now = new Date()), 1000);
    return () => clearInterval(timer);
  });

  const time = $derived(
    now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false }),
  );

  async function toggleFullScreen() {
    try {
      if (document.fullscreenElement) await document.exitFullscreen();
      else await document.documentElement.requestFullscreen();
    } catch {
      // The browser may refuse; the room works the same without it.
    }
  }
</script>

<header class="bar">
  <Button label={SECLUSION.stepOut} description="Step out of Seclusion" onclick={onleave} />
  <h1 class="title display">{SECLUSION.title}</h1>
  <GuidanceButton topic="seclusion" />
  <span class="tagline">{SECLUSION.tagline}</span>
  <span class="clock display digits">{time}</span>
  <GlyphButton label={SECLUSION.fullScreen} onclick={toggleFullScreen}>
    <GlyphIcon name="fullscreen" />
  </GlyphButton>
</header>

<style>
  .bar {
    flex: none;
    display: flex;
    align-items: center;
    gap: var(--space-4);
    height: var(--size-seclusion-bar);
    padding-inline: var(--size-gutter);
    background: var(--surface-panel);
    border-bottom: var(--border-width) solid var(--line);
  }

  .title {
    margin: 0;
    font-size: var(--text-display-lg);
    letter-spacing: 0.3em;
  }

  .tagline {
    flex: 1;
    color: var(--ink-muted);
  }

  .clock {
    font-size: var(--text-display-lg);
  }
</style>
