<script lang="ts">
  type Tone =
    | 'default'
    | 'primary'
    | 'gold'
    | 'strong'
    | 'horizon'
    | 'foundational'
    | 'restorative'
    | 'archives';

  let {
    label,
    onclick,
    tone = 'default',
    disabled = false,
    description,
    size = 'normal',
    chip = false,
    tour,
  }: {
    label: string;
    onclick: () => void;
    tone?: Tone;
    disabled?: boolean;
    description?: string;
    /** `large` is for the one button a screen is built around (the landing screen). */
    size?: 'normal' | 'large';
    /** A lacquer chip: a row's own action (Promote, Summon), with a gold rule inside its edge. */
    chip?: boolean;
    /** The tour's lesson this button teaches (lib/knowledge.svelte.ts). */
    tour?: string;
  } = $props();
</script>

<button
  class="button display"
  class:lacquer-frame={chip}
  class:chip
  type="button"
  data-tour={tour}
  data-tone={tone}
  data-size={size}
  aria-label={description}
  title={description}
  {onclick}
  {disabled}>{label}</button
>

<style>
  .button {
    padding: var(--space-2) var(--space-4);
    cursor: pointer;
    background: var(--tone-bg, var(--btn));
    background-image: var(--gloss-btn);
    color: var(--tone-ink, var(--ink));
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-button);
    font-size: var(--text-display-sm);
    white-space: nowrap;
  }

  .chip {
    --frame-rule: color-mix(in srgb, var(--tone-ink, var(--ink)) 40%, transparent);
    padding: var(--space-1) var(--space-4);
    font-size: var(--text-body-sm);
    letter-spacing: 0.06em;
  }

  .button[data-size='large'] {
    padding: var(--space-5) var(--space-10);
    font-size: var(--text-display-md);
  }

  .button[data-tone='primary'] {
    --tone-bg: var(--growth);
    --tone-ink: var(--on-growth);
    background-image: none;
  }

  .button[data-tone='gold'] {
    --tone-bg: var(--gold);
    --tone-ink: var(--on-gold);
    background-image: none;
  }

  .button[data-tone='strong'] {
    --tone-bg: var(--strong);
    --tone-ink: var(--on-strong);
    background-image: none;
  }

  .button[data-tone='horizon'] {
    --tone-bg: var(--card-horizon-action-bg);
    --tone-ink: var(--card-horizon-action-ink);
  }

  .button[data-tone='foundational'] {
    --tone-bg: var(--card-foundational-action-bg);
    --tone-ink: var(--card-foundational-action-ink);
  }

  .button[data-tone='restorative'] {
    --tone-bg: var(--card-restorative-action-bg);
    --tone-ink: var(--card-restorative-action-ink);
  }

  .button[data-tone='archives'] {
    --tone-bg: var(--entry-archives-bg);
    --tone-ink: var(--entry-archives-ink);
    background-image: none;
  }

  .button:active:not(:disabled) {
    box-shadow: none;
    transform: translate(var(--shadow-offset), var(--shadow-offset));
  }

  .button:disabled {
    cursor: default;
    box-shadow: none;
    background: var(--surface-stripe);
    background-image: none;
    color: var(--ink-faint);
  }
</style>
