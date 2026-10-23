<script lang="ts">
  import { onMount } from 'svelte';
  import Button from '../components/Button.svelte';
  import ScrollSheet from '../components/ScrollSheet.svelte';
  import { planning } from '../lib/api';
  import { cutLine } from '../lib/cut-line';
  import { view } from '../lib/view.svelte';
  import Notice from './plan/Notice.svelte';
  import OnScroll from './plan/OnScroll.svelte';
  import SourcePanels from './plan/SourcePanels.svelte';

  const SAVE_DELAY_MS = 400;

  const sources = $derived(
    (view.planning?.horizon.length ?? 0) +
      (view.planning?.foundational.length ?? 0) +
      (view.planning?.restorative.length ?? 0) >
      0,
  );

  // Read once: a refresh must never overwrite what is being typed.
  let text = $state(view.planning?.text ?? '');
  let timer: ReturnType<typeof setTimeout> | undefined;

  onMount(() => {
    view.notice = '';
    return () => {
      if (timer !== undefined) void planning.saveText(text);
    };
  });

  function edit() {
    view.rememberText(text);
    clearTimeout(timer);
    timer = setTimeout(() => {
      timer = undefined;
      void planning.saveText(text);
    }, SAVE_DELAY_MS);
  }

  async function saveNow(): Promise<boolean> {
    clearTimeout(timer);
    timer = undefined;
    return view.act(() => planning.saveText(text));
  }

  async function proceed() {
    if (await saveNow()) await view.act(planning.proceed);
  }

  async function abandon() {
    clearTimeout(timer);
    timer = undefined;
    await view.act(planning.abandon);
  }
</script>

<ScrollSheet title="Inscribe the Scroll" guide="inscribe">
  <!-- The Horizon and the Arts only once they hold something: a first day is the brain dump alone. -->
  <div class="phase" class:alone={!sources}>
    {#if sources}<SourcePanels />{/if}
    <div class="column">
      <div class="write">
        <label class="prompt" for="dump">
          Empty your mind. Scribe every trial you must conquer today. <strong
            >One trial per line.</strong
          >
        </label>
        <textarea
          id="dump"
          data-tour="dump"
          data-tour-on="input"
          use:cutLine
          bind:value={text}
          oninput={edit}
          placeholder={'Morning coffee + podcast\nNutritious breakfast\nRead chapter 1'}
        ></textarea>
      </div>
      <div class="staged"><OnScroll /></div>
      <Notice />
      <div class="actions">
        <Button label="Abandon" onclick={abandon} />
        <Button label="Proceed: Divine the Time" tone="primary" tour="proceed" onclick={proceed} />
      </div>
    </div>
  </div>
</ScrollSheet>

<style>
  .phase {
    flex: 1;
    min-height: 0;
    display: grid;
    grid-template-columns: minmax(0, 2fr) minmax(0, 3fr);
    gap: var(--space-5);
  }

  .phase.alone {
    grid-template-columns: minmax(0, 1fr);
  }

  .column {
    display: grid;
    grid-template-rows: minmax(0, 1fr) var(--size-staged) auto auto;
    gap: var(--space-3);
    min-height: 0;
    padding-right: var(--shadow-room);
    padding-bottom: var(--shadow-room);
  }

  .write {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
    min-height: 0;
  }

  .prompt {
    font-size: var(--text-body-lg);
  }

  textarea {
    flex: 1;
    min-height: 0;
    padding: var(--space-3);
    resize: none;
    background: var(--surface-raised);
    color: var(--ink);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-sunken);
    font-family: var(--font-body);
    font-size: var(--text-body-md);
  }

  .staged {
    display: grid;
    min-height: 0;
  }

  .actions {
    display: flex;
    justify-content: space-between;
  }
</style>
