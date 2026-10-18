<script lang="ts">
  import Button from '../components/Button.svelte';
  import { planning } from '../lib/api';
  import { view } from '../lib/view.svelte';
  import Screen1 from './Screen1.svelte';
</script>

<div class="zero">
  <div class="fogged" inert><Screen1 /></div>
  <div class="veil">
    <section class="message" aria-label="The Peak is Serene">
      <h1 class="display title">The Peak is Serene</h1>
      <p class="line">Nothing is on the scroll today.</p>
      <Button
        label="Cultivate Your Focus"
        tone="primary"
        onclick={() => view.act(planning.start)}
      />
    </section>
  </div>
</div>

<style>
  .zero {
    position: relative;
    flex: 1;
    min-height: 0;
    display: flex;
    flex-direction: column;
  }

  .fogged {
    flex: 1;
    min-height: 0;
    display: flex;
    flex-direction: column;
  }

  .veil {
    position: absolute;
    inset: 0;
    display: grid;
    place-items: center;
    background: color-mix(in srgb, var(--surface-canvas) 80%, transparent);
    backdrop-filter: blur(var(--space-2));
  }

  .message {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--space-4);
    padding: var(--space-10) var(--space-12);
    background: var(--surface-panel);
    background-image: var(--gloss-faint);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-panel);
  }

  .title {
    margin: 0;
    font-size: var(--text-display-xl);
  }

  .line {
    margin: 0;
    color: var(--ink-muted);
    font-size: var(--text-body-lg);
  }
</style>
