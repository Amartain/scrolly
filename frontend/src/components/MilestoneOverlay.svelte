<!-- After the day's first seal: how many days are sealed, and a line to carry into the day. -->
<script lang="ts">
  import { MILESTONE } from '../lib/copy';
  import { view } from '../lib/view.svelte';
  import Button from './Button.svelte';
  import Modal from './Modal.svelte';

  const milestone = $derived(view.milestone);
  const close = () => view.dismissMilestone();
</script>

{#if milestone}
  <Modal title={MILESTONE.title} onclose={close}>
    <div class="sheet">
      {#if milestone.banner}<p class="banner display">{milestone.banner}</p>{/if}
      <p class="count display">{milestone.cycles}</p>
      <p class="unit">{milestone.cycles === 1 ? MILESTONE.one : MILESTONE.many}</p>
      <blockquote class="quote read">
        <p>{milestone.quote}</p>
        {#if milestone.attribution}<footer>— {milestone.attribution}</footer>{/if}
      </blockquote>
      <Button label={MILESTONE.close} tone="primary" onclick={close} />
    </div>
  </Modal>
{/if}

<style>
  .sheet {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--space-3);
    padding: var(--space-6) var(--space-8);
    text-align: center;
  }

  p {
    margin: 0;
  }

  .banner {
    color: var(--growth-text);
    font-size: var(--text-display-md);
  }

  .count {
    color: var(--num);
    font-size: var(--text-display-xl);
    line-height: 1;
    text-shadow: var(--space-1) var(--space-1) 0 var(--num-shadow);
  }

  .unit {
    color: var(--ink-muted);
    font-size: var(--text-body-md);
  }

  .quote {
    margin: var(--space-4) 0;
    max-width: 36rem;
  }

  footer {
    margin-top: var(--space-2);
    color: var(--ink-muted);
    font-size: var(--text-body-sm);
  }
</style>
