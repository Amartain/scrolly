/**
 * The desktop notice for the end of the Cycles. The browser asks permission once, when the user first
 * starts a cycle (a click, as browsers require). It only reaches the user while Scrolly is open in a
 * tab; a closed tab has no sound and no notice, but the times are still right when it opens again.
 */
export function askNotifyPermission(): void {
  if (typeof Notification === 'undefined' || Notification.permission !== 'default') return;
  void Notification.requestPermission();
}

export function notify(title: string, body: string): void {
  if (typeof Notification === 'undefined' || Notification.permission !== 'granted') return;
  new Notification(title, { body });
}
