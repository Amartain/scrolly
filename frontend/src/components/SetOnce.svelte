<!-- An estimate that is written once. Empty: a small field with a check mark. Set: the number, in brackets. -->
<script lang="ts">
  let {
    value,
    label,
    confirm,
    kind,
    restores = false,
    onsave,
  }: {
    value: string;
    label: string;
    /** The name of the check mark, which must not contain `label` (tests and readers tell them apart). */
    confirm: string;
    kind: 'time' | 'qi';
    restores?: boolean;
    onsave: (text: string) => Promise<boolean>;
  } = $props();

  let draft = $state('');

  const shown = $derived(`(${restores ? '+' : ''}${value}${kind === 'qi' ? ' Qi' : ''})`);

  async function commit() {
    if (draft.trim()) await onsave(draft);
  }
</script>

{#if value}
  <span class="figure digits" title={label}>{shown}</span>
{:else}
  <span class="set">
    <input
      class="field digits {kind}"
      bind:value={draft}
      placeholder={kind === 'time' ? '30m' : '5'}
      inputmode={kind === 'qi' ? 'numeric' : 'text'}
      aria-label={label}
      onkeydown={(event) => event.key === 'Enter' && commit()}
    />
    <button class="check" type="button" aria-label={confirm} title={confirm} onclick={commit}>
      ✓
    </button>
  </span>
{/if}

<style>
  .figure {
    flex: none;
    color: var(--ink-muted);
    font-size: var(--text-body-sm);
  }

  .set {
    flex: none;
    display: flex;
    align-items: center;
    gap: var(--space-1);
  }

  .field {
    height: var(--size-glyph-button);
    padding-inline: var(--space-2);
    background: var(--surface-raised);
    border: var(--border-width) solid var(--line);
    box-shadow: var(--shadow-sunken);
    color: var(--ink);
    font-size: var(--text-body-sm);
    text-align: right;
  }

  .time {
    width: var(--size-estimate);
  }

  .qi {
    width: var(--size-qi-field);
  }

  .check {
    padding-block: 0;
    padding-inline: var(--space-1);
    background: none;
    border: 0;
    color: inherit;
    cursor: pointer;
    font-size: var(--text-body-md);
  }
</style>
