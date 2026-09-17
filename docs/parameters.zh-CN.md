# CharacterDNA 参数手册

## 坐标含义

19 个 Feature 都使用 `-1.0 ～ +1.0` 的连续坐标：

- `-1`：明显偏向负方向。
- `-0.5`：轻度偏向负方向。
- `0`：中性基线，同时表示不指定该结构，不输出对应 Feature 提示词。
- `+0.5`：轻度偏向正方向。
- `+1`：明显偏向正方向。

正负号只代表结构方向，不代表好坏、美丑或质量。参数改变的是身份结构，妆容、发型、表情、姿势和灯光应由其他提示词控制。Seeder 产生连续值时，最接近 `0` 档的数值保留在 DNA 中，但不输出“均衡”提示词。

如果某个 Composite 组的来源参数全部为 `0`，该组不会输出“均衡”描述；19 项全部为 `0` 时，结构提示词和 Composite anchors 都为空，只保留基础身份、年龄与固定质量词。

## 19 个 Feature

| 分组 | 参数 | `-1` 方向 | `0` | `+1` 方向 | 所属 Composite |
|---|---|---|---|---|---|
| 脸部 | `face_length` | 明显较短的面部比例 | 均衡脸长 | 明显较长的面部比例 | Facial Silhouette |
| 脸部 | `face_width` | 明显较窄的脸 | 均衡脸宽 | 明显较宽的脸 | Facial Silhouette |
| 脸部 | `cheekbone_width` | 窄、较收的颧骨 | 均衡颧宽 | 宽且突出的颧骨 | Facial Silhouette |
| 脸部 | `jaw_width` | 窄而收尖的下颌 | 均衡下颌 | 宽而有力的下颌 | Facial Silhouette |
| 脸部 | `chin_width` | 窄下巴 | 均衡下巴宽度 | 宽下巴 | Facial Silhouette |
| 脸部 | `chin_length` | 短而紧凑的下巴 | 均衡下巴长度 | 较长的下巴 | Facial Silhouette |
| 眼部 | `eye_elongation` | 圆、横向较短的眼型 | 均衡杏眼 | 横向细长的眼型 | Eye Geometry、Brow–Eye Relationship 显著度 |
| 眼部 | `eye_openness` | 窄、开合较小 | 均衡开合 | 开合较大、较圆睁 | Eye Geometry、Brow–Eye Relationship 显著度 |
| 眼部 | `eye_spacing` | 近眼距 | 均衡眼距 | 宽眼距 | Eye Geometry |
| 眼部 | `canthal_tilt` | 外眼角向下 | 接近水平 | 外眼角向上 | Eye Geometry |
| 眉眼 | `brow_eye_distance` | 眉眼距离紧凑 | 均衡眉眼距离 | 眉眼距离舒展 | Brow–Eye Relationship |
| 鼻部 | `nose_width` | 窄鼻 | 均衡鼻宽 | 宽鼻 | Nose Profile |
| 鼻部 | `nose_length` | 短鼻 | 均衡鼻长 | 长鼻 | Nose Profile |
| 鼻部 | `nose_projection` | 鼻部较平、投影较低 | 均衡立体度 | 鼻部更立体、更突出 | Nose Profile |
| 鼻部 | `nose_tip_rotation` | 鼻尖向下 | 中性鼻尖方向 | 鼻尖向上 | Nose Profile |
| 嘴唇 | `mouth_width` | 窄嘴 | 均衡嘴宽 | 宽嘴 | Lip Relationship |
| 嘴唇 | `upper_lip_fullness` | 上唇较薄 | 均衡上唇 | 上唇丰满 | Lip Relationship |
| 嘴唇 | `lower_lip_fullness` | 下唇较薄 | 均衡下唇 | 下唇丰满 | Lip Relationship |
| 嘴唇 | `cupid_bow_definition` | 唇峰柔和、不明显 | 均衡唇峰 | 唇峰清晰、明确 | Lip Relationship |

## 常见关系

Composite 会看参数之间的关系，而不是机械拼接单项词语：

- `face_length` 高、`face_width` 低：修长感会同时增强。
- `face_length` 高、`face_width` 也高：脸长仍存在，但宽度会削弱修长观感。
- `face_width` 很窄、`jaw_width` 很宽：属于较强结构冲突，高 `harmony` 会柔化宽下颌。
- `upper_lip_fullness` 与 `lower_lip_fullness` 一正一负：Composite 会表达为上下唇的对比关系。
- `eye_elongation` 与 `eye_openness` 共同决定细长、杏眼或圆睁的整体观感。
- `brow_eye_distance` 决定眉眼关系的主要方向；眼型和开合度只参与该组显著度。

## Face DNA Seed Generator 参数

### `seed`

决定 19 个 Feature 的原始方向、数值和主要身份特征。同一个基础身份使用相同的 `seed`、`distinctiveness` 和 `harmony`，结果可重复。

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

## Composite 参数

### `max_composites`

现有系统计算 5 组 Composite，再按 `salience × identity importance` 排序。该参数控制排名最前的 N 组使用整体关系描述：

- `1–2`：只有最显著分组使用整体关系描述；其他分组退回非中性的逐项 Feature 描述。
- `3`：三组使用整体关系，其余结构仍以 Feature 形式保留。
- `5`：全部五组都使用自然关系描述，推荐默认值。

Composite 使用混合输出：已选分组会补回没有被关系语句充分表达、绝对值达到 `0.5` 的强显著 Feature；未选分组会补回所有非中性 Feature。它只改变语言组织方式，不删除或覆盖 `parametric_identity.features` 中的任何数值。`composite_identity_v4.hybrid_residual_features` 会记录实际补回的参数名。

## 多参数调整方法

Parametric Face Designer 每个节点只覆盖一个 Feature，并继承输入 DNA 中其余 18 个值。修改多个参数时按顺序串联：

```text
Face DNA Seed Generator
  → Parametric: face_length = 0.5
  → Parametric: jaw_width = -0.5
  → Parametric: canthal_tilt = 0.5
  → Face Composite Identity
```

同一个 Feature 被修改多次时，后面的节点覆盖前面的值。
