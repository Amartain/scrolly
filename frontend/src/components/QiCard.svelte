<!-- After a conquest: how much qi it took, on a slider that starts at the estimate. Closing it keeps the
     estimate; the back arrow takes the conquest back. Shown wherever a trial is conquered. -->
<script lang="ts">
  import { QI_CARD } from '../lib/copy-qi';
  import { qiAsk } from '../lib/qi-ask.svelte';
  import Button from './Button.svelte';
  import Modal from './Modal.svelte';

  const question = $derived(qiAsk.question);
  // The thumb follows the hand; the number is only sent on Done.
  let shown = $state(0);
  $effect(() => {
    shown = question?.estimate ?? 0;
  });
</script>

{#if question}
  <Modal title={QI_CARD.title} onclose={qiAsk.keep}>
    <div class="sheet">
      <p class="what read">{question.title}</p>
      <p class="amount display digits" aria-live="polite">{QI_CARD.amount(shown)}</p>
      <input
        type="range"
        min={0}
        max={100}
        step={1}
        aria-label={QI_CARD.title}
        bind:value={shown}
      />
      <p class="hint">{QI_CARD.hint}</p>
      <div class="actions">
        <button
          class="link display"
          type="button"
          aria-label={QI_CARD.backDescription}
          onclick={qiAsk.back}>{QI_CARD.back}</button
        >
        <Button label={QI_CARD.confirm} tone="primary" onclick={() => qiAsk.confirm(shown)} />
      </div>
    </div>
  </Modal>
{/if}

<style>
  .sheet {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--space-3);
    min-width: min(24rem, 80vw);
    padding: var(--space-6) var(--space-8);
    text-align: center;
  }

  p {
    margin: 0;
  }

  .what {
    font-size: var(--text-read-lg);
  }

  .amount {
    color: var(--num);
    font-size: var(--text-display-lg);
    line-height: 1;
  }

  input {
    width: 100%;
    height: var(--size-slider-thumb);
    margin: 0;
    accent-color: var(--growth);
    cursor: pointer;
  }

  .hint {
    color: var(--ink-muted);
    font-size: var(--text-body-sm);
  }

  .actions {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: var(--space-5);
  }

  .link {
    padding: 0;
    background: none;
    border: 0;
    color: var(--ink-muted);
    font-size: var(--text-display-sm);
    text-decoration: underline;
    cursor: pointer;
  }
</style>
