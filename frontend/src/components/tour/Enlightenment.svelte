<!-- Enlightenment, 悟道: everything of the tour is learned (owner, 2026-10-23: "something cool when the
     user finds all"). The screen dims, a ring of golden light opens, a lotus blooms, 悟 is stamped, and
     the card says so. Once only: Return to the path keeps it (Python), and from then on the cultivator
     wears gold. A key shows the last frame at once; under reduced motion it is the last frame. -->
<script lang="ts">
  import { onMount } from 'svelte';
  import { playEnlightenment } from '../../lib/chime-ceremony';
  import { KNOWLEDGE } from '../../lib/copy-knowledge';
  import { knowledgeApi } from '../../lib/knowledge.svelte';
  import { view } from '../../lib/view.svelte';

  const WORDS = KNOWLEDGE.enlightenment;
  const PETALS = [0, 45, 90, 135, 180, 225, 270, 315];

  let still = $state(window.matchMedia('(prefers-reduced-motion: reduce)').matches);
  let button: HTMLButtonElement;

  onMount(() => {
    playEnlightenment();
    button.focus({ preventScroll: true });
  });

  const close = () => view.act(knowledgeApi.enlightened);
</script>

<svelte:window onkeydowncapture={() => (still = true)} />

<div class="enlightenment" class:still role="dialog" aria-modal="true" aria-label={WORDS.title}>
  <div class="light" aria-hidden="true"></div>
  <svg class="lotus" viewBox="0 0 200 200" aria-hidden="true">
    {#each PETALS as angle, i (angle)}
      <g transform="translate(100 100) rotate({angle})">
        <path class="petal" style:--i={i} d="M0,0 C-20,-28 -16,-62 0,-84 C16,-62 20,-28 0,0 Z" />
      </g>
    {/each}
    <circle class="heart" cx="100" cy="100" r="16" />
  </svg>
  <div class="card">
    <span class="seal display" aria-hidden="true">悟</span>
    <h2 class="title display">{WORDS.title}</h2>
    <p class="line">{WORDS.line}</p>
    <p class="reward">{WORDS.reward}</p>
    <button bind:this={button} class="close display" type="button" onclick={close}
      >{WORDS.close}</button
    >
  </div>
</div>
