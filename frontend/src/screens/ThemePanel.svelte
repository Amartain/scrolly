<script lang="ts">
  import Panel from '../components/Panel.svelte';
  import type { DayVariant, ReadingFont, Theme } from '../lib/api';
  import { view } from '../lib/view.svelte';

  const themes: { value: Theme; label: string }[] = [
    { value: 'serene', label: 'Serene Peak' },
    { value: 'pavilion', label: 'Hidden Pavilion' },
  ];
  const variants: { value: DayVariant; label: string }[] = [
    { value: 'teal', label: 'Teal' },
    { value: 'crimson', label: 'Crimson' },
  ];

  const fonts: { value: ReadingFont; label: string }[] = [
    { value: 'atkinson', label: 'Atkinson' },
    { value: 'opendyslexic', label: 'OpenDyslexic' },
  ];

  const appearance = $derived(view.current?.appearance);
  const isPavilion = $derived(appearance?.theme === 'pavilion');
</script>

<Panel title="Theme">
  <div class="groups">
    <fieldset class="group">
      <legend class="display">Theme</legend>
      {#each themes as theme (theme.value)}
        <label class="choice display">
          <input
            type="radio"
            name="theme"
            value={theme.value}
            checked={appearance?.theme === theme.value}
            onchange={() => view.choose(theme.value, null)}
          />
          {theme.label}
        </label>
      {/each}
    </fieldset>
    <fieldset class="group" disabled={!isPavilion}>
      <legend class="display">Pavilion by day</legend>
      {#each variants as variant (variant.value)}
        <label class="choice display">
          <input
            type="radio"
            name="day-variant"
            value={variant.value}
            checked={appearance?.day_variant === variant.value}
            onchange={() => view.choose('pavilion', variant.value)}
          />
          {variant.label}
        </label>
      {/each}
    </fieldset>
    <fieldset class="group">
      <legend class="display">Reading font</legend>
      {#each fonts as font (font.value)}
        <label class="choice font-{font.value}">
          <input
            type="radio"
            name="reading-font"
            value={font.value}
            checked={appearance?.reading_font === font.value}
            onchange={() => view.chooseReadingFont(font.value)}
          />
          {font.label}
        </label>
      {/each}
    </fieldset>
  </div>
</Panel>

<style>
  .groups {
    display: flex;
    gap: var(--space-8);
    padding: var(--space-4);
  }

  .group {
    display: flex;
    flex-direction: column;
    gap: var(--space-3);
    margin: 0;
    padding: 0;
    border: 0;
    min-width: 0;
  }

  .group:disabled {
    color: var(--ink-faint);
  }

  legend {
    padding: 0;
    margin-bottom: var(--space-3);
    font-size: var(--text-display-sm);
    color: var(--ink-muted);
  }

  .choice {
    position: relative;
    padding: var(--space-3) var(--space-5);
    cursor: pointer;
    background: var(--btn);
    background-image: var(--gloss-btn);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-button);
    font-size: var(--text-display-sm);
  }

  .font-atkinson {
    font-family: var(--font-atkinson);
    font-size: var(--text-read-md);
  }

  .font-opendyslexic {
    font-family: var(--font-opendyslexic);
    font-size: var(--text-read-md);
  }

  .choice input {
    position: absolute;
    opacity: 0;
    inset: 0;
    margin: 0;
    cursor: inherit;
  }

  .choice:has(input:checked) {
    background: var(--strong);
    color: var(--on-strong);
    box-shadow: none;
    transform: translate(var(--shadow-offset), var(--shadow-offset));
  }

  .choice:has(input:focus-visible) {
    outline: var(--border-width) solid var(--gold);
    outline-offset: var(--space-1);
  }

  .group:disabled .choice {
    cursor: default;
    box-shadow: none;
    background: var(--surface-stripe);
    color: var(--ink-faint);
  }
</style>
