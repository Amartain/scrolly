<script lang="ts">
  import Button from '../components/Button.svelte';
  import Panel from '../components/Panel.svelte';
  import ToggleChoice from '../components/ToggleChoice.svelte';
  import { advisor } from '../lib/api';
  import { playChime } from '../lib/chime';
  import { ADVISOR, SUNSET } from '../lib/copy';
  import { view } from '../lib/view.svelte';

  const sunset = $derived(view.current?.sunset);
  let at = $state('');
  let message = $state('');

  $effect(() => {
    at = sunset?.at_text ?? '';
  });

  async function save() {
    const ok = await view.setSunset({ at });
    message = ok ? '' : SUNSET.hint;
    if (ok) view.notice = '';
  }
</script>

<Panel title="Sunset">
  <div class="body">
    <ToggleChoice
      label="Keep a sunset"
      checked={sunset?.enabled ?? false}
      onchange={(enabled) => view.setSunset({ enabled })}
    />
    <input
      class="digits"
      bind:value={at}
      aria-label="Sunset time"
      disabled={!sunset?.enabled}
      onkeydown={(event) => event.key === 'Enter' && save()}
    />
    <Button label="Set" onclick={save} disabled={!sunset?.enabled} />
    <ToggleChoice
      label="Chime at sunset"
      checked={sunset?.chime ?? false}
      onchange={(chime) => view.setSunset({ chime })}
    />
    <Button label="Test chime" onclick={playChime} />
    <Button
      label={ADVISOR.wake}
      disabled={!view.current?.advisor.silenced}
      onclick={() => view.act(() => advisor.silence(false))}
    />
    <p class="note" aria-live="polite">{message || (sunset?.enabled ? '' : SUNSET.off)}</p>
  </div>
</Panel>

<style>
  .body {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: var(--space-4);
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

  input:disabled {
    color: var(--ink-faint);
  }

  .note {
    margin: 0;
    color: var(--ink-muted);
  }
</style>
