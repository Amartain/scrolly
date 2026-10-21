/** DRAFT, proposed 2026-10-21: asked when a timer was running while the app was away. */
export const GHOST = {
  title: 'Welcome back',
  away: (left: string, gap: string) =>
    `You were last here at ${left}, ${gap} ago, with a timer running.`,
  question: 'Did that time count?',
  keep: 'Keep all of it',
  cut: 'Count only until I left',
};
