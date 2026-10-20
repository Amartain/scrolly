<!-- One gentle word when the open trials would run past sunset. Dismiss hides it until a reload. -->
<script lang="ts">
  import { advisor } from '../lib/api';
  import { ADVISOR } from '../lib/copy';
  import { view } from '../lib/view.svelte';
  import Button from './Button.svelte';
  import Modal from './Modal.svelte';

  let dismissed = $state(false);
  const due = $derived(view.current?.advisor.due ?? false);
  const mandates = $derived(view.current?.advisor.mandates ?? 0);
</script>

{#if due && !dismissed}
  <Modal title={ADVISOR.title} onclose={() => (dismissed = true)}>
    <div class="sheet">
      <p class="read">{mandates > 0 ? ADVISOR.body : ADVISOR.bodyNoMandates}</p>
      <div class="actions">
        {#if mandates > 0}
          <Button
            label={ADVISOR.postpone}
            tone="primary"
            onclick={() => view.act(advisor.postponeMandates)}
          />
        {/if}
        <Button label={ADVISOR.dismiss} onclick={() => (dismissed = true)} />
        <Button label={ADVISOR.never} onclick={() => view.act(() => advisor.silence(true))} />
      </div>
    </div>
  </Modal>
{/if}

<style>
  .sheet {
    display: flex;
    flex-direction: column;
    gap: var(--space-5);
    max-width: 36rem;
    padding: var(--space-6) var(--space-8);
  }

  p {
    margin: 0;
  }

  .actions {
    display: flex;
    flex-wrap: wrap;
    gap: var(--space-3);
  }
</style>
