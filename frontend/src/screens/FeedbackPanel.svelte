<!-- Settings › Feedback: three short forms, opened in the browser only when you click. -->
<script lang="ts">
  import Panel from '../components/Panel.svelte';
  import { FEEDBACK } from '../lib/copy';
</script>

<Panel title={FEEDBACK.title}>
  <div class="body">
    <p class="note">{FEEDBACK.note}</p>
    <ul>
      {#each FEEDBACK.links as link (link.href)}
        <li><a href={link.href} target="_blank" rel="noopener noreferrer">{link.label}</a></li>
      {/each}
    </ul>
  </div>
</Panel>

<style>
  .body {
    padding: var(--space-4);
  }

  .note {
    margin: 0;
    margin-bottom: var(--space-3);
    color: var(--ink-muted);
  }

  ul {
    margin: 0;
    padding: 0;
    list-style: none;
    display: flex;
    flex-wrap: wrap;
    gap: var(--space-5);
  }

  a {
    color: var(--ink);
    text-decoration: underline;
    text-underline-offset: var(--space-1);
  }
</style>
