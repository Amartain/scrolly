<script lang="ts">
  import ArtIcon from '../icons/ArtIcon.svelte';
  import CloudIcon from '../icons/CloudIcon.svelte';
  import MandateMark from './MandateMark.svelte';

  let { trial }: { trial: { is_mandate: boolean; origin_type: string } } = $props();
</script>

{#if trial.is_mandate}
  <MandateMark />
{:else if trial.origin_type === 'foundational_art'}
  <ArtIcon kind="foundational" />
{:else if trial.origin_type === 'restorative_art'}
  <ArtIcon kind="restorative" />
{:else}
  <CloudIcon />
{/if}
