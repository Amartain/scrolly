<!-- Settings › Symbols: your own emoji and Discord shortcodes for each state and type. -->
<script lang="ts">
  import Button from '../components/Button.svelte';
  import Panel from '../components/Panel.svelte';
  import { putSymbol, type View } from '../lib/api';
  import { SYMBOLS } from '../lib/copy';
  import { view } from '../lib/view.svelte';

  type Group = 'states' | 'types';
  type Symbol = View['legend']['states'][string];

  /** The refusal of this panel's own last change (not the shared notice other panels use). */
  let message = $state('');

  const groups = $derived<[Group, [string, Symbol][]][]>([
    ['states', Object.entries(view.current?.legend.states ?? {})],
    ['types', Object.entries(view.current?.legend.types ?? {})],
  ]);

  /** Saves wait for each other, so two quick edits never overwrite one another. */
  let queue: Promise<unknown> = Promise.resolve();

  function send(command: () => Promise<View>): Promise<boolean> {
    const done = queue.then(() => view.act(command));
    queue = done;
    return done;
  }

  /** Save the one part that changed. A refused one (in use, unreadable) puts the old value back. */
  async function save(
    event: Event & { currentTarget: HTMLInputElement },
    group: Group,
    key: string,
    patch: { emoji?: string; shortcode?: string },
    old: string,
  ) {
    const field = event.currentTarget;
    const done = await send(() => putSymbol(group, key, patch));
    message = done ? '' : view.notice;
    if (!done) field.value = old;
  }

  async function restore(group: Group, key: string) {
    message = (await send(() => putSymbol(group, key))) ? '' : view.notice;
  }
</script>

<Panel title={SYMBOLS.title}>
  <div class="symbols">
    <p class="note">{SYMBOLS.note}</p>
    {#each groups as [group, entries] (group)}
      {#each entries as [key, symbol] (key)}
        {@const label = symbol.label}
        <div class="row">
          <span class="label">{label}</span>
          <input
            class="emoji"
            value={symbol.emoji}
            aria-label="Symbol for {label}"
            onchange={(event) =>
              save(event, group, key, { emoji: event.currentTarget.value }, symbol.emoji)}
          />
          <input
            class="code digits"
            value={symbol.shortcode}
            aria-label="Shortcode for {label}"
            onchange={(event) =>
              save(event, group, key, { shortcode: event.currentTarget.value }, symbol.shortcode)}
          />
          <Button
            label={SYMBOLS.reset}
            description="Restore the default for {label}"
            onclick={() => restore(group, key)}
          />
        </div>
      {/each}
    {/each}
    <p class="note" aria-live="polite">{message}</p>
  </div>
</Panel>

<style>
  .symbols {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
    padding: var(--space-4);
  }

  .row {
    display: flex;
    align-items: center;
    gap: var(--space-3);
  }

  .label {
    flex: 1;
    min-width: 0;
  }

  input {
    height: var(--size-field);
    padding-inline: var(--space-3);
    background: var(--surface-raised);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-sunken);
    color: var(--ink);
    font-family: var(--font-body);
    font-size: var(--text-body-md);
  }

  .emoji {
    width: calc(var(--size-estimate) * 0.8);
    text-align: center;
  }

  .code {
    width: calc(var(--size-estimate) * 2.4);
  }

  .note {
    margin: 0;
    color: var(--ink-muted);
  }
</style>
