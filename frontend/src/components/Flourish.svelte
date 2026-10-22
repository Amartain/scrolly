<!-- The layer of flourishes (lib/flourish.svelte.ts): a lit-incense ring with sparks, a conquest seal
     and a spark flying to Conquered Today. Fixed over the page, it moves nothing and catches no click.
     The keyframes are in styles/flourish.css. -->
<script lang="ts">
  import { flourish } from '../lib/flourish.svelte';

  const SPARKS = [-1, 0, 1];
</script>

<div class="layer" aria-hidden="true">
  {#each flourish.effects as effect (effect.id)}
    {#if effect.kind === 'ignite'}
      <div class="at" data-flourish={effect.kind} style:--x={effect.x} style:--y={effect.y}>
        <span class="ring"></span>
        {#each SPARKS as side (side)}
          <span class="spark" style:--side={side}></span>
        {/each}
      </div>
    {:else if effect.kind === 'seal'}
      <div class="at" data-flourish={effect.kind} style:--x={effect.x} style:--y={effect.y}>
        <span class="seal read" lang="zh">勝</span>
      </div>
    {:else if effect.kind === 'comet'}
      <div class="at" data-flourish={effect.kind} style:--x={effect.x} style:--y={effect.y}>
        <span class="comet" style:--dx={effect.dx} style:--dy={effect.dy}></span>
      </div>
    {/if}
  {/each}
</div>

<style>
  .layer {
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 1;
  }

  .at {
    position: absolute;
    left: var(--x);
    top: var(--y);
    width: 0;
    height: 0;
  }

  .ring,
  .spark,
  .seal,
  .comet {
    position: absolute;
    translate: -50% -50%;
  }

  .ring {
    width: var(--size-icon-button);
    height: var(--size-icon-button);
    border: var(--space-1) solid var(--scene-gold);
    border-radius: 50%;
    box-shadow: var(--scene-glow);
    animation: flourish-ring 600ms ease-out both;
  }

  .spark {
    width: var(--space-3);
    height: var(--space-3);
    background: var(--scene-bolt);
    border: var(--border-width) solid var(--scene-gold-deep);
    rotate: 45deg;
    animation: flourish-spark 700ms calc(60ms * (var(--side) + 1)) ease-out both;
  }

  .seal {
    display: grid;
    place-items: center;
    width: 2.2em;
    height: 2.2em;
    background: var(--scene-gold);
    color: var(--scene-ink);
    border: var(--border-width) solid var(--scene-ink);
    box-shadow: var(--shadow-button);
    font-size: var(--text-display-xl);
    animation: flourish-seal 900ms ease-out both;
  }

  .comet {
    width: var(--space-4);
    height: var(--space-4);
    background: var(--scene-bolt);
    border-radius: 50%;
    box-shadow: var(--scene-glow-strong);
    animation: flourish-comet 650ms 150ms ease-in both;
  }
</style>
