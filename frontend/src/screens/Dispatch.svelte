<!-- The Dispatch: today's scroll as your companions will see it in Discord, with the options and Clip to
     Scroll beside it. The raw markdown waits behind "Show markdown". -->
<script lang="ts">
  import Button from '../components/Button.svelte';
  import ToggleChoice from '../components/ToggleChoice.svelte';
  import { dispatch, type DispatchData } from '../lib/api';
  import { DISPATCH } from '../lib/copy';
  import { DISPATCH_PREVIEW } from '../lib/copy-dispatch';
  import DiscordMessage from './dispatch/DiscordMessage.svelte';

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
  <div class="columns">
    <div class="stage">
      {#if scroll}<DiscordMessage text={scroll.text} />{/if}
    </div>
    <aside class="side" aria-label={DISPATCH_PREVIEW.options}>
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
      <div class="clip">
        <Button label={DISPATCH.clip} tone="primary" size="large" onclick={clip} />
      </div>
      <p class="note" role="status">{message}</p>
      <details class="raw">
        <summary class="display">{DISPATCH_PREVIEW.markdown}</summary>
        <pre aria-label="Scroll text">{scroll?.text ?? ''}</pre>
      </details>
    </aside>
  </div>
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

  .columns {
    flex: 1;
    min-height: 0;
    display: grid;
    grid-template-columns: minmax(0, 3fr) minmax(0, 2fr);
    gap: var(--space-6);
  }

  .stage {
    min-height: 0;
    overflow-y: auto;
    padding-right: var(--shadow-room);
    scrollbar-width: thin;
    scrollbar-color: var(--scrollbar-thumb) var(--scrollbar-track);
  }

  .side {
    display: flex;
    flex-direction: column;
    align-items: stretch;
    gap: var(--space-3);
    min-height: 0;
    padding-right: var(--shadow-room);
  }

  .clip {
    display: grid;
    margin-top: var(--space-3);
  }

  .note {
    min-height: var(--size-row);
    margin: 0;
    color: var(--ink-muted);
  }

  .raw {
    min-height: 0;
    overflow-y: auto;
  }

  summary {
    color: var(--ink-muted);
    font-size: var(--text-display-sm);
    cursor: pointer;
  }

  pre {
    margin: var(--space-2) 0 0;
    padding: var(--space-3);
    background: var(--surface-raised);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-sunken);
    font-family: var(--font-body);
    font-size: var(--text-body-sm);
    white-space: pre-wrap;
    overflow-wrap: anywhere;
  }
</style>
