import { app } from "../../scripts/app.js";

const NODE_TYPE = "CharacterDNAClothingSceneComposer";
const LEGACY_WIDGETS = new Set(["clothing", "scene", "服装", "场景"]);

function hideLegacyWidget(widget) {
  if (!widget || widget.__characterDnaLegacyHidden) return;
  widget.__characterDnaLegacyHidden = true;
  widget.__characterDnaOriginalType = widget.type;
  widget.type = "converted-widget";
  widget.computeSize = () => [0, -4];
}

function install(node) {
  if (node.__characterDnaVisualBlueprintInstalled) return;
  for (const widget of node.widgets ?? []) {
    if (LEGACY_WIDGETS.has(String(widget.name ?? ""))) hideLegacyWidget(widget);
  }
  node.__characterDnaVisualBlueprintInstalled = true;
  requestAnimationFrame(() => {
    node.setSize?.([Math.max(node.size?.[0] ?? 320, 320), Math.max(150, node.computeSize?.()[1] ?? 150)]);
    node.graph?.setDirtyCanvas?.(true, true);
  });
}

app.registerExtension({
  name: "CharacterDNA.VisualBlueprintCompatibility",
  nodeCreated(node) {
    if (node.comfyClass === NODE_TYPE || node.type === NODE_TYPE) install(node);
  },
  loadedGraphNode(node) {
    if (node.comfyClass === NODE_TYPE || node.type === NODE_TYPE) install(node);
  },
});
