import { putTrialQi } from './qi-api';
import { view } from './view.svelte';

/** What the card needs to ask about a conquest, and how to take that conquest back. */
export interface QiQuestion {
  id: string;
  title: string;
  /** The Qi first estimated: the card opens on it ("As foreseen"). */
  estimate: number;
  /** A Restorative Art: its Qi is what it gave back, and the choices say so. */
  restores: boolean;
  undo: () => Promise<unknown>;
}

/** Right after a conquest, anywhere: "How much qi did this take?" waits here until it is answered. */
class QiAsk {
  question = $state<QiQuestion | null>(null);

  ask = (question: QiQuestion) => {
    this.question = question;
  };

  /** Record what was told. A refusal shows as the notice, and the estimate stays. */
  confirm = async (qi: number) => {
    const question = this.question;
    this.question = null;
    if (question) await view.act(() => putTrialQi(question.id, qi));
  };

  /** Close the card: the estimate stands. */
  keep = () => {
    this.question = null;
  };

  /** The back arrow: take the conquest back. */
  back = async () => {
    const question = this.question;
    this.question = null;
    if (question) await question.undo();
  };
}

export const qiAsk = new QiAsk();
