<!-- The Dispatch: today's scroll as markdown, exactly as it will be pasted, with the options and Clip to Scroll
     beside it. The options are switches marked with their emoji (postponed and abandoned use the Legend's). -->
<script lang="ts">
  import Button from '../components/Button.svelte';
  import ToggleSwitch from '../components/ToggleSwitch.svelte';
  import { dispatch, type DispatchData } from '../lib/api';
  import { DISPATCH } from '../lib/copy';
  import { DISPATCH_PREVIEW } from '../lib/copy-dispatch';
  import { view } from '../lib/view.svelte';

  let { onback }: { onback: () => void } = $props();

  let scroll = $state<DispatchData | null>(null);
  let message = $state('');
  const states = $derived(view.current?.legend.states);

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
      <pre aria-label="Scroll text">{scroll?.text ?? ''}</pre>
    </div>
    <aside class="side" aria-label={DISPATCH_PREVIEW.options}>
      <ToggleSwitch
        label={DISPATCH.dnd}
        emoji="🌙"
        checked={scroll?.dnd ?? false}
        onchange={(dnd) => choose({ dnd })}
      />
      <ToggleSwitch
        label={DISPATCH.postponed}
        emoji={states?.postponed?.emoji ?? '💤'}
        checked={scroll?.include_postponed ?? false}
        onchange={(include_postponed) => choose({ include_postponed })}
      />
      <ToggleSwitch
        label={DISPATCH.abandoned}
        emoji={states?.lost?.emoji ?? '🍂'}
        checked={scroll?.include_abandoned ?? false}
        onchange={(include_abandoned) => choose({ include_abandoned })}
      />
      <div class="clip">
        <Button label={DISPATCH.clip} tone="primary" size="large" onclick={clip} />
      </div>
      <p class="note" role="status">{message}</p>
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

  /* The scroll is as tall as its text; only a very long day scrolls, on the theme's own scrollbar. */
  .stage {
    min-height: 0;
    overflow-y: auto;
    padding-right: var(--shadow-room);
    padding-bottom: var(--shadow-room);
  }

  .side {
    display: flex;
    flex-direction: column;
    align-items: stretch;
    gap: var(--space-2);
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

  pre {
    margin: 0;
    padding: var(--space-4);
    background: var(--surface-raised);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-sunken);
    font-family: var(--font-body);
    font-size: var(--text-body-md);
    line-height: 1.4;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
  }
</style>
