<!-- The `?` beside a header: hover or focus gives a short tip, a click opens the scroll. The tip sits
     over what is below, so nothing moves. -->
<script lang="ts">
  import { GUIDANCE, GUIDE, type GuideKey } from '../lib/copy-guidance';
  import { guidance } from '../lib/guidance.svelte';

  let { topic }: { topic: GuideKey } = $props();

  const guide = $derived(GUIDE[topic]);
  const tipId = $derived(`guide-tip-${topic}`);
</script>

<span class="guide">
  <button
    class="button display"
    type="button"
    aria-label={GUIDANCE.button(guide.name)}
    aria-describedby={tipId}
    onclick={() => guidance.open(topic)}>?</button
  >
  <span class="tip" id={tipId} role="tooltip">{guide.tip}</span>
</span>

<style>
  .guide {
    position: relative;
    flex: none;
    display: inline-flex;
  }

  .button {
    width: var(--size-guide-button);
    height: var(--size-guide-button);
    padding: 0;
    cursor: pointer;
    background: var(--btn);
    background-image: var(--gloss-btn);
    color: var(--ink);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-button);
    font-size: var(--text-display-sm);
    line-height: 1;
  }

  .button:active {
    box-shadow: none;
    transform: translate(var(--shadow-offset), var(--shadow-offset));
  }

  .tip {
    position: absolute;
    top: 100%;
    left: 0;
    z-index: 2;
    margin-top: var(--space-2);
    padding: var(--space-2) var(--space-3);
    width: max-content;
    max-width: 16rem;
    background: var(--surface-raised);
    color: var(--ink);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-button);
    font-size: var(--text-body-sm);
    font-weight: normal;
    letter-spacing: normal;
    text-transform: none;
    /* Not displayed until asked for: an invisible tip would still be as wide as its text, and
       widen a narrow panel before the fonts load. */
    display: none;
    pointer-events: none;
  }

  .guide:hover .tip,
  .button:focus-visible + .tip {
    display: block;
  }
</style>
