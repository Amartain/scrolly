/** True while the user is typing, so a shortcut must stay out of the way. */
export function typing(target: EventTarget | null): boolean {
  return (
    target instanceof HTMLElement && target.matches('input, textarea, select, [contenteditable]')
  );
}

/** True when the key press would already activate the focused control (Space or Enter on a button). */
export function onControl(target: EventTarget | null): boolean {
  return target instanceof HTMLElement && target.matches('button, a, [role="button"], summary');
}
