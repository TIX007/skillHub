# AI提示词工程规范与模型适配

## 提示词组装公式

### 文生图提示词组装

```
[画风前缀] + [场景资产描述] + [人物资产描述] + [动作与表情] + [构图与光影] + [画质参数] + [画幅参数]
```

各部分均从资产库模板自动填充，变量替换规则：

| 变量 | 来源 | 示例 |
|------|------|------|
| {appearance} | 人物资产.appearance | 清冷鹅蛋脸，黑长直长发及腰，杏眼 |
| {costume} | 人物资产.costume（按场景选择） | 酒红色缎面吊带长裙+银色细高跟 |
| {emotion} | 情绪脚本匹配的emotion_tags | 嘴角微扬，眼神下垂（smug） |
| {action} | 动作脚本提取 | 右手举起红酒杯，手腕翻转 |
| {lighting} | 场景资产.lighting | 暖金色主光+冷白补光 |
| {atmosphere_color} | 场景资产.atmosphere_color | 暖金色调 |
| {fixtures} | 场景资产.fixtures | 水晶吊灯，圆形宴会桌阵 |
| {context} | 道具资产.prompt_template变量 | 泼洒状态，液体飞溅 |

### 图生视频提示词组装

```
[主体动作（精简）] + [运镜动态] + [环境氛围变化] + [稳定性约束]
```

**核心原则**：图生视频提示词必须精简，只描述动态变化要素，静态要素由首帧图片承载。

---

## 画风前缀库

| 画风 | 前缀提示词 | 适用题材 |
|------|------------|----------|
| 真人写实风 | photorealistic, real person, cinematic lighting, 8K, DSLR photography | 都市逆袭、战神赘婿、悬疑推理 |
| 古风二次元 | anime style, ancient Chinese aesthetic, soft coloring, detailed line art | 古风甜宠、仙侠玄幻 |
| 漫画分镜风 | manga style, screentone, black and white ink, dynamic panel | 漫剧改编 |
| 电影质感 | cinematic, film grain, anamorphic lens, color graded | 所有题材的高质感版本 |
| 国风水墨 | Chinese ink painting style, traditional aesthetic, brush stroke | 古风仙侠、武侠 |

---

## 画质参数标准

### 通用画质参数

```
highly detailed, sharp focus, professional photography, no artifacts, no blur, 8K resolution
```

### 竖屏画幅参数

```
vertical composition, 9:16 aspect ratio, portrait orientation, full frame
```

### 真人写实风附加

```
realistic skin texture, natural lighting, depth of field, bokeh background
```

### 二次元附加

```
clean line art, vibrant colors, cel shading, high quality anime art
```

---

## 负面提示词模板

### 全局通用负面（全项目复用）

```
deformed, disfigured, extra limbs, extra fingers, mutated hands, bad anatomy, bad proportions, face distortion, blurry face, missing limbs, fused limbs, watermark, text, logo, low quality, jpeg artifacts, oversaturated, unnatural skin
```

### 真人写实风附加负面

```
anime style, cartoon, 3d render, plastic skin, waxy face, uncanny valley, overly smooth skin
```

### 二次元附加负面

```
realistic, photo, 3d render, live action, detailed skin texture, pores
```

### 图生视频附加负面

```
morphing, warping, flickering, unstable, jitter, ghosting, tearing, distortion over time
```

---

## 模型适配语法

### 可灵（Kling）适配

- 文生图：使用英文逗号分隔短语，避免长句
- 图生视频：动作描述前置，运镜描述后置
- 支持参数：`--ar 9:16`（画幅）、`--quality high`（画质）
- 示例：`young woman, red evening dress, holding wine glass, smug expression, close-up shot, warm golden lighting, luxury banquet hall background, photorealistic --ar 9:16 --quality high`

### Seedance 适配

- 文生图：中文描述+英文关键词混合
- 图生视频：强调动作幅度控制词"轻微""缓慢"
- 示例：`年轻女性，酒红色晚礼服，举起红酒杯，得意的表情，特写镜头，暖金色灯光 --ar 9:16`

### Runway 适配

- 文生图：英文提示词，使用 `style:` 和 `camera:` 前缀分类
- 图生视频：使用 `motion:` 前缀描述动态
- 示例：`style: photorealistic, a young woman in red dress holding wine glass, smug expression, camera: close-up shot, warm golden lighting, motion: slow hand movement`

### Stable Diffusion 适配

- 文生图：标准英文提示词，使用括号加权
- 权重语法：`(young woman:1.2), (red dress:1.1), holding wine glass`
- 负面提示词：放在 Negative Prompt 区域

---

## 提示词质量自检清单

每条提示词生成后，自动检查以下项目：

| 检查项 | 要求 | 不通过处理 |
|--------|------|------------|
| 资产引用 | 人物/场景/道具ID正确关联 | 重新匹配资产档案 |
| 变量替换 | 所有{变量}已替换为具体值 | 补充缺失资产描述 |
| 画风一致性 | 同项目同画风前缀 | 统一画风前缀 |
| 画幅参数 | 包含9:16竖屏标识 | 追加画幅参数 |
| 负面提示词 | 包含全局负面项 | 追加负面提示词 |
| 动作复杂度 | 图生视频单镜头动作≤2个 | 拆分为多镜头 |
| 禁用词 | 无"氛围感""高级感"等模糊词 | 替换为具体参数 |
| 模型适配 | 语法格式符合目标模型 | 调整语法结构 |

---

## 禁用词替换表

| 禁用词 | 替换为 |
|--------|--------|
| 氛围感 | 具体色调参数（如"暖金色调，色温3200K"） |
| 高级感 | 具体构图+光影术语（如"伦勃朗侧光，前后景分层虚化"） |
| 质感超强 | 具体材质+帧率（如"写实肌肤纹理，24帧标准帧率"） |
| 很精致 | "无过度曝光，画面干净，细节清晰" |
| 极度好看 | 具体视觉参数组合 |
| 动感 | 具体运镜动词（推/拉/移/摇/跟/环绕） |
| 有故事感 | 具体表情+肢体语言描述 |
