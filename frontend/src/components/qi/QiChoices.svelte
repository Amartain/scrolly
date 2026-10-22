<!-- The card's answer: three pressed-in choices (Lighter, As foreseen, Heavier, from Python), then the exact
     number between − and +, which can also be typed. A typed number counts as soon as it is a whole number from 0
     to 100; the choice that matches it stays pressed. -->
<script lang="ts">
  import GlyphIcon from '../../icons/GlyphIcon.svelte';
  import type { QiCard } from '../../lib/qi-api';
  import { QI_CARD } from '../../lib/copy-qi';
  import GlyphButton from '../GlyphButton.svelte';

  let {
    choices,
    value,
    restores,
    onchange,
  }: {
    choices: QiCard['choices'];
    value: number;
    restores: boolean;
    onchange: (value: number) => void;
  } = $props();

  const words = $derived(restores ? QI_CARD.restoreChoices : QI_CARD.choices);
  const options = $derived([
    { word: words.lighter, qi: choices.lighter, first: false },
    { word: words.foreseen, qi: choices.foreseen, first: true },
    { word: words.heavier, qi: choices.heavier, first: false },
  ]);
  const set = (next: number) => onchange(Math.min(100, Math.max(0, next)));

  function typed(event: Event & { currentTarget: HTMLInputElement }) {
    const text = event.currentTarget.value.trim();
    if (/^\d{1,3}$/.test(text) && Number(text) <= 100) onchange(Number(text));
  }
</script>

<div class="choices" role="radiogroup" aria-label={QI_CARD.title}>
  {#each options as option (option.word)}
    <label class="choice">
      <input
        type="radio"
        name="qi-choice"
        checked={value === option.qi}
        {@attach (node) => {
          // The card opens on "As foreseen", so Enter alone answers it.
          if (option.first) node.focus();
        }}
        onchange={() => onchange(option.qi)}
      />
      <span class="word display">{option.word}</span>
      <span class="qi digits">{option.qi}</span>
    </label>
  {/each}
</div>

<div class="exact" role="group" aria-label={QI_CARD.exact}>
  <GlyphButton label={QI_CARD.less} onclick={() => set(value - 1)}>
    <GlyphIcon name="minus" />
  </GlyphButton>
  <input
    class="number display digits"
    inputmode="numeric"
    aria-label={QI_CARD.exact}
    value={String(value)}
    oninput={typed}
    onfocus={(event) => event.currentTarget.select()}
  />
  <span class="unit display">Qi</span>
  <GlyphButton label={QI_CARD.more} onclick={() => set(value + 1)}>
    <GlyphIcon name="plus" />
  </GlyphButton>
</div>

<style>
  .choices {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    width: 100%;
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-button);
  }

  .choice {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--space-1);
    padding: var(--space-3) var(--space-2);
    cursor: pointer;
    background: var(--btn);
    background-image: var(--gloss-btn);
  }

  .choice + .choice {
    border-left: var(--border-width) solid var(--line);
  }

  .choice input {
    position: absolute;
    inset: 0;
    margin: 0;
    opacity: 0;
    cursor: inherit;
  }

  .choice:has(input:checked) {
    background: var(--strong);
    color: var(--on-strong);
  }

  /* The pressed choice: a gold rule just inside its edge. */
  .choice:has(input:checked)::after {
    content: '';
    position: absolute;
    inset: var(--space-1);
    border: var(--border-width) solid var(--gold);
    pointer-events: none;
  }

  .choice:has(input:focus-visible) {
    outline: var(--border-width) solid var(--gold);
    outline-offset: calc(-1 * var(--space-2));
  }

  .word {
    font-size: var(--text-display-sm);
  }

  .qi {
    font-size: var(--text-display-md);
    line-height: 1;
  }

  .exact {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: var(--space-2);
  }

  .number {
    width: var(--size-stepper-number);
    padding: var(--space-1);
    background: var(--inset);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-sunken);
    color: var(--num-text);
    font-size: var(--text-display-md);
    text-align: center;
  }

  .unit {
    color: var(--ink-muted);
    font-size: var(--text-display-sm);
  }
</style>
