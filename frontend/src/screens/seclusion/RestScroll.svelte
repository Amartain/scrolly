<!-- Nothing is left to focus on. After the last trial: a word of rest, and Undo for a conquest. -->
<script lang="ts">
  import Panel from '../../components/Panel.svelte';
  import { SECLUSION } from '../../lib/copy-seclusion';
  import { seclusion } from '../../lib/seclusion.svelte';

  const finished = $derived(seclusion.finished);
</script>

<Panel title={SECLUSION.title}>
  <div class="rest">
    <p class="words display">{finished ? SECLUSION.rest : SECLUSION.nothingLeft}</p>
    {#if finished?.how === 'conquered'}
      <button class="link display" type="button" onclick={() => seclusion.undo()}
        >{SECLUSION.undo}</button
      >
    {/if}
  </div>
</Panel>

<style>
  .rest {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: var(--space-4);
    height: 100%;
  }

  .words {
    margin: 0;
    font-size: var(--text-display-lg);
    text-align: center;
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
