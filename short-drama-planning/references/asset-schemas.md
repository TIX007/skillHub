# 资产数据完整Schema与ID规范

## ID命名规范

所有资产ID遵循统一格式：`{type}_{三位序号}`，序号从001起递增。

| 资产类型 | ID前缀 | 示例 |
|----------|--------|------|
| 人物 | char_ | char_001, char_002 |
| 场景 | loca_ | loca_001, loca_002 |
| 道具 | prop_ | prop_001, prop_002 |

跨项目复用时，ID保持原值不变，通过资产索引中的 `source_project` 字段标记来源。

---

## 人物资产完整Schema

```json
{
  "character_id": "char_001",
  "name": "林晚",
  "role": "女主",
  "age": "22岁",
  "appearance": "清冷鹅蛋脸，黑长直长发及腰，杏眼，鼻梁挺直，肤色白皙，身高168cm，体型纤瘦",
  "costume": {
    "daily": "白色丝质衬衫+黑色高腰西装裤+黑色尖头高跟鞋",
    "banquet": "酒红色缎面吊带长裙+银色细高跟+珍珠耳坠",
    "business": "黑色收腰西装套装+白色内搭衬衫"
  },
  "personality": "外冷内热，坚韧冷静",
  "signature_expression": "微微眯眼，嘴角轻抿",
  "voice_feature": "低沉清冷女声，语速偏慢",
  "emotion_tags": {
    "calm": "面无表情，目光平视",
    "angry": "眉头微蹙，下颌线收紧",
    "smug": "嘴角微扬，眼神下垂",
    "shocked": "瞳孔微缩，嘴唇微张"
  },
  "prompt_template": "年轻女性，{age}，{appearance}，穿着{costume}，{emotion}表情，{action}，竖屏9:16构图",
  "negative_prompt": "畸形手指，面部崩坏，五官扭曲，多肢体，多余手指，模糊面部",
  "tags": ["清冷", "职场", "逆袭", "黑长直"]
}
```

### 字段说明

| 字段 | 必填 | 说明 |
|------|------|------|
| character_id | 是 | 唯一标识，格式 char_XXX |
| name | 是 | 角色姓名 |
| role | 是 | 角色定位（女主/男主/反派/配角等） |
| age | 否 | 年龄描述 |
| appearance | 是 | 外貌特征，聚焦AI可识别要素：脸型、发型、眼型、肤色、身高体型 |
| costume | 是 | 服饰档案，按场景分类，每套含具体材质与颜色 |
| personality | 否 | 性格标签，2-4个关键词 |
| signature_expression | 否 | 标志性表情，用于角色辨识 |
| voice_feature | 否 | 声线特征，用于配音参考 |
| emotion_tags | 否 | 情绪-表情映射表，供情绪脚本调用 |
| prompt_template | 是 | 正向提示词模板，使用 {变量名} 占位符 |
| negative_prompt | 是 | 负面排除项 |
| tags | 否 | 检索标签数组 |

---

## 场景资产完整Schema

```json
{
  "scene_id": "loca_001",
  "name": "宴会大厅",
  "space_type": "室内-大型公共空间",
  "time_weather": "夜晚，室内恒温",
  "lighting": "暖金色主光+冷白补光，水晶吊灯顶光，整体明暗比3:1",
  "atmosphere_color": "暖金色调为主，局部冷光点缀",
  "fixtures": [
    "水晶吊灯",
    "圆形宴会桌阵",
    "香槟塔",
    "红毯通道",
    "落地玻璃窗"
  ],
  "linked_props": ["prop_001", "prop_003"],
  "prompt_template": "{space_type}，{lighting}，{atmosphere_color}，陈设：{fixtures}，{time_weather}，竖屏9:16构图",
  "negative_prompt": "室外元素，自然光，简陋陈设，空白墙面",
  "tags": ["宴会", "豪门", "夜景", "室内"]
}
```

### 字段说明

| 字段 | 必填 | 说明 |
|------|------|------|
| scene_id | 是 | 唯一标识，格式 loca_XXX |
| name | 是 | 场景名称 |
| space_type | 是 | 空间类型（室内/室外+具体类型） |
| time_weather | 是 | 时间与天气/温度 |
| lighting | 是 | 光影基调，含光源、光比、色温 |
| atmosphere_color | 是 | 氛围色调描述 |
| fixtures | 否 | 固定陈设列表 |
| linked_props | 否 | 关联道具ID列表 |
| prompt_template | 是 | 正向提示词模板 |
| negative_prompt | 是 | 负面排除项 |
| tags | 否 | 检索标签数组 |

---

## 道具资产完整Schema

```json
{
  "prop_id": "prop_001",
  "name": "红酒杯",
  "appearance": "高脚水晶杯，杯身透明，内盛深红色液体，杯沿有水珠",
  "function": "宴会道具，打脸时泼洒使用",
  "key_scenes": ["第1集-第3场", "第2集-第1场"],
  "visual_tags": ["透明", "反光", "液体", "高脚"],
  "prompt_template": "水晶高脚杯，杯身透明反光，内盛深红色液体，{context}",
  "negative_prompt": "塑料杯，纸杯，无液体，不透明",
  "tags": ["宴会", "打脸", "容器"]
}
```

### 字段说明

| 字段 | 必填 | 说明 |
|------|------|------|
| prop_id | 是 | 唯一标识，格式 prop_XXX |
| name | 是 | 道具名称 |
| appearance | 是 | 外观细节，聚焦AI可识别视觉特征 |
| function | 否 | 功能属性与剧情用途 |
| key_scenes | 否 | 出场关键场次列表 |
| visual_tags | 否 | 视觉特征标签数组 |
| prompt_template | 是 | 正向提示词模板 |
| negative_prompt | 是 | 负面排除项 |
| tags | 否 | 检索标签数组 |

---

## 资产索引Schema

```json
{
  "project_id": "drama_都市逆袭之千金归来_20260826",
  "project_name": "都市逆袭之千金归来",
  "created_at": "2026-08-26",
  "art_style": "真人写实风",
  "assets": {
    "characters": [
      {
        "id": "char_001",
        "name": "林晚",
        "role": "女主",
        "file": "人物资产库.json"
      },
      {
        "id": "char_002",
        "name": "苏曼",
        "role": "反派-继妹",
        "file": "人物资产库.json"
      }
    ],
    "scenes": [
      {
        "id": "loca_001",
        "name": "宴会大厅",
        "file": "场景资产库.json"
      }
    ],
    "props": [
      {
        "id": "prop_001",
        "name": "红酒杯",
        "file": "道具资产库.json"
      }
    ]
  },
  "reuse_guide": "调用时传入 reuse_asset_ids: {characters: ['char_001'], scenes: ['loca_001']} 即可加载已有设定"
}
```

---

## 资产复用机制

### 跨集复用

同一项目内，续集生成时传入已有资产ID，系统自动加载原设定：
- 人物外貌、服饰保持一致，避免画风漂移
- 场景光影氛围继承，保证视觉连贯
- 道具外观统一，避免穿帮

### 跨项目复用

不同项目间通过资产索引中的 `source_project` 字段追溯来源：
- 提取目标ID对应资产档案
- 复制到新项目资产库并重新编号
- 保留 `original_id` 字段用于溯源

### 增量迭代

基于已有资产ID新增剧情时：
1. 读取资产索引，加载指定ID的完整档案
2. 新剧情中引用已有ID，无需重复描述设定
3. 新增人物/场景/道具按序号继续递增
4. 更新资产索引，追加新增项
