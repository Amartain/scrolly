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

  $effect(() => {
    const opener = document.activeElement;
    dialog?.showModal();
    return () => {
      dialog?.close();
      if (opener instanceof HTMLElement) opener.focus();
    };
  });
</script>

<dialog
  bind:this={dialog}
  aria-label={title}
  onkeydown={(event) => {
    if (event.key !== 'Escape') return;
    event.preventDefault();
    onclose();
  }}
  oncancel={(event) => {
    event.preventDefault();
    onclose();
  }}
>
  <Panel {title} {tone} scroll striped>
    {#snippet actions()}
      <GlyphButton label="Close {title}" onclick={onclose}>
        <GlyphIcon name="x" />
      </GlyphButton>
    {/snippet}
    {@render children()}
  </Panel>
</dialog>
