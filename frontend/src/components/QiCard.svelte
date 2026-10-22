<!-- After a conquest: how much qi it took. It opens on "As foreseen" (the estimate), so Enter alone answers it;
     Lighter and Heavier are one press away, and the exact number can be stepped or typed. Below, today's Qi bar
     shows where the answer lands (Python works it out; nothing is saved until Done). Closing keeps the estimate;
     "Take it back" undoes the conquest. Shown wherever a trial is conquered. -->
<script lang="ts">
  import { untrack } from 'svelte';
  import { QI_CARD } from '../lib/copy-qi';
  import { qiAsk } from '../lib/qi-ask.svelte';
  import { getQiCard, type QiCard } from '../lib/qi-api';
  import { view } from '../lib/view.svelte';
  import Button from './Button.svelte';
  import Modal from './Modal.svelte';
  import QiChoices from './qi/QiChoices.svelte';
  import QiLanding from './qi/QiLanding.svelte';

  const question = $derived(qiAsk.question);
  let shown = $state(0);
  let card = $state<QiCard | null>(null);
  // The day's spent Qi as it stands (the estimate is recorded on conquest), for "60 → 80".
  let from = $state(0);

  // A new question starts the card afresh; a refresh of the view while it is open changes nothing.
  $effect(() => {
    shown = question?.estimate ?? 0;
    from = untrack(() => view.planning?.qi.spent ?? 0);
    card = null;
  });

  // Ask Python again whenever the answer changes; only the newest reply is kept.
  let asked = 0;
  $effect(() => {
    if (!question) return;
    const ticket = ++asked;
    void getQiCard(question.id, shown)
      .then((reply) => {
        if (ticket === asked) card = reply;
      })
      .catch(() => {});
  });

  function onkeydown(event: KeyboardEvent) {
    if (event.key !== 'Enter' || event.target instanceof HTMLButtonElement) return;
    event.preventDefault();
    void qiAsk.confirm(shown);
  }
</script>

{#if question}
  <Modal title={QI_CARD.title} striped={false} onclose={qiAsk.keep}>
    <!-- svelte-ignore a11y_no_static_element_interactions (Enter anywhere on the card answers it) -->
    <div class="sheet" {onkeydown}>
      <p class="what read">{question.title}</p>
      {#if card}
        <QiChoices
          choices={card.choices}
          value={shown}
          restores={question.restores}
          onchange={(next) => (shown = next)}
        />
        <QiLanding {card} {from} />
      {/if}
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
    gap: var(--space-4);
    width: min(30rem, 86vw);
    padding: var(--space-5) var(--space-6);
    text-align: center;
  }

  p {
    margin: 0;
  }

  .what {
    font-size: var(--text-read-lg);
  }

  .actions {
    display: flex;
    align-items: center;
    justify-content: space-between;
    align-self: stretch;
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
