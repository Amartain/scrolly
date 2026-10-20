<!-- The ring as a dial: drag round it to set minutes, or type them. Arrow keys and PageUp/PageDown work
     through a range input that is there for the keyboard (hard rule 9). The server holds the limits. -->
<script lang="ts">
  import type { Snippet } from 'svelte';
  import RingFrame, { type Tone } from './RingFrame.svelte';

  let {
    value = $bindable(),
    max,
    prompt,
    unit,
    tone,
    children,
  }: {
    value: number;
    max: number;
    prompt: string;
    unit: string;
    tone: Tone;
    children: Snippet;
  } = $props();

  const BIG_STEP = 5;
  const INNER = 0.3; // a press inside this part of the ring (by radius) is not a drag

  let dial: HTMLDivElement | undefined = $state();
  let dragging = false;
  let typing = $state(false);
  let field: HTMLInputElement | undefined = $state();
  let range: HTMLInputElement | undefined = $state();

  // The dial takes the keyboard when it appears, so arrow keys and Enter work at once.
  $effect(() => range?.focus());

  function pick(event: PointerEvent, first: boolean) {
    if (!dial) return;
    const box = dial.getBoundingClientRect();
    const dx = event.clientX - (box.left + box.width / 2);
    const dy = event.clientY - (box.top + box.height / 2);
    const turns = (Math.atan2(dx, -dy) / (2 * Math.PI) + 1) % 1;
    let next = Math.max(1, Math.round(turns * max));
    // Round the top the value would jump from one end to the other: keep it at the nearer end.
    if (!first && Math.abs(next - value) > max / 2) next = value > max / 2 ? max : 1;
    value = next;
  }

  function onpointerdown(event: PointerEvent) {
    if (!dial) return;
    const box = dial.getBoundingClientRect();
    const dx = event.clientX - (box.left + box.width / 2);
    const dy = event.clientY - (box.top + box.height / 2);
    if (Math.hypot(dx, dy) < box.width * INNER) return;
    dial.setPointerCapture(event.pointerId);
    dragging = true;
    pick(event, true);
  }

  const onpointermove = (event: PointerEvent) => dragging && pick(event, false);
  const stop = () => (dragging = false);

  function onkeydown(event: KeyboardEvent) {
    if (event.key !== 'PageUp' && event.key !== 'PageDown') return;
    event.preventDefault();
    const step = event.key === 'PageUp' ? BIG_STEP : -BIG_STEP;
    value = Math.min(max, Math.max(1, value + step));
  }

  function commit(text: string) {
    const next = Number.parseInt(text, 10);
    if (!Number.isNaN(next)) value = Math.min(max, Math.max(1, next));
    typing = false;
  }

  $effect(() => {
    if (typing && field) {
      field.focus();
      field.select();
    }
  });
</script>

<!-- The pointer is one way to turn the dial; the range input inside is the keyboard's. -->
<!-- svelte-ignore a11y_no_static_element_interactions -->
<div
  class="dial"
  bind:this={dial}
  {onpointerdown}
  {onpointermove}
  onpointerup={stop}
  onpointercancel={stop}
>
  <RingFrame fill={(value / max) * 100} {tone} label={prompt} role="group">
    <input
      class="range"
      bind:this={range}
      type="range"
      min="1"
      {max}
      step="1"
      bind:value
      aria-label={prompt}
      aria-valuetext="{value} {unit}"
      {onkeydown}
    />
    <p class="ask display">{prompt}</p>
    {#if typing}
      <input
        class="big display digits type"
        inputmode="numeric"
        aria-label="Type the {unit}"
        bind:this={field}
        value={String(value)}
        onkeydown={(event) => {
          if (event.key === 'Enter') commit(event.currentTarget.value);
          else if (event.key === 'Escape') typing = false;
          else return;
          event.preventDefault();
          event.stopPropagation();
        }}
        onblur={(event) => commit(event.currentTarget.value)}
      />
    {:else}
      <button
        class="big display digits numeral"
        type="button"
        aria-label="{value} {unit}, press to type"
        onclick={() => (typing = true)}>{value}</button
      >
    {/if}
    <p class="small">{unit}</p>
    {@render children()}
  </RingFrame>
</div>

<style>
  .dial {
    touch-action: none;
    cursor: grab;
  }

  .dial:active {
    cursor: grabbing;
  }

  .dial:has(.range:focus-visible) :global(.ring) {
    outline: var(--border-width) solid var(--line);
    outline-offset: var(--space-2);
  }

  .range {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    opacity: 0;
    pointer-events: none;
  }

  .numeral,
  .type {
    padding: 0;
    background: none;
    border: 0;
    font-family: inherit;
    cursor: text;
  }

  .type {
    width: 100%;
    text-align: center;
    border-bottom: var(--border-width) solid var(--line);
  }
</style>
