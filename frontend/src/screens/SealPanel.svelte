<!-- Settings › Secret Seal Inscription: words that do something unusual. Unknown words do nothing. -->
<script lang="ts">
  import Button from '../components/Button.svelte';
  import Panel from '../components/Panel.svelte';
  import { inscribeSeal } from '../lib/api';
  import { SEAL } from '../lib/copy';
  import { view } from '../lib/view.svelte';

  /** Called after a seal took effect, so the screen under Settings can show what it did. */
  let { ondone }: { ondone: () => void } = $props();

  let words = $state('');
  let message = $state('');

  async function inscribe() {
    if (!words.trim()) return;
    const result = await inscribeSeal(words);
    view.show(result.view);
    view.preview = result.victory_preview ?? null;
    if (result.recognized) {
      words = '';
      message = '';
      ondone();
    } else {
      message = SEAL.unknown;
    }
  }
</script>

<Panel title={SEAL.title}>
  <div class="body">
    <input
      bind:value={words}
      placeholder={SEAL.placeholder}
      aria-label="Secret seal words"
      autocomplete="off"
      spellcheck="false"
      onkeydown={(event) => event.key === 'Enter' && inscribe()}
    />
    <Button label={SEAL.inscribe} onclick={inscribe} />
    <p class="note" aria-live="polite">{message}</p>
  </div>
</Panel>

<style>
  .body {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: var(--space-3);
    padding: var(--space-4);
  }

  input {
    flex: 1;
    min-width: 0;
    height: var(--size-field);
    padding-inline: var(--space-3);
    background: var(--surface-raised);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-sunken);
    color: var(--ink);
    font-family: var(--font-body);
    font-size: var(--text-body-md);
  }

  .note {
    flex-basis: 100%;
    margin: 0;
    color: var(--ink-muted);
  }
</style>
