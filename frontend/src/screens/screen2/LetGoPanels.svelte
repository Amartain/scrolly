<script lang="ts">
  import ExpandButton from '../../components/ExpandButton.svelte';
  import Panel from '../../components/Panel.svelte';
  import StateMark from '../../components/StateMark.svelte';
  import { EMPTY } from '../../lib/copy';
  import type { LetGo } from '../../lib/api';
  import { view } from '../../lib/view.svelte';
  import LetGoList from './LetGoList.svelte';

  const postponed = $derived(view.current?.dashboard.postponed ?? []);
  const lost = $derived(view.current?.dashboard.lost ?? []);
  let open = $state<'postponed' | 'lost' | null>(null);
</script>

{#snippet line(items: LetGo[], state: string, empty: string)}
  {#if items.length === 0}
    <p class="empty">{empty}</p>
  {:else}
    <p class="line read">
      <StateMark {state} />
      <span class="names">{items.map((item) => item.title).join(', ')}</span>
    </p>
  {/if}
{/snippet}

<div class="pair">
  <Panel title="Postponed Today" guide="postponed" count={postponed.length}>
    {#snippet actions()}
      <ExpandButton label="Expand Postponed Today" onclick={() => (open = 'postponed')} />
    {/snippet}
    {@render line(postponed, 'postponed', EMPTY.postponed)}
  </Panel>
  <Panel title="Fallen Leaves" guide="fallen" count={lost.length}>
    {#snippet actions()}
      <ExpandButton label="Expand Fallen Leaves" onclick={() => (open = 'lost')} />
    {/snippet}
    {@render line(lost, 'lost', EMPTY.fallen)}
  </Panel>
</div>

{#if open === 'postponed'}
  <LetGoList
    title="Postponed Today"
    items={postponed}
    state="postponed"
    empty={EMPTY.postponed}
    onclose={() => (open = null)}
  />
{:else if open === 'lost'}
  <LetGoList
    title="Fallen Leaves"
    items={lost}
    state="lost"
    empty={EMPTY.fallen}
    onclose={() => (open = null)}
  />
{/if}

<style>
  .pair {
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
    gap: var(--space-5);
    min-height: 0;
  }

  .empty,
  .line {
    margin: 0;
    padding: var(--space-2) var(--space-4);
  }

  .empty {
    color: var(--ink-muted);
  }

  .line {
    display: flex;
    align-items: center;
    gap: var(--space-2);
  }

  .names {
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
</style>
