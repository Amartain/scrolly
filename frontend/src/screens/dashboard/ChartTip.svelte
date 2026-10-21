<!-- The value of one point or bar, shown on hover or keyboard focus. The chart places it: `x` and `y` are
     CSS lengths measured from the left of the chart's plot and from its bottom (or its top, when
     `above` is false), and `align` says which side of `x` the box grows to, so it never runs past
     the panel. The words come from Python. -->
<script lang="ts">
  let {
    text,
    x,
    y,
    align = 'center',
    above = true,
  }: {
    text: string;
    x: string;
    y: string;
    align?: 'start' | 'center' | 'end';
    above?: boolean;
  } = $props();
</script>

<span
  class="tip"
  data-align={align}
  style:left={x}
  style:bottom={above ? y : undefined}
  style:top={above ? undefined : y}
  role="status">{text}</span
>

<style>
  .tip {
    position: absolute;
    z-index: 1;
    padding: var(--space-1) var(--space-2);
    background: var(--surface-raised);
    color: var(--ink);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-button);
    font-size: var(--text-body-sm);
    white-space: nowrap;
    pointer-events: none;
  }

  .tip[data-align='center'] {
    transform: translateX(-50%);
  }

  .tip[data-align='end'] {
    transform: translateX(-100%);
  }
</style>
