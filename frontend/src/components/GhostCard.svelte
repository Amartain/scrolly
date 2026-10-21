<!-- A timer was running while the app was away. The timers wait, paused where the user left, until
     this is answered; closing the card only puts the question off. -->
<script lang="ts">
  import { GHOST } from '../lib/copy-ghost';
  import { cutGhost, keepGhost } from '../lib/ghost-api';
  import { seclusion } from '../lib/seclusion.svelte';
  import { view } from '../lib/view.svelte';
  import Button from './Button.svelte';
  import Modal from './Modal.svelte';

  const ghost = $derived(view.current?.ghost ?? null);
  const key = $derived(ghost ? `${ghost.left_text}/${ghost.gap_text}` : '');
  let putOff = $state('');

  async function answer(command: typeof keepGhost) {
    if (await view.act(command)) await seclusion.load(); // a run in the room moved with it
  }
</script>

{#if ghost && putOff !== key}
  <Modal title={GHOST.title} onclose={() => (putOff = key)}>
    <div class="sheet">
      <p class="away read">{GHOST.away(ghost.left_text, ghost.gap_text)}</p>
      <p class="ask display">{GHOST.question}</p>
      <div class="actions">
        <Button label={GHOST.cut} onclick={() => answer(cutGhost)} />
        <Button label={GHOST.keep} tone="primary" onclick={() => answer(keepGhost)} />
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
    max-width: 30rem;
    padding: var(--space-6) var(--space-8);
    text-align: center;
  }

  p {
    margin: 0;
  }

  .away {
    font-size: var(--text-read-lg);
  }

  .ask {
    color: var(--ink-muted);
    font-size: var(--text-display-md);
  }

  .actions {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: var(--space-3);
  }
</style>
