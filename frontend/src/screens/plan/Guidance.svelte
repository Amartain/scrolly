<script lang="ts">
  import Button from '../../components/Button.svelte';

  let open = $state(true);
</script>

<section class="guidance" aria-label="Guidance">
  <div class="bar">
    <h2 class="display title">Guidance Scroll</h2>
    <Button label={open ? 'Minimize Guidance' : 'Show Guidance'} onclick={() => (open = !open)} />
  </div>
  {#if open}
    <div class="copy">
      <p>
        To bypass the mind's resistance, do not organize or estimate yet. Empty your thoughts below.
      </p>
      <ul>
        <li><strong>Brain Dump:</strong> one trial per line.</li>
        <li><strong>The Horizon:</strong> summon future ideas waiting for their time.</li>
        <li>
          <strong>Arts:</strong> opt in to habits and energy recovery without the pressure of auto-adding.
        </li>
      </ul>
    </div>
  {/if}
</section>

<style>
  .guidance {
    padding: var(--space-3) var(--space-4);
    background: var(--surface-raised);
    border: var(--border-width) dashed var(--gold);
  }

  .bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--space-3);
  }

  .title {
    margin: 0;
    font-size: var(--text-display-md);
    color: var(--ink-muted);
  }

  .copy {
    font-size: var(--text-body-md);
  }

  p {
    margin: var(--space-2) 0;
  }

  ul {
    margin: 0;
    padding-left: var(--space-5);
  }
</style>
