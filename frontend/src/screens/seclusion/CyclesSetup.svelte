<!-- Harmonious Cycles, before it starts: the ring is a dial. Focus, then the break (the ring turns the
     break shade), then how many cycles, then Start. What was set last time is already there, so a
     return is Next, Next, Start. Enter does the same as the button. -->
<script lang="ts">
  import { untrack } from 'svelte';
  import Button from '../../components/Button.svelte';
  import { SECLUSION } from '../../lib/copy-seclusion';
  import { onControl, typing } from '../../lib/keys';
  import { seclusion } from '../../lib/seclusion.svelte';
  import type { SeclusionState } from '../../lib/seclusion-api';
  import Dial from './Dial.svelte';
  import RingFrame from './RingFrame.svelte';
  import Stepper from './Stepper.svelte';

  type Step = 'focus' | 'break' | 'cycles';

  let { room }: { room: SeclusionState } = $props();

  const copy = SECLUSION.cycles;
  let step = $state<Step>('focus');
  let focus = $state(untrack(() => room.plan.focus_min));
  let rest = $state(untrack(() => room.plan.break_min));
  let cycles = $state(untrack(() => room.plan.cycles));

  const start = () => seclusion.startCycles({ focus_min: focus, break_min: rest, cycles });
  const forward = () => {
    if (step === 'focus') step = 'break';
    else if (step === 'break') step = 'cycles';
    else void start();
  };
  const back = () => (step = step === 'cycles' ? 'break' : 'focus');

  function onkeydown(event: KeyboardEvent) {
    const modified = event.altKey || event.ctrlKey || event.metaKey || event.shiftKey;
    const onDial = event.target instanceof HTMLInputElement && event.target.type === 'range';
    if (event.key !== 'Enter' || modified || onControl(event.target)) return;
    if (typing(event.target) && !onDial) return;
    event.preventDefault();
    forward();
  }
</script>

<svelte:window {onkeydown} />

{#snippet buttons()}
  <div class="row">
    {#if step !== 'focus'}
      <button class="link display" type="button" onclick={back}>{copy.back}</button>
    {/if}
    <Button
      label={step === 'cycles' ? SECLUSION.start : copy.next}
      tone={step === 'cycles' ? 'primary' : 'default'}
      onclick={forward}
    />
  </div>
{/snippet}

{#if step === 'focus'}
  <Dial
    bind:value={focus}
    max={room.limits.focus_max_min}
    prompt={copy.askFocus}
    unit={copy.minutes}
    tone="cycles"
  >
    {@render buttons()}
  </Dial>
{:else if step === 'break'}
  <Dial
    bind:value={rest}
    max={room.limits.break_max_min}
    prompt={copy.askBreak}
    unit={copy.minutes}
    tone="cycles-break"
  >
    {@render buttons()}
  </Dial>
{:else}
  <RingFrame fill={100} tone="cycles" label={copy.askCycles} role="group">
    <p class="ask display">{copy.askCycles}</p>
    <Stepper
      value={cycles}
      min={1}
      max={room.limits.cycles_max}
      label={copy.cycles}
      onchange={(next) => (cycles = next)}
    />
    <p class="small">{focus} + {rest} {copy.minutes}</p>
    {@render buttons()}
  </RingFrame>
{/if}

<style>
  .row {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: var(--space-4);
  }

  .link {
    padding: 0;
    background: none;
    border: 0;
    color: var(--ink-muted);
    font-size: var(--text-display-sm);
    text-decoration: underline;
    cursor: pointer;
  }
</style>
