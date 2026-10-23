<!-- Settings › Seclusion: how soon the full way up (the climb or the summon) shows again. Until then a
     quick way up; 0 shows it every time (lib/travel.ts). -->
<script lang="ts">
  import Button from '../components/Button.svelte';
  import Panel from '../components/Panel.svelte';
  import { putTravel } from '../lib/seclusion-api';
  import { TRAVEL } from '../lib/copy-seclusion';
  import { view } from '../lib/view.svelte';

  const interval = $derived(view.current?.travel.interval_min);
  let minutes = $state('');
  let message = $state('');

  $effect(() => {
    minutes = String(interval ?? '');
  });

  async function save() {
    const value = Number(minutes.trim() || Number.NaN);
    if (!Number.isInteger(value)) {
      message = TRAVEL.whole;
      return;
    }
    const ok = await view.act(() => putTravel({ interval_min: value }));
    message = ok ? '' : view.notice;
  }
</script>

<Panel title={TRAVEL.title}>
  <div class="body">
    <label for="travel-interval">{TRAVEL.label}</label>
    <input
      id="travel-interval"
      class="digits"
      inputmode="numeric"
      bind:value={minutes}
      onkeydown={(event) => event.key === 'Enter' && save()}
    />
    <span>{TRAVEL.unit}</span>
    <Button label="Set" onclick={save} />
    <p class="note" aria-live="polite">{message || TRAVEL.hint}</p>
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
    flex: none;
    width: var(--size-estimate);
    height: var(--size-field);
    padding-inline: var(--space-3);
    background: var(--surface-raised);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-sunken);
    color: var(--ink);
    font-family: var(--font-body);
    font-size: var(--text-body-md);
    text-align: right;
  }

  .note {
    flex-basis: 100%;
    margin: 0;
    color: var(--ink-muted);
  }
</style>
