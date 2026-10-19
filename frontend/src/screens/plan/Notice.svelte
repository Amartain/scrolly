<script lang="ts">
  import NoticeText from '../../components/NoticeText.svelte';
  import { view } from '../../lib/view.svelte';
</script>

<!-- One reserved line so a message never moves anything. -->
<p class="notice" role="status">
  {#if view.notice}<NoticeText />{:else}&nbsp;{/if}
</p>

<style>
  .notice {
    margin: 0;
    color: var(--ink-muted);
    font-size: var(--text-body-md);
  }
</style>
