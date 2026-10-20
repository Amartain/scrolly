<!-- The speaker button. The volume and the mute stay out of sight until it is pressed; Esc or a press
     elsewhere closes them. One volume and one mute for every sound of the room (and the sunset chime's loudness). -->
<script lang="ts">
  import GlyphButton from '../../components/GlyphButton.svelte';
  import ToggleChoice from '../../components/ToggleChoice.svelte';
  import GlyphIcon from '../../icons/GlyphIcon.svelte';
  import { playTick } from '../../lib/chime';
  import { SECLUSION } from '../../lib/copy-seclusion';
  import { view } from '../../lib/view.svelte';

  let open = $state(false);
  let wrap: HTMLDivElement | undefined = $state();
  const sound = $derived(view.current?.sound ?? { volume: 60, muted: false });

  function onwindowclick(event: MouseEvent) {
    if (open && wrap && event.target instanceof Node && !wrap.contains(event.target)) open = false;
  }

  function onkeydown(event: KeyboardEvent) {
    if (!open || event.key !== 'Escape') return;
    open = false;
    event.stopPropagation(); // the room stays; only the volume closes
  }

  // Released, not dragged: one save, and a tick at the new level so it can be heard.
  async function setVolume(volume: number) {
    if (await view.setSound({ volume })) playTick();
  }
</script>

<svelte:window onclick={onwindowclick} />

<div class="sound" role="presentation" bind:this={wrap} {onkeydown}>
  <GlyphButton label={SECLUSION.sound} onclick={() => (open = !open)}>
    <GlyphIcon name={sound.muted ? 'muted' : 'speaker'} />
  </GlyphButton>
  {#if open}
    <div class="popover" role="group" aria-label={SECLUSION.sound}>
      <label class="volume display">
        {SECLUSION.volume}
        <input
          type="range"
          min="0"
          max="100"
          step="5"
          value={sound.volume}
          aria-label={SECLUSION.volume}
          onchange={(event) => setVolume(Number(event.currentTarget.value))}
        />
      </label>
      <ToggleChoice
        label={SECLUSION.mute}
        checked={sound.muted}
        onchange={(muted) => view.setSound({ muted })}
      />
    </div>
  {/if}
</div>

<style>
  .sound {
    position: relative;
  }

  .popover {
    position: absolute;
    top: calc(100% + var(--space-2));
    right: 0;
    z-index: 5;
    display: flex;
    flex-direction: column;
    gap: var(--space-3);
    width: var(--size-popover);
    padding: var(--space-4);
    background: var(--surface-raised);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-panel);
  }

  .volume input {
    accent-color: var(--growth);
  }

  .volume {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
    font-size: var(--text-display-sm);
  }
</style>
