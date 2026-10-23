<!-- Settings › The Tour: the step cards on or off, the Knowledge of the Dao bar shown or hidden (a
     hidden bar still fills and shows for a moment when it moves), and walking the path again (the cards
     come back; nothing learned is lost). -->
<script lang="ts">
  import Button from '../components/Button.svelte';
  import Panel from '../components/Panel.svelte';
  import ToggleChoice from '../components/ToggleChoice.svelte';
  import { KNOWLEDGE } from '../lib/copy-knowledge';
  import { knowledgeApi } from '../lib/knowledge.svelte';
  import { view } from '../lib/view.svelte';

  const WORDS = KNOWLEDGE.settings;
  const known = $derived(view.current?.knowledge);
</script>

<Panel title={WORDS.title}>
  <div class="body">
    <ToggleChoice
      label={WORDS.cards}
      checked={known?.tour ?? true}
      onchange={(tour) => view.act(() => knowledgeApi.choose({ tour }))}
    />
    <ToggleChoice
      label={WORDS.bar}
      checked={!(known?.bar_hidden ?? false)}
      onchange={(shown) => view.act(() => knowledgeApi.choose({ bar_hidden: !shown }))}
    />
    <Button label={WORDS.again} onclick={() => view.act(knowledgeApi.walkAgain)} />
    {#if known}<p class="note">{WORDS.note(known.count, known.total)}</p>{/if}
  </div>
</Panel>

<style>
  .body {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: var(--space-3);
    padding: var(--space-4);
  }

  .note {
    flex-basis: 100%;
    margin: 0;
    color: var(--ink-muted);
  }
</style>
