<!-- The Parallel sidebar: Parallel Flow, Scribe Trial and Bamboo Scraps on one scroll, each its own card,
     so nothing pulls the user out of the trial. It folds as a whole to a slim strip (its button or
     Ctrl+B, as in VS Code); the strip's marks open it on that section. The server keeps the choice;
     a new room starts folded, so the peak is seen. -->
<script lang="ts">
  import { tick } from 'svelte';
  import GlyphButton from '../../components/GlyphButton.svelte';
  import GuidanceButton from '../../components/GuidanceButton.svelte';
  import GlyphIcon from '../../icons/GlyphIcon.svelte';
  import { SECLUSION } from '../../lib/copy-seclusion';
  import { scrapPad } from '../../lib/scrap-pad.svelte';
  import { seclusion } from '../../lib/seclusion.svelte';
  import ParallelPanel from './ParallelPanel.svelte';
  import ScrapsPanel from './ScrapsPanel.svelte';
  import ScribeBox from './ScribeBox.svelte';

  const SECTIONS = [
    { id: 'valve-parallel', title: SECLUSION.parallelTitle, icon: 'parallel' },
    { id: 'valve-scribe', title: SECLUSION.scribeTitle, icon: 'brush' },
    { id: 'valve-scraps', title: SECLUSION.scrapsTitle, icon: 'bamboo' },
  ] as const;

  const folded = $derived(seclusion.state?.sidebar_hidden ?? false);

  async function fold(hidden: boolean) {
    if (hidden) await scrapPad.flush(); // what is written is saved before the pad goes away
    await seclusion.hideSidebar(hidden);
  }

  async function openAt(id: string) {
    await fold(false);
    await tick();
    const field = document.querySelector<HTMLElement>(`#${id} :is(input, textarea, button)`);
    field?.focus();
  }

  function onkeydown(event: KeyboardEvent) {
    const ctrl = event.ctrlKey || event.metaKey;
    if (!ctrl || event.altKey || event.shiftKey || event.key.toLowerCase() !== 'b') return;
    event.preventDefault();
    void fold(!folded);
  }
</script>

<svelte:window {onkeydown} />

{#if folded}
  <nav class="strip" aria-label={SECLUSION.sidebar.name}>
    <GlyphButton label={SECLUSION.sidebar.show} expanded={false} onclick={() => fold(false)}>
      <GlyphIcon name="sidebar" />
    </GlyphButton>
    <span class="rule" aria-hidden="true"></span>
    {#each SECTIONS as section (section.id)}
      <GlyphButton label={SECLUSION.sidebar.open(section.title)} onclick={() => openAt(section.id)}>
        <GlyphIcon name={section.icon} />
      </GlyphButton>
    {/each}
  </nav>
{:else}
  <aside class="sidebar" aria-label={SECLUSION.sidebar.name}>
    <div class="roller">
      <GuidanceButton topic="sidebar" />
      <GlyphButton label={SECLUSION.sidebar.hide} expanded={true} onclick={() => fold(true)}>
        <GlyphIcon name="sidebar" />
      </GlyphButton>
    </div>
    <div class="cards">
      <ParallelPanel />
      <ScribeBox />
      <ScrapsPanel />
    </div>
  </aside>
{/if}

<style>
  /* It floats at the right over the peak, frosted like the card, so folding it moves nothing. */
  .sidebar,
  .strip {
    position: absolute;
    right: var(--size-gutter);
    display: flex;
    flex-direction: column;
    min-height: 0;
    background: var(--seclusion-frost);
    backdrop-filter: var(--seclusion-blur);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-panel);
  }

  .sidebar {
    top: calc(var(--size-seclusion-bar) + var(--space-3) + var(--space-4));
    bottom: var(--space-8);
    width: var(--size-seclusion-side);
  }

  .strip {
    top: 50%;
    transform: translateY(-50%);
  }

  @media (max-width: 60rem) {
    .sidebar,
    .strip {
      position: static;
      width: auto;
      margin: var(--space-4) var(--size-gutter);
      transform: none;
    }

    .strip {
      flex-direction: row;
    }
  }

  /* The scroll's roller: a dark band with gold ends, holding the `?` and the fold. */
  .roller {
    position: relative;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-2) var(--space-5);
    background: var(--head-bg);
    border-bottom: var(--border-width) solid var(--line);
  }

  .roller::before,
  .roller::after {
    content: '';
    position: absolute;
    top: 50%;
    width: var(--space-2);
    height: var(--space-6);
    background: var(--gold);
    border: var(--border-width) solid var(--line);
    transform: translateY(-50%);
  }

  .roller::before {
    left: var(--space-1);
  }

  .roller::after {
    right: var(--space-1);
  }

  .cards {
    flex: 1;
    min-height: 0;
    display: flex;
    flex-direction: column;
    gap: var(--space-3);
    padding: var(--space-3);
  }

  .strip {
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-2);
  }

  .rule {
    width: 100%;
    border-top: var(--border-width) solid var(--grid);
  }
</style>
