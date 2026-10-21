/**
 * Ctrl+X (or Cmd+X) with nothing selected cuts the whole line, as in VS Code. The action only selects
 * the line; the browser's own cut then does the rest, so the clipboard, the `input` event and Ctrl+Z
 * all behave as they always do. With a selection it does nothing.
 *
 * The last line has no newline after it, so the newline before it goes too: cutting line after line
 * from the bottom then never leaves a blank line behind.
 */
export function cutLine(node: HTMLTextAreaElement) {
  function onkeydown(event: KeyboardEvent) {
    const cut = (event.ctrlKey || event.metaKey) && !event.altKey && !event.shiftKey;
    if (!cut || event.key.toLowerCase() !== 'x' || node.selectionStart !== node.selectionEnd)
      return;
    const text = node.value;
    const caret = node.selectionStart;
    const start = caret === 0 ? 0 : text.lastIndexOf('\n', caret - 1) + 1;
    const newline = text.indexOf('\n', caret);
    const end = newline === -1 ? text.length : newline + 1;
    node.setSelectionRange(newline === -1 && start > 0 ? start - 1 : start, end);
  }

  node.addEventListener('keydown', onkeydown);
  return { destroy: () => node.removeEventListener('keydown', onkeydown) };
}
