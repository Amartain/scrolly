import type { GuideKey } from './copy-guidance';

/** Which `?` scroll is open, if any. One scroll at a time, drawn once by the app shell. */
class Guidance {
  topic = $state<GuideKey | null>(null);

  open = (topic: GuideKey) => {
    this.topic = topic;
  };

  close = () => {
    this.topic = null;
  };
}

export const guidance = new Guidance();
