<!-- The finished day, kept on the dashboard once the ceremony is closed: the seal, the day's line
     and a compact tally. It takes the Immediate Trial's place. -->
<script lang="ts">
  import Panel from '../../components/Panel.svelte';
  import type { Victory } from '../../lib/api';
  import { SCENES, VICTORY } from '../../lib/copy-victory';

  let { victory }: { victory: Victory } = $props();

  const scene = $derived(SCENES[victory.scene]);
</script>

<Panel title={scene.title}>
  <div class="banner">
    <p class="seal read" lang="zh" aria-hidden="true">{scene.seal}</p>
    <div class="words">
      <p class="lead">{scene.lead}</p>
      <p class="line read">{victory.line}</p>
      <p class="tally digits">
        {VICTORY.row(victory.conquered, victory.mandates, victory.essence_text)}
      </p>
    </div>
  </div>
</Panel>

<style>
  .banner {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: var(--space-6);
    padding: var(--space-4);
    height: 100%;
  }

  p {
    margin: 0;
  }

  .seal {
    flex: none;
    display: grid;
    place-items: center;
    width: 2.5em;
    height: 2.5em;
    background: var(--gold);
    color: var(--on-gold);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-button);
    font-size: var(--text-display-xl);
  }

  .words {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
  }

  .lead {
    font-size: var(--text-body-lg);
  }

  .line {
    color: var(--ink-muted);
  }

  .tally {
    color: var(--num);
  }
</style>
