// Pure JS Random Forest inference — exact same results as predict_cli.py
// No native modules, no network, fully offline.
// Model version: 2026-03-30-20:05

const RIPENESS_MAP: Record<number, string> = {
  0: 'Unripe',
  1: 'Near Ripe',
  2: 'Ripe',
  3: 'Very Ripe',
  4: 'Overripe',
  5: 'Molds',
  6: 'Rotten',
};

export type PredictionResult = {
  shelf_life_hours: number;
  shelf_life_days: number;
  ripeness_label: string;
  ripeness_class: number;
  note: string;
};

export const defaultPrediction: PredictionResult = {
  shelf_life_hours: 0,
  shelf_life_days: 0,
  ripeness_label: '—',
  ripeness_class: -1,
  note: 'Connect sensor to get prediction.',
};

// Node format: [feature, threshold, left, right] for internal, [value] for leaf
type RegNode = [number, number, number, number] | [number];
type ClsNode = [number, number, number, number] | [number];

let regTrees: RegNode[][] | null = null;
let clsTrees: ClsNode[][] | null = null;
let clsClasses: number[] | null = null;

function loadModels() {
  if (!regTrees) {
    regTrees = require('../assets/reg_trees_compact.json') as RegNode[][];
    console.log('[ML] Loaded regression trees:', regTrees.length, 'trees');
    console.log('[ML] First reg tree has', regTrees[0].length, 'nodes');
    console.log('[ML] First reg tree root:', JSON.stringify(regTrees[0][0]));
  }
  if (!clsTrees) {
    const clsData = require('../assets/cls_trees_compact.json') as { t: ClsNode[][]; c: number[] };
    clsTrees = clsData.t;
    clsClasses = clsData.c;
    console.log('[ML] Loaded classification trees:', clsTrees.length, 'trees');
    console.log('[ML] Classes:', clsClasses);
    console.log('[ML] First cls tree has', clsTrees[0].length, 'nodes');
    console.log('[ML] First cls tree root:', JSON.stringify(clsTrees[0][0]));
  }
}

function predictReg(features: number[]): number {
  let sum = 0;
  for (const tree of regTrees!) {
    let node = tree.length - 1; // root is the last node (post-order traversal)
    while (tree[node].length === 4) {
      const [feat, thr, left, right] = tree[node] as [number, number, number, number];
      node = features[feat] <= thr ? left : right;
    }
    sum += (tree[node] as [number])[0];
  }
  return sum / regTrees!.length;
}

function predictCls(features: number[]): number {
  const votes: Record<number, number> = {};
  for (const tree of clsTrees!) {
    let node = tree.length - 1; // root is the last node (post-order traversal)
    while (tree[node].length === 4) {
      const [feat, thr, left, right] = tree[node] as [number, number, number, number];
      node = features[feat] <= thr ? left : right;
    }
    const cls = (tree[node] as [number])[0];
    votes[cls] = (votes[cls] ?? 0) + 1;
  }
  // Return class with most votes
  console.log('[ML] Votes:', JSON.stringify(votes));
  const winnerClass = Number(Object.entries(votes).sort((a, b) => b[1] - a[1])[0][0]);
  console.log('[ML] Winner class:', winnerClass);
  return winnerClass;
}

export async function fetchPrediction(
  temperature: string,
  humidity: string,
  pressure: string,
  gasResistance: string,
  co2: string
): Promise<PredictionResult> {
  loadModels();

  // Feature order: gas_resistance, co2, temperature, humidity, pressure
  const features = [
    parseFloat(gasResistance),
    parseFloat(co2),
    parseFloat(temperature),
    parseFloat(humidity),
    parseFloat(pressure),
  ];

  console.log('[ML] Input features:', features);

  const ripeness_class = predictCls(features);
  const ripeness_label = RIPENESS_MAP[ripeness_class] ?? 'Unknown';

  console.log('[ML] Classification result:', ripeness_class, ripeness_label);

  // Clamp shelf life based on ripeness: overripe/molds/rotten = 0 remaining
  const rawHours = predictReg(features);
  console.log('[ML] Raw regression hours:', rawHours);
  
  const shelf_life_hours = ripeness_class >= 4 ? 0 : Math.max(0, rawHours);
  const shelf_life_days = shelf_life_hours / 24;

  let note: string;
  if (shelf_life_days <= 0) {
    note = 'Consume immediately or discard.';
  } else if (shelf_life_days < 1) {
    note = `Will last about ${Math.round(shelf_life_hours)} more hours.`;
  } else if (shelf_life_days < 2) {
    note = 'Will be at peak ripeness within 1 day.';
  } else {
    note = `Estimated ${shelf_life_days.toFixed(1)} days of shelf life remaining.`;
  }

  return {
    shelf_life_hours: Math.round(shelf_life_hours * 10) / 10,
    shelf_life_days: Math.round(shelf_life_days * 100) / 100,
    ripeness_label,
    ripeness_class,
    note,
  };
}
