<!-- A small Qi number the user can correct. The server checks it; a refusal puts the old value back. -->
<script lang="ts">
  let {
    value,
    label,
    restores = false,
    onsave,
  }: {
    value: string;
    label: string;
    restores?: boolean;
    onsave: (text: string) => Promise<boolean>;
  } = $props();

  async function commit(event: Event) {
    const input = event.currentTarget as HTMLInputElement;
    if (input.value.trim() === value) return;
    if (!(await onsave(input.value))) input.value = value;
  }
</script>

<span class="sign" aria-hidden="true">{restores ? '+' : ''}</span>
<input
  class="qi digits"
  {value}
  placeholder="0"
  inputmode="numeric"
  aria-label={label}
  onchange={commit}
/>

<style>
  .sign {
    flex: none;
    width: var(--space-3);
    text-align: right;
  }

  .qi {
    flex: none;
    width: var(--size-qi-field);
    height: var(--size-glyph-button);
    padding-inline: var(--space-2);
    background: var(--surface-raised);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-sunken);
    font-size: var(--text-body-md);
    text-align: right;
  }
</style>
