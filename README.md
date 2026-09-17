# ComfyUI-CharacterDNA

CharacterDNA 用一组可重复、可调节的结构参数描述原创角色身份。它的目标不是训练模型，而是把角色身份拆成稳定的 DNA Seed、19 个连续 Feature 和 5 组 Composite，输出可用于图像生成的中英文提示词。

## 快速开始

项目自带两个可直接拖入 ComfyUI 的示例：

- [`examples/01_basic_seed_to_composite.json`](examples/01_basic_seed_to_composite.json)：从基础身份随机生成 19 个参数，再合成为自然的身份描述。
- [`examples/02_multiple_feature_adjustments.json`](examples/02_multiple_feature_adjustments.json)：在随机 DNA 后连续修改多个 Feature，演示参数继承和覆盖。

将 JSON 拖进 ComfyUI 后：

1. 修改角色名称、性别、族裔和视觉年龄。
2. 在 DNA Seed Generator 中选择 seed 的生成后控制方式。
3. 点击完整的 **Run**。
4. 生成的中文身份核心提示词会由 ComfyUI 自带的 Save Text 写入 `output/CharacterDNA/`。

> 保存工作流后再刷新页面。若使用“只运行选中节点”等部分执行方式，ComfyUI 不会更新 `control after generate`。

## 核心生成路线

```text
Character DNA Designer
        ↓
DNA Seed Generator
        ↓
Parametric Character Designer（可选，可串联多个）
        ↓
Composite Identity
        ↓
中英文身份核心提示词
```

### Character DNA Designer

建立不随机的基础身份资料：

- `character_name`：角色名称，只用于身份记录。
- `gender`：提示词中的性别表达。
- `ancestry`：提示词中的外观族裔表达。
- `visual_age`：视觉年龄，范围 0–120，不限制为成年人。

### DNA Seed Generator

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

### Parametric Character Designer

每个节点只覆盖一个 Feature，其他参数从输入 DNA 完整继承。因此要修改多个参数时，直接串联多个节点：

```text
Seed Generator
  → face_length = 0.5
  → jaw_width = -0.5
  → canthal_tilt = 0.5
  → Composite Identity
```

`value` 是 `-1.0` 到 `+1.0` 的连续值。词库提供 `-1、-0.5、0、0.5、1` 五个语义锚点，中间值会采用最接近的词条；实际 DNA 仍保留连续数值。数值为 `0` 表示未指定结构，该 Feature 不输出提示词；某个 Composite 组全部为 `0` 时也不会输出该组。

### Composite Identity

把多个 Feature 的数值关系合成为更自然的整体描述，并按显著度选择最重要的组合：

1. Facial Silhouette：脸长、脸宽、颧骨、下颌和下巴。
2. Eye Geometry：眼型、开合度、眼距和眼角倾斜。
3. Brow–Eye Relationship：眉眼距离与眼部关系。
4. Nose Profile：鼻宽、鼻长、立体度和鼻尖方向。
5. Lip Relationship：嘴宽、上下唇厚度和唇峰。

`max_composites` 控制最多输出几组，范围为 1–5。它不会改变 DNA，只控制提示词保留多少组整体特征。

## 参数说明

完整的 19 个 Feature、正负方向、所属 Composite 和常见联动关系见：

- [`docs/parameters.zh-CN.md`](docs/parameters.zh-CN.md)

## 词库管理

打开 ComfyUI 左侧的 **CharacterDNA Vocabulary** 面板，可以编辑：

- 每个 Feature 的五档中英文提示词；
- 5 组 Composite 的中英文短语；
- 年龄阶段、基础身份模板和固定质量词。

点击保存后，后续执行的生成节点会直接使用新词库。修改前建议先导出备份。

## 其他节点

- `InsightFace 106 Detector`：从图像检测 106 点人脸关键点。
- `Phenotype Geometry`：从关键点计算可比较的几何表型。
- `Batch Phenotype Analyzer`：统计一批候选图的表型分布。
- `Casting Dataset Loader`：加载候选图数据集。
- `Directional Candidate Selector`：按 DNA 的正负方向筛选更匹配的候选图。
