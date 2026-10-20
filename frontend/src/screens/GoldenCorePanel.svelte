<script lang="ts">
  import Panel from '../components/Panel.svelte';
  import { goldenCore } from '../lib/api';
  import { view } from '../lib/view.svelte';

  const enabled = $derived(view.planning?.qi.enabled ?? false);
</script>

<Panel title="Golden Core">
  <div class="body">
    <label class="choice display">
      <input
        type="checkbox"
        checked={enabled}
        onchange={(event) => view.act(() => goldenCore.set(event.currentTarget.checked))}
      />
      Weigh Qi while planning
    </label>
    <p class="note">
      An optional phase after estimating: give each trial a Qi cost, and watch the day's energy. It
      can be switched off at any time.
    </p>
  </div>
</Panel>

<style>
  .body {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: var(--space-5);
    padding: var(--space-4);
  }

  .choice {
    position: relative;
    flex: none;
    padding: var(--space-3) var(--space-5);
    cursor: pointer;
    background: var(--btn);
    background-image: var(--gloss-btn);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-button);
    font-size: var(--text-display-sm);
  }

  .choice input {
    position: absolute;
    opacity: 0;
    inset: 0;
    margin: 0;
    cursor: inherit;
  }

  .choice:has(input:checked) {
    background: var(--strong);
    color: var(--on-strong);
    box-shadow: none;
    transform: translate(var(--shadow-offset), var(--shadow-offset));
  }

  .choice:has(input:focus-visible) {
    outline: var(--border-width) solid var(--gold);
    outline-offset: var(--space-1);
  }

  .note {
    margin: 0;
    color: var(--ink-muted);
    font-size: var(--text-body-md);
  }
</style>
