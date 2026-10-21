<!-- One past day: its Essence, then what became of each trial. Read-only; Python grouped and worded it. -->
<script lang="ts">
  import StateMark from '../../components/StateMark.svelte';
  import TypeMark from '../../components/TypeMark.svelte';
  import { ARCHIVES } from '../../lib/copy-archives';
  import type { ArchiveCard } from '../../lib/archives-api';
  import { view } from '../../lib/view.svelte';

  let { card }: { card: ArchiveCard } = $props();

  const qiOn = $derived(view.planning?.qi.enabled ?? false);
</script>

<article class="day" aria-label={card.day_text}>
  <header class="head">
    <h2 class="name display">{card.day_text}</h2>
    <p class="essence digits">{ARCHIVES.essence(card.actual_text, card.expected_text)}</p>
  </header>
  <ul class="rows">
    {#each card.conquered as row (row.id)}
      <li class="row">
        <StateMark state="done" />
        <span class="title read">{row.title}</span>
        {#if row.expected_text}<span class="figure digits">({row.expected_text})</span>{/if}
        <span class="figure digits">{row.actual_text || '—'}</span>
        {#if qiOn}<span class="figure digits">{row.qi_text ? `${row.qi_text} Qi` : '—'}</span>{/if}
        <span class="figure digits">{row.at_text}</span>
        <TypeMark type={row.type} title={row.title} />
      </li>
    {/each}
    {#each card.lost as row (row.id)}
      <li class="row quiet">
        <StateMark state="lost" />
        <span class="title read">{row.title}</span>
        <span class="figure note">{ARCHIVES.lost}</span>
        <TypeMark type={row.type} title={row.title} />
      </li>
    {/each}
    {#each card.sent_back as row (row.id)}
      <li class="row quiet">
        <StateMark state="postponed" />
        <span class="title read">{row.title}</span>
        <span class="figure note">{ARCHIVES.sentBack}</span>
        <TypeMark type={row.type} title={row.title} />
      </li>
    {/each}
  </ul>
</article>

<style>
  .day {
    background: var(--surface-raised);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-panel);
  }

  .head {
    display: flex;
    flex-wrap: wrap;
    align-items: baseline;
    justify-content: space-between;
    gap: var(--space-2) var(--space-4);
    padding: var(--space-2) var(--space-4);
    background: var(--head-bg);
    color: var(--head-ink);
    border-bottom: var(--border-width) solid var(--line);
  }

  .name {
    margin: 0;
    font-size: var(--text-display-md);
  }

  .essence {
    margin: 0;
    font-size: var(--text-body-md);
  }

  .rows {
    margin: 0;
    padding: 0;
    list-style: none;
  }

  .row {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    min-height: var(--size-row);
    padding-inline: var(--space-4);
  }

  .row:nth-child(even) {
    background: var(--surface-stripe);
  }

  .title {
    flex: 1;
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .figure {
    flex: none;
    color: var(--ink-muted);
    font-size: var(--text-body-md);
    text-align: right;
  }

  .quiet .title,
  .note {
    color: var(--ink-muted);
    font-style: italic;
  }
</style>
