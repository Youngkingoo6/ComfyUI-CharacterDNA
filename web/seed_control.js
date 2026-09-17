import { app } from "../../scripts/app.js";

const NODE_TYPE = "CharacterDNASeedGenerator";
const CONTROL_NAMES = new Set([
  "control_after_generate",
  "control before generate",
  "control after generate",
  "生成后控制",
  "生成前控制",
]);
const SAFE_INTEGER_MAX = 1125899906842624;

function findWidgets(node) {
  const widgets = node.widgets ?? [];
  const seed = widgets.find((widget) => widget.name === "seed");
  const control = widgets.find((widget) =>
    CONTROL_NAMES.has(String(widget.name ?? "").toLowerCase()),
  );
  return { seed, control };
}

function nextSeed(seed, mode) {
  const current = Number(seed.value);
  if (!Number.isFinite(current) || mode === "fixed") return undefined;

  const minimum = Math.max(0, Number(seed.options?.min ?? 0));
  const maximum = Math.min(
    SAFE_INTEGER_MAX,
    Number(seed.options?.max ?? SAFE_INTEGER_MAX),
  );
  const step = Math.max(1, Number(seed.options?.step2 ?? 1));

  if (mode === "increment" || mode === "increment-wrap") {
    return Math.min(maximum, current + step);
  }
  if (mode === "decrement") {
    return Math.max(minimum, current - step);
  }
  if (mode === "randomize") {
    const steps = Math.floor((maximum - minimum) / step);
    return minimum + Math.floor(Math.random() * (steps + 1)) * step;
  }
  return undefined;
}

function installFallback(node) {
  const { seed, control } = findWidgets(node);
  if (!seed || !control || control.__characterDnaSeedFix) return;

  // Old saved nodes may not retain the relationship between the seed and its
  // secondary control widget. Restoring it also lets ComfyUI's native handler
  // work again without replacing normal frontend behaviour.
  const linked = Array.isArray(seed.linkedWidgets) ? seed.linkedWidgets : [];
  if (!linked.includes(control)) seed.linkedWidgets = [...linked, control];

  const nativeAfterQueued = control.afterQueued?.bind(control);
  control.afterQueued = (options = {}) => {
    const previous = seed.value;
    nativeAfterQueued?.(options);

    // ComfyUI intentionally disables automatic controls during partial runs.
    // Keep that contract so unrelated partial executions do not change DNA.
    if (options.isPartialExecution || seed.value !== previous) return;

    const next = nextSeed(seed, control.value);
    if (next === undefined || next === previous) return;
    seed.value = next;
    seed.callback?.(next);
    node.graph?.setDirtyCanvas?.(true, true);
  };
  control.__characterDnaSeedFix = true;
}

app.registerExtension({
  name: "CharacterDNA.SeedControlCompatibility",
  nodeCreated(node) {
    if (node.comfyClass === NODE_TYPE || node.type === NODE_TYPE) {
      installFallback(node);
    }
  },
  loadedGraphNode(node) {
    if (node.comfyClass === NODE_TYPE || node.type === NODE_TYPE) {
      installFallback(node);
    }
  },
});
