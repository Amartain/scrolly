<script lang="ts">
  import Button from '../../components/Button.svelte';
  import GlyphButton from '../../components/GlyphButton.svelte';
  import GuidanceButton from '../../components/GuidanceButton.svelte';
  import GlyphIcon from '../../icons/GlyphIcon.svelte';
  import ThemeOrbs from '../../components/ThemeOrbs.svelte';
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

<!-- A slim strip of frosted paper over the peak: Step out, the plaque, the orbs (another theme paints
     its own peak), the clock and full screen. The sun itself is in the painting now. -->
<header class="bar gold-foot">
  <Button label={SECLUSION.stepOut} description="Step out of Seclusion" onclick={onleave} />
  <h1 class="title display plaque">{SECLUSION.title}</h1>
  <GuidanceButton topic="seclusion" />
  <span class="tagline">{SECLUSION.tagline}</span>
  <ThemeOrbs placement="header" />
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
    margin: var(--space-3) var(--size-gutter) 0;
    padding-inline: var(--space-3);
    background: var(--seclusion-frost);
    backdrop-filter: var(--seclusion-blur);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-panel);
  }

  /* A dark plaque on the light strip, as the dashboard's panel titles sit on their bands. */
  .title {
    margin: 0;
    background: var(--head-bg);
    color: var(--head-ink);
    font-size: var(--text-display-md);
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
