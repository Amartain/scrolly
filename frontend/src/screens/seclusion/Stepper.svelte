<!-- A small number with − and + around it. The number can also be typed; the server checks the limits. -->
<script lang="ts">
  import GlyphButton from '../../components/GlyphButton.svelte';
  import GlyphIcon from '../../icons/GlyphIcon.svelte';

  let {
    value,
    min,
    max,
    label,
    onchange,
  }: { value: number; min: number; max: number; label: string; onchange: (value: number) => void } =
    $props();

  const set = (next: number) => onchange(Math.min(max, Math.max(min, next)));

  function typed(event: Event & { currentTarget: HTMLInputElement }) {
    const next = Number.parseInt(event.currentTarget.value, 10);
    if (Number.isNaN(next)) event.currentTarget.value = String(value);
    else set(next);
  }
</script>

<div class="stepper" role="group" aria-label={label}>
  <GlyphButton label="Fewer {label}" onclick={() => set(value - 1)}>
    <GlyphIcon name="minus" />
  </GlyphButton>
  <input
    class="number display digits"
    inputmode="numeric"
    aria-label={label}
    {value}
    onchange={typed}
  />
  <GlyphButton label="More {label}" onclick={() => set(value + 1)}>
    <GlyphIcon name="plus" />
  </GlyphButton>
</div>

<style>
  .stepper {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: var(--space-2);
  }

  .number {
    width: var(--size-stepper-number);
    padding: var(--space-1);
    background: var(--surface-raised);
    color: var(--ink);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-sunken);
    font-size: var(--text-display-lg);
    text-align: center;
  }
</style>
