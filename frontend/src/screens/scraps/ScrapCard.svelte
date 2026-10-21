<!-- One finished visit to Seclusion: the day, the hours, which trials were worked and when (a lane
     each, so trials run side by side show lit at the same time), then what was written. -->
<script lang="ts">
  import { SECLUSION } from '../../lib/copy-seclusion';
  import type { ScrapPage } from '../../lib/scraps-api';

  let { scrap }: { scrap: ScrapPage } = $props();
</script>

<article class="scrap" aria-label="{scrap.day_text}, {scrap.time_text}">
  <header class="head">
    <h2 class="day display">{scrap.day_text}</h2>
    <p class="when">{scrap.time_text} · {scrap.length_text}</p>
  </header>
  {#if scrap.lanes.length > 0}
    <ul class="lanes" aria-label={SECLUSION.scrapsPage.trials}>
      {#each scrap.lanes as lane, index (index)}
        <li class="lane">
          <span class="name">{lane.title}</span>
          <span class="track" aria-hidden="true">
            {#each lane.spans as span, at (at)}
              <span class="span" style:left="{span.start_pct}%" style:width="{span.width_pct}%"
              ></span>
            {/each}
          </span>
        </li>
      {/each}
    </ul>
  {/if}
  <p class="text read">{scrap.text}</p>
</article>

<style>
  .scrap {
    display: flex;
    flex-direction: column;
    gap: var(--space-3);
    padding: var(--space-4) var(--space-5);
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
  }

  .day {
    margin: 0;
    font-size: var(--text-display-md);
  }

  .when {
    margin: 0;
    color: var(--ink-muted);
  }

  .lanes {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
    margin: 0;
    padding: 0;
    list-style: none;
  }

  .lane {
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(0, 2fr);
    align-items: center;
    gap: var(--space-3);
  }

  .name {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    font-size: var(--text-body-sm);
  }

  .track {
    position: relative;
    display: block;
    height: var(--space-3);
    background: var(--surface-stripe);
    border: var(--border-width) solid var(--line);
  }

  .span {
    position: absolute;
    top: 0;
    bottom: 0;
    min-width: var(--space-1);
    background: var(--growth);
  }

  .text {
    margin: 0;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
  }
</style>
