# 角色画面蓝图与表现层词库

画面蓝图属于角色的可变表现层，不会修改稳定的面部或身体 DNA。它把一张图需要的造型、动作、环境和摄影语言打包成可复用预设，避免每增加一种需求就增加一个节点。

## 最简用法

将 `Character Visual Blueprint / 角色画面蓝图` 接在完整身份链路的最后：

```text
Face DNA Seed Generator / Parametric Face Designer
  → Body DNA Seed Generator（可选）
  → Parametric Body Designer（可选，可串联）
  → Character Visual Blueprint
```

画布上只显示两个设置：

- `blueprint`：整套画面方向；内置键 `identity_only` 在界面显示为“默认人像”，会组合唯一的默认表现层预设。
- `variant_seed`：从该蓝图的 Seed 变化中稳定选择一条。相同蓝图与种子始终得到同一结果，并支持生成后固定、递增、递减或随机。

节点另外输出 `negative_prompt` 与 `negative_prompt_zh`。每套蓝图可维护自己的中英文负向提示词；未填写时输出空字符串。

输出顺序是：

```text
完整身份 → Outfit → Expression & Pose → Scene → Photography
         → Seed 变化 → Fixed quality phrases
```

固定质量词放在最前或最后，仍由基础词库的 `Fixed quality position` 控制。

## 四类可复用图层

- `Outfit / 穿搭`：服装、材质、发型、配饰和妆容。
- `Expression & Pose / 表情跟姿态`：动作、姿态、表情、视线和情绪。
- `Scene / 场景`：地点、空间关系、环境物件和氛围细节。
- `Photography / 摄影`：镜头、视角、构图、景深、光线、色彩和画面质感。

图层本身不包含角色的长期身份结构。身份由前面的 Face / Body DNA 节点提供。

## 默认内容

- `identity_only`：界面显示为“默认人像”，组合默认穿搭、默认表情跟姿态、默认场景和默认摄影。
- Outfit、Expression & Pose、Scene、Photography 各只保留一套内置默认预设。
- 外观辨识特征只保留 `oriental_clear_beauty` 一套内置默认。

需要更多风格时可在词库面板自行添加；所有“添加”入口位于对应列表顶部，新增内容不会要求增加节点。

## 在界面修改

1. 打开 ComfyUI 左侧的 **CharacterDNA Vocabulary**。
2. 在 **Distinctive Appearance Features / 外观辨识特征** 中维护会被所有身份提示词继承、用于增强角色辨识度的瞳色、肤色、发型和自然标记。
3. 在 **Visual Blueprints / 画面蓝图** 中编辑显示名称、正负向提示词和 Seed 变化。
4. 展开 **Advanced layer stack / 高级图层栈**，添加、删除、排序或停用图层。
5. 在 Outfit、Expression & Pose、Scene、Photography 标签页维护可复用预设。
6. 点击保存，再完整运行工作流。

每个预设都有中文显示名、英文显示名和稳定内部键。面板会根据 ComfyUI 当前语言显示对应名称，在蓝图的图层下拉菜单中也使用当前语言；内部键会以小字保留，便于导出 JSON 后准确定位。

每个蓝图图层支持四种合并方式：

- `replace`：替换该类别之前的内容，适合蓝图中的主要选择。
- `append`：在同类内容后继续追加。
- `merge`：追加并自动去重。
- `clear`：清空该类别已累积的内容。

## 自由组合

画面蓝图不检查或推断年龄。无论 `visual_age` 的数值是多少，或身份提示词使用“少女”等不明确表达，所选 Outfit、Expression & Pose、Scene、Photography 都会正常组合，不会跳过任何图层。年龄表达只由身份 DNA 本身决定。

## 从旧节点升级

新版节点 ID 为 `CharacterDNAVisualBlueprint`，不保留旧版 `Clothing & Scene Composer` 的隐藏输入或自动迁移代码。旧工作流中删除原节点，添加一次新的角色画面蓝图节点并重新连线即可。旧词库中的自定义内容可在新版面板的 Outfit 或 Scene 页重新建立。
