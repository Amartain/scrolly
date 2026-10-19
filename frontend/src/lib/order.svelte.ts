import type { View } from './api';
import { view } from './view.svelte';

/** A list the user can reorder: the new order shows at once, then the server's answer replaces it. */
export function useOrder<T extends { id: string }>(
  items: () => T[],
  save: (ids: string[]) => Promise<View>,
) {
  let pending = $state<string[] | null>(null);
  return {
    get shown(): T[] {
      const all = items();
      return pending ? pending.flatMap((id) => all.filter((item) => item.id === id)) : all;
    },
    async reorder(ids: string[]) {
      pending = ids;
      await view.act(() => save(ids));
      pending = null;
    },
  };
}
