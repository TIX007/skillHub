# 完整输出示例（都市逆袭之千金归来）

以下为基于调用示例的完整输出演示，展示全部7项产物的实际内容。

---

## 产物1：项目总览.md

```markdown
# 项目总览：都市逆袭之千金归来

## 基础信息

| 项目 | 内容 |
|------|------|
| 项目名称 | 都市逆袭之千金归来 |
| 题材类型 | 都市逆袭 |
| 目标平台 | 抖音 |
| 单集时长 | 60秒 |
| 视觉画风 | 真人写实风 |
| 计划集数 | 3集 |
| 创建日期 | 2026-08-26 |

## 分集大纲

### 第1集：逐出家门
女主林晚被继妹苏曼陷害，诬其偷取家族传承玉佩。父亲林国栋不分青红白，当众宣布与林晚断绝父女关系。林晚含泪离开林家，雨中背影渐行渐远。
- 核心冲突：诬陷 vs 清白
- 爽点：无（铺垫集，制造同情）
- 结尾钩子：林晚回头望向林家大门，眼神从悲伤转为冰冷

### 第2集：王者归来
三年后，铭晟集团新任总裁神秘亮相行业晚宴。继妹苏曼试图攀附，不知此人正是当年的林晚。宴会全程林晚未摘墨镜，直到苏曼当众炫耀当年的"正义之举"。
- 核心冲突：身份揭示前的信息不对称
- 爽点：身份悬念+苏曼的浑然不知
- 结尾钩子：林晚缓缓摘下墨镜，嘴角微扬

### 第3集：当众打脸
林晚当众亮明身份，宣布收购林氏产业。苏曼震惊跪地求饶，林国栋灰白面色赶来赔罪。林晚冷声宣布：从今天起，林氏改姓铭晟。
- 核心冲突：反转 vs 接受
- 爽点：身份反转打脸、继妹跪地、父亲赔罪
- 结尾钩子：林晚转身离去，镜头拉远，林家大门牌匾被工作人员摘下

## 核心冲突与爽点排布

| 集数 | 冲突类型 | 爽点类型 | 情绪曲线 |
|------|----------|----------|----------|
| 1 | 诬陷驱动 | 无（压抑铺垫） | 低谷 |
| 2 | 身份悬念 | 悬念积累+信息差爽感 | 上升 |
| 3 | 反转打脸 | 身份反转+跪地+收编 | 爆发峰值 |
```

---

## 产物2：人物资产库.json

```json
{
  "project": "都市逆袭之千金归来",
  "characters": [
    {
      "character_id": "char_001",
      "name": "林晚",
      "role": "女主",
      "age": "22岁（第1集）/25岁（第2-3集）",
      "appearance": "清冷鹅蛋脸，黑长直长发及腰，杏眼，鼻梁挺直，肤色白皙，身高168cm，体型纤瘦",
      "costume": {
        "ep01_rain": "白色棉质T恤+浅蓝牛仔裤+白色帆布鞋，被雨水打湿贴身",
        "ep02_banquet": "黑色定制西装套装+黑色墨镜+银色尖头高跟鞋，头发盘成低马尾",
        "ep03_reveal": "酒红色缎面吊带长裙外搭黑色西装外套+银色细高跟+珍珠耳坠，长发披散"
      },
      "personality": "外冷内热，坚韧冷静，复仇时从容不迫",
      "signature_expression": "微微眯眼，嘴角轻抿后缓缓上扬",
      "voice_feature": "低沉清冷女声，语速偏慢，字字清晰",
      "emotion_tags": {
        "wronged": "眼眶泛红，嘴唇紧抿，下颌微颤",
        "calm_composed": "面无表情，目光平视，脊背挺直",
        "smug": "嘴角微扬，眼神下垂，下巴微抬",
        "cold_anger": "眉头微蹙，下颌线收紧，目光如刀"
      },
      "prompt_template": "young woman, {age}, {appearance}, wearing {costume}, {emotion}, {action}, vertical 9:16 composition, photorealistic, cinematic lighting",
      "negative_prompt": "deformed, disfigured, extra limbs, extra fingers, mutated hands, bad anatomy, face distortion, blurry face, anime style, cartoon, low quality",
      "tags": ["清冷", "职场", "逆袭", "黑长直", "女主"]
    },
    {
      "character_id": "char_002",
      "name": "苏曼",
      "role": "反派-继妹",
      "age": "20岁（第1集）/23岁（第2-3集）",
      "appearance": "甜美圆脸，栗色波浪卷发及肩，桃花眼，樱桃小嘴，肤色偏粉白，身高162cm，身材凹凸有致",
      "costume": {
        "ep01_home": "粉色蕾丝连衣裙+白色平底鞋",
        "ep02_banquet": "香槟金色亮片短裙+裸色高跟鞋+钻石项链",
        "ep03_kneel": "香槟金色亮片短裙（裙摆凌乱），高跟鞋掉落一只"
      },
      "personality": "虚荣嫉妒，表面甜美内心狠毒，得志猖狂失势崩溃",
      "signature_expression": "歪头微笑（伪装甜美）/ 瞳孔放大嘴唇颤抖（崩溃）",
      "voice_feature": "甜美高音女声，语速快，情绪激动时尖锐刺耳",
      "emotion_tags": {
        "smug_jealous": "歪头微笑，眼底带嫉恨",
        "panic_shocked": "瞳孔放大，嘴唇颤抖，脸色惨白",
        "desperate_kneel": "泪流满面，膝盖弯曲，双手合十"
      },
      "prompt_template": "young woman, {age}, {appearance}, wearing {costume}, {emotion}, {action}, vertical 9:16 composition, photorealistic, cinematic lighting",
      "negative_prompt": "deformed, disfigured, extra limbs, extra fingers, mutated hands, bad anatomy, face distortion, blurry face, anime style, cartoon, low quality",
      "tags": ["反派", "继妹", "虚荣", "波浪卷"]
    },
    {
      "character_id": "char_003",
      "name": "林国栋",
      "role": "配角-女主父亲",
      "age": "50岁",
      "appearance": "国字脸，灰白短发，浓眉，法令纹深，肤色偏黄，身高175cm，微胖",
      "costume": {
        "ep01_home": "深灰色家居毛衣+黑色长裤",
        "ep03_apologize": "藏蓝色商务西装+白色衬衫，领带松垮歪斜"
      },
      "personality": "偏信偏听，强势固执，后悔时卑微",
      "emotion_tags": {
        "furious": "眉头紧锁，面红耳赤，手指颤抖",
        "regretful": "面色灰白，嘴唇哆嗦，肩膀垮塌"
      },
      "prompt_template": "middle-aged man, 50 years old, {appearance}, wearing {costume}, {emotion}, {action}, vertical 9:16 composition, photorealistic",
      "negative_prompt": "deformed, disfigured, extra limbs, bad anatomy, face distortion, blurry, anime style, low quality",
      "tags": ["父亲", "偏信", "后悔"]
    }
  ]
}
```

---

## 产物3：场景资产库.json

```json
{
  "project": "都市逆袭之千金归来",
  "scenes": [
    {
      "scene_id": "loca_001",
      "name": "林家客厅",
      "space_type": "室内-豪华别墅客厅",
      "time_weather": "夜晚，暴雨，室内暖灯",
      "lighting": "暖黄主光+窗外闪电冷白补光，明暗比2:1，闪电时瞬间3:1",
      "atmosphere_color": "暖黄基调，闪电时冷白冲击",
      "fixtures": ["真皮沙发", "大理石茶几", "家族合影框", "水晶花瓶", "实木展示柜"],
      "linked_props": ["prop_002"],
      "prompt_template": "luxury villa living room, {lighting}, {atmosphere_color}, furnishings: {fixtures}, nighttime, thunderstorm outside window, vertical 9:16 composition, photorealistic",
      "negative_prompt": "outdoor elements, natural light, simple furnishings, blank walls",
      "tags": ["别墅", "客厅", "夜景", "暴雨"]
    },
    {
      "scene_id": "loca_002",
      "name": "雨中街道",
      "space_type": "室外-城市街道",
      "time_weather": "夜晚，暴雨，路灯照明",
      "lighting": "路灯暖黄主光+雨水反射冷光，整体偏暗，水面反光",
      "atmosphere_color": "冷暗色调，局部暖光点缀",
      "fixtures": ["路灯", "湿漉路面", "远处车辆尾灯", "积水反射"],
      "linked_props": [],
      "prompt_template": "city street at night, heavy rain, {lighting}, {atmosphere_color}, wet ground reflections, street lamps, distant car taillights, vertical 9:16 composition, photorealistic, cinematic",
      "negative_prompt": "daytime, sunny, indoor elements, bright lighting",
      "tags": ["室外", "街道", "雨夜", "城市"]
    },
    {
      "scene_id": "loca_003",
      "name": "宴会大厅",
      "space_type": "室内-大型宴会厅",
      "time_weather": "夜晚，室内恒温，灯光全开",
      "lighting": "暖金色主光+冷白补光，水晶吊灯顶光，整体明暗比3:1，人物面部柔光",
      "atmosphere_color": "暖金色调为主，局部冷光点缀，整体奢华明亮",
      "fixtures": ["水晶吊灯", "圆形宴会桌阵", "香槟塔", "红毯通道", "落地玻璃窗", "金色装饰墙"],
      "linked_props": ["prop_001", "prop_003"],
      "prompt_template": "grand banquet hall, {lighting}, {atmosphere_color}, furnishings: {fixtures}, nighttime, luxury event venue, vertical 9:16 composition, photorealistic, cinematic",
      "negative_prompt": "outdoor elements, natural light, simple furnishings, empty walls, daytime",
      "tags": ["宴会", "豪门", "夜景", "室内", "奢华"]
    }
  ]
}
```

---

## 产物4：道具资产库.json

```json
{
  "project": "都市逆袭之千金归来",
  "props": [
    {
      "prop_id": "prop_001",
      "name": "红酒杯",
      "appearance": "高脚水晶杯，杯身透明，内盛深红色液体约半杯，杯沿有水珠，高约20cm",
      "function": "宴会道具，打脸高潮时泼洒使用",
      "key_scenes": ["第3集-第2场"],
      "visual_tags": ["透明", "反光", "深红液体", "高脚", "水晶材质"],
      "prompt_template": "crystal wine glass, transparent body, filled with deep red liquid, water droplets on rim, tall stem, {context}",
      "negative_prompt": "plastic cup, paper cup, empty, opaque material",
      "tags": ["宴会", "打脸", "容器"]
    },
    {
      "prop_id": "prop_002",
      "name": "家族传承玉佩",
      "appearance": "椭圆形白玉佩，约5cm长，表面刻有龙纹浮雕，系红色丝绦，温润光泽",
      "function": "关键道具，诬陷事件的导火索",
      "key_scenes": ["第1集-第1场", "第3集-第1场"],
      "visual_tags": ["白色", "椭圆形", "浮雕", "丝绦", "温润光泽"],
      "prompt_template": "white jade pendant, oval shape, dragon relief carving, red silk cord, warm luster, {context}",
      "negative_prompt": "plastic, metal, modern design, no cord",
      "tags": ["玉佩", "传承", "诬陷道具"]
    },
    {
      "prop_id": "prop_003",
      "name": "总裁墨镜",
      "appearance": "黑色方框墨镜，镜片为渐变深灰，镜框哑光金属材质，大牌设计感",
      "function": "身份悬念道具，遮住面部制造悬念",
      "key_scenes": ["第2集-第1场", "第2集-第3场"],
      "visual_tags": ["黑色", "方框", "渐变镜片", "哑光金属", "大牌"],
      "prompt_template": "black square sunglasses, gradient dark grey lenses, matte metal frame, designer style, {context}",
      "negative_prompt": "round frame, colorful, plastic frame, clear lenses",
      "tags": ["墨镜", "悬念", "身份标识"]
    }
  ]
}
```

---

## 产物5：分镜执行表.csv

以下为第3集（打脸高潮集）的完整分镜表示例（12个镜头）：

| shot_id | scene | duration | shot_size | angle | movement | technique | visual_desc | action | dialogue | emotion | sound_effect | char_ids | scene_id | prop_ids | transition | txt2img_prompt |
|---------|-------|----------|-----------|-------|----------|-----------|-------------|--------|----------|---------|--------------|----------|----------|----------|-----------|-----------------|
| 3-01 | 3-1 | 4s | 特写 | 平视 | 推镜 | 主观视角 | 苏曼端着红酒杯在宴会厅与人寒暄，得意洋洋 | 右手举杯晃动，左手叉腰，身体微晃 | "三年了，当年那个小偷终于不会再出现了" | smug_jealous | 背景宴会嘈杂声 | char_002 | loca_003 | prop_001 | 硬切 | young woman, 23, sweet round face, chestnut wavy hair, wearing champagne gold sequin dress, smug expression with jealousy in eyes, holding wine glass, close-up shot, push-in, warm golden lighting, luxury banquet hall, vertical 9:16, photorealistic |
| 3-02 | 3-1 | 3s | 中景 | 平视 | 固定 | 过肩 | 从苏曼身后过肩拍摄，背景中一个黑色西装身影缓步入场 | 苏曼未察觉，继续说笑 | （无台词） | 未知（背景人物） | 高跟鞋踏地声 | char_002 | loca_003 | | 硬切 | medium shot, over-shoulder, champagne dress woman foreground blurred, black suit figure entering background, static camera, warm golden lighting, banquet hall, vertical 9:16, photorealistic |
| 3-03 | 3-1 | 5s | 全景 | 仰拍 | 推镜 | 固定 | 林晚着黑色西装墨镜缓步走入宴会大厅，众人侧目 | 稳步前行，双手自然下垂，脊背挺直，下巴微抬 | （无台词，背景嘈杂渐静） | calm_composed | 高跟鞋声渐近+背景骤静 | char_001 | loca_003 | prop_003 | 硬切 | full shot looking up, young woman in black suit and sunglasses walking calmly into banquet hall, crowd turning to look, push-in camera, warm golden lighting, luxury venue, vertical 9:16, photorealistic, cinematic |
| 3-04 | 3-1 | 3s | 特写 | 平视 | 固定 | 固定 | 苏曼转身看到来人，表情从得意骤变震惊 | 转身动作，手中酒杯微倾，瞳孔放大 | "你…你怎么可能……" | panic_shocked | 酒杯碰撞声 | char_002 | loca_003 | | 硬切 | close-up, young woman, sweet face turning from smug to shocked, eyes widened, lips trembling, close-up shot, static camera, warm golden lighting, banquet hall, vertical 9:16, photorealistic |
| 3-05 | 3-1 | 5s | 中景 | 平视 | 固定 | 正反打 | 林晚缓缓解下墨镜，露出冷漠面容，与苏曼四目相对 | 右手缓缓摘下墨镜，嘴角微扬 | "三年不见，继妹。过得不错？" | smug | 墨镜折叠声 | char_001, char_002 | loca_003 | prop_003 | 叠化 | medium shot, young woman removing sunglasses revealing cold calm face, slight smirk, eye contact with shocked woman, shot/reverse shot, static camera, warm golden lighting, vertical 9:16, photorealistic |
| 3-06 | 3-1 | 4s | 大特写 | 仰拍 | 推镜 | 固定 | 苏曼面部大特写，恐惧与不可置信交织 | 瞳孔剧烈收缩，嘴唇颤抖，脸色惨白 | "不……这不可能……" | desperate_kneel | 心跳声放大 | char_002 | loca_003 | | 硬切 | extreme close-up, young woman face, pupils contracted, lips trembling, face pale, fear and disbelief, low angle, slow push-in, warm golden lighting, vertical 9:16, photorealistic |
| 3-07 | 3-2 | 5s | 中景 | 平视 | 跟拍 | 固定 | 林晚从随从手中接过文件，缓步走向宴会中央舞台 | 右手持文件，左手背身后，步伐从容 | "各位，铭晟集团正式收购林氏产业，即日起生效。" | cold_anger | 文件展开声+背景议论声 | char_001 | loca_003 | | 硬切 | medium shot, tracking, young woman in red dress holding document walking to center stage, calm cold expression, warm golden lighting, banquet hall, vertical 9:16, photorealistic |
| 3-08 | 3-2 | 4s | 全景 | 俯拍 | 升降 | 空镜转场 | 宴会厅全景，众人震惊围观，苏曼踉跄后退 | 人群后退让出空间，苏曼后退两步 | （背景议论声） | 惊愕氛围 | 嘈杂议论声 | char_001, char_002 | loca_003 | | 硬切 | wide shot, high angle crane, banquet hall全景, crowd in shock, woman staggering backward, warm golden lighting, vertical 9:16, photorealistic |
| 3-09 | 3-2 | 4s | 特写 | 仰拍 | 固定 | 固定 | 苏曼双膝跪地，泪流满面，仰视林晚 | 膝盖弯曲触地，双手合十，身体前倾 | "姐姐……求你……我错了……" | desperate_kneel | 膝盖触地声+哭声 | char_002 | loca_003 | | 硬切 | close-up low angle, young woman kneeling on floor, tears streaming, hands clasped, looking up, desperate expression, warm golden lighting, banquet hall floor, vertical 9:16, photorealistic |
| 3-10 | 3-2 | 4s | 特写 | 平视 | 推镜 | 固定 | 林晚居高临下俯视苏曼，面无表情 | 双手交叉胸前，下颌微抬，目光下垂 | "三年前你让我跪着离开，今天，轮到你了。" | cold_anger | 寂静中高跟鞋声 | char_001 | loca_003 | | 硬切 | close-up, young woman arms crossed, chin raised, looking down with cold anger, slow push-in, warm golden lighting, vertical 9:16, photorealistic |
| 3-11 | 3-3 | 5s | 全景 | 平视 | 拉镜 | 固定 | 林国栋匆忙跑入宴会厅，面色灰白，领带歪斜 | 跑步入场，急停踉跄，双手前伸 | "晚晚……是爸爸错了……" | regretful | 急促脚步声 | char_003 | loca_003 | | 硬切 | full shot, pull-back, middle-aged man rushing in, gray face, tilted tie, arms reaching forward, regretful expression, warm golden lighting, banquet hall entrance, vertical 9:16, photorealistic |
| 3-12 | 3-3 | 6s | 全景 | 平视 | 拉镜→升降 | 空镜转场 | 林晚转身走向大门，镜头拉远升高，工作人员开始摘下"林氏集团"门牌 | 转身步伐从容离去，不回头 | "从今天起，这里姓铭晟。" | calm_composed | 高跟鞋声渐远+门牌拆卸声 | char_001 | loca_003 | | 黑场 | full shot, pull-back to crane up, young woman walking away toward door without looking back, workers removing sign plate, warm golden lighting, banquet hall, vertical 9:16, photorealistic, cinematic ending |

---

## 产物6：AI生成提示词集.md

以下为第3集镜头3-01和3-05的提示词示例：

### 镜头 3-01

**文生图提示词**：
```
young woman, 23 years old, sweet round face, chestnut wavy shoulder-length hair, peach blossom eyes, cherry lips, fair pink skin, wearing champagne gold sequin short dress and nude heels, smug expression with jealousy in eyes,歪头微笑 holding crystal wine glass in right hand, left hand on hip, close-up shot, eye-level angle, push-in camera, warm golden main light with cool white fill, crystal chandelier overhead, luxury banquet hall background, vertical 9:16 composition, photorealistic, cinematic lighting, 8K, DSLR photography, highly detailed, sharp focus
```

**图生视频提示词**：
```
static to slow push-in, woman holding wine glass swaying slightly, left hand on hip, body swaying, smug expression maintained, background banquet hall ambiance, warm golden lighting stable, slight head tilt movement
```

**负面提示词**：
```
deformed, disfigured, extra limbs, extra fingers, mutated hands, bad anatomy, bad proportions, face distortion, blurry face, missing limbs, fused limbs, watermark, text, logo, low quality, jpeg artifacts, oversaturated, unnatural skin, anime style, cartoon, 3d render, plastic skin
```

### 镜头 3-05

**文生图提示词**：
```
medium shot, young woman, 25 years old, cold oval face, black long straight hair to waist, almond eyes, fair skin, wearing black tailored suit jacket, removing black square sunglasses with right hand, slight smirk, cold calm expression, eye contact direction, close-up shot, shot/reverse shot composition, static camera, warm golden main light, crystal chandelier, luxury banquet hall background, vertical 9:16 composition, photorealistic, cinematic lighting, 8K, highly detailed, sharp focus, professional photography
```

**图生视频提示词**：
```
slow hand movement removing sunglasses, slight smirk appearing, head micro-tilt, eyes maintaining contact, static camera, warm golden lighting stable, background slightly blurred
```

**负面提示词**：
```
deformed, disfigured, extra limbs, extra fingers, mutated hands, bad anatomy, face distortion, blurry face, anime style, cartoon, 3d render, plastic skin, waxy face, oversaturated, low quality, morphing, warping, flickering
```

### 全局负面提示词（全项目复用）

```
deformed, disfigured, extra limbs, extra fingers, mutated hands, bad anatomy, bad proportions, face distortion, blurry face, missing limbs, fused limbs, watermark, text, logo, low quality, jpeg artifacts, oversaturated, unnatural skin, anime style, cartoon, 3d render, plastic skin, waxy face, uncanny valley, overly smooth skin, morphing, warping, flickering, unstable, jitter, ghosting, tearing
```

---

## 产物7：资产索引.json

```json
{
  "project_id": "drama_都市逆袭之千金归来_20260826",
  "project_name": "都市逆袭之千金归来",
  "created_at": "2026-08-26",
  "art_style": "真人写实风",
  "assets": {
    "characters": [
      { "id": "char_001", "name": "林晚", "role": "女主", "file": "人物资产库.json" },
      { "id": "char_002", "name": "苏曼", "role": "反派-继妹", "file": "人物资产库.json" },
      { "id": "char_003", "name": "林国栋", "role": "配角-父亲", "file": "人物资产库.json" }
    ],
    "scenes": [
      { "id": "loca_001", "name": "林家客厅", "file": "场景资产库.json" },
      { "id": "loca_002", "name": "雨中街道", "file": "场景资产库.json" },
      { "id": "loca_003", "name": "宴会大厅", "file": "场景资产库.json" }
    ],
    "props": [
      { "id": "prop_001", "name": "红酒杯", "file": "道具资产库.json" },
      { "id": "prop_002", "name": "家族传承玉佩", "file": "道具资产库.json" },
      { "id": "prop_003", "name": "总裁墨镜", "file": "道具资产库.json" }
    ]
  },
  "reuse_guide": "调用时传入 reuse_asset_ids: {characters: ['char_001','char_002'], scenes: ['loca_003']} 即可加载林晚、苏曼及宴会大厅的完整设定，无需重复描述"
}
```
