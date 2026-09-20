# 表型校准与筛选

## 工作流

`Character DNA → 批量生成 → Batch Phenotype Analyzer → Directional Candidate Selector`

分析器必须接收生成后的同一个图片批次。筛选器的 `images` 与 `phenotype_dataset` 也必须来自该批次，节点会使用 `batch_index` 返回 `top_images` 和 `pareto_images`。

## 两种分数

- `relative_directional_index`：候选在当前批次中是否朝 DNA 指定方向靠近。
- `calibrated_match_index`：目标比例匹配占 65%，批内方向占 35%，作为最终排序依据。

目标比例不是身份概率，也不是固定的人类学标准。它们是可编辑的工作流初始校准值。打开 **CharacterDNA Vocabulary → Face Features**，可为可测量特征修改：

- 7 个目标档位：`-1、-0.6667、-0.3333、0、0.3333、0.6667、1`。
- `tolerance`：允许误差尺度；越小越严格。
- 中英文测量提示词模板：使用 `{target}` 插入当前目标比例。

任意中间 DNA 值在相邻两档之间进行线性插值。例如眼距 `+0.3333 = 1.10`、`+0.6667 = 1.20`，则 `+0.5` 的目标为约 `1.15` 个平均眼宽。

可测量 Feature 会把目标写成相对于标准正面二维投影基准的完整关系，并说明保持不变的参照尺寸。例如：

```text
slightly wide-set eyes, target inner-canthal distance is approximately 1.1 times the average eye width; preserve average eye width and projected face width
眼距偏宽，目标内眦间距约为平均眼宽的1.1倍；保持平均眼宽和二维投影脸宽不变
```

DNA 为 `0` 时仍遵循极简规则：不输出该 Feature 的形容词，也不输出比例。

## 当前可测量范围

可校准：眼形横纵比、眼睛开合、眼距、眼角倾斜、眉眼距离、鼻宽、鼻长、嘴宽、上下唇厚度、唇峰。

暂不输出伪精确目标：鼻部前向投影、鼻尖旋转、脸长、脸宽、颧骨、下颌和下巴。这些项目需要三维/侧脸信息或先完成轮廓点语义校准。

`capture_quality.frontal_validation` 输出 InsightFace 3D 姿态估计和标准正面有效性。三庭五眼只在 `|pitch| ≤ 5°`、`|yaw| ≤ 5°`、`|roll| ≤ 3°` 时参与标准比较。眼尾到太阳穴使用眼睛中心高度与左右面部轮廓的二维交点，不使用全脸最宽点。缺少姿态数据或超过阈值时，诊断图显示 `NOT COMPARABLE`，避免把透视压缩误判为身份比例变化。

## Pareto 集合

`pareto_images` 保留不存在“所有有效特征都更差”的候选。它适合人工复核多种折中方案；`top_images` 则按综合分直接返回前 N 名。
