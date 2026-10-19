<!-- A framed counter with a big numeral. The number comes from Python; this only draws it. -->
<script lang="ts">
  let { title, value }: { title: string; value: number } = $props();
</script>

<section class="card" aria-label={title}>
  <h2 class="label display">{title}</h2>
  <p class="figure display">{value}</p>
</section>

<style>
  .card {
    display: flex;
    flex-direction: column;
    gap: var(--space-1);
    padding: var(--space-2) var(--space-4);
    background: var(--surface-panel);
    background-image: var(--gloss-faint);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-panel);
  }

  .label {
    margin: 0;
    color: var(--ink-muted);
    font-size: var(--text-display-sm);
  }

  .figure {
    margin: 0;
    color: var(--num);
    font-size: var(--text-numeral);
    line-height: 1;
    text-shadow: var(--space-1) var(--space-1) 0 var(--num-shadow);
  }
</style>
