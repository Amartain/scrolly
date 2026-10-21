<script lang="ts">
  import Button from '../components/Button.svelte';
  import { planning } from '../lib/api';
  import { view } from '../lib/view.svelte';
  import Header from './Header.svelte';
  import Screen1 from './Screen1.svelte';
</script>

<div class="zero">
  <div class="fogged" inert>
    <Header settingsOpen={false} onsettings={() => {}} />
    <Screen1 />
  </div>
  <div class="veil">
    <section class="message" aria-label="The Peak is Serene">
      <h1 class="display title">The Peak is Serene</h1>
      <Button
        label="Cultivate Your Focus"
        tone="primary"
        size="large"
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

  /* No frame: the title and the one button float on the fog, a little above the middle. */
  .message {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--space-8);
    margin-bottom: var(--space-12);
  }

  .title {
    margin: 0;
    font-size: var(--text-display-xl);
    text-shadow: var(--space-1) var(--space-1) 0 var(--surface-canvas);
  }
</style>
