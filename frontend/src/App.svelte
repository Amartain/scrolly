<script lang="ts">
  import { typing } from './lib/keys';
  import { peak } from './lib/peak.svelte';
  import { travel, wayDown, wayUp } from './lib/travel';
  import { focusScribe, onScreenTwo, showScreen } from './lib/screens';
  import { seclusion } from './lib/seclusion.svelte';
  import { view } from './lib/view.svelte';
  import Header from './screens/Header.svelte';
  import ArchivesPage from './screens/archives/ArchivesPage.svelte';
  import ScrapsPage from './screens/scraps/ScrapsPage.svelte';
  import Seclusion from './screens/seclusion/Seclusion.svelte';
  import Phase1 from './screens/Phase1.svelte';
  import Phase2 from './screens/Phase2.svelte';
  import Phase3 from './screens/Phase3.svelte';
  import Screen1 from './screens/Screen1.svelte';
  import Screen2 from './screens/Screen2.svelte';
  import Flourish from './components/Flourish.svelte';
  import MilestoneOverlay from './components/MilestoneOverlay.svelte';
  import GhostCard from './components/GhostCard.svelte';
  import GuidanceScroll from './components/GuidanceScroll.svelte';
  import QiCard from './components/QiCard.svelte';
  import PlanningTimer from './components/PlanningTimer.svelte';
  import SunsetAdvisor from './components/SunsetAdvisor.svelte';
  import SunsetPoem from './components/SunsetPoem.svelte';
  import ThemeOrbs from './components/ThemeOrbs.svelte';
  import TribulationOverlay from './components/TribulationOverlay.svelte';
  import Dispatch from './screens/Dispatch.svelte';
  import Settings from './screens/Settings.svelte';
  import ZeroState from './screens/ZeroState.svelte';

  let mode = $state<'dashboard' | 'settings' | 'dispatch' | 'scraps' | 'archives' | 'seclusion'>(
    'dashboard',
  );

  $effect(() => view.start());

  // Seclusion left open (a reload, a crash, a night session) opens again where it was. It asks only
  // after the first view has arrived: two first requests at once would both start the day.
  let seclusionAsked = false;
  $effect(() => {
    if (!view.current || seclusionAsked) return;
    seclusionAsked = true;
    void seclusion.load().then(() => {
      if (!seclusion.state?.active) return;
      peak.arrive('paint');
      mode = 'seclusion';
    });
  });

  // The cultivator of the peak, in the room and in the header: up or down is Python's word (the
  // room's while it is open), and the climb goes on while a timer runs.
  $effect(() => {
    const up = mode === 'seclusion' ? seclusion.state?.on_peak : view.current?.on_peak;
    if (up !== undefined) peak.sync(up);
  });
  $effect(() => {
    const dashboard = view.current?.dashboard.immediate?.timer.running ?? false;
    peak.running = mode === 'seclusion' ? seclusion.running : dashboard;
  });

  /** Up the mountain (↑, F or the moon gate): the scene is painted upward, or opens if seen lately. */
  async function enterSeclusion() {
    if (!(await seclusion.enter())) return;
    const way = wayUp(peak.stage !== 'foot');
    await travel(way, () => {
      peak.arrive(way === 'none' ? 'paint' : way === 'rise' ? 'rise' : 'open');
      mode = 'seclusion';
    });
  }

  /** Stepping out leaves the run going; a scroll held open past 04:00 then rolls over. */
  async function leaveSeclusion() {
    await seclusion.leave();
    await view.refresh();
    await travel(wayDown(), () => (mode = 'dashboard'));
  }

  const status = $derived(view.planning?.status);
  const onboarding = $derived(
    mode === 'dashboard' &&
      (status === 'zero' || status === 'inscribe' || status === 'estimate' || status === 'weigh'),
  );
  const onDashboard = $derived(mode === 'dashboard' && status === 'active');

  const toggleSettings = () => (mode = mode === 'settings' ? 'dashboard' : 'settings');

  function onkeydown(event: KeyboardEvent) {
    const modified = event.altKey || event.ctrlKey || event.metaKey;
    // A key a focused widget already used (a list, the search) is not a way up or down.
    const free = !modified && !typing(event.target) && !event.defaultPrevented;
    if (event.key === 'Escape' && mode === 'seclusion') void leaveSeclusion();
    else if (event.key === 'Escape' && mode !== 'dashboard') mode = 'dashboard';
    else if (event.key === 'ArrowDown' && mode === 'seclusion' && free) {
      event.preventDefault();
      void leaveSeclusion();
    }
    if (!onDashboard || !free) return;
    if (event.key === 'n' || event.key === 'N') {
      event.preventDefault();
      focusScribe();
      return;
    }
    // F, or ↑ from the top of the dashboard: up the mountain to Seclusion.
    const up = event.key === 'ArrowUp' && !onScreenTwo();
    if ((event.key === 'f' || event.key === 'F' || up) && view.current?.dashboard.immediate) {
      event.preventDefault();
      void enterSeclusion();
      return;
    }
    const down = event.key === 'ArrowDown' && !onScreenTwo();
    const back = event.key === 'ArrowUp' && onScreenTwo();
    if (down || back) {
      event.preventDefault();
      showScreen(down ? 'two' : 'one');
    }
  }
</script>

<svelte:window {onkeydown} />

<!-- The header belongs to the dashboard (and sits under the zero-state fog). Planning has none. -->
<div class="screen">
  {#if mode === 'seclusion'}
    <Seclusion onleave={leaveSeclusion} />
  {:else if mode === 'settings'}
    <Header settingsOpen onsettings={toggleSettings} />
    <Settings onback={() => (mode = 'dashboard')} />
  {:else if mode === 'dispatch'}
    <Header settingsOpen={false} onsettings={toggleSettings} />
    <Dispatch onback={() => (mode = 'dashboard')} />
  {:else if mode === 'scraps'}
    <Header settingsOpen={false} onsettings={toggleSettings} />
    <ScrapsPage onback={() => (mode = 'dashboard')} />
  {:else if mode === 'archives'}
    <Header settingsOpen={false} onsettings={toggleSettings} />
    <ArchivesPage onback={() => (mode = 'dashboard')} />
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
    <Screen1 onseclusion={enterSeclusion} />
  {/if}
</div>
<Flourish />
<QiCard />
<TribulationOverlay />
<GhostCard />
<GuidanceScroll />
{#if onDashboard}
  <Screen2
    ondispatch={() => (mode = 'dispatch')}
    onscraps={() => (mode = 'scraps')}
    onarchives={() => (mode = 'archives')}
  />
  <MilestoneOverlay />
  <SunsetAdvisor />
  <SunsetPoem />
{/if}
{#if onboarding}
  <ThemeOrbs />
{/if}
{#if onboarding && status !== 'zero'}
  <PlanningTimer />
{/if}

<style>
  .screen {
    display: flex;
    flex-direction: column;
    height: 100dvh;
  }
</style>
