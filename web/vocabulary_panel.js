import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

const API_PATH = "/character-dna/vocabulary";
const TAB_ID = "character-dna-vocabulary";
const FEATURE_GROUPS = {
  face: ["face_length", "face_width", "cheekbone_width", "jaw_width", "chin_width", "chin_length"],
  eyes: ["eye_elongation", "eye_openness", "eye_spacing", "canthal_tilt", "brow_eye_distance"],
  nose: ["nose_width", "nose_length", "nose_projection", "nose_tip_rotation"],
  mouth: ["mouth_width", "upper_lip_fullness", "lower_lip_fullness", "cupid_bow_definition"],
};
const COMPOSITE_GROUPS = ["facial_silhouette", "eye_geometry", "brow_eye_relationship", "nose_profile", "lip_relationship"];
const BODY_FEATURE_GROUPS = {
  frame: ["stature", "shoulder_width", "shoulder_slope", "ribcage_width", "pelvis_width"],
  torso: ["neck_length", "neck_thickness", "torso_length", "chest_fullness", "waist_definition", "hip_fullness"],
  limbs: ["arm_length", "hand_scale", "leg_length", "thigh_length_ratio", "foot_scale"],
  build: ["upper_body_fullness", "lower_body_fullness", "limb_thickness", "muscularity"],
};
const BODY_COMPOSITE_GROUPS = ["overall_frame", "torso_architecture", "limb_proportions", "build_distribution", "scale_balance"];

const FALLBACK = {
  title: "CharacterDNA Vocabulary", autoApply: "Changes apply after saving", save: "Save", reload: "Reload",
  export: "Export", import: "Import", reset: "Restore defaults", features: "Feature vocabulary",
  composites: "Composite vocabulary", profile: "Base templates", searchFeatures: "Search features or phrases…",
  searchComposites: "Search composites or phrases…", searchPhrases: "Search presets or phrases…", searchProfile: "Search is available in vocabulary tabs",
  loading: "Loading vocabulary…", loaded: "Vocabulary loaded", unsaved: "Unsaved changes",
  discard: "Discard unsaved changes and reload?", saving: "Validating and saving…",
  saved: "Saved. Generation nodes now use the updated vocabulary.", saveFailed: "Save failed: ",
  resetConfirm: "Restore the default vocabulary? Current changes will be overwritten.", resetting: "Restoring defaults…",
  resetDone: "Default vocabulary restored", resetFailed: "Restore failed: ", exported: "Vocabulary exported",
  imported: "Imported into the editor; click Save to apply", importFailed: "Import failed: ", invalidRoot: "JSON root must be an object",
  emptyFeatures: "No matching features", emptyComposites: "No matching composite phrases", emptyPhrases: "No matching presets", notLoaded: "Vocabulary is not loaded",
  english: "English prompt", chinese: "Chinese prompt", value: "Value", identityTemplate: "Identity template",
  ageTemplate: "Age template", lifeStages: "Life stages", maxAge: "Upper age (blank for last)", addStage: "+ Add life stage",
  quality: "Fixed quality phrases", qualityPosition: "Fixed quality position", qualityAtStart: "At prompt start", qualityAtEnd: "At prompt end", face: "Face", eyes: "Eyes", nose: "Nose", mouth: "Mouth",
  faceFeatures: "Face Features", bodyFeatures: "Body Features", faceComposites: "Face Composite", bodyComposites: "Body Composite",
  identityAppearances: "Identity Appearance", addAppearance: "+ Add appearance", newAppearanceKey: "New appearance key",
  visualBlueprints: "Visual Blueprints", look: "Look", performance: "Performance", scene: "Scene", photography: "Photography",
  addBlueprint: "+ Add blueprint", addPreset: "+ Add preset", addLayer: "+ Add layer", addVariation: "+ Add variation",
  newBlueprintKey: "New blueprint key", newPresetKey: "New preset key", deleteEntry: "Delete", blueprintLabel: "Display label", layerStack: "Advanced layer stack", variations: "Seed variations", enabled: "Enabled", layerType: "Layer", preset: "Preset", mergeMode: "Mode",
  negativePrompt: "Negative prompt",
  frame: "Frame", torso: "Torso", limbs: "Limbs", build: "Build",
  overall_frame: "Overall frame", torso_architecture: "Torso architecture", limb_proportions: "Limb proportions",
  build_distribution: "Build distribution", scale_balance: "Scale balance",
  facial_silhouette: "Facial silhouette", eye_geometry: "Eye geometry", brow_eye_relationship: "Brow-eye relationship",
  nose_profile: "Nose profile", lip_relationship: "Lip relationship", requestError: "Request failed",
};

let messages = FALLBACK;
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
      if (all?.[candidate]?.characterDNA) {
        messages = { ...FALLBACK, ...all[candidate].characterDNA };
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
    .character-dna-vocab-icon::before{content:"🧬";font-size:20px}.cdna-vocab{height:100%;display:flex;flex-direction:column;color:var(--fg-color,#ddd);background:var(--comfy-menu-bg,#202020);font:13px/1.4 system-ui,sans-serif}.cdna-vocab *{box-sizing:border-box}.cdna-vocab-header{padding:12px;border-bottom:1px solid var(--border-color,#444);display:grid;gap:9px}.cdna-vocab-title{font-size:16px;font-weight:700;display:flex;justify-content:space-between;gap:8px;align-items:center}.cdna-vocab-title small{font-size:11px;font-weight:500;opacity:.65}.cdna-vocab-toolbar,.cdna-vocab-tabs{display:flex;flex-wrap:wrap;gap:6px}.cdna-vocab button{border:1px solid var(--border-color,#555);border-radius:6px;padding:6px 9px;color:inherit;background:var(--comfy-input-bg,#303030);cursor:pointer}.cdna-vocab button:hover{filter:brightness(1.15)}.cdna-vocab button:disabled{opacity:.45;cursor:wait}.cdna-vocab button.primary{background:#2f6fda;color:white;border-color:#4d86e8}.cdna-vocab button.danger{color:#ffb3b3}.cdna-vocab-tabs button.active{background:#6741a5;color:white;border-color:#8d67cb}.cdna-vocab input,.cdna-vocab textarea,.cdna-vocab select{width:100%;border:1px solid var(--border-color,#555);border-radius:5px;padding:6px 7px;color:inherit;background:var(--comfy-input-bg,#292929);font:inherit}.cdna-vocab textarea{min-height:54px;resize:vertical}.cdna-vocab-content{min-height:0;flex:1;overflow:auto;padding:10px}.cdna-vocab-status{min-height:32px;padding:7px 11px;border-top:1px solid var(--border-color,#444);font-size:12px;opacity:.85}.cdna-vocab-status.error{color:#ff8e8e;opacity:1}.cdna-vocab-status.success{color:#8ee5aa;opacity:1}.cdna-vocab-group{margin-bottom:14px}.cdna-vocab-group>h3{position:sticky;top:-10px;z-index:2;margin:0 0 7px;padding:8px 2px 5px;background:var(--comfy-menu-bg,#202020);font-size:13px}.cdna-vocab-card{border:1px solid var(--border-color,#444);border-radius:7px;padding:9px;margin-bottom:8px;background:color-mix(in srgb,var(--comfy-input-bg,#292929) 70%,transparent)}.cdna-vocab-card h4{margin:0 0 8px;font:600 12px/1.3 ui-monospace,monospace;word-break:break-all}.cdna-vocab-field{display:grid;gap:4px;margin-bottom:8px}.cdna-vocab-field>label{font-size:11px;opacity:.72}.cdna-vocab-level{display:grid;grid-template-columns:48px 1fr 1fr;gap:6px;align-items:start;margin-bottom:7px}.cdna-vocab-level strong{padding:7px 2px;text-align:center}.cdna-vocab-bilingual{display:grid;grid-template-columns:1fr 1fr;gap:7px}.cdna-vocab-empty{padding:24px 8px;text-align:center;opacity:.6}.cdna-vocab-life-stage{display:grid;grid-template-columns:90px 1fr 1fr auto;gap:5px;margin-bottom:6px}.cdna-layer-row{display:grid;grid-template-columns:26px 1fr 1.4fr .8fr auto;gap:5px;align-items:center;margin-bottom:6px}.cdna-layer-actions{display:flex;gap:3px}.cdna-layer-actions button{padding:4px 6px}@media(max-width:700px){.cdna-layer-row{grid-template-columns:26px 1fr}.cdna-layer-row select,.cdna-layer-actions{grid-column:2}.cdna-vocab-level,.cdna-vocab-bilingual{grid-template-columns:1fr}.cdna-vocab-level strong{text-align:left}.cdna-vocab-life-stage{grid-template-columns:80px 1fr}.cdna-vocab-life-stage button{grid-column:2;justify-self:end}}
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
  const state = { vocabulary: null, activeTab: "faceFeatures", search: "", dirty: false };
  const root = el("div", { className: "cdna-vocab" });
  const content = el("div", { className: "cdna-vocab-content" });
  const status = el("div", { className: "cdna-vocab-status", text: t("loading") });
  const search = el("input", { type: "search", placeholder: t("searchFeatures"), oninput: (event) => { state.search = event.target.value.trim().toLowerCase(); renderContent(); } });
  const setStatus = (message, kind = "") => { status.textContent = message; status.className = `cdna-vocab-status${kind ? ` ${kind}` : ""}`; };
  const markDirty = () => { state.dirty = true; setStatus(t("unsaved")); };
  const setBusy = (busy) => root.querySelectorAll("button").forEach((button) => { button.disabled = busy; });
  const matches = (...values) => !state.search || values.some((value) => String(value ?? "").toLowerCase().includes(state.search));

  async function load(force = false) {
    if (state.dirty && !force && !window.confirm(t("discard"))) return;
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
    if (!window.confirm(t("resetConfirm"))) return;
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
  function bilingual(en, zh, updateEn, updateZh) {
    return el("div", { className: "cdna-vocab-bilingual" }, [field(t("english"), en, updateEn), field(t("chinese"), zh, updateZh)]);
  }
  function renderFeatures(featureSection, featureGroups) {
    const fragment = document.createDocumentFragment(); let count = 0;
    for (const [groupName, names] of Object.entries(featureGroups)) {
      const group = el("section", { className: "cdna-vocab-group" }); group.appendChild(el("h3", { text: t(groupName) })); let groupCount = 0;
      for (const name of names) {
        const feature = featureSection[name];
        if (!matches(name, ...feature.levels.flatMap((level) => [level.text, level.text_zh]))) continue;
        const card = el("article", { className: "cdna-vocab-card" }); card.appendChild(el("h4", { text: name }));
        for (const level of feature.levels) card.appendChild(el("div", { className: "cdna-vocab-level" }, [
          el("strong", { text: String(level.value) }),
          field(t("english"), level.text, (value) => { level.text = value; }),
          field(t("chinese"), level.text_zh, (value) => { level.text_zh = value; }),
        ]));
        group.appendChild(card); groupCount += 1; count += 1;
      }
      if (groupCount) fragment.appendChild(group);
    }
    if (!count) fragment.appendChild(el("div", { className: "cdna-vocab-empty", text: t("emptyFeatures") })); return fragment;
  }
  function renderComposites(compositeSection, localizedSection, compositeGroups) {
    const fragment = document.createDocumentFragment(); let count = 0;
    for (const groupName of compositeGroups) {
      const entries = compositeSection[groupName]; const localized = localizedSection[groupName];
      const keys = Object.keys(entries).filter((key) => matches(groupName, key, entries[key], localized[key])); if (!keys.length) continue;
      const group = el("section", { className: "cdna-vocab-group" }); group.appendChild(el("h3", { text: t(groupName) }));
      for (const key of keys) { const card = el("article", { className: "cdna-vocab-card" }); card.appendChild(el("h4", { text: key })); card.appendChild(bilingual(entries[key], localized[key], (value) => { entries[key] = value; }, (value) => { localized[key] = value; })); group.appendChild(card); count += 1; }
      fragment.appendChild(group);
    }
    if (!count) fragment.appendChild(el("div", { className: "cdna-vocab-empty", text: t("emptyComposites") })); return fragment;
  }
  function renderLayerPresets(section, sectionName) {
    const fragment = document.createDocumentFragment(); let count = 0;
    const group = el("section", { className: "cdna-vocab-group" }); group.appendChild(el("h3", { text: t(sectionName) }));
    for (const [key, entry] of Object.entries(section)) {
      if (!matches(key, entry.prompt, entry.prompt_zh)) continue;
      const card = el("article", { className: "cdna-vocab-card" });
      card.appendChild(el("div", { className: "cdna-vocab-title" }, [
        el("h4", { text: key }),
        el("button", { className: "danger", text: t("deleteEntry"), onclick: () => {
          for (const blueprint of Object.values(state.vocabulary.visual_blueprints)) {
            for (const layer of blueprint.layers || []) {
              if (layer.type === sectionName && layer.preset === key) layer.preset = "none";
            }
          }
          delete section[key]; markDirty(); renderContent();
        } }),
      ]));
      card.appendChild(bilingual(entry.prompt, entry.prompt_zh, (value) => { entry.prompt = value; }, (value) => { entry.prompt_zh = value; }));
      group.appendChild(card); count += 1;
    }
    group.appendChild(el("button", { text: t("addPreset"), onclick: () => {
      const rawKey = window.prompt(t("newPresetKey"), `new_${sectionName}`);
      const key = String(rawKey || "").trim();
      if (!key || key === "none" || section[key]) return;
      section[key] = { prompt: "new prompt", prompt_zh: "新提示词" }; markDirty(); renderContent();
    } }));
    if (!count && state.search) fragment.appendChild(el("div", { className: "cdna-vocab-empty", text: t("emptyPhrases") }));
    fragment.appendChild(group); return fragment;
  }
  function renderIdentityAppearances() {
    const fragment = document.createDocumentFragment(); const section = state.vocabulary.identity_appearances; let count = 0;
    for (const [key, entry] of Object.entries(section)) {
      if (!matches(key, entry.label, entry.label_zh, entry.prompt, entry.prompt_zh)) continue;
      const card = el("article", { className: "cdna-vocab-card" });
      card.appendChild(el("div", { className: "cdna-vocab-title" }, [
        el("h4", { text: key }),
        el("button", { className: "danger", text: t("deleteEntry"), onclick: () => { delete section[key]; markDirty(); renderContent(); } }),
      ]));
      card.appendChild(bilingual(entry.label, entry.label_zh, (value) => { entry.label = value; }, (value) => { entry.label_zh = value; }));
      card.appendChild(bilingual(entry.prompt, entry.prompt_zh, (value) => { entry.prompt = value; }, (value) => { entry.prompt_zh = value; }));
      fragment.appendChild(card); count += 1;
    }
    fragment.appendChild(el("button", { text: t("addAppearance"), onclick: () => {
      const rawKey = window.prompt(t("newAppearanceKey"), "new_appearance"); const key = String(rawKey || "").trim();
      if (!key || key === "none" || section[key]) return;
      section[key] = { label: key.replaceAll("_", " "), label_zh: "新稳定外观", prompt: "new stable appearance", prompt_zh: "新稳定外观描述" }; markDirty(); renderContent();
    } }));
    if (!count && state.search) fragment.appendChild(el("div", { className: "cdna-vocab-empty", text: t("emptyPhrases") }));
    return fragment;
  }
  function renderBlueprints() {
    const fragment = document.createDocumentFragment(); const blueprints = state.vocabulary.visual_blueprints; const layers = state.vocabulary.visual_layers;
    const layerTypes = ["look", "performance", "scene", "photography"]; const modes = ["replace", "append", "merge", "clear"];
    for (const [name, blueprint] of Object.entries(blueprints)) {
      if (!matches(name, blueprint.label, blueprint.label_zh, ...(blueprint.layers || []).flatMap((item) => [item.type, item.preset]))) continue;
      const card = el("article", { className: "cdna-vocab-card" });
      card.appendChild(el("div", { className: "cdna-vocab-title" }, [
        el("h4", { text: name }),
        name === "identity_only" ? null : el("button", { className: "danger", text: t("deleteEntry"), onclick: () => { delete blueprints[name]; markDirty(); renderContent(); } }),
      ]));
      card.appendChild(bilingual(blueprint.label, blueprint.label_zh, (value) => { blueprint.label = value; }, (value) => { blueprint.label_zh = value; }));
      card.appendChild(el("h4", { text: t("negativePrompt") }));
      card.appendChild(bilingual(blueprint.negative_prompt || "", blueprint.negative_prompt_zh || "", (value) => { blueprint.negative_prompt = value; }, (value) => { blueprint.negative_prompt_zh = value; }));
      card.appendChild(el("h4", { text: t("layerStack") }));
      (blueprint.layers || []).forEach((layer, index) => {
        const typeSelect = el("select", { onchange: (event) => { layer.type = event.target.value; layer.preset = Object.keys(layers[layer.type] || {})[0] || "none"; markDirty(); renderContent(); } }, layerTypes.map((key) => el("option", { value: key, text: t(key) })));
        typeSelect.value = layer.type;
        const presetSelect = el("select", { onchange: (event) => { layer.preset = event.target.value; markDirty(); } }, [el("option", { value: "none", text: "none" }), ...Object.keys(layers[layer.type] || {}).map((key) => el("option", { value: key, text: key }))]);
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
      card.appendChild(el("button", { text: t("addLayer"), onclick: () => { blueprint.layers ??= []; blueprint.layers.push({ type: "look", preset: Object.keys(layers.look)[0] || "none", mode: "replace", enabled: true }); markDirty(); renderContent(); } }));
      card.appendChild(el("h4", { text: t("variations") }));
      (blueprint.variations || []).forEach((variation, index) => card.appendChild(el("div", { className: "cdna-vocab-card" }, [
        bilingual(variation.prompt, variation.prompt_zh, (value) => { variation.prompt = value; }, (value) => { variation.prompt_zh = value; }),
        el("button", { className: "danger", text: t("deleteEntry"), onclick: () => { blueprint.variations.splice(index, 1); markDirty(); renderContent(); } }),
      ])));
      card.appendChild(el("button", { text: t("addVariation"), onclick: () => { blueprint.variations ??= []; blueprint.variations.push({ prompt: "new variation", prompt_zh: "新变化" }); markDirty(); renderContent(); } }));
      fragment.appendChild(card);
    }
    fragment.appendChild(el("button", { text: t("addBlueprint"), onclick: () => {
      const rawKey = window.prompt(t("newBlueprintKey"), "new_blueprint"); const key = String(rawKey || "").trim();
      if (!key || blueprints[key]) return;
      blueprints[key] = { label: key.replaceAll("_", " "), label_zh: "新画面蓝图", layers: [], variations: [] }; markDirty(); renderContent();
    } }));
    return fragment;
  }
  function renderProfile() {
    const p = state.vocabulary.profile; const fragment = document.createDocumentFragment();
    const templates = el("section", { className: "cdna-vocab-group" }, [el("h3", { text: t("profile") })]); const card = el("article", { className: "cdna-vocab-card" });
    card.appendChild(bilingual(p.identity_template, p.identity_template_zh, (v) => { p.identity_template = v; }, (v) => { p.identity_template_zh = v; }));
    card.appendChild(bilingual(p.age_template, p.age_template_zh, (v) => { p.age_template = v; }, (v) => { p.age_template_zh = v; })); templates.appendChild(card); fragment.appendChild(templates);
    const stages = el("section", { className: "cdna-vocab-group" }, [el("h3", { text: t("lifeStages") })]); const stageCard = el("article", { className: "cdna-vocab-card" });
    p.life_stages.forEach((stage, index) => stageCard.appendChild(el("div", { className: "cdna-vocab-life-stage" }, [
      el("input", { type: "number", min: 0, placeholder: t("maxAge"), value: stage.max_exclusive ?? "", oninput: (e) => { if (e.target.value === "") delete stage.max_exclusive; else stage.max_exclusive = Number(e.target.value); markDirty(); } }),
      el("input", { value: stage.text, placeholder: t("english"), oninput: (e) => { stage.text = e.target.value; markDirty(); } }),
      el("input", { value: stage.text_zh, placeholder: t("chinese"), oninput: (e) => { stage.text_zh = e.target.value; markDirty(); } }),
      el("button", { className: "danger", text: "×", onclick: () => { p.life_stages.splice(index, 1); markDirty(); renderContent(); } }),
    ])));
    stageCard.appendChild(el("button", { text: t("addStage"), onclick: () => { p.life_stages.push({ text: "new stage", text_zh: "新阶段" }); markDirty(); renderContent(); } })); stages.appendChild(stageCard); fragment.appendChild(stages);
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
      faceComposites: () => renderComposites(state.vocabulary.composites, state.vocabulary.composites_zh, COMPOSITE_GROUPS),
      bodyComposites: () => renderComposites(state.vocabulary.body_composites, state.vocabulary.body_composites_zh, BODY_COMPOSITE_GROUPS),
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
  for (const key of ["identityAppearances", "faceFeatures", "bodyFeatures", "faceComposites", "bodyComposites", "visualBlueprints", "look", "performance", "scene", "photography", "profile"]) { const button = el("button", { className: key === state.activeTab ? "active" : "", text: t(key), onclick: () => { state.activeTab = key; buttons.forEach((item, itemKey) => item.classList.toggle("active", itemKey === key)); search.placeholder = t(key.endsWith("Features") ? "searchFeatures" : key.endsWith("Composites") ? "searchComposites" : ["identityAppearances", "visualBlueprints", "look", "performance", "scene", "photography"].includes(key) ? "searchPhrases" : "searchProfile"); renderContent(); } }); buttons.set(key, button); tabs.appendChild(button); }
  const toolbar = el("div", { className: "cdna-vocab-toolbar" }, [el("button", { className: "primary", text: t("save"), onclick: save }), el("button", { text: t("reload"), onclick: () => load(false) }), el("button", { text: t("export"), onclick: exportVocabulary }), el("button", { text: t("import"), onclick: () => importInput.click() }), el("button", { className: "danger", text: t("reset"), onclick: reset })]);
  const header = el("header", { className: "cdna-vocab-header" }, [el("div", { className: "cdna-vocab-title" }, [el("span", { text: `🧬 ${t("title")}` }), el("small", { text: t("autoApply") })]), toolbar, tabs, search, importInput]);
  root.append(header, content, status); container.replaceChildren(root); container.style.height = "100%"; container.style.overflow = "hidden"; load(true);
}

app.registerExtension({
  name: "CharacterDNA.VocabularyPanel",
  async setup() {
    await loadMessages(); ensureStyles();
    if (globalThis.__characterDnaVocabularyTabRegistered) return;
    globalThis.__characterDnaVocabularyTabRegistered = true;
    app.extensionManager.registerSidebarTab({ id: TAB_ID, type: "custom", title: t("title"), tooltip: t("title"), icon: "character-dna-vocab-icon", render: renderVocabularyPanel });
  },
});
