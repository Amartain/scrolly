<!-- The finished-day ceremony, when it is owed: the day's last trial was conquered (features.md). It waits
     for the Qi card and does not come back until another trial is conquered. A secret seal can also
     ask to see it once (`view.preview`); closing that changes nothing. -->
<script lang="ts">
  import { qiAsk } from '../lib/qi-ask.svelte';
  import { victorySeen } from '../lib/victory-api';
  import { view } from '../lib/view.svelte';
  import Ceremony from './ceremony/Ceremony.svelte';

  const victory = $derived(view.current?.dashboard.victory);
  const owed = $derived(victory?.due && !qiAsk.question ? victory : null);
  const shown = $derived(owed ?? view.preview);

  function close() {
    if (owed) void view.act(victorySeen);
    else view.preview = null;
  }
</script>

<!-- No key on `shown`: the minute's refresh brings a new object, and the scene must not start over. -->
{#if shown}
  <Ceremony victory={shown} onclose={close} />
{/if}
