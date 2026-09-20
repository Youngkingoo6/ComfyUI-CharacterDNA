# 表型校准与筛选

## 工作流

`Character DNA → 批量生成 → Batch Phenotype Analyzer → Directional Candidate Selector`

分析器必须接收生成后的同一个图片批次。筛选器的 `images` 与 `phenotype_dataset` 也必须来自该批次，节点会使用 `batch_index` 返回 `top_images` 和 `pareto_images`。

## 两种分数

- `relative_directional_index`：候选在当前批次中是否朝 DNA 指定方向靠近。
- `calibrated_match_index`：目标比例匹配占 65%，批内方向占 35%，作为最终排序依据。

目标比例不是身份概率，也不是固定的人类学标准。它们是可编辑的工作流初始校准值。打开 **CharacterDNA Vocabulary → Face Features**，可为可测量特征修改：

- `negative_target`：DNA = -1 时的目标。
- `baseline_target`：DNA = 0 时的目标。
- `positive_target`：DNA = +1 时的目标。
- `tolerance`：允许误差尺度；越小越严格。

中间 DNA 值使用分段线性插值，例如 `+0.5` 位于基线与 `+1` 目标的中点。

## 当前可测量范围

可校准：眼形横纵比、眼睛开合、眼距、眼角倾斜、眉眼距离、鼻宽、鼻长、嘴宽、上下唇厚度、唇峰。

暂不输出伪精确目标：鼻部前向投影、鼻尖旋转、脸长、脸宽、颧骨、下颌和下巴。这些项目需要三维/侧脸信息或先完成轮廓点语义校准。

`capture_quality` 另外输出眼线倾斜和双眼宽高不对称度，用于识别歪头、侧转或表情干扰，不直接冒充 DNA 特征。

## Pareto 集合

`pareto_images` 保留不存在“所有有效特征都更差”的候选。它适合人工复核多种折中方案；`top_images` 则按综合分直接返回前 N 名。
