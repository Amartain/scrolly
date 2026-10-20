<script lang="ts">
  import { typing } from './lib/keys';
  import { focusScribe, onScreenTwo, showScreen } from './lib/screens';
  import { view } from './lib/view.svelte';
  import Header from './screens/Header.svelte';
  import Phase1 from './screens/Phase1.svelte';
  import Phase2 from './screens/Phase2.svelte';
  import Phase3 from './screens/Phase3.svelte';
  import Screen1 from './screens/Screen1.svelte';
  import Screen2 from './screens/Screen2.svelte';
  import MilestoneOverlay from './components/MilestoneOverlay.svelte';
  import SunsetAdvisor from './components/SunsetAdvisor.svelte';
  import ThemeOrbs from './components/ThemeOrbs.svelte';
  import Settings from './screens/Settings.svelte';
  import ZeroState from './screens/ZeroState.svelte';

  let mode = $state<'dashboard' | 'settings'>('dashboard');

  $effect(() => view.start());

  const status = $derived(view.planning?.status);
  const onboarding = $derived(
    mode === 'dashboard' &&
      (status === 'zero' || status === 'inscribe' || status === 'estimate' || status === 'weigh'),
  );
  const onDashboard = $derived(mode === 'dashboard' && status === 'active');

  const toggleSettings = () => (mode = mode === 'settings' ? 'dashboard' : 'settings');

  function onkeydown(event: KeyboardEvent) {
    if (event.key === 'Escape' && mode === 'settings') mode = 'dashboard';
    if (!onDashboard || typing(event.target) || event.altKey || event.ctrlKey || event.metaKey)
      return;
    if (event.key === 'n' || event.key === 'N') {
      event.preventDefault();
      focusScribe();
      return;
    }
    const down = event.key === 'ArrowDown' && !onScreenTwo();
    const up = event.key === 'ArrowUp' && onScreenTwo();
    if (down || up) {
      event.preventDefault();
      showScreen(down ? 'two' : 'one');
    }
  }
</script>

<svelte:window {onkeydown} />

<!-- The header belongs to the dashboard (and sits under the zero-state fog). Planning has none. -->
<div class="screen">
  {#if mode === 'settings'}
    <Header settingsOpen onsettings={toggleSettings} />
    <Settings onback={() => (mode = 'dashboard')} />
  {:else if status === 'zero'}
    <ZeroState />
  {:else if status === 'inscribe'}
    <Phase1 />
  {:else if status === 'estimate'}
    <Phase2 />
  {:else if status === 'weigh'}
    <Phase3 />
  {:else if status === 'active'}
    <Header settingsOpen={false} onsettings={toggleSettings} />
    <Screen1 />
  {/if}
</div>
{#if onDashboard}
  <Screen2 />
  <MilestoneOverlay />
  <SunsetAdvisor />
{/if}
{#if onboarding}
  <ThemeOrbs />
{/if}

<style>
  .screen {
    display: flex;
    flex-direction: column;
    height: 100dvh;
  }
</style>
