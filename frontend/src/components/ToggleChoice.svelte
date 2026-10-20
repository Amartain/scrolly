<!-- A pressed-in checkbox button, as in Settings. The native input stays for keyboard and screen readers. -->
<script lang="ts">
  let {
    label,
    checked,
    onchange,
  }: { label: string; checked: boolean; onchange: (checked: boolean) => void } = $props();
</script>

<label class="choice display">
  <input type="checkbox" {checked} onchange={(event) => onchange(event.currentTarget.checked)} />
  {label}
</label>

<style>
  .choice {
    position: relative;
    flex: none;
    padding: var(--space-3) var(--space-5);
    cursor: pointer;
    background: var(--btn);
    background-image: var(--gloss-btn);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-button);
    font-size: var(--text-display-sm);
  }

  .choice input {
    position: absolute;
    opacity: 0;
    inset: 0;
    margin: 0;
    cursor: inherit;
  }

  .choice:has(input:checked) {
    background: var(--strong);
    color: var(--on-strong);
    box-shadow: none;
    transform: translate(var(--shadow-offset), var(--shadow-offset));
  }

  .choice:has(input:focus-visible) {
    outline: var(--border-width) solid var(--gold);
    outline-offset: var(--space-1);
  }
</style>
