import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

const API_PATH = "/character-dna/vocabulary";
const TAB_ID = "character-dna-vocabulary";
const FEATURE_GROUPS = {
  face: ["face_length", "face_width", "cheekbone_width", "cheekbone_height", "cheekbone_projection", "jaw_width", "jawline_definition", "chin_width", "chin_length"],
  eyebrows: ["eyebrow_shape", "eyebrow_thickness"],
  eyes: ["eye_elongation", "eye_openness", "eye_spacing", "canthal_tilt", "brow_eye_distance"],
  nose: ["nose_width", "nose_length", "nose_projection", "nose_tip_rotation"],
  mouth: ["mouth_width", "upper_lip_fullness", "lower_lip_fullness", "cupid_bow_definition"],
};
const BODY_FEATURE_GROUPS = {
  frame: ["stature", "shoulder_width", "shoulder_slope", "ribcage_width", "pelvis_width"],
  torso: ["neck_length", "neck_thickness", "torso_length", "chest_fullness", "waist_definition", "hip_fullness"],
  limbs: ["arm_length", "hand_scale", "leg_length", "thigh_length_ratio", "foot_scale"],
  build: ["upper_body_fullness", "lower_body_fullness", "limb_thickness", "muscularity"],
};

const FALLBACK = {
  title: "CharacterDNA Vocabulary", autoApply: "Changes apply after saving", save: "Save", reload: "Reload",
  export: "Export", import: "Import", reset: "Restore defaults", features: "Feature vocabulary",
  profile: "Base templates", searchFeatures: "Search features or phrases…",
  searchPhrases: "Search presets or phrases…", searchProfile: "Search is available in vocabulary tabs",
  loading: "Loading vocabulary…", loaded: "Vocabulary loaded", unsaved: "Unsaved changes",
  discard: "Discard unsaved changes and reload?", saving: "Validating and saving…",
  saved: "Saved. Generation nodes now use the updated vocabulary.", saveFailed: "Save failed: ",
  resetConfirm: "Restore the default vocabulary? Current changes will be overwritten.", resetting: "Restoring defaults…",
  resetDone: "Default vocabulary restored", resetFailed: "Restore failed: ", exported: "Vocabulary exported",
  imported: "Imported into the editor; click Save to apply", importFailed: "Import failed: ", invalidRoot: "JSON root must be an object",
  emptyFeatures: "No matching features", emptyPhrases: "No matching presets", notLoaded: "Vocabulary is not loaded",
  english: "English prompt", chinese: "Chinese prompt", englishLabel: "English name", chineseLabel: "Chinese name", value: "Value", identityTemplate: "Identity template", entryTitle: "Title",
  quality: "Fixed quality phrases", qualityPosition: "Fixed quality position", qualityAtStart: "At prompt start", qualityAtEnd: "At prompt end", face: "Face", eyebrows: "Eyebrows", eyes: "Eyes", nose: "Nose", mouth: "Mouth",
  faceFeatures: "Face Features", bodyFeatures: "Body Features",
  identityAppearances: "Distinctive Appearance Features", addAppearance: "+ Add distinctive feature", newAppearanceTitle: "New distinctive feature title",
  visualBlueprints: "Visual Blueprints", look: "Outfit", performance: "Expression & Pose", scene: "Scene", photography: "Photography",
  addBlueprint: "+ Add blueprint", addPreset: "+ Add preset", addLayer: "+ Add layer", addVariation: "+ Add variation",
  newBlueprintTitle: "New blueprint title", newPresetTitle: "New preset title", deleteEntry: "Delete", blueprintLabel: "Display label", layerStack: "Advanced layer stack", variations: "Seed variations", enabled: "Enabled", layerType: "Layer", preset: "Preset", mergeMode: "Mode",
  negativePrompt: "Negative prompt",
  frame: "Frame", torso: "Torso", limbs: "Limbs", build: "Build",
  requestError: "Request failed",
  confirm: "Confirm", cancel: "Cancel",
};

let messages = FALLBACK;
let featureOptionLabels = { face: {}, body: {} };
const t = (key) => messages[key] ?? FALLBACK[key] ?? key;

function currentLocale() {
  const configured = app.ui?.settings?.getSettingValue?.("Comfy.Locale");
  return String(configured || navigator.language || "en");
}

async function loadMessages() {
  try {
    const response = await api.fetchApi("/i18n");
    const all = await response.json();
    const locale = currentLocale();
    const candidates = [locale, locale.replace("_", "-"), locale.split(/[-_]/)[0], "en"];
    for (const candidate of candidates) {
      const localeKey = Object.keys(all || {}).find(
        (key) => key.toLowerCase() === String(candidate).toLowerCase(),
      );
      if (localeKey && all[localeKey]?.characterDNA) {
        const localeData = all[localeKey];
        messages = { ...FALLBACK, ...localeData.characterDNA };
        featureOptionLabels = {
          face: localeData.nodeDefs?.CharacterDNAParametricDesigner?.inputs?.feature?.options || {},
          body: localeData.nodeDefs?.CharacterDNAParametricBodyDesigner?.inputs?.feature?.options || {},
        };
        return;
      }
    }
  } catch (error) {
    console.warn("[CharacterDNA] Unable to load ComfyUI translations", error);
  }
}

function ensureStyles() {
  if (document.getElementById("character-dna-vocabulary-styles")) return;
  const style = document.createElement("style");
  style.id = "character-dna-vocabulary-styles";
  style.textContent = `
    .character-dna-vocab-icon::before{content:"🧬";font-size:20px}.cdna-vocab{position:relative;height:100%;display:flex;flex-direction:column;color:var(--fg-color,#ddd);background:var(--comfy-menu-bg,#202020);font:13px/1.4 system-ui,sans-serif}.cdna-vocab *{box-sizing:border-box}.cdna-vocab-header{padding:12px;border-bottom:1px solid var(--border-color,#444);display:grid;gap:9px}.cdna-vocab-title{font-size:16px;font-weight:700;display:flex;justify-content:space-between;gap:8px;align-items:center}.cdna-vocab-title small{font-size:11px;font-weight:500;opacity:.65}.cdna-vocab-toolbar,.cdna-vocab-tabs{display:flex;flex-wrap:wrap;gap:6px}.cdna-vocab button{border:1px solid var(--border-color,#555);border-radius:6px;padding:6px 9px;color:inherit;background:var(--comfy-input-bg,#303030);cursor:pointer}.cdna-vocab button:hover{filter:brightness(1.15)}.cdna-vocab button:disabled{opacity:.45;cursor:wait}.cdna-vocab button.primary{background:#2f6fda;color:white;border-color:#4d86e8}.cdna-vocab button.danger{color:#ffb3b3}.cdna-vocab-tabs button.active{background:#6741a5;color:white;border-color:#8d67cb}.cdna-vocab input,.cdna-vocab textarea,.cdna-vocab select{width:100%;border:1px solid var(--border-color,#555);border-radius:5px;padding:6px 7px;color:inherit;background:var(--comfy-input-bg,#292929);font:inherit}.cdna-vocab textarea{min-height:54px;resize:vertical}.cdna-vocab-content{min-height:0;flex:1;overflow:auto;padding:10px}.cdna-vocab-status{min-height:32px;padding:7px 11px;border-top:1px solid var(--border-color,#444);font-size:12px;opacity:.85}.cdna-vocab-status.error{color:#ff8e8e;opacity:1}.cdna-vocab-status.success{color:#8ee5aa;opacity:1}.cdna-vocab-group{margin-bottom:14px}.cdna-vocab-group>h3{position:sticky;top:-10px;z-index:2;margin:0 0 7px;padding:8px 2px 5px;background:var(--comfy-menu-bg,#202020);font-size:13px}.cdna-vocab-card{border:1px solid var(--border-color,#444);border-radius:7px;padding:9px;margin-bottom:8px;background:color-mix(in srgb,var(--comfy-input-bg,#292929) 70%,transparent)}.cdna-vocab-card h4{margin:0 0 8px;font:600 13px/1.3 system-ui,sans-serif;word-break:break-all}.cdna-vocab-key{display:block;margin-top:2px;font:11px/1.3 ui-monospace,monospace;opacity:.55}.cdna-vocab-field{display:grid;gap:4px;margin-bottom:8px}.cdna-vocab-field>label{font-size:11px;opacity:.72}.cdna-vocab-level{display:grid;grid-template-columns:48px 1fr 1fr;gap:6px;align-items:start;margin-bottom:7px}.cdna-vocab-level strong{padding:7px 2px;text-align:center}.cdna-vocab-bilingual{display:grid;grid-template-columns:1fr 1fr;gap:7px}.cdna-vocab-measurement{border-top:1px dashed var(--border-color,#555);margin-top:9px;padding-top:9px;display:grid;grid-template-columns:repeat(3,1fr);gap:6px}.cdna-vocab-measurement h5{grid-column:1/-1;margin:0;font-size:11px;opacity:.8}.cdna-vocab-empty{padding:24px 8px;text-align:center;opacity:.6}.cdna-layer-row{display:grid;grid-template-columns:26px 1fr 1.4fr .8fr auto;gap:5px;align-items:center;margin-bottom:6px}.cdna-layer-actions{display:flex;gap:3px}.cdna-layer-actions button{padding:4px 6px}.cdna-add-button{margin:0 0 9px}.cdna-modal-backdrop{position:absolute;inset:0;z-index:20;display:grid;place-items:center;padding:18px;background:rgba(0,0,0,.66)}.cdna-modal{width:min(420px,100%);border:1px solid var(--border-color,#555);border-radius:9px;padding:14px;background:var(--comfy-menu-bg,#202020);box-shadow:0 18px 50px rgba(0,0,0,.5)}.cdna-modal h3{margin:0 0 12px;font-size:15px}.cdna-modal-actions{display:flex;justify-content:flex-end;gap:7px;margin-top:12px}@media(max-width:700px){.cdna-layer-row{grid-template-columns:26px 1fr}.cdna-layer-row select,.cdna-layer-actions{grid-column:2}.cdna-vocab-level,.cdna-vocab-bilingual,.cdna-vocab-measurement{grid-template-columns:1fr}.cdna-vocab-level strong{text-align:left}}
  `;
  document.head.appendChild(style);
}

function el(tag, props = {}, children = []) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(props)) {
    if (key === "className") node.className = value;
    else if (key === "text") node.textContent = value;
    else if (key.startsWith("on") && typeof value === "function") node.addEventListener(key.slice(2).toLowerCase(), value);
    else if (value !== undefined && value !== null) node[key] = value;
  }
  for (const child of Array.isArray(children) ? children : [children]) if (child) node.appendChild(child);
  return node;
}
const clone = (value) => JSON.parse(JSON.stringify(value));

async function requestVocabulary(path = API_PATH, options = {}) {
  const response = await api.fetchApi(path, options);
  let payload;
  try { payload = await response.json(); } catch { throw new Error(`${t("requestError")} (HTTP ${response.status})`); }
  if (!response.ok || !payload?.ok) throw new Error(payload?.error || `${t("requestError")} (HTTP ${response.status})`);
  return payload.vocabulary;
}

function renderVocabularyPanel(container) {
  const state = { vocabulary: null, activeTab: "profile", search: "", dirty: false };
  const root = el("div", { className: "cdna-vocab" });
  const content = el("div", { className: "cdna-vocab-content" });
  const status = el("div", { className: "cdna-vocab-status", text: t("loading") });
  const search = el("input", { type: "search", placeholder: t("searchFeatures"), oninput: (event) => { state.search = event.target.value.trim().toLowerCase(); renderContent(); } });
  const setStatus = (message, kind = "") => { status.textContent = message; status.className = `cdna-vocab-status${kind ? ` ${kind}` : ""}`; };
  const markDirty = () => { state.dirty = true; setStatus(t("unsaved")); };
  const setBusy = (busy) => root.querySelectorAll("button").forEach((button) => { button.disabled = busy; });
  const matches = (...values) => !state.search || values.some((value) => String(value ?? "").toLowerCase().includes(state.search));
  const nextInternalKey = (section, prefix) => {
    let index = 1;
    while (section[`${prefix}_${index}`]) index += 1;
    return `${prefix}_${index}`;
  };
  const isChinese = () => currentLocale().toLowerCase().startsWith("zh");
  const featureLabel = (feature, key) => feature.title || (
    isChinese() ? feature.label_zh || feature.label || key : feature.label || key
  );

  function panelDialog(message, defaultValue) {
    return new Promise((resolve) => {
      const hasInput = defaultValue !== undefined;
      const input = hasInput ? el("input", { value: defaultValue }) : null;
      const backdrop = el("div", { className: "cdna-modal-backdrop" });
      const finish = (value) => { backdrop.remove(); resolve(value); };
      const dialog = el("div", { className: "cdna-modal" }, [
        el("h3", { text: message }),
        input,
        el("div", { className: "cdna-modal-actions" }, [
          el("button", { text: t("cancel"), onclick: () => finish(null) }),
          el("button", { className: "primary", text: t("confirm"), onclick: () => finish(hasInput ? input.value : true) }),
        ]),
      ]);
      backdrop.appendChild(dialog);
      backdrop.addEventListener("click", (event) => { if (event.target === backdrop) finish(null); });
      dialog.addEventListener("keydown", (event) => {
        if (event.key === "Escape") finish(null);
        if (event.key === "Enter" && (!hasInput || event.target === input)) finish(hasInput ? input.value : true);
      });
      root.appendChild(backdrop);
      (input || dialog.querySelector("button.primary"))?.focus();
      if (input) input.select();
    });
  }

  async function load(force = false) {
    if (state.dirty && !force && !(await panelDialog(t("discard")))) return;
    setBusy(true); setStatus(t("loading"));
    try { state.vocabulary = clone(await requestVocabulary()); state.dirty = false; renderContent(); setStatus(t("loaded"), "success"); }
    catch (error) { setStatus(error.message, "error"); } finally { setBusy(false); }
  }
  async function save() {
    setBusy(true); setStatus(t("saving"));
    try { state.vocabulary = clone(await requestVocabulary(API_PATH, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(state.vocabulary) })); state.dirty = false; renderContent(); setStatus(t("saved"), "success"); }
    catch (error) { setStatus(t("saveFailed") + error.message, "error"); } finally { setBusy(false); }
  }
  async function reset() {
    if (!(await panelDialog(t("resetConfirm")))) return;
    setBusy(true); setStatus(t("resetting"));
    try { state.vocabulary = clone(await requestVocabulary(`${API_PATH}/reset`, { method: "POST" })); state.dirty = false; renderContent(); setStatus(t("resetDone"), "success"); }
    catch (error) { setStatus(t("resetFailed") + error.message, "error"); } finally { setBusy(false); }
  }
  function exportVocabulary() {
    const blob = new Blob([JSON.stringify(state.vocabulary, null, 2) + "\n"], { type: "application/json" });
    const url = URL.createObjectURL(blob); const link = el("a", { href: url, download: "character-dna-vocabulary.json" });
    document.body.appendChild(link); link.click(); link.remove(); URL.revokeObjectURL(url); setStatus(t("exported"), "success");
  }
  const importInput = el("input", { type: "file", accept: ".json,application/json", onchange: async (event) => {
    const file = event.target.files?.[0]; event.target.value = ""; if (!file) return;
    try { const value = JSON.parse(await file.text()); if (!value || typeof value !== "object" || Array.isArray(value)) throw new Error(t("invalidRoot")); state.vocabulary = value; state.dirty = true; renderContent(); setStatus(t("imported")); }
    catch (error) { setStatus(t("importFailed") + error.message, "error"); }
  }}); importInput.hidden = true;

  function field(label, value, update, multiline = true) {
    return el("div", { className: "cdna-vocab-field" }, [el("label", { text: label }), el(multiline ? "textarea" : "input", { value: value ?? "", oninput: (event) => { update(event.target.value); markDirty(); } })]);
  }
  function bilingual(en, zh, updateEn, updateZh, englishLabel = t("english"), chineseLabel = t("chinese")) {
    return el("div", { className: "cdna-vocab-bilingual" }, [field(englishLabel, en, updateEn), field(chineseLabel, zh, updateZh)]);
  }
  function renderFeatures(featureSection, featureGroups) {
    const fragment = document.createDocumentFragment(); let count = 0;
    for (const [groupName, names] of Object.entries(featureGroups)) {
      const group = el("section", { className: "cdna-vocab-group" }); group.appendChild(el("h3", { text: t(groupName) })); let groupCount = 0;
      for (const name of names) {
        const feature = featureSection[name];
        if (!matches(name, feature.label, feature.label_zh, ...feature.levels.flatMap((level) => [level.text, level.text_zh]))) continue;
        const card = el("article", { className: "cdna-vocab-card" });
        card.appendChild(el("h4", { text: featureLabel(feature, name) }));
        for (const level of feature.levels) {
          const row = el("div", { className: "cdna-vocab-level" }, [
            el("strong", { text: String(level.value) }),
            field(t("english"), level.text, (value) => { level.text = value; }),
            field(t("chinese"), level.text_zh, (value) => { level.text_zh = value; }),
          ]);
          card.appendChild(row);
        }
        group.appendChild(card); groupCount += 1; count += 1;
      }
      if (groupCount) fragment.appendChild(group);
    }
    if (!count) fragment.appendChild(el("div", { className: "cdna-vocab-empty", text: t("emptyFeatures") })); return fragment;
  }
  function renderLayerPresets(section, sectionName) {
    const fragment = document.createDocumentFragment(); let count = 0;
    const group = el("section", { className: "cdna-vocab-group" }); group.appendChild(el("h3", { text: t(sectionName) }));
    group.appendChild(el("button", { className: "cdna-add-button", text: t("addPreset"), onclick: async () => {
      const title = String(await panelDialog(t("newPresetTitle"), t("newPresetTitle")) || "").trim();
      if (!title) return;
      const key = nextInternalKey(section, `custom_${sectionName}`);
      section[key] = { title, prompt: "new prompt", prompt_zh: "新提示词" }; markDirty(); renderContent();
    } }));
    for (const [key, entry] of Object.entries(section)) {
      if (!matches(key, entry.title, entry.prompt, entry.prompt_zh)) continue;
      const card = el("article", { className: "cdna-vocab-card" });
      card.appendChild(el("div", { className: "cdna-vocab-title" }, [
        el("h4", { text: featureLabel(entry, key) }),
        el("button", { className: "danger", text: t("deleteEntry"), onclick: () => {
          for (const blueprint of Object.values(state.vocabulary.visual_blueprints)) {
            for (const layer of blueprint.layers || []) {
              if (layer.type === sectionName && layer.preset === key) layer.preset = "none";
            }
          }
          delete section[key]; markDirty(); renderContent();
        } }),
      ]));
      card.appendChild(field(t("entryTitle"), entry.title, (value) => { entry.title = value; }, false));
      card.appendChild(bilingual(entry.prompt, entry.prompt_zh, (value) => { entry.prompt = value; }, (value) => { entry.prompt_zh = value; }));
      group.appendChild(card); count += 1;
    }
    if (!count && state.search) fragment.appendChild(el("div", { className: "cdna-vocab-empty", text: t("emptyPhrases") }));
    fragment.appendChild(group); return fragment;
  }
  function renderIdentityAppearances() {
    const fragment = document.createDocumentFragment(); const section = state.vocabulary.identity_appearances; let count = 0;
    fragment.appendChild(el("button", { className: "cdna-add-button", text: t("addAppearance"), onclick: async () => {
      const title = String(await panelDialog(t("newAppearanceTitle"), t("newAppearanceTitle")) || "").trim();
      if (!title) return;
      const key = nextInternalKey(section, "custom_appearance");
      section[key] = { title, prompt: "new distinctive appearance feature", prompt_zh: "新的外观辨识特征描述" }; markDirty(); renderContent();
    } }));
    for (const [key, entry] of Object.entries(section)) {
      if (!matches(key, entry.title, entry.prompt, entry.prompt_zh)) continue;
      const card = el("article", { className: "cdna-vocab-card" });
      card.appendChild(el("div", { className: "cdna-vocab-title" }, [
        el("h4", { text: featureLabel(entry, key) }),
        el("button", { className: "danger", text: t("deleteEntry"), onclick: () => { delete section[key]; markDirty(); renderContent(); } }),
      ]));
      card.appendChild(field(t("entryTitle"), entry.title, (value) => { entry.title = value; }, false));
      card.appendChild(bilingual(entry.prompt, entry.prompt_zh, (value) => { entry.prompt = value; }, (value) => { entry.prompt_zh = value; }));
      fragment.appendChild(card); count += 1;
    }
    if (!count && state.search) fragment.appendChild(el("div", { className: "cdna-vocab-empty", text: t("emptyPhrases") }));
    return fragment;
  }
  function renderBlueprints() {
    const fragment = document.createDocumentFragment(); const blueprints = state.vocabulary.visual_blueprints; const layers = state.vocabulary.visual_layers;
    const layerTypes = ["look", "performance", "scene", "photography"]; const modes = ["replace", "append", "merge", "clear"];
    fragment.appendChild(el("button", { className: "cdna-add-button", text: t("addBlueprint"), onclick: async () => {
      const title = String(await panelDialog(t("newBlueprintTitle"), t("newBlueprintTitle")) || "").trim();
      if (!title) return;
      const key = nextInternalKey(blueprints, "custom_blueprint");
      blueprints[key] = { title, layers: [], variations: [], negative_prompt: "", negative_prompt_zh: "" }; markDirty(); renderContent();
    } }));
    for (const [name, blueprint] of Object.entries(blueprints)) {
      if (!matches(name, blueprint.title, ...(blueprint.layers || []).flatMap((item) => [item.type, item.preset]))) continue;
      const card = el("article", { className: "cdna-vocab-card" });
      card.appendChild(el("div", { className: "cdna-vocab-title" }, [
        el("h4", { text: featureLabel(blueprint, name) }),
        el("button", { className: "danger", text: t("deleteEntry"), onclick: () => { delete blueprints[name]; markDirty(); renderContent(); } }),
      ]));
      card.appendChild(field(t("entryTitle"), blueprint.title, (value) => { blueprint.title = value; }, false));
      card.appendChild(el("h4", { text: t("negativePrompt") }));
      card.appendChild(bilingual(blueprint.negative_prompt || "", blueprint.negative_prompt_zh || "", (value) => { blueprint.negative_prompt = value; }, (value) => { blueprint.negative_prompt_zh = value; }));
      card.appendChild(el("h4", { text: t("layerStack") }));
      card.appendChild(el("button", { className: "cdna-add-button", text: t("addLayer"), onclick: () => { blueprint.layers ??= []; blueprint.layers.push({ type: "look", preset: Object.keys(layers.look)[0] || "none", mode: "replace", enabled: true }); markDirty(); renderContent(); } }));
      (blueprint.layers || []).forEach((layer, index) => {
        const typeSelect = el("select", { onchange: (event) => { layer.type = event.target.value; layer.preset = Object.keys(layers[layer.type] || {})[0] || "none"; markDirty(); renderContent(); } }, layerTypes.map((key) => el("option", { value: key, text: t(key) })));
        typeSelect.value = layer.type;
        const presetSelect = el("select", { onchange: (event) => { layer.preset = event.target.value; markDirty(); } }, [el("option", { value: "none", text: "none" }), ...Object.entries(layers[layer.type] || {}).map(([key, entry]) => el("option", { value: key, text: featureLabel(entry, key) }))]);
        presetSelect.value = layer.preset;
        const modeSelect = el("select", { onchange: (event) => { layer.mode = event.target.value; markDirty(); } }, modes.map((key) => el("option", { value: key, text: key })));
        modeSelect.value = layer.mode || "replace";
        card.appendChild(el("div", { className: "cdna-layer-row" }, [
          el("input", { type: "checkbox", checked: layer.enabled !== false, onchange: (event) => { layer.enabled = event.target.checked; markDirty(); } }),
          typeSelect, presetSelect, modeSelect,
          el("div", { className: "cdna-layer-actions" }, [
            el("button", { text: "↑", onclick: () => { if (index) [blueprint.layers[index - 1], blueprint.layers[index]] = [blueprint.layers[index], blueprint.layers[index - 1]]; markDirty(); renderContent(); } }),
            el("button", { text: "↓", onclick: () => { if (index < blueprint.layers.length - 1) [blueprint.layers[index + 1], blueprint.layers[index]] = [blueprint.layers[index], blueprint.layers[index + 1]]; markDirty(); renderContent(); } }),
            el("button", { className: "danger", text: "×", onclick: () => { blueprint.layers.splice(index, 1); markDirty(); renderContent(); } }),
          ]),
        ]));
      });
      card.appendChild(el("h4", { text: t("variations") }));
      card.appendChild(el("button", { className: "cdna-add-button", text: t("addVariation"), onclick: () => { blueprint.variations ??= []; blueprint.variations.push({ prompt: "new variation", prompt_zh: "新变化" }); markDirty(); renderContent(); } }));
      (blueprint.variations || []).forEach((variation, index) => card.appendChild(el("div", { className: "cdna-vocab-card" }, [
        bilingual(variation.prompt, variation.prompt_zh, (value) => { variation.prompt = value; }, (value) => { variation.prompt_zh = value; }),
        el("button", { className: "danger", text: t("deleteEntry"), onclick: () => { blueprint.variations.splice(index, 1); markDirty(); renderContent(); } }),
      ])));
      fragment.appendChild(card);
    }
    return fragment;
  }
  function renderProfile() {
    const p = state.vocabulary.profile; const fragment = document.createDocumentFragment();
    const templates = el("section", { className: "cdna-vocab-group" }, [el("h3", { text: t("profile") })]); const card = el("article", { className: "cdna-vocab-card" });
    card.appendChild(bilingual(p.identity_template, p.identity_template_zh, (v) => { p.identity_template = v; }, (v) => { p.identity_template_zh = v; }));
    templates.appendChild(card); fragment.appendChild(templates);
    const quality = el("section", { className: "cdna-vocab-group" }, [el("h3", { text: t("quality") })]); const qc = el("article", { className: "cdna-vocab-card" });
    const positionSelect = el("select", { onchange: (event) => { p.quality_position = event.target.value; markDirty(); } }, [
      el("option", { value: "end", text: t("qualityAtEnd") }),
      el("option", { value: "start", text: t("qualityAtStart") }),
    ]);
    positionSelect.value = p.quality_position ?? "end";
    qc.appendChild(el("div", { className: "cdna-vocab-field" }, [el("label", { text: t("qualityPosition") }), positionSelect]));
    qc.appendChild(bilingual(
      p.quality_phrases.join("\n"),
      p.quality_phrases_zh.join("\n"),
      (value) => { p.quality_phrases = value.split("\n").map((item) => item.trim()).filter(Boolean); },
      (value) => { p.quality_phrases_zh = value.split("\n").map((item) => item.trim()).filter(Boolean); },
    ));
    quality.appendChild(qc); fragment.appendChild(quality); return fragment;
  }
  function renderContent() {
    content.replaceChildren(); if (!state.vocabulary) { content.appendChild(el("div", { className: "cdna-vocab-empty", text: t("notLoaded") })); return; }
    const views = {
      identityAppearances: renderIdentityAppearances,
      faceFeatures: () => renderFeatures(state.vocabulary.features, FEATURE_GROUPS),
      bodyFeatures: () => renderFeatures(state.vocabulary.body_features, BODY_FEATURE_GROUPS),
      visualBlueprints: renderBlueprints,
      look: () => renderLayerPresets(state.vocabulary.visual_layers.look, "look"),
      performance: () => renderLayerPresets(state.vocabulary.visual_layers.performance, "performance"),
      scene: () => renderLayerPresets(state.vocabulary.visual_layers.scene, "scene"),
      photography: () => renderLayerPresets(state.vocabulary.visual_layers.photography, "photography"),
      profile: renderProfile,
    };
    content.appendChild(views[state.activeTab]());
  }

  const tabs = el("div", { className: "cdna-vocab-tabs" }); const buttons = new Map();
  for (const key of ["profile", "identityAppearances", "faceFeatures", "bodyFeatures", "look", "performance", "scene", "photography", "visualBlueprints"]) { const button = el("button", { className: key === state.activeTab ? "active" : "", text: t(key), onclick: () => { state.activeTab = key; buttons.forEach((item, itemKey) => item.classList.toggle("active", itemKey === key)); search.placeholder = t(key.endsWith("Features") ? "searchFeatures" : ["identityAppearances", "visualBlueprints", "look", "performance", "scene", "photography"].includes(key) ? "searchPhrases" : "searchProfile"); renderContent(); } }); buttons.set(key, button); tabs.appendChild(button); }
  const toolbar = el("div", { className: "cdna-vocab-toolbar" }, [el("button", { className: "primary", text: t("save"), onclick: save }), el("button", { text: t("reload"), onclick: () => load(false) }), el("button", { text: t("export"), onclick: exportVocabulary }), el("button", { text: t("import"), onclick: () => importInput.click() }), el("button", { className: "danger", text: t("reset"), onclick: reset })]);
  const header = el("header", { className: "cdna-vocab-header" }, [el("div", { className: "cdna-vocab-title" }, [el("span", { text: `🧬 ${t("title")}` }), el("small", { text: t("autoApply") })]), toolbar, tabs, search, importInput]);
  root.append(header, content, status); container.replaceChildren(root); container.style.height = "100%"; container.style.overflow = "hidden"; load(true);
}

app.registerExtension({
  name: "CharacterDNA.VocabularyPanel",
  beforeRegisterNodeDef(nodeType, nodeData) {
    const labelGroup = {
      CharacterDNAParametricDesigner: "face",
      CharacterDNAParametricBodyDesigner: "body",
    }[nodeData.name];
    if (!labelGroup) return;
    const originalOnNodeCreated = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function () {
      const result = originalOnNodeCreated?.apply(this, arguments);
      const widget = this.widgets?.find((item) => item.name === "feature");
      if (widget) {
        widget.options ||= {};
        widget.options.getOptionLabel = (value) => (
          featureOptionLabels[labelGroup]?.[String(value)] || String(value)
        );
      }
      return result;
    };
  },
  async setup() {
    await loadMessages(); ensureStyles();
    if (globalThis.__characterDnaVocabularyTabRegistered) return;
    globalThis.__characterDnaVocabularyTabRegistered = true;
    app.extensionManager.registerSidebarTab({ id: TAB_ID, type: "custom", title: t("title"), tooltip: t("title"), icon: "character-dna-vocab-icon", render: renderVocabularyPanel });
  },
});
