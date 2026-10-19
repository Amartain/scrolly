<!-- A Horizon item: title, estimate, then the type mark (the Mandate switch) and the buttons. -->
<script lang="ts">
  import Button from '../../components/Button.svelte';
  import EditableText from '../../components/EditableText.svelte';
  import GlyphButton from '../../components/GlyphButton.svelte';
  import TypeMark from '../../components/TypeMark.svelte';
  import GlyphIcon from '../../icons/GlyphIcon.svelte';
  import { horizon, type HorizonItem } from '../../lib/api';
  import { view } from '../../lib/view.svelte';

  let {
    item,
    onsummon,
    editable = false,
  }: { item: HorizonItem; onsummon: () => void; editable?: boolean } = $props();

  let name = $state<EditableText>();
  const edit = (patch: Parameters<typeof horizon.edit>[1]) =>
    view.act(() => horizon.edit(item.id, patch));

  async function commitEstimate(event: Event) {
    const input = event.currentTarget as HTMLInputElement;
    if (input.value.trim() === item.expected_text) return;
    if (!(await edit({ estimate: input.value }))) input.value = item.expected_text;
  }
</script>

{#if editable}
  <EditableText
    value={item.title}
    label="Rename {item.title}"
    onsave={(title) => edit({ title })}
    bind:this={name}
  />
  <input
    class="estimate digits"
    value={item.expected_text}
    placeholder="—"
    aria-label="Estimate for {item.title}"
    onchange={commitEstimate}
  />
{:else}
  <span class="title read">{item.title}</span>
  <span class="figure digits">{item.expected_text}</span>
{/if}
<TypeMark
  type={item.type}
  title={item.title}
  onToggle={editable ? () => edit({ is_mandate: !item.is_mandate }) : undefined}
/>
{#if editable}
  <GlyphButton label="Edit {item.title}" onclick={() => name?.start()}>
    <GlyphIcon name="pencil" />
  </GlyphButton>
  <GlyphButton
    label="Discard {item.title}"
    onclick={() => view.act(() => horizon.discard(item.id))}
  >
    <GlyphIcon name="x" />
  </GlyphButton>
{/if}
<Button label="Summon" tone="horizon" description="Summon {item.title}" onclick={onsummon} />

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

  .estimate {
    flex: none;
    width: var(--size-estimate);
    height: var(--size-glyph-button);
    padding-inline: var(--space-2);
    background: var(--surface-raised);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-sunken);
    color: var(--ink);
    font-size: var(--text-body-md);
    text-align: right;
  }
</style>
