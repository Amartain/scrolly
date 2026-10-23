<!-- Settings › Header: behind the title plate, the theme's live peak, or a picture of your own. The three
     built-in pictures were retired for the peak (owner, 2026-10-23). -->
<script lang="ts">
  import Button from '../components/Button.svelte';
  import Panel from '../components/Panel.svelte';
  import RadioChoice from '../components/RadioChoice.svelte';
  import { putHeader, uploadHeader, type HeaderChoice, type View } from '../lib/api';
  import { HEADER } from '../lib/copy';
  import { view } from '../lib/view.svelte';

  const choices: { value: HeaderChoice; label: string }[] = [{ value: 'auto', label: HEADER.auto }];

  const appearance = $derived(view.current?.appearance);
  let picker: HTMLInputElement;
  /** The refusal of this panel's own last action (not the shared notice other panels use). */
  let message = $state('');

  async function run(command: () => Promise<View>) {
    message = (await view.act(command)) ? '' : view.notice;
  }

  async function chosen() {
    const file = picker.files?.[0];
    picker.value = '';
    if (file) await run(() => uploadHeader(file));
  }
</script>

<Panel title={HEADER.title}>
  <div class="body">
    <div class="choices">
      {#each choices as choice (choice.value)}
        <RadioChoice
          name="header"
          label={choice.label}
          checked={appearance?.header === choice.value}
          onchange={() => run(() => putHeader(choice.value))}
        />
      {/each}
      <RadioChoice
        name="header"
        label={HEADER.custom}
        checked={appearance?.header === 'custom'}
        disabled={(appearance?.header_version ?? 0) === 0}
        onchange={() => run(() => putHeader('custom'))}
      />
    </div>
    <div class="upload">
      <Button label={HEADER.choose} onclick={() => picker.click()} />
      <input
        bind:this={picker}
        type="file"
        accept="image/png,image/jpeg,image/webp"
        hidden
        aria-label="Header picture"
        onchange={chosen}
      />
      <p class="note" aria-live="polite">{message || HEADER.hint}</p>
    </div>
  </div>
</Panel>

<style>
  .body {
    display: flex;
    flex-direction: column;
    gap: var(--space-4);
    padding: var(--space-4);
  }

  .choices,
  .upload {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: var(--space-3);
  }

  .note {
    margin: 0;
    color: var(--ink-muted);
  }
</style>
