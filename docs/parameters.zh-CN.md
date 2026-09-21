# CharacterDNA 参数手册

## 坐标含义

24 个 Feature 都使用 `-1.0 ～ +1.0` 的连续坐标：

Parametric 节点的界面步进为 `0.1`，手动覆盖值保留 1 位小数；语义输出仍匹配最近的七档锚点。

- `-1`：极度偏向负方向。
- `-0.6667`：明显偏向负方向。
- `-0.3333`：轻度偏向负方向。
- `0`：中性基线，同时表示不指定该结构，不输出对应 Feature 提示词。
- `+0.3333`：轻度偏向正方向。
- `+0.6667`：明显偏向正方向。
- `+1`：极度偏向正方向。

正负号只代表结构方向，不代表好坏、美丑或质量。参数改变的是身份结构，妆容、发型、表情、姿势和灯光应由其他提示词控制。Seeder 产生连续值时，最接近 `0` 档的数值保留在 DNA 中，但不输出“均衡”提示词。

24 项全部为 `0` 时不输出面部结构词，只保留基础身份、年龄与固定质量词。

## 24 个 Feature

| 分组 | 参数 | `-1` 方向 | `0` | `+1` 方向 |
|---|---|---|---|---|
| 脸部 | `face_length` | 短脸 | 不输出 | 长脸 |
| 脸部 | `face_width` | 窄脸 | 不输出 | 宽脸 |
| 脸部 | `cheekbone_width` | 窄颧骨 | 不输出 | 宽颧骨 |
| 脸部 | `jaw_width` | 窄下颌 | 不输出 | 宽下颌 |
| 脸部 | `chin_width` | 窄下巴 | 不输出 | 宽下巴 |
| 脸部 | `chin_length` | 短下巴 | 不输出 | 长下巴 |
| 脸部 | `cheekbone_height` | 颧骨重心低 | 不输出 | 颧骨重心高 |
| 脸部 | `cheekbone_projection` | 颧骨轮廓平 | 不输出 | 颧骨轮廓突出 |
| 脸部 | `jawline_definition` | 下颌线柔和 | 不输出 | 下颌线清晰 |
| 眉毛 | `eyebrow_shape` | 平直眉 | 不输出 | 高挑弧形眉 |
| 眉毛 | `eyebrow_thickness` | 纤细稀疏眉 | 不输出 | 粗密饱满眉 |
| 眼部 | `eye_elongation` | 圆眼 | 不输出 | 细长眼 |
| 眼部 | `eye_openness` | 细眼 | 不输出 | 大眼睛 |
| 眼部 | `eye_spacing` | 近眼距 | 不输出 | 宽眼距 |
| 眼部 | `canthal_tilt` | 眼尾下垂 | 不输出 | 眼尾上扬 |
| 眉眼 | `brow_eye_distance` | 眉眼距离近 | 不输出 | 眉眼距离远 |
| 鼻部 | `nose_width` | 窄鼻 | 不输出 | 宽鼻 |
| 鼻部 | `nose_length` | 短鼻 | 不输出 | 长鼻 |
| 鼻部 | `nose_projection` | 鼻梁偏平 | 不输出 | 鼻梁挺 |
| 鼻部 | `nose_tip_rotation` | 鼻尖向下 | 不输出 | 鼻尖上翘 |
| 嘴唇 | `mouth_width` | 窄嘴 | 不输出 | 宽嘴 |
| 嘴唇 | `upper_lip_fullness` | 薄上唇 | 不输出 | 丰满上唇 |
| 嘴唇 | `lower_lip_fullness` | 薄下唇 | 不输出 | 丰满下唇 |
| 嘴唇 | `cupid_bow_definition` | 唇峰柔和 | 不输出 | 唇峰清晰 |

## 常见关系

Seed Generator 的 `harmony` 会在生成参数时处理明显冲突，例如：

- `face_length` 高、`face_width` 低：修长感会同时增强。
- `face_length` 高、`face_width` 也高：脸长仍存在，但宽度会削弱修长观感。
- `face_width` 很窄、`jaw_width` 很宽：属于较强结构冲突，高 `harmony` 会柔化宽下颌。
- `upper_lip_fullness` 与 `lower_lip_fullness` 一正一负：会形成上下唇厚度对比。
- `eye_elongation` 与 `eye_openness` 共同决定细长、杏眼或圆睁的整体观感。
- `brow_eye_distance` 决定眉眼关系的主要方向；眼型和开合度只参与该组显著度。

## Face DNA Seed Generator 参数

### `seed`

决定 24 个 Feature 的原始方向、数值和主要身份特征。同一个基础身份使用相同的 `seed`、`distinctiveness` 和 `harmony`，结果可重复。

`control after generate`：

- `fixed`：下一次仍使用当前 seed。
- `increment`：每次完整运行后加 1。
- `decrement`：每次完整运行后减 1。
- `randomize`：每次完整运行后产生新 seed。

生成后控制发生在任务入队之后，因此节点上显示的是“下一次运行”的 seed；刚完成的结果使用的是入队前的 seed。

### `distinctiveness`

控制身份结构偏离中性基线的强度，不改变 seed 决定的正负方向。

| 范围 | 建议理解 |
|---|---|
| `0.00–0.29` | 温和，约 2 个主要身份特征 |
| `0.30–0.49` | 较克制，约 3 个主要身份特征 |
| `0.50–0.69` | 中等，约 4 个主要身份特征 |
| `0.70–0.84` | 鲜明，约 5 个主要身份特征 |
| `0.85–1.00` | 强烈，约 6 个主要身份特征 |

### `harmony`

控制系统对冲突和极端组合的柔化程度：

- 高值：更协调、稳定，减少窄脸配极宽下颌等明显冲突。
- 低值：保留更多夸张、偶然性和极端组合。
- 它不是美感分数，也不会把所有参数拉回 0。

## 多参数调整方法

Parametric Face Designer 每个节点只覆盖一个 Feature，并继承输入 DNA 中其余 23 个值。修改多个参数时按顺序串联：

```text
Face DNA Seed Generator
  → Parametric: face_length = 0.3
  → Parametric: jaw_width = -0.3
  → Parametric: canthal_tilt = 0.3
  → 直接使用最后一个 Parametric 的提示词
```

同一个 Feature 被修改多次时，后面的节点覆盖前面的值。

### `weight`

只对当前节点修改的 Feature 进行提示词加权：

- `0`：关闭权重，输出原始特征描述，不增加括号。
- `1.0–2.0`：以 `0.1` 为步进，输出 `(特征描述:权重)`。
- 权重会和 Feature 一起写入 DNA，并由后续 Parametric Face Designer 继承。
- 后续节点再次选择同一 Feature 且把权重设为 `0`，会移除该 Feature 原来的权重。

例如：

```text
(slightly wide-set eyes with more visible space beside the nose bridge:1.2)
(双眼横向分布略微分开，鼻梁两侧留白较多:1.2)
```
