<!-- A sudden trial, exactly as on the dashboard: it lands on top of Remaining. Enter inscribes. -->
<script lang="ts">
  import Button from '../../components/Button.svelte';
  import { today } from '../../lib/api';
  import { playTick } from '../../lib/chime';
  import { SECLUSION } from '../../lib/copy-seclusion';
  import { seclusion } from '../../lib/seclusion.svelte';
  import Valve from './Valve.svelte';

  const TOAST_MS = 2500;

  let title = $state('');
  let saved = $state(false);
  let toastTimer: ReturnType<typeof setTimeout> | undefined;

  async function inscribe(event?: Event) {
    event?.preventDefault();
    if (!title.trim()) return;
    if (!(await seclusion.trial(() => today.scribe(title, '', '')))) return;
    title = '';
    playTick();
    saved = true;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => (saved = false), TOAST_MS);
  }
</script>

<Valve id="valve-scribe" title={SECLUSION.scribeTitle} icon="brush" accent="gold">
  <form class="scribe" onsubmit={inscribe}>
    <div class="row">
      <input
        id="seclusion-scribe"
        class="title"
        bind:value={title}
        placeholder={SECLUSION.scribePlaceholder}
        aria-label={SECLUSION.scribeLabel}
        autocomplete="off"
      />
      <Button label={SECLUSION.inscribe} tone="primary" tour="scribe" onclick={inscribe} />
    </div>
    <!-- One reserved line, so the confirmation never moves anything. -->
    <p class="toast" role="status">{saved ? SECLUSION.inscribed : ''}</p>
  </form>
</Valve>

<style>
  .scribe {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
    padding: var(--space-3) var(--space-4);
  }

  .row {
    display: flex;
    gap: var(--space-3);
  }

  .title {
    flex: 1;
    min-width: 0;
    height: var(--size-field);
    padding-inline: var(--space-3);
    background: var(--surface-raised);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-sunken);
    color: var(--ink);
    font-size: var(--text-body-md);
  }

  .toast {
    min-height: var(--space-6);
    margin: 0;
    color: var(--ink-muted);
  }
</style>
