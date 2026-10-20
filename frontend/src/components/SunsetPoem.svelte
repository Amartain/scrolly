<!-- The sunset poem. The layout (one of seven) and which language comes first are chosen in Python. -->
<script lang="ts">
  import { playChime } from '../lib/chime';
  import { poemSeen } from '../lib/api';
  import { POEM } from '../lib/copy';
  import { view } from '../lib/view.svelte';
  import Button from './Button.svelte';
  import Modal from './Modal.svelte';

  // One modal at a time: the milestone after a first seal goes first.
  const poem = $derived(view.milestone ? null : (view.current?.poem ?? null));
  let chimed = '';

  $effect(() => {
    if (poem && chimed !== poem.id && view.current?.sunset.chime) {
      chimed = poem.id;
      playChime();
    }
  });

  const settle = () => view.act(poemSeen);
</script>

{#if poem}
  <Modal title={POEM.title} onclose={settle}>
    <div
      class="page {poem.archetype}"
      data-pairing={poem.pairing}
      class:english-first={!poem.chinese_first}
    >
      <p class="seal display" aria-hidden="true">{poem.ideogram}</p>
      <div class="chinese" lang="zh">
        {#each poem.chinese as line (line)}<p>{line}</p>{/each}
      </div>
      <div class="english read">
        <p class="pinyin display">{poem.pinyin}</p>
        <p>{poem.english}</p>
        <p class="reflection">{poem.reflection}</p>
      </div>
      <div class="close"><Button label={POEM.close} tone="primary" onclick={settle} /></div>
    </div>
  </Modal>
{/if}

<style>
  /* Every layout is the same four pieces placed differently: the seal, the couplet, the translation
     and the button. The class english-first swaps the two languages. */
  .page {
    --paint: var(--growth);
    --on-paint: var(--on-growth);
    display: grid;
    grid-template-columns: auto 1fr;
    gap: var(--space-4) var(--space-6);
    align-items: center;
    max-width: 44rem;
    padding: var(--space-6) var(--space-8);
  }

  .page[data-pairing='gold'] {
    --paint: var(--gold);
    --on-paint: var(--on-gold);
  }

  .page[data-pairing='ink'] {
    --paint: var(--strong);
    --on-paint: var(--on-strong);
  }

  p {
    margin: 0;
  }

  .seal {
    order: -2;
    grid-row: span 2;
    display: grid;
    place-items: center;
    width: 5em;
    height: 5em;
    background: var(--paint);
    color: var(--on-paint);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-button);
    font-size: var(--text-display-xl);
  }

  .chinese {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
    font-size: var(--text-display-lg);
    letter-spacing: 0.3em;
  }

  .english {
    display: flex;
    flex-direction: column;
    gap: var(--space-3);
  }

  .english-first .english {
    order: -1;
  }

  .pinyin {
    color: var(--ink-muted);
    font-size: var(--text-display-sm);
  }

  .reflection {
    color: var(--ink-muted);
    font-style: italic;
  }

  .close {
    order: 9;
    grid-column: 1 / -1;
    justify-self: end;
  }

  .classical-imperial-scroll .chinese {
    writing-mode: vertical-rl;
    flex-direction: row-reverse;
    height: 9rem;
  }

  .translation-hero,
  .zen-monograph {
    grid-template-columns: 1fr;
    justify-items: center;
    text-align: center;
  }

  .translation-hero .seal,
  .zen-monograph .seal {
    grid-row: auto;
  }

  .translation-hero .english {
    font-size: var(--text-display-sm);
  }

  .zen-monograph .seal,
  .mountain-hermit-asymmetry .seal {
    width: 7em;
    height: 7em;
    background: none;
    border: 0;
    box-shadow: none;
    color: var(--paint);
  }

  .mountain-hermit-asymmetry {
    grid-template-columns: 1fr 1.4fr;
  }

  .retro-scholar-tablet {
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-panel);
  }

  .split-column-pavilion {
    grid-template-columns: 1fr 1fr;
    align-items: start;
  }

  .split-column-pavilion .seal {
    grid-column: 1 / -1;
    grid-row: auto;
    justify-self: center;
  }

  .golden-pavilion-seal {
    grid-template-columns: 1fr auto;
  }

  .golden-pavilion-seal .seal {
    order: 5;
    grid-column: 2;
    grid-row: 1 / span 2;
    background: var(--gold);
    color: var(--on-gold);
  }

  .golden-pavilion-seal .chinese,
  .golden-pavilion-seal .english {
    grid-column: 1;
  }
</style>
