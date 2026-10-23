<!-- The bottom-left corner of planning, fixed so nothing moves: Knowledge of the Dao (owner, 2026-10-23:
     "in Phase 1 instead of the clock"), and from Phase 2 the planning clock beside it. -->
<script lang="ts">
  import KnowledgeBar from './KnowledgeBar.svelte';
  import PlanningTimer from './PlanningTimer.svelte';

  let { clock }: { clock: boolean } = $props();
</script>

<div class="corner">
  <KnowledgeBar place="corner" />
  {#if clock}<PlanningTimer />{/if}
</div>

<style>
  .corner {
    position: fixed;
    left: var(--size-gutter);
    bottom: var(--space-2);
    z-index: 10;
    display: flex;
    align-items: flex-end;
    gap: var(--space-3);
  }
</style>
