<!-- One trial postponed or let go today. A double-click (or Enter when focused) summons it back to the
     scroll (owner, 2026-10-23); a single click does nothing, so nothing comes back by accident. -->
<script lang="ts">
  import { today, type LetGo } from '../../lib/api';
  import { LET_GO } from '../../lib/copy-dashboard';
  import { knowledge } from '../../lib/knowledge.svelte';
  import { view } from '../../lib/view.svelte';

  let { item }: { item: LetGo } = $props();

  // The tour learns it first: once summoned back, the name is gone from here.
  function back(event: Event) {
    void knowledge.learn('resummon', event.currentTarget as Element);
    return view.act(() => today.resummon(item.id));
  }
</script>

<span
  class="name"
  role="button"
  tabindex="0"
  title={LET_GO.hint}
  aria-label={LET_GO.back(item.title)}
  ondblclick={back}
  onkeydown={(event) => {
    if (event.key !== 'Enter') return;
    event.preventDefault();
    void back(event);
  }}>{item.title}</span
>

<style>
  .name {
    cursor: pointer;
  }

  .name:hover,
  .name:focus-visible {
    color: var(--growth-text);
    text-decoration: underline;
  }
</style>
