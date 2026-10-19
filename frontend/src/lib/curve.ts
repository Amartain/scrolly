/**
 * A smooth line through the points that never overshoots (monotone cubic, Fritsch-Carlson), so a
 * rising series stays rising between its points. Drawing only: the series itself comes from Python.
 */
export function monotonePath(points: [number, number][]): string {
  const n = points.length;
  if (n === 0) return '';
  const [x0, y0] = points[0];
  if (n === 1) return `M${x0},${y0}`;

  const dx = points.slice(1).map(([x], i) => x - points[i][0]);
  const slope = points.slice(1).map(([, y], i) => (y - points[i][1]) / dx[i]);
  const tangent = points.map((_, i) => {
    if (i === 0) return slope[0];
    if (i === n - 1) return slope[n - 2];
    return slope[i - 1] * slope[i] <= 0 ? 0 : (slope[i - 1] + slope[i]) / 2;
  });
  for (let i = 0; i < n - 1; i++) {
    if (slope[i] === 0) {
      tangent[i] = 0;
      tangent[i + 1] = 0;
      continue;
    }
    const a = tangent[i] / slope[i];
    const b = tangent[i + 1] / slope[i];
    const size = a * a + b * b;
    if (size > 9) {
      const scale = 3 / Math.sqrt(size);
      tangent[i] = scale * a * slope[i];
      tangent[i + 1] = scale * b * slope[i];
    }
  }

  const round = (value: number) => Math.round(value * 10) / 10;
  let path = `M${round(x0)},${round(y0)}`;
  for (let i = 0; i < n - 1; i++) {
    const [xa, ya] = points[i];
    const [xb, yb] = points[i + 1];
    const third = dx[i] / 3;
    const c1 = `${round(xa + third)},${round(ya + tangent[i] * third)}`;
    const c2 = `${round(xb - third)},${round(yb - tangent[i + 1] * third)}`;
    path += ` C${c1} ${c2} ${round(xb)},${round(yb)}`;
  }
  return path;
}
