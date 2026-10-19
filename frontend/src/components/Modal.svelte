<!-- A panel that opens over the screen. Escape or the close button closes it; focus returns to the opener. -->
<script lang="ts">
  import type { Snippet } from 'svelte';
  import GlyphIcon from '../icons/GlyphIcon.svelte';
  import GlyphButton from './GlyphButton.svelte';
  import Panel from './Panel.svelte';

  type Tone = 'neutral' | 'horizon' | 'foundational' | 'restorative' | 'conquered';

  let {
    title,
    tone = 'neutral',
    onclose,
    children,
  }: { title: string; tone?: Tone; onclose: () => void; children: Snippet } = $props();

  let dialog = $state<HTMLDialogElement>();

  $effect(() => dialog?.showModal());
</script>

<dialog bind:this={dialog} aria-label={title} {onclose}>
  <Panel {title} {tone} scroll striped>
    {#snippet actions()}
      <GlyphButton label="Close {title}" onclick={() => dialog?.close()}>
        <GlyphIcon name="x" />
      </GlyphButton>
    {/snippet}
    {@render children()}
  </Panel>
</dialog>

<style>
  dialog {
    width: min(100% - var(--space-6) * 2, 48rem);
    max-height: 80dvh;
    padding: 0;
    background: transparent;
    border: 0;
    color: var(--ink);
  }

  dialog[open] {
    display: flex;
    flex-direction: column;
  }

  dialog :global(.panel) {
    flex: 1;
  }

  dialog::backdrop {
    background: color-mix(in srgb, var(--surface-panel) 55%, transparent);
    backdrop-filter: blur(var(--space-2));
  }
</style>
