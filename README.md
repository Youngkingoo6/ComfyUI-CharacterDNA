# ComfyUI-CharacterDNA

CharacterDNA 用一组可重复、可调节的参数描述原创角色身份。它的目标不是训练模型，而是用 DNA Seed 和口语化特征词，直接输出可用于图像生成的中英文提示词。

## 快速开始

项目自带四个可直接拖入 ComfyUI 的示例：

- [`examples/01_basic_face_seed.json`](examples/01_basic_face_seed.json)：从基础身份随机生成 24 个面部参数，并直接输出提示词。
- [`examples/02_multiple_feature_adjustments.json`](examples/02_multiple_feature_adjustments.json)：在随机 DNA 后连续修改多个 Feature，演示参数继承和覆盖。
- [`examples/03_face_and_body_combined.json`](examples/03_face_and_body_combined.json)：分别生成面部和身体 DNA，再输出合并后的完整身份提示词。
- [`examples/04_batch_generate_analyze_select.json`](examples/04_batch_generate_analyze_select.json)：批量生成、几何分析、目标筛选和 Pareto 预览。

将 JSON 拖进 ComfyUI 后：

1. 修改角色名称、性别、族裔和视觉年龄。
2. 在 Face DNA Seed Generator 中选择 seed 的生成后控制方式。
3. 点击完整的 **Run**。
4. 生成的中文身份核心提示词会由 ComfyUI 自带的 Save Text 写入 `output/CharacterDNA/`。

> 保存工作流后再刷新页面。若使用“只运行选中节点”等部分执行方式，ComfyUI 不会更新 `control after generate`。

## 核心生成路线

```text
Character DNA Designer
        ↓
Face DNA Seed Generator
        ↓
Parametric Face Designer（可选，可串联多个）
        ↓
直接使用中英文面部提示词
```

身体 DNA 与面部 DNA 共用同一个 `CHARACTER_DNA`，推荐接法：

```text
Character DNA Designer
        ↓
Face DNA Seed Generator
        ↓
Body DNA Seed Generator（身体）
        ↓
Parametric Face / Body Designer（可选，可串联）
        ↓
Character Visual Blueprint（可选）
        ↓
中英文完整身份提示词
```

### Character DNA Designer

建立不随机的基础身份资料：

- `character_name`：角色名称，只用于身份记录。
- `gender`：提示词中的性别表达。
- `ancestry`：提示词中的外观族裔表达。
- `visual_age`：视觉年龄，范围 0–120，不限制为成年人。
- `identity_appearance`：可选的外观辨识特征，用于固定有辨识度的瞳色、肤色、发型和自然标记；会被后续所有身份提示词继承。

### Face DNA Seed Generator

根据同一组 `seed + distinctiveness + harmony` 确定性生成同一套 24 维参数。

- `seed`：决定各 Feature 的方向和组合；相同输入会得到相同身份。
- `control after generate`：`fixed` 保持、`increment` 递增、`decrement` 递减、`randomize` 随机。
- `distinctiveness`：控制偏离中性脸的强度与主要身份特征数量。数值越高，显著特征通常越多、越强。
- `harmony`：柔化明显冲突或过度极端的组合。数值越高，关系越协调；数值越低，保留更多夸张和偶然性。

推荐起点：

```text
distinctiveness = 0.70
harmony = 0.85
```

### Parametric Face Designer

每个节点只覆盖一个 Feature，其他参数从输入 DNA 完整继承。因此要修改多个参数时，直接串联多个节点：

```text
Seed Generator
  → face_length = 0.3
  → jaw_width = -0.3
  → canthal_tilt = 0.3
  → 直接使用最后一个节点的提示词
```

`value` 使用 `-1、-0.5、0、0.5、1` 五档下拉选择，输出“短脸、眼距稍宽、鼻梁偏平”这类直接的词。数值为 `0` 表示未指定结构，不输出该 Feature。

脸部和身体 Parametric 节点的 `weight` 都只控制当前节点所修改 Feature 的提示词权重。`0` 表示关闭加权、保持原文；启用值为 `1.0–2.0`，步进 `0.1`。例如设置为 `1.2` 后输出 `(slightly wide-set eyes:1.2)` 或 `(long legs:1.2)`，中文输出同样使用 `(特征描述:1.2)`。权重保存在对应 DNA 中并随后续 Parametric 节点继承；再次修改同一 Feature 且设为 `0` 会移除该项已有权重。

每次执行 Parametric Face Designer 都会根据当前 DNA 重新生成完整面部提示词，因此最后一个 Parametric 节点的输出已经包含之前设置的所有非零特征。Face Composite Identity 已移除，避免重复改写和弱化具体参数。

身体部分采用相同方式：Body DNA Seed Generator 和 Parametric Body Designer 会直接输出继承面部后的完整身份提示词。`body_profile` 可选择按种子随机生成，或直接使用 `balanced / petite / athletic / curvy / slender_tall` 组合预设；预设只映射现有 20 项身体参数，不增加新参数。多个 Parametric Body 节点可以串联，最后一个节点包含此前所有非零身体参数。Body Composite Identity 已移除。

## 参数说明

完整的面部与身体 Feature、正负方向和常见联动关系见：

- [`docs/parameters.zh-CN.md`](docs/parameters.zh-CN.md)
- [`docs/body-parameters.zh-CN.md`](docs/body-parameters.zh-CN.md)：20 个身体 Feature、正负方向与串联修改方法。
- [`docs/phenotype-calibration.zh-CN.md`](docs/phenotype-calibration.zh-CN.md)：可测量比例、校准目标、批内排名与 Pareto 筛选。

## 词库管理

打开 ComfyUI 左侧的 **CharacterDNA Vocabulary** 面板，可以编辑：

- 每个 Feature 的五档中英文提示词；
- 画面蓝图，以及穿搭、表情跟姿态、场景、摄影四类带中英文显示名称的预设；
- 外观辨识特征（含瞳色、肤色、肤质、发型与自然标记组合）与每套画面蓝图的中英文负向提示词；
- 年龄阶段、基础身份模板和固定质量词。

`Fixed quality position` 可选择固定质量词位于完整提示词的最前面或最后面，默认放在最后。面部、身体和 Parametric 输出统一遵循该设置。

点击保存后，后续执行的生成节点会直接使用新词库。修改前建议先导出备份。

Parametric Face Designer 和 Face DNA Seed Generator 会把词库修订版本加入执行缓存。即使节点输入没有改变，保存词库后再次完整运行也会重新生成提示词。

身体词库独立保存，因此升级身体功能不会覆盖你已经修改过的面部固定质量词。

### 角色画面蓝图

`Character Visual Blueprint` 是稳定 DNA 之后的画面导演层。画布上只需选择一套 `blueprint` 和一个 `variant_seed`；节点会保留当前最完整的面部/身体身份提示词，并组合这套蓝图中的四类内容：

```text
身份 DNA → Outfit 穿搭 → Expression & Pose 表情跟姿态 → Scene 场景
         → Photography 摄影 → Seed 细节变化 → 固定质量词
```

默认操作保持极简：选择唯一的 `identity_only`（界面显示为“默认人像”）即可组合默认的穿搭、表情跟姿态、场景和摄影。相同蓝图与相同 `variant_seed` 会得到相同细节变化；生成后控制支持固定、递增、递减和随机。

蓝图不设置年龄门槛：无论角色年龄数值或“少女”等年龄表达是否明确，所有造型、动作、场景和摄影预设都可以自由组合。

节点同时输出英文和中文负向提示词，可直接连接到对应模型的负向条件输入。内置内容只保留一套默认外观辨识特征和一套默认画面蓝图，用户仍可在词库面板自行添加预设。

需要精调时，在 **CharacterDNA Vocabulary** 面板打开 **Visual Blueprints / 画面蓝图**：可调整高级图层栈、顺序、启用状态和 `replace / append / merge / clear` 合并方式，也可以维护每个蓝图的多条 Seed 变化。Outfit、Expression & Pose、Scene、Photography 四套词库可以独立复用，不必为更多需求继续增加节点。

内置表现层词库各保留一套默认 Outfit、Expression & Pose、Scene 和 Photography；外观辨识特征也只保留一套默认。内容采用可直接观察的自然语言描述，而不是堆叠孤立标签。词库面板会随界面语言显示中文或英文名称，同时保留内部键名作为小字标识；新增按钮固定显示在列表顶部。

新版使用独立节点 ID `CharacterDNAVisualBlueprint`，不保留旧 `Clothing & Scene Composer` 的输入结构。已有工作流需要删除旧节点并添加一次新的角色画面蓝图节点。详细说明见 [`docs/presentation-vocabulary.zh-CN.md`](docs/presentation-vocabulary.zh-CN.md)。

## 其他节点

- `InsightFace 106 Detector`：从图像检测 106 点人脸关键点，并输出三庭五眼及实测相对比例诊断图。
- `Phenotype Geometry`：从关键点计算可比较的几何表型，并给出歪头/双眼不对称等拍摄质量指标。
- `Batch Phenotype Analyzer`：统计一批候选图的表型分布，并保留每张图的批次位置。
- `Casting Dataset Loader`：加载候选图数据集。
- `Directional Candidate Selector`：按可编辑比例目标与 DNA 方向共同筛选，并直接输出前 N 名图片和 Pareto 图片。

完整示例见 [`examples/04_batch_generate_analyze_select.json`](examples/04_batch_generate_analyze_select.json)。它把 DNA 提示词、批量生图、106 点分析、候选排名、前 N 名和 Pareto 预览连成一条工作流。比例只用于生成后的分析与筛选，不再写入生图提示词。
