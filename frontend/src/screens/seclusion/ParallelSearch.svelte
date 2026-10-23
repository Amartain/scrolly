<!-- The search bar of Parallel Flow: it finds a waiting trial, an Art or a Horizon item to run beside the
     trial at hand, or names a new one. Enter takes the exact match, else makes the title; the arrows
     walk the list. -->
<script lang="ts">
  import TypeMark from '../../components/TypeMark.svelte';
  import { SECLUSION } from '../../lib/copy-seclusion';
  import { parallelApi, type Candidate } from '../../lib/parallel-api';
  import { parallel } from '../../lib/parallel.svelte';

  const copy = SECLUSION.parallel;

  let query = $state('');
  let found = $state<Candidate[]>([]);
  let list = $state<HTMLElement>();
  let asked = 0;

  const title = $derived(query.trim());
  const exact = $derived(found.find((c) => c.title.toLowerCase() === title.toLowerCase()));

  async function search() {
    const mine = ++asked;
    if (!title) {
      found = [];
      return;
    }
    try {
      const result = await parallelApi.search(title);
      if (mine === asked) found = result;
    } catch {
      // The list stays as it was; the next keystroke asks again.
    }
  }

  const pick = (candidate: Candidate) => parallel.pick(candidate.source, candidate.id);
  const make = () => parallel.pick('new', title);

  function enter(event: KeyboardEvent) {
    if (event.key !== 'Enter' || !title) return;
    event.preventDefault();
    void (exact ? pick(exact) : make());
  }

  function walk(event: KeyboardEvent) {
    if (event.key !== 'ArrowDown' && event.key !== 'ArrowUp') return;
    const stops = [
      document.getElementById('parallel-search'),
      ...(list?.querySelectorAll('button') ?? []),
    ];
    const at = stops.indexOf(document.activeElement as HTMLElement);
    const next = stops[at + (event.key === 'ArrowDown' ? 1 : -1)];
    event.preventDefault(); // at either end too: ↓ is not the way down the mountain here
    next?.focus();
  }
</script>

<div class="search" role="presentation" onkeydown={walk}>
  <input
    id="parallel-search"
    class="field"
    bind:value={query}
    oninput={search}
    onkeydown={enter}
    placeholder={copy.search}
    aria-label={SECLUSION.parallelTitle}
    autocomplete="off"
  />
  <ul class="found" bind:this={list} aria-label={SECLUSION.parallelTitle}>
    {#each found as candidate (candidate.source + candidate.id)}
      <li>
        <button class="option" type="button" onclick={() => pick(candidate)}>
          <TypeMark type={candidate.type} title={candidate.title} />
          <span class="name">{candidate.title}</span>
          <span class="from">{copy.from[candidate.source]}</span>
        </button>
      </li>
    {/each}
    {#if title && !exact}
      <li>
        <button class="option" type="button" onclick={make}>
          <span class="name">{copy.make(title)}</span>
        </button>
      </li>
    {/if}
  </ul>
  <p class="hint">{SECLUSION.parallelLine}</p>
</div>

<style>
  .search {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
    padding: var(--space-3) var(--space-4);
  }

  .field {
    height: var(--size-field);
    padding-inline: var(--space-3);
    background: var(--surface-raised);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-sunken);
    color: var(--ink);
    font-size: var(--text-body-md);
  }

  .found {
    margin: 0;
    padding: 0;
    list-style: none;
  }

  .option {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    width: 100%;
    padding: var(--space-2) var(--space-3);
    background: none;
    border: 0;
    color: var(--ink);
    text-align: left;
    cursor: pointer;
  }

  .option:hover,
  .option:focus-visible {
    background: var(--surface-stripe);
  }

  .name {
    flex: 1;
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    font-size: var(--text-body-md);
  }

  .from {
    color: var(--ink-muted);
    font-size: var(--text-body-sm);
  }

  .hint {
    margin: 0;
    color: var(--ink-muted);
    font-size: var(--text-body-sm);
  }
</style>
