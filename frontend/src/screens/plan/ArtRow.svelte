<!-- An Art template on an Arts-only list: its mark leads (static, nothing to switch), then title, default
     duration, and ↑ to summon a copy. -->
<script lang="ts">
  import GlyphButton from '../../components/GlyphButton.svelte';
  import TypeMark from '../../components/TypeMark.svelte';
  import GlyphIcon from '../../icons/GlyphIcon.svelte';
  import type { Art } from '../../lib/api';

  let {
    art,
    kind,
    onsummon,
  }: { art: Art; kind: 'foundational' | 'restorative'; onsummon: () => void } = $props();
</script>

<TypeMark type={kind} />
<span class="title read">{art.title}</span>
<span class="figure digits">{art.expected_text}</span>
<GlyphButton label="Summon {art.title}" onclick={onsummon}>
  <GlyphIcon name="up" />
</GlyphButton>

<style>
  .title {
    flex: 1;
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .figure {
    color: var(--ink-muted);
  }
</style>
