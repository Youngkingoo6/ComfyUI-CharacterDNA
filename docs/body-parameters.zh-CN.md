# 身体 DNA 参数说明

身体 DNA 使用 20 个连续参数描述稳定的身体比例。每项范围为 `-1` 到 `+1`，Parametric 界面以 `0.1` 步进并保留 1 位小数，`0` 是中性基线且不输出提示词。词库默认统一为 `-1、-0.6667、-0.3333、0、0.3333、0.6667、1` 七档中英文语义，连续数值会使用最接近的词条；最接近 `0` 档时保留 DNA 数值，但省略“均衡”词条。

这些参数只描述长期稳定的骨架、比例和体量，不包含姿势、服装、镜头、体重数字或私密身体细节。

## 20 个 Feature

| 分组 | 参数 | -1 方向 | +1 方向 |
|---|---|---|---|
| 骨架 | `stature` | 紧凑 | 高挑 |
| 骨架 | `shoulder_width` | 窄肩 | 宽肩 |
| 骨架 | `shoulder_slope` | 平直方肩 | 斜肩 |
| 骨架 | `ribcage_width` | 窄胸廓 | 宽胸廓 |
| 骨架 | `pelvis_width` | 窄骨盆 | 宽骨盆 |
| 躯干 | `neck_length` | 短颈 | 长颈 |
| 躯干 | `neck_thickness` | 纤细 | 厚实 |
| 躯干 | `torso_length` | 短躯干 | 长躯干 |
| 躯干 | `chest_fullness` | 平坦胸部轮廓 | 饱满胸部轮廓 |
| 躯干 | `waist_definition` | 平直腰线 | 明显腰线 |
| 躯干 | `hip_fullness` | 清瘦臀胯 | 饱满臀胯 |
| 四肢 | `arm_length` | 短手臂 | 长手臂 |
| 四肢 | `hand_scale` | 小手 | 大手 |
| 四肢 | `leg_length` | 短腿 | 长腿 |
| 四肢 | `thigh_length_ratio` | 紧凑大腿比例 | 修长大腿比例 |
| 四肢 | `foot_scale` | 小足部 | 大足部 |
| 体型 | `upper_body_fullness` | 清瘦上身 | 厚实上身 |
| 体型 | `lower_body_fullness` | 清瘦下身 | 厚实下身 |
| 体型 | `limb_thickness` | 纤细四肢 | 厚实四肢 |
| 体型 | `muscularity` | 柔和、低肌肉感 | 结实、运动型 |

## 节点使用

- `Body DNA Seed Generator`：`body_profile=seeded` 时，用 `body_seed + distinctiveness + harmony` 确定性生成 20 项身体参数；也可选择固定组合预设，并输出继承面部/基础身份后的完整提示词。
- `Parametric Body Designer`：覆盖一个参数并继承面部、基础身份和其他身体值；调整多项时串联多个节点。它的提示词输出是完整身份，不只是当前修改的单项身体词。

## 身体组合预设

组合预设不会增加新的身体参数，只是一次写入一组现有参数：

| `body_profile` | 用途 |
|---|---|
| `seeded` | 按种子、独特度和协调度生成可复现的随机身体 DNA |
| `balanced` | 20 项全部归零，不输出身体结构词 |
| `petite` | 紧凑身高、较窄骨架、小手足和偏纤细体量 |
| `athletic` | 较宽肩背、略长四肢和清晰运动型肌肉感 |
| `curvy` | 较宽骨盆、明显腰线，以及更饱满的胸部和臀胯轮廓 |
| `slender_tall` | 高挑身高、修长四肢、窄体量和纤细轮廓 |

选择固定组合时，`body_seed`、`distinctiveness` 和 `harmony` 不再改变预设参数；如需个性化，继续串联 Parametric Body Designer 覆盖任意单项。

身体提示词使用“窄肩、腿稍长、腰线明显、运动型身材”这类直接表达，不再附加比值锚点，也不再经过 Composite 改写。

面部 seed 与身体 seed 相互独立，因此可以固定面孔，只随机寻找身体比例；也可以固定身体，只变化面孔。
