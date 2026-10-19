import type { ChartSeries, Metric } from './api';

/** Which series both charts show. One choice for the two, so they always agree. */
class ChartChoice {
  metric = $state<Metric>('trials');

  /** The chosen series, or the first one if that metric is no longer offered (Qi switched off). */
  pick(charts: ChartSeries[]): ChartSeries | undefined {
    return charts.find((series) => series.metric === this.metric) ?? charts[0];
  }
}

export const chartChoice = new ChartChoice();
