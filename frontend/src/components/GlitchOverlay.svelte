<!-- Day 100: the scroll glitches into a system window. The one place neon and long motion are allowed
     (features.md). Under reduced motion it is a plain fade. Both Yes buttons, Esc and the backdrop close it. -->
<script lang="ts">
  import { GLITCH } from '../lib/copy-glitch';
  import { REWARD } from '../lib/copy-player';

  let {
    cycles,
    quote,
    attribution,
    onaccept,
    onclose,
  }: {
    cycles: number;
    quote: string;
    attribution: string | null;
    /** [ Yes ]: the user is a player. True when the System's reward is due (the first time). */
    onaccept: () => Promise<boolean>;
    onclose: () => void;
  } = $props();

  let dialog = $state<HTMLDialogElement>();
  let rewarded = $state(false);

  async function accept() {
    if (await onaccept()) rewarded = true;
    else onclose();
  }

  $effect(() => {
    const opener = document.activeElement;
    dialog?.showModal();
    return () => {
      dialog?.close();
      if (opener instanceof HTMLElement) opener.focus();
    };
  });
</script>

<dialog
  bind:this={dialog}
  aria-label={GLITCH.window}
  onkeydown={(event) => {
    if (event.key !== 'Escape') return;
    event.preventDefault();
    event.stopPropagation();
    onclose();
  }}
  oncancel={(event) => {
    event.preventDefault();
    onclose();
  }}
  onclick={(event) => {
    if (event.target === dialog) onclose();
  }}
>
  {#if rewarded}
    <!-- The System rewards the accepted quest (owner, 2026-10-23), in the same window. -->
    <div class="window" role="group" aria-label={REWARD.header}>
      <p class="head display"><span class="dot" aria-hidden="true"></span>{REWARD.header}</p>
      <p class="distortion display">{REWARD.quest}</p>
      <p class="prompt">{REWARD.granted}</p>
      {#each REWARD.items as item (item)}<p class="arise display">{item}</p>{/each}
      <p class="prompt">{REWARD.hint}</p>
      <button class="yes display" type="button" onclick={onclose}>{REWARD.confirm}</button>
    </div>
  {:else}
    <div class="window">
      <p class="head display"><span class="dot" aria-hidden="true"></span>{GLITCH.header}</p>
      <p class="count display">{cycles}</p>
      <p class="distortion display">{GLITCH.distortion}</p>
      <p class="arise display">{quote}</p>
      {#if attribution}<p class="by">— {attribution}</p>{/if}
      <p class="prompt">{GLITCH.prompt}</p>
      <div class="choices">
        <button class="yes display" type="button" onclick={accept}>{GLITCH.yes}</button>
        <button class="yes display" type="button" onclick={accept}>{GLITCH.yes}</button>
      </div>
    </div>
  {/if}
</dialog>

<style>
  dialog {
    padding: 0;
    border: 0;
    background: transparent;
    color: var(--glitch-ink);
    overflow: visible;
  }

  dialog::backdrop {
    background: color-mix(in srgb, var(--glitch-bg) 88%, transparent);
  }

  .window {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--space-3);
    width: min(var(--size-glitch), 90vw);
    padding: var(--space-8);
    background: linear-gradient(160deg, var(--glitch-bg), var(--glitch-bg-raised));
    border: var(--space-1) solid var(--glitch-line);
    box-shadow: var(--glitch-glow);
    text-align: center;
    animation: glitch-in var(--glitch-run) steps(1, end) both;
  }

  p {
    margin: 0;
  }

  .head {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    color: var(--glitch-line);
    font-size: var(--text-display-sm);
    letter-spacing: 0.1em;
  }

  .dot {
    width: var(--space-3);
    height: var(--space-3);
    background: var(--glitch-line);
    border-radius: 50%;
    box-shadow: var(--glitch-text-glow);
    animation: glitch-pulse 1.6s ease-in-out infinite;
  }

  .count {
    color: var(--glitch-line);
    font-size: var(--text-glitch-numeral);
    line-height: 1;
    text-shadow: var(--glitch-text-glow);
    animation: glitch-split var(--glitch-run) steps(1, end) both;
  }

  .distortion {
    color: var(--glitch-ink-muted);
    font-size: var(--text-display-sm);
  }

  .arise {
    font-size: var(--text-display-lg);
    text-shadow: var(--glitch-text-glow);
  }

  .by {
    color: var(--glitch-ink-muted);
    font-size: var(--text-body-sm);
  }

  .prompt {
    max-width: 26rem;
    color: var(--glitch-ink-muted);
    font-size: var(--text-body-md);
  }

  .choices {
    display: flex;
    gap: var(--space-4);
    margin-top: var(--space-3);
  }

  .yes {
    padding: var(--space-2) var(--space-6);
    background: var(--glitch-bg);
    color: var(--glitch-line);
    border: var(--space-1) solid var(--glitch-line);
    font-size: var(--text-display-md);
    cursor: pointer;
  }

  .yes:hover,
  .yes:focus-visible {
    background: var(--glitch-line);
    color: var(--glitch-bg);
  }

  /* The keyframes are in styles/glitch.css. */
  @media (prefers-reduced-motion: reduce) {
    .window {
      animation: glitch-fade var(--glitch-fade) linear both;
    }

    .count,
    .dot {
      animation: none;
    }
  }
</style>
