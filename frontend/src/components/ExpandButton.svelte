<script lang="ts">
  import GlyphButton from './GlyphButton.svelte';

  let { label, onclick }: { label: string; onclick: () => void } = $props();
</script>

<GlyphButton {label} {onclick}>
  <span class="mark" aria-hidden="true">⛶</span>
</GlyphButton>

<style>
  .mark {
    font-size: var(--text-body-md);
    line-height: 1;
  }
</style>
