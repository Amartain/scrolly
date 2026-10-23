<!-- Bamboo Scraps: a plain scratchpad for loose thoughts. It saves itself on a pause in typing, on
     blur and when the page closes; a small mark says so. One scrap per visit to Seclusion. -->
<script lang="ts">
  import { onMount } from 'svelte';
  import { cutLine } from '../../lib/cut-line';
  import { SECLUSION } from '../../lib/copy-seclusion';
  import { scrapPad } from '../../lib/scrap-pad.svelte';
  import Valve from './Valve.svelte';

  onMount(() => void scrapPad.load());
</script>

<svelte:window onpagehide={scrapPad.unload} />

<Valve id="valve-scraps" title={SECLUSION.scrapsTitle} icon="bamboo" accent="growth" grow>
  <div class="pad">
    <textarea
      data-tour="scraps"
      data-tour-on="input"
      use:cutLine
      value={scrapPad.text}
      placeholder={SECLUSION.scrapsLine}
      aria-label={SECLUSION.scrapsTitle}
      oninput={(event) => scrapPad.type(event.currentTarget.value)}
      onblur={scrapPad.flush}
    ></textarea>
    <!-- One reserved line, so the mark never moves anything. -->
    <p class="mark" role="status">{scrapPad.saved && scrapPad.text ? SECLUSION.scrapSaved : ''}</p>
  </div>
</Valve>

<style>
  .pad {
    flex: 1;
    min-height: 0;
    display: flex;
    flex-direction: column;
    gap: var(--space-1);
    padding: var(--space-3) var(--space-3) var(--space-1);
  }

  /* The box takes everything the other valves leave. */
  textarea {
    flex: 1;
    min-height: calc(var(--size-field) * 3);
    padding: var(--space-3);
    resize: none;
    background: var(--surface-panel);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-sunken);
    color: var(--ink);
    font-family: var(--font-body);
    font-size: var(--text-body-md);
  }

  .mark {
    min-height: var(--space-5);
    margin: 0;
    color: var(--ink-muted);
    font-size: var(--text-body-sm);
  }
</style>
