# 身体 DNA 参数说明

身体 DNA 使用 20 个连续参数描述稳定的身体比例。每项范围为 `-1` 到 `+1`，`0` 是中性基线且不输出提示词。词库默认提供 `-1、-0.5、0、0.5、1` 五档中英文语义，连续数值会使用最接近的词条；最接近 `0` 档时保留 DNA 数值，但省略“均衡”词条。

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

## 5 组 Composite

1. `overall_frame`：综合身高体量、肩宽、胸廓、骨盆、腰线和臀胯，描述整体轮廓。
2. `torso_architecture`：综合颈部、肩线、胸廓、躯干长度和胸部轮廓。
3. `limb_proportions`：综合手臂、手、腿、大腿比例和足部尺度。
4. `build_distribution`：综合上下身体量、四肢粗细和肌肉感。
5. `scale_balance`：描述四肢与整体骨架之间的尺度协调关系。

Composite 不是简单拼接 20 个单项词，而是先判断参数之间的相对关系，再输出自然的整体描述。某一组全部为 0 时，该组不输出。

## 节点使用

- `Body DNA Seed Generator`：用 `body_seed + distinctiveness + harmony` 确定性生成 20 项身体参数，并输出继承面部/基础身份后的完整提示词。
- `Parametric Body Designer`：覆盖一个参数并继承面部、基础身份和其他身体值；调整多项时串联多个节点。它的提示词输出是完整身份，不只是当前修改的单项身体词。
- `Body Composite Identity`：输出身体提示词，并额外输出已经合并面部与身体的完整身份提示词。

面部 seed 与身体 seed 相互独立，因此可以固定面孔，只随机寻找身体比例；也可以固定身体，只变化面孔。
