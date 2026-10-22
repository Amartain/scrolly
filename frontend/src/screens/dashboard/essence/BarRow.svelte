<!-- One row of the Essence panel: its name and one bar, all shares from Python. Solid is what is done; a faint
     wash behind it is what is planned; Essence's gold notch is the sunset. Qi takes its zone's colour, with ticks
     where Harmonious and Igniting the Blood end. The numbers show over the bar on hover or keyboard focus. -->
<script lang="ts">
  type Tone = 'essence' | 'harmonious' | 'igniting' | 'strain';

  let {
    label,
    done,
    plan,
    tip,
    tone = 'essence',
    planTone = tone,
    sunset = null,
    ticks = [],
  }: {
    label: string;
    /** How far the solid fill reaches, 0 to 100. */
    done: number;
    /** How far the faint plan reaches, 0 to 100. */
    plan: number;
    /** The numbers, shown on hover or focus and read out by screen readers. */
    tip: string;
    tone?: Tone;
    planTone?: Tone;
    sunset?: number | null;
    ticks?: number[];
  } = $props();
</script>

<div class="row">
  <span class="label display">{label}</span>
  <!-- svelte-ignore a11y_no_noninteractive_tabindex (focus shows the numbers, as hover does) -->
  <div
    class="track"
    role="meter"
    tabindex="0"
    aria-label={label}
    aria-valuemin={0}
    aria-valuemax={100}
    aria-valuenow={Math.round(done)}
    aria-valuetext={tip}
  >
    <span class="plan" data-tone={planTone} style:width="{plan}%"></span>
    <span class="fill" data-tone={tone} style:width="{done}%"></span>
    {#each ticks as tick (tick)}<span class="tick" style:left="{tick}%"></span>{/each}
    {#if sunset !== null}<span class="sunset" style:left="{sunset}%"></span>{/if}
    <span class="tip digits" aria-hidden="true">{tip}</span>
  </div>
</div>

<style>
  .row {
    display: grid;
    grid-template-columns: var(--size-tile-label) minmax(0, 1fr);
    align-items: center;
    gap: var(--space-3);
    line-height: 1;
  }

  .label {
    font-size: var(--text-display-sm);
  }

  .track {
    position: relative;
    height: var(--size-tile);
    background: var(--inset);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-sunken);
    cursor: default;
  }

  [data-tone='essence'] {
    --tone: var(--essence-ink);
  }

  [data-tone='harmonious'] {
    --tone: var(--qi-calm);
  }

  [data-tone='igniting'] {
    --tone: var(--qi-surge);
  }

  [data-tone='strain'] {
    --tone: var(--qi-redline);
  }

  .plan,
  .fill {
    position: absolute;
    inset: 0 auto 0 0;
  }

  .plan {
    background: color-mix(in srgb, var(--tone) 28%, transparent);
  }

  .fill {
    background-color: var(--tone);
    background-image: var(--gloss);
  }

  /* A zone's end: a short notch from the top and the bottom, in muted ink so it shows on light and dark
     tracks alike. */
  .tick {
    position: absolute;
    top: 0;
    bottom: 0;
    width: var(--border-width);
    translate: -50% 0;
    background: linear-gradient(
      var(--ink-muted) 30%,
      transparent 30%,
      transparent 70%,
      var(--ink-muted) 70%
    );
  }

  /* The sunset: a gold line standing a little proud of the bar. */
  .sunset {
    position: absolute;
    top: calc(-1 * var(--space-1));
    bottom: calc(-1 * var(--space-1));
    width: var(--border-width);
    translate: -50% 0;
    background: var(--gold);
    outline: var(--border-width) solid var(--line);
  }

  .tip {
    position: absolute;
    inset: 0;
    display: grid;
    place-items: center;
    padding-inline: var(--space-2);
    overflow: hidden;
    background: color-mix(in srgb, var(--inset) 82%, transparent);
    color: var(--num-text);
    font-size: var(--text-body-sm);
    white-space: nowrap;
    opacity: 0;
    transition: opacity 150ms;
  }

  .track:hover .tip,
  .track:focus-visible .tip {
    opacity: 1;
  }

  @media (prefers-reduced-motion: reduce) {
    .tip {
      transition: none;
    }
  }
</style>
