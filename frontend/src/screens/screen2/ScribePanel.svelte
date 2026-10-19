<script lang="ts">
  import Button from '../../components/Button.svelte';
  import Panel from '../../components/Panel.svelte';
  import { today } from '../../lib/api';
  import { view } from '../../lib/view.svelte';

  let title = $state('');
  let estimate = $state('');
  let qi = $state('');

  const qiOn = $derived(view.planning?.qi.enabled ?? false);

  async function inscribe(event?: Event) {
    event?.preventDefault();
    if (!title.trim()) return;
    if (await view.act(() => today.scribe(title, estimate, qi))) {
      title = '';
      estimate = '';
      qi = '';
    }
  }
</script>

<Panel title="Scribe Trial">
  <form class="scribe" onsubmit={inscribe}>
    <input
      id="scribe-title"
      class="title"
      bind:value={title}
      placeholder="A sudden trial appears…"
      aria-label="Trial to scribe"
    />
    <input class="small digits" bind:value={estimate} placeholder="30m" aria-label="Estimate" />
    {#if qiOn}
      <input class="small digits" bind:value={qi} placeholder="Qi" aria-label="Qi expected" />
    {/if}
    <Button label="Inscribe" tone="primary" onclick={() => inscribe()} />
    <!-- Several fields: a hidden submit lets Enter inscribe from any of them. -->
    <button type="submit" hidden tabindex="-1" aria-hidden="true"></button>
  </form>
</Panel>

<style>
  .scribe {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    padding: var(--space-1) var(--space-4);
  }

  input {
    height: var(--size-glyph-button);
    padding-inline: var(--space-3);
    background: var(--surface-raised);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-sunken);
    font-size: var(--text-body-md);
  }

  .title {
    flex: 1;
    min-width: 0;
    font-family: var(--font-body);
  }

  .small {
    flex: none;
    width: var(--size-estimate);
    text-align: right;
  }
</style>
