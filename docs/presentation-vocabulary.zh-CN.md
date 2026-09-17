# 服装与场景词库

服装和场景属于角色的可变表现层，不属于稳定的面部或身体 DNA。更换预设只改变最终提示词，不会修改任何 Face Feature、Body Feature、Seed 或 Composite。

## 使用节点

将 `Clothing & Scene Composer` 接在当前 DNA 链路的最后，推荐接在 `Body Composite Identity` 之后：

```text
Face / Body DNA
  → Face Composite Identity
  → Body Composite Identity
  → Clothing & Scene Composer
  → 完整中英文提示词
```

- `clothing`：选择服装预设；`none` 表示不添加服装。
- `scene`：选择场景预设；`none` 表示不添加场景。
- `complete_prompt`：身份、服装、场景及固定质量词组成的英文提示词。
- `complete_prompt_zh`：同一内容的中文提示词。

可以只选择服装、只选择场景，也可以同时选择。拼接顺序固定为：

```text
身份 DNA → 服装 → 场景 → Fixed quality phrases
```

如果固定质量词位置设置为“最前面”，节点会自动改为把质量词放在整条最终提示词最前面。

## 修改词库

打开 ComfyUI 左侧的 `CharacterDNA 词库` 面板：

1. 进入 `服装` 或 `场景` 标签页。
2. 直接修改预设的英文和中文提示词。
3. 点击“添加服装”或“添加场景”建立新预设；预设标识建议只使用小写英文、数字和下划线。
4. 点击“保存”。已经存在的组合节点下次执行会使用更新后的提示词。

新增或删除预设后，刷新 ComfyUI 页面即可让节点下拉列表同步更新。
