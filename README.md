# ComfyUI-CharacterDNA

CharacterDNA 用一组可重复、可调节的结构参数描述原创角色身份。它的目标不是训练模型，而是把角色身份拆成稳定的 DNA Seed、19 个连续 Feature 和 5 组 Composite，输出可用于图像生成的中英文提示词。

## 快速开始

项目自带四个可直接拖入 ComfyUI 的示例：

- [`examples/01_basic_seed_to_composite.json`](examples/01_basic_seed_to_composite.json)：从基础身份随机生成 19 个参数，再合成为自然的身份描述。
- [`examples/02_multiple_feature_adjustments.json`](examples/02_multiple_feature_adjustments.json)：在随机 DNA 后连续修改多个 Feature，演示参数继承和覆盖。
- [`examples/03_face_and_body_combined.json`](examples/03_face_and_body_combined.json)：分别生成面部和身体 DNA，再输出合并后的完整身份提示词。
- [`examples/04_batch_generate_analyze_select.json`](examples/04_batch_generate_analyze_select.json)：批量生成、比例分析、目标筛选和 Pareto 预览。

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
Face Composite Identity
        ↓
中英文身份核心提示词
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
Face Composite Identity
        ↓
Body Composite Identity
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
- `identity_appearance`：可选的稳定外观预设，用于瞳色、肤色、发色和辨识标记；会被后续所有身份提示词继承。

### Face DNA Seed Generator

根据同一组 `seed + distinctiveness + harmony` 确定性生成同一套 19 维参数。

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
  → Face Composite Identity
```

`value` 是 `-1.0` 到 `+1.0` 的连续值，Parametric 节点以 `0.1` 步进并保留 1 位小数。词库统一提供 `-1、-0.6667、-0.3333、0、0.3333、0.6667、1` 七个语义锚点，对应“极低 → 明显偏低 → 偏低 → 标准 → 偏高 → 明显偏高 → 极高”。输入值会采用最接近的七档词条；数值为 `0` 表示未指定结构，该 Feature 不输出提示词；某个 Composite 组全部为 `0` 时也不会输出该组。

### Face Composite Identity

把多个 Feature 的数值关系合成为更自然的整体描述，并按显著度选择最重要的组合：

1. Facial Silhouette：脸长、脸宽、颧骨、下颌和下巴。
2. Eye Geometry：眼型、开合度、眼距和眼角倾斜。
3. Brow–Eye Relationship：眉眼距离与眼部关系。
4. Nose Profile：鼻宽、鼻长、立体度和鼻尖方向。
5. Lip Relationship：嘴宽、上下唇厚度和唇峰。

`max_composites` 控制最多输出几组整体关系，范围为 1–5。Composite 采用混合模式：保留关系描述后，会补充其中尚未充分表达的强显著原始 Feature；没有入选的 Composite 组则退回逐项 Feature 描述。因此 19 个数值始终保留在 DNA 中，减少 Composite 数量也不会把对应结构从最终提示词中静默删除。推荐保持 `5`，获得最自然的关系描述。

## 参数说明

完整的 19 个 Feature、正负方向、所属 Composite 和常见联动关系见：

- [`docs/parameters.zh-CN.md`](docs/parameters.zh-CN.md)
- [`docs/body-parameters.zh-CN.md`](docs/body-parameters.zh-CN.md)：20 个身体 Feature、5 组身体 Composite 与组合方法。
- [`docs/phenotype-calibration.zh-CN.md`](docs/phenotype-calibration.zh-CN.md)：可测量比例、校准目标、批内排名与 Pareto 筛选。
- [`docs/facial-proportion-standard.zh-CN.md`](docs/facial-proportion-standard.zh-CN.md)：三庭五眼基准、七档命名与统一比例规则。

## 词库管理

打开 ComfyUI 左侧的 **CharacterDNA Vocabulary** 面板，可以编辑：

- 每个 Feature 的七档中英文提示词；
- 已校准 Feature 的比值定义、标准值、各档锚点及区间；
- 可测量面部 Feature 的 7 档目标比例、容差和中英文比例提示词模板；
- 面部和身体各 5 组 Composite 的中英文短语；
- 画面蓝图，以及造型、表演、场景、摄影四类中英文预设；
- 稳定外观预设与每套画面蓝图的中英文负向提示词；
- 年龄阶段、基础身份模板和固定质量词。

`Fixed quality position` 可选择固定质量词位于完整提示词的最前面或最后面，默认放在最后。面部、身体、Parametric 和 Composite 输出统一遵循该设置。

点击保存后，后续执行的生成节点会直接使用新词库。修改前建议先导出备份。

Parametric Face Designer、Face DNA Seed Generator 和 Face Composite Identity 会把词库修订版本加入执行缓存。即使节点输入没有改变，保存词库后再次完整运行也会重新生成提示词。

身体词库独立保存，因此升级身体功能不会覆盖你已经修改过的面部固定质量词。

### 角色画面蓝图

`Character Visual Blueprint` 是稳定 DNA 之后的画面导演层。画布上只需选择一套 `blueprint` 和一个 `variant_seed`；节点会保留当前最完整的面部/身体身份提示词，并组合这套蓝图中的四类内容：

```text
身份 DNA → Look 人物造型 → Performance 表演 → Scene 场景
         → Photography 摄影 → Seed 细节变化 → 固定质量词
```

默认操作保持极简：选蓝图即可，`identity_only` 表示只输出身份。相同蓝图与相同 `variant_seed` 会得到相同细节变化；生成后控制支持固定、递增、递减和随机。

蓝图不设置年龄门槛：无论角色年龄数值或“少女”等年龄表达是否明确，所有造型、动作、场景和摄影预设都可以自由组合。

节点同时输出英文和中文负向提示词，可直接连接到对应模型的负向条件输入。默认新增 `cool_jewelry_beauty_closeup` 清冷珠宝美妆特写蓝图；配合 Character DNA Designer 的 `oriental_clear_beauty` 稳定外观，可保持灰棕瞳色、真实皮肤、小痣和深棕黑发等身份标记。

需要精调时，在 **CharacterDNA Vocabulary** 面板打开 **Visual Blueprints / 画面蓝图**：可调整高级图层栈、顺序、启用状态和 `replace / append / merge / clear` 合并方式，也可以维护每个蓝图的多条 Seed 变化。Look、Performance、Scene、Photography 四套词库可以独立复用，不必为更多需求继续增加节点。

新版使用独立节点 ID `CharacterDNAVisualBlueprint`，不保留旧 `Clothing & Scene Composer` 的输入结构。已有工作流需要删除旧节点并添加一次新的角色画面蓝图节点。详细说明见 [`docs/presentation-vocabulary.zh-CN.md`](docs/presentation-vocabulary.zh-CN.md)。

## 其他节点

- `InsightFace 106 Detector`：从图像检测 106 点人脸关键点，并输出三庭五眼及实测相对比例诊断图。
- `Face Landmark Geometry Guide`：把 DNA 眼距目标换算为像素级位移，输出局部变形参考、编辑遮罩、目标结构网格和目标 106 点。
- `Phenotype Geometry`：从关键点计算可比较的几何表型，并给出歪头/双眼不对称等拍摄质量指标。
- `Batch Phenotype Analyzer`：统计一批候选图的表型分布，并保留每张图的批次位置。
- `Casting Dataset Loader`：加载候选图数据集。
- `Directional Candidate Selector`：按可编辑比例目标与 DNA 方向共同筛选，并直接输出前 N 名图片和 Pareto 图片。

完整示例见 [`examples/04_batch_generate_analyze_select.json`](examples/04_batch_generate_analyze_select.json)。它把 DNA 提示词、批量生图、106 点分析、目标比例排名、前 N 名和 Pareto 预览连成一条工作流。
