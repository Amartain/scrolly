<!-- A Horizon item: title, its duration in small figures, the type mark, then Summon or the edit buttons. -->
<script lang="ts">
  import Button from '../../components/Button.svelte';
  import EditableText from '../../components/EditableText.svelte';
  import GlyphButton from '../../components/GlyphButton.svelte';
  import TypeMark from '../../components/TypeMark.svelte';
  import GlyphIcon from '../../icons/GlyphIcon.svelte';
  import { horizon, type HorizonItem } from '../../lib/api';
  import { workedNote } from '../../lib/copy';
  import { view } from '../../lib/view.svelte';

  /** `editable` is the expanded view: rename, switch the type, delete. Otherwise the row only summons. */
  let {
    item,
    onsummon,
    editable = false,
  }: { item: HorizonItem; onsummon?: () => void; editable?: boolean } = $props();

  const edit = (patch: Parameters<typeof horizon.edit>[1]) =>
    view.act(() => horizon.edit(item.id, patch));
</script>

{#if editable}
  <EditableText
    value={item.title}
    label="Rename {item.title}"
    onsave={(title) => edit({ title })}
  />
{:else}
  <span class="title read small">{item.title}</span>
{/if}
<span class="figure digits">{item.expected_text}</span>
{#if item.worked_text}<span class="figure digits">{workedNote(item.worked_text)}</span>{/if}
<TypeMark
  type={item.type}
  title={item.title}
  onToggle={editable ? () => edit({ is_mandate: !item.is_mandate }) : undefined}
/>
{#if editable}
  <GlyphButton
    label="Discard {item.title}"
    onclick={() => view.act(() => horizon.discard(item.id))}
  >
    <GlyphIcon name="x" />
  </GlyphButton>
{:else if onsummon}
  <Button label="Summon" tone="horizon" chip description="Summon {item.title}" onclick={onsummon} />
{/if}

<style>
  .title {
    flex: 1;
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .small {
    font-size: var(--text-read-sm);
  }

  .figure {
    color: var(--ink-muted);
    font-size: var(--text-body-sm);
  }
</style>
