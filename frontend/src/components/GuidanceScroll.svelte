<!-- A guidance scroll: why (the Dao), how (the Art), the words in plain language and, where a screen has
     shortcuts, its keys. Each part opens with a chip in one of the theme's colours, so the parts are
     found at a glance. Closes with its button, Esc or a click outside, and focus goes back to the `?`. -->
<script lang="ts">
  import { GUIDANCE, GUIDE } from '../lib/copy-guidance';
  import { guidance } from '../lib/guidance.svelte';
  import Button from './Button.svelte';
  import Modal from './Modal.svelte';

  const guide = $derived(guidance.topic ? GUIDE[guidance.topic] : null);
  const keys = $derived(guide && 'keys' in guide ? guide.keys : []);
</script>

{#if guide}
  <Modal title={GUIDANCE.title(guide.name)} onclose={guidance.close}>
    <div class="sheet">
      <section class="part dao">
        <h3 class="chip display">{GUIDANCE.dao}</h3>
        <p class="read">{guide.dao}</p>
      </section>
      <section class="part art">
        <h3 class="chip display">{GUIDANCE.art}</h3>
        <p class="read">{guide.art}</p>
      </section>
      <section class="part terms">
        <h3 class="chip display">{GUIDANCE.terms}</h3>
        <dl class="read">
          {#each guide.terms as [term, meaning] (term)}
            <div class="pair">
              <dt>{term}</dt>
              <dd>{meaning}</dd>
            </div>
          {/each}
        </dl>
      </section>
      {#if keys.length > 0}
        <section class="part keys">
          <h3 class="chip display">{GUIDANCE.keys}</h3>
          <dl class="read">
            {#each keys as [key, what] (key)}
              <div class="pair key-pair">
                <dt><kbd class="digits">{key}</kbd></dt>
                <dd>{what}</dd>
              </div>
            {/each}
          </dl>
        </section>
      {/if}
      <div class="close">
        <Button label={GUIDANCE.close} tone="primary" onclick={guidance.close} />
      </div>
    </div>
  </Modal>
{/if}

<style>
  .sheet {
    display: flex;
    flex-direction: column;
    gap: var(--space-4);
    max-width: 36rem;
    padding: var(--space-5) var(--space-6);
  }

  .part {
    --chip-bg: var(--gold);
    --chip-ink: var(--on-gold);
    padding-left: var(--space-3);
    border-left: var(--space-1) solid var(--chip-bg);
  }

  .art {
    --chip-bg: var(--growth);
    --chip-ink: var(--on-growth);
  }

  .terms {
    --chip-bg: var(--entry-dispatch-bg);
    --chip-ink: var(--entry-dispatch-ink);
  }

  .keys {
    --chip-bg: var(--head-bg);
    --chip-ink: var(--head-ink);
  }

  .chip {
    display: inline-block;
    margin: 0;
    margin-bottom: var(--space-2);
    padding: var(--space-1) var(--space-3);
    background: var(--chip-bg);
    color: var(--chip-ink);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-button);
    font-size: var(--text-display-sm);
  }

  p,
  dl,
  dd {
    margin: 0;
  }

  .pair {
    padding-block: var(--space-1);
  }

  dt {
    color: var(--growth-text);
    font-weight: bold;
  }

  .key-pair {
    display: flex;
    align-items: baseline;
    gap: var(--space-3);
  }

  .key-pair dt {
    flex: none;
    min-width: 6rem;
  }

  kbd {
    display: inline-block;
    padding-inline: var(--space-2);
    background: var(--surface-raised);
    color: var(--ink);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-button);
    font-size: var(--text-body-sm);
    font-weight: normal;
  }

  .close {
    display: flex;
    justify-content: flex-end;
  }
</style>
