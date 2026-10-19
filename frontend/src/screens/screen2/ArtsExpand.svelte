<!-- The Arts of one kind at full size: add, rename, set the duration, delete. -->
<script lang="ts">
  import Button from '../../components/Button.svelte';
  import EditableText from '../../components/EditableText.svelte';
  import GlyphButton from '../../components/GlyphButton.svelte';
  import Modal from '../../components/Modal.svelte';
  import RowList from '../../components/RowList.svelte';
  import TypeMark from '../../components/TypeMark.svelte';
  import GlyphIcon from '../../icons/GlyphIcon.svelte';
  import { arts, type Art, type ArtKind } from '../../lib/api';
  import { EMPTY } from '../../lib/copy';
  import { view } from '../../lib/view.svelte';
  import Notice from '../plan/Notice.svelte';

  let { kind, onclose }: { kind: ArtKind; onclose: () => void } = $props();

  const heading = $derived(kind === 'foundational' ? 'Foundational Arts' : 'Restorative Arts');
  const list = $derived(
    (kind === 'foundational' ? view.planning?.foundational : view.planning?.restorative) ?? [],
  );
  let title = $state('');
  let estimate = $state('');
  let nameField = $state<HTMLInputElement>();

  // Opened from the + in the header: the name is ready to type. Runs after Modal has shown the dialog.
  $effect(() => nameField?.focus());

  async function add(event?: Event) {
    event?.preventDefault();
    if (!title.trim()) return;
    if (await view.act(() => arts.add(kind, title, estimate))) {
      title = '';
      estimate = '';
    }
  }

  async function setDuration(art: Art, event: Event) {
    const input = event.currentTarget as HTMLInputElement;
    if (input.value.trim() === art.expected_text) return;
    if (!(await view.act(() => arts.edit(art.id, { estimate: input.value })))) {
      input.value = art.expected_text;
    }
  }
</script>

{#snippet row(art: Art)}
  <TypeMark type={kind} />
  <EditableText
    value={art.title}
    label="Rename {art.title}"
    onsave={(next) => view.act(() => arts.edit(art.id, { title: next }))}
  />
  <input
    class="duration digits"
    value={art.expected_text}
    placeholder="30m"
    aria-label="Duration of {art.title}"
    onchange={(event) => setDuration(art, event)}
  />
  <GlyphButton label="Delete {art.title}" onclick={() => view.act(() => arts.remove(art.id))}>
    <GlyphIcon name="x" />
  </GlyphButton>
{/snippet}

<Modal title="{heading}, expanded" tone={kind} {onclose}>
  <form class="add" onsubmit={add}>
    <input
      bind:this={nameField}
      bind:value={title}
      placeholder="Name a practice…"
      aria-label="A new Art"
    />
    <input
      class="duration digits"
      bind:value={estimate}
      placeholder="30m"
      aria-label="Duration of the new Art"
    />
    <Button label="Add" tone={kind} onclick={() => add()} />
    <!-- Two fields: a hidden submit lets Enter add from either. -->
    <button type="submit" hidden tabindex="-1" aria-hidden="true"></button>
  </form>
  <div class="note"><Notice /></div>
  <RowList items={list} {row} empty={EMPTY[kind]} />
</Modal>

<style>
  .add {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    height: calc(var(--size-row) * 2);
    padding-inline: var(--space-4);
    background: var(--card-ink-head);
  }

  .note {
    padding-inline: var(--space-4);
    background: var(--card-ink-row-a);
  }

  input {
    flex: 1;
    min-width: 0;
    height: var(--size-field);
    padding-inline: var(--space-3);
    background: var(--surface-raised);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-sunken);
    color: var(--ink);
    font-family: var(--font-body);
    font-size: var(--text-body-md);
  }

  input.duration {
    flex: none;
    width: var(--size-estimate);
    height: var(--size-glyph-button);
    text-align: right;
  }

  .add input.duration {
    height: var(--size-field);
  }
</style>
