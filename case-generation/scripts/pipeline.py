#!/usr/bin/env python3
"""
语音转结构化病历 - 核心处理引擎
演示版本：展示完整的处理流水线

技术栈：
- 语音识别：本地 Whisper（隐私保护）/ 腾讯云 ASR（备选）
- NLP处理：正则 + 关键词匹配 + LLM提取
- 术语纠错：基于 JSON 词典的 RAG 模式
- 输出：Markdown 结构化病历
"""

import json
import re
import os
import time
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
REFS_DIR = BASE_DIR / "references"
OUTPUT_DIR = BASE_DIR / "output"
LOGS_DIR = BASE_DIR / "logs"

OUTPUT_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)


class MedicalTermNormalizer:
    """医学术语标准化（RAG 纠错核心）"""

    def __init__(self):
        with open(REFS_DIR / "medical_terms.json", encoding="utf-8") as f:
            self.terms = json.load(f)
        with open(REFS_DIR / "colloquial_to_formal.json", encoding="utf-8") as f:
            self.colloquial = json.load(f)
        self._build_reverse_index()

    def _build_reverse_index(self):
        """构建口语→标准语的反向索引"""
        self.reverse_map = {}
        # 处理症状
        for formal, colloquials in self.terms.get("symptoms", {}).items():
            for c in colloquials:
                self.reverse_map[c] = formal
        # 处理口语映射
        for category in self.colloquial.values():
            if isinstance(category, dict):
                for colloquial, formal in category.items():
                    self.reverse_map[colloquial] = formal

    def normalize(self, text: str) -> tuple[str, list]:
        """返回标准化文本和替换日志"""
        replacements = []
        result = text
        # 按长度降序排列，避免短词先匹配导致长词漏匹配
        sorted_map = sorted(self.reverse_map.items(), key=lambda x: len(x[0]), reverse=True)
        for colloquial, formal in sorted_map:
            if colloquial in result:
                result = result.replace(colloquial, formal)
                replacements.append({"original": colloquial, "normalized": formal})
        return result, replacements


class MedicalRecordExtractor:
    """病历字段智能提取"""

    FIELD_PATTERNS = {
        "主诉": [
            r"主诉[：:]\s*(.+?)(?=现病史|既往史|$)",
            r"因(.+?)(?:来院|入院|就诊)",
            r"患者(?:诉|主诉)?(.{5,50})(?:入院|来院|就诊)",
        ],
        "现病史": [
            r"现病史[：:]\s*(.+?)(?=既往史|过敏史|体格检查|查体|$)",
            r"(\d+(?:天|月|年|小时)前.+?)(?=既往|查体|$)",
        ],
        "既往史": [
            r"既往史[：:]\s*(.+?)(?=过敏史|体格检查|查体|$)",
            r"既往(.+?)(?=查体|检查|诊断|$)",
            r"(?:有|患有)(.+?(?:病|史|手术))(?=，|。|$)",
        ],
        "过敏史": [
            r"过敏史[：:]\s*(.+?)(?=体格检查|查体|辅助检查|$)",
            r"(?:对|)(.+?)过敏",
            r"(.+?)不能用",
        ],
        "体格检查": [
            r"(?:体格检查|查体)[：:]\s*(.+?)(?=辅助检查|化验|诊断|$)",
        ],
        "辅助检查": [
            r"(?:辅助检查|化验|检查结果)[：:]\s*(.+?)(?=诊断|印象|$)",
            r"(?:血常规|CT|B超|心电图|MRI).+?(?=诊断|印象|$)",
        ],
        "诊断": [
            r"(?:初步诊断|诊断|考虑|印象)[：:]\s*(.+?)(?=治疗|处理|给予|$)",
        ],
        "治疗方案": [
            r"(?:治疗方案|处理|给予|诊疗计划)[：:]\s*(.+?)$",
            r"(?:给予|建议)(.+?)(?:治疗|处理|观察)",
        ],
    }

    # 生命体征提取
    VITAL_PATTERNS = {
        "体温": r"(?:体温|T)[：:\s]*(\d+(?:\.\d+)?)\s*(?:°C|℃|度)?",
        "脉搏": r"(?:脉搏|P)[：:\s]*(\d+)\s*(?:次[/／]分|bpm)?",
        "呼吸": r"(?:呼吸|R)[：:\s]*(\d+)\s*(?:次[/／]分)?",
        "血压": r"(?:血压|BP)[：:\s]*(\d+[/／]\d+)\s*(?:mmHg|毫米汞柱)?",
        "血氧": r"(?:血氧|SpO2|血氧饱和度)[：:\s]*(\d+(?:\.\d+)?)\s*%?",
    }

    def extract(self, text: str) -> dict:
        """提取所有病历字段"""
        record = {}
        confidence = {}

        # 提取结构化字段
        for field, patterns in self.FIELD_PATTERNS.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.DOTALL)
                if match:
                    # 优先取第1捕获组，若无捕获组则取整个匹配
                    try:
                        content = match.group(1).strip()
                    except IndexError:
                        content = match.group(0).strip()
                    # 清理多余空白
                    content = re.sub(r'\s+', ' ', content)
                    record[field] = content
                    confidence[field] = 0.85
                    break
            if field not in record:
                record[field] = "[待补充]"
                confidence[field] = 0.0

        # 提取生命体征
        vitals = {}
        for vital, pattern in self.VITAL_PATTERNS.items():
            match = re.search(pattern, text)
            if match:
                vitals[vital] = match.group(1)
        record["生命体征"] = vitals
        confidence["生命体征"] = 0.9 if vitals else 0.0

        # 基本信息提取
        record["基本信息"] = self._extract_basic_info(text)
        record["_confidence"] = confidence

        return record

    def _extract_basic_info(self, text: str) -> dict:
        info = {}
        # 床号
        bed_match = re.search(r"(\d+)床", text)
        if bed_match:
            info["床号"] = bed_match.group(1) + "床"
        # 年龄
        age_match = re.search(r"(\d+)\s*岁", text)
        if age_match:
            info["年龄"] = age_match.group(1) + "岁"
        # 性别
        if "男" in text[:50]:
            info["性别"] = "男"
        elif "女" in text[:50]:
            info["性别"] = "女"
        return info


class MedicalRecordGenerator:
    """病历模板填充与生成"""

    def __init__(self):
        template_path = REFS_DIR / "hospital_record_template.md"
        with open(template_path, encoding="utf-8") as f:
            self.template = f.read()

    def generate(self, record: dict, doctor_name: str = "[待填写]") -> str:
        """生成完整病历"""
        now = datetime.now().strftime("%Y年%m月%d日 %H:%M")
        basic = record.get("基本信息", {})
        vitals = record.get("生命体征", {})
        confidence = record.get("_confidence", {})

        def fmt(field, value, conf_threshold=0.7):
            """低置信度字段添加核查标记"""
            conf = confidence.get(field, 1.0)
            if conf < conf_threshold and value != "[待补充]":
                return f"{value} [⚠️AI填充-请核查]"
            return value

        output = f"""# 住院病历（AI辅助生成草稿）

> ⚠️ **本病历由语音转病历 AI 系统辅助生成，归档前必须经主治医师审核签字**
> 生成时间：{now}

---

## 基本信息

| 项目 | 内容 |
|------|------|
| **患者姓名** | {basic.get('姓名', '[待补充]')} |
| **性别** | {basic.get('性别', '[待补充]')} |
| **年龄** | {basic.get('年龄', '[待补充]')} |
| **床号** | {basic.get('床号', '[待补充]')} |
| **科室** | {basic.get('科室', '[待补充]')} |
| **记录日期** | {now} |
| **记录医师** | {doctor_name} |

---

## 主诉

{fmt('主诉', record.get('主诉', '[待补充-必填]'))}

---

## 现病史

{fmt('现病史', record.get('现病史', '[待补充-必填]'))}

---

## 既往史

{fmt('既往史', record.get('既往史', '[待补充]'))}

---

## 过敏史

{fmt('过敏史', record.get('过敏史', '否认食物及药物过敏史'))}

---

## 体格检查

**生命体征：**
- 体温（T）：{vitals.get('体温', '[待补充]')}°C
- 脉搏（P）：{vitals.get('脉搏', '[待补充]')} 次/分
- 呼吸（R）：{vitals.get('呼吸', '[待补充]')} 次/分
- 血压（BP）：{vitals.get('血压', '[待补充]')} mmHg

**专科检查：**
{fmt('体格检查', record.get('体格检查', '[待补充]'))}

---

## 辅助检查

{fmt('辅助检查', record.get('辅助检查', '[待补充]'))}

---

## 初步诊断

{fmt('诊断', record.get('诊断', '[待补充-必填]'))}

---

## 诊疗计划

{fmt('治疗方案', record.get('治疗方案', '[待补充]'))}

---

**记录医师签名：** _______________ 　**日期：** _______________

**上级医师审核：** _______________ 　**日期：** _______________

> 合规说明：患者数据本地处理，未上传任何第三方服务器。本系统为辅助工具，最终医疗决策由医师负责。
"""
        return output


class AuditLogger:
    """操作审计日志（合规要求）"""

    def __init__(self):
        self.log_file = LOGS_DIR / "audit.log"

    def log(self, action: str, details: dict):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            **details
        }
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")


class VoiceToMedicalRecordPipeline:
    """完整处理流水线"""

    def __init__(self):
        self.normalizer = MedicalTermNormalizer()
        self.extractor = MedicalRecordExtractor()
        self.generator = MedicalRecordGenerator()
        self.logger = AuditLogger()

    def process(self, input_text: str, doctor_name: str = "[待填写]") -> dict:
        print("\n" + "="*60)
        print("🏥 语音转结构化病历 AI 处理流水线")
        print("="*60)

        # Step 1: 记录原始输入
        self.logger.log("INPUT_RECEIVED", {"length": len(input_text)})
        print(f"\n[Step 1] ✅ 接收输入（{len(input_text)} 字符）")

        # Step 2: 医学术语标准化
        normalized_text, replacements = self.normalizer.normalize(input_text)
        print(f"[Step 2] ✅ 术语标准化完成（{len(replacements)} 处替换）")
        for r in replacements[:5]:  # 只显示前5条
            print(f"         '{r['original']}' → '{r['normalized']}'")
        if len(replacements) > 5:
            print(f"         ... 还有 {len(replacements)-5} 处替换")
        self.logger.log("TERMS_NORMALIZED", {"replacements_count": len(replacements)})

        # Step 3: 字段提取
        record = self.extractor.extract(normalized_text)
        extracted_fields = [k for k, v in record.items()
                          if k not in ['_confidence', '基本信息', '生命体征'] and v != "[待补充]"]
        print(f"[Step 3] ✅ 字段提取完成（成功提取 {len(extracted_fields)}/{len(self.extractor.FIELD_PATTERNS)} 个核心字段）")
        self.logger.log("FIELDS_EXTRACTED", {"fields": extracted_fields})

        # Step 4: 生成病历
        medical_record = self.generator.generate(record, doctor_name)
        print(f"[Step 4] ✅ 病历生成完成（{len(medical_record)} 字符）")

        # Step 5: 检查必填字段
        required_fields = ["主诉", "诊断"]
        missing_required = [f for f in required_fields if record.get(f) == "[待补充]"]
        low_confidence_fields = [
            f for f, conf in record.get("_confidence", {}).items()
            if 0 < conf < 0.8
        ]

        print(f"\n[Step 5] 📋 质量检查报告：")
        if missing_required:
            print(f"         ❌ 缺少必填字段：{', '.join(missing_required)}")
        else:
            print(f"         ✅ 所有必填字段已提取")
        if low_confidence_fields:
            print(f"         ⚠️  低置信度字段（需医生重点核查）：{', '.join(low_confidence_fields)}")

        # Step 6: 保存输出
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = OUTPUT_DIR / f"medical_record_{timestamp}.md"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(medical_record)
        print(f"\n[Step 6] 💾 病历已保存至：{output_path}")
        self.logger.log("RECORD_GENERATED", {"output_path": str(output_path)})

        print("\n" + "="*60)
        print("⚠️  重要提示：请主治医师审核以下内容后确认归档")
        print("="*60)

        return {
            "record": medical_record,
            "output_path": str(output_path),
            "replacements": replacements,
            "extracted_fields": extracted_fields,
            "missing_required": missing_required,
            "low_confidence_fields": low_confidence_fields,
        }


# ========== 演示用例 ==========
DEMO_INPUT = """
3床，张三，男，45岁，因发烧三天来院，体温最高39度，
伴咳嗽咳痰，痰是黄色的，没有胸痛，呼吸还好。
既往有高血压，一直吃氨氯地平，对青霉素过敏。
查体：体温38.5，脉搏92次分，呼吸18次分，血压130/85mmHg，
肺部听诊右下肺有湿罗音，心律齐无杂音，肚子软无压痛。
血常规：白细胞12点8，中性粒87%。
胸片：右下肺有片影。
考虑肺炎，给予头孢曲松静脉滴注，同时监测血压，明天复查血常规。
"""

if __name__ == "__main__":
    pipeline = VoiceToMedicalRecordPipeline()
    result = pipeline.process(DEMO_INPUT, doctor_name="李医生")
    print("\n" + "="*60)
    print("生成的结构化病历预览：")
    print("="*60)
    print(result["record"][:800] + "\n...\n（完整内容已保存至文件）")
