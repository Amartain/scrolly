<!-- A question before something that cannot be undone. Esc or Cancel leaves everything as it was. -->
<script lang="ts">
  import { DATA } from '../lib/copy';
  import Button from './Button.svelte';
  import Modal from './Modal.svelte';

  let {
    title,
    body,
    confirm,
    onconfirm,
    oncancel,
  }: {
    title: string;
    body: string;
    confirm: string;
    onconfirm: () => void;
    oncancel: () => void;
  } = $props();
</script>

<Modal {title} onclose={oncancel}>
  <div class="sheet">
    <p class="read">{body}</p>
    <div class="actions">
      <Button label={confirm} tone="primary" onclick={onconfirm} />
      <Button label={DATA.cancel} onclick={oncancel} />
    </div>
  </div>
</Modal>

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
    gap: var(--space-3);
  }
</style>
