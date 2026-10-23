<!-- One step of the tour, as in a game: a small card beside the thing to do, pointing at it. Doing the
     thing ends the step; "Got it" sets it aside; "Skip the tour" turns the cards off (Settings turns
     them on again). It sits beside its target, never over it, and blocks nothing else. -->
<script lang="ts">
  import { KNOWLEDGE } from '../../lib/copy-knowledge';
  import { knowledge, knowledgeApi } from '../../lib/knowledge.svelte';
  import { view } from '../../lib/view.svelte';

  let { key, target }: { key: string; target: DOMRect } = $props();

  const GAP = 14;
  const EDGE = 16;

  let width = $state(0);
  let height = $state(0);
  const words = $derived(KNOWLEDGE.steps[key]);

  // Right of the target if it fits, else left, else below; always inside the window.
  const place = $derived.by(() => {
    const room = window.innerWidth;
    const middle = target.top + target.height / 2 - height / 2;
    const top = Math.min(Math.max(EDGE, middle), window.innerHeight - height - EDGE);
    if (target.right + GAP + width + EDGE <= room)
      return { side: 'right', left: target.right + GAP, top };
    if (target.left - GAP - width >= EDGE)
      return { side: 'left', left: target.left - GAP - width, top };
    const left = Math.min(Math.max(EDGE, target.left), room - width - EDGE);
    const below = target.bottom + GAP + height + EDGE <= window.innerHeight;
    return {
      side: below ? 'below' : 'above',
      left,
      top: below ? target.bottom + GAP : target.top - GAP - height,
    };
  });
</script>

{#if words}
  <div
    class="card"
    role="note"
    aria-label="{KNOWLEDGE.title}: {words[0]}"
    data-side={place.side}
    style:left="{place.left}px"
    style:top="{place.top}px"
    bind:clientWidth={width}
    bind:clientHeight={height}
  >
    <p class="eyebrow display">{KNOWLEDGE.title}</p>
    <h2 class="title display">{words[0]}</h2>
    <p class="line">{words[1]}</p>
    <div class="actions">
      <button
        class="link"
        type="button"
        onclick={() => view.act(() => knowledgeApi.choose({ tour: false }))}
        >{KNOWLEDGE.skip}</button
      >
      <button class="got display" type="button" onclick={() => knowledge.pass(key)}
        >{KNOWLEDGE.gotIt}</button
      >
    </div>
  </div>
{/if}

<style>
  .card {
    position: fixed;
    z-index: 40;
    width: var(--size-tour-card);
    padding: var(--space-3) var(--space-4);
    background: var(--surface-panel);
    background-image: var(--gloss-faint);
    color: var(--ink);
    border: var(--border-width) solid var(--line);
    border-left: var(--space-1) solid var(--gold);
    box-shadow: var(--shadow-card);
    animation: tour-in var(--motion-fast) ease-out both;
  }

  /* The pointer: a small square turned on its corner, on the side that faces the target. */
  .card::before {
    content: '';
    position: absolute;
    width: var(--space-3);
    height: var(--space-3);
    background: var(--surface-panel);
    border: var(--border-width) solid var(--line);
    transform: rotate(45deg);
  }

  .card[data-side='right']::before {
    left: calc(var(--space-2) * -1 - var(--space-1));
    top: calc(50% - var(--space-2));
    border-top: none;
    border-right: none;
    border-left-color: var(--gold);
  }

  .card[data-side='left']::before {
    right: calc(var(--space-2) * -1);
    top: calc(50% - var(--space-2));
    border-bottom: none;
    border-left: none;
  }

  .card[data-side='below']::before {
    top: calc(var(--space-2) * -1);
    left: var(--space-5);
    border-bottom: none;
    border-right: none;
  }

  .card[data-side='above']::before {
    bottom: calc(var(--space-2) * -1);
    left: var(--space-5);
    border-top: none;
    border-left: none;
  }

  .eyebrow {
    margin: 0;
    color: var(--ink-muted);
    font-size: var(--text-body-sm);
  }

  .title {
    margin: var(--space-1) 0;
    font-size: var(--text-display-md);
  }

  .line {
    margin: 0;
    font-size: var(--text-body-md);
  }

  .actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: var(--space-3);
  }

  .link {
    padding: 0;
    background: none;
    border: none;
    color: var(--ink-muted);
    font-size: var(--text-body-sm);
    text-decoration: underline;
    cursor: pointer;
  }

  .got {
    padding: var(--space-1) var(--space-3);
    background: var(--gold);
    color: var(--on-gold);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-button);
    cursor: pointer;
  }

  @keyframes tour-in {
    from {
      opacity: 0;
    }
  }

  @media (prefers-reduced-motion: reduce) {
    .card {
      animation: none;
    }
  }
</style>
