<!-- A guidance scroll: why (the Dao), how (the Art) and the words in plain language. Closes with its
     button, Esc or a click outside, and focus goes back to the `?` that opened it. -->
<script lang="ts">
  import { GUIDANCE, GUIDE } from '../lib/copy-guidance';
  import { guidance } from '../lib/guidance.svelte';
  import Button from './Button.svelte';
  import Modal from './Modal.svelte';

  const guide = $derived(guidance.topic ? GUIDE[guidance.topic] : null);
</script>

{#if guide}
  <Modal title={GUIDANCE.title(guide.name)} onclose={guidance.close}>
    <div class="sheet">
      <section>
        <h3 class="display">{GUIDANCE.dao}</h3>
        <p class="read">{guide.dao}</p>
      </section>
      <section>
        <h3 class="display">{GUIDANCE.art}</h3>
        <p class="read">{guide.art}</p>
      </section>
      <section>
        <h3 class="display">{GUIDANCE.terms}</h3>
        <dl class="read">
          {#each guide.terms as [term, meaning] (term)}
            <dt>{term}</dt>
            <dd>{meaning}</dd>
          {/each}
        </dl>
      </section>
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
    max-width: 34rem;
    padding: var(--space-5) var(--space-6);
  }

  h3 {
    margin: 0;
    margin-bottom: var(--space-1);
    color: var(--ink-muted);
    font-size: var(--text-display-sm);
  }

  p,
  dl,
  dd {
    margin: 0;
  }

  dt {
    font-weight: bold;
  }

  dd {
    margin-bottom: var(--space-2);
  }

  .close {
    display: flex;
    justify-content: flex-end;
  }
</style>
