<script lang="ts">
  import pavilion from '../assets/headers/pavilion.webp';
  import sereneDay from '../assets/headers/serene-day.webp';
  import sereneDusk from '../assets/headers/serene-dusk.webp';
  import { view } from '../lib/view.svelte';
  import HandscrollIcon from '../icons/HandscrollIcon.svelte';
  import SlidersIcon from '../icons/SlidersIcon.svelte';
  import IconButton from '../components/IconButton.svelte';
  import ThemeOrbs from '../components/ThemeOrbs.svelte';
  import PeakScene from '../components/peak/PeakScene.svelte';

  let { settingsOpen, onsettings }: { settingsOpen: boolean; onsettings: () => void } = $props();

  let now = $state(new Date());
  $effect(() => {
    const timer = setInterval(() => (now = new Date()), 1000);
    return () => clearInterval(timer);
  });

  /** The user's choice of picture. Left undefined ("match the theme"), the live peak shows. */
  const picture = $derived.by(() => {
    const a = view.current?.appearance;
    if (a?.header === 'serene-day') return `url(${sereneDay})`;
    if (a?.header === 'serene-dusk') return `url(${sereneDusk})`;
    if (a?.header === 'pavilion') return `url(${pavilion})`;
    if (a?.header === 'custom') return `url(/api/header-image?v=${a.header_version})`;
    return undefined;
  });

  const time = $derived(
    now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false }),
  );
  const date = $derived(
    now.toLocaleDateString('en-GB', { weekday: 'short', day: 'numeric', month: 'short' }),
  );
</script>

<header class="header" style:background-image={picture}>
  {#if !picture}<PeakScene frame="header" />{/if}
  <div class="plate lacquer-frame">
    <HandscrollIcon />
    <div class="titles">
      <div class="name display">Scrolly</div>
      <div class="tagline display">Path of Cultivation</div>
    </div>
  </div>
  <div class="tools">
    <div class="bar">
      <div class="clock lacquer-frame">
        <div class="time display digits">{time}</div>
        <div class="date">{date}</div>
      </div>
      <span class="settings lacquer-frame">
        <IconButton label="Settings" pressed={settingsOpen} onclick={onsettings}>
          <SlidersIcon />
        </IconButton>
      </span>
    </div>
    <ThemeOrbs placement="header" />
  </div>
</header>

<style>
  .header {
    position: relative;
    isolation: isolate;
    flex: none;
    height: var(--size-header);
    overflow: hidden;
    background-color: var(--surface-panel);
    background-size: cover;
    background-position: center 40%;
    border-bottom: var(--border-width) solid var(--line);
  }

  .plate,
  .clock {
    background: var(--surface-panel);
    background-image: var(--gloss-faint);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-panel);
  }

  .plate {
    position: absolute;
    left: var(--size-gutter);
    bottom: var(--space-4);
    display: flex;
    align-items: center;
    gap: var(--space-3);
    padding: var(--space-2) var(--space-4) var(--space-2) var(--space-3);
  }

  .titles {
    display: flex;
    flex-direction: column;
    gap: var(--space-1);
  }

  .name {
    font-size: var(--text-display-xl);
    line-height: 1;
  }

  .tagline {
    font-size: var(--text-display-md);
    font-weight: 400;
    color: var(--ink-muted);
  }

  /* The clock and Settings, the theme orbs under them. */
  .tools {
    position: absolute;
    right: var(--size-gutter);
    top: var(--space-4);
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: var(--space-2);
  }

  .bar {
    display: flex;
    align-items: stretch;
    gap: var(--space-3);
  }

  .clock {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    justify-content: center;
    padding: var(--space-2) var(--space-3);
  }

  .settings {
    display: flex;
  }

  .time {
    font-size: var(--text-display-lg);
    line-height: 1;
  }

  .date {
    color: var(--ink-muted);
  }
</style>
