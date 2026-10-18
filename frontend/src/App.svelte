<script lang="ts">
  import { onScreenTwo, showScreen } from './lib/screens';
  import { view } from './lib/view.svelte';
  import Header from './screens/Header.svelte';
  import Screen1 from './screens/Screen1.svelte';
  import Screen2 from './screens/Screen2.svelte';
  import Settings from './screens/Settings.svelte';

  let mode = $state<'dashboard' | 'settings'>('dashboard');

  $effect(() => view.start());

  const toggleSettings = () => (mode = mode === 'settings' ? 'dashboard' : 'settings');

  function typing(target: EventTarget | null): boolean {
    return (
      target instanceof HTMLElement && target.matches('input, textarea, select, [contenteditable]')
    );
  }

  function onkeydown(event: KeyboardEvent) {
    if (event.key === 'Escape' && mode === 'settings') mode = 'dashboard';
    if (
      mode !== 'dashboard' ||
      typing(event.target) ||
      event.altKey ||
      event.ctrlKey ||
      event.metaKey
    )
      return;
    const down = event.key === 'ArrowDown' && !onScreenTwo();
    const up = event.key === 'ArrowUp' && onScreenTwo();
    if (down || up) {
      event.preventDefault();
      showScreen(down ? 'two' : 'one');
    }
  }
</script>

<svelte:window {onkeydown} />

<div class="screen">
  <Header settingsOpen={mode === 'settings'} onsettings={toggleSettings} />
  {#if mode === 'settings'}
    <Settings onback={() => (mode = 'dashboard')} />
  {:else}
    <Screen1 />
  {/if}
</div>
{#if mode === 'dashboard'}
  <Screen2 />
{/if}

<style>
  .screen {
    display: flex;
    flex-direction: column;
    height: 100dvh;
  }
</style>
