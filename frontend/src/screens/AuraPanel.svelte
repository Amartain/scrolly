<!-- Settings › Aura, for players only (domain/player.py): the robe and the glow, each a row of orbs
     like the theme orbs (the first orb is the theme's own), and whether the glow shines always. -->
<script lang="ts">
  import Panel from '../components/Panel.svelte';
  import { AURA } from '../lib/copy-player';
  import { auraToken, playerApi, type AuraColour } from '../lib/player-api';
  import { view } from '../lib/view.svelte';

  const player = $derived(view.current?.player);

  type Patch = { robe?: AuraColour | null; glow?: AuraColour | null; on?: boolean };
  let saving: Promise<unknown> = Promise.resolve();

  /** One save at a time, each from the answer to the last: two quick clicks keep both choices. */
  function save(patch: Patch) {
    saving = saving.then(() => {
      const now = view.current?.player;
      if (!now) return;
      const robe = patch.robe === undefined ? now.robe : patch.robe;
      const glow = patch.glow === undefined ? now.glow : patch.glow;
      return view.act(() => playerApi.aura(robe, glow, patch.on ?? now.glow_on));
    });
  }
</script>

{#snippet orbs(part: 'robe' | 'glow', chosen: AuraColour | null)}
  <div class="row">
    <span class="part display">{part === 'robe' ? AURA.robe : AURA.glow}</span>
    <div class="orbs" role="group" aria-label={part === 'robe' ? AURA.robe : AURA.glow}>
      <button
        class="orb own"
        aria-label="{part === 'robe' ? AURA.robe : AURA.glow}: {AURA.own}"
        aria-pressed={chosen === null}
        title={AURA.own}
        onclick={() => save({ [part]: null })}
      ></button>
      {#each player?.colours ?? [] as colour (colour)}
        <button
          class="orb"
          style:background={auraToken(colour)}
          aria-label="{part === 'robe' ? AURA.robe : AURA.glow}: {AURA.names[colour]}"
          aria-pressed={chosen === colour}
          title={AURA.names[colour]}
          onclick={() => save({ [part]: colour })}
        ></button>
      {/each}
    </div>
  </div>
{/snippet}

{#if player?.is_player}
  <Panel title={AURA.title}>
    <div class="body">
      <p class="note">{AURA.note}</p>
      {@render orbs('robe', player.robe)}
      {@render orbs('glow', player.glow)}
      <label class="shine">
        <input
          type="checkbox"
          checked={player.glow_on}
          onchange={(event) => save({ on: event.currentTarget.checked })}
        />
        {AURA.shine}
      </label>
    </div>
  </Panel>
{/if}

<style>
  .body {
    display: flex;
    flex-direction: column;
    gap: var(--space-3);
    padding: var(--space-4);
  }

  .note {
    margin: 0;
    color: var(--ink-muted);
    font-size: var(--text-body-md);
  }

  .row {
    display: flex;
    align-items: center;
    gap: var(--space-4);
  }

  .part {
    width: var(--size-estimate);
    font-size: var(--text-display-sm);
  }

  .orbs {
    display: flex;
    flex-wrap: wrap;
    gap: var(--space-3);
  }

  .orb {
    width: var(--size-orb);
    height: var(--size-orb);
    padding: 0;
    border: var(--border-width) solid var(--line);
    border-radius: 50%;
    box-shadow: var(--shadow-button);
    cursor: pointer;
  }

  /* The theme's own: an empty dashed ring, so it never reads as a colour (cream is one). */
  .own {
    background: transparent;
    border-style: dashed;
    box-shadow: none;
  }

  .orb[aria-pressed='true'] {
    outline: var(--border-width) solid var(--gold);
    outline-offset: var(--space-1);
  }

  .orb:active {
    transform: translate(var(--shadow-offset), var(--shadow-offset));
    box-shadow: none;
  }

  .shine {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    font-size: var(--text-body-md);
    cursor: pointer;
  }
</style>
