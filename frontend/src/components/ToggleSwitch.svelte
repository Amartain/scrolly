<!-- An on/off switch: its emoji, its words, then a track with a knob (left off, right and gold on). The native
     checkbox stays for keyboard and screen readers. The knob jumps; only its colours ease. -->
<script lang="ts">
  let {
    label,
    emoji,
    checked,
    onchange,
  }: {
    label: string;
    emoji: string;
    checked: boolean;
    onchange: (checked: boolean) => void;
  } = $props();
</script>

<label class="switch">
  <span class="emoji" aria-hidden="true">{emoji}</span>
  <span class="word display">{label}</span>
  <input
    type="checkbox"
    role="switch"
    {checked}
    onchange={(event) => onchange(event.currentTarget.checked)}
  />
  <span class="track" aria-hidden="true"><span class="knob"></span></span>
</label>

<style>
  .switch {
    position: relative;
    display: grid;
    grid-template-columns: auto minmax(0, 1fr) auto;
    align-items: center;
    gap: var(--space-3);
    padding: var(--space-2) var(--space-3);
    cursor: pointer;
  }

  .emoji {
    font-size: var(--text-display-md);
    line-height: 1;
  }

  .word {
    font-size: var(--text-display-sm);
  }

  input {
    position: absolute;
    inset: 0;
    opacity: 0;
    margin: 0;
    cursor: inherit;
  }

  .track {
    display: flex;
    width: calc(var(--size-glyph-button) * 2);
    height: var(--size-glyph-button);
    padding: var(--space-1);
    background: var(--inset);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-sunken);
    transition: background-color 150ms;
  }

  .knob {
    aspect-ratio: 1;
    height: 100%;
    background: var(--btn);
    background-image: var(--gloss-btn);
    border: var(--border-width) solid var(--line);
    transition: background-color 150ms;
  }

  .switch:has(input:checked) .track {
    justify-content: flex-end;
    background: var(--strong);
  }

  .switch:has(input:checked) .knob {
    background-color: var(--gold);
  }

  .switch:has(input:focus-visible) .track {
    outline: var(--border-width) solid var(--gold);
    outline-offset: var(--space-1);
  }

  @media (prefers-reduced-motion: reduce) {
    .track,
    .knob {
      transition: none;
    }
  }
</style>
