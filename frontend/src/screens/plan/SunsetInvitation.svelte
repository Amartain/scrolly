<!-- One-time question in the Day Summary: when does your sunset come? Either answer retires it. -->
<script lang="ts">
  import Button from '../../components/Button.svelte';
  import { SUNSET } from '../../lib/copy';
  import { view } from '../../lib/view.svelte';

  let at = $state('');

  const set = () => view.setSunset({ at: at.trim() || view.current?.sunset.at_text });
</script>

<span class="ask">{SUNSET.ask}</span>
<input
  class="digits"
  bind:value={at}
  placeholder={view.current?.sunset.at_text ?? '21:00'}
  aria-label="Sunset time"
  onkeydown={(event) => event.key === 'Enter' && set()}
/>
<Button label={SUNSET.set} onclick={set} />
<Button label={SUNSET.later} onclick={() => view.setSunset({ enabled: false })} />

<style>
  .ask {
    color: var(--ink-muted);
  }

  input {
    flex: none;
    width: var(--size-estimate);
    height: var(--size-glyph-button);
    padding-inline: var(--space-2);
    background: var(--surface-raised);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-sunken);
    color: var(--ink);
    font-family: var(--font-body);
    font-size: var(--text-body-md);
    text-align: right;
  }
</style>
