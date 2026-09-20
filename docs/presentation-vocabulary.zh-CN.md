# 角色画面蓝图与表现层词库

画面蓝图属于角色的可变表现层，不会修改稳定的面部或身体 DNA。它把一张图需要的造型、动作、环境和摄影语言打包成可复用预设，避免每增加一种需求就增加一个节点。

## 最简用法

将 `Character Visual Blueprint / 角色画面蓝图` 接在完整身份链路的最后：

```text
Face DNA Seed Generator / Parametric Face Designer
  → Body DNA Seed Generator（可选）
  → Body Composite Identity（可选）
  → Character Visual Blueprint
```

画布上只显示两个设置：

- `blueprint`：整套画面方向；`identity_only` 表示不添加表现层内容。
- `variant_seed`：从该蓝图的 Seed 变化中稳定选择一条。相同蓝图与种子始终得到同一结果，并支持生成后固定、递增、递减或随机。

节点另外输出 `negative_prompt` 与 `negative_prompt_zh`。每套蓝图可维护自己的中英文负向提示词；未填写时输出空字符串。

输出顺序是：

```text
完整身份 → Look → Performance → Scene → Photography
         → Seed 变化 → Fixed quality phrases
```

固定质量词放在最前或最后，仍由基础词库的 `Fixed quality position` 控制。

## 四类可复用图层

- `Look / 人物造型`：服装、材质、发型、配饰和妆容。
- `Performance / 表演`：动作、姿态、表情、视线和情绪。
- `Scene / 场景`：地点、空间关系、环境物件和氛围细节。
- `Photography / 摄影`：镜头、视角、构图、景深、光线、色彩和画面质感。

图层本身不包含角色的长期身份结构。身份由前面的 Face / Body DNA 节点提供。

## 默认蓝图

- `identity_only`：只保留身份。
- `quiet_luxury_studio`：静奢通勤造型与柔和 85mm 编辑人像。
- `classical_chinese_studio`：现代中式造型、古典室内和棚拍镜头。
- `bathroom_hair_drying_vlog`：浴室吹发动态与手机纪实镜头。
- `dark_cozy_bedroom`：暗调卧室、安静凝视与浪漫 HDR 氛围。
- `warm_minimal_bedroom_lifestyle`：暖色现代卧室里的手机生活方式画面。
- `golden_hour_coast`：海岸度假造型与金色时刻胶片感。
- `cool_jewelry_beauty_closeup`：清冷珠宝美妆大头特写、高调灰白棚拍与独立负向提示词。

## 在界面修改

1. 打开 ComfyUI 左侧的 **CharacterDNA Vocabulary**。
2. 在 **Identity Appearance / 稳定外观** 中维护会被所有身份提示词继承的瞳色、肤色、发色和辨识标记。
3. 在 **Visual Blueprints / 画面蓝图** 中编辑显示名称、正负向提示词和 Seed 变化。
4. 展开 **Advanced layer stack / 高级图层栈**，添加、删除、排序或停用图层。
5. 在 Look、Performance、Scene、Photography 标签页维护可复用预设。
6. 点击保存，再完整运行工作流。

每个蓝图图层支持四种合并方式：

- `replace`：替换该类别之前的内容，适合蓝图中的主要选择。
- `append`：在同类内容后继续追加。
- `merge`：追加并自动去重。
- `clear`：清空该类别已累积的内容。

## 自由组合

画面蓝图不检查或推断年龄。无论 `visual_age` 的数值是多少，或身份提示词使用“少女”等不明确表达，所选 Look、Performance、Scene、Photography 都会正常组合，不会跳过任何图层。年龄表达只由身份 DNA 本身决定。

## 从旧节点升级

新版节点 ID 为 `CharacterDNAVisualBlueprint`，不保留旧版 `Clothing & Scene Composer` 的隐藏输入或自动迁移代码。旧工作流中删除原节点，添加一次新的角色画面蓝图节点并重新连线即可。旧词库中的自定义内容可在新版面板的 Look 或 Scene 页重新建立。
