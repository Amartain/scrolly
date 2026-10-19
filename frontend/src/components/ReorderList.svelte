<script lang="ts" generics="T extends { id: string }">
  import { tick, type Snippet } from 'svelte';

  let {
    items,
    label,
    onreorder,
    row,
  }: { items: T[]; label: string; onreorder: (ids: string[]) => void; row: Snippet<[T]> } =
    $props();

  let list: HTMLUListElement;
  let dragging = $state<string | null>(null);
  let slot = $state(0);
  let indicatorY = $state(0);

  const ids = () => items.map((item) => item.id);

  /** The order after taking `id` out and putting it back at index `to`. */
  function moved(id: string, to: number): string[] {
    const order = ids().filter((other) => other !== id);
    order.splice(to, 0, id);
    return order;
  }

  const rows = () => [...list.querySelectorAll<HTMLElement>(':scope > li')];

  /** The gap (0..n) the pointer is over: how many rows are wholly above it. */
  function slotAt(y: number): number {
    return rows().filter((el) => {
      const box = el.getBoundingClientRect();
      return y > box.top + box.height / 2;
    }).length;
  }

  function edgeOf(index: number): number {
    const all = rows();
    const box = list.getBoundingClientRect();
    const target = index >= all.length ? all[all.length - 1] : all[index];
    const rect = target.getBoundingClientRect();
    return (index >= all.length ? rect.bottom : rect.top) - box.top;
  }

  function down(event: PointerEvent, id: string) {
    const target = event.target as HTMLElement;
    if (event.button !== 0 || target.closest('input, button, textarea, select, a')) return;
    event.preventDefault();
    dragging = id;
    slot = ids().indexOf(id);
    indicatorY = edgeOf(slot);
    (event.currentTarget as HTMLElement).setPointerCapture(event.pointerId);
  }

  function move(event: PointerEvent) {
    if (dragging === null) return;
    slot = slotAt(event.clientY);
    indicatorY = edgeOf(slot);
  }

  function drop() {
    if (dragging === null) return;
    const id = dragging;
    const from = ids().indexOf(id);
    const to = slot > from ? slot - 1 : slot;
    dragging = null;
    if (to !== from) onreorder(moved(id, to));
  }

  async function key(event: KeyboardEvent, id: string) {
    if (!event.altKey) return;
    const from = ids().indexOf(id);
    const last = items.length - 1;
    const wanted = { ArrowUp: from - 1, ArrowDown: from + 1, Home: 0, End: last }[event.key];
    if (wanted === undefined) return;
    event.preventDefault();
    const to = Math.max(0, Math.min(last, wanted));
    if (to === from) return;
    onreorder(moved(id, to));
    await tick();
    list.querySelector<HTMLElement>(`[data-id="${CSS.escape(id)}"]`)?.focus();
  }
</script>

<div class="wrap">
  <ul class="rows" aria-label={label} bind:this={list}>
    {#each items as item (item.id)}
      <!-- svelte-ignore a11y_no_noninteractive_tabindex, a11y_no_noninteractive_element_interactions -->
      <li
        class="row"
        class:dragging={dragging === item.id}
        data-id={item.id}
        tabindex="0"
        aria-keyshortcuts="Alt+ArrowUp Alt+ArrowDown Alt+Home Alt+End"
        onpointerdown={(event) => down(event, item.id)}
        onpointermove={move}
        onpointerup={drop}
        onpointercancel={() => (dragging = null)}
        onkeydown={(event) => key(event, item.id)}
      >
        {@render row(item)}
      </li>
    {/each}
  </ul>
  {#if dragging !== null}
    <div class="drop" style:top="{indicatorY}px" aria-hidden="true"></div>
  {/if}
</div>

<style>
  .wrap {
    position: relative;
  }

  .rows {
    margin: 0;
    padding: 0;
    list-style: none;
  }

  .row {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    min-height: var(--size-row);
    padding-inline: var(--space-4);
    font-size: var(--text-body-md);
    cursor: grab;
  }

  .row.dragging {
    opacity: 0.6;
    cursor: grabbing;
    user-select: none;
  }

  .drop {
    position: absolute;
    left: 0;
    right: 0;
    height: var(--border-width);
    transform: translateY(-50%);
    background: var(--strong);
    pointer-events: none;
  }
</style>
