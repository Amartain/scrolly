<!-- The last refusal as text, with the user's own titles in italics. -->
<script lang="ts">
  import { view } from '../lib/view.svelte';
</script>

{#each view.noticeParts as part}{#if part.em}<em>{part.text}</em>{:else}{part.text}{/if}{/each}
