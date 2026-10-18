<script lang="ts">
  import TrialMark from './TrialMark.svelte';

  let {
    trial,
  }: { trial: { title: string; expected_text: string; is_mandate: boolean; origin_type: string } } =
    $props();
</script>

<TrialMark {trial} />
<span class="title read">{trial.title}</span>
<span class="estimate digits">{trial.expected_text}</span>

<style>
  .title {
    flex: 1;
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .estimate {
    color: var(--ink-muted);
  }
</style>
