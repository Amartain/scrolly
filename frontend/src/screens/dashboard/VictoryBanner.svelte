<script lang="ts">
  import Panel from '../../components/Panel.svelte';
  import HandscrollIcon from '../../icons/HandscrollIcon.svelte';
</script>

<Panel title="The Sun Sets on the Peak">
  <div class="banner">
    <HandscrollIcon size={64} />
    <div>
      <p class="lead">Every trial on the scroll is conquered.</p>
      <p class="rest">Rest is part of the path.</p>
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

  .lead {
    font-size: var(--text-body-lg);
  }

  .rest {
    color: var(--ink-muted);
  }
</style>
