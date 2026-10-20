<!-- The Dispatch: today's scroll as Discord markdown, with a live preview and Clip to Scroll. -->
<script lang="ts">
  import Button from '../components/Button.svelte';
  import Panel from '../components/Panel.svelte';
  import ToggleChoice from '../components/ToggleChoice.svelte';
  import { dispatch, type DispatchData } from '../lib/api';
  import { DISPATCH } from '../lib/copy';

  let { onback }: { onback: () => void } = $props();

  let scroll = $state<DispatchData | null>(null);
  let message = $state('');

  $effect(() => {
    void dispatch.get().then((data) => (scroll = data));
  });

  async function choose(patch: Parameters<typeof dispatch.set>[0]) {
    scroll = await dispatch.set(patch);
  }

  async function clip() {
    if (!scroll) return;
    try {
      await navigator.clipboard.writeText(scroll.text);
      message = DISPATCH.clipped;
    } catch {
      message = DISPATCH.unclipped;
    }
  }
</script>

<div class="dispatch">
  <div class="bar">
    <h1 class="display title">{DISPATCH.title}</h1>
    <Button label={DISPATCH.back} onclick={onback} />
  </div>
  <div class="options">
    <ToggleChoice
      label={DISPATCH.dnd}
      checked={scroll?.dnd ?? false}
      onchange={(dnd) => choose({ dnd })}
    />
    <ToggleChoice
      label={DISPATCH.postponed}
      checked={scroll?.include_postponed ?? false}
      onchange={(include_postponed) => choose({ include_postponed })}
    />
    <ToggleChoice
      label={DISPATCH.abandoned}
      checked={scroll?.include_abandoned ?? false}
      onchange={(include_abandoned) => choose({ include_abandoned })}
    />
    <Button label={DISPATCH.clip} tone="primary" onclick={clip} />
    <p class="note" role="status">{message}</p>
  </div>
  <Panel title="Preview" scroll>
    <pre class="preview" aria-label="Scroll text">{scroll?.text ?? ''}</pre>
  </Panel>
</div>

<style>
  .dispatch {
    flex: 1;
    min-height: 0;
    display: flex;
    flex-direction: column;
    gap: var(--space-4);
    padding: var(--space-4) var(--size-gutter) var(--shadow-room);
  }

  .bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .title {
    margin: 0;
    font-size: var(--text-display-lg);
  }

  .options {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: var(--space-4);
  }

  .note {
    margin: 0;
    color: var(--ink-muted);
  }

  .preview {
    margin: 0;
    padding: var(--space-4);
    font-family: var(--font-body);
    font-size: var(--text-body-md);
    white-space: pre-wrap;
    overflow-wrap: anywhere;
  }

  :global(.dispatch section.panel) {
    flex: 1;
    margin-right: var(--shadow-room);
  }
</style>
