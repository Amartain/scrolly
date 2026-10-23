<!-- The tour, drawn once by the app shell. It learns a lesson when an element marked `data-tour` is
     used (a click, or `data-tour-on`: typing, a double-click, a hover), and shows the first step card
     still pending whose target is on screen, beside it. No card while a pop-up is open, while
     Seclusion paints itself in, or with the tour off. -->
<script lang="ts">
  import { knowledge } from '../../lib/knowledge.svelte';
  import { peak } from '../../lib/peak.svelte';
  import { view } from '../../lib/view.svelte';
  import Enlightenment from './Enlightenment.svelte';
  import TourCard from './TourCard.svelte';
  import TourFind from './TourFind.svelte';

  /** How often the card looks for its target: screens change, scroll and fold. */
  const LOOK_MS = 400;

  let step = $state<{ key: string; target: DOMRect } | null>(null);

  function learnFrom(event: Event, how: string) {
    const marked = event.target instanceof Element ? event.target.closest('[data-tour]') : null;
    if (!marked || (marked.getAttribute('data-tour-on') ?? 'click') !== how) return;
    const typed = marked instanceof HTMLTextAreaElement || marked instanceof HTMLInputElement;
    if (how === 'input' && typed && !marked.value.trim()) return;
    knowledge.learn(marked.getAttribute('data-tour') ?? '', marked);
  }

  function visible(key: string): DOMRect | null {
    const target = document.querySelector(`[data-tour="${key}"]`);
    const box = target?.getBoundingClientRect();
    if (!box || box.width === 0 || box.bottom < 0 || box.top > window.innerHeight) return null;
    return box;
  }

  function look() {
    const known = view.current?.knowledge;
    const quiet = !known?.tour || peak.arriving || document.querySelector('dialog[open]');
    const key = quiet ? undefined : known.pending_steps.find((k) => visible(k));
    const target = key ? visible(key) : null;
    const same =
      step?.key === key && step?.target.top === target?.top && step?.target.left === target?.left;
    if (!same) step = key && target ? { key, target } : null;
  }

  $effect(() => {
    look();
    const id = setInterval(look, LOOK_MS);
    return () => clearInterval(id);
  });

  // Opening the app is the first thing learned.
  $effect(() => {
    if (view.current) knowledge.learn('open');
  });
</script>

<!-- Clicks are read on the way down (capture): a control may replace itself when it handles one
     (the conquered time becomes a field), and then nothing marked is left to look up from. -->
<svelte:document
  onclickcapture={(event) => learnFrom(event, 'click')}
  oninput={(event) => learnFrom(event, 'input')}
  ondblclickcapture={(event) => learnFrom(event, 'dblclick')}
  onpointerover={(event) => learnFrom(event, 'hover')}
  onfocusin={(event) => learnFrom(event, 'hover')}
/>

{#if step}<TourCard key={step.key} target={step.target} />{/if}
{#if knowledge.found}<TourFind {...knowledge.found} />{/if}
{#if view.current?.knowledge.complete && !view.current.knowledge.enlightened && !peak.arriving}
  <Enlightenment />
{/if}
