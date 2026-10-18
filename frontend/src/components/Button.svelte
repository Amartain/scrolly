<script lang="ts">
  type Tone = 'default' | 'primary' | 'horizon' | 'foundational' | 'restorative';

  let {
    label,
    onclick,
    tone = 'default',
    disabled = false,
    description,
  }: {
    label: string;
    onclick: () => void;
    tone?: Tone;
    disabled?: boolean;
    description?: string;
  } = $props();
</script>

<button
  class="button display"
  type="button"
  data-tone={tone}
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

  .button[data-tone='primary'] {
    --tone-bg: var(--growth);
    --tone-ink: var(--on-growth);
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
