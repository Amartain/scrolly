<script lang="ts">
  import Panel from '../../components/Panel.svelte';
</script>

<Panel title="Guidance">
  <div class="copy">
    <p>
      <strong>Why:</strong> equal minutes rarely cost equal energy. Weighing your Qi teaches you what
      a task takes from you, not only how long it takes.
    </p>
    <p>
      <strong>How:</strong> give each trial a Qi cost from 0 to 100. Nothing is calculated for you: a
      short errand may cost 40, a long focused session only 10. Restorative Arts give Qi back.
    </p>
    <p>
      <strong>Your core:</strong> it begins at 100 Qi on a rested day. Spending past it is allowed, but
      the next day begins lower, because the body keeps its own ledger. Rest comes first: when tired,
      begin with a Restorative Art.
    </p>
  </div>
</Panel>

<style>
  .copy {
    padding: var(--space-3) var(--space-4);
    font-size: var(--text-body-md);
  }

  p {
    margin: 0;
    margin-bottom: var(--space-3);
  }

  p:last-child {
    margin-bottom: 0;
  }
</style>
