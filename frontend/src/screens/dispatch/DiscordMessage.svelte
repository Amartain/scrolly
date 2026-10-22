<!-- The Dispatch as one Discord message: an avatar, the author and the time, then the scroll rendered
     (lib/discord-preview.ts). Only a picture of what will be posted; the text is copied unchanged. -->
<script lang="ts">
  import { DISPATCH_PREVIEW } from '../../lib/copy-dispatch';
  import { preview } from '../../lib/discord-preview';
  import { view } from '../../lib/view.svelte';

  let { text }: { text: string } = $props();

  const lines = $derived(preview(text, view.current?.legend));
  const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
</script>

<article class="message" aria-label={DISPATCH_PREVIEW.label}>
  <span class="avatar" aria-hidden="true">📜</span>
  <div class="content">
    <p class="meta"><span class="author">{DISPATCH_PREVIEW.author}</span> <span>{time}</span></p>
    {#each lines as line, i (i)}
      {#if line.kind === 'h1'}
        <h2 class="h1">{line.parts[0].text}</h2>
      {:else if line.kind === 'h2'}
        <h3 class="h2">{line.parts[0].text}</h3>
      {:else if line.kind === 'blank'}
        <p class="blank"></p>
      {:else}
        <p class="line">
          {#each line.parts as part, j (j)}<span class:strong={part.strong} class:muted={part.muted}
              >{part.text}</span
            >{/each}
        </p>
      {/if}
    {/each}
  </div>
</article>

<style>
  .message {
    display: flex;
    gap: var(--space-4);
    padding: var(--space-5) var(--space-6);
    background: var(--discord-bg);
    color: var(--discord-text);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-panel);
    font-family: var(--font-read);
    font-size: var(--text-read-md);
    line-height: 1.4;
  }

  .avatar {
    flex: none;
    display: grid;
    place-items: center;
    width: var(--size-icon-button);
    height: var(--size-icon-button);
    border-radius: 50%;
    background: var(--discord-avatar);
    font-size: var(--size-icon);
  }

  .content {
    flex: 1;
    min-width: 0;
  }

  p,
  h2,
  h3 {
    margin: 0;
    overflow-wrap: anywhere;
  }

  .meta {
    margin-bottom: var(--space-1);
    color: var(--discord-muted);
    font-size: var(--text-read-sm);
  }

  .author {
    color: var(--discord-heading);
    font-weight: 700;
  }

  .h1,
  .h2 {
    color: var(--discord-heading);
    font-weight: 700;
  }

  .h1 {
    margin-block: var(--space-2);
    font-size: var(--text-read-lg);
  }

  .h2 {
    margin-top: var(--space-3);
    font-size: var(--text-read-md);
  }

  .blank {
    height: var(--space-3);
  }

  .strong {
    color: var(--discord-heading);
    font-weight: 700;
  }

  .muted {
    color: var(--discord-muted);
  }
</style>
